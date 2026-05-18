# Governance Provenance Record (GPR)

The **Governance Provenance Record (GPR)** is the concrete machine-readable artifact AI-GR produces at every Ribbon cell. Each GPR entry is a JSON-LD document with a fixed schema.

## The chain is the artifact

GPR entries chain together. Each entry's `linkage.prev_hash` field stores the SHA-256 hash of the prior entry's canonical bytes. Tampering with any historical entry breaks the hash linkage of every subsequent entry.

This is the central design idea of AI-GR: **the chain itself — not any individual entry — is the audit artifact**. A regulator, auditor, or downstream operator can verify the entire chain's integrity by checking only the cryptographic linkage and signatures, without needing to trust the operator's processes or storage.

## Mandatory fields

Every GPR entry carries nine fields, eight of which are mandatory and one of which (`agentic_context`) is conditional on the system type:

| Field | Description |
|---|---|
| `id` | URN identifying the entry: `urn:gpr:<org>/<system>/<gate>/<seq>` |
| `subject` | The system being governed (name, version, type) |
| `gate` | Which lifecycle gate emitted this entry |
| `risk_tier` | Critical, High, or Managed |
| `decision` | approve, approve_with_conditions, reject, rollback, defer |
| `evidence` | Datasets, evaluations, red-team reports, model-weight hashes, SBOM, free-form additional |
| `authority` | Approver DID, delegated scope, co-approvers, **legal_identity** (required for Critical) |
| `regime` | Array of regulatory regime claims |
| `linkage` | Pointer to the prior GPR entry's content hash |
| `attestation` | Ed25519 signature + RFC 3161 trusted timestamp |
| `agentic_context` | (Required iff `subject.type == "agentic"`) action authority, tool registry, runtime context, human oversight |

## A worked example

```json
{
  "@context": "https://ai-gr.dev/v1",
  "@type": "GPREntry",
  "schema_version": "0.2.0",
  "id": "urn:gpr:acme-health/cds-agent/build/0042",
  "subject": {
    "system": "ClinicalDecisionSupportAgent",
    "version": "2.3.1",
    "type": "agentic"
  },
  "gate": "Build",
  "risk_tier": "Critical",
  "decision": "approve_with_conditions",
  "evidence": {
    "datasets": ["mimic-iv-v3.0:sha256:a3f2..."],
    "evaluations": ["bias-eval-2026-05-12.pdf"],
    "red_team": ["atlas-v1.2-passed"],
    "model_weights": "9bc4e1...",
    "sbom": "spdx-2.3:cds-agent-bom.json"
  },
  "authority": {
    "approver": "did:web:acme-health:caio",
    "delegated_scope": "tier:critical;phi:read",
    "legal_identity": {
      "name": "ACME Health Systems Inc.",
      "registration_id": "LEI:5493001K3F3DUM2KRD89",
      "jurisdiction": "DE",
      "address": "Musterstrasse 1, 10115 Berlin",
      "contact_email": "compliance@acme-health.example",
      "gdpr_role": "controller"
    }
  },
  "regime": [
    {"regime": "EU-AI-Act:high-risk"},
    {"regime": "HIPAA:164.312"},
    {"regime": "FDA-SaMD:Class-IIb"},
    {"regime": "NIST-AI-RMF:Manage-2.3"}
  ],
  "linkage": {
    "prev_gpr": "urn:gpr:acme-health/cds-agent/conceive/0001",
    "prev_hash": "...",
    "chain_root": "urn:gpr:acme-health/cds-agent/conceive/0001"
  },
  "attestation": {
    "signature": "ed25519:gN2X...",
    "signature_alg": "ed25519",
    "public_key": "...",
    "timestamp": "2026-05-17T14:22:08Z",
    "tsa": "rfc3161:digicert"
  },
  "agentic_context": {
    "action_authority": ["read:phi", "write:ehr:annotation"],
    "tool_registry": ["epic-fhir-r4", "lab-result-lookup"],
    "runtime_context": {"temperature": 0.2, "max_steps": 5},
    "human_oversight": "in-the-loop"
  }
}
```

## Canonicalization

GPR content hashing uses [RFC 8785 (JSON Canonicalization Scheme, JCS)](https://www.rfc-editor.org/rfc/rfc8785). The hash input is the JCS-serialised entry with the `attestation` field excluded (so the signature isn't hashing itself); the SHA-256 digest is what subsequent entries reference via `linkage.prev_hash`.

JCS guarantees that compliant implementations in any language produce byte-identical canonical output for the same JSON value. This is what makes chain interoperability possible across heterogeneous implementations.

Note: RFC 8785 does **not** mandate NFC normalization (that's I-JSON / RFC 7493). Callers needing cross-encoding-form consistency should NFC-normalize before serialization.

## Threat model

The GPR chain defends against **post-hoc tampering**: any attempt to alter a historical entry breaks both the entry's own signature verification and the linkage hash held by every subsequent entry.

What AI-GR explicitly does **not** defend against:

- **Collusion at signing time.** If the approving authority signs a knowingly false entry, the cryptographic posture is satisfied but the substantive claim is wrong. Detecting collusion requires controls outside the cryptographic layer (segregation of duties, independent audit sampling, whistle-blower channels).
- **Compromised signing infrastructure.** A stolen private key produces valid-looking entries until detection and revocation.

Deployments should pair the GPR chain with conventional key management practices (HSMs where possible, short-lived signing certificates, revocation registries) appropriate to the risk tier.

## Legal identity vs. cryptographic identity

A DID-based identifier (`did:web:acme-health:caio`) satisfies cryptographic authentication but **does not, on its own, identify the legal person bound by regulatory obligations**. The EU AI Act requires conformity assessments and the Article 47 Declaration of Conformity to be signed by identifiable legal persons. The same applies under HIPAA.

AI-GR v0.2.0+ addresses this with the `LegalIdentity` sub-model under `Authority`. The DID layer provides cryptographic binding; the `legal_identity` layer provides regulatory binding. Both are required for regulated deployments; one is not a substitute for the other.

The `legal_identity` field is **mandatory for Critical-tier entries**, enforced at schema-validation time. Critical-tier entries lacking `legal_identity` will fail construction.

## Right to erasure: the Article 17 tension

Append-only cryptographic chains and the GDPR right to erasure are in structural tension. AI-GR follows the European Data Protection Board's [Guidelines 02/2025](https://www.edpb.europa.eu/) patterns:

- **Pattern 1: Off-chain personal data.** Personal data is never embedded directly in GPR entries. The `evidence` field carries *references* to external artifacts and the *hashes* of those artifacts; the artifacts themselves live in conventional, modifiable storage. When an Article 17 request is honoured, the underlying dataset is modified in its native storage; the GPR entry's hash continues to reference the prior dataset state, but no personal data within the GPR chain requires modification.

- **Pattern 2: Crypto-shredding of references.** Where a GPR entry references a dataset by hash and the dataset is subsequently erased, the entry remains cryptographically valid as a record-of-fact ("at the time of decision, dataset X with hash H existed and was relied upon"), even though the dataset itself is no longer recoverable. This is compatible with Article 17 where the legitimate-interest balancing under Article 17(3)(e) supports retention for establishing, exercising, or defending legal claims.
