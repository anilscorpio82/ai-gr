"""
ai_gr.crypto.sign — Ed25519 signing for GPR entries.

We chose Ed25519 because:

  - It's the modern default for new digital signature systems (2026 best
    practice). RSA-2048 is fine but verbose; ECDSA P-256 is fine but has
    historical implementation footguns.
  - Keys are small (32 bytes) and fit comfortably inside a DID document.
  - Signing and verification are constant-time, making side-channel attacks
    on the signer harder.
  - The standard is finalized and broadly supported (RFC 8032).

Signing produces a base64-encoded signature stored in
``GPREntry.attestation.signature`` with the prefix ``ed25519:``. The
canonical bytes (per ``GPREntry.canonical_bytes()``) are signed; the
attestation block is excluded from those bytes by construction.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from ai_gr.schema import Attestation, GPREntry


@dataclass(frozen=True)
class KeyPair:
    """A serializable Ed25519 keypair.

    For demonstration purposes only. In production, private keys live in an
    HSM or KMS — never in process memory, never on disk in cleartext.
    """

    private_key_b64: str
    public_key_b64: str

    @classmethod
    def generate(cls) -> KeyPair:
        """Generate a fresh Ed25519 keypair."""
        sk = Ed25519PrivateKey.generate()
        pk = sk.public_key()
        return cls(
            private_key_b64=base64.b64encode(
                sk.private_bytes(
                    encoding=Encoding.Raw,
                    format=PrivateFormat.Raw,
                    encryption_algorithm=NoEncryption(),
                )
            ).decode("ascii"),
            public_key_b64=base64.b64encode(
                pk.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
            ).decode("ascii"),
        )

    def _private_key(self) -> Ed25519PrivateKey:
        return Ed25519PrivateKey.from_private_bytes(
            base64.b64decode(self.private_key_b64)
        )

    def public_key_object(self) -> Ed25519PublicKey:
        return Ed25519PublicKey.from_public_bytes(
            base64.b64decode(self.public_key_b64)
        )


def sign_entry(entry: GPREntry, keypair: KeyPair) -> GPREntry:
    """Sign a GPR entry with the given keypair.

    Returns a *new* entry with the attestation block populated. The original
    entry is not mutated. The signature covers ``entry.canonical_bytes()``,
    which excludes the attestation block — so the signature does not have to
    sign itself (a classic recursive-definition trap).
    """
    canonical = entry.canonical_bytes()
    sk = keypair._private_key()
    raw_sig = sk.sign(canonical)
    sig_b64 = base64.b64encode(raw_sig).decode("ascii")

    new_attestation = Attestation(
        signature=f"ed25519:{sig_b64}",
        signature_alg="ed25519",
        public_key=keypair.public_key_b64,
        timestamp=entry.attestation.timestamp,
        rfc3161_token=entry.attestation.rfc3161_token,
        tsa=entry.attestation.tsa,
    )

    return entry.model_copy(update={"attestation": new_attestation})


__all__ = ["KeyPair", "sign_entry"]
