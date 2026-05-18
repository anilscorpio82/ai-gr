"""ai_gr.store.base — Append-only GPR store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from ai_gr.schema import GPREntry


class GPRStore(ABC):
    """Append-only store for GPR entries.

    Stores are append-only by contract: once an entry is appended, it cannot
    be modified or removed. This is a framework-level invariant — modifying a
    GPR after it has been chained would invalidate every entry downstream.

    The store also enforces chain integrity at append time: any new entry's
    ``linkage.prev_gpr`` and ``linkage.prev_hash`` must point to the most
    recent entry for the same subject system, or be None (for the root entry).
    """

    @abstractmethod
    def append(self, entry: GPREntry) -> None:
        """Append a new entry to the store.

        Raises:
            ValueError: If the entry's linkage does not match the current head
                of the chain for its subject system.
            FileExistsError: If an entry with this ID already exists.
        """

    @abstractmethod
    def get(self, entry_id: str) -> GPREntry:
        """Retrieve an entry by its URN id."""

    @abstractmethod
    def chain_for(self, system_urn_prefix: str) -> list[GPREntry]:
        """Retrieve the ordered chain for a given system URN prefix.

        The prefix is of the form ``urn:gpr:<org>/<system>``. Returns the
        chain in chronological order (root first).
        """

    @abstractmethod
    def __iter__(self) -> Iterator[GPREntry]:
        """Iterate all entries in the store (no guaranteed order)."""

    @abstractmethod
    def __len__(self) -> int:
        """Total number of entries in the store."""

    def head_for(self, system_urn_prefix: str) -> GPREntry | None:
        """Return the most recent entry for a system, or None if none exist."""
        chain = self.chain_for(system_urn_prefix)
        return chain[-1] if chain else None


__all__ = ["GPRStore"]
