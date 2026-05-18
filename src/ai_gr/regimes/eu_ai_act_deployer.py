"""
ai_gr.regimes.eu_ai_act_deployer — EU AI Act Article 26 deployer obligations.

Regulation (EU) 2024/1689 Article 26 imposes obligations on *deployers* of
high-risk AI systems, which apply independently of the provider's own
conformity activities. Compliance enforcement begins 2 August 2026.

Most enterprise AI adopters are deployers (using a third-party-developed
system) rather than providers (placing one on the market). The deployer
regime is therefore the most operationally relevant slice of the EU AI Act
for typical AI-GR adopters.

Maps to §5.5 (Table 6) of the v1.4 AI-GR paper.

References:
  - Article 26(1)+(3): use system per provider instructions
  - Article 26(2): human oversight by natural persons with competence
  - Article 26(4): input-data governance where deployer controls input
  - Article 26(5): monitoring; inform provider per Art. 72; suspend if risk
  - Article 26(6): log retention ≥6 months
  - Article 26(7): worker notification before workplace deployment
  - Article 26(8): public-sector and EU-institution registration
  - Article 26(9): use provider Art. 13 info for GDPR Art. 35 DPIA
  - Article 27: Fundamental Rights Impact Assessment for applicable deployers
  - Article 73: serious incident reporting within 15 days
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class EUAIActDeployer(Regime):
    identifier = "EU-AI-Act-Deployer"
    name = "EU AI Act Article 26 — Deployer Obligations"
    description = (
        "Obligations on deployers of high-risk AI systems under Article 26 of "
        "Regulation (EU) 2024/1689. Applies independently of provider conformity "
        "activities. Enforcement begins 2 August 2026."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="Article 26(1)+(3) — Use per provider instructions",
                description=(
                    "Take appropriate technical and organisational measures to ensure use "
                    "in accordance with the instructions for use accompanying the system."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate attestation of instruction-conforming use",
                    "hash of provider's instructions-for-use document",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(2) — Competent human oversight",
                description=(
                    "Assign human oversight to natural persons with the necessary "
                    "competence, training, authority, and support."
                ),
                relevant_gates=(Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=(
                    "agentic_context.human_oversight value",
                    "authority.legal_identity naming responsible natural person(s)",
                    "evidence.additional carrying oversight-training attestation",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(4) — Input data governance",
                description=(
                    "Where the deployer controls input data, ensure that input data is "
                    "relevant and sufficiently representative in view of the intended purpose."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "evidence.datasets attesting to deployer-controlled input data governance",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(5) — Monitoring and incident response",
                description=(
                    "Monitor operation on the basis of the instructions for use. Inform "
                    "the provider per Art. 72; suspend use if Art. 79(1) risk is identified; "
                    "report serious incidents per Art. 73 within 15 days."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate entries with decision=rollback or decision_with_conditions",
                    "serious-incident attestations with 15-day timestamps per Art. 73",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(6) — Log retention ≥6 months",
                description=(
                    "Keep automatically generated logs for a period appropriate to the "
                    "intended purpose, of at least six months. Financial institutions may "
                    "satisfy via existing internal governance arrangements (subpar. 2)."
                ),
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=(
                    "operate-gate runtime attestation chain spanning ≥6 months",
                    "chain integrity demonstration across retention period",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(7) — Worker notification",
                description=(
                    "Notify workers and their representatives before workplace deployment."
                ),
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=(
                    "deploy-gate entry attesting to worker notification",
                    "evidence.additional carrying the notification record",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(8) — EU database registration",
                description=(
                    "Public-sector and EU-institution deployers register in the EU "
                    "database referred to in Article 49."
                ),
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=(
                    "deploy-gate entry with regime='EU-AI-Act-Deployer:Art-49-registration'",
                ),
            ),
            RegimeRequirement(
                citation="Article 26(9) — GDPR DPIA cross-reference",
                description=(
                    "Use the information provided under Article 13 to comply with the "
                    "deployer's GDPR Article 35 DPIA obligation, where applicable."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "conceive-gate entry referencing provider Art. 13 information packet",
                    "conceive-gate entry referencing deployer DPIA",
                ),
            ),
            RegimeRequirement(
                citation="Article 27 — Fundamental Rights Impact Assessment",
                description=(
                    "Public-sector deployers, private entities providing public services, "
                    "and deployers of certain Annex III 5(b)/(c) systems (creditworthiness, "
                    "life/health insurance) must carry out a Fundamental Rights Impact Assessment."
                ),
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=(
                    "conceive-gate entry with FRIA reference in evidence.additional",
                ),
            ),
        ]


_register(EUAIActDeployer())
