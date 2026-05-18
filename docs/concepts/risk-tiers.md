# Risk Tiers

AI-GR uses three risk tiers: **Critical**, **High**, and **Managed**. Tier classification is operational, not legal — it determines the evidence burden a system carries through the Ribbon, not its regulatory status under any specific law.

## The tiers

### Critical

Systems whose failure or misuse carries serious consequences for safety, rights, or essential services. The full Ribbon applies, with:

- Mandatory co-approver(s) at Conceive and Build
- Full evidence at every gate (datasets, evaluations, red-team, model weights, SBOM)
- `legal_identity` mandatory on `Authority` (enforced at schema-validation time)
- Signed attestation required (no draft mode)

### High

Systems with material business or consumer-facing impact, not captured by Critical triggers. The full lifecycle gates apply with lighter-weight evidence. `legal_identity` is recommended but not mandatory.

### Managed

Internal productivity systems and low-stakes assistive AI. Self-service registration, lightweight checklist, automatic approval with guardrails. The full Ribbon still applies; the evidence burden is calibrated to the risk.

## Classification heuristic

### Critical triggers — any one is sufficient

1. EU AI Act Annex III high-risk classification
2. Handles HIPAA-regulated PHI
3. Regulated as SaMD by FDA or equivalent national regulator
4. Makes automated decisions with significant consumer effect (CCPA ADMT, NYC AEDT, Colorado SB 26-189, Connecticut SB 5)
5. Affects employment, credit, insurance, housing, or essential public services
6. Deployed in critical infrastructure (NERC CIP, EO 14028, equivalent sectoral baselines)
7. Processes TS/SCI or equivalent national-security classified data

### High triggers — any one is sufficient if no Critical trigger fires

8. Consumer-facing or substantially affects external customer experience
9. Makes material business decisions without point-of-decision human review
10. Subject to internal model risk management policy comparable to OCC/FRB/FDIC SR-11-7

### Managed

Systems satisfying none of the above.

## Conservatism

The classification is intentionally conservative. **Ambiguous cases default upward.** If a system might trigger #4 (consumer-effect ADMT) in some use contexts but not others, classify it Critical and document the scope under which it operates in Managed mode (if applicable) via a Deploy-gate entry.

## Reclassification

A system's tier is not fixed for its lifetime. If scope, data, or jurisdiction changes such that the trigger list now yields a different tier, the operator must:

1. Emit an **Evolve-gate GPR entry** attesting to the change that justifies the new classification
2. Begin emitting subsequent entries at the new tier
3. The chain itself documents when and why the reclassification occurred

## Role-relative classification

The Critical triggers cross the provider/deployer boundary defined by the EU AI Act. AI-GR v0.1+ treats classification as **role-relative**:

- **Trigger #1** (EU AI Act high-risk) is fundamentally provider-side — the provider classifies the system at design time, and the classification persists for the system's market lifetime.
- **Trigger #4** (consequential automated decision-making) is more often deployer-side — the same system may be non-high-risk in the abstract but produce consequential automated decisions in a specific deployer's use context.

Providers and deployers classify independently against the same trigger list. The two classifications may differ. A provider classifying their system Managed and a deployer classifying their use of that system Critical are both valid outcomes — they produce parallel GPR chains with different evidence obligations. This mirrors the EU AI Act's own treatment, where provider obligations under Articles 16-22 and deployer obligations under Article 26 apply independently.
