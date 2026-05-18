"""
ai_gr.store.filesystem — Filesystem-backed append-only GPR store.

Storage layout:

    <root>/
      <org>/
        <system>/
          chain.jsonl              # append-only chronological log
          entries/
            <gate>-<seq>.jsonld    # canonical per-entry file

The chain.jsonl is the chronological audit log; the per-entry files are the
addressable artifacts. Both are written atomically (write-then-rename) to
survive interrupted writes.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

from ai_gr.jsonld import from_jsonld_dict, to_jsonld_string
from ai_gr.schema import GPREntry
from ai_gr.store.base import GPRStore


class FilesystemStore(GPRStore):
    """Append-only GPR store on the local filesystem."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    # ---- Layout helpers ----

    @staticmethod
    def _split_id(entry_id: str) -> tuple[str, str, str, str]:
        """Parse 'urn:gpr:<org>/<system>/<gate>/<seq>' into parts."""
        # entry_id format guaranteed by GPREntry validator.
        # Strip 'urn:gpr:' prefix, then split on '/'.
        body = entry_id[len("urn:gpr:") :]
        org, system, gate, seq = body.split("/")
        return org, system, gate, seq

    def _system_dir(self, org: str, system: str) -> Path:
        return self._root / org / system

    def _chain_file(self, org: str, system: str) -> Path:
        return self._system_dir(org, system) / "chain.jsonl"

    def _entry_path(self, entry_id: str) -> Path:
        org, system, gate, seq = self._split_id(entry_id)
        return self._system_dir(org, system) / "entries" / f"{gate.lower()}-{seq}.jsonld"

    # ---- Atomic write helper ----

    @staticmethod
    def _atomic_write(path: Path, data: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=path.suffix)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
            os.replace(tmp, path)
        except Exception:
            # Clean up the temp file if anything went wrong before rename.
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ---- GPRStore interface ----

    def append(self, entry: GPREntry) -> None:
        entry_path = self._entry_path(entry.id)
        if entry_path.exists():
            raise FileExistsError(f"Entry file already exists: {entry_path}")

        org, system, _, _ = self._split_id(entry.id)
        existing_chain = self.chain_for(f"urn:gpr:{org}/{system}")

        if not existing_chain:
            if entry.linkage.prev_gpr is not None:
                raise ValueError(
                    f"First entry for urn:gpr:{org}/{system} must have prev_gpr=None, "
                    f"got {entry.linkage.prev_gpr!r}."
                )
        else:
            head = existing_chain[-1]
            if entry.linkage.prev_gpr != head.id:
                raise ValueError(
                    f"Chain head is {head.id!r}, "
                    f"but new entry's prev_gpr is {entry.linkage.prev_gpr!r}."
                )
            if entry.linkage.prev_hash != head.content_hash():
                raise ValueError(
                    f"prev_hash mismatch: expected {head.content_hash()!r}, "
                    f"got {entry.linkage.prev_hash!r}."
                )

        # Write the per-entry file atomically.
        self._atomic_write(entry_path, to_jsonld_string(entry, indent=2))

        # Append to the chain log. We open in append mode rather than atomic
        # write because JSONL is designed for append-only semantics, and the
        # per-entry file is the authoritative artifact.
        chain_file = self._chain_file(org, system)
        chain_file.parent.mkdir(parents=True, exist_ok=True)
        with chain_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"id": entry.id, "hash": entry.content_hash()}) + "\n")

    def get(self, entry_id: str) -> GPREntry:
        path = self._entry_path(entry_id)
        if not path.exists():
            raise KeyError(entry_id)
        with path.open("r", encoding="utf-8") as f:
            return from_jsonld_dict(json.load(f))

    def chain_for(self, system_urn_prefix: str) -> list[GPREntry]:
        body = system_urn_prefix[len("urn:gpr:") :]
        try:
            org, system = body.split("/")
        except ValueError as exc:
            raise ValueError(
                f"system_urn_prefix must be 'urn:gpr:<org>/<system>', got {system_urn_prefix!r}"
            ) from exc

        chain_file = self._chain_file(org, system)
        if not chain_file.exists():
            return []

        entries: list[GPREntry] = []
        with chain_file.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                entries.append(self.get(rec["id"]))
        return entries

    def __iter__(self) -> Iterator[GPREntry]:
        for chain_file in self._root.rglob("chain.jsonl"):
            with chain_file.open("r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    yield self.get(rec["id"])

    def __len__(self) -> int:
        return sum(1 for _ in self)


__all__ = ["FilesystemStore"]
