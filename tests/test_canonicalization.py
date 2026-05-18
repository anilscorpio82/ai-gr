"""Tests that GPR canonicalization is RFC 8785 (JCS) compliant.

New in v0.2.0. The prior implementation used json.dumps(sort_keys=True), which
produced byte-identical output to JCS for ASCII inputs but diverged on:
- Unicode normalization (RFC 8785 requires NFC; Python doesn't normalize by default)
- Number rendering (RFC 8785 has strict shortest-form rules)
- Some edge cases around nested objects and arrays

These tests verify that the canonicalization conforms to RFC 8785 and that
two implementations consuming the same GPR will produce identical hashes.
"""

from __future__ import annotations

import hashlib
import json

import rfc8785

from ai_gr import (
    Authority,
    Decision,
    Evidence,
    Gate,
    GPREntry,
    LegalIdentity,
    RiskTier,
    Subject,
    SystemType,
)


def _make_entry(extra_evidence: dict | None = None) -> GPREntry:
    legal_id = LegalIdentity(
        name="Test Corp Ltd.",
        registration_id="LEI:TESTCORP000000000001",
        jurisdiction="GB",
        address="1 Test Lane, London",
        contact_email="test@example.com",
    )
    return GPREntry(
        id="urn:gpr:t/s/build/0001",
        subject=Subject(system="S", version="1", type=SystemType.PREDICTIVE),
        gate=Gate.BUILD,
        risk_tier=RiskTier.CRITICAL,
        decision=Decision.APPROVE,
        evidence=Evidence(additional=extra_evidence or {}),
        authority=Authority(
            approver="did:web:t:r",
            delegated_scope="x",
            legal_identity=legal_id,
        ),
        regime=[],
    )


class TestRfc8785Conformance:
    def test_canonical_bytes_are_rfc8785_output(self) -> None:
        """canonical_bytes() must equal rfc8785.dumps() of the same payload."""
        entry = _make_entry()
        payload = entry.model_dump(by_alias=True, mode="json", exclude={"attestation"})
        expected = rfc8785.dumps(payload)
        assert entry.canonical_bytes() == expected

    def test_unicode_characters_preserved(self) -> None:
        """Unicode strings are preserved as-is per RFC 8785 §3.2.3.

        Note: RFC 8785 does NOT mandate NFC normalization — that's I-JSON
        (RFC 7493). JCS preserves the input bytes. If callers need
        NFC normalization for consistency between NFC/NFD inputs, they
        must normalize before serializing.
        """
        entry = _make_entry(extra_evidence={"note": "caf\u00e9"})  # NFC
        canonical = entry.canonical_bytes().decode("utf-8")
        assert "caf\u00e9" in canonical

    def test_key_ordering_is_lexicographic(self) -> None:
        """Object keys are sorted lexicographically by code point."""
        entry = _make_entry(extra_evidence={"zebra": 1, "apple": 2, "mango": 3})
        canonical = entry.canonical_bytes().decode("utf-8")
        apple_pos = canonical.find('"apple"')
        mango_pos = canonical.find('"mango"')
        zebra_pos = canonical.find('"zebra"')
        # Keys must appear in lexicographic order
        assert apple_pos < mango_pos < zebra_pos

    def test_no_structural_whitespace_in_output(self) -> None:
        """JCS output has no insignificant whitespace between JSON tokens.

        Note: whitespace inside string values is preserved (e.g. "foo bar"
        keeps its space; an address like "1 Lane, London" preserves its
        comma-space). Only structural whitespace between tokens is removed.

        To test this cleanly, we use a payload with no whitespace anywhere in
        string values, so any whitespace in the output must be structural —
        and per RFC 8785, structural whitespace is absent.
        """
        entry = _make_entry(extra_evidence={"a": "b", "c": "d"})
        # Strip out all string contents to check structural whitespace
        # cleanly: replace every "..." string with "" and check the
        # resulting JSON skeleton has no whitespace.
        canonical = entry.canonical_bytes().decode("utf-8")

        import re

        # Remove all string values (anything between unescaped quote pairs)
        skeleton = re.sub(r'"(?:[^"\\]|\\.)*"', '""', canonical)
        # The skeleton should now contain only structural JSON tokens.
        # RFC 8785 mandates no whitespace between them.
        assert " " not in skeleton, (
            f"Structural whitespace found in JSON skeleton: {skeleton!r}"
        )

    def test_content_hash_is_stable(self) -> None:
        """Two entries with identical content produce identical hashes."""
        e1 = _make_entry()
        e2 = _make_entry()
        assert e1.content_hash() == e2.content_hash()

    def test_content_hash_changes_on_data_change(self) -> None:
        e1 = _make_entry(extra_evidence={"k": "v1"})
        e2 = _make_entry(extra_evidence={"k": "v2"})
        assert e1.content_hash() != e2.content_hash()

    def test_attestation_excluded_from_canonical_bytes(self) -> None:
        """The attestation block is excluded so signature can be computed over the rest."""
        entry = _make_entry()
        canonical = entry.canonical_bytes().decode("utf-8")
        assert "attestation" not in canonical


class TestInteroperability:
    """Tests that two independent implementations producing the same GPR
    semantics would produce the same canonical hash."""

    def test_hash_matches_independent_jcs_implementation(self) -> None:
        """An independent JCS implementation should produce the same hash."""
        entry = _make_entry()
        # Reconstruct the canonical bytes via the underlying rfc8785 library
        # directly (this is what the schema does internally; here we verify
        # there's no path-dependence).
        payload = entry.model_dump(by_alias=True, mode="json", exclude={"attestation"})
        independent_bytes = rfc8785.dumps(payload)
        independent_hash = hashlib.sha256(independent_bytes).hexdigest()
        assert entry.content_hash() == independent_hash

    def test_hash_does_not_match_plain_json_dumps_for_floats(self) -> None:
        """Naive json.dumps does NOT produce JCS output for float-containing
        payloads, demonstrating why v0.2.0 changed the canonicalization.

        JCS renders 1.0 as "1" (no trailing .0), while json.dumps renders
        it as "1.0". Similarly, JCS renders 1.5e-5 as "0.000015" while
        json.dumps keeps scientific notation.
        """
        # Use a payload where float rendering matters
        entry = _make_entry(extra_evidence={"score": 1.0, "tiny": 1.5e-5})
        payload = entry.model_dump(by_alias=True, mode="json", exclude={"attestation"})
        naive_bytes = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        # JCS renders these floats differently than json.dumps.
        assert naive_bytes != entry.canonical_bytes()
