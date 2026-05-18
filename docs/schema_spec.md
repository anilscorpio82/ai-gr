# GPR specification — v1

This document is the normative specification of the **Governance Provenance
Record (GPR)** — the artifact emitted at every gate of the Agentic Governance
Ribbon (AI-GR).

  - Specification URL: `https://ai-gr.dev/v1`
  - Originator: Anil Singh, May 2026
  - Status: v0.1 (reference)
  - Language: English. The schema is the authoritative source.

## 1. Terminology

| Term | Meaning |
|---|---|
| **Framework** | AI-GR — the Agentic Governance Ribbon. |
| **Gate** | One of five lifecycle decision points: Conceive, Build, Deploy, Operate, Evolve (plus terminal Retire). |
| **Risk tier** | One of three control depths: Critical, High, Managed. |
| **GPR entry** | A single signed JSON-LD document attesting to a gate decision. |
| **Chain** | An ordered sequence of GPR entries for one (org, system) pair. |
| **Regime** | A regulatory or standards regime (EU AI Act, HIPAA, etc.) referenced by GPR entries. |
| **Subject** | The AI system or model being governed. |
| **Authority** | The identity (DID) and scope of the entity rendering the decision. |
| **Attestation** | The cryptographic block (signature, public key, timestamp). |

## 2. JSON-LD shape

Every GPR entry MUST include `"@context": "https://ai-gr.dev/v1"` and
`"@type": "GPREntry"`. Implementations MUST reject documents whose `@context`
value is not recognized.

```json
{
  "@context": "https://ai-gr.dev/v1",
  "@type": "GPREntry",
  "schema_version": "0.1.0",
  "id": "urn:gpr:<org>/<system>/<gate>/<seq>",
  "subject": { ... },
  "gate": "Conceive | Build | Deploy | Operate | Evolve | Retire",
  "risk_tier": "Critical | High | Managed",
  "decision": "approve | approve_with_conditions | reject | rollback | defer",
  "evidence": { ... },
  "authority": { ... },
  "regime": [ ... ],
  "agentic_context": { ... } | null,
  "linkage": { ... },
  "attestation": { ... }
}
```

## 3. Identifiers

GPR entries are identified by URNs of the form:

```
urn:gpr:<org>/<system>/<gate>/<seq>
```

where:

- `<org>` is the originating organization slug (lowercase, hyphens permitted),
- `<system>` is the subject system slug,
- `<gate>` is one of `conceive`, `build`, `deploy`, `operate`, `evolve`, `retire`,
- `<seq>` is a zero-padded decimal sequence number of at least four digits.

Example: `urn:gpr:acme-health/cds-agent/build/0001`.

## 4. Linkage and chain integrity

Each entry references the prior entry via:

- `linkage.prev_gpr` — the URN of the prior entry (`null` for the chain root).
- `linkage.prev_hash` — the SHA-256 of the prior entry's *canonical bytes* (see §6).
- `linkage.chain_root` — the URN of the root entry (i.e., the Conceive entry).

A chain is **valid** iff:

1. The root entry's `linkage.prev_gpr` is `null`.
2. For every adjacent pair `(prev, curr)`:
   - `curr.linkage.prev_gpr == prev.id`
   - `curr.linkage.prev_hash == SHA-256(canonical_bytes(prev))`
3. Every entry's signature verifies against its declared public key.

## 5. Attestation

The attestation block contains:

- `signature` — algorithm-prefixed base64 (`ed25519:<base64>`).
- `signature_alg` — currently `ed25519` (only algorithm supported in v0.1).
- `public_key` — base64-encoded raw 32-byte Ed25519 public key, OR a DID
  resolution hint.
- `timestamp` — ISO 8601 UTC time of signing.
- `rfc3161_token` — optional base64-encoded RFC 3161 TimeStampToken.
- `tsa` — optional identifier of the trusted timestamping authority used.

## 6. Canonicalization for hashing

To compute the content hash of an entry:

1. Render the entry as a JSON-LD dict, including all fields except
   `attestation`.
2. Serialize to JSON with:
   - sorted keys,
   - no whitespace (`separators=(",", ":")`),
   - UTF-8 encoding.
3. SHA-256 the resulting byte string.
4. Hex-encode the digest.

The attestation block is excluded because the signature signs the canonical
bytes — including the signature in its own input is a recursive definition.

**Note:** v0.1 uses simple JSON canonicalization. v1.0 will switch to JSON-LD
URDNA2015 (RFC 8785 / RDF Dataset Canonical Form) for cross-implementation
interoperability.

## 7. The agentic invariant

If `subject.type == "agentic"`, then `agentic_context` MUST NOT be null. The
`agentic_context` block contains at minimum:

- `action_authority`: the actions the agent is authorized to take.
- `tool_registry`: the tools/APIs the agent may call.
- `human_oversight`: one of `in-the-loop`, `on-the-loop`, `audit-only`, `none`.

This invariant is the wedge of AI-GR over predictive/generative-only
frameworks. The Ribbon explicitly attests to action authority as a
first-class governance dimension.

## 8. Regime claims

A single entry MAY claim conformance with multiple regulatory regimes. Each
`RegimeClaim` has:

- `regime`: a colon-separated identifier (e.g. `EU-AI-Act:Article-9`,
  `HIPAA:164.312(b)`, `NIST-AI-RMF:MEASURE-2.3`).
- `citation`: an optional human-readable citation string.
- `evidence_refs`: optional pointers into the parent `Evidence` block.

Implementations SHOULD register regime modules that translate Evidence into
regulator-ready summaries. See `src/ai_gr/regimes/` in the reference
implementation for seven worked regime mappings.

## 9. Evidence content addressing

Where possible, `Evidence` fields SHOULD be content-addressable:

- Datasets MAY include a SHA-256 component: `"<name>:sha256:<hex>"`.
- Model weights are stored as raw 64-char hex SHA-256 strings.
- SBOMs reference content-addressable artifacts (SPDX, CycloneDX).
- Other artifacts MAY be referenced by URI; implementations are free to
  resolve URIs to verify content.

## 10. Backwards compatibility

The `schema_version` field declares the implementation version of the schema.
The `@context` URL declares the major version of the specification. Any
breaking change to the JSON-LD shape produces a new `@context` URL (`/v2`,
etc.).

Implementations MUST reject entries whose `@context` is not recognized.
Implementations MAY accept future `schema_version` values within the same
`@context` if all required fields are present.

---

*This specification is © 2026 Anil Singh and licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The reference
implementation is licensed under Apache 2.0; see [LICENSE](../LICENSE).*
