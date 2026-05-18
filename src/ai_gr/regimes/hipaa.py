"""
ai_gr.regimes.hipaa — HIPAA Security Rule + HITECH mapping.

45 CFR Part 164 Subpart C (Security Standards) and Subpart D (Breach
Notification). HITECH (2009) extended HIPAA obligations to business
associates, which now includes most LLM providers when PHI is processed.

The HIPAA Security Rule's three safeguard categories (administrative,
physical, technical) map directly to multiple Ribbon gates. We focus on the
technical safeguards (164.312) and audit requirements that AI systems most
commonly need to address.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class HIPAA(Regime):
    identifier = "HIPAA"
    name = "HIPAA Security Rule + HITECH"
    description = (
        "US federal protection of electronic protected health information "
        "(ePHI). AI systems accessing PHI must implement administrative, "
        "physical, and technical safeguards; LLM providers are business "
        "associates requiring BAAs."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="45 CFR 164.308(a)(1) — Security management process",
                description="Implement policies and procedures to prevent, detect, contain, and correct security violations.",
                relevant_gates=(Gate.CONCEIVE, Gate.BUILD),
                evidence_needed=("risk_assessment", "security_policy"),
            ),
            RegimeRequirement(
                citation="45 CFR 164.308(b)(1) — Business associate contracts",
                description="Obtain satisfactory assurances (BAA) from business associates handling ePHI.",
                relevant_gates=(Gate.BUILD, Gate.DEPLOY),
                evidence_needed=("baa",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.312(a)(1) — Access control",
                description="Implement technical policies and procedures for accessing ePHI.",
                relevant_gates=(Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=("access_control_design",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.312(b) — Audit controls",
                description="Implement hardware, software, and procedural mechanisms that record and examine activity in information systems containing or using ePHI.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("audit_logs",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.312(c)(1) — Integrity",
                description="Implement policies and procedures to protect ePHI from improper alteration or destruction.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("integrity_controls",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.312(e)(1) — Transmission security",
                description="Implement technical security measures to guard against unauthorized access to ePHI being transmitted over a network.",
                relevant_gates=(Gate.BUILD, Gate.DEPLOY),
                evidence_needed=("encryption_in_transit",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.502(b) — Minimum necessary",
                description="When using or disclosing PHI, limit it to the minimum necessary to accomplish the intended purpose.",
                relevant_gates=(Gate.BUILD, Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=("data_minimization_design",),
            ),
            RegimeRequirement(
                citation="45 CFR 164.404 — Breach notification",
                description="Provide notification following a breach of unsecured PHI.",
                relevant_gates=(Gate.OPERATE,),
                evidence_needed=("incident_response_plan",),
            ),
        ]


_register(HIPAA())
