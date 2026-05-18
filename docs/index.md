# AI-GR — The Agentic Governance Ribbon

A provenance-first governance framework for agentic AI.

> *Working paper v1.4 · Reference implementation v0.2.0 · May 2026*

## What AI-GR is

The Agentic Governance Ribbon (AI-GR) is a vendor-neutral framework for governing agentic AI systems. It organises governance as a 5×3 matrix — five lifecycle gates (Conceive, Build, Deploy, Operate, Evolve) crossed with three risk tiers (Critical, High, Managed). Each cell of the matrix emits a **Governance Provenance Record** (GPR): a content-addressable, cryptographically attested, append-only entry that captures the decision, the evidence, the approving authority, and the applicable regulatory regimes.

GPR entries chain together through linkage pointers, producing a tamper-evident provenance sequence in which **the chain itself — not any individual document — is the audit artifact**.

## What problem it solves

The major AI governance frameworks active in 2026 (NIST AI RMF 1.0, ISO/IEC 42001:2023, the EU AI Act, HIPAA, FDA SaMD guidance, SEC cyber disclosure) were designed for predictive and generative AI systems. They govern what models *say*. They have comparatively little to say about what agentic systems *do*: the autonomous actions, tool calls, and runtime-evolving behaviour that distinguish agents from prior generations of AI.

AI-GR fills that structural gap with three constructs: **The Ribbon** (lifecycle gates × risk tiers), **The GPR** (the chained evidence artifact), and **the regime map** (a single GPR entry can simultaneously satisfy seventeen regulatory regimes).

## How AI-GR positions against Atlas and OVERT

[Section §8.12 of the v1.4 paper](comparison.md) provides a structured ten-criterion comparison with Intel Labs' Atlas (ML lifecycle provenance) and Glacis' OVERT (runtime verification evidence). The honest read:

- **AI-GR's contribution is narrower than the framework's ambition suggests.** It is not the most cryptographically rigorous (Atlas, with TEE-backed attestation, is stronger). It is not the most independence-rigorous (OVERT, with structural third-party attestation, is stronger). It is not the most mature in implementation (both Atlas and OVERT are further ahead).
- **AI-GR's actual contribution** is (a) an explicit, lifecycle-spanning evidence-reuse schema for cross-regime regulatory mapping, and (b) a structured agentic-context field for systems that take autonomous actions.
- **The three frameworks are more complementary than competitive.** A plausible deployment uses Atlas at the training-pipeline boundary, AI-GR for lifecycle governance and cross-regime evidence assembly, and OVERT at the runtime action boundary.

## Where to start

- New to AI-GR? Start with [Getting Started](getting-started.md).
- Want to understand the framework conceptually? See [The Ribbon](concepts/ribbon.md) and [Governance Provenance Record](concepts/gpr.md).
- Building or extending the implementation? See [Schema Specification](schema_spec.md) and [Architecture](architecture.md).
- Validating compliance? See [Regulatory Mapping](regimes/overview.md) and [Verification](verification.md).
- Integrating with surrounding tools? See [Adapters](adapters/sigstore.md).

## Citation

If you use AI-GR or build on its concepts, please cite:

```
Singh, A. (2026). The Agentic Governance Ribbon: A Provenance-First Framework
for Governing Agentic AI Across Regulatory Regimes. Working paper v1.4.
https://doi.org/10.5281/zenodo.XXXXXXX
```
