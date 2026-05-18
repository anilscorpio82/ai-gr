"""ai_gr.regimes.base — Regime interface and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ai_gr.schema import Gate, GPREntry


@dataclass(frozen=True)
class RegimeRequirement:
    """A specific requirement of a regulatory regime."""

    citation: str
    description: str
    relevant_gates: tuple[Gate, ...]
    evidence_needed: tuple[str, ...] = field(default_factory=tuple)


class Regime(ABC):
    """Base class for a regulatory regime mapping."""

    #: Canonical identifier prefix used in ``regime[].regime`` strings.
    #: For example, "EU-AI-Act" produces claims like "EU-AI-Act:high-risk".
    identifier: str

    #: Human-readable name for reports.
    name: str

    #: Brief description for the executive summary of an exported dossier.
    description: str

    @abstractmethod
    def requirements(self) -> list[RegimeRequirement]:
        """Return the requirements this regime imposes."""

    def applies_to_entry(self, entry: GPREntry) -> bool:
        """True iff this entry contains at least one regime claim matching this regime."""
        return any(claim.regime.startswith(f"{self.identifier}:") for claim in entry.regime)

    def coverage_summary(self, chain: list[GPREntry]) -> dict[str, object]:
        """Summarize how well a chain satisfies this regime.

        Returns a dict suitable for emitting in an exported dossier:
            {
              "regime": <name>,
              "claims_made": <int>,
              "entries_covered": <int>,
              "gates_covered": [<Gate>, ...],
              "requirements": [
                {
                  "citation": <str>,
                  "satisfied": <bool>,
                  "evidence_entries": [<entry_id>, ...]
                }, ...
              ]
            }
        """
        relevant = [e for e in chain if self.applies_to_entry(e)]
        claims = sum(
            1
            for e in relevant
            for c in e.regime
            if c.regime.startswith(f"{self.identifier}:")
        )
        gates_covered = sorted({e.gate.value for e in relevant})

        requirements_summary = []
        for req in self.requirements():
            satisfied_in = [
                e.id
                for e in relevant
                if e.gate in req.relevant_gates
            ]
            requirements_summary.append(
                {
                    "citation": req.citation,
                    "description": req.description,
                    "satisfied": bool(satisfied_in),
                    "evidence_entries": satisfied_in,
                }
            )

        return {
            "regime": self.name,
            "identifier": self.identifier,
            "description": self.description,
            "claims_made": claims,
            "entries_covered": len(relevant),
            "gates_covered": gates_covered,
            "requirements": requirements_summary,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class RegimeRegistry:
    """Process-wide registry of regime instances."""

    def __init__(self) -> None:
        self._regimes: dict[str, Regime] = {}

    def register(self, regime: Regime) -> None:
        self._regimes[regime.identifier] = regime

    def get(self, identifier: str) -> Regime:
        if identifier not in self._regimes:
            raise KeyError(f"No regime registered with identifier {identifier!r}.")
        return self._regimes[identifier]

    def list(self) -> list[Regime]:
        return list(self._regimes.values())


_REGISTRY = RegimeRegistry()


def get_regime(identifier: str) -> Regime:
    return _REGISTRY.get(identifier)


def list_regimes() -> list[Regime]:
    return _REGISTRY.list()


def _register(regime: Regime) -> Regime:
    _REGISTRY.register(regime)
    return regime


__all__ = [
    "Regime",
    "RegimeRegistry",
    "RegimeRequirement",
    "_register",
    "get_regime",
    "list_regimes",
]
