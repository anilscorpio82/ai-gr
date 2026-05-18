"""
ai_gr.regimes.gdpr — General Data Protection Regulation.

Regulation (EU) 2016/679. The EU AI Act explicitly defers to the GDPR for
personal data processing (Recital 9, Article 2(7)). Every Critical-tier
deployment in EU jurisdictions will be simultaneously subject to the GDPR.

Maps to §5.4 of the v1.4 AI-GR paper.

References:
  - Article 5(2): accountability principle
  - Article 6: lawful basis for processing
  - Article 9: special-category data (special basis required)
  - Article 17: right to erasure
  - Article 26: joint controllers
  - Article 28: processor relationships
  - Article 35: Data Protection Impact Assessment
  - Chapter V: cross-border transfers

Article 17 right-to-erasure interacts structurally with append-only chains;
v0.2.0 follows the EDPB Guidelines 02/2025 patterns: personal data is held
off-chain by reference (Pattern 1) and chain entries remain valid as
records-of-fact after underlying data erasure (Pattern 2).
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class GDPR(Regime):
    identifier = "GDPR"
    name = "General Data Protection Regulation (EU 2016/679)"
    description = (
        "EU data protection regulation. Applies in parallel with the EU AI Act for "
        "any AI deployment processing personal data of EU data subjects. AI-GR v0.2.0 "
        "implements the EDPB Guidelines 02/2025 patterns for blockchain/append-only "
        "chain compatibility."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 5(2) — Accountability principle",
                description=(
                    "The controller shall be responsible for, and be able to demonstrate "
                    "compliance with, the data protection principles."
                ),
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD, Gate.OPERATE),
                evidence_needed=(
                    "GPR chain itself serves as accountability evidence",
                    "authority.legal_identity.gdpr_role attestation",
                ),
            ),
            RegimeRequirement(
                citation="Article 6 — Lawful basis",
                description=(
                    "Each processing operation must have an identifiable lawful basis "
                    "under Article 6(1)(a)-(f): consent, contract, legal obligation, "
                    "vital interests, public interest, or legitimate interests."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.lawful_basis naming one of Art. 6(1) bases",
                ),
            ),
            RegimeRequirement(
                citation="Article 9 — Special category data",
                description=(
                    "For processing of special-category data (health, biometric, race, "
                    "political opinion, etc.), an Article 9(2) condition must additionally "
                    "be identified."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.article_9_basis if special-category data is processed",
                ),
            ),
            RegimeRequirement(
                citation="Article 17 — Right to erasure",
                description=(
                    "Data subjects have the right to erasure of personal data in specified "
                    "circumstances. AI-GR follows EDPB 02/2025 patterns: personal data is "
                    "held off-chain by reference; chain entries remain valid as "
                    "records-of-fact (under Art. 17(3)(e) legitimate-interest balancing) "
                    "after underlying data is erased."
                ),
                relevant_gates=(Gate.OPERATE, Gate.EVOLVE),
                evidence_needed=(
                    "evidence.datasets stored off-chain by hash reference",
                    "operate-gate entries documenting Art. 17 request handling",
                ),
            ),
            RegimeRequirement(
                citation="Article 26 — Joint controllers",
                description=(
                    "Where two or more controllers jointly determine purposes and means of "
                    "processing, they must transparently determine their respective "
                    "responsibilities by arrangement."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "authority.legal_identity.gdpr_role = JOINT_CONTROLLER",
                    "evidence.additional.joint_controller_arrangement reference",
                ),
            ),
            RegimeRequirement(
                citation="Article 28 — Processor relationships",
                description=(
                    "Processing by a processor shall be governed by a contract binding "
                    "the processor to the controller and setting out subject-matter, "
                    "duration, nature, purpose, and processor obligations."
                ),
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=(
                    "authority.legal_identity.gdpr_role = PROCESSOR (where applicable)",
                    "evidence.additional.processor_contract reference",
                ),
            ),
            RegimeRequirement(
                citation="Article 35 — Data Protection Impact Assessment",
                description=(
                    "DPIA required before processing likely to result in high risk to "
                    "the rights and freedoms of natural persons. The Conceive gate is the "
                    "natural locus for DPIA evidence."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "evidence.additional.dpia reference to DPIA document",
                    "decision.conditions reflecting DPIA risk-treatment decisions",
                ),
            ),
            RegimeRequirement(
                citation="Chapter V — Cross-border transfers",
                description=(
                    "Transfers of personal data to third countries require an adequacy "
                    "decision, appropriate safeguards (SCCs, BCRs), or a derogation under "
                    "Article 49."
                ),
                relevant_gates=(Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=(
                    "evidence.additional.chapter_v_mechanism attestation for any transfer",
                ),
            ),
        ]


_register(GDPR())
