"""Tests for the gate × tier policy matrix."""

from __future__ import annotations

from ai_gr import (
    Authority,
    Decision,
    Evidence,
    Gate,
    GPREntry,
    LegalIdentity,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.crypto import KeyPair, sign_entry
from ai_gr.ribbon.policy import check_entry, requirements_for


def _test_legal_identity() -> LegalIdentity:
    """Construct a valid LegalIdentity for use in test fixtures."""
    return LegalIdentity(
        name="Test Corp Ltd.",
        registration_id="LEI:TESTCORP000000000001",
        jurisdiction="GB",
        address="1 Test Lane, London, UK",
        contact_email="compliance@testcorp.example",
    )


def _build_entry(
    *,
    gate: Gate,
    tier: RiskTier,
    evidence: Evidence | None = None,
    regimes: list[RegimeClaim] | None = None,
    co_approvers: list[str] | None = None,
    sign: bool = True,
) -> GPREntry:
    # Critical-tier entries require legal_identity per schema v0.2.0.
    legal_identity = _test_legal_identity() if tier == RiskTier.CRITICAL else None
    entry = GPREntry(
        id=f"urn:gpr:t/s/{gate.value.lower()}/0001",
        subject=Subject(system="S", version="1", type=SystemType.PREDICTIVE),
        gate=gate,
        risk_tier=tier,
        decision=Decision.APPROVE,
        evidence=evidence or Evidence(),
        authority=Authority(
            approver="did:web:t:r",
            delegated_scope="x",
            co_approvers=co_approvers or [],
            legal_identity=legal_identity,
        ),
        regime=regimes or [],
    )
    if sign:
        entry = sign_entry(entry, KeyPair.generate())
    return entry


class TestMatrixShape:
    def test_critical_build_has_more_reqs_than_managed_build(self) -> None:
        crit = requirements_for(Gate.BUILD, RiskTier.CRITICAL)
        man = requirements_for(Gate.BUILD, RiskTier.MANAGED)
        assert len(crit) > len(man)

    def test_critical_conceive_requires_co_approver(self) -> None:
        reqs = requirements_for(Gate.CONCEIVE, RiskTier.CRITICAL)
        assert any(r.name == "co_approver_required" for r in reqs)


class TestViolationDetection:
    def test_critical_build_unsigned_flags_signature(self) -> None:
        entry = _build_entry(
            gate=Gate.BUILD, tier=RiskTier.CRITICAL,
            sign=False,
        )
        violations = check_entry(entry)
        names = {v.requirement for v in violations}
        assert "signature_present" in names

    def test_critical_build_missing_evidence_flagged(self) -> None:
        entry = _build_entry(
            gate=Gate.BUILD, tier=RiskTier.CRITICAL,
            regimes=[RegimeClaim(regime="EU-AI-Act:Article-9")],
            evidence=Evidence(),  # empty
        )
        violations = check_entry(entry)
        names = {v.requirement for v in violations}
        # Critical Build requires datasets, evaluations, red_team, model_hash, sbom.
        assert "datasets_referenced" in names
        assert "evaluation_results" in names
        assert "red_team_report" in names
        assert "model_weight_hash" in names
        assert "sbom_present" in names

    def test_critical_build_fully_evidenced_passes(self) -> None:
        entry = _build_entry(
            gate=Gate.BUILD, tier=RiskTier.CRITICAL,
            regimes=[RegimeClaim(regime="EU-AI-Act:Article-9")],
            evidence=Evidence(
                datasets=["ds:sha256:" + "a" * 64],
                evaluations=["eval.pdf"],
                red_team=["redteam.pdf"],
                model_weights="a" * 64,
                sbom="spdx-2.3:bom.json",
            ),
        )
        violations = check_entry(entry)
        assert violations == []

    def test_managed_conceive_minimal_passes(self) -> None:
        entry = _build_entry(gate=Gate.CONCEIVE, tier=RiskTier.MANAGED)
        violations = check_entry(entry)
        assert violations == []
