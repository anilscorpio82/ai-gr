# Sigstore Adapter

`ai_gr.adapters.sigstore` — Sigstore Cosign + Rekor integration reference pattern.

!!! warning "Reference pattern, not production"
    This adapter is a **reference pattern**. It demonstrates how an AI-GR deployment would consume Sigstore-signed model artifact attestations as evidence in a Build-gate GPR entry, and how it would emit a hash-only Rekor transparency log entry for an AI-GR entry. Production deployments must add error handling, retries, real endpoint configuration, and credential management.

## What this adapter provides

- **`SigstoreAttestation`** dataclass — a typed reference to a Sigstore-signed model artifact attestation, suitable for placement in `evidence.additional["sigstore_attestation"]` of a Build-gate GPR entry.
- **`submit_to_rekor(content_hash)`** — returns the request body that would submit an AI-GR entry's hash to Rekor. The caller is responsible for the actual HTTP call.

## Wire shape: SigstoreAttestation

```python
from ai_gr.adapters.sigstore import SigstoreAttestation

attestation = SigstoreAttestation(
    artifact_uri="oci://registry.example/cds-agent@sha256:abc...",
    artifact_sha256="abc..." * 8,
    bundle_uri="oci://registry.example/cds-agent.bundle",
    rekor_log_index=12345678,
    certificate_subject="caio@acme-health.example",
    in_toto_predicate_type="https://slsa.dev/provenance/v1",
)

# Place in evidence.additional
evidence = Evidence(
    model_weights="abc..." * 8,
    additional={
        "sigstore_attestation": attestation.to_evidence_dict(),
    },
)
```

## Wire shape: Rekor submission

```python
from ai_gr.adapters.sigstore import submit_to_rekor

# Build a GPR entry, sign it, then get the Rekor submission body
entry = build_my_gpr_entry()
rekor_payload = submit_to_rekor(entry.content_hash())

# rekor_payload['request_url'] == "https://rekor.sigstore.dev/api/v1/log/entries"
# rekor_payload['request_body'] is a hashedrekord v0.0.1 shape

# Caller makes the HTTP call:
import requests
response = requests.post(rekor_payload["request_url"], json=rekor_payload["request_body"])
log_index = response.json()["..."]["logIndex"]

# Record the Rekor log index back into the attestation:
attestation_with_rekor = SigstoreAttestation(
    ...,
    rekor_log_index=log_index,
)
```

## What this adapter does not do

- It does **not** make actual HTTP requests to Rekor.
- It does **not** verify a Sigstore bundle against a Sigstore trust root. Use the [`sigstore` Python library](https://github.com/sigstore/sigstore-python) for verification proper.
- It does **not** handle Fulcio short-lived certificate workflows.

## Installing

```bash
pip install -e ".[adapters]"
```

Optional `requests` dependency is needed for production use to make the actual HTTP call to Rekor.
