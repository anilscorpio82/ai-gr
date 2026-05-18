"""Tests for the v0.2.0 regime modules (EU AI Act Article 26, GDPR, NIS2,
MDR/IVDR, DORA, DSA, Data Act, CRA, EHDS).

These tests verify (a) every new regime registers correctly, (b) every regime
has a non-empty requirements list, (c) every requirement names at least one
Ribbon gate, and (d) the regimes correctly identify entries claiming them.
"""

from __future__ import annotations

import pytest

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
from ai_gr.regimes import get_regime, list_regimes

# Identifiers added in v0.2.0
V020_REGIMES = [
    "EU-AI-Act-Deployer",
    "GDPR",
    "NIS2",
    "MDR-IVDR",
    "DORA",
    "DSA",
    "Data-Act",
    "CRA",
    "EHDS",
]


def _legal_identity() -> LegalIdentity:
    return LegalIdentity(
        name="Test Corp",
        registration_id="LEI:TEST00000000000000001",
        jurisdiction="DE",
        address="Teststrasse 1, Berlin",
        contact_email="test@test.example",
    )


def _entry_with_regime(regime_id: str, gate: Gate = Gate.BUILD) -> GPREntry:
    return GPREntry(
        id=f"urn:gpr:t/s/{gate.value.lower()}/0001",
        subject=Subject(system="S", version="1", type=SystemType.PREDICTIVE),
        gate=gate,
        risk_tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        evidence=Evidence(),
        authority=Authority(
            approver="did:web:t:r",
            delegated_scope="x",
            legal_identity=_legal_identity(),
        ),
        regime=[RegimeClaim(regime=f"{regime_id}:test-citation")],
    )


@pytest.mark.parametrize("regime_id", V020_REGIMES)
class TestNewRegimeRegistration:
    def test_regime_is_registered(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        assert regime.identifier == regime_id

    def test_regime_has_non_empty_name(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        assert len(regime.name) > 0

    def test_regime_has_non_empty_description(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        assert len(regime.description) > 0

    def test_regime_has_at_least_one_requirement(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        assert len(regime.requirements()) >= 1

    def test_every_requirement_names_at_least_one_gate(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        for req in regime.requirements():
            assert len(req.relevant_gates) >= 1, (
                f"{regime_id} requirement {req.citation!r} has no relevant gates"
            )

    def test_every_requirement_has_citation_and_description(self, regime_id: str) -> None:
        regime = get_regime(regime_id)
        for req in regime.requirements():
            assert len(req.citation) > 0
            assert len(req.description) > 0


@pytest.mark.parametrize("regime_id", V020_REGIMES)
class TestNewRegimeCoverage:
    def test_applies_to_entry_with_matching_claim(self, regime_id: str) -> None:
        entry = _entry_with_regime(regime_id)
        regime = get_regime(regime_id)
        assert regime.applies_to_entry(entry) is True

    def test_does_not_apply_to_entry_with_unrelated_claim(self, regime_id: str) -> None:
        # Use an unrelated regime id that doesn't accidentally prefix-match
        # any of the new identifiers.
        entry = _entry_with_regime("SOMETHING-ELSE-XYZ-99")
        regime = get_regime(regime_id)
        assert regime.applies_to_entry(entry) is False

    def test_coverage_summary_returns_dict(self, regime_id: str) -> None:
        chain = [_entry_with_regime(regime_id)]
        regime = get_regime(regime_id)
        summary = regime.coverage_summary(chain)
        assert summary["identifier"] == regime_id
        assert summary["claims_made"] == 1
        assert summary["entries_covered"] == 1


class TestTotalRegimeCount:
    def test_v020_has_16_regimes(self) -> None:
        """v0.2.0 ships 16 regimes — 7 from v0.1.0 plus 9 new in v0.2.0."""
        assert len(list_regimes()) == 16


class TestGDPRSpecific:
    """GDPR has v0.2.0-specific design choices worth testing explicitly."""

    def test_gdpr_addresses_article_17(self) -> None:
        regime = get_regime("GDPR")
        citations = [req.citation for req in regime.requirements()]
        assert any("Article 17" in c for c in citations)

    def test_gdpr_addresses_article_35_dpia(self) -> None:
        regime = get_regime("GDPR")
        citations = [req.citation for req in regime.requirements()]
        assert any("Article 35" in c for c in citations)

    def test_gdpr_addresses_chapter_v_transfers(self) -> None:
        regime = get_regime("GDPR")
        citations = [req.citation for req in regime.requirements()]
        assert any("Chapter V" in c for c in citations)


class TestEUAIActDeployerSpecific:
    """EU AI Act Article 26 covers the full deployer obligation surface."""

    def test_addresses_human_oversight_article_26_2(self) -> None:
        regime = get_regime("EU-AI-Act-Deployer")
        citations = [req.citation for req in regime.requirements()]
        assert any("26(2)" in c for c in citations)

    def test_addresses_log_retention_article_26_6(self) -> None:
        regime = get_regime("EU-AI-Act-Deployer")
        citations = [req.citation for req in regime.requirements()]
        assert any("26(6)" in c for c in citations)

    def test_addresses_fundamental_rights_article_27(self) -> None:
        regime = get_regime("EU-AI-Act-Deployer")
        citations = [req.citation for req in regime.requirements()]
        assert any("Article 27" in c for c in citations)
