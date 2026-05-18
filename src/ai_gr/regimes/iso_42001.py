"""
ai_gr.regimes.iso_42001 — ISO/IEC 42001:2023 Artificial Intelligence Management System.

ISO/IEC 42001:2023 is the first international management system standard for AI.
Modeled on the ISO management system family (9001, 27001, 14001), it specifies
requirements for establishing, implementing, maintaining, and continually
improving an AI management system within an organization.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class ISO42001(Regime):
    identifier = "ISO-42001"
    name = "ISO/IEC 42001:2023 (AI Management System)"
    description = (
        "International management system standard for AI. Auditable certification "
        "track; widely adopted as the procurement baseline for enterprise AI."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Clause 5.1 — Leadership and commitment",
                description="Top management demonstrates leadership and commitment to the AI management system.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("leadership_commitment",),
            ),
            RegimeRequirement(
                citation="Clause 6.1.2 — AI risk assessment",
                description="Organization plans actions to address AI risks and opportunities.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=("risk_assessment",),
            ),
            RegimeRequirement(
                citation="Clause 7.5 — Documented information",
                description="AI management system includes documented information required by the standard.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD, Gate.DEPLOY, Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=("documentation",),
            ),
            RegimeRequirement(
                citation="Clause 8.2 — AI system impact assessment",
                description="Conduct AI system impact assessments at planned intervals.",
                relevant_gates=(Gate.CONCEIVE, Gate.EVOLVE),
                evidence_needed=("impact_assessment",),
            ),
            RegimeRequirement(
                citation="Clause 9.1 — Monitoring, measurement, analysis, evaluation",
                description="Organization determines what needs to be monitored and measured.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("monitoring_results",),
            ),
            RegimeRequirement(
                citation="Annex A.6.2.6 — AI system verification and validation",
                description="V&V activities are performed at appropriate points in the lifecycle.",
                relevant_gates=(Gate.BUILD, Gate.DEPLOY),
                evidence_needed=("evaluations",),
            ),
            RegimeRequirement(
                citation="Annex A.8.2 — AI system operation and monitoring",
                description="System operation is monitored throughout the AI lifecycle.",
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=("operational_logs",),
            ),
        ]


_register(ISO42001())
