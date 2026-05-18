"""
examples.code_review_agent — Internal AI-augmented code review agent.

Demonstrates AI-GR's Build-gate pattern for AI-augmented code: a nine-phase
code attestation pipeline that produces signed evidence at the Build gate
of the Ribbon, and runtime attestation events at the Operate gate.

This is the slide-8 narrative from the deck made concrete: a worked
instantiation of AI-GR for AI-augmented engineering workflows, showing
how Build-gate evidence is produced from a CI pipeline and how
runtime attestation evidence flows through the Operate gate.

The nine pipeline phases shown here (ingest, static-analysis, secret-scan,
dependency-audit, model-attest, atlas-redteam, policy-check, human-review,
sign-off) are illustrative — organizations will adapt them to their own
engineering practices. AI-GR is agnostic to the specific phases; what it
cares about is that the resulting evidence is signed and chained into the
GPR for the system.
"""

from __future__ import annotations

from ai_gr import (
    AgenticContext,
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
        system="CodeReviewAgent",
        version="0.9.2",
        type=SystemType.AGENTIC,
        description="AI-augmented code review agent integrated into the engineering CI pipeline; evidence produced via the AI-GR Build-gate code attestation pattern.",
    )
    # Optional for High tier but recommended.
    legal_identity = LegalIdentity(
        name="ACME Engineering Pty Ltd.",
        registration_id="LEI:5493001ACMEENG000001",
        jurisdiction="AU",
        address="100 Engineering Way, Sydney NSW 2000, Australia",
        contact_email="compliance@acme-engineering.example",
        gdpr_role=GdprRole.NOT_APPLICABLE,
    )
    builder = ChainBuilder(
        org="acme-engineering",
        system="code-review-agent",
        subject=subject,
        keypair=keypair,
        approver_did="did:web:acme-engineering:cto",
        legal_identity=legal_identity,
    )

    builder.append(
        gate=Gate.CONCEIVE,
        tier=RiskTier.HIGH,
        decision=Decision.APPROVE,
        delegated_scope="tier:high;ai-augmented-engineering",
        regimes=[
            RegimeClaim(regime="NIST-AI-RMF:MAP-1.1", citation="Use case context — engineering productivity"),
            RegimeClaim(regime="ISO-42001:5.1", citation="Leadership commitment"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:repo", "comment:pr", "suggest:edit", "block:merge-on-critical-finding"],
            tool_registry=["github-api", "code-attestation-pipeline", "sbom-generator"],
            human_oversight="on-the-loop",
            runtime_context={"max_pr_size_loc": 5000, "blocked_paths": ["secrets/", "infra/"]},
        ),
    )

    # Build-gate evidence flows from the code attestation pipeline.
    builder.append(
        gate=Gate.BUILD,
        tier=RiskTier.HIGH,
        decision=Decision.APPROVE,
        delegated_scope="tier:high;model:approve",
        evidence=Evidence(
            datasets=["internal-code-review-corpus:sha256:e9c3a5d7f1b3e5c7d9b1f3a5c7e0d2b4f6a8c1e3f5d7b99bc4e1a8f3d2c7b5e9"],
            evaluations=["code-attestation-pipeline-report-v0.9.2.json", "false-positive-rate-eval.pdf"],
            red_team=["atlas-redteam-passed", "prompt-injection-suite-passed"],
            model_weights="b5e9f1a3c5d7b9e2f4c6d8a0e3f5b7d9c1a4e6f8b0d2c5e7f99bc4e1a8f3d2c7",
            sbom="spdx-2.3:code-review-agent-bom-v0.9.2.json",
            additional={
                "code_attestation_pipeline_run": "pipeline-run-2026-05-15-001",
                "attestation_phases_passed": [
                    "ingest", "static-analysis", "secret-scan", "dependency-audit",
                    "model-attest", "atlas-redteam", "policy-check", "human-review", "sign-off",
                ],
            },
        ),
        regimes=[
            RegimeClaim(regime="NIST-AI-RMF:MEASURE-2.3", citation="Performance evaluation"),
            RegimeClaim(regime="SEC-Cyber:AI-Security-Rider", citation="Adversarial red-teaming"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:repo", "comment:pr", "suggest:edit", "block:merge-on-critical-finding"],
            tool_registry=["github-api", "code-attestation-pipeline", "sbom-generator"],
            human_oversight="on-the-loop",
        ),
    )

    builder.append(
        gate=Gate.DEPLOY,
        tier=RiskTier.HIGH,
        decision=Decision.APPROVE,
        delegated_scope="tier:high;deploy:engineering-org",
        evidence=Evidence(
            additional={
                "deployment_scope": "engineering-org-only",
                "rollback_runbook": "runbooks/code-review-agent-rollback.md",
            },
        ),
        regimes=[
            RegimeClaim(regime="ISO-42001:7.5", citation="Documented information"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:repo", "comment:pr", "suggest:edit", "block:merge-on-critical-finding"],
            tool_registry=["github-api", "code-attestation-pipeline", "sbom-generator"],
            human_oversight="on-the-loop",
        ),
    )

    # Runtime attestation events flow into the Operate gate.
    builder.append(
        gate=Gate.OPERATE,
        tier=RiskTier.HIGH,
        decision=Decision.APPROVE,
        delegated_scope="tier:high;operate:monitor",
        evidence=Evidence(
            evaluations=["weekly-pr-acceptance-rate-report.json"],
            additional={
                "runtime_attestations_count": 4_213,
                "rollback_events_2026Q2": 2,
                "incident_log": "servicenow:code-review-agent-q2",
            },
        ),
        regimes=[
            RegimeClaim(regime="NIST-AI-RMF:MANAGE-2.3", citation="Incident response procedures invoked"),
            RegimeClaim(regime="ISO-42001:A.8.2", citation="Operational monitoring"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:repo", "comment:pr", "suggest:edit", "block:merge-on-critical-finding"],
            tool_registry=["github-api", "code-attestation-pipeline", "sbom-generator"],
            human_oversight="on-the-loop",
        ),
    )

    return builder.chain


if __name__ == "__main__":
    chain = build_chain()
    print(f"Built {len(chain)} entries for the code review agent (AI-GR Build-gate pattern).")
    for e in chain:
        print(f"  {e.gate.value:<10}  {e.id}")
