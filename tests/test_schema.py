"""Tests for the GPR schema — the IP core."""

from __future__ import annotations

import pytest

from ai_gr import (
    AgenticContext,
    Authority,
    Decision,
    Evidence,
    Gate,
    GPREntry,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.schema import AI_GR_CONTEXT, SCHEMA_VERSION


def _minimal_entry(**overrides) -> GPREntry:
    defaults = {
        "id": "urn:gpr:test-org/test-system/conceive/0001",
        "subject": Subject(system="TestSystem", version="1.0.0", type=SystemType.PREDICTIVE),
        "gate": Gate.CONCEIVE,
        "risk_tier": RiskTier.MANAGED,
        "decision": Decision.APPROVE,
        "evidence": Evidence(),
        "authority": Authority(
            approver="did:web:test-org:role",
            delegated_scope="tier:managed",
        ),
    }
    defaults.update(overrides)
    return GPREntry(**defaults)


class TestBasicConstruction:
    def test_minimal_entry_constructs(self) -> None:
        entry = _minimal_entry()
        assert entry.id.startswith("urn:gpr:")
        assert entry.context == AI_GR_CONTEXT
        assert entry.schema_version == SCHEMA_VERSION

    def test_jsonld_emits_at_context(self) -> None:
        entry = _minimal_entry()
        jsonld = entry.to_jsonld()
        assert jsonld["@context"] == AI_GR_CONTEXT
        assert jsonld["@type"] == "GPREntry"

    def test_content_hash_is_deterministic(self) -> None:
        e1 = _minimal_entry()
        e2 = _minimal_entry()
        # Override timestamps to be identical so hashes match.
        e2 = e2.model_copy(update={"attestation": e1.attestation})
        assert e1.content_hash() == e2.content_hash()

    def test_content_hash_excludes_attestation(self) -> None:
        e1 = _minimal_entry()
        # Mutating the attestation should NOT change the content hash —
        # the signature signs the rest of the entry.
        from ai_gr.schema import Attestation

        e2 = e1.model_copy(
            update={"attestation": Attestation(signature="ed25519:fake", public_key="fake")}
        )
        assert e1.content_hash() == e2.content_hash()


class TestURNValidation:
    def test_valid_urn_accepted(self) -> None:
        e = _minimal_entry(id="urn:gpr:acme-co/my-system/build/0042")
        assert e.id == "urn:gpr:acme-co/my-system/build/0042"

    def test_missing_prefix_rejected(self) -> None:
        with pytest.raises(ValueError, match="urn:gpr"):
            _minimal_entry(id="gpr:org/sys/conceive/0001")

    def test_unknown_gate_rejected(self) -> None:
        with pytest.raises(ValueError):
            _minimal_entry(id="urn:gpr:org/sys/release/0001")

    def test_uppercase_rejected(self) -> None:
        with pytest.raises(ValueError):
            _minimal_entry(id="urn:gpr:ORG/SYS/conceive/0001")

    def test_short_sequence_rejected(self) -> None:
        with pytest.raises(ValueError):
            _minimal_entry(id="urn:gpr:org/sys/conceive/1")


class TestAgenticInvariant:
    """Agentic systems MUST carry an agentic_context block."""

    def test_agentic_without_context_rejected(self) -> None:
        with pytest.raises(ValueError, match="agentic_context"):
            _minimal_entry(
                subject=Subject(system="Agent", version="1.0", type=SystemType.AGENTIC),
            )

    def test_agentic_with_context_accepted(self) -> None:
        entry = _minimal_entry(
            subject=Subject(system="Agent", version="1.0", type=SystemType.AGENTIC),
            agentic_context=AgenticContext(
                action_authority=["read:data"],
                human_oversight="in-the-loop",
            ),
        )
        assert entry.agentic_context is not None
        assert entry.agentic_context.action_authority == ["read:data"]

    def test_generative_without_context_accepted(self) -> None:
        # Non-agentic systems don't need agentic_context.
        entry = _minimal_entry(
            subject=Subject(system="GenAI", version="1.0", type=SystemType.GENERATIVE),
        )
        assert entry.agentic_context is None


class TestStrictness:
    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValueError):
            GPREntry.model_validate(
                {
                    "@context": AI_GR_CONTEXT,
                    "id": "urn:gpr:org/sys/conceive/0001",
                    "subject": {"system": "X", "version": "1", "type": "predictive"},
                    "gate": "Conceive",
                    "risk_tier": "Managed",
                    "decision": "approve",
                    "evidence": {},
                    "authority": {"approver": "did:web:x:y", "delegated_scope": "x"},
                    "rogue_extra_field": "boom",
                }
            )


class TestRegimeClaims:
    def test_multiple_regime_claims_supported(self) -> None:
        entry = _minimal_entry(
            regime=[
                RegimeClaim(regime="EU-AI-Act:Article-9"),
                RegimeClaim(regime="HIPAA:164.308"),
                RegimeClaim(regime="NIST-AI-RMF:MAP-1.1"),
            ]
        )
        assert len(entry.regime) == 3
