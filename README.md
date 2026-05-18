# AI-GR — Agentic Governance Ribbon™

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Reference Implementation v0.2.0](https://img.shields.io/badge/status-reference--impl-orange.svg)](#)
[![Paper: v1.4](https://img.shields.io/badge/paper-v1.4-green.svg)](#cite-this-work)

> **Agentic Governance Ribbon (AI-GR)** is a provenance-first governance framework
> for agentic AI. This repository is the reference implementation of the framework
> and the Governance Provenance Record (GPR) artifact specification.

**Originator:** Anil Singh
**First public introduction:** May 2026
**Current paper version:** v1.4 (May 2026)
**Specification URL:** [`https://ai-gr.dev/v1`](https://ai-gr.dev/v1)
**Mark:** "Agentic Governance Ribbon" is a trademark of Anil Singh (USPTO application pending). "GPR" and "Governance Provenance Record" are descriptive technical vocabulary in the spec, not claimed marks.

---

## What's new in v0.2.0

- **`LegalIdentity` schema field** binding the cryptographic DID layer to the named legal person required by the EU AI Act, HIPAA, and other regimes. Required for Critical-tier entries.
- **Nine new regime modules** matching the v1.4 paper's expanded coverage: EU AI Act Article 26 (deployer obligations), GDPR, NIS2, MDR/IVDR, DORA, DSA, Data Act, Cyber Resilience Act, EHDS.
- **RFC 8785 (JCS) canonicalization** replacing the prior near-JCS approach. Hashes are now byte-identical to any independent JCS implementation.
- **Certificate Revocation List (CRL) primitive** for handling compromised signing keys. The verifier now rejects signatures made *after* the signing DID was revoked, so a stolen key can be neutralised without rewriting the immutable chain. Reference implementation only — the CRL in v0.2.0 is in-memory; persistent storage and transparency-log anchoring are deferred.
- **Reference-pattern adapters** for Sigstore, OPA, and OpenTelemetry under `ai_gr.adapters`.
- **`ai-gr-verify` CLI** that any third party can run to validate a GPR chain.
- **Cross-regime worked example** exercising the new regime modules.
- **mkdocs documentation site** under `docs/`.

See [CHANGELOG.md](CHANGELOG.md) for the full v0.1.0 → v0.2.0 migration notes. A separate `ai-gr-saas` repository explores commercial SaaS deployment patterns (multi-tenant infrastructure, semantic firewall reverse proxy, admin UI); the present repository is the academic reference implementation paired with the v1.4 working paper and is the appropriate citation target.

---

## The problem AI-GR solves

The major AI governance frameworks in force in 2026 — **NIST AI RMF 1.0**, **ISO/IEC 42001:2023**, the **EU AI Act**, **HIPAA**, **FDA SaMD guidance**, **SEC cyber disclosure** — were designed for *predictive* and *generative* AI systems. They were not designed for systems that:

- take autonomous actions on enterprise data and tools,
- chain multi-step tool calls with delegated authority,
- evolve their own behavior between deployments,
- operate under cyber-insurance "AI Security Riders" that require demonstrable, signed evidence of controls.

AI-GR fills that structural gap with three constructs:

1. **The Ribbon** — five lifecycle gates (Conceive → Build → Deploy → Operate → Evolve) crossed by three risk tiers (Critical / High / Managed). A control gradient, not a binary checklist.
2. **The GPR (Governance Provenance Record)** — a signed, content-addressable, chained artifact emitted at every gate. The chain is tamper-evident by construction.
3. **The regime map** — a single Evidence block on a Build entry can satisfy EU AI Act Annex IV, GDPR Article 35, HIPAA §164.312, NIST AI RMF MEASURE-2.6, and ISO 42001 §6.1.2 simultaneously. Build the evidence once; map it many times.

AI-GR sits **on top of** existing tools (IBM watsonx.governance Factsheets, AWS / Azure Model Cards, NIST AI 600-1, Credo AI registries) — it is an integration layer, not a replacement. See [ARCHITECTURE.md](ARCHITECTURE.md) for the five-layer reference architecture.

---

## Quick start

```bash
git clone https://github.com/anilscorpio82/ai-gr
cd ai-gr
pip install -e ".[dev]"

# Run the bundled clinical-decision-support demo end-to-end.
ai-gr demo --out-dir ./demo-store

# Verify the chain (signatures + hash linkage + legal_identity on Critical tier).
ai-gr-verify ./demo-store

# Export an EU AI Act dossier in Markdown.
ai-gr export ./demo-store urn:gpr:acme-health/cds-agent \
    --regime EU-AI-Act --format markdown > eu-ai-act-dossier.md
```

---

## A minimal GPR entry

```python
from ai_gr import (
    AgenticContext, Authority, Decision, Evidence, Gate, GdprRole,
    GPREntry, LegalIdentity, RegimeClaim, RiskTier, Subject, SystemType,
)

entry = GPREntry(
    id="urn:gpr:acme-health/cds-agent/build/0001",
    subject=Subject(
        system="ClinicalDecisionSupportAgent",
        version="2.3.1",
        type=SystemType.AGENTIC,
    ),
    gate=Gate.BUILD,
    risk_tier=RiskTier.CRITICAL,
    decision=Decision.APPROVE_WITH_CONDITIONS,
    evidence=Evidence(
        datasets=["mimic-iv-v3.0:sha256:a3f2..."],
        evaluations=["bias-eval-2026-05-12.pdf"],
        red_team=["atlas-v1.2-passed"],
        model_weights="9bc4e1" + "0" * 58,
        sbom="spdx-2.3:cds-agent-bom.json",
    ),
    authority=Authority(
        approver="did:web:acme-health:caio",
        delegated_scope="tier:critical;phi:read",
        # Required for Critical tier under schema v0.2.0+ (§4.3 of paper):
        legal_identity=LegalIdentity(
            name="ACME Health Systems Inc.",
            registration_id="LEI:5493001K3F3DUM2KRD89",
            jurisdiction="DE",
            address="Musterstrasse 1, 10115 Berlin, Germany",
            contact_email="compliance@acme-health.example",
            gdpr_role=GdprRole.CONTROLLER,
        ),
    ),
    regime=[
        RegimeClaim(regime="EU-AI-Act:high-risk"),
        RegimeClaim(regime="EU-AI-Act:Art-26"),
        RegimeClaim(regime="GDPR:Art-35-DPIA"),
        RegimeClaim(regime="HIPAA:164.312"),
        RegimeClaim(regime="NIST-AI-RMF:Manage-2.3"),
    ],
    agentic_context=AgenticContext(
        action_authority=["read:phi", "write:ehr:annotation"],
        tool_registry=["epic-fhir-r4", "lab-result-lookup"],
        runtime_context={"temperature": 0.2, "max_steps": 5},
        human_oversight="in-the-loop",
    ),
)
```

For an ergonomic builder that handles chaining and signing automatically, see `ai_gr.builder.ChainBuilder` and the three worked examples under `examples/`.

---

## Regulatory regime coverage

v0.2.0 ships regime modules for seventeen regimes. The framework treats regime as a property of evidence (the GPR `regime` array), not of system, so a single entry can carry multiple regime claims simultaneously.

| Regime | Module | Coverage scope |
|---|---|---|
| EU AI Act (provider) | `ai_gr.regimes.eu_ai_act` | Annex IV technical documentation, conformity assessment |
| EU AI Act Article 26 (deployer) | `ai_gr.regimes.eu_ai_act_deployer` | Articles 26-27 deployer obligations + FRIA |
| GDPR | `ai_gr.regimes.gdpr` | Articles 5, 6, 17, 26, 28, 35; Chapter V transfers |
| NIS2 Directive | `ai_gr.regimes.nis2` | Article 21 cybersecurity risk management |
| MDR/IVDR | `ai_gr.regimes.mdr_ivdr` | EU 2017/745 + 2017/746 SaMD-equivalents |
| DORA | `ai_gr.regimes.dora` | ICT risk management for financial entities |
| DSA | `ai_gr.regimes.dsa` | Platform algorithmic transparency |
| Data Act | `ai_gr.regimes.data_act` | EU 2023/2854 data access and sharing |
| Cyber Resilience Act | `ai_gr.regimes.cra` | EU CRA security-by-design |
| EHDS | `ai_gr.regimes.ehds` | European Health Data Space |
| NIST AI RMF | `ai_gr.regimes.nist_ai_rmf` | Govern, Map, Measure, Manage functions |
| ISO/IEC 42001 | `ai_gr.regimes.iso_42001` | AI management system standard |
| HIPAA + HITECH | `ai_gr.regimes.hipaa` | §164.308 admin, §164.312 technical safeguards |
| FDA SaMD + PCCP | `ai_gr.regimes.fda_samd` | Software as a Medical Device + change control |
| SEC cyber + AI disclosure | `ai_gr.regimes.sec_cyber` | Cybersecurity Risk Management Final Rule 2023 |
| State ADMT/AEDT laws | `ai_gr.regimes.state_aedt` | California ADMT, NYC AEDT, Colorado AI Act |
| FedRAMP + EO 14028 | (planned for v0.3) | US federal deployment controls |

See `ai-gr regimes` (CLI) for a current authoritative list at any commit.

---

## Reference architecture

AI-GR's reference architecture has five layers, each bound to specific open standards. See [STANDARDS.md](STANDARDS.md) for the full capability requirements matrix.

```
┌──────────────────────────────────────────────────────────┐
│  Integration Layer  · SIEM · IAM · observability         │
├──────────────────────────────────────────────────────────┤
│  Chain Layer        · append-only log · Merkle · TSA     │
├──────────────────────────────────────────────────────────┤
│  GPR Layer          · JSON-LD · JCS · Ed25519            │
├──────────────────────────────────────────────────────────┤
│  Evidence Layer     · content-addressable · SBOM         │
├──────────────────────────────────────────────────────────┤
│  Authority Layer    · DID · legal_identity · scope       │
└──────────────────────────────────────────────────────────┘
                                                      ↑ to regulator
```

The architecture is intentionally vendor-neutral. The framework specification binds capabilities to protocols (W3C DID Core 1.0, ISO 17442 LEI, RFC 8785 JCS, RFC 8032 Ed25519, RFC 3161 timestamping, RFC 7644 SCIM, OIDC, SAML 2.0, OpenTelemetry, CloudEvents 1.0, SPDX 2.3 / CycloneDX 1.5+), not to vendor products.

Four deployment patterns are documented: cloud-native, on-premises, hybrid, and air-gapped. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

---

## Reference-pattern adapters

Three adapter modules under `ai_gr.adapters` demonstrate the integration shape for the most common surrounding tools:

- `ai_gr.adapters.sigstore` — signed model attestation via Sigstore Cosign and the Rekor transparency log.
- `ai_gr.adapters.opa` — capability-scope policy enforcement via Open Policy Agent (OPA).
- `ai_gr.adapters.otel` — OpenTelemetry export for downstream observability and SIEM integration.

**These are reference patterns**, not production-grade integrations. They demonstrate the wire-level interface but assume callers will add error handling, retries, real endpoint configuration, and credential management appropriate to their deployment. Install them with `pip install -e ".[adapters]"`.

---

## Verification CLI

Anyone — regulator, auditor, downstream operator — can verify a GPR chain's integrity without access to the original signing infrastructure:

```bash
ai-gr-verify ./path-to-store [--chain urn:gpr:org/system]
```

The verifier checks:
1. **Hash linkage** — each entry's `linkage.prev_hash` matches the prior entry's `content_hash()`
2. **Signatures** — each entry's Ed25519 signature verifies against the embedded public key
3. **Schema conformance** — every entry validates against the v0.2.0 Pydantic schema
4. **Critical-tier invariant** — every Critical-tier entry carries `authority.legal_identity`
5. **Canonicalization** — recomputed canonical bytes are byte-identical RFC 8785 output

Exit code is 0 if all checks pass, non-zero with a structured report otherwise.

---

## How it compares to Atlas and OVERT

Section §8.12 of the v1.4 paper provides a structured ten-criterion comparison with Intel Labs' Atlas (ML lifecycle provenance, TEE-backed, IEEE-published) and Glacis' OVERT (runtime verification evidence, structural-independence requirement, commercial deployments). The honest read of that comparison:

- **AI-GR wins** on: explicit regulatory regime mapping (17 regimes), explicit agentic-context schema
- **AI-GR ties** with at least one competitor on: lifecycle scope (qualified), license openness
- **AI-GR loses** to at least one competitor on: cryptographic trust root (Atlas has TEE-backed), independence model (OVERT has structural independence), implementation maturity (both have more), production deployment evidence (Atlas has measured prototype, OVERT has live customers), independent verification accessibility, peer-review status (Atlas is IEEE-published)

The three frameworks are more complementary than competitive. A plausible deployment uses **Atlas at the training-pipeline boundary** feeding into AI-GR's Build gate, **AI-GR for lifecycle governance and cross-regime evidence assembly**, and **OVERT at the runtime action boundary** feeding into AI-GR's Operate gate. Integration interfaces are targeted for v1.5 of the paper.

---

## Cite this work

If you use AI-GR or build on its concepts, please cite:

```
Singh, A. (2026). The Agentic Governance Ribbon: A Provenance-First Framework
for Governing Agentic AI Across Regulatory Regimes. Working paper v1.4.
https://doi.org/10.5281/zenodo.XXXXXXX
```

A `CITATION.cff` file is included in the repository for tools that prefer
the Citation File Format.

---

## Documentation

- [`CHANGELOG.md`](CHANGELOG.md) — version history with v0.1.0 → v0.2.0 migration notes
- [`STANDARDS.md`](STANDARDS.md) — capability requirements matrix (Table 7 of the paper)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — five-layer reference architecture (§6 of the paper)
- [`docs/schema_spec.md`](docs/schema_spec.md) — formal GPR specification
- [`docs/`](docs/) — mkdocs documentation site (run `mkdocs serve` from this directory)

---

## Contributing

AI-GR is an open framework offered to the practitioner and research community. Specific contributions sought ahead of v1.5 of the paper:

1. **Regime mapping co-review** — if you have regulatory law or sectoral compliance training and would be willing to independently review one of the regime modules, the author would value the second-rater contribution. Particularly valuable: practicing EU data protection officer for GDPR; MDR-experienced regulatory affairs professional for MDR/IVDR.
2. **Framework critique** — arguments that the Ribbon construct, the GPR schema, the cross-regime evidence-reuse claim, or the reference architecture is flawed or overreaching, especially with worked counterexamples.
3. **Pilot reports** — if you are evaluating or piloting AI-GR in a regulated environment, structured feedback (what worked, what didn't, what would have to change) is the most valuable form of contribution available.

Engagement from the Atlas and OVERT maintainer teams on the proposed integration path is welcome.

File issues, PRs, or comments via this repository or direct correspondence.

---

## License

This implementation is licensed Apache 2.0. The paper is separately licensed CC BY 4.0. The trademark *Agentic Governance Ribbon* is claimed by Anil Singh (USPTO application pending).
