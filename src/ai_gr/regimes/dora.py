"""
ai_gr.regimes.dora — Digital Operational Resilience Act.

Regulation (EU) 2022/2554. Applies to financial entities (banks, insurers,
investment firms, payment institutions, crypto-asset service providers) and
their ICT third-party service providers. Effective 17 January 2025.

DORA's ICT risk management framework intersects directly with AI deployment
in financial services: AI systems used for credit decisioning, fraud detection,
trading, or operational decisions fall within DORA scope.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class DORA(Regime):
    identifier = "DORA"
    name = "Digital Operational Resilience Act (EU 2022/2554)"
    description = (
        "EU regulation on digital operational resilience for the financial sector. "
        "AI-GR maps the ICT risk management and third-party risk management "
        "obligations to Ribbon gates."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 5 — ICT risk management framework",
                description=(
                    "Financial entities shall have a sound, comprehensive and well-"
                    "documented ICT risk management framework, including AI systems."
                ),
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD, Gate.OPERATE),
                evidence_needed=(
                    "evidence.evaluations covering ICT risk assessment",
                ),
            ),
            RegimeRequirement(
                citation="Article 8 — Identification of ICT supported business functions",
                description=(
                    "Identify, classify and adequately document all ICT supported business "
                    "functions, roles and responsibilities, including AI-supported functions."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.business_function_classification",
                ),
            ),
            RegimeRequirement(
                citation="Article 17 — ICT-related incident management",
                description=(
                    "Process to monitor, manage, log, classify and report ICT-related "
                    "incidents. Major incidents notified to competent authority within "
                    "regulatory deadlines."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate incident attestations",
                ),
            ),
            RegimeRequirement(
                citation="Article 25 — Contractual arrangements with ICT third-party providers",
                description=(
                    "Contracts with ICT third-party service providers shall include specific "
                    "minimum content, especially for critical functions."
                ),
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=(
                    "evidence.additional.third_party_contract_reference",
                ),
            ),
            RegimeRequirement(
                citation="Article 28 — Concentration risk on ICT third-party providers",
                description=(
                    "Assessment of concentration risk where critical or important functions "
                    "are supported by ICT third-party service providers."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.concentration_risk_assessment",
                ),
            ),
            RegimeRequirement(
                citation="Article 24 — Digital operational resilience testing",
                description=(
                    "Resilience testing programme including advanced threat-led penetration "
                    "testing (TLPT) for systemically important entities."
                ),
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=(
                    "evidence.red_team referencing TLPT or equivalent",
                ),
            ),
        ]


_register(DORA())
