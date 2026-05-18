"""
AI-GR — The Agentic Governance Ribbon.

Reference implementation of the AI-GR framework and the Governance Provenance
Record (GPR) specification.

  Framework name :  AI-GR (Agentic Governance Ribbon)
  Artifact name  :  GPR (Governance Provenance Record)
  Originator     :  Anil Singh, May 2026
  Specification  :  https://ai-gr.dev/v1
  License        :  Apache 2.0
  Paper          :  https://doi.org/10.5281/zenodo.XXXXXXX (v1.4)
"""

from ai_gr.schema import (
    AI_GR_CONTEXT,
    SCHEMA_VERSION,
    AgenticContext,
    Attestation,
    Authority,
    Decision,
    Evidence,
    Gate,
    GdprRole,
    GPREntry,
    Iso3166Alpha2,
    LegalIdentity,
    Linkage,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "AI_GR_CONTEXT",
    "SCHEMA_VERSION",
    "AgenticContext",
    "Attestation",
    "Authority",
    "Decision",
    "Evidence",
    "Gate",
    "GdprRole",
    "GPREntry",
    "Iso3166Alpha2",
    "LegalIdentity",
    "Linkage",
    "RegimeClaim",
    "RiskTier",
    "Subject",
    "SystemType",
]
