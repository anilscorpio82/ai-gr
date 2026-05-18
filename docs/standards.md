# Standards Conformance

This page mirrors `STANDARDS.md` at the repository root for documentation-site navigation. Both reflect Table 7 of the v1.4 paper.

## Capability requirements matrix

| Layer | Capability | Standard / protocol reference |
|---|---|---|
| Authority | DID resolution | W3C DID Core 1.0; did:web; did:key |
| Authority | Legal identity registry | ISO 17442 (LEI); EU EORI; national company registers |
| Authority | Capability-scope policy | Open Policy Agent (Rego); AWS Cedar; or equivalent |
| Authority | Key custody | PKCS#11; FIPS 140-3 where applicable |
| Evidence | Content addressing | SHA-256 (FIPS 180-4); content-hash-as-URL |
| Evidence | SBOM generation | SPDX 2.3; CycloneDX 1.5+ |
| Evidence | Model weight attestation | Sigstore (cosign); in-toto attestation |
| Evidence | Evaluation result format | Structured JSON / JSON-LD |
| GPR | JSON-LD processing | W3C JSON-LD 1.1 |
| GPR | Canonicalization | RFC 8785 (JCS) |
| GPR | Schema validation | Pydantic v2 (or equivalent strict typing) |
| GPR | Signing | RFC 8032 (Ed25519); algorithm-prefixed extensible |
| GPR | Timestamping | RFC 3161 TSA client |
| Chain | Append-only storage | Merkle tree or transparency log structure |
| Chain | Aggregation | RFC 6962 (CT-style) or in-toto attestation chain |
| Chain | Public anchoring (optional) | Sigstore Rekor; public-ledger anchoring |
| Integration | Identity | SCIM (RFC 7644); OIDC; SAML 2.0 |
| Integration | Observability | OpenTelemetry |
| Integration | Pipeline triggers | Webhook (HTTP+HMAC); CloudEvents 1.0 |
| Integration | Regulatory export | Plain JSON / PDF for current authority portals |

## Hard constraints

These cannot be substituted in v0.2.0 without bumping the AI-GR specification version (currently `https://ai-gr.dev/v1`):

- **RFC 8785 (JCS)** for canonicalization
- **SHA-256** for content hashing (algorithm is named in the spec; future versions may add SHA-3 or post-quantum primitives via the algorithm-prefix mechanism)
- **The GPR schema shape** as defined in `ai_gr.schema.GPREntry`

## What can be substituted

Everything else. The framework is vendor-neutral at the capability level. See [`STANDARDS.md`](https://github.com/anilscorpio82/ai-gr/blob/main/STANDARDS.md) at the repository root for the full discussion.
