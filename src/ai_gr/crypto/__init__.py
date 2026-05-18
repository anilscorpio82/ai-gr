"""ai_gr.crypto — Cryptographic primitives for GPR attestation and chain verification."""

from ai_gr.crypto.sign import KeyPair, sign_entry
from ai_gr.crypto.timestamp import attach_rfc3161
from ai_gr.crypto.verify import (
    ChainVerificationError,
    SignatureVerificationError,
    verify_chain,
    verify_signature,
)

__all__ = [
    "ChainVerificationError",
    "KeyPair",
    "SignatureVerificationError",
    "attach_rfc3161",
    "sign_entry",
    "verify_chain",
    "verify_signature",
]
