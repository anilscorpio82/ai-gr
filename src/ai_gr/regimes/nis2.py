"""
ai_gr.regimes.nis2 — NIS2 Directive cybersecurity risk management.

Directive (EU) 2022/2555 (NIS2) on measures for a high common level of
cybersecurity across the Union. Applies to essential and important entities
across 18 sectors including digital infrastructure, healthcare, banking,
energy, transport, and ICT service management.

Article 21 cybersecurity risk management measures and Article 23 reporting
obligations have direct overlap with AI-GR Build/Deploy/Operate gates for
AI systems deployed by NIS2-regulated entities.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class NIS2(Regime):
    identifier = "NIS2"
    name = "NIS2 Directive (EU 2022/2555)"
    description = (
        "EU cybersecurity directive applying to essential and important entities. "
        "AI-GR maps the cybersecurity risk-management and incident-reporting "
        "obligations to Ribbon gates where AI is part of the in-scope system."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 21(1) — Cybersecurity risk-management measures",
                description=(
                    "Appropriate and proportionate technical, operational and organisational "
                    "measures to manage cybersecurity risks to network and information systems."
                ),
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=(
                    "evidence.evaluations covering risk-management measures",
                    "evidence.sbom for supply-chain risk identification",
                ),
            ),
            RegimeRequirement(
                citation="Article 21(2)(a) — Risk analysis and information system security policies",
                description="Policies on risk analysis and information system security.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=("evidence.evaluations referencing risk-analysis policy",),
            ),
            RegimeRequirement(
                citation="Article 21(2)(d) — Supply chain security",
                description=(
                    "Supply chain security, including security-related aspects concerning the "
                    "relationships between each entity and its direct suppliers or service providers."
                ),
                relevant_gates=(Gate.BUILD,),
                evidence_needed=("evidence.sbom in SPDX or CycloneDX format",),
            ),
            RegimeRequirement(
                citation="Article 21(2)(e) — Vulnerability handling and disclosure",
                description=(
                    "Security in network and information systems acquisition, development "
                    "and maintenance, including vulnerability handling and disclosure."
                ),
                relevant_gates=(Gate.BUILD, Gate.EVOLVE),
                evidence_needed=(
                    "evidence.red_team results referencing vulnerability inventory",
                    "evolve-gate entries for security patches",
                ),
            ),
            RegimeRequirement(
                citation="Article 23 — Reporting obligations",
                description=(
                    "Early warning of significant incident within 24h; incident notification "
                    "within 72h; final report within one month."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate incident attestations with timestamps satisfying 24h/72h/1mo windows",
                ),
            ),
        ]


_register(NIS2())
