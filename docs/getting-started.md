# Getting Started

## Install

```bash
git clone https://github.com/anilscorpio82/ai-gr
cd ai-gr
pip install -e ".[dev]"
```

For the reference-pattern adapters (Sigstore, OPA, OpenTelemetry):

```bash
pip install -e ".[adapters]"
```

For building this documentation site:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Run the bundled demo

```bash
# Builds a 5-entry clinical decision support chain.
ai-gr demo --out-dir ./demo-store

# Verify the chain (schema, canonicalization, hash linkage, signatures,
# Critical-tier legal_identity).
ai-gr-verify ./demo-store
```

Expected output:

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
```

## Build a minimal chain in code

```python
from ai_gr import (
    AgenticContext, Decision, Evidence, Gate, GdprRole,
    LegalIdentity, RegimeClaim, RiskTier, Subject, SystemType,
)
from ai_gr.builder import ChainBuilder
from ai_gr.crypto import KeyPair

keypair = KeyPair.generate()

subject = Subject(
    system="MyAgent",
    version="1.0.0",
    type=SystemType.AGENTIC,
    description="Example agent",
)

# Required for Critical tier in schema v0.2.0+ — bind cryptographic identity
# to a named legal person.
legal_identity = LegalIdentity(
    name="Example Corp Ltd.",
    registration_id="LEI:EXAMPLE000000000001",
    jurisdiction="GB",
    address="1 Example Lane, London",
    contact_email="compliance@example.com",
    gdpr_role=GdprRole.CONTROLLER,
)

builder = ChainBuilder(
    org="example-co",
    system="my-agent",
    subject=subject,
    keypair=keypair,
    approver_did="did:web:example-co:caio",
    legal_identity=legal_identity,
)

builder.append(
    gate=Gate.CONCEIVE,
    tier=RiskTier.CRITICAL,
    decision=Decision.APPROVE,
    regimes=[
        RegimeClaim(regime="EU-AI-Act:high-risk"),
        RegimeClaim(regime="GDPR:Article 35 — DPIA"),
    ],
    agentic_context=AgenticContext(
        action_authority=["read:data"],
        tool_registry=["my-api"],
        human_oversight="in-the-loop",
    ),
)

print(f"Chain has {len(builder.chain)} entries.")
print(f"First entry hash: {builder.chain[0].content_hash()}")
```

## Run the worked examples

Three worked examples ship with the implementation:

```bash
# 1. Clinical decision support agent — EU MDR + GDPR + US HIPAA + FDA SaMD
python -m examples.clinical_decision_support

# 2. Financial advice agent — SEC + California ADMT
python -m examples.financial_advice_agent

# 3. Code review agent — AI-augmented engineering CI
python -m examples.code_review_agent

# 4. Cross-regime evidence (new in v0.2.0) — 8 simultaneous regimes
python -m examples.cross_regime_evidence
```

The cross-regime example is the most informative — it demonstrates a single Build-gate Evidence block carrying eight simultaneous regime claims (EU AI Act provider + Article 26 deployer, GDPR, MDR, NIS2, HIPAA, NIST AI RMF, with EU AI Act and MDR each carrying multiple sub-claims).

## What to explore next

- [Concepts → The Ribbon](concepts/ribbon.md) — the framework's organising structure
- [Concepts → Governance Provenance Record](concepts/gpr.md) — the artifact schema
- [Schema Specification](schema_spec.md) — the formal GPR v0.2.0 schema
- [Architecture](architecture.md) — the five-layer reference architecture
- [Regulatory Mapping → Overview](regimes/overview.md) — the seventeen-regime coverage
