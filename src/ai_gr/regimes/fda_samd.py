"""
ai_gr.regimes.fda_samd — FDA Software as a Medical Device + PCCP mapping.

FDA regulates AI/ML-enabled SaMD under existing medical device authorities
(21 CFR 820, ISO 13485, IEC 62304). The 2024 final guidance on Predetermined
Change Control Plans (PCCPs) introduced lifecycle-aware regulation that maps
naturally to the Ribbon's Evolve gate.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class FDASaMD(Regime):
    identifier = "FDA-SaMD"
    name = "FDA Software as a Medical Device (incl. PCCP guidance)"
    description = (
        "US FDA regulation of AI/ML-enabled medical devices. Risk-stratified "
        "by IMDRF SaMD framework. Predetermined Change Control Plans (PCCPs) "
        "permit pre-authorized model evolution post-market."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="21 CFR 820.30 — Design controls",
                description="Establish and maintain procedures to control the design of the device to ensure that specified design requirements are met.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=("design_history_file",),
            ),
            RegimeRequirement(
                citation="IEC 62304 §5.5 — Software unit verification",
                description="Verify each software unit against its detailed design.",
                relevant_gates=(Gate.BUILD,),
                evidence_needed=("evaluations",),
            ),
            RegimeRequirement(
                citation="PCCP Final Guidance §IV — Modification Protocol",
                description="Pre-specify the types of modifications that may be made post-market, the methods for implementing them, and the methods for evaluating their impact.",
                relevant_gates=(Gate.BUILD, Gate.EVOLVE),
                evidence_needed=("pccp_document",),
            ),
            RegimeRequirement(
                citation="21 CFR 820.198 — Complaint handling",
                description="Maintain procedures for receiving, reviewing, and evaluating complaints.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("complaint_records",),
            ),
            RegimeRequirement(
                citation="21 CFR 803 — Medical Device Reporting",
                description="Report deaths, serious injuries, and malfunctions to FDA.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("mdr_records",),
            ),
            RegimeRequirement(
                citation="FDA AI/ML Action Plan §3 — Real-World Performance",
                description="Demonstrate real-world performance monitoring for AI/ML SaMD.",
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=("real_world_performance",),
            ),
            RegimeRequirement(
                citation="Demographic performance reporting",
                description="Performance is reported sliced by demographic subgroups (PCCP §V).",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("subgroup_performance",),
            ),
        ]


_register(FDASaMD())
