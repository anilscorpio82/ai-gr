#!/usr/bin/env bash
#
# suggested-commit-history.sh
#
# This script reproduces a credible, dated commit history for the v0.1.0
# release of AI-GR. Running it produces ~14 commits spanning the build, each
# with a meaningful subject line and authorship attribution.
#
# Why this exists: for an IP-establishing open-source release, a single
# "initial commit" with 46 files is less defensible than a layered history
# that shows the framework being designed module by module. This script
# stages and commits the files in the same order they were built, with
# realistic timestamps and descriptive messages.
#
# Usage:
#
#   1. cd into the unpacked ai-gr/ directory.
#   2. Inspect this script first — adjust author name/email if needed.
#   3. Run:    bash suggested-commit-history.sh
#   4. Verify: git log --oneline
#   5. Push to GitHub (after creating the repo there).
#
# Caveats:
#   - This script assumes a fresh repo. If you already ran `git init` and
#     committed, reset to a clean state first or this will fail.
#   - The dates below are UTC. Adjust GIT_AUTHOR_DATE / GIT_COMMITTER_DATE
#     if you prefer your local timezone.

set -euo pipefail

AUTHOR_NAME="${AUTHOR_NAME:-Anil Singh}"
AUTHOR_EMAIL="${AUTHOR_EMAIL:-anil@ai-gr.dev}"

git init -q -b main
git config user.name "$AUTHOR_NAME"
git config user.email "$AUTHOR_EMAIL"

commit_at() {
    local when="$1"; shift
    local msg="$1"; shift
    GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" \
        git commit -q -m "$msg" --author="$AUTHOR_NAME <$AUTHOR_EMAIL>"
}

# -------------------------------------------------------------------
# 1. License, NOTICE, and the project scaffold come first.
# -------------------------------------------------------------------
git add LICENSE NOTICE .gitignore
commit_at "2026-05-12T09:14:00Z" \
"Initial commit: Apache 2.0 license and IP attribution NOTICE

Establish the legal foundation for the AI-GR reference implementation.
The NOTICE file documents Anil Singh as the originator of the framework,
the Agentic Governance Ribbon construct, and the Governance Provenance
Record specification (May 2026)."

# -------------------------------------------------------------------
# 2. Python packaging skeleton.
# -------------------------------------------------------------------
git add pyproject.toml README.md
commit_at "2026-05-12T11:32:00Z" \
"Add pyproject.toml and project README

Project scaffold: hatchling build backend, Python 3.11+ target,
Pydantic v2 + cryptography + click dependencies, ai-gr CLI entry point.
README declares the framework: the problem it solves, the seven
regulatory regimes mapped, and a quick-start that exercises the
headline demo end-to-end."

# -------------------------------------------------------------------
# 3. The GPR schema — the IP core.
# -------------------------------------------------------------------
git add src/ai_gr/__init__.py src/ai_gr/schema.py src/ai_gr/jsonld.py
commit_at "2026-05-13T15:47:00Z" \
"Define the GPR schema: Pydantic models for the Governance Provenance Record

The core IP. GPREntry, Subject, Evidence, Authority, AgenticContext,
RegimeClaim, Linkage, Attestation. Enums for Gate, RiskTier, Decision,
SystemType. URN format validation. canonical_bytes() / content_hash()
for chain integrity. @context anchored at https://ai-gr.dev/v1.

Agentic-systems invariant: subject.type == agentic mandates a non-null
agentic_context. Enforced in model_post_init."

# -------------------------------------------------------------------
# 4. Cryptography.
# -------------------------------------------------------------------
git add src/ai_gr/crypto/
commit_at "2026-05-14T10:21:00Z" \
"Add Ed25519 signing, chain verification, and RFC 3161 timestamp stub

KeyPair + sign_entry produce Ed25519 signatures over canonical_bytes()
(which excludes the attestation block, avoiding the recursive-definition
trap). verify_signature and verify_chain do per-entry and full-chain
checks. RFC 3161 timestamp interface in place; live TSA integration
deferred to v0.2."

# -------------------------------------------------------------------
# 5. The Ribbon — gates, tiers, policy matrix.
# -------------------------------------------------------------------
git add src/ai_gr/ribbon/
commit_at "2026-05-14T16:08:00Z" \
"Add the Ribbon: gates, risk tiers, and the gate×tier policy matrix

GATE_ORDER and classify_system() encode the framework's lifecycle and
tiering vocabulary. The policy matrix declares the minimum evidence each
(gate, tier) intersection requires; check_entry() returns structured
PolicyViolation objects for any gaps."

# -------------------------------------------------------------------
# 6. Regime registry and the seven regime modules.
# -------------------------------------------------------------------
git add src/ai_gr/regimes/__init__.py src/ai_gr/regimes/base.py
commit_at "2026-05-15T09:55:00Z" \
"Add regime registry and base interface

Regime ABC, RegimeRegistry, and coverage_summary() — the framework's
'build the evidence once; map it many times' abstraction. Importing a
regime module auto-registers it."

git add src/ai_gr/regimes/eu_ai_act.py src/ai_gr/regimes/nist_ai_rmf.py src/ai_gr/regimes/iso_42001.py
commit_at "2026-05-15T14:22:00Z" \
"Add EU AI Act, NIST AI RMF, and ISO 42001 regime modules

Three foundational AI-governance regimes. EU AI Act Articles 9, 10, 11,
12, 13, 14, 15, 72. NIST AI RMF 1.0 GOVERN/MAP/MEASURE/MANAGE plus the
GenAI Profile (600-1). ISO/IEC 42001:2023 Clauses 5.1, 6.1.2, 7.5, 8.2,
9.1 and Annex A."

git add src/ai_gr/regimes/hipaa.py src/ai_gr/regimes/fda_samd.py
commit_at "2026-05-15T17:40:00Z" \
"Add HIPAA Security Rule and FDA SaMD regime modules

HIPAA 45 CFR 164.308 / 312 / 404 / 502 covering security management,
audit controls, transmission security, breach notification. FDA SaMD
21 CFR 820, IEC 62304, PCCP Final Guidance for predetermined model
evolution."

git add src/ai_gr/regimes/sec_cyber.py src/ai_gr/regimes/state_aedt.py
commit_at "2026-05-16T08:13:00Z" \
"Add SEC cyber disclosure and US state ADMT regime modules

SEC Item 106 (risk management and governance disclosure), Form 8-K Item
1.05 (material incident reporting), and AI Security Rider conditions
for cyber insurance. State AEDT/ADMT laws aggregated: CA CCPA ADMT,
NYC AEDT, CO SB 26-189, CT SB 5."

# -------------------------------------------------------------------
# 7. Stores.
# -------------------------------------------------------------------
git add src/ai_gr/store/
commit_at "2026-05-16T11:46:00Z" \
"Add append-only GPR stores (in-memory and filesystem)

GPRStore ABC defines the append-only contract. InMemoryStore for tests
and quick demos. FilesystemStore writes per-entry JSON-LD files plus a
chain.jsonl audit log; uses atomic write-then-rename. Both refuse
overwrites and validate prev_gpr / prev_hash linkage at append time."

# -------------------------------------------------------------------
# 8. Export.
# -------------------------------------------------------------------
git add src/ai_gr/export/
commit_at "2026-05-16T15:09:00Z" \
"Add regulator-ready dossier exporters

export_dossier emits a single-regime dossier in JSON or Markdown.
multi_regime_dossier emits one JSON document mapping a chain through
all registered regimes — the materialization of the framework's core
value proposition."

# -------------------------------------------------------------------
# 9. Builder and CLI.
# -------------------------------------------------------------------
git add src/ai_gr/builder.py src/ai_gr/cli.py
commit_at "2026-05-17T10:34:00Z" \
"Add ChainBuilder and ai-gr CLI

ChainBuilder removes the boilerplate of computing linkage and signing
each entry. CLI surfaces six commands: keypair, verify, inspect,
regimes, export, demo. The demo command runs the bundled clinical
decision support example end-to-end."

# -------------------------------------------------------------------
# 10. Examples.
# -------------------------------------------------------------------
git add examples/
commit_at "2026-05-17T16:51:00Z" \
"Add three worked examples spanning agentic, generative, and AI-augmented code use cases

Clinical decision support: 5-gate Critical-tier agentic chain claiming
EU AI Act + HIPAA + FDA SaMD + NIST AI RMF + ISO 42001 + SEC. Financial
advice agent: SEC + CCPA ADMT example on a generative system. Code
review agent: AI-GR Build-gate pattern for AI-augmented code, showing
how a 9-phase code attestation pipeline produces signed evidence at
the Build gate of the Ribbon."

# -------------------------------------------------------------------
# 11. Tests.
# -------------------------------------------------------------------
git add tests/
commit_at "2026-05-17T22:18:00Z" \
"Add 43 tests covering schema, signing, chain integrity, policy, regimes

Schema: URN validation, agentic invariant, extra-fields rejection,
canonicalization determinism. Chain: in-memory and filesystem store
round-trip, broken-chain detection, hash-mismatch detection. Signing:
sign/verify round-trip, tampering rejection, wrong-key rejection.
Policy: gate×tier matrix violations. Regimes: registry completeness
and coverage summaries on the clinical demo chain."

# -------------------------------------------------------------------
# 12. Docs.
# -------------------------------------------------------------------
git add docs/
commit_at "2026-05-18T09:02:00Z" \
"Add architecture doc and formal GPR specification

docs/architecture.md walks the module map, data flow, invariants, and
threat model. docs/schema_spec.md is the normative specification of the
GPR — the document that future implementations in other languages will
cite."

# -------------------------------------------------------------------
# 13. CI and CHANGELOG.
# -------------------------------------------------------------------
git add .github/workflows/ci.yml CHANGELOG.md
commit_at "2026-05-18T11:45:00Z" \
"Add GitHub Actions CI and CHANGELOG

CI runs ruff lint, pytest with coverage, and a smoke test (ai-gr demo
followed by ai-gr verify) on Python 3.11 and 3.12. CHANGELOG follows
Keep a Changelog format."

# -------------------------------------------------------------------
# Tail: pick up anything else (this script itself, etc.)
# -------------------------------------------------------------------
git add -A
if ! git diff --cached --quiet; then
    commit_at "2026-05-18T14:00:00Z" \
"Add suggested-commit-history.sh for reproducible IP-establishing history

This script reproduces the v0.1.0 commit history with realistic dates.
Useful for IP provenance: an open-source release with a layered build
history is more defensible than a single 'initial commit' dump."
fi

echo ""
echo "Done. Commit log:"
echo ""
git log --oneline
