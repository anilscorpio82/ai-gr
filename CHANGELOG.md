# Changelog

All notable changes to AI-GR are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-05-18

Schema and regulatory-coverage expansion matching v1.4 of the AI-GR paper.
The two consequential changes are an additive schema field
(`Authority.legal_identity`) required for Critical-tier entries and a
correctness fix to canonicalization (RFC 8785). The fix means hashes
computed by v0.1.0 are not byte-identical to v0.2.0 hashes for entries
containing floats; this is a one-time transition cost in exchange for
spec-compliant interoperability across implementations.

### Added
- **`LegalIdentity` sub-model** (`ai_gr.schema.LegalIdentity`) — binds the
  cryptographic DID-based authority to the named legal person required by
  EU AI Act Article 47 (Declaration of Conformity), HIPAA (Business
  Associate Agreement framework), and other regulatory regimes. Required
  for Critical-tier GPR entries; enforced by `GPREntry.model_post_init`.
  Fields: `name`, `registration_id` (LEI / EORI / national company number),
  `jurisdiction` (ISO 3166-1 alpha-2), `address`, `contact_email`,
  optional `gdpr_role`.
- **`GdprRole` enum** (`controller`, `joint_controller`, `processor`,
  `sub_processor`, `not_applicable`) — set on `LegalIdentity` for GDPR-
  relevant deployments.
- **`Iso3166Alpha2` type alias** — Pydantic-enforced two-letter country code.
- **Certificate Revocation List (`ai_gr.crypto.crl`)** — reference primitive
  for handling compromised signing keys. The verifier rejects signatures
  made *after* the signing DID was revoked, so a stolen key can be
  neutralised without rewriting the immutable chain. In-memory storage in
  v0.2.0; persistent storage and transparency-log anchoring deferred to v0.3.
- **Critical-tier invariant** — `GPREntry.model_post_init` now rejects
  Critical-tier entries that lack `authority.legal_identity`.
- **New regime modules** matching the v1.4 paper's expanded regime coverage:
  EU AI Act Article 26 (deployer obligations), GDPR (with Article 17 right-
  to-erasure patterns), NIS2 Directive, MDR/IVDR, DORA, DSA, Data Act,
  Cyber Resilience Act, EHDS.
- **Reference-pattern adapters** (`ai_gr.adapters`) for Sigstore, OPA, and
  OpenTelemetry. These are intentionally reference patterns — they
  demonstrate the integration shape but require production hardening
  (error handling, retries, real endpoint configuration) before use in
  regulated deployments.
- **`ai-gr-verify` CLI** — standalone verification tool that any third
  party (regulator, auditor, downstream operator) can run to validate a
  GPR chain's integrity, signatures, and Critical-tier legal_identity
  presence without needing access to the original signing infrastructure.
- **Cross-regime worked example** (`examples/cross_regime_evidence`) —
  demonstrates a single Build-gate GPR entry claiming compliance with EU
  AI Act Annex IV, GDPR Article 35, HIPAA §164.312, and NIST AI RMF
  Manage-2.3 simultaneously, exercising the new regime modules.
- **`STANDARDS.md`** — mirrors Table 7 of the v1.4 paper, binding each
  layer of the reference architecture to specific open standards.
- **`ARCHITECTURE.md`** — mirrors §6 of the v1.4 paper, documenting the
  five-layer reference architecture and four deployment patterns.
- **`CITATION.cff`** — Citation File Format metadata for the v1.4 paper
  and the v0.2.0 reference implementation.
- **mkdocs documentation site** under `docs/` with content pages for the
  schema, architecture, regime mappings, and adapter patterns.

### Changed
- **Canonicalization is now RFC 8785 (JCS) compliant** via the `rfc8785`
  library. The prior `json.dumps(sort_keys=True)` approach was close to
  JCS but diverged on float rendering (`1.0` vs `1`, `1.5e-5` vs
  `0.000015`) and a few other edge cases. The new behaviour is what the
  v1.4 paper §4.5 specifies and what independent implementations need to
  match for chain interoperability.
- **`ChainBuilder` constructor** now accepts an optional `legal_identity`
  parameter and propagates it to every entry's Authority block. This is
  the ergonomic path for building Critical-tier chains.
- **Examples and tests** updated to construct realistic `LegalIdentity`
  values where Critical tier is used.

### Fixed
- Canonicalization edge cases around float representation that produced
  spec-non-compliant hashes for floating-point evidence values. Existing
  v0.1.0 chains containing floats will produce different hashes under
  v0.2.0; this is intentional and aligns the implementation with RFC 8785.

### Notes for v0.1.0 → v0.2.0 migrators
- If you have v0.1.0 chains in production, they remain readable by v0.2.0
  (the field is additive and optional except for Critical-tier
  enforcement). However, `content_hash()` on float-containing entries may
  differ between v0.1.0 and v0.2.0 due to the canonicalization fix; the
  on-disk hashes from v0.1.0 entries will not match recomputed v0.2.0
  hashes for those entries. Treat this as expected behaviour.
- New Critical-tier entries created without `legal_identity` will fail
  validation. Add a `legal_identity` block to your `Authority` for every
  Critical-tier write site, or use `ChainBuilder(legal_identity=...)` to
  have it injected automatically.

## [0.1.0] — 2026-05-18

Initial public release of the AI-GR reference implementation.

### Added
- **Core schema** (`ai_gr.schema`) — Pydantic v2 models for the Governance
  Provenance Record (GPR), with strict `extra="forbid"` validation, URN
  format enforcement, and the agentic-context invariant.
- **JSON-LD serialization** (`ai_gr.jsonld`) — round-trip serialization with
  `@context` validation to guard against schema spoofing.
- **Ed25519 signing and chain verification** (`ai_gr.crypto`) — per-entry
  signatures and full-chain integrity checks (hash linkage + signatures).
- **RFC 3161 trusted timestamp stub** — interface ready; live TSA integration
  in v0.2.
- **The Ribbon** (`ai_gr.ribbon`) — five-gate × three-tier policy matrix with
  per-cell requirement checks.
- **Seven regulatory regime modules** — EU AI Act, NIST AI RMF 1.0
  (incl. GenAI Profile), ISO/IEC 42001:2023, HIPAA Security Rule + HITECH,
  FDA SaMD + PCCP, SEC cybersecurity disclosure, US State AEDT/ADMT laws.
- **Append-only stores** — in-memory and filesystem implementations with
  chain-integrity enforcement at append time.
- **Dossier exporters** (`ai_gr.export`) — single-regime (JSON, Markdown)
  and multi-regime (JSON) regulator-ready dossiers.
- **`ai-gr` CLI** — `keypair`, `verify`, `inspect`, `regimes`, `export`,
  `demo` subcommands.
- **Three worked examples**: clinical decision support (agentic, HIPAA + EU
  AI Act + FDA SaMD), financial advice agent (generative, SEC + ADMT), code
  review agent (agentic, AI-GR Build-gate pattern for AI-augmented code).
- **43 tests** covering schema, signing, chain integrity, policy matrix,
  and regime coverage. 74% line coverage.
- **Documentation**: README with quick-start, architecture diagram, regime
  table, citation block; `docs/architecture.md`; `docs/schema_spec.md`
  (the formal GPR specification).

### Security
- Ed25519 chosen as the only signature algorithm in v0.1 (modern default,
  constant-time).
- All Pydantic models use `extra="forbid"` to reject unknown fields.
- Filesystem store uses atomic write-then-rename to survive interrupted
  writes.
- The signature signs `canonical_bytes()`, which excludes the attestation
  block, preventing recursive-definition vulnerabilities.

[0.2.0]: https://github.com/anilscorpio82/ai-gr/releases/tag/v0.2.0
[0.1.0]: https://github.com/anilscorpio82/ai-gr/releases/tag/v0.1.0
