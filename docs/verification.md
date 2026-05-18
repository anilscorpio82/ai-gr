# Verification

The `ai-gr-verify` command-line tool is the standalone verifier that any third party — regulator, auditor, downstream operator — can run against a GPR chain to validate its integrity.

## Why a separate verifier?

The main `ai-gr` CLI offers `ai-gr verify` as a subcommand, but it shares a code path with the chain construction logic. `ai-gr-verify` is a **separate entry point** with the explicit design goal of being runnable by parties who have no relationship with the operator:

- **No write paths** — the verifier never modifies the chain.
- **No dependencies on signing infrastructure** — the verifier only needs the public keys embedded in the entries, not access to any HSM, KMS, or DID resolution service.
- **Self-contained output** — the verifier produces a structured pass/fail report on stdout; nothing is logged elsewhere.

A regulator with a copy of a GPR chain (e.g., obtained via Article 23 EU AI Act information request) can run `ai-gr-verify` against it in an air-gapped environment and get a structured answer about the chain's integrity. That's the design intent.

## Five checks

| # | Check | What it validates |
|---|---|---|
| 1 | Schema conformance | Every file loads as a valid `GPREntry` against schema v0.2.0 |
| 2 | Canonicalization (RFC 8785) | Recomputed canonical bytes match the RFC 8785 output and are deterministic |
| 3 | Hash linkage | Each entry's `linkage.prev_hash` matches the prior entry's `content_hash()` |
| 4 | Signatures (Ed25519) | Each entry's Ed25519 signature verifies against the embedded public key |
| 5 | Critical-tier `legal_identity` | Every Critical-tier entry carries `authority.legal_identity` |

## Usage

```bash
# Verify all entries in a store
ai-gr-verify ./demo-store

# Verify a specific chain by root URN
ai-gr-verify ./demo-store --chain urn:gpr:acme-health/cds-agent

# Emit the report as JSON instead of a Rich table
ai-gr-verify ./demo-store --json > verification-report.json
```

Exit codes:

- `0` — all five checks passed
- `1` — at least one check failed
- `2` — the chain could not be loaded at all

## Sample output

```
                AI-GR Chain Verification — ./demo-store
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check                        ┃ Result ┃ Detail                               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Schema conformance           │ ✓ PASS │ All 5 entries validate                │
│ Canonicalization (RFC 8785)  │ ✓ PASS │ Canonicalization is deterministic     │
│ Hash linkage                 │ ✓ PASS │ All 5 entries form a valid hash chain │
│ Signatures (Ed25519)         │ ✓ PASS │ All 5 signatures verify               │
│ Critical-tier legal_identity │ ✓ PASS │ All 5 Critical-tier entries carry it  │
└──────────────────────────────┴────────┴──────────────────────────────────────┘

Overall: ALL CHECKS PASSED
Total entries verified: 5
```

## What `ai-gr-verify` does not do

- It does **not** verify that the public key embedded in each entry belongs to the claimed approver DID. That requires DID resolution and a trust relationship with the DID method's infrastructure. For high-stakes audits, follow up the cryptographic verification with DID resolution against the relevant authority registry.
- It does **not** evaluate the substantive correctness of regime claims. A chain can pass all five checks and still claim regime coverage that the underlying evidence does not actually support; substantive claim correctness is a regulator's call, not a tool's.
- It does **not** verify external Sigstore Rekor inclusion. If the chain references Rekor log indices in `evidence.additional.sigstore_attestation.rekor_log_index`, those should be independently verified against the public Rekor log.

## Integration into CI/CD

`ai-gr-verify` is suitable for pre-deployment gates:

```yaml
# .github/workflows/governance-check.yml
- name: Verify governance chain
  run: ai-gr-verify ./governance-store --json > verify-report.json
- name: Block deploy if verification fails
  if: failure()
  run: exit 1
```
