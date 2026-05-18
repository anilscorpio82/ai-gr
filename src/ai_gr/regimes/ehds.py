"""
ai_gr.regimes.ehds — European Health Data Space.

Regulation on the European Health Data Space (EHDS). Establishes a common
framework for the use of electronic health data for primary use (healthcare
delivery) and secondary use (research, policymaking, regulatory purposes,
including AI training).

Most directly relevant for AI deployments that train on or process EU
electronic health data, particularly under the EHDS secondary-use regime.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class EHDS(Regime):
    identifier = "EHDS"
    name = "European Health Data Space"
    description = (
        "EU regulation establishing a common framework for electronic health data "
        "use across primary (healthcare delivery) and secondary (research, AI "
        "training, regulatory) purposes."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 33 — Categories of electronic health data for secondary use",
                description=(
                    "Defined categories of electronic health data may be processed for "
                    "specified secondary-use purposes including AI training, scientific "
                    "research, and public health."
                ),
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=(
                    "evidence.datasets attesting to EHDS data category and lawful "
                    "secondary-use purpose",
                ),
            ),
            RegimeRequirement(
                citation="Article 34 — Permit-based access to electronic health data",
                description=(
                    "Health data access bodies issue data permits allowing access to "
                    "electronic health data for specified secondary-use purposes."
                ),
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=(
                    "evidence.additional.ehds_data_permit reference",
                ),
            ),
            RegimeRequirement(
                citation="Article 50 — Secure processing environment",
                description=(
                    "Secondary-use processing of electronic health data shall take place "
                    "in a secure processing environment operated by the health data access "
                    "body."
                ),
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=(
                    "evidence.additional.secure_processing_environment_attestation",
                ),
            ),
            RegimeRequirement(
                citation="Article 51 — Anonymisation and pseudonymisation",
                description=(
                    "Health data access bodies shall ensure data is anonymised wherever "
                    "the purpose of the processing can be achieved with anonymised data; "
                    "otherwise pseudonymised data shall be provided."
                ),
                relevant_gates=(Gate.BUILD,),
                evidence_needed=(
                    "evidence.additional.anonymisation_method_attestation",
                ),
            ),
        ]


_register(EHDS())
