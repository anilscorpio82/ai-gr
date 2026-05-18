"""
Cross-regime evidence worked example.

This example demonstrates the central claim of AI-GR: a single Build-gate
GPR entry can simultaneously satisfy the evidence demands of multiple
regulatory regimes — including the new regimes added in v0.2.0.

The scenario: a healthcare AI deployed in Germany. It is simultaneously
subject to:

  - EU AI Act (high-risk Annex III healthcare AI system; provider obligations)
  - EU AI Act Article 26 (the deploying hospital is a deployer)
  - GDPR (processes special-category health data)
  - MDR (software with a medical purpose, EU 2017/745)
  - NIS2 (the hospital is an essential entity in the healthcare sector)
  - HIPAA (the hospital network also operates in the US under HIPAA)
  - NIST AI RMF (voluntarily adopted by the deploying organisation)

A single Build-gate evidence block — datasets, evaluations, red-team
results, model weight hash, SBOM, DPIA reference — is annotated with seven
RegimeClaim entries, demonstrating that the same evidence is interpretable
through seven different regulatory lenses.

Run this example with::

    python -m examples.cross_regime_evidence
"""

from __future__ import annotations

from ai_gr import (
    AgenticContext,
    Decision,
    Evidence,
    Gate,
    GdprRole,
    GPREntry,
    LegalIdentity,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.builder import ChainBuilder
from ai_gr.crypto import KeyPair


def build_chain() -> list[GPREntry]:
    """Build a cross-regime evidence chain demonstrating seven simultaneous claims."""
    keypair = KeyPair.generate()

    subject = Subject(
        system="ClinicalImagingAgent",
        version="3.1.0",
        type=SystemType.AGENTIC,
        description=(
            "Multi-modal clinical imaging agent supporting radiologists with "
            "preliminary classification and triage. Deployed at a German hospital "
            "network with US affiliates."
        ),
    )

    # The hospital network is a German GmbH with US operations. As the deployer
    # of a third-party AI system it is also subject to Article 26 deployer
    # obligations. The legal_identity here is the deployer's legal entity.
    legal_identity = LegalIdentity(
        name="Universitätsklinikum München GmbH",
        registration_id="LEI:5493001MUNICH00000001",
        jurisdiction="DE",
        address="Marchioninistrasse 15, 81377 München, Germany",
        contact_email="datenschutz@klinikum-muc.example",
        gdpr_role=GdprRole.CONTROLLER,
    )

    builder = ChainBuilder(
        org="klinikum-muc",
        system="imaging-agent",
        subject=subject,
        keypair=keypair,
        approver_did="did:web:klinikum-muc:caio",
        legal_identity=legal_identity,
    )

    # ----- Gate 1: Conceive -----
    # The Conceive gate references the DPIA (GDPR Art. 35) and FRIA (EU AI Act
    # Art. 27 — applies because the hospital provides public health services).
    # The lawful basis is Article 6(1)(c) (legal obligation under MDR
    # post-market surveillance) supplemented by Article 9(2)(h) for
    # special-category health data processing.
    builder.append(
        gate=Gate.CONCEIVE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE_WITH_CONDITIONS,
        delegated_scope="tier:critical;phi:read;health-data:process",
        co_approvers=[
            "did:web:klinikum-muc:cmio",       # Chief Medical Information Officer
            "did:web:klinikum-muc:dpo",         # Data Protection Officer (GDPR Art. 37)
            "did:web:klinikum-muc:ciso",        # CISO (NIS2 Art. 21)
        ],
        evidence=Evidence(
            additional={
                "dpia": "dpia-klinikum-muc-imaging-agent-v3.1.0.pdf",
                "fria": "fria-klinikum-muc-imaging-agent-v3.1.0.pdf",
                "lawful_basis": "Art-6(1)(c)+Art-9(2)(h)",
                "intended_use": "Preliminary classification and triage of chest CT studies",
                "mdr_classification": "Class IIb (MDR Rule 11)",
                "business_function_classification": "Patient-care critical (DORA-equivalent for non-financial)",
            }
        ),
        regimes=[
            RegimeClaim(
                regime="EU-AI-Act:high-risk",
                citation="Annex III §5 — access to essential healthcare services",
            ),
            RegimeClaim(
                regime="EU-AI-Act-Deployer:Article 27 — Fundamental Rights Impact Assessment",
                citation="Public-service entity — FRIA required",
            ),
            RegimeClaim(
                regime="GDPR:Article 35 — Data Protection Impact Assessment",
                citation="High-risk processing of special-category health data",
            ),
            RegimeClaim(
                regime="MDR-IVDR:MDR Rule 11 — Classification of software",
                citation="Software intended for diagnosis/therapeutic decisions",
            ),
            RegimeClaim(
                regime="NIS2:Article 21(2)(a) — Risk analysis and information system security policies",
                citation="Healthcare essential entity",
            ),
            RegimeClaim(
                regime="NIST-AI-RMF:MAP-3.1",
                citation="System categorization and impact analysis",
            ),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:imaging-study"],
            tool_registry=["dicom-pacs"],
            runtime_context={"design_phase": True},
            human_oversight="in-the-loop",
        ),
    )

    # ----- Gate 2: Build -----
    # This is the central demonstration. A single Build-gate Evidence block
    # carries six pieces of evidence (datasets, evaluations, red-team, model
    # weights, SBOM, MDR clinical evaluation). Each piece is interpretable
    # through multiple regulatory lenses, expressed as seven simultaneous
    # RegimeClaim entries.
    builder.append(
        gate=Gate.BUILD,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE_WITH_CONDITIONS,
        delegated_scope="tier:critical;health-data:process",
        co_approvers=["did:web:klinikum-muc:cmio"],
        evidence=Evidence(
            datasets=[
                "mimic-cxr-jpg-v2.1.0:sha256:" + "a" * 64,
                "klinikum-muc-internal-cxr-2026q1:sha256:" + "b" * 64,
            ],
            evaluations=[
                "bias-audit-2026-05-10.pdf",
                "clinical-evaluation-report-mdr.pdf",
                "performance-validation-prospective.pdf",
            ],
            red_team=[
                "atlas-v1.4-mitre-passed",
                "owasp-agentic-top10-passed",
            ],
            model_weights="c" * 64,
            sbom="spdx-2.3:imaging-agent-bom-v3.1.0.json",
            additional={
                "clinical_evaluation_report": "cer-imaging-agent-v3.1.0.pdf",
                "technical_documentation": "annex-iv-imaging-agent-v3.1.0.pdf",
                "supply_chain_attestation": "sigstore-cosign-bundle-v3.1.0",
            },
        ),
        regimes=[
            # 1. EU AI Act Annex IV technical documentation (provider side)
            RegimeClaim(
                regime="EU-AI-Act:Annex IV §2 — Elements and development process",
                citation="Methods, design, datasets, training process",
            ),
            # 2. EU AI Act Annex IV §3 monitoring, validation, testing
            RegimeClaim(
                regime="EU-AI-Act:Annex IV §3 — Monitoring, validation, testing",
                citation="Performance metrics and red-team results",
            ),
            # 3. GDPR Article 35 — DPIA processing of special-category data
            RegimeClaim(
                regime="GDPR:Article 35 — Data Protection Impact Assessment",
                citation="Build-time DPIA validation",
            ),
            # 4. MDR clinical evaluation (EU 2017/745 Article 61)
            RegimeClaim(
                regime="MDR-IVDR:MDR Article 61 — Clinical evaluation",
                citation="Clinical evaluation report references in evidence.additional",
            ),
            # 5. MDR Annex II — Technical documentation
            RegimeClaim(
                regime="MDR-IVDR:MDR Annex II — Technical documentation",
                citation="Device description, design, manufacturing, clinical evaluation",
            ),
            # 6. NIS2 supply-chain security (SBOM)
            RegimeClaim(
                regime="NIS2:Article 21(2)(d) — Supply chain security",
                citation="SBOM in SPDX format with verifiable provenance",
            ),
            # 7. HIPAA Security Rule technical safeguards (US affiliates)
            RegimeClaim(
                regime="HIPAA:164.312(c) — Integrity",
                citation="Model weight hash + attestation signature + chain linkage",
            ),
            # 8. NIST AI RMF Manage subcategory
            RegimeClaim(
                regime="NIST-AI-RMF:Manage-2.3",
                citation="Procedures for trustworthiness deviation",
            ),
        ],
        agentic_context=AgenticContext(
            action_authority=[
                "read:imaging-study",
                "write:triage-annotation",
            ],
            tool_registry=[
                "dicom-pacs",
                "snomed-ct-lookup",
                "hl7-fhir-r4",
            ],
            runtime_context={
                "temperature": 0.1,
                "max_steps": 3,
                "isolation_level": "tenant-scoped",
                "model_provider": "self-hosted",
            },
            human_oversight="in-the-loop",
        ),
    )

    # ----- Gate 3: Deploy -----
    builder.append(
        gate=Gate.DEPLOY,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;deployment:approved",
        co_approvers=["did:web:klinikum-muc:ciso"],
        evidence=Evidence(
            additional={
                "instructions_for_use": "ifu-imaging-agent-v3.1.0.pdf:sha256:" + "d" * 64,
                "worker_notification_record": "wbr-imaging-agent-2026-05-15.pdf",
                "doc_signed": "art-47-doc-imaging-agent-v3.1.0.pdf",
            },
        ),
        regimes=[
            RegimeClaim(
                regime="EU-AI-Act:Annex IV §8 — EU Declaration of Conformity",
                citation="Article 47 DoC issued",
            ),
            RegimeClaim(
                regime="EU-AI-Act-Deployer:Article 26(7) — Worker notification",
                citation="Worker representatives notified per Art. 26(7)",
            ),
            RegimeClaim(
                regime="MDR-IVDR:MDR Annex I — General safety and performance requirements",
                citation="CE marking affixed",
            ),
            RegimeClaim(
                regime="GDPR:Article 28 — Processor relationships",
                citation="Sub-processor agreements in place for cloud regions",
            ),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:imaging-study", "write:triage-annotation"],
            tool_registry=["dicom-pacs", "snomed-ct-lookup", "hl7-fhir-r4"],
            human_oversight="in-the-loop",
        ),
    )

    # ----- Gate 4: Operate -----
    builder.append(
        gate=Gate.OPERATE,
        tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        delegated_scope="tier:critical;ops:monitor",
        evidence=Evidence(
            additional={
                "weekly_drift_report": "drift-2026-w20.json",
                "weekly_incident_count": 0,
                "log_retention_attestation": "retention-policy-7y-acknowledged",
            },
        ),
        regimes=[
            RegimeClaim(
                regime="EU-AI-Act:Article 72 — Post-market monitoring",
                citation="Weekly PMS report",
            ),
            RegimeClaim(
                regime="EU-AI-Act-Deployer:Article 26(5) — Monitoring and incident response",
                citation="Continuous monitoring per provider IFU",
            ),
            RegimeClaim(
                regime="EU-AI-Act-Deployer:Article 26(6) — Log retention",
                citation="≥6 months log retention; AI-GR chain satisfies",
            ),
            RegimeClaim(
                regime="MDR-IVDR:MDR Article 83 — Post-market surveillance",
                citation="PMS system in operation",
            ),
            RegimeClaim(
                regime="NIS2:Article 23 — Reporting obligations",
                citation="No reportable incidents this period",
            ),
            RegimeClaim(
                regime="HIPAA:164.312(b) — Audit controls",
                citation="Chain provides tamper-evident audit log",
            ),
            RegimeClaim(
                regime="NIST-AI-RMF:Manage-4.1",
                citation="Post-deployment monitoring and logging",
            ),
        ],
        agentic_context=AgenticContext(
            action_authority=["read:imaging-study", "write:triage-annotation"],
            tool_registry=["dicom-pacs", "snomed-ct-lookup", "hl7-fhir-r4"],
            runtime_context={"invocations_this_period": 4287, "drift_score": 0.014},
            human_oversight="in-the-loop",
        ),
    )

    return builder.chain


def run(store_root: str = "./cross-regime-store") -> list[GPREntry]:
    """Build the chain and persist it to a filesystem store."""
    from pathlib import Path

    from ai_gr.store import FilesystemStore

    chain = build_chain()
    store = FilesystemStore(Path(store_root))
    for entry in chain:
        store.append(entry)
    return chain
