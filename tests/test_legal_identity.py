"""Tests for LegalIdentity and the Critical-tier invariant.

New in v0.2.0 per §4.3 of the AI-GR paper (v1.2+). The DID layer provides
cryptographic authentication; the legal_identity layer provides regulatory
binding to a named legal person.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_gr import (
    Authority,
    Decision,
    Evidence,
    Gate,
    GdprRole,
    GPREntry,
    LegalIdentity,
    RiskTier,
    Subject,
    SystemType,
)


def _valid_legal_identity(**overrides) -> LegalIdentity:
    defaults = {
        "name": "ACME Health Systems Inc.",
        "registration_id": "LEI:5493001K3F3DUM2KRD89",
        "jurisdiction": "DE",
        "address": "Musterstrasse 1, 10115 Berlin, Germany",
        "contact_email": "compliance@acme-health.example",
        "gdpr_role": GdprRole.CONTROLLER,
    }
    defaults.update(overrides)
    return LegalIdentity(**defaults)


class TestLegalIdentityValidation:
    def test_valid_legal_identity_constructs(self) -> None:
        legal_id = _valid_legal_identity()
        assert legal_id.name == "ACME Health Systems Inc."
        assert legal_id.jurisdiction == "DE"

    def test_jurisdiction_must_be_iso_3166_alpha2(self) -> None:
        with pytest.raises(ValidationError):
            _valid_legal_identity(jurisdiction="Germany")
        with pytest.raises(ValidationError):
            _valid_legal_identity(jurisdiction="DEU")  # alpha-3
        with pytest.raises(ValidationError):
            _valid_legal_identity(jurisdiction="de")  # lowercase

    def test_contact_email_validated(self) -> None:
        with pytest.raises(ValidationError):
            _valid_legal_identity(contact_email="not-an-email")

    def test_gdpr_role_optional(self) -> None:
        # GDPR role can be None for non-GDPR deployments; explicit
        # NOT_APPLICABLE is preferred but both are accepted.
        legal_id = _valid_legal_identity(gdpr_role=None)
        assert legal_id.gdpr_role is None

    def test_all_required_fields(self) -> None:
        for field in ["name", "registration_id", "jurisdiction", "address", "contact_email"]:
            kwargs = {
                "name": "X",
                "registration_id": "LEI:X",
                "jurisdiction": "US",
                "address": "X",
                "contact_email": "x@x.com",
            }
            del kwargs[field]
            with pytest.raises(ValidationError):
                LegalIdentity(**kwargs)


class TestCriticalTierInvariant:
    """The Critical-tier invariant: every Critical-tier GPR entry must carry
    Authority.legal_identity. Enforced in GPREntry.model_post_init.
    """

    def _base_entry_kwargs(self, tier: RiskTier, legal_id: LegalIdentity | None):
        return {
            "id": f"urn:gpr:t/s/{Gate.BUILD.value.lower()}/0001",
            "subject": Subject(system="S", version="1", type=SystemType.PREDICTIVE),
            "gate": Gate.BUILD,
            "risk_tier": tier,
            "decision": Decision.APPROVE,
            "evidence": Evidence(),
            "authority": Authority(
                approver="did:web:t:r",
                delegated_scope="x",
                legal_identity=legal_id,
            ),
            "regime": [],
        }

    def test_critical_without_legal_identity_rejected(self) -> None:
        kwargs = self._base_entry_kwargs(RiskTier.CRITICAL, legal_id=None)
        with pytest.raises(ValidationError) as exc_info:
            GPREntry(**kwargs)
        assert "legal_identity" in str(exc_info.value)

    def test_critical_with_legal_identity_accepted(self) -> None:
        kwargs = self._base_entry_kwargs(
            RiskTier.CRITICAL, legal_id=_valid_legal_identity()
        )
        entry = GPREntry(**kwargs)
        assert entry.authority.legal_identity is not None
        assert entry.authority.legal_identity.name == "ACME Health Systems Inc."

    def test_high_without_legal_identity_accepted(self) -> None:
        kwargs = self._base_entry_kwargs(RiskTier.HIGH, legal_id=None)
        entry = GPREntry(**kwargs)
        assert entry.authority.legal_identity is None

    def test_managed_without_legal_identity_accepted(self) -> None:
        kwargs = self._base_entry_kwargs(RiskTier.MANAGED, legal_id=None)
        entry = GPREntry(**kwargs)
        assert entry.authority.legal_identity is None


class TestRegistrationIdFormats:
    """The registration_id field accepts multiple jurisdictional formats."""

    def test_lei_format(self) -> None:
        legal_id = _valid_legal_identity(registration_id="LEI:5493001K3F3DUM2KRD89")
        assert legal_id.registration_id.startswith("LEI:")

    def test_eu_eori_format(self) -> None:
        legal_id = _valid_legal_identity(registration_id="EORI:DE123456789012345")
        assert legal_id.registration_id.startswith("EORI:")

    def test_uk_companies_house_format(self) -> None:
        legal_id = _valid_legal_identity(registration_id="UK-CRN:01234567")
        assert legal_id.registration_id.startswith("UK-CRN:")

    def test_de_handelsregister_format(self) -> None:
        legal_id = _valid_legal_identity(registration_id="DE-HRB:123456")
        assert legal_id.registration_id.startswith("DE-HRB:")
