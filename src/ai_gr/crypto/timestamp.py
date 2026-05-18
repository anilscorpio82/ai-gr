"""
ai_gr.crypto.timestamp — RFC 3161 trusted timestamp attachment.

A signature proves who signed; a timestamp proves *when*. For long-term audit
(SEC post-incident review, EU AI Act technical documentation retention, HIPAA
six-year audit retention), having a third-party-attested timestamp is what
prevents back-dating attacks.

RFC 3161 Time-Stamp Protocol (TSP) is the standard. A real implementation
would POST a TimeStampReq to a TSA endpoint (DigiCert, Sectigo, FreeTSA) and
attach the returned TimeStampResp. For the reference implementation we provide
the integration shape so users can wire in a TSA of their choosing without
modifying the schema.

For v0.1 this is a stub that records the intent and metadata; v0.2 will ship
with a working FreeTSA client (their service is free and well-suited for
reference implementations).
"""

from __future__ import annotations

from ai_gr.schema import Attestation, GPREntry


class TSAUnavailableError(RuntimeError):
    """Raised when the TSA is not reachable or returns an error."""


def attach_rfc3161(
    entry: GPREntry,
    *,
    tsa_url: str | None = None,
    tsa_identifier: str = "rfc3161:stub",
) -> GPREntry:
    """Attach an RFC 3161 timestamp token to an already-signed GPR entry.

    Args:
        entry: A signed GPR entry.
        tsa_url: TSA endpoint URL. If None, generates a stub token (testing only).
        tsa_identifier: Human-readable identifier for the TSA used.

    Returns:
        A new GPR entry with ``attestation.rfc3161_token`` populated.

    Raises:
        TSAUnavailable: If the live TSA call fails.
        ValueError: If the entry has no signature to timestamp.
    """
    if entry.attestation.signature is None:
        raise ValueError(
            "Cannot timestamp an unsigned entry. Call sign_entry() first."
        )

    if tsa_url is None:
        # Stub mode — emit a deterministic placeholder so that the
        # attestation shape is testable without a network call.
        # NOTE: This is NOT a real RFC 3161 token; do not use in production.
        token = f"stub:{entry.content_hash()[:16]}"
    else:
        # Live mode would issue:
        #   1. Build a TimeStampReq containing SHA-256(signature bytes).
        #   2. POST to tsa_url with Content-Type: application/timestamp-query.
        #   3. Parse the response and base64-encode the token.
        #
        # See RFC 3161 §2.4. We intentionally do not ship a network call in
        # v0.1 to keep the reference implementation hermetic.
        raise NotImplementedError(
            "Live RFC 3161 TSA integration arrives in v0.2. "
            "Pass tsa_url=None for stub mode."
        )

    new_attestation = Attestation(
        signature=entry.attestation.signature,
        signature_alg=entry.attestation.signature_alg,
        public_key=entry.attestation.public_key,
        timestamp=entry.attestation.timestamp,
        rfc3161_token=token,
        tsa=tsa_identifier,
    )
    return entry.model_copy(update={"attestation": new_attestation})


__all__ = ["TSAUnavailableError", "attach_rfc3161"]
