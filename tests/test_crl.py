import pytest
from datetime import datetime, timezone, timedelta
from ai_gr.crypto.crl import CertificateRevocationList, global_crl
from ai_gr.crypto import KeyPair, SignatureVerificationError, sign_entry, verify_signature
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

def _entry(did: str) -> GPREntry:
    return GPREntry(
        id="urn:gpr:org/sys/conceive/0001",
        subject=Subject(system="S", version="1.0.0", type=SystemType.PREDICTIVE),
        gate=Gate.CONCEIVE,
        risk_tier=RiskTier.MANAGED,
        decision=Decision.APPROVE,
        evidence=Evidence(),
        authority=Authority(approver=did, delegated_scope="tier:managed"),
    )

def test_crl_revocation_logic():
    crl = CertificateRevocationList()
    did = "did:web:acme:ciso"
    
    # 1. Not revoked
    assert not crl.is_revoked(did)
    
    # 2. Revoke it now
    now_str = datetime.now(timezone.utc).isoformat()
    crl.revoke_key(did, now_str)
    assert crl.is_revoked(did)
    
    # 3. Signature created BEFORE revocation is valid
    past_str = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    assert not crl.was_revoked_at_time(did, past_str)
    
    # 4. Signature created AFTER revocation is invalid
    future_str = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    assert crl.was_revoked_at_time(did, future_str)

def test_verify_rejects_revoked_key():
    kp = KeyPair.generate()
    # In a real system, the DID is derived from or associated with the public key.
    # We will just use a dummy DID.
    did = "did:web:acme:ciso"
    
    entry = _entry(did)
    signed = sign_entry(entry, kp)
    
    # Initially, verification passes
    verify_signature(signed)
    
    # Now, a malicious actor steals the key. The enterprise revokes it *before* the signature timestamp
    # (Simulating a signature made after the key was revoked)
    past_revocation_time = (signed.attestation.timestamp - timedelta(minutes=5)).isoformat()
    global_crl.revoke_key(did, past_revocation_time)
    
    # Verification should now fail because the key was on the CRL at the time of signing
    with pytest.raises(SignatureVerificationError, match="Signature rejected: DID .* was revoked prior to signing"):
        verify_signature(signed)
