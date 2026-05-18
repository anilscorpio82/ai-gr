"""
ai_gr.regimes.cra — EU Cyber Resilience Act.

Regulation (EU) on horizontal cybersecurity requirements for products with
digital elements. Provides essential cybersecurity requirements applicable
across the lifecycle of products with digital elements, including AI software.

Key obligations include security-by-design, vulnerability handling, incident
reporting, and provision of SBOM information.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class CRA(Regime):
    identifier = "CRA"
    name = "EU Cyber Resilience Act"
    description = (
        "EU horizontal cybersecurity regulation for products with digital elements. "
        "AI-GR maps the security-by-design, SBOM, vulnerability handling, and "
        "incident reporting obligations to Ribbon gates."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Annex I §1 — Essential cybersecurity requirements (security-by-design)",
                description=(
                    "Products with digital elements shall be designed, developed and "
                    "produced in such a way that they ensure an appropriate level of "
                    "cybersecurity based on the risks."
                ),
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=(
                    "evidence.evaluations covering security-by-design assessment",
                ),
            ),
            RegimeRequirement(
                citation="Annex I §2 — Vulnerability handling",
                description=(
                    "Manufacturers shall identify and document vulnerabilities and "
                    "components contained in the product, including by drawing up an SBOM."
                ),
                relevant_gates=(Gate.BUILD, Gate.EVOLVE),
                evidence_needed=(
                    "evidence.sbom in SPDX or CycloneDX format",
                    "evidence.red_team referencing vulnerability inventory",
                ),
            ),
            RegimeRequirement(
                citation="Article 11 — Reporting obligations of manufacturers",
                description=(
                    "Manufacturers shall report actively exploited vulnerabilities and "
                    "severe incidents to ENISA without undue delay (24h early warning, "
                    "72h notification, final report within 14 days)."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate incident attestations with 24h/72h/14d timestamps",
                ),
            ),
            RegimeRequirement(
                citation="Article 13 — Support period",
                description=(
                    "Manufacturers shall ensure vulnerabilities of the product are handled "
                    "effectively throughout the support period (≥5 years where appropriate)."
                ),
                relevant_gates=(Gate.EVOLVE,),
                evidence_needed=(
                    "evolve-gate entries spanning the declared support period",
                ),
            ),
        ]


_register(CRA())
