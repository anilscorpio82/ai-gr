"""
ai_gr.schema — The Governance Provenance Record (GPR) schema.

This module defines the canonical Pydantic models for a GPR entry. The schema
is the IP core of the AI-GR framework: every field has a defined relationship
to one or more regulatory regimes, and every entry produced by this library
conforms to the JSON-LD shape declared here.

Originator: Anil Singh (May 2026).
Specification URL: https://ai-gr.dev/v1

Schema changes since v0.1.0:
- Added LegalIdentity sub-model and Authority.legal_identity field. Required
  for Critical-tier entries per §4.3 of the v1.2+ paper. The DID layer
  provides cryptographic binding; the legal_identity layer provides regulatory
  binding under regimes like the EU AI Act (Article 47 Declaration of
  Conformity) and HIPAA (Business Associate Agreement framework).
- Replaced json.dumps(sort_keys=True) canonicalization with RFC 8785 (JCS)
  via the rfc8785 library. The prior approach diverged from JCS on float
  rendering (1.0 vs 1, scientific notation) and a few other edge cases.
  v0.2.0 GPR entry hashes are not byte-identical to v0.1.0 hashes for
  entries containing floats; this is a one-time transition cost in exchange
  for full RFC compliance.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

import rfc8785
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

# ---------------------------------------------------------------------------
# Canonical constants — DO NOT change without versioning the schema.
# ---------------------------------------------------------------------------

#: JSON-LD context URL. Every GPR entry references this. Changes to the
#: schema shape require a new version path (v2, v3, ...).
AI_GR_CONTEXT = "https://ai-gr.dev/v1"

#: Schema version. Bumped with every breaking change.
SCHEMA_VERSION = "0.2.0"

#: URN scheme. GPR entry IDs are URNs in the form:
#:     urn:gpr:<org>/<system>/<gate>/<sequence>
URN_PREFIX = "urn:gpr:"

URN_PATTERN = re.compile(
    r"^urn:gpr:[a-z0-9][a-z0-9\-]*"  # org
    r"/[a-z0-9][a-z0-9\-]*"          # system
    r"/(conceive|build|deploy|operate|evolve|retire)"
    r"/\d{4,}$"
)

Sha256Hex = Annotated[
    str,
    StringConstraints(pattern=r"^[a-f0-9]{64}$"),
]

#: ISO 3166-1 alpha-2 country code (two upper-case letters).
Iso3166Alpha2 = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{2}$"),
]


# ---------------------------------------------------------------------------
# Enumerations — the framework's vocabulary.
# ---------------------------------------------------------------------------


class Gate(StrEnum):
    """The five lifecycle gates of the Ribbon, plus Retire."""

    CONCEIVE = "Conceive"
    BUILD = "Build"
    DEPLOY = "Deploy"
    OPERATE = "Operate"
    EVOLVE = "Evolve"
    RETIRE = "Retire"


class RiskTier(StrEnum):
    """The three risk tiers of the Ribbon."""

    CRITICAL = "Critical"  # EU AI Act high-risk, HIPAA PHI, FDA SaMD, ADMT
    HIGH = "High"          # Material business or consumer-facing impact
    MANAGED = "Managed"    # Internal productivity, low-stakes assistive AI


class Decision(StrEnum):
    """The decision rendered at a Ribbon gate."""

    APPROVE = "approve"
    APPROVE_WITH_CONDITIONS = "approve_with_conditions"
    REJECT = "reject"
    ROLLBACK = "rollback"
    DEFER = "defer"


class SystemType(StrEnum):
    """High-level taxonomy of governed systems."""

    PREDICTIVE = "predictive"
    GENERATIVE = "generative"
    AGENTIC = "agentic"
    HYBRID = "hybrid"


class GdprRole(StrEnum):
    """GDPR role of the legally responsible person.

    Set on LegalIdentity for any deployment subject to GDPR. Joint
    controllership under GDPR Article 26 should use JOINT_CONTROLLER and
    reference a joint_controller_arrangement document in evidence.additional.
    """

    CONTROLLER = "controller"
    JOINT_CONTROLLER = "joint_controller"
    PROCESSOR = "processor"
    SUB_PROCESSOR = "sub_processor"
    NOT_APPLICABLE = "not_applicable"


# ---------------------------------------------------------------------------
# Sub-models — the building blocks of a GPR entry.
# ---------------------------------------------------------------------------


class Subject(BaseModel):
    """The system, model, or agent being governed."""

    model_config = ConfigDict(extra="forbid")

    system: str = Field(..., description="System identifier.")
    version: str = Field(..., description="Semantic version of the system.")
    type: SystemType = Field(..., description="System taxonomy.")
    description: str | None = Field(None, description="Optional human-readable description.")


class Evidence(BaseModel):
    """Evidence produced or referenced at this gate."""

    model_config = ConfigDict(extra="forbid")

    datasets: list[str] = Field(default_factory=list)
    evaluations: list[str] = Field(default_factory=list)
    red_team: list[str] = Field(default_factory=list)
    model_weights: Sha256Hex | None = Field(None)
    sbom: str | None = Field(None)
    additional: dict[str, Any] = Field(default_factory=dict)


class LegalIdentity(BaseModel):
    """The legally responsible person bound by the regulatory obligations.

    Required for Critical-tier entries per §4.3 of the AI-GR paper. The DID
    layer (Authority.approver) provides cryptographic authentication; the
    legal_identity layer provides the named legal person that regulators
    require for conformity assessments, Business Associate Agreements, and
    Article 47 Declarations of Conformity.

    A DID-based identifier satisfies cryptographic authentication but does
    not, on its own, identify the legal person bound by the EU AI Act's
    obligations. The same applies under HIPAA. Both layers are required for
    regulated deployments.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Registered legal name of the responsible person or entity.",
        min_length=1,
    )
    registration_id: str = Field(
        ...,
        description=(
            "Jurisdictional registration identifier. Acceptable formats include "
            "ISO 17442 LEI (20 alphanumeric characters), EU EORI, or a national "
            "company-register number (e.g. UK Companies House CRN, "
            "DE Handelsregister HRB number, FR INPI SIREN)."
        ),
        min_length=1,
    )
    jurisdiction: Iso3166Alpha2 = Field(
        ...,
        description="ISO 3166-1 alpha-2 country code where the entity is registered.",
    )
    address: str = Field(
        ...,
        description="Registered business address of the entity.",
        min_length=1,
    )
    contact_email: str = Field(
        ...,
        description="Contact email for compliance and regulatory correspondence.",
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    gdpr_role: GdprRole | None = Field(
        None,
        description=(
            "GDPR role of this legal identity. Required for deployments subject "
            "to GDPR. Use NOT_APPLICABLE for deployments outside GDPR scope."
        ),
    )


class Authority(BaseModel):
    """Who decided, and what authority they had to decide.

    Authority is verifiable, not asserted. The DID layer provides cryptographic
    authentication; the legal_identity layer (required for Critical tier)
    provides regulatory binding.
    """

    model_config = ConfigDict(extra="forbid")

    approver: str = Field(
        ...,
        description="DID of the approver, e.g. 'did:web:acme-health:caio'.",
        pattern=r"^did:[a-z0-9]+:.+$",
    )
    delegated_scope: str = Field(
        ...,
        description="Capability-style scope, e.g. 'tier:critical;phi:read'.",
    )
    co_approvers: list[str] = Field(default_factory=list)
    legal_identity: LegalIdentity | None = Field(
        None,
        description=(
            "Legally responsible person bound by the regulatory obligations. "
            "Required for Critical-tier entries; recommended for High; optional "
            "for Managed. Enforced by the GPREntry.model_post_init validator."
        ),
    )


class AgenticContext(BaseModel):
    """Agentic-native fields — the wedge over predictive/generative governance."""

    model_config = ConfigDict(extra="forbid")

    action_authority: list[str] = Field(default_factory=list)
    tool_registry: list[str] = Field(default_factory=list)
    runtime_context: dict[str, Any] = Field(default_factory=dict)
    human_oversight: str | None = Field(
        None,
        description="Human oversight mode: 'in-the-loop', 'on-the-loop', 'audit-only', 'none'.",
    )


class RegimeClaim(BaseModel):
    """A single regulatory claim made by this GPR entry."""

    model_config = ConfigDict(extra="forbid")

    regime: str = Field(
        ...,
        description=(
            "Regime identifier, e.g. 'EU-AI-Act:high-risk', 'EU-AI-Act:Art-26', "
            "'GDPR:Art-35-DPIA', 'HIPAA:164.312', 'NIST-AI-RMF:Manage-2.3', "
            "'MDR:Class-IIb', 'NIS2:Art-21'."
        ),
    )
    citation: str | None = Field(None)
    evidence_refs: list[str] = Field(default_factory=list)


class Linkage(BaseModel):
    """The provenance chain — what makes the GPR a chain, not a document."""

    model_config = ConfigDict(extra="forbid")

    prev_gpr: str | None = Field(None)
    prev_hash: Sha256Hex | None = Field(None)
    chain_root: str | None = Field(None)


class Attestation(BaseModel):
    """Cryptographic attestation of the entry."""

    model_config = ConfigDict(extra="forbid")

    signature: str | None = Field(None)
    signature_alg: str = Field("ed25519")
    public_key: str | None = Field(None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rfc3161_token: str | None = Field(None)
    tsa: str | None = Field(None)


# ---------------------------------------------------------------------------
# Top-level model — the GPR entry itself.
# ---------------------------------------------------------------------------


class GPREntry(BaseModel):
    """A single Governance Provenance Record entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "GPREntry",
            "description": "A Governance Provenance Record entry — the canonical AI-GR artifact.",
        },
    )

    context: str = Field(default=AI_GR_CONTEXT, alias="@context")
    type_: str = Field(default="GPREntry", alias="@type")
    schema_version: str = Field(default=SCHEMA_VERSION)

    id: str = Field(...)

    subject: Subject
    gate: Gate
    risk_tier: RiskTier
    decision: Decision
    evidence: Evidence
    authority: Authority
    regime: list[RegimeClaim] = Field(default_factory=list)

    agentic_context: AgenticContext | None = None

    linkage: Linkage = Field(default_factory=Linkage)
    attestation: Attestation = Field(default_factory=Attestation)

    # ----- Validators -----

    @field_validator("id")
    @classmethod
    def _validate_id_urn(cls, v: str) -> str:
        if not URN_PATTERN.match(v):
            raise ValueError(
                f"GPR entry id must match urn:gpr:<org>/<system>/<gate>/<seq>, got: {v}"
            )
        return v

    def model_post_init(self, __context: Any) -> None:
        # Invariant: agentic systems must carry an AgenticContext.
        if self.subject.type == SystemType.AGENTIC and self.agentic_context is None:
            raise ValueError(
                "Agentic systems must include an agentic_context block. "
                "Action authority, tool registry, and runtime context are "
                "non-optional for agents."
            )
        # Invariant: Critical-tier entries must carry legal_identity.
        # New in v0.2.0 per §4.3 of the v1.2+ AI-GR paper.
        if self.risk_tier == RiskTier.CRITICAL and self.authority.legal_identity is None:
            raise ValueError(
                "Critical-tier GPR entries must include authority.legal_identity. "
                "The DID layer provides cryptographic authentication; the "
                "legal_identity layer provides the named legal person required "
                "by the EU AI Act, HIPAA, and other regulatory regimes. See "
                "§4.3 of the AI-GR paper for the rationale."
            )

    # ----- Serialization helpers -----

    def to_jsonld(self) -> dict[str, Any]:
        """Render this entry as a JSON-LD dict."""
        return self.model_dump(by_alias=True, mode="json", exclude_none=False)

    def canonical_bytes(self) -> bytes:
        """Return the canonical byte representation for hashing.

        Uses RFC 8785 (JSON Canonicalization Scheme, JCS). Excludes the
        attestation block (signature is computed over the rest of the entry,
        so it cannot include itself).

        Changed in v0.2.0: previously used json.dumps(sort_keys=True), which
        diverged from RFC 8785 on float rendering (e.g. 1.0 vs 1, 1.5e-5 vs
        0.000015) and a few other edge cases. RFC 8785 compliance is
        required for chain interoperability across implementations.

        Note on Unicode: RFC 8785 does NOT mandate NFC normalization (that
        is I-JSON / RFC 7493). JCS preserves the input string bytes. Callers
        who need cross-encoding-form consistency should NFC-normalize their
        inputs before passing them to the schema.
        """
        payload = self.model_dump(by_alias=True, mode="json", exclude={"attestation"})
        return rfc8785.dumps(payload)

    def content_hash(self) -> str:
        """SHA-256 of the canonical byte representation (hex-encoded)."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# Re-exports for cleaner import paths.
__all__ = [
    "AI_GR_CONTEXT",
    "SCHEMA_VERSION",
    "URN_PREFIX",
    "AgenticContext",
    "Attestation",
    "Authority",
    "Decision",
    "Evidence",
    "GPREntry",
    "Gate",
    "GdprRole",
    "Iso3166Alpha2",
    "LegalIdentity",
    "Linkage",
    "RegimeClaim",
    "RiskTier",
    "Subject",
    "SystemType",
]
