# GDPR

Regulation (EU) 2016/679. The General Data Protection Regulation applies in parallel with the EU AI Act for any AI deployment processing personal data of EU data subjects. The EU AI Act explicitly defers to GDPR for personal data processing (Recital 9, Article 2(7)).

**Every Critical-tier deployment in EU jurisdictions will be simultaneously subject to GDPR.** A framework that does not address GDPR interaction is not deployable in the EU.

## DPIA evidence and the Conceive gate

GDPR Article 35 requires a Data Protection Impact Assessment before processing likely to result in high risk. AI-GR's Conceive gate is the natural locus for DPIA evidence:

- The Conceive-gate entry should carry a reference to the DPIA document in `evidence.additional`
- The DPIA's risk-treatment decisions should be reflected in `decision.conditions`
- For deployers, EU AI Act Article 26(9) explicitly links deployer DPIA obligations to information provided by the AI provider under Article 13 — both should be cross-referenced in the same Conceive-gate entry

The GPR chain provides a verifiable record of when the DPIA was conducted, by whom, and against which version of the system — addressing GDPR Article 5(2) accountability without replacing the DPIA itself.

## Lawful basis attestation

GDPR Article 6 requires identification of a lawful basis for each processing operation. For systems processing personal data under EU jurisdiction, the Conceive-gate GPR entry should carry an explicit `lawful_basis` attestation within `evidence.additional`, naming one of the Article 6(1) bases.

For processing of **special-category data** under Article 9 (health data, biometric data, race, political opinion, etc.), an additional Article 9(2) basis must be attested.

```python
evidence=Evidence(
    additional={
        "lawful_basis": "Art-6(1)(c)+Art-9(2)(h)",
        # Art-6(1)(c) = legal obligation; Art-9(2)(h) = preventive/occupational medicine
        "dpia": "dpia-system-v3.1.0.pdf",
    },
)
```

## The Article 17 right-to-erasure tension

GDPR Article 17 establishes a data subject's right to erasure in specified circumstances. Append-only cryptographic chains and right-to-erasure are in **structural tension**: any deletion of personal data within an entry invalidates that entry's hash, and therefore breaks the chain's verifiability.

This is not a novel problem; the European Data Protection Board's [Guidelines 02/2025](https://www.edpb.europa.eu/) on blockchain technologies and personal data addresses it explicitly. AI-GR v0.2.0 inherits the relevant patterns:

### Pattern 1: Off-chain personal data

**Personal data should never be embedded directly in GPR entries.** The `evidence` field carries:
- **References** to external artifacts (datasets, evaluation reports, DPIAs)
- **Hashes** of those artifacts

The artifacts themselves live in conventional, modifiable storage. When an Article 17 request is honoured:

1. The underlying dataset is modified or deleted in its native storage
2. The GPR entry's hash continues to reference the prior dataset state
3. No personal data within the GPR chain itself requires modification

### Pattern 2: Crypto-shredding of references

Where a GPR entry references a dataset by hash and the dataset is subsequently erased under Article 17:

- The entry remains cryptographically valid as a **record-of-fact** ("at the time of decision, dataset X with hash H existed and was relied upon")
- The dataset itself is no longer recoverable
- This is compatible with Article 17 where the legitimate-interest balancing under **Article 17(3)(e)** supports retention for establishing, exercising, or defending legal claims

### What AI-GR explicitly does not solve

If an authority's **name** in the `legal_identity` field is itself personal data subject to erasure (i.e., an individual rather than a corporate identity), the framework does not currently provide a clean mechanism for handling Article 17 requests over that name.

**v0.2.0 deployments should use corporate or role-based identities** rather than personal names in `legal_identity` where possible. v0.3 of the framework is targeted to address this through structured pseudonymisation.

## Controller and processor identification

GDPR distinguishes:
- **Controllers** — determine purposes and means of processing
- **Processors** — process on behalf of controllers under Article 28
- **Joint controllers** — jointly determine purposes and means under Article 26
- **Sub-processors** — engaged by processors

In AI-GR's authority model, the `legal_identity` sub-field carries the legally responsible person. For GDPR-relevant deployments, the schema requires this person's GDPR role to be named within `legal_identity`:

```python
LegalIdentity(
    name="ACME Health Systems Inc.",
    registration_id="LEI:5493001K3F3DUM2KRD89",
    jurisdiction="DE",
    address="...",
    contact_email="dpo@acme-health.example",
    gdpr_role=GdprRole.CONTROLLER,
)
```

Joint controllership arrangements under Article 26 should be reflected in:
- `gdpr_role=GdprRole.JOINT_CONTROLLER` on the legal_identity, AND
- A `joint_controller_arrangement` reference within `evidence.additional`

## Cross-border transfers

GDPR Chapter V governs transfers of personal data to third countries. AI-GR's GPR chain is itself a record of processing and may contain personal data references; **where the chain or its referenced artifacts are stored outside the EU/EEA, Chapter V transfer mechanisms apply** (adequacy decisions, standard contractual clauses, binding corporate rules).

v0.2.0 of the framework does not prescribe storage location, but deployments crossing jurisdictional boundaries should attest to the Chapter V mechanism in use within the relevant GPR entries:

```python
evidence=Evidence(
    additional={
        "chapter_v_mechanism": "SCC-2021-modules-1-and-2",
        # Or: "adequacy-decision:UK", "BCR-controller-XYZ", etc.
    },
)
```
