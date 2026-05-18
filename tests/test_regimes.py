"""Tests for the regime registry and coverage summaries."""

from __future__ import annotations

import pytest

from ai_gr.regimes import get_regime, list_regimes


class TestRegistry:
    def test_all_expected_regimes_registered(self) -> None:
        identifiers = {r.identifier for r in list_regimes()}
        expected = {
            "EU-AI-Act",
            "NIST-AI-RMF",
            "ISO-42001",
            "HIPAA",
            "FDA-SaMD",
            "SEC-Cyber",
            "State-AEDT",
        }
        assert expected.issubset(identifiers)

    def test_get_unknown_regime_raises(self) -> None:
        with pytest.raises(KeyError):
            get_regime("Made-Up-Regime")

    def test_every_regime_has_requirements(self) -> None:
        for r in list_regimes():
            reqs = r.requirements()
            assert reqs, f"Regime {r.identifier} has no requirements"
            for req in reqs:
                assert req.citation
                assert req.description
                assert req.relevant_gates


class TestCoverageOnDemoChain:
    """Run the bundled clinical demo and verify the coverage summary."""

    def test_clinical_demo_eu_ai_act_coverage(self) -> None:
        from examples.clinical_decision_support import build_chain

        chain = build_chain()
        eu = get_regime("EU-AI-Act")
        summary = eu.coverage_summary(chain)
        assert summary["regime"] == eu.name
        assert summary["claims_made"] >= 5  # multiple EU AI Act claims across gates
        assert summary["entries_covered"] == 5
        # Every EU AI Act requirement should have at least one entry that
        # falls within its relevant gates.
        unsatisfied = [r for r in summary["requirements"] if not r["satisfied"]]
        assert not unsatisfied, f"Unsatisfied EU AI Act requirements: {unsatisfied}"

    def test_clinical_demo_hipaa_coverage(self) -> None:
        from examples.clinical_decision_support import build_chain

        chain = build_chain()
        hipaa = get_regime("HIPAA")
        summary = hipaa.coverage_summary(chain)
        # The CDS chain claims HIPAA explicitly at Conceive/Build/Deploy/Operate.
        assert summary["claims_made"] >= 3
        assert summary["entries_covered"] >= 3
