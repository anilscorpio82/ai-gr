"""
ai_gr.regimes.eu_ai_act — EU AI Act mapping.

Regulation (EU) 2024/1689. Entered into force August 1, 2024. Full
applicability August 2, 2026, with potential extension to December 2027 for
Annex III high-risk systems per the November 2025 "AI Omnibus" amendments.

References:
  - Article 9: Risk management system
  - Article 10: Data and data governance
  - Article 11: Technical documentation
  - Article 12: Record-keeping (logs)
  - Article 13: Transparency and provision of information to deployers
  - Article 14: Human oversight
  - Article 15: Accuracy, robustness, and cybersecurity
  - Article 17: Quality management system
  - Article 72: Post-market monitoring
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class EUAIAct(Regime):
    identifier = "EU-AI-Act"
    name = "EU AI Act (Regulation 2024/1689)"
    description = (
        "EU's comprehensive AI regulation. Risk-based framework with prohibited, "
        "high-risk, limited-risk, and minimal-risk categories. Full applicability "
        "from August 2, 2026 (subject to AI Omnibus amendments)."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 9 — Risk management system",
                description="Establish, implement, document, and maintain a risk management system across the AI system lifecycle.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD, Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=("risk_assessment", "mitigation_measures"),
            ),
            RegimeRequirement(
                citation="Article 10 — Data and data governance",
                description="Training, validation, and testing datasets must meet quality criteria; document data provenance.",
                relevant_gates=(Gate.BUILD,),
                evidence_needed=("datasets", "data_governance_record"),
            ),
            RegimeRequirement(
                citation="Article 11 — Technical documentation",
                description="Draw up technical documentation before placing on market or putting into service.",
                relevant_gates=(Gate.BUILD, Gate.DEPLOY),
                evidence_needed=("technical_documentation",),
            ),
            RegimeRequirement(
                citation="Article 12 — Record-keeping (logs)",
                description="High-risk systems must automatically log events during operation.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("operational_logs",),
            ),
            RegimeRequirement(
                citation="Article 13 — Transparency",
                description="High-risk systems must be sufficiently transparent for deployers to interpret outputs.",
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=("user_documentation",),
            ),
            RegimeRequirement(
                citation="Article 14 — Human oversight",
                description="High-risk systems must be designed so that natural persons can effectively oversee them.",
                relevant_gates=(Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=("human_oversight_design",),
            ),
            RegimeRequirement(
                citation="Article 15 — Accuracy, robustness, cybersecurity",
                description="Achieve appropriate level of accuracy, robustness, and cybersecurity throughout lifecycle.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("accuracy_metrics", "robustness_tests", "cybersecurity_controls"),
            ),
            RegimeRequirement(
                citation="Article 72 — Post-market monitoring",
                description="Establish and document a post-market monitoring system proportionate to the risks.",
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=("post_market_monitoring_plan",),
            ),
        ]


_register(EUAIAct())
