# AI-GR architecture

This document describes the module structure and the data flow through the
reference implementation. The goal is to make every design choice
discoverable: a future implementer in another language (Go, TypeScript, Rust)
should be able to read this and reproduce the framework's semantics.

## Module map

| Module | Role |
|---|---|
| `ai_gr.schema` | The canonical Pydantic models. Equivalent to the GPR specification. |
| `ai_gr.jsonld` | JSON-LD serialization, deterministic canonicalization for hashing. |
| `ai_gr.crypto.sign` | Ed25519 signing of GPR entries. |
| `ai_gr.crypto.verify` | Per-entry signature and full-chain verification. |
| `ai_gr.crypto.timestamp` | RFC 3161 trusted-timestamp attachment (stub in v0.1). |
| `ai_gr.ribbon.gates` | Lifecycle gate ordering helpers. |
| `ai_gr.ribbon.tiers` | Risk-tier classification heuristics. |
| `ai_gr.ribbon.policy` | The gate × tier requirement matrix. |
| `ai_gr.regimes.base` | Regime interface and process-wide registry. |
| `ai_gr.regimes.*` | Per-regime requirement maps and coverage logic. |
| `ai_gr.store.base` | Append-only store interface (`GPRStore` ABC). |
| `ai_gr.store.memory` | Reference in-memory implementation. |
| `ai_gr.store.filesystem` | Reference filesystem implementation (atomic writes). |
| `ai_gr.export.dossier` | Multi-regime dossier exporters (JSON, Markdown). |
| `ai_gr.builder` | `ChainBuilder` — ergonomic chain construction with auto-linkage. |
| `ai_gr.cli` | Click-based CLI: `keypair`, `verify`, `inspect`, `regimes`, `export`, `demo`. |

## Data flow

```
[Operator decision]                  [Tool / pipeline output]
        │                                       │
        ▼                                       ▼
ChainBuilder.append(...)  ──linkage from prior head──▶  GPREntry
        │                                       │
        │                                       ├─ canonical_bytes() (excludes attestation)
        │                                       └─ content_hash() = SHA-256(canonical_bytes)
        ▼
sign_entry(entry, keypair) ──▶ Attestation { ed25519, public_key, timestamp }
        │
        ▼
attach_rfc3161(entry, tsa_url) ──▶ Attestation { ..., rfc3161_token, tsa }   (optional, v0.2)
        │
        ▼
GPRStore.append(entry)
        │   (validates linkage against current head; refuses overwrites)
        ▼
[ Disk / Postgres / etc. ]
        │
        ▼
verify_chain(chain)
        ├─ each entry: verify_signature
        └─ adjacent pairs: prev_gpr == prior.id AND prev_hash == prior.content_hash()

[ regulator / auditor ]
        │
        ▼
export_dossier(chain, regime, format) ──▶ JSON | Markdown
multi_regime_dossier(chain) ──▶ JSON across all registered regimes
```

## Critical invariants

1. **Append-only at the API surface.** A `GPRStore.append` call validates that
   the new entry's `linkage.prev_gpr` matches the current head for its
   subject system, and that `linkage.prev_hash` matches the head's
   `content_hash()`. Stores never mutate existing entries.

2. **Signature signs the entry minus the attestation block.** This avoids the
   recursive-definition trap (a signature cannot include itself). Mutating
   the attestation block after signing does not invalidate the signature —
   but mutating any other field does.

3. **Content hash drives chain integrity.** Every entry stores the prior
   entry's content hash in `linkage.prev_hash`. Tampering with any historical
   entry breaks the chain at every entry downstream.

4. **`extra="forbid"` everywhere.** Pydantic models reject unknown fields.
   This guards against silent schema drift.

5. **Agentic-systems carry agentic context.** Enforced in
   `GPREntry.model_post_init`. There is no path to create an agentic-typed
   entry without an `agentic_context` block.

## Versioning

- The JSON-LD `@context` is `https://ai-gr.dev/v1`. Any breaking change
  produces `/v2`, etc., and entries reference the version at which they were
  produced.
- `SCHEMA_VERSION` ("0.1.0") is the implementation version of the schema and
  is included in every entry for forward-compatibility checks.
- Regime modules version independently of the core schema — adding a new
  citation to a regime does not bump the schema version.

## Threat model (informational)

| Threat | Mitigation |
|---|---|
| Tampering with a historical entry | Breaks `prev_hash` linkage at every downstream entry; `verify_chain` flags. |
| Replaying an old entry as new | New entries must point to the current head, not any historical entry. |
| Schema spoofing (unknown `@context`) | `from_jsonld_dict` rejects unrecognized contexts. |
| Substituting another approver's public key | Signature fails verification against the substituted key. |
| Back-dating a signature | RFC 3161 timestamping in v0.2 — third-party-attested time. |

## Cross-language portability

The schema is intentionally:

- **JSON-serializable** (no custom binary encodings),
- **Deterministically canonicalizable** (sorted keys, no whitespace, UTF-8),
- **Cryptographically minimal** (one signature algorithm in v0.1).

A second implementation in Go, TypeScript, or Rust must produce byte-identical
canonical bytes for the same entry. v1.0 will replace the simple JSON
canonicalization with JSON-LD URDNA2015 to remove all ambiguity.
