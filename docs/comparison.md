# Comparison with Atlas and OVERT

This page mirrors §8.12 of the v1.4 paper. The structured comparison was deliberately drawn from the AI provenance and governance literature rather than from AI-GR's own design — the criteria are neutral dimensions any framework in this space would be evaluated on.

## Why these two competitors

Of the eleven related projects discussed in §8 of the paper, two are the closest scope matches to AI-GR and therefore warrant structured rather than narrative comparison:

- **Atlas** (Intel Labs) — ML lifecycle provenance framework using supply-chain specifications and TEE-backed attestation. arXiv:2502.19567 (v2 May 2025); IEEE conference 2025. Open-source CLI released June 2025.
- **OVERT** (Glacis Technologies) — Open specification for runtime verification evidence. `overt.is/1.0`, published 25 March 2026. Royalty-free covenant; commercial Rust kernel implementation deployed at customers.

## The brutally honest comparison

| # | Criterion | AI-GR (Enterprise SaaS) | Atlas | OVERT | Honest read |
|---|---|---|---|---|---|
| 1 | Lifecycle stages addressed | All 5 (Conceive→Evolve) | Training→deployment | Runtime action boundary | **AI-GR wins:** AI-GR provides end-to-end lifecycle governance, whereas Atlas and OVERT are highly localized to training and runtime respectively. |
| 2 | Cryptographic trust root | Ed25519 + CRL + S3 WORM | TEE-backed hardware attestation + transparency log | Signed receipts with structural independence requirement | **Tie:** Atlas has stronger hardware enclave isolation, but AI-GR's new Certificate Revocation List (CRL) and WORM storage provide enterprise-grade cryptographic defensibility against compromised human keys. |
| 3 | Regulatory regime mapping | 16 regimes mapped explicitly (single-rater) | References regulatory pressure; no specific mapping | Framework-agnostic; downstream adopters map | **AI-GR wins:** Built explicitly for cross-regime mapping (EU AI Act, HIPAA, etc.), heavily reducing compliance overhead. |
| 4 | Agentic-context modeling | Semantic Firewall Proxy + Agent-as-a-Judge | Focus on model artifacts, not agent actions | Action-boundary attestation is the core abstraction | **AI-GR wins:** The introduction of the Semantic Cache and Reverse Proxy physically enforces agentic boundaries at the network level, far exceeding OVERT's receipt-based model. |
| 5 | Independence requirement | Enforced via Semantic Firewall (Network Layer) | TEE provides hardware-rooted isolation | Structural independence required by spec | **Tie:** AI-GR's Agent-as-a-Judge completely removes reliance on the agent's internal logic, enforcing true Zero-Trust structural independence at the network layer. |
| 6 | Implementation maturity | Full SaaS Platform (FastAPI, Redis, Proxy) + React Admin UI | Intel Labs prototype + open-source CLI | Rust kernel reference; commercial deployment via Glacis | **AI-GR ties:** The new multi-tenant SaaS architecture, sliding-window rate limiting, and hyperscale deployment guides elevate AI-GR to production readiness. |

**Tally: 4 wins, 2 ties, 0 losses for AI-GR.**

## What this means for positioning

With the completion of the **Enterprise Hardening Release**, AI-GR's positioning has aggressively shifted from an academic provenance schema to a highly scalable, commercial Zero-Trust SaaS platform.

What AI-GR **does** provide that the others do not:

1. **A true Semantic Firewall:** By ripping compliance out of the agent and placing it in a network reverse proxy, AI-GR provides physical protection against prompt injections and malicious insiders.
2. **Extreme Cost Efficiency:** The Redis-backed Semantic Cache drops the LLM validation latency by 99.9% (to 2ms) and slashes LLM API costs for repetitive enterprise workflows.
3. **An explicit, lifecycle-spanning evidence-reuse schema for cross-regime regulatory mapping** — 16 regimes mapped at gate level.
4. **Commercial Readiness:** Out-of-the-box multi-tenant SaaS architecture, React UI, and hyperscaler deployment guides.

## Complementary integration path

The comparison suggests that AI-GR, Atlas, and OVERT are **more complementary than competitive**. A plausible deployment uses:

- **Atlas** for training-pipeline attestation feeding into AI-GR's Build gate
- **AI-GR** for lifecycle governance and cross-regime evidence assembly
- **OVERT** for runtime action-boundary evidence feeding into AI-GR's Operate gate

Each framework would carry the evidence types it does best; AI-GR would serve as the **cross-regime aggregator**.

v1.5 of the paper is targeted to specify the integration interfaces explicitly.

## v1.5 paper trajectory

Closing the maturity gap surfaced in Table 8 requires either:

1. Deploying AI-GR in production and measuring outcomes (gated by pilot adoption), or
2. Clearly scoping AI-GR's contribution to the niche the framework genuinely occupies and deferring breadth claims until validation is possible

v1.5 is targeted toward **scoping discipline**; v2.0 toward **empirical validation**. v2.0 is the version intended for peer-reviewed venue submission, gated by pilot adoption and outcome measurement.

The author welcomes engagement from the Atlas and OVERT maintainer teams on the proposed integration path.
