"""
ai_gr.regimes.state_aedt — US state Automated Employment / Decision-Making Tool laws.

The fastest-moving regulatory area in 2026: state laws governing AI-driven
"consequential decisions" about employment, housing, credit, healthcare, and
education. Key statutes:

  - California CCPA ADMT regulations (effective Jan 1, 2026; compliance
    deadline Jan 1, 2027)
  - NYC AEDT Law (Local Law 144 of 2021, in effect)
  - Colorado SB 26-189 (proposed May 2026, would replace original CO AI Act)
  - Connecticut SB 5 (omnibus AI bill, advancing 2026)
  - Texas TRAIGA (effective Jan 1, 2026; narrowed to government use)

These are aggregated into one regime because the core obligations recur:
notice, opt-out, bias audit, pre-use impact assessment.
"""

from __future__ import annotations

from ai_gr.regimes.base import Regime, RegimeRequirement, _register
from ai_gr.schema import Gate


class StateAEDT(Regime):
    identifier = "State-AEDT"
    name = "US State Automated Decision-Making / Employment Tool Laws"
    description = (
        "Aggregated requirements from US state laws regulating AI-driven "
        "consequential decisions: California CCPA ADMT, NYC AEDT, Colorado, "
        "Connecticut, Texas. Common themes: notice, opt-out, bias audit, "
        "impact assessment."
    )

    def requirements(self) -> list[RegimeRequirement]:
        return [
            RegimeRequirement(
                citation="CA CCPA ADMT §7220 — Pre-use notice",
                description="Provide consumers with a pre-use notice when ADMT is used for significant decisions.",
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=("pre_use_notice",),
            ),
            RegimeRequirement(
                citation="CA CCPA ADMT §7221 — Right to opt-out",
                description="Enable consumers to opt out of the use of ADMT for significant decisions.",
                relevant_gates=(Gate.DEPLOY, Gate.OPERATE),
                evidence_needed=("opt_out_mechanism",),
            ),
            RegimeRequirement(
                citation="NYC AEDT — Independent bias audit",
                description="Annual independent bias audit performed and made public.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("bias_audit",),
            ),
            RegimeRequirement(
                citation="NYC AEDT — Candidate notice",
                description="Notify candidates of AEDT use at least 10 business days before assessment.",
                relevant_gates=(Gate.DEPLOY,),
                evidence_needed=("candidate_notice",),
            ),
            RegimeRequirement(
                citation="CO SB 26-189 — Impact assessment",
                description="Conduct documented impact assessment before deploying high-risk AI for consequential decisions.",
                relevant_gates=(Gate.CONCEIVE,),
                evidence_needed=("impact_assessment",),
            ),
            RegimeRequirement(
                citation="CT SB 5 — Anti-discrimination",
                description="Use reasonable care to avoid algorithmic discrimination.",
                relevant_gates=(Gate.BUILD, Gate.OPERATE),
                evidence_needed=("bias_audit", "fairness_metrics"),
            ),
        ]


_register(StateAEDT())
