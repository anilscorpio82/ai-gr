"""
ai_gr.adapters.sigstore — Sigstore Cosign + Rekor integration reference pattern.

**This is a reference pattern, not a production-grade integration.** It
demonstrates how an AI-GR deployment would consume Sigstore-signed model
artifact attestations as evidence in a Build-gate GPR entry, and how it
would emit a hash-only Rekor transparency log entry for an AI-GR entry.

What this module does:
  - Defines a wire-shape for a Sigstore-style attestation reference, suitable
    for placing in ``evidence.additional["sigstore_attestation"]``.
  - Provides a helper to construct an ``evidence.model_weights`` hash
    reference from a cosign-signed artifact bundle.
  - Provides a helper to format an AI-GR GPR entry's content_hash for
    submission to a Rekor instance.

What this module does NOT do:
  - It does not make actual HTTP requests to Rekor. The
    ``submit_to_rekor()`` function returns the request body that would be
    submitted; the caller is responsible for the actual HTTP call, retries,
    and response handling.
  - It does not verify a Sigstore bundle against a Sigstore trust root. Use
    the ``sigstore`` Python library for verification proper.
  - It does not handle Fulcio short-lived certificate workflows.

For production deployments, use the official Sigstore SDKs:
  https://github.com/sigstore/sigstore-python
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SigstoreAttestation:
    """A reference to a Sigstore-signed model artifact attestation.

    Suitable for placement in ``evidence.additional["sigstore_attestation"]``
    of a Build-gate GPR entry.
    """

    artifact_uri: str
    """URI of the signed artifact (e.g. an OCI reference)."""

    artifact_sha256: str
    """SHA-256 hash of the artifact bundle."""

    bundle_uri: str | None = None
    """URI of the cosign bundle (.bundle file with signature, certificate, and Rekor entry)."""

    rekor_log_index: int | None = None
    """Optional Rekor transparency log index for this attestation."""

    certificate_subject: str | None = None
    """Subject of the Fulcio short-lived certificate (e.g., an OIDC identity)."""

    in_toto_predicate_type: str | None = None
    """If the attestation is an in-toto v1.0 statement, its predicate type."""

    extra: dict[str, Any] = field(default_factory=dict)
    """Additional fields specific to the deployment's Sigstore configuration."""

    def to_evidence_dict(self) -> dict[str, Any]:
        """Render as a dict suitable for evidence.additional storage."""
        result = {
            "artifact_uri": self.artifact_uri,
            "artifact_sha256": self.artifact_sha256,
        }
        if self.bundle_uri:
            result["bundle_uri"] = self.bundle_uri
        if self.rekor_log_index is not None:
            result["rekor_log_index"] = self.rekor_log_index
        if self.certificate_subject:
            result["certificate_subject"] = self.certificate_subject
        if self.in_toto_predicate_type:
            result["in_toto_predicate_type"] = self.in_toto_predicate_type
        if self.extra:
            result["extra"] = dict(self.extra)
        return result


def submit_to_rekor(content_hash: str, public_rekor_url: str = "https://rekor.sigstore.dev") -> dict[str, Any]:
    """Return the request body that would submit an AI-GR entry's hash to Rekor.

    This is a reference pattern. The actual HTTP call is left to the caller
    so that production deployments can handle authentication, retries,
    error reporting, and rate-limiting on their own terms.

    Args:
        content_hash: The SHA-256 hex digest of the GPR entry's canonical bytes.
        public_rekor_url: The Rekor instance URL (default: public Sigstore Rekor).

    Returns:
        A dict with two keys:
          - ``request_url``: the POST endpoint for entry submission
          - ``request_body``: a hashedrekord v0.0.1 request body shape suitable
            for POSTing as JSON

    The caller is responsible for:
      - Performing the HTTP POST with retries and timeouts
      - Recording the returned Rekor log index in
        ``evidence.additional["sigstore_attestation"]["rekor_log_index"]``
      - Handling rate limiting and failures
    """
    return {
        "request_url": f"{public_rekor_url.rstrip('/')}/api/v1/log/entries",
        "request_body": {
            "kind": "hashedrekord",
            "apiVersion": "0.0.1",
            "spec": {
                "data": {
                    "hash": {
                        "algorithm": "sha256",
                        "value": content_hash,
                    },
                },
                "signature": {
                    "format": "x509",
                    # Production callers fill these in. They are intentionally
                    # left as placeholders here so the wire shape is visible
                    # without committing to a specific signing identity model.
                    "content": "<base64-encoded-signature>",
                    "publicKey": {
                        "content": "<base64-encoded-x509-certificate-or-public-key>",
                    },
                },
            },
        },
    }
