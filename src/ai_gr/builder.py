"""
ai_gr.builder — Ergonomic chain construction helpers.

The schema is intentionally strict — every GPR entry must declare its linkage,
attestation, and content hash chain. Constructing this by hand is verbose, so
this module offers a builder that handles the chaining and signing
boilerplate automatically.
"""

from __future__ import annotations

from typing import Any

from ai_gr.crypto.sign import KeyPair, sign_entry
from ai_gr.schema import (
    AgenticContext,
    Authority,
    Decision,
    Evidence,
    Gate,
    GPREntry,
    LegalIdentity,
    Linkage,
    RegimeClaim,
    RiskTier,
    Subject,
)


class ChainBuilder:
    """Build a chain of GPR entries for a single system.

    The builder accepts a ``legal_identity`` representing the legal person
    operating the AI system. This identity is automatically attached to the
    Authority of every entry created via ``append()``, satisfying the
    Critical-tier invariant introduced in schema v0.2.0.

    Usage:

        builder = ChainBuilder(
            org="acme-health",
            system="cds-agent",
            subject=Subject(...),
            keypair=KeyPair.generate(),
            approver_did="did:web:acme-health:caio",
            legal_identity=LegalIdentity(
                name="ACME Health Systems Inc.",
                registration_id="LEI:5493001K3F3DUM2KRD89",
                jurisdiction="DE",
                address="Musterstrasse 1, 10115 Berlin",
                contact_email="compliance@acme-health.example",
                gdpr_role=GdprRole.CONTROLLER,
            ),
        )
    """

    def __init__(
        self,
        *,
        org: str,
        system: str,
        subject: Subject,
        keypair: KeyPair,
        approver_did: str,
        legal_identity: LegalIdentity | None = None,
    ) -> None:
        self.org = org
        self.system = system
        self.subject = subject
        self.keypair = keypair
        self.approver_did = approver_did
        self.legal_identity = legal_identity
        self._chain: list[GPREntry] = []
        self._gate_counts: dict[Gate, int] = {}

    def _next_id(self, gate: Gate) -> str:
        n = self._gate_counts.get(gate, 0) + 1
        self._gate_counts[gate] = n
        return f"urn:gpr:{self.org}/{self.system}/{gate.value.lower()}/{n:04d}"

    @property
    def chain(self) -> list[GPREntry]:
        """Return a copy of the chain built so far."""
        return list(self._chain)

    @property
    def head(self) -> GPREntry | None:
        return self._chain[-1] if self._chain else None

    def append(
        self,
        *,
        gate: Gate,
        tier: RiskTier,
        decision: Decision,
        regimes: list[RegimeClaim] | None = None,
        evidence: Evidence | None = None,
        agentic_context: AgenticContext | None = None,
        delegated_scope: str = "tier:critical",
        co_approvers: list[str] | None = None,
        sign: bool = True,
        **extra: Any,
    ) -> GPREntry:
        """Append a new entry to the chain.

        Args:
            gate: The Ribbon gate this entry attests to.
            tier: Risk tier.
            decision: Decision rendered at this gate.
            regimes: Regulatory claims attested by this entry.
            evidence: Evidence block. Defaults to empty.
            agentic_context: Required for agentic systems.
            delegated_scope: Authority scope string.
            co_approvers: Optional co-approver DIDs.
            sign: If True, the entry is signed with the builder's keypair.
            extra: Forwarded to GPREntry constructor.

        Returns:
            The appended entry.
        """
        head = self.head
        linkage = Linkage(
            prev_gpr=head.id if head else None,
            prev_hash=head.content_hash() if head else None,
            chain_root=self._chain[0].id if self._chain else None,
        )

        entry = GPREntry(
            id=self._next_id(gate),
            subject=self.subject,
            gate=gate,
            risk_tier=tier,
            decision=decision,
            evidence=evidence or Evidence(),
            authority=Authority(
                approver=self.approver_did,
                delegated_scope=delegated_scope,
                co_approvers=co_approvers or [],
                legal_identity=self.legal_identity,
            ),
            regime=regimes or [],
            agentic_context=agentic_context,
            linkage=linkage,
            **extra,
        )

        if sign:
            entry = sign_entry(entry, self.keypair)

        self._chain.append(entry)
        return entry


__all__ = ["ChainBuilder"]
