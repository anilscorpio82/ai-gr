# Reference Architecture — AI-GR v0.2.0

This document mirrors §6 of the v1.4 AI-GR paper. Two design commitments shape the architecture:

1. **Vendor neutrality** — the framework is specified at the capability level with concrete protocol and standard references where they exist, but does not prescribe specific vendor products.
2. **Layered separation** — the architecture is organised as five horizontal layers with clear interfaces between adjacent layers, so each layer can be implemented, replaced, or upgraded independently.

```
┌────────────────────────────────────────────────────────────────────┐
│  INTEGRATION LAYER                                                 │
│  SIEM · observability · IAM · GRC · regulatory submission          │
├────────────────────────────────────────────────────────────────────┤
│  CHAIN LAYER                                                       │
│  append-only log · Merkle / transparency-log · RFC 3161 anchoring  │
├────────────────────────────────────────────────────────────────────┤
│  GPR LAYER                                                         │
│  JSON-LD schema · JCS canonicalization · Ed25519 signing           │
├────────────────────────────────────────────────────────────────────┤
│  EVIDENCE LAYER                                                    │
│  content-addressable artifacts · SBOM · evaluations · DPIA         │
├────────────────────────────────────────────────────────────────────┤
│  AUTHORITY LAYER                                                   │
│  DID resolution · legal_identity registry · capability scope       │
└────────────────────────────────────────────────────────────────────┘
                                                          ↑ to regulator
```

Evidence flows upward through the layers; trust establishment flows downward (higher-layer components depend on lower-layer identity and authority bindings).

## 1. Authority Layer

**Purpose.** Establishes who is authorised to sign GPR entries, what scope of decisions each authority may make, and how cryptographic identity binds to legal identity. Answers two questions: *who is this signing key?* and *what may they decide?*

**Required capabilities:**
- Decentralized Identifier resolution for `did:web` and `did:key` at minimum
- Legal identity registry supporting LEI lookup (ISO 17442), EU EORI lookup, and at least one jurisdictional company-number resolver
- Capability-scope policy enforcement supporting role-based or attribute-based access control with a declarative policy language
- Key custody appropriate to the risk tier of systems being governed (software keystore for Managed; HSM-backed for Critical)

**Example fits.** Open-source DID resolvers from the Decentralized Identity Foundation, the Linux Foundation Sigstore Fulcio component for keyless signing, Open Policy Agent (OPA) or AWS Cedar for policy enforcement, PKCS#11-compliant HSMs from any major hardware vendor.

**v0.2.0 reference implementation:** `ai_gr.crypto.sign.KeyPair` (software keystore), `ai_gr.schema.LegalIdentity`, `ai_gr.adapters.opa` (policy enforcement reference pattern).

## 2. Evidence Layer

**Purpose.** Stores and retrieves the substantive artifacts referenced by GPR entries: datasets, model weights, evaluation reports, red-team results, SBOMs, DPIAs, FRIAs, conformity dossiers, instructions for use. The evidence layer is where the Annex IV technical file actually lives (§5.3.1 of the paper).

**Required capabilities:**
- Content-addressable storage with SHA-256 (or stronger) hashing
- SBOM generation in SPDX 2.3 or CycloneDX 1.5+ format
- Model weight hashing with provenance binding (Sigstore-style attestations are a natural fit)
- Evaluation result storage in a structured machine-readable format
- Evidence retention policy enforcement compatible with EU AI Act Article 18 ten-year retention and HIPAA six-year minimum

**Example fits.** S3-compatible object stores (any vendor), OCI registries, IPFS for genuinely content-addressed storage, Sigstore Cosign for signed model artifacts, SPDX/CycloneDX toolchains (Syft, Trivy, Tern, or equivalents). For evaluation frameworks: NIST AI 600-1, UK AISI Inspect, Stanford HELM, lm-evaluation-harness, and equivalents — all compatible.

**v0.2.0 reference implementation:** `ai_gr.schema.Evidence` (content-addressable references), `ai_gr.adapters.sigstore` (model attestation reference pattern).

## 3. GPR Layer

**Purpose.** Constructs, validates, and signs individual GPR entries. This is where the schema (§4.4 of the paper) is enforced and the canonicalization (§4.5) is applied. The GPR layer is the only layer whose interface is fully prescribed by the framework specification; the others are vendor-neutral at the capability level.

**Required capabilities:**
- JSON-LD 1.1 processing with context document resolution
- RFC 8785 (JCS) canonicalization
- Pydantic v2 (or equivalent strict-typing) validation against the GPR schema
- Ed25519 signing per RFC 8032, with provision for algorithm upgrade via the `attestation.signature` algorithm prefix
- RFC 3161 trusted timestamping client

**v0.2.0 reference implementation:** `ai_gr.schema`, `ai_gr.crypto.sign`, `ai_gr.crypto.timestamp`. Uses `pyld` for JSON-LD, Pydantic v2 for validation, `rfc8785` for canonicalization, `cryptography` for Ed25519.

## 4. Chain Layer

**Purpose.** Stores GPR entries in an append-only structure where each entry's `linkage.prev_hash` binds it to its predecessor. The chain layer is what makes the audit artifact *the chain itself* rather than any individual entry (§3.3 of the paper).

**Required capabilities:**
- Append-only storage with cryptographic integrity verification across entries
- Merkle-tree or transparency-log aggregation for efficient bulk verification
- Trusted timestamp anchoring per RFC 3161
- Optional but recommended public anchoring (e.g., transparency log or blockchain) to provide third-party-verifiable time bounds
- Chain verification tooling that any party (including a regulator with no prior trust relationship to the operator) can run independently

**Example fits.** Google's Trillian and certificate transparency log implementations, Sigstore's Rekor transparency log, Linux Foundation's in-toto attestation framework's chain features, and (for organisations comfortable with the infrastructure) Ethereum-based or Hyperledger-Fabric-based anchoring.

**v0.2.0 reference implementation:** `ai_gr.store.FilesystemStore` (file-per-entry append-only with chain-integrity validation at append time), `ai_gr.crypto.verify` (chain verification), `ai-gr-verify` CLI.

## 5. Integration Layer

**Purpose.** Connects AI-GR to the existing enterprise governance, observability, identity, and regulatory-submission infrastructure. This is where AI-GR meets the deployment reality of an enterprise that already has tooling and cannot rip-and-replace it. The integration layer is the most vendor-neutral by necessity — the enterprise's existing tools determine what adapters are required.

**Required capabilities:**
- Adapter pattern for consuming evidence from upstream governance platforms (model registries, governance Factsheets, evaluation frameworks)
- Adapter pattern for emitting events to downstream observability and SIEM systems
- IAM integration supporting SCIM (RFC 7644), OIDC, and SAML 2.0 at minimum
- Workflow integration for triggering Build-gate, Deploy-gate, and Operate-gate entry creation from existing CI/CD or MLOps pipelines
- Regulatory-submission export producing artifacts in formats consumable by relevant authorities

**Example fits.** Generic webhook handlers, OpenTelemetry collectors, any SCIM/OIDC/SAML-compliant identity provider, GitOps and pipeline platforms (Argo, Tekton, GitHub Actions, GitLab CI, Jenkins, Azure Pipelines — all equivalently compatible), SOAR platforms for governance-event response orchestration.

**v0.2.0 reference implementation:** `ai_gr.export.dossier` (regulatory export), `ai_gr.adapters.otel` (OpenTelemetry reference pattern). SCIM/OIDC/SAML integration documented but reference clients deferred to v0.3.

## Deployment patterns

Four deployment patterns cover the practical variation:

### Cloud-native
All five layers run on managed cloud services. Public anchoring is straightforward; key custody uses cloud-vendor HSMs (KMS-style). Integration layer adapters connect to managed observability and identity services.

**Suitable for:** most Critical-tier deployments where the cloud vendor has appropriate regulatory certifications (FedRAMP, C5, ENS, ISO 27001).

### On-premises
Authority and Chain layers run inside the enterprise security perimeter; Evidence layer uses on-premises object storage. Public anchoring may be omitted or directed at an internal transparency log.

**Suitable for:** highly regulated sectors (defense, central banking) where external dependencies are restricted.

### Hybrid
Authority and GPR layers on-premises; Chain layer split between internal log and external public anchoring; Evidence layer on managed cloud with encryption-at-rest under enterprise-controlled keys.

**The most common pattern** in practice for Critical-tier enterprise deployments.

### Air-gapped
All layers run inside an isolated network with no external connectivity. Timestamping uses an internal RFC 3161 TSA. Public anchoring is unavailable; the chain's integrity relies entirely on the internal trust model.

**Suitable only for** highly specialised deployments (classified national-security systems). The loss of external time-bound verifiability is a real cost that should be weighed against the air-gap benefit.

## What the architecture explicitly does not specify

Three things are deliberately left to deployments:

- **User interfaces.** The framework specifies the data model and interfaces but not how humans interact with the system. Dashboards, approval workflows, and operator consoles are deployment concerns.
- **Multi-tenant isolation.** The framework specifies single-organisation chains; multi-tenant deployments (e.g., a managed-service provider running AI-GR for many clients) require additional architectural patterns not yet specified.
- **Performance and scale.** The framework specifies no throughput targets; deployments must size the Evidence and Chain layers for their expected GPR-entry production rate.

All three are candidates for future specification versions; v0.2 leaves them to the implementer.
