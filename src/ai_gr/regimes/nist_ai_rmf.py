"""
ai_gr.regimes.nist_ai_rmf — NIST AI Risk Management Framework 1.0 + GenAI Profile.

References:
  - NIST AI 100-1 (AI RMF 1.0, January 2023)
  - NIST AI 600-1 (Generative AI Profile, July 2024)

The four core functions: Govern, Map, Measure, Manage. Each function expands
into categories and subcategories. We map the most commonly cited
subcategories to Ribbon gates.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class NISTAIRMF(Regime):
    identifier = "NIST-AI-RMF"
    name = "NIST AI Risk Management Framework 1.0 (incl. Generative AI Profile)"
    description = (
        "Voluntary US framework establishing AI risk management practices across "
        "four functions (Govern, Map, Measure, Manage). Authoritative reference "
        "for federal and many state AI governance regimes."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="GOVERN 1.1 — Policies and procedures",
                description="Legal and regulatory requirements involving AI are understood, managed, and documented.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("governance_policy",),
            ),
            RegimeRequirement(
                citation="MAP 1.1 — Context establishment",
                description="Intended purpose, potentially beneficial uses, and context-specific laws are understood and documented.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("use_case_documentation",),
            ),
            RegimeRequirement(
                citation="MAP 3.1 — Categorization",
                description="AI system is categorized by capability, intended purpose, and impact.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("system_categorization",),
            ),
            RegimeRequirement(
                citation="MEASURE 2.3 — Performance evaluation",
                description="AI system performance is regularly evaluated against documented metrics.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("evaluations",),
            ),
            RegimeRequirement(
                citation="MEASURE 2.6 — AI risks identified",
                description="AI system is evaluated for trustworthy characteristics (validity, reliability, safety, security, accountability, transparency, explainability, privacy, fairness).",
                relevant_gates=(Gate.BUILD,),
                evidence_needed=("evaluations", "red_team"),
            ),
            RegimeRequirement(
                citation="MANAGE 2.3 — Incidents and errors",
                description="Procedures are followed to respond to and recover from incidents involving the AI system.",
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=("incident_log", "rollback_procedure"),
            ),
            RegimeRequirement(
                citation="MANAGE 4.1 — Post-deployment monitoring",
                description="AI system performance is regularly monitored after deployment.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("monitoring_telemetry",),
            ),
            RegimeRequirement(
                citation="GenAI Profile GV 1.3 — GenAI-specific risks",
                description="Confabulation, dangerous content, data privacy, and harmful bias risks are governed.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("red_team",),
            ),
        ]


_register(NISTAIRMF())
