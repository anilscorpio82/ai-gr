"""
ai_gr.regimes.dsa — Digital Services Act.

Regulation (EU) 2022/2065. Applies to intermediary services with EU users.
Article 27 algorithmic transparency, Article 34/35 risk assessment for Very
Large Online Platforms (VLOPs), and Article 38 recommender system
transparency are most relevant for AI-using platforms.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class DSA(Regime):
    identifier = "DSA"
    name = "Digital Services Act (EU 2022/2065)"
    description = (
        "EU regulation on intermediary services. AI-GR maps the algorithmic "
        "transparency and systemic risk assessment obligations to Ribbon gates."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 27 — Recommender system transparency",
                description=(
                    "Providers of online platforms shall set out the main parameters used in "
                    "their recommender systems in their terms and conditions in a plain and "
                    "intelligible manner."
                ),
                relevant_gates=(Gate.CONCEIVE, Gate.OPERATE),
                evidence_needed=(
                    "evidence.additional.recommender_parameters_disclosure",
                ),
            ),
            RegimeRequirement(
                citation="Article 34 — Risk assessment (VLOPs)",
                description=(
                    "Very Large Online Platforms shall identify, analyse and assess any "
                    "systemic risks stemming from the design, functioning or use of their "
                    "services."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.evaluations covering systemic risk assessment",
                ),
            ),
            RegimeRequirement(
                citation="Article 35 — Mitigation of risks (VLOPs)",
                description=(
                    "Reasonable, proportionate and effective mitigation measures, including "
                    "adapting algorithmic systems, where the assessment under Article 34 "
                    "identifies risks."
                ),
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=(
                    "operate/evolve-gate entries documenting mitigation measures",
                ),
            ),
        ]


_register(DSA())
