"""Tests for the reference-pattern adapters in ai_gr.adapters.

These adapters are reference patterns, not production-grade integrations.
The tests verify the wire shapes of their inputs and outputs — they do not
exercise actual Sigstore/OPA/OpenTelemetry network endpoints.
"""

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
from ai_gr.adapters import opa, otel, sigstore


def _legal_identity() -> LegalIdentity:
    return LegalIdentity(
        name="Test Corp",
        registration_id="LEI:TEST00000000000000001",
        jurisdiction="DE",
        address="Teststrasse 1, Berlin",
        contact_email="test@test.example",
    )


def _entry() -> GPREntry:
    return GPREntry(
        id="urn:gpr:t/s/build/0001",
        subject=Subject(system="TestSys", version="1.0.0", type=SystemType.PREDICTIVE),
        gate=Gate.BUILD,
        risk_tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        evidence=Evidence(),
        authority=Authority(
            approver="did:web:test:r",
            delegated_scope="tier:critical",
            legal_identity=_legal_identity(),
        ),
        regime=[RegimeClaim(regime="EU-AI-Act:high-risk")],
    )


class TestSigstoreAdapter:
    def test_attestation_to_evidence_dict_minimal(self) -> None:
        att = sigstore.SigstoreAttestation(
            artifact_uri="oci://registry.example/model@sha256:abc",
            artifact_sha256="a" * 64,
        )
        d = att.to_evidence_dict()
        assert d["artifact_uri"] == "oci://registry.example/model@sha256:abc"
        assert d["artifact_sha256"] == "a" * 64
        # Optional fields absent
        assert "bundle_uri" not in d
        assert "rekor_log_index" not in d

    def test_attestation_to_evidence_dict_full(self) -> None:
        att = sigstore.SigstoreAttestation(
            artifact_uri="oci://x/y",
            artifact_sha256="b" * 64,
            bundle_uri="oci://x/y.bundle",
            rekor_log_index=12345,
            certificate_subject="caio@example.com",
            in_toto_predicate_type="https://slsa.dev/provenance/v1",
            extra={"deployment": "prod"},
        )
        d = att.to_evidence_dict()
        assert d["rekor_log_index"] == 12345
        assert d["in_toto_predicate_type"] == "https://slsa.dev/provenance/v1"
        assert d["extra"] == {"deployment": "prod"}

    def test_submit_to_rekor_returns_expected_shape(self) -> None:
        result = sigstore.submit_to_rekor("a" * 64)
        assert "request_url" in result
        assert "request_body" in result
        assert result["request_body"]["kind"] == "hashedrekord"
        assert result["request_body"]["apiVersion"] == "0.0.1"
        assert result["request_body"]["spec"]["data"]["hash"]["algorithm"] == "sha256"
        assert result["request_body"]["spec"]["data"]["hash"]["value"] == "a" * 64

    def test_submit_to_rekor_default_url(self) -> None:
        result = sigstore.submit_to_rekor("b" * 64)
        assert "rekor.sigstore.dev" in result["request_url"]


class TestOpaAdapter:
    def test_build_opa_request_shape(self) -> None:
        req = opa.build_opa_request(
            approver_did="did:web:t:r",
            requested_capability="tier:critical;phi:read",
            risk_tier="Critical",
            gate="Build",
        )
        assert req["url"] == "/v1/data/ai_gr/authority/allow"
        assert req["body"]["input"]["approver_did"] == "did:web:t:r"
        assert req["body"]["input"]["gate"] == "Build"

    def test_parse_opa_response_boolean(self) -> None:
        decision = opa.parse_opa_response({"result": True})
        assert decision.allowed is True
        assert decision.reasons == ()

    def test_parse_opa_response_boolean_false(self) -> None:
        decision = opa.parse_opa_response({"result": False})
        assert decision.allowed is False

    def test_parse_opa_response_object(self) -> None:
        decision = opa.parse_opa_response(
            {"result": {"allow": False, "reasons": ["missing co-approver", "wrong tier"]}}
        )
        assert decision.allowed is False
        assert "missing co-approver" in decision.reasons
        assert "wrong tier" in decision.reasons

    def test_parse_opa_response_unknown_shape(self) -> None:
        decision = opa.parse_opa_response({"result": "weird"})
        assert decision.allowed is False
        assert decision.reasons == ("opa returned unexpected shape",)


class TestOtelAdapter:
    def test_gpr_event_attributes_contains_required_fields(self) -> None:
        attrs = otel.gpr_event_attributes(_entry())
        assert attrs[otel.ATTR_GPR_ID] == "urn:gpr:t/s/build/0001"
        assert attrs[otel.ATTR_GPR_GATE] == "Build"
        assert attrs[otel.ATTR_GPR_RISK_TIER] == "Critical"
        assert attrs[otel.ATTR_GPR_DECISION] == "approve"
        assert attrs[otel.ATTR_SUBJECT_SYSTEM] == "TestSys"
        assert attrs[otel.ATTR_AUTHORITY_APPROVER] == "did:web:test:r"
        assert attrs[otel.ATTR_REGIME_COUNT] == 1

    def test_gpr_event_attributes_includes_legal_identity_name(self) -> None:
        attrs = otel.gpr_event_attributes(_entry())
        assert attrs[otel.ATTR_AUTHORITY_LEGAL_IDENTITY_NAME] == "Test Corp"

    def test_gpr_event_attributes_excludes_pii_by_default(self) -> None:
        attrs = otel.gpr_event_attributes(_entry())
        # contact_email and address are excluded — they may be personal data
        # and should not be exported by default to observability backends.
        assert "test@test.example" not in str(attrs)
        assert "Teststrasse" not in str(attrs)

    def test_verification_event_attributes_shape(self) -> None:
        attrs = otel.verification_event_attributes(
            check_name="signatures",
            passed=True,
            entries_checked=5,
            entries_failed=[],
        )
        assert attrs[otel.ATTR_VERIFICATION_CHECK] == "signatures"
        assert attrs[otel.ATTR_VERIFICATION_PASSED] is True
        assert attrs["ai_gr.verification.entries_checked"] == 5
        assert attrs["ai_gr.verification.entries_failed_count"] == 0
