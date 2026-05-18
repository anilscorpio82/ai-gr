# Regulatory Mapping — Overview

AI-GR v0.2.0 ships regime modules for **sixteen regulatory regimes**. The framework treats regime as a property of evidence (the GPR `regime` array), not of system, so a single entry can carry multiple regime claims simultaneously.

## Why regime is a property of evidence

A system is not statically a "HIPAA system" or an "EU AI Act system." Rather, particular evidence the system produces is relevant to one or both. The same Build-gate evidence block (datasets, evaluations, model weight hash, SBOM, red-team results) can be claimed against:

- EU AI Act Annex IV §2 (elements and development process)
- HIPAA §164.312(c) (integrity)
- NIST AI RMF Measure-2.3
- GDPR Article 35 (DPIA)
- MDR Article 61 (clinical evaluation)
- NIS2 Article 21(2)(d) (supply chain security)

…simultaneously, with no duplication of evidence. This is the central practical claim of AI-GR.

## Important qualification

Some regulatory determinations are inherently system-level rather than evidence-level. The EU AI Act's Article 6 high-risk classification is the clearest example: a system **is or is not** Annex III high-risk by virtue of its purpose, and that classification triggers Annex IV documentation obligations that apply across the system's full lifetime on the market.

AI-GR's evidence-level regime attachment is **additive over** such system-level determinations, not a replacement for them. A Critical-tier AI-GR system corresponding to an EU AI Act high-risk classification must produce Annex IV documentation for the system as a whole; the per-entry regime claims attest to which specific obligations each piece of evidence satisfies.

## Sixteen regimes — gate coverage summary

| Regime | Ribbon gates | Source |
|---|---|---|
| EU AI Act (high-risk; provider) | Conceive · Build · Operate | EU 2024/1689 |
| EU AI Act Art. 26 (deployers) | Deploy · Operate · Evolve | EU 2024/1689 |
| GDPR | Conceive · Build · Operate | EU 2016/679 |
| NIS2 Directive | Build · Operate | EU 2022/2555 |
| MDR/IVDR | Build · Deploy · Evolve | EU 2017/745, 2017/746 |
| DORA | Build · Operate | EU 2022/2554 |
| DSA | Conceive · Operate | EU 2022/2065 |
| Data Act | Build · Operate | EU 2023/2854 |
| Cyber Resilience Act | Build · Deploy · Operate | EU CRA |
| EHDS | Conceive · Build · Operate | EU EHDS |
| NIST AI RMF + GenAI Profile | Build · Operate | NIST AI 100-1 + 600-1 |
| ISO/IEC 42001 | All gates | ISO 42001:2023 |
| HIPAA + HITECH | Build · Deploy · Operate | 45 CFR Part 164 |
| FDA SaMD + PCCP | Build · Evolve | FDA guidance |
| SEC cyber + AI disclosure | Operate · Evolve | SEC Release 33-11216 + AI guidance |
| State ADMT/AEDT laws | Conceive · Operate | California, NYC, Colorado |

## Single-rater caveat

The mappings in v0.2.0 were derived through structured close reading of each regime's primary source text by one author. The author acknowledges that different readers, particularly those with regulatory law training, may map differently. **Future versions will publish inter-rater agreement scores; v0.2.0 should be read as an initial proposal inviting refinement.**

If you have regulatory law or sectoral compliance training and would be willing to independently review one of the regime modules, the author would value the second-rater contribution. See the [GitHub repository](https://github.com/anilscorpio82/ai-gr) to engage.

## Detailed per-regime documentation

Two regimes are detailed on dedicated pages:

- [EU AI Act](eu-ai-act.md) — provider Annex IV obligations and Article 26 deployer obligations
- [GDPR](gdpr.md) — including Article 17 right-to-erasure patterns

The remaining 14 regimes are documented inline in their respective Python modules under `src/ai_gr/regimes/`. Each module's docstring states the source regulation, the article-level references, and the gate mapping rationale.
