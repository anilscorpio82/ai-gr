"""
examples.financial_advice_agent — SEC + state ADMT example.

A consumer-facing generative agent that drafts retirement allocation
suggestions. Triggers:

  - SEC AI governance disclosures (Item 106)
  - California CCPA ADMT pre-use notice + opt-out (Jan 2027 deadline)
  - NIST AI RMF generative AI profile

System type is *generative* (not agentic) — the agent suggests, the human
decides. This is included to demonstrate that AI-GR works equally well for
non-agentic systems; the agentic_context is simply omitted.
"""

from __future__ import annotations

from ai_gr import (
    Decision,
    Evidence,
    Gate,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.builder import ChainBuilder
from ai_gr.crypto import KeyPair
from ai_gr.schema import GdprRole, LegalIdentity


def build_chain() -> list:
    keypair = KeyPair.generate()
    subject = Subject(
        system="RetirementAllocationAssistant",
        version="1.4.0",
        type=SystemType.GENERATIVE,
        description="Generative AI assistant proposing retirement portfolio allocations for human advisor review.",
    )
    legal_identity = LegalIdentity(
        name="ACME Wealth Management LLC",
        registration_id="LEI:5493001ACMEWEALTH001",
        jurisdiction="US",
        address="200 Madison Avenue, New York, NY 10016, USA",
        contact_email="compliance@acme-wealth.example",
        gdpr_role=GdprRole.NOT_APPLICABLE,
    )
    builder = ChainBuilder(
        org="acme-wealth",
        system="ret-alloc-agent",
        subject=subject,
        keypair=keypair,
        approver_did="did:web:acme-wealth:cco",
        legal_identity=legal_identity,
    )

    # Conceive
    builder.append(
        gate=Gate.CONCEIVE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        co_approvers=["did:web:acme-wealth:ciso", "did:web:acme-wealth:caio"],
        delegated_scope="tier:critical;consumer-facing;financial-advice",
        regimes=[
            RegimeClaim(regime="SEC-Cyber:Item-106(b)", citation="Risk management process for AI"),
            RegimeClaim(regime="SEC-Cyber:Item-106(c)", citation="Board oversight of AI risk"),
            RegimeClaim(regime="State-AEDT:CO-SB26-189", citation="Impact assessment for consequential decisions"),
            RegimeClaim(regime="NIST-AI-RMF:GenAI-Profile-GV-1.3", citation="GenAI-specific risk governance"),
        ],
    )

    # Build
    builder.append(
        gate=Gate.BUILD,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE_WITH_CONDITIONS,
        delegated_scope="tier:critical;model:approve",
        co_approvers=["did:web:acme-wealth:ciso"],
        evidence=Evidence(
            datasets=["public-filings-corpus-2026Q1:sha256:c1e3f5d7b9a2e4f6d8c0a3b5e7f9d1c4b6e8f0a2c5d7e9b1f3a5c7e0d2b4f6a8"],
            evaluations=["hallucination-rate-eval.pdf", "fairness-by-demographics.xlsx"],
            red_team=["financial-advice-jailbreak-suite-passed"],
            model_weights="a4e6f8b0d2c5e7f99bc4e1a8f3d2c7b5e9f1a3c5d7b9e2f4c6d8a0e3f5b7d9c1",
            sbom="spdx-2.3:ret-alloc-agent-bom-v1.4.json",
        ),
        regimes=[
            RegimeClaim(regime="SEC-Cyber:AI-Security-Rider", citation="Adversarial red-teaming"),
            RegimeClaim(regime="NIST-AI-RMF:MEASURE-2.6", citation="Trustworthy characteristics"),
            RegimeClaim(regime="State-AEDT:NYC-AEDT", citation="Independent bias audit"),
        ],
    )

    # Deploy
    builder.append(
        gate=Gate.DEPLOY,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;deploy:production",
        evidence=Evidence(
            additional={
                "pre_use_notice": "ccpa-admt-pre-use-notice-v2.html",
                "opt_out_mechanism": "preferences/admt-opt-out",
                "candidate_disclosure": "ai-assist-disclosure-banner-deployed",
            },
        ),
        regimes=[
            RegimeClaim(regime="State-AEDT:CA-CCPA-ADMT-§7220", citation="Pre-use notice deployed"),
            RegimeClaim(regime="State-AEDT:CA-CCPA-ADMT-§7221", citation="Opt-out enabled"),
            RegimeClaim(regime="EU-AI-Act:Article-13", citation="Transparency to deployers"),
        ],
    )

    # Operate
    builder.append(
        gate=Gate.OPERATE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;operate:monitor",
        evidence=Evidence(
            evaluations=["monthly-fairness-report-2026-04.pdf"],
            additional={
                "incident_log": "servicenow:ret-alloc-agent-incidents",
                "monitoring_telemetry": "datadog:ret-alloc-agent",
            },
        ),
        regimes=[
            RegimeClaim(regime="SEC-Cyber:Form-8K-1.05", citation="Material incident disclosure readiness"),
            RegimeClaim(regime="NIST-AI-RMF:MANAGE-4.1", citation="Post-deployment monitoring"),
            RegimeClaim(regime="State-AEDT:CT-SB5", citation="Algorithmic discrimination monitoring"),
        ],
    )

    return builder.chain


if __name__ == "__main__":
    chain = build_chain()
    print(f"Built {len(chain)} entries for the financial advice example.")
    for e in chain:
        print(f"  {e.gate.value:<10}  {e.id}")
