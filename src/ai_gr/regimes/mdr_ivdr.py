"""
ai_gr.regimes.mdr_ivdr — EU Medical Device Regulation / In Vitro Diagnostic Regulation.

Regulation (EU) 2017/745 (MDR) and Regulation (EU) 2017/746 (IVDR). Apply
to software with a medical purpose ('software as a medical device' in EU
terminology). The EU-jurisdiction equivalent of the US FDA SaMD regime.

For an AI system deployed in EU healthcare contexts, MDR/IVDR applies in
addition to the EU AI Act (the AI Act explicitly does not displace
medical-device regulation) and in addition to the GDPR.

MDR Rule 11 classifies most clinical decision support software as Class IIa
or IIb depending on intended use; some life-support roles can reach Class III.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class MdrIvdr(Regime):
    identifier = "MDR-IVDR"
    name = "EU Medical Device / IVD Regulation (EU 2017/745, 2017/746)"
    description = (
        "EU medical-device and in-vitro-diagnostic regulation. Applies to software "
        "with a medical purpose. Administered by EMA for centrally-regulated "
        "products and by Member State competent authorities for most cases."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="MDR Annex I — General safety and performance requirements",
                description=(
                    "Devices shall achieve the performance intended by their manufacturer and "
                    "be designed and manufactured in such a way that they are suitable for "
                    "their intended purpose."
                ),
                relevant_gates=(Gate.BUILD, Gate.DEPLOY),
                evidence_needed=(
                    "evidence.evaluations covering safety and performance",
                ),
            ),
            RegimeRequirement(
                citation="MDR Rule 11 — Classification of software",
                description=(
                    "Software intended to provide information used to take decisions with "
                    "diagnosis or therapeutic purposes is classified Class IIa, IIb, or III "
                    "depending on the potential to cause death, serious deterioration, or "
                    "serious health impact."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.mdr_classification with the assigned class",
                    "evidence.additional.intended_use document",
                ),
            ),
            RegimeRequirement(
                citation="MDR Annex II — Technical documentation",
                description=(
                    "Manufacturers shall draw up technical documentation enabling assessment "
                    "of conformity with the regulation, including device description, "
                    "design and manufacturing information, and clinical evaluation."
                ),
                relevant_gates=(Gate.BUILD,),
                evidence_needed=(
                    "evidence.additional.technical_documentation reference",
                    "evidence.additional.clinical_evaluation reference",
                ),
            ),
            RegimeRequirement(
                citation="MDR Article 83 — Post-market surveillance",
                description=(
                    "Manufacturers shall plan, establish, document, implement, maintain, "
                    "and update a post-market surveillance system."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate runtime attestations forming the PMS evidence chain",
                ),
            ),
            RegimeRequirement(
                citation="MDR Article 87 — Vigilance reporting",
                description=(
                    "Serious incidents and field safety corrective actions shall be reported "
                    "to competent authorities within statutory deadlines (immediate for "
                    "serious public-health threats; within 10 days otherwise)."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate serious-incident attestations with timestamps",
                ),
            ),
            RegimeRequirement(
                citation="MDR Article 61 — Clinical evaluation",
                description=(
                    "Clinical evaluation and its documentation shall be conducted "
                    "throughout the lifecycle of the device."
                ),
                relevant_gates=(Gate.BUILD, Gate.EVOLVE),
                evidence_needed=(
                    "evidence.additional.clinical_evaluation_report",
                    "evolve-gate entries for clinical-evaluation updates",
                ),
            ),
        ]


_register(MdrIvdr())
