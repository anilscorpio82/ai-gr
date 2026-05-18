"""Tests for chain construction, persistence, and integrity verification."""

from __future__ import annotations

import pytest

from ai_gr import (
    Decision,
    Evidence,
    Gate,
    RegimeClaim,
    RiskTier,
    Subject,
    SystemType,
)
from ai_gr.builder import ChainBuilder
from ai_gr.crypto import ChainVerificationError, KeyPair, verify_chain
from ai_gr.store import FilesystemStore, InMemoryStore


def _make_builder() -> ChainBuilder:
    return ChainBuilder(
        org="test-org",
        system="test-sys",
        subject=Subject(system="TestSystem", version="1.0.0", type=SystemType.PREDICTIVE),
        keypair=KeyPair.generate(),
        approver_did="did:web:test-org:approver",
    )


def _populate(builder: ChainBuilder, n: int = 3) -> None:
    gates = [Gate.CONCEIVE, Gate.BUILD, Gate.DEPLOY, Gate.OPERATE, Gate.EVOLVE]
    for i in range(n):
        builder.append(
            gate=gates[i],
            tier=RiskTier.MANAGED,
            decision=Decision.APPROVE,
            evidence=Evidence(evaluations=[f"eval-{i}.pdf"]),
            regimes=[RegimeClaim(regime="NIST-AI-RMF:MAP-1.1")],
        )


class TestInMemoryStore:
    def test_append_and_retrieve(self) -> None:
        builder = _make_builder()
        _populate(builder, n=3)
        store = InMemoryStore()
        for e in builder.chain:
            store.append(e)
        assert len(store) == 3
        for e in builder.chain:
            assert store.get(e.id) == e

    def test_chain_retrieval_preserves_order(self) -> None:
        builder = _make_builder()
        _populate(builder, n=3)
        store = InMemoryStore()
        for e in builder.chain:
            store.append(e)
        chain = store.chain_for("urn:gpr:test-org/test-sys")
        assert [e.id for e in chain] == [e.id for e in builder.chain]

    def test_duplicate_id_rejected(self) -> None:
        builder = _make_builder()
        _populate(builder, n=2)
        store = InMemoryStore()
        for e in builder.chain:
            store.append(e)
        with pytest.raises(FileExistsError):
            store.append(builder.chain[0])

    def test_broken_chain_at_append_rejected(self) -> None:
        """Out-of-order append (skipping a link) should be refused."""
        builder = _make_builder()
        _populate(builder, n=3)
        store = InMemoryStore()
        store.append(builder.chain[0])
        # Attempt to append the third entry without the second.
        with pytest.raises(ValueError, match="prev_gpr"):
            store.append(builder.chain[2])


class TestFilesystemStore:
    def test_persist_and_reread(self, tmp_path) -> None:
        builder = _make_builder()
        _populate(builder, n=3)
        store = FilesystemStore(tmp_path)
        for e in builder.chain:
            store.append(e)

        # Re-instantiate and re-read.
        store2 = FilesystemStore(tmp_path)
        chain = store2.chain_for("urn:gpr:test-org/test-sys")
        assert len(chain) == 3
        for original, reread in zip(builder.chain, chain, strict=True):
            assert original.id == reread.id
            assert original.content_hash() == reread.content_hash()

    def test_per_entry_files_exist(self, tmp_path) -> None:
        builder = _make_builder()
        _populate(builder, n=2)
        store = FilesystemStore(tmp_path)
        for e in builder.chain:
            store.append(e)
        assert (tmp_path / "test-org" / "test-sys" / "entries" / "conceive-0001.jsonld").exists()
        assert (tmp_path / "test-org" / "test-sys" / "entries" / "build-0001.jsonld").exists()
        assert (tmp_path / "test-org" / "test-sys" / "chain.jsonl").exists()


class TestChainVerification:
    def test_clean_chain_verifies(self) -> None:
        builder = _make_builder()
        _populate(builder, n=4)
        verify_chain(builder.chain)

    def test_empty_chain_rejected(self) -> None:
        with pytest.raises(ChainVerificationError, match="Empty"):
            verify_chain([])

    def test_root_with_non_null_prev_rejected(self) -> None:
        """If chain[0] has a non-null prev_gpr, verification must fail."""
        builder = _make_builder()
        _populate(builder, n=2)
        chain = builder.chain
        # Tamper the root by giving it a prev_gpr.
        tampered_root = chain[0].model_copy(
            update={"linkage": chain[0].linkage.model_copy(update={"prev_gpr": "urn:gpr:fake/x/conceive/0001"})}
        )
        with pytest.raises(ChainVerificationError, match="prev_gpr"):
            verify_chain([tampered_root, chain[1]], verify_signatures=False)

    def test_hash_mismatch_detected(self) -> None:
        """Tampering with an entry should break the chain at the next entry."""
        builder = _make_builder()
        _populate(builder, n=3)
        chain = builder.chain
        # Tamper entry[1] by changing its content but keeping the original
        # entry[2] (which holds a hash of the *original* entry[1]).
        tampered_middle = chain[1].model_copy(
            update={"evidence": Evidence(evaluations=["tampered-evidence.pdf"])}
        )
        with pytest.raises(ChainVerificationError, match="hash mismatch"):
            verify_chain([chain[0], tampered_middle, chain[2]], verify_signatures=False)
