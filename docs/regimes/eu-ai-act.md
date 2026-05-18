# EU AI Act

Regulation (EU) 2024/1689. Entered into force August 1, 2024. Full applicability August 2, 2026 (subject to potential extension for some Annex III high-risk systems per the November 2025 "AI Omnibus" amendments).

AI-GR maps the EU AI Act in two parallel regime modules:

- **`EU-AI-Act`** — provider obligations (Articles 9-17, Article 47, Annex IV)
- **`EU-AI-Act-Deployer`** — deployer obligations (Articles 26-27)

## Why two regimes?

The EU AI Act imposes substantially different obligations on **providers** (those who place AI systems on the market) and **deployers** (those who use them). Most enterprise AI adopters are deployers — they use third-party-developed systems — and Article 26 applies to them **independently of the provider's own conformity activities**.

A single deployment may need to make claims under both regimes if the deploying organisation is also the provider (built in-house). The regime field is multi-valued, so this is mechanically straightforward.

## Provider regime: GPR field mapping

The framework's role with respect to Annex IV technical documentation is **supplementary**, not substitutive. AI-GR does not produce the Annex IV file itself — the file's substantive content is prescribed by the Act and authored by the provider. What AI-GR produces is **verifiable provenance over the artifacts that constitute the Annex IV file**.

| Annex IV section | Substantive artifact (provider produces) | GPR provenance field | Gate |
|---|---|---|---|
| 1. General description & intended purpose | System description document | `subject`; `agentic_context.runtime_context` | Conceive |
| 2. Elements & development process | Methods, datasets, datasheets, pre-trained model attestation | `evidence.datasets`; `evidence.modelWeights`; `evidence.sbom` | Build |
| 3. Monitoring, validation, testing | Validation procedures, performance metrics | `evidence.evaluations`; `evidence.redTeam` | Build |
| 4. Information for deployers | Instructions for use; human oversight measures | `agentic_context.tool_registry`; `agentic_context.action_authority` | Deploy |
| 5. Risk management (Art. 9) | Risk register; mitigation traceability | `evidence.evaluations`; `decision.conditions` | Conceive·Build |
| 6. Lifecycle change management | Versioning & traceability documentation | `linkage.prevGPR` (chain); Evolve-gate entries | Evolve |
| 7. Harmonised standards applied | Conformance reports for harmonised standards | `evidence.evaluations` | Build |
| 8. EU Declaration of Conformity (Art. 47) | Signed DoC document | Deploy-gate GPR entry with `regime="EU-AI-Act:DoC"` | Deploy |
| 9. Post-market monitoring plan (Art. 72) | PMS plan; serious incident reporting procedures | Operate-gate runtime attestations | Operate |

## Deployer regime: GPR field mapping

| Article 26 obligation | GPR mechanism | Gate |
|---|---|---|
| Art. 26(1)+(3): use system per provider instructions | Operate-gate entries attest to instruction-conforming use | Operate |
| Art. 26(2): human oversight by competent natural persons | `agentic_context.human_oversight`; `authority.legal_identity` | Deploy·Operate |
| Art. 26(4): input-data governance (where deployer-controlled) | Operate-gate entries with `evidence.datasets` | Operate |
| Art. 26(5): monitor operation; inform provider; suspend if risk; report incidents | Operate-gate rollback entries; serious-incident attestations within 15 days | Operate |
| Art. 26(6): retain auto-generated logs ≥6 months | Operate-gate runtime attestation chain; chain integrity demonstration | Operate |
| Art. 26(7): notify workers before workplace deployment | Deploy-gate entry attests to worker notification | Deploy |
| Art. 26(8): EU database registration (public sector + EU institutions) | Deploy-gate entry with `regime="EU-AI-Act-Deployer:Art-49-registration"` | Deploy |
| Art. 26(9): use Art. 13 info for GDPR Art. 35 DPIA | Conceive-gate entry references provider Art. 13 packet + deployer DPIA | Conceive |
| Art. 27: Fundamental Rights Impact Assessment | Conceive-gate entry with FRIA reference | Conceive |

## Notified body workflow

For Annex III high-risk systems requiring conformity assessment by a notified body under Article 43, AI-GR's role is narrow but real: the notified body can verify that the technical file presented to it is **the same file** that was produced at the relevant Ribbon gates, by checking the chain's cryptographic linkage and the timestamps.

This does not replace any element of the notified body's substantive review — the Annex VII procedures remain operative — but it provides verifiable evidence that the file has not been altered between issuance and presentation. For the Article 18 ten-year retention obligation, the GPR chain provides an integrity-preserving record across organisational change, signing-key rotation, and storage migration, **provided that signing-key rotation events are themselves captured in the chain** as Evolve-gate entries.

## Legal identity binding

The EU AI Act requires conformity assessments and the Article 47 Declaration of Conformity to be signed by identifiable legal persons — the provider (Article 16), an authorised representative (Article 22), or a notified body (Article 43). A DID-based identifier satisfies cryptographic authentication but does **not** identify the legal person bound by the Act's obligations.

AI-GR v0.2.0+ addresses this with the `LegalIdentity` sub-field on `Authority`, mandatory for Critical-tier entries. See [Concepts → GPR](../concepts/gpr.md) for the design rationale.
