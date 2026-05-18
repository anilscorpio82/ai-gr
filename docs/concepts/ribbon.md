# The Ribbon

The **Ribbon** is AI-GR's organising metaphor. It is a 5×3 matrix:

- **Five lifecycle gates** running horizontally: Conceive, Build, Deploy, Operate, Evolve.
- **Three risk tiers** running vertically: Critical, High, Managed.

Each cell of the matrix is a class of governance event. When such an event occurs, the framework requires that a Governance Provenance Record (GPR) entry be emitted.

```
                        Conceive  Build   Deploy  Operate Evolve
                       ┌────────┬────────┬────────┬────────┬────────┐
        Critical       │  GPR   │  GPR   │  GPR   │  GPR   │  GPR   │
                       ├────────┼────────┼────────┼────────┼────────┤
        High           │  GPR   │  GPR   │  GPR   │  GPR   │  GPR   │
                       ├────────┼────────┼────────┼────────┼────────┤
        Managed        │  GPR   │  GPR   │  GPR   │  GPR   │  GPR   │
                       └────────┴────────┴────────┴────────┴────────┘
                                                                        ↑ Ribbon
                                                                          flows
                                                                          forward
                                                                          in time
```

## The five gates

| Gate | Question answered | Typical outputs |
|---|---|---|
| **Conceive** | Should we build this? | Use-case approval, risk classification, impact assessment, DPIA, FRIA |
| **Build** | Is it safe to release? | Evaluation results, bias/red-team reports, dataset and model-weight hashes, SBOM, action-authority specification |
| **Deploy** | Are deployment conditions met? | Conformity attestations, BAA scope, access-scope definition, rollback plans, Declaration of Conformity |
| **Operate** | Is the system behaving in production? | Drift telemetry, incident logs, usage attribution, regulator-ready audit traces, runtime action attestations |
| **Evolve** | Has the system changed? | Change-control records, retrain attestations, PCCP invocations, decommissioning evidence |

## The three tiers

| Tier | Triggers | Evidence burden |
|---|---|---|
| **Critical** | EU AI Act Annex III high-risk, HIPAA PHI, FDA SaMD, ADMT consequential decisions, critical infrastructure | Full Ribbon with required co-approvers, full evidence at every gate, `legal_identity` mandatory |
| **High** | Material business or consumer-facing impact, not captured by Critical triggers | Full lifecycle gates but lighter-weight evidence |
| **Managed** | Internal productivity, low-stakes assistive AI | Self-service registration, lightweight checklist, automatic approval with guardrails |

A vocabulary note for European readers: AI-GR's three tiers are not the EU AI Act's four risk levels (Unacceptable, High, Limited, Minimal). The mapping is approximate but not exact, and AI-GR's classification is operational rather than legal. See §3.2 of the paper for details.

## What "Ribbon" means

The metaphor is intentional and load-bearing. A ribbon is **continuous** — it does not have gaps. The audit artifact AI-GR produces is the continuous sequence of GPR entries produced across the lifecycle, with each entry referencing its predecessor via a cryptographic hash.

A ribbon is also **flexible**. It bends through the lifecycle, accommodating prospective gates (Conceive, Build, Deploy) that set policy before action and retrospective gates (Operate, Evolve) that document what occurred. Both kinds of governance live on the same ribbon, in the same shape, with the same evidence schema.

## Asymmetry: prospective vs. retrospective governance

The five gates are not symmetric in kind. Conceive, Build, and Deploy perform *prospective* governance — they set policy and approve action before action occurs. Operate and Evolve perform *retrospective* governance — they document what occurred. AI-GR v0.1 treats both with the same evidence schema for uniformity; a future version may introduce structural differences.

## Classification heuristic

For deciding which tier a system falls into, AI-GR proposes a list of triggers. Any one of the **Critical triggers** is sufficient to classify a system Critical:

1. EU AI Act Annex III high-risk classification
2. Handles HIPAA-regulated PHI
3. Regulated as SaMD by FDA or equivalent national regulator
4. Makes automated decisions with significant consumer effect (CCPA ADMT, NYC AEDT, Colorado SB 26-189)
5. Affects employment, credit, insurance, housing, or essential public services
6. Deployed in critical infrastructure
7. Processes TS/SCI or equivalent classified data

Any one of the **High triggers** if no Critical trigger fires:

8. Consumer-facing or substantially affects external customer experience
9. Makes material business decisions without point-of-decision human review
10. Subject to internal model risk management policy comparable to OCC/FRB/FDIC SR-11-7

Systems satisfying none of the above are classified **Managed**. Classification is intentionally conservative: ambiguous cases default upward. Re-classification requires an Evolve-gate GPR entry attesting to the change that justifies it.

## Provider vs. deployer

Several Critical triggers cross the provider/deployer boundary defined by the EU AI Act. AI-GR v0.1 treats classification as **role-relative**: both providers and deployers classify independently against the same trigger list, and the two classifications may differ if the role-relevant facts differ. A provider classifying their system Managed and a deployer classifying their use of that system Critical are both valid outcomes, and produce parallel GPR chains with different evidence obligations.
