"""
ai_gr.ribbon.policy — Gate × tier requirement matrix.

This module encodes the requirements that a GPR entry must satisfy at each
(gate, tier) intersection. It is the executable form of the grid on slide 3
of the AI-GR deck.

The matrix is intentionally conservative: the requirements listed here are
the *minimums*. Organizations layer their own additional requirements on top
via the ``extra_requirements`` parameter to ``check_entry``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_gr.schema import Gate, GPREntry, RiskTier


@dataclass(frozen=True)
class GateRequirement:
    """A requirement that a GPR entry at a given gate/tier must satisfy."""

    name: str
    description: str
    #: Function that returns True iff the entry satisfies the requirement.
    check: callable  # type: ignore[type-arg]


@dataclass
class PolicyViolation:
    """Records a failed requirement check on an entry."""

    entry_id: str
    requirement: str
    description: str
    severity: str = field(default="error")  # error | warn


# ---------------------------------------------------------------------------
# Reusable check primitives
# ---------------------------------------------------------------------------


def _has_datasets(entry: GPREntry) -> bool:
    return bool(entry.evidence.datasets)


def _has_evaluations(entry: GPREntry) -> bool:
    return bool(entry.evidence.evaluations)


def _has_red_team(entry: GPREntry) -> bool:
    return bool(entry.evidence.red_team)


def _has_model_weight_hash(entry: GPREntry) -> bool:
    return entry.evidence.model_weights is not None


def _has_sbom(entry: GPREntry) -> bool:
    return entry.evidence.sbom is not None


def _has_co_approvers(entry: GPREntry) -> bool:
    return len(entry.authority.co_approvers) >= 1


def _has_human_oversight(entry: GPREntry) -> bool:
    return (
        entry.agentic_context is not None
        and entry.agentic_context.human_oversight is not None
    )


def _has_action_authority(entry: GPREntry) -> bool:
    return (
        entry.agentic_context is not None
        and len(entry.agentic_context.action_authority) >= 1
    )


def _claims_at_least_one_regime(entry: GPREntry) -> bool:
    return len(entry.regime) >= 1


def _has_signature(entry: GPREntry) -> bool:
    return entry.attestation.signature is not None


# ---------------------------------------------------------------------------
# The matrix — minimum requirements per (gate, tier).
# ---------------------------------------------------------------------------


def _build_matrix() -> dict[tuple[Gate, RiskTier], list[GateRequirement]]:
    req = GateRequirement

    # Reusable requirement objects.
    req_signature = req(
        "signature_present",
        "Entry must be signed before being committed to the chain.",
        _has_signature,
    )
    req_regime = req(
        "regime_declared",
        "At least one regulatory regime claim must be declared.",
        _claims_at_least_one_regime,
    )
    req_datasets = req(
        "datasets_referenced",
        "Training/evaluation datasets must be referenced (content-addressable where possible).",
        _has_datasets,
    )
    req_evals = req(
        "evaluation_results",
        "Evaluation or assessment results must be attached.",
        _has_evaluations,
    )
    req_red_team = req(
        "red_team_report",
        "Red-team report required for Critical-tier Build entries.",
        _has_red_team,
    )
    req_model_hash = req(
        "model_weight_hash",
        "SHA-256 of model weights must be recorded.",
        _has_model_weight_hash,
    )
    req_sbom = req(
        "sbom_present",
        "Software bill of materials (SBOM) required.",
        _has_sbom,
    )
    req_co_approver = req(
        "co_approver_required",
        "Critical-tier decisions require at least one co-approver (e.g. CISO + CAIO).",
        _has_co_approvers,
    )
    req_oversight = req(
        "human_oversight_declared",
        "Human oversight mode must be declared for Critical-tier agentic systems.",
        _has_human_oversight,
    )
    req_action_auth = req(
        "action_authority_declared",
        "Agentic systems must declare action authority.",
        _has_action_authority,
    )

    matrix: dict[tuple[Gate, RiskTier], list[GateRequirement]] = {}

    # ---------------- CONCEIVE ----------------
    matrix[(Gate.CONCEIVE, RiskTier.CRITICAL)] = [req_signature, req_regime, req_co_approver]
    matrix[(Gate.CONCEIVE, RiskTier.HIGH)] = [req_signature, req_regime]
    matrix[(Gate.CONCEIVE, RiskTier.MANAGED)] = [req_signature]

    # ---------------- BUILD ----------------
    matrix[(Gate.BUILD, RiskTier.CRITICAL)] = [
        req_signature, req_regime, req_datasets, req_evals,
        req_red_team, req_model_hash, req_sbom,
    ]
    matrix[(Gate.BUILD, RiskTier.HIGH)] = [
        req_signature, req_regime, req_datasets, req_evals, req_model_hash,
    ]
    matrix[(Gate.BUILD, RiskTier.MANAGED)] = [req_signature, req_evals]

    # ---------------- DEPLOY ----------------
    matrix[(Gate.DEPLOY, RiskTier.CRITICAL)] = [
        req_signature, req_regime, req_co_approver, req_action_auth, req_oversight,
    ]
    matrix[(Gate.DEPLOY, RiskTier.HIGH)] = [req_signature, req_regime]
    matrix[(Gate.DEPLOY, RiskTier.MANAGED)] = [req_signature]

    # ---------------- OPERATE ----------------
    matrix[(Gate.OPERATE, RiskTier.CRITICAL)] = [req_signature, req_regime, req_evals]
    matrix[(Gate.OPERATE, RiskTier.HIGH)] = [req_signature, req_evals]
    matrix[(Gate.OPERATE, RiskTier.MANAGED)] = [req_signature]

    # ---------------- EVOLVE ----------------
    matrix[(Gate.EVOLVE, RiskTier.CRITICAL)] = [
        req_signature, req_regime, req_co_approver, req_evals, req_model_hash,
    ]
    matrix[(Gate.EVOLVE, RiskTier.HIGH)] = [req_signature, req_regime, req_evals]
    matrix[(Gate.EVOLVE, RiskTier.MANAGED)] = [req_signature]

    # ---------------- RETIRE ----------------
    matrix[(Gate.RETIRE, RiskTier.CRITICAL)] = [req_signature, req_co_approver]
    matrix[(Gate.RETIRE, RiskTier.HIGH)] = [req_signature]
    matrix[(Gate.RETIRE, RiskTier.MANAGED)] = [req_signature]

    return matrix


_MATRIX = _build_matrix()


def requirements_for(gate: Gate, tier: RiskTier) -> list[GateRequirement]:
    """Return the list of requirements that apply at a given (gate, tier)."""
    return list(_MATRIX[(gate, tier)])


def check_entry(
    entry: GPREntry,
    *,
    extra_requirements: list[GateRequirement] | None = None,
) -> list[PolicyViolation]:
    """Check an entry against the Ribbon's policy matrix.

    Args:
        entry: The GPR entry to evaluate.
        extra_requirements: Optional list of organization-specific requirements
            layered on top of the framework defaults.

    Returns:
        List of ``PolicyViolation`` objects. Empty list means all requirements
        passed.
    """
    reqs = requirements_for(entry.gate, entry.risk_tier)
    if extra_requirements:
        reqs = [*reqs, *extra_requirements]

    violations: list[PolicyViolation] = []
    for req in reqs:
        if not req.check(entry):
            violations.append(
                PolicyViolation(
                    entry_id=entry.id,
                    requirement=req.name,
                    description=req.description,
                )
            )
    return violations


__all__ = ["GateRequirement", "PolicyViolation", "check_entry", "requirements_for"]
