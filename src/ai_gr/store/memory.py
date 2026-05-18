"""ai_gr.store.memory — In-memory GPR store (for tests and demos)."""

from __future__ import annotations

from collections.abc import Iterator

from ai_gr.schema import GPREntry
from ai_gr.store.base import GPRStore


class InMemoryStore(GPRStore):
    """A simple append-only store backed by a list."""

    def __init__(self) -> None:
        self._entries: dict[str, GPREntry] = {}
        # System prefix -> ordered list of entry IDs (chronological).
        self._chains: dict[str, list[str]] = {}

    @staticmethod
    def _system_prefix(entry: GPREntry) -> str:
        # Extract "urn:gpr:<org>/<system>" from "urn:gpr:<org>/<system>/<gate>/<seq>".
        parts = entry.id.split("/")
        return "/".join(parts[:2])

    def append(self, entry: GPREntry) -> None:
        if entry.id in self._entries:
            raise FileExistsError(f"Entry {entry.id} already exists in store.")

        prefix = self._system_prefix(entry)
        existing_head = self._chains.get(prefix, [])

        if not existing_head:
            # First entry for this system — must be root (prev_gpr is None).
            if entry.linkage.prev_gpr is not None:
                raise ValueError(
                    f"First entry for {prefix} must have prev_gpr=None, "
                    f"got {entry.linkage.prev_gpr!r}."
                )
        else:
            head_id = existing_head[-1]
            head_entry = self._entries[head_id]
            if entry.linkage.prev_gpr != head_id:
                raise ValueError(
                    f"Chain head for {prefix} is {head_id!r}, "
                    f"but new entry's prev_gpr is {entry.linkage.prev_gpr!r}."
                )
            if entry.linkage.prev_hash != head_entry.content_hash():
                raise ValueError(
                    f"prev_hash mismatch: expected {head_entry.content_hash()!r}, "
                    f"got {entry.linkage.prev_hash!r}."
                )

        self._entries[entry.id] = entry
        self._chains.setdefault(prefix, []).append(entry.id)

    def get(self, entry_id: str) -> GPREntry:
        return self._entries[entry_id]

    def chain_for(self, system_urn_prefix: str) -> list[GPREntry]:
        ids = self._chains.get(system_urn_prefix, [])
        return [self._entries[eid] for eid in ids]

    def __iter__(self) -> Iterator[GPREntry]:
        return iter(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)


__all__ = ["InMemoryStore"]
