"""
examples.clinical_decision_support — End-to-end HIPAA + EU AI Act + FDA SaMD example.

This is the headline demo: a Critical-tier agentic clinical decision support
system, governed through all five Ribbon gates, with the GPR chain exported
as a multi-regime regulator dossier.

Run it with:

    python -m examples.clinical_decision_support

Or via the CLI:

    ai-gr demo

The demo constructs a synthetic but realistic chain. No real PHI is involved.
"""

from __future__ import annotations

from pathlib import Path

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
from ai_gr.export import multi_regime_dossier
from ai_gr.schema import GdprRole, LegalIdentity
from ai_gr.store import FilesystemStore


def build_chain() -> list:
    """Build the canonical CDS demo chain in memory and return it."""
    keypair = KeyPair.generate()
    subject = Subject(
        system="ClinicalDecisionSupportAgent",
        version="2.3.1",
        type=SystemType.AGENTIC,
        description="LLM-based clinical decision support assisting on sepsis triage decisions.",
    )
    # The legal_identity binds the cryptographic authority (DID) to the
    # named legal person required by EU AI Act Art. 47 (Declaration of
    # Conformity) and HIPAA (Business Associate Agreement framework).
    # Required for Critical-tier entries in schema v0.2.0+.
    legal_identity = LegalIdentity(
        name="ACME Health Systems Inc.",
        registration_id="LEI:5493001K3F3DUM2KRD89",
        jurisdiction="DE",
        address="Musterstrasse 1, 10115 Berlin, Germany",
        contact_email="compliance@acme-health.example",
        gdpr_role=GdprRole.CONTROLLER,
    )
    builder = ChainBuilder(
        org="acme-health",
        system="cds-agent",
        subject=subject,
        keypair=keypair,
        approver_did="did:web:acme-health:caio",
        legal_identity=legal_identity,
    )

    # ---- Gate 1: Conceive ----
    builder.append(
        gate=Gate.CONCEIVE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;phi:read;ai-governance:approve",
        co_approvers=["did:web:acme-health:ciso", "did:web:acme-health:privacy-officer"],
        regimes=[
            RegimeClaim(
                regime="EU-AI-Act:high-risk",
                citation="Annex III §5(a) — access to essential healthcare services",
            ),
            RegimeClaim(
                regime="HIPAA:164.308",
                citation="Security management process and risk analysis",
            ),
            RegimeClaim(
                regime="NIST-AI-RMF:MAP-3.1",
                citation="System categorization and impact analysis",
            ),
            RegimeClaim(
                regime="ISO-42001:6.1.2",
                citation="AI risk assessment for the proposed use case",
            ),
            RegimeClaim(
                regime="FDA-SaMD:Class-IIb",
                citation="Software intended to drive clinical management of a serious condition",
            ),
        ],
        agentic_context=AgenticContext(
            action_authority=[
                "read:phi:hospital-emr",
                "compute:risk-score",
                "annotate:patient-record",
            ],
            tool_registry=["epic-fhir-r4", "lab-result-lookup", "vital-signs-stream"],
            human_oversight="in-the-loop",
            runtime_context={
                "max_steps_per_session": 10,
                "isolation_level": "patient-scoped",
                "audit_log_destination": "siem:hospital-prod",
            },
        ),
    )

    # ---- Gate 2: Build ----
    builder.append(
        gate=Gate.BUILD,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE_WITH_CONDITIONS,
        delegated_scope="tier:critical;model:approve-for-deploy",
        co_approvers=["did:web:acme-health:ciso"],
        evidence=Evidence(
            datasets=[
                "mimic-iv-v3.0:sha256:a3f2c8e1b9d04f7e2c5a8b1f6e9d3c7b4a8f2e6c1d9b5f3a7e0c4b8d2a6f1e9c3",
                "hospital-internal-sepsis-cohort-2025:sha256:f1e3d5c7b9a2e4f6d8c0a3b5e7f9d1c4b6e8f0a2c5d7e9b1f3a5c7e0d2b4f6a8",
            ],
            evaluations=[
                "sepsis-triage-eval-2026-05-12.pdf",
                "subgroup-performance-by-demographic.xlsx",
            ],
            red_team=["mitre-atlas-v1.2-passed", "internal-adversarial-suite-2026Q2"],
            model_weights="9bc4e1a8f3d2c7b5e9f1a3c5d7b9e2f4c6d8a0e3f5b7d9c1a4e6f8b0d2c5e7f9",
            sbom="spdx-2.3:cds-agent-bom-v2.3.1.json",
            additional={
                "bias_audit": "third-party-bias-audit-2026-05-01.pdf",
                "accuracy_metrics": {"sensitivity": 0.91, "specificity": 0.88, "auroc": 0.94},
            },
        ),
        regimes=[
            RegimeClaim(regime="EU-AI-Act:Article-10", citation="Data governance and quality"),
            RegimeClaim(regime="EU-AI-Act:Article-15", citation="Accuracy, robustness, cybersecurity"),
            RegimeClaim(regime="NIST-AI-RMF:MEASURE-2.6", citation="Trustworthy characteristics evaluation"),
            RegimeClaim(regime="HIPAA:164.312(e)", citation="Transmission security"),
            RegimeClaim(regime="FDA-SaMD:IEC-62304", citation="Software verification"),
            RegimeClaim(regime="SEC-Cyber:AI-Security-Rider", citation="Adversarial red-teaming evidence"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:phi:hospital-emr", "compute:risk-score", "annotate:patient-record"],
            tool_registry=["epic-fhir-r4", "lab-result-lookup", "vital-signs-stream"],
            human_oversight="in-the-loop",
        ),
    )

    # ---- Gate 3: Deploy ----
    builder.append(
        gate=Gate.DEPLOY,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;deploy:production",
        co_approvers=["did:web:acme-health:ciso", "did:web:acme-health:cmio"],
        evidence=Evidence(
            evaluations=["deployment-readiness-review-2026-05-15.pdf"],
            additional={
                "baa_reference": "baa-anthropic-2025-renewed",
                "rollback_plan": "runbook-cds-agent-rollback-v3.md",
                "access_control_review": "rbac-review-2026-05-14.pdf",
            },
        ),
        regimes=[
            RegimeClaim(regime="EU-AI-Act:Article-11", citation="Technical documentation"),
            RegimeClaim(regime="EU-AI-Act:Article-13", citation="Transparency to deployers"),
            RegimeClaim(regime="EU-AI-Act:Article-14", citation="Human oversight design"),
            RegimeClaim(regime="HIPAA:164.308(b)", citation="BAA in place with model provider"),
            RegimeClaim(regime="HIPAA:164.312(a)", citation="Access control implementation"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:phi:hospital-emr", "compute:risk-score", "annotate:patient-record"],
            tool_registry=["epic-fhir-r4", "lab-result-lookup", "vital-signs-stream"],
            human_oversight="in-the-loop",
        ),
    )

    # ---- Gate 4: Operate ----
    builder.append(
        gate=Gate.OPERATE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;operate:continuous-monitoring",
        evidence=Evidence(
            evaluations=["weekly-drift-report-2026-W19.json"],
            additional={
                "monitoring_telemetry": "splunk:cds-agent-prod-metrics",
                "incident_log": "servicenow:cds-agent-incidents-q2-2026",
                "operational_logs": "s3://acme-health-audit/cds-agent/2026/05/",
            },
        ),
        regimes=[
            RegimeClaim(regime="EU-AI-Act:Article-12", citation="Automatic event logging"),
            RegimeClaim(regime="EU-AI-Act:Article-72", citation="Post-market monitoring"),
            RegimeClaim(regime="NIST-AI-RMF:MANAGE-4.1", citation="Post-deployment monitoring"),
            RegimeClaim(regime="HIPAA:164.312(b)", citation="Audit controls"),
            RegimeClaim(regime="FDA-SaMD:Real-World-Performance", citation="Real-world performance monitoring"),
            RegimeClaim(regime="ISO-42001:9.1", citation="Monitoring, measurement, analysis"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:phi:hospital-emr", "compute:risk-score", "annotate:patient-record"],
            tool_registry=["epic-fhir-r4", "lab-result-lookup", "vital-signs-stream"],
            human_oversight="in-the-loop",
        ),
    )

    # ---- Gate 5: Evolve (minor model update) ----
    builder.append(
        gate=Gate.EVOLVE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE_WITH_CONDITIONS,
        delegated_scope="tier:critical;model:approve-evolution",
        co_approvers=["did:web:acme-health:ciso"],
        evidence=Evidence(
            datasets=["additional-2026Q1-cohort:sha256:b2e4f6d8c0a3b5e7f9d1c4b6e8f0a2c5d7e9b1f3a5c7e0d2b4f6a8c1e3f5d7b9"],
            evaluations=["re-evaluation-after-retrain-2026-05-16.pdf"],
            red_team=["mitre-atlas-v1.2-passed-revalidation"],
            model_weights="d8c0a3b5e7f9d1c4b6e8f0a2c5d7e9b1f3a5c7e0d2b4f6a8c1e3f5d7b99bc4e1",
            additional={
                "pccp_document": "pccp-cds-agent-v2.3-modifications.pdf",
                "modification_summary": "Improved performance on pediatric subgroup. No change to intended use.",
            },
        ),
        regimes=[
            RegimeClaim(regime="FDA-SaMD:PCCP-§IV", citation="Pre-specified modification protocol"),
            RegimeClaim(regime="EU-AI-Act:Article-9", citation="Risk management system update"),
            RegimeClaim(regime="ISO-42001:8.2", citation="Updated impact assessment"),
            RegimeClaim(regime="FDA-SaMD:Subgroup-Performance", citation="Demographic performance evidence"),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:phi:hospital-emr", "compute:risk-score", "annotate:patient-record"],
            tool_registry=["epic-fhir-r4", "lab-result-lookup", "vital-signs-stream"],
            human_oversight="in-the-loop",
        ),
    )

    return builder.chain


def run(store_root: str = "./demo-store") -> list:
    """Run the full demo: build the chain, persist it, export a dossier."""
    chain = build_chain()
    store = FilesystemStore(store_root)
    for entry in chain:
        store.append(entry)

    dossier_path = Path(store_root) / "multi-regime-dossier.json"
    dossier_path.write_text(
        multi_regime_dossier(chain, organization="Acme Health"),
        encoding="utf-8",
    )
    return chain


if __name__ == "__main__":
    chain = run()
    print(f"Built and persisted {len(chain)} entries.")
    for e in chain:
        print(f"  {e.gate.value:<10}  {e.id}")
