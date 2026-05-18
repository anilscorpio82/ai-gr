"""
ai_gr.crypto.verify — Signature and chain verification.

Two distinct verifications happen on a GPR chain:

  1. Per-entry signature verification — proves each entry was signed by the
     holder of the named public key, and has not been tampered with since
     signing.

  2. Chain integrity verification — proves the sequence of entries is
     unbroken: each entry's ``linkage.prev_hash`` matches the content hash of
     the prior entry, and the ``linkage.prev_gpr`` URN matches the prior
     entry's ``id``.

Both must pass for a chain to be regulator-ready. The chain verification is
what distinguishes GPR from document-based artifacts: tampering with any
historical entry invalidates every entry downstream.
"""

from __future__ import annotations

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ai_gr.schema import GPREntry
from ai_gr.crypto.crl import global_crl


class SignatureVerificationError(ValueError):
    """Raised when an entry's signature fails to verify."""


class ChainVerificationError(ValueError):
    """Raised when chain integrity is broken (missing link, wrong hash, etc.)."""


def verify_signature(entry: GPREntry) -> None:
    """Verify the Ed25519 signature on a single entry.

    Raises ``SignatureVerificationError`` if the entry is unsigned, the public
    key is missing, or the signature does not match the entry's canonical
    bytes.
    """
    att = entry.attestation
    if att.signature is None:
        raise SignatureVerificationError(
            f"Entry {entry.id} has no signature — cannot verify."
        )
    if att.public_key is None:
        raise SignatureVerificationError(
            f"Entry {entry.id} signature is present but public_key is missing."
        )
    if not att.signature.startswith("ed25519:"):
        raise SignatureVerificationError(
            f"Entry {entry.id}: unsupported signature algorithm. Only ed25519 is supported in v0.1."
        )

    sig_b64 = att.signature.split(":", 1)[1]
    sig = base64.b64decode(sig_b64)
    pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(att.public_key))

    # Verify CRL Status
    did = entry.authority.approver
    if global_crl.was_revoked_at_time(did, att.timestamp.isoformat()):
        raise SignatureVerificationError(
            f"Signature rejected: DID {did} was revoked prior to signing."
        )

    try:
        pk.verify(sig, entry.canonical_bytes())
    except InvalidSignature as exc:
        raise SignatureVerificationError(
            f"Entry {entry.id}: signature did not verify against the entry's canonical bytes. "
            "This indicates tampering or key mismatch."
        ) from exc


def verify_chain(entries: list[GPREntry], *, verify_signatures: bool = True) -> None:
    """Verify an ordered chain of GPR entries.

    Entries must be ordered from oldest (chain root) to newest. The first
    entry's ``linkage.prev_gpr`` must be ``None``; every subsequent entry's
    ``linkage.prev_gpr`` and ``linkage.prev_hash`` must match the prior
    entry's ``id`` and content hash respectively.

    Args:
        entries: Ordered list of GPR entries (root first).
        verify_signatures: If True, also verify each entry's signature.

    Raises:
        ChainVerificationError: If chain integrity is broken.
        SignatureVerificationError: If any signature verification fails.
    """
    if not entries:
        raise ChainVerificationError("Empty chain — nothing to verify.")

    root = entries[0]
    if root.linkage.prev_gpr is not None:
        raise ChainVerificationError(
            f"Chain root {root.id} has a non-null prev_gpr ({root.linkage.prev_gpr!r}). "
            "Root entries must have prev_gpr=None."
        )
    if verify_signatures:
        verify_signature(root)

    for prev, curr in zip(entries[:-1], entries[1:], strict=True):
        if curr.linkage.prev_gpr != prev.id:
            raise ChainVerificationError(
                f"Chain broken at {curr.id}: prev_gpr={curr.linkage.prev_gpr!r}, "
                f"but prior entry id was {prev.id!r}."
            )
        prev_hash = prev.content_hash()
        if curr.linkage.prev_hash != prev_hash:
            raise ChainVerificationError(
                f"Chain hash mismatch at {curr.id}: prev_hash={curr.linkage.prev_hash!r}, "
                f"but prior entry content hash was {prev_hash!r}. "
                "This indicates the prior entry was modified after the current entry was signed."
            )
        if verify_signatures:
            verify_signature(curr)


__all__ = [
    "ChainVerificationError",
    "SignatureVerificationError",
    "verify_chain",
    "verify_signature",
]
