"""
ai_gr.regimes.sec_cyber — SEC cybersecurity disclosure + AI governance.

References:
  - 17 CFR 229.106 (Item 106 of Regulation S-K) — cybersecurity disclosures
  - 17 CFR 240.13a-11 (Form 8-K Item 1.05) — material cybersecurity incident reporting
  - SEC Staff Bulletin on AI disclosures (2024-2025)
  - Investor Advisory Committee recommendations on board AI oversight (2025)

For public companies, AI risk and AI-related incidents are increasingly
treated as material disclosure events. Cyber-insurance carriers are also
introducing "AI Security Riders" that condition coverage on documented
controls — making GPR-style evidence directly economically relevant.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class SECCyber(Regime):
    identifier = "SEC-Cyber"
    name = "SEC Cybersecurity Disclosure + AI Governance Oversight"
    description = (
        "US SEC requirements for cybersecurity risk management disclosure "
        "and material incident reporting, increasingly applied to AI systems "
        "and AI-related incidents."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Item 106(b) — Risk management and strategy",
                description="Disclose processes for assessing, identifying, and managing material risks from cybersecurity threats (and increasingly AI risks).",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("risk_management_process",),
            ),
            RegimeRequirement(
                citation="Item 106(c) — Governance",
                description="Disclose the board of directors' oversight of risks from cybersecurity threats and AI; management's role.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("governance_charter",),
            ),
            RegimeRequirement(
                citation="Form 8-K Item 1.05 — Material cybersecurity incidents",
                description="Disclose material cybersecurity (and AI) incidents within four business days of determining materiality.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("incident_log",),
            ),
            RegimeRequirement(
                citation="Cyber insurance AI Security Riders",
                description="Document AI-specific controls (adversarial red-teaming, model risk assessments) as conditions of coverage.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("red_team", "model_risk_assessment"),
            ),
        ]


_register(SECCyber())
