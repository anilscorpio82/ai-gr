"""Tests for Ed25519 signing and verification."""

from __future__ import annotations

import pytest

from ai_gr import (
    Authority,
    Decision,
    Evidence,
    Gate,
    GPREntry,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.crypto import KeyPair, SignatureVerificationError, sign_entry, verify_signature
from ai_gr.crypto.timestamp import attach_rfc3161


def _entry(**overrides) -> GPREntry:
    defaults = {
        "id": "urn:gpr:org/sys/conceive/0001",
        "subject": Subject(system="S", version="1.0.0", type=SystemType.PREDICTIVE),
        "gate": Gate.CONCEIVE,
        "risk_tier": RiskTier.MANAGED,
        "decision": Decision.APPROVE,
        "evidence": Evidence(),
        "authority": Authority(approver="did:web:x:y", delegated_scope="tier:managed"),
    }
    defaults.update(overrides)
    return GPREntry(**defaults)


class TestKeyPair:
    def test_generate_produces_distinct_keys(self) -> None:
        kp1 = KeyPair.generate()
        kp2 = KeyPair.generate()
        assert kp1.private_key_b64 != kp2.private_key_b64
        assert kp1.public_key_b64 != kp2.public_key_b64

    def test_keys_are_base64_decodable(self) -> None:
        import base64

        kp = KeyPair.generate()
        # Ed25519 raw private and public keys are both 32 bytes.
        assert len(base64.b64decode(kp.private_key_b64)) == 32
        assert len(base64.b64decode(kp.public_key_b64)) == 32


class TestSignAndVerify:
    def test_sign_then_verify(self) -> None:
        kp = KeyPair.generate()
        entry = _entry()
        signed = sign_entry(entry, kp)
        assert signed.attestation.signature is not None
        assert signed.attestation.signature.startswith("ed25519:")
        verify_signature(signed)

    def test_unsigned_entry_rejected(self) -> None:
        with pytest.raises(SignatureVerificationError, match="no signature"):
            verify_signature(_entry())

    def test_tampered_entry_rejected(self) -> None:
        """Changing any field after signing must invalidate the signature."""
        kp = KeyPair.generate()
        signed = sign_entry(_entry(), kp)
        tampered = signed.model_copy(update={"decision": Decision.REJECT})
        with pytest.raises(SignatureVerificationError, match="did not verify"):
            verify_signature(tampered)

    def test_wrong_public_key_rejected(self) -> None:
        kp_signer = KeyPair.generate()
        kp_other = KeyPair.generate()
        signed = sign_entry(_entry(), kp_signer)
        # Swap in another party's public key.
        bad = signed.model_copy(
            update={
                "attestation": signed.attestation.model_copy(
                    update={"public_key": kp_other.public_key_b64}
                )
            }
        )
        with pytest.raises(SignatureVerificationError, match="did not verify"):
            verify_signature(bad)


class TestTimestamp:
    def test_stub_timestamp_attaches(self) -> None:
        kp = KeyPair.generate()
        signed = sign_entry(_entry(), kp)
        stamped = attach_rfc3161(signed, tsa_url=None)
        assert stamped.attestation.rfc3161_token is not None
        assert stamped.attestation.rfc3161_token.startswith("stub:")
        # Stamped entry still verifies (timestamp is metadata, not signed content).
        verify_signature(stamped)

    def test_unsigned_cannot_be_timestamped(self) -> None:
        with pytest.raises(ValueError, match="unsigned"):
            attach_rfc3161(_entry(), tsa_url=None)
