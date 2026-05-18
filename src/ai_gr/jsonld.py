"""
ai_gr.jsonld — JSON-LD serialization and canonicalization helpers.

The AI-GR framework uses JSON-LD as its on-the-wire format because it gives us
three properties we need for free:

  1. Machine-readable namespacing — the @context URL anchors the vocabulary.
  2. Deterministic canonicalization — required for content addressing.
  3. Linked-data semantics — regimes and authorities are URIs that resolve.

For v0.1 we use a deterministic JSON serialization (sorted keys, no
whitespace) rather than full JSON-LD Normalization (RDF Dataset Canonical
Form). This is faster, simpler, and sufficient for hashing within a closed
schema. v0.2 will add full URDNA2015 canonicalization for cross-implementation
interop.
"""

from __future__ import annotations

import json
from typing import Any

from ai_gr.schema import AI_GR_CONTEXT, GPREntry


def to_jsonld_string(entry: GPREntry, indent: int | None = 2) -> str:
    """Serialize a GPR entry as a pretty-printed JSON-LD string.

    Use ``indent=None`` for compact output (e.g. for storage).
    """
    return json.dumps(entry.to_jsonld(), indent=indent, sort_keys=True, default=str)


def from_jsonld_dict(payload: dict[str, Any]) -> GPREntry:
    """Parse a JSON-LD dict into a GPREntry.

    Validates that the @context is recognized; rejects unknown contexts to
    guard against schema spoofing.
    """
    ctx = payload.get("@context")
    if ctx != AI_GR_CONTEXT:
        raise ValueError(
            f"Unrecognized @context: {ctx!r}. Expected {AI_GR_CONTEXT!r}. "
            "This entry was not produced by an AI-GR v1 implementation."
        )
    return GPREntry.model_validate(payload)


def from_jsonld_string(s: str) -> GPREntry:
    """Parse a JSON-LD string into a GPREntry."""
    return from_jsonld_dict(json.loads(s))


__all__ = [
    "from_jsonld_dict",
    "from_jsonld_string",
    "to_jsonld_string",
]
