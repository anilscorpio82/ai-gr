"""
ai_gr.regimes — Regulatory regime registry.

Each regime is a structured description of:

  - Identifier (used in GPR ``regime[].regime`` strings)
  - Citation references
  - Which Ribbon gates it requires evidence at
  - Which evidence fields it consumes
  - A renderer that emits a regulator-ready export from a GPR chain

This is the "build the evidence once; map it many times" layer. The same
``Evidence`` block on a Build-tier entry can satisfy an EU AI Act conformity
assessment, a NIST AI RMF Manage function, a GDPR DPIA attestation, and a
HIPAA Security Rule documentation requirement simultaneously — because the
regime modules know how to read the same evidence through different
regulatory lenses.

Coverage in v0.2.0 (16 regimes):
  - EU AI Act (provider) + Article 26 (deployer)
  - GDPR
  - NIS2, MDR/IVDR, DORA, DSA, Data Act, Cyber Resilience Act, EHDS
  - NIST AI RMF + GenAI Profile
  - ISO/IEC 42001
  - HIPAA + HITECH
  - FDA SaMD + PCCP
  - SEC cyber + AI disclosure
  - US State ADMT/AEDT laws
"""

# Importing the regime modules registers them with the registry.
from ai_gr.regimes import (  # noqa: F401
    cra,
    data_act,
    dora,
    dsa,
    ehds,
    eu_ai_act,
    eu_ai_act_deployer,
    fda_samd,
    gdpr,
    hipaa,
    iso_42001,
    mdr_ivdr,
    nis2,
    nist_ai_rmf,
    sec_cyber,
    state_aedt,
)
from ai_gr.regimes.base import Regime, RegimeRegistry, get_regime, list_regimes

__all__ = ["Regime", "RegimeRegistry", "get_regime", "list_regimes"]
