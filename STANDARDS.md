# Standards Conformance — AI-GR v0.2.0

This document is the authoritative source for which open standards AI-GR conforms to. It mirrors **Table 7** of the v1.4 paper ("Capability requirements matrix"). The framework specification binds capabilities to protocols, **not to vendor products** — any vendor or open-source implementation meeting the protocol-level interface satisfies the framework.

## Capability requirements matrix

| Layer | Capability | Standard / protocol reference | v0.2.0 reference impl |
|---|---|---|---|
| Authority | DID resolution | W3C DID Core 1.0; did:web; did:key | Pydantic DID-pattern validation; `did:web` resolution in `ai_gr.crypto.verify` |
| Authority | Legal identity registry | ISO 17442 (LEI); EU EORI; national company registers | `LegalIdentity` schema (multi-format `registration_id`) |
| Authority | Capability-scope policy | Open Policy Agent (Rego); AWS Cedar; or equivalent | `ai_gr.adapters.opa` reference pattern |
| Authority | Key custody | PKCS#11; FIPS 140-3 where applicable | Software keystore in `ai_gr.crypto.sign.KeyPair`; PKCS#11 extension point documented |
| Evidence | Content addressing | SHA-256 (FIPS 180-4); content-hash-as-URL | `GPREntry.content_hash()`; `Sha256Hex` type |
| Evidence | SBOM generation | SPDX 2.3; CycloneDX 1.5+ | Accepted as `evidence.sbom` string reference |
| Evidence | Model weight attestation | Sigstore (cosign); in-toto attestation | `ai_gr.adapters.sigstore` reference pattern |
| Evidence | Evaluation result format | Structured JSON / JSON-LD with eval-method identifier | `evidence.evaluations` list field |
| GPR | JSON-LD processing | W3C JSON-LD 1.1 | `@context = "https://ai-gr.dev/v1"` |
| GPR | Canonicalization | RFC 8785 (JCS) | `rfc8785` library (v0.2.0 hard requirement) |
| GPR | Schema validation | Pydantic v2 (or equivalent strict typing) | Pydantic v2 with `extra="forbid"` |
| GPR | Signing | RFC 8032 (Ed25519); algorithm-prefixed extensible | `ai_gr.crypto.sign`; `attestation.signature_alg` field |
| GPR | Timestamping | RFC 3161 TSA client | `ai_gr.crypto.timestamp` (stub in v0.2.0; live integration v0.3) |
| Chain | Append-only storage | Merkle tree or transparency log structure | `ai_gr.store.FilesystemStore` (file-per-entry append-only) |
| Chain | Aggregation | RFC 6962 (CT-style) or in-toto attestation chain | Linear linkage chain in v0.2.0; Merkle aggregation v0.3 |
| Chain | Public anchoring (optional) | Sigstore Rekor; or public-ledger anchoring | `ai_gr.adapters.sigstore` Rekor integration pattern |
| Integration | Identity | SCIM (RFC 7644); OIDC (OpenID Connect); SAML 2.0 | Documented integration points; reference clients in v0.3 |
| Integration | Observability | OpenTelemetry | `ai_gr.adapters.otel` reference pattern |
| Integration | Pipeline triggers | Webhook (HTTP+HMAC); CloudEvents 1.0 | Documented contract; reference handler in v0.3 |
| Integration | Regulatory export | Plain JSON / PDF for current authority portals | `ai_gr.export.dossier` (single-regime and multi-regime) |

## What this means in practice

If you want to substitute a different implementation for any of the above:

- **Authority layer:** swap the DID method (e.g., `did:ion` instead of `did:web`); swap the HSM (use PKCS#11-compliant hardware from any vendor); swap the policy engine (use Cedar or your own engine; the GPR schema doesn't care).
- **Evidence layer:** swap the object store (S3-compatible, OCI registry, IPFS, on-prem MinIO — all fine); swap the SBOM tool (Syft, Trivy, Tern, or others); swap the evaluation framework (NIST AI 600-1, UK AISI Inspect, HELM, lm-evaluation-harness, or equivalent).
- **GPR layer:** the canonicalization (RFC 8785) and signing (RFC 8032) are the only hard constraints. Use any JCS-compliant library; use any Ed25519 library with constant-time operations.
- **Chain layer:** the append-only invariant is the constraint; the storage mechanism (filesystem, transparency log, blockchain) is the deployment choice.
- **Integration layer:** any SCIM/OIDC/SAML-compliant IdP; any OpenTelemetry-compliant observability backend; any CI/CD platform.

## Hard constraints (cannot be substituted in v0.2.0)

These are baked into the wire format and changing them requires bumping the AI-GR specification version (currently `https://ai-gr.dev/v1`):

- **RFC 8785 (JCS)** for canonicalization. Different canonicalization → different content hashes → broken chain interoperability across implementations.
- **SHA-256** for content hashing. Algorithm is named in the spec; future versions may add SHA-3 or post-quantum primitives via the algorithm-prefix mechanism.
- **The GPR schema shape** as defined in `ai_gr.schema.GPREntry` and surfaced in `docs/schema_spec.md`. Field additions are minor-version compatible; field removals or renames are breaking.

## Standards we explicitly do not adopt

- **Centralized identity assertion mechanisms** (e.g., uploading all signing keys to a single vendor's KMS as the sole source of truth). AI-GR is vendor-neutral by design; a deployment may choose to use vendor KMS internally, but the framework specification does not require it.
- **Self-attestation alone for Critical-tier deployments.** The `LegalIdentity` requirement makes self-attestation incomplete: the cryptographic DID layer attests to the signing identity, but the named legal person bound by EU AI Act / HIPAA / GDPR obligations must be separately identifiable. Note that AI-GR permits self-attestation as the default model (unlike OVERT, which mandates structural independence); this is a deliberate trade-off documented in §8.12 of the v1.4 paper.
