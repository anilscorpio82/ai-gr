"""ai_gr.ribbon.gates — Lifecycle gate ordering and transitions."""

from __future__ import annotations

from ai_gr.schema import Gate

#: Canonical order of the lifecycle gates. The provenance chain advances
#: through them sequentially, though a system may revisit Build, Deploy,
#: Operate, and Evolve repeatedly over its lifetime before reaching Retire.
GATE_ORDER: tuple[Gate, ...] = (
    Gate.CONCEIVE,
    Gate.BUILD,
    Gate.DEPLOY,
    Gate.OPERATE,
    Gate.EVOLVE,
    Gate.RETIRE,
)


def next_gate(current: Gate) -> Gate | None:
    """Return the canonical successor of the given gate, or None for Retire."""
    idx = GATE_ORDER.index(current)
    if idx == len(GATE_ORDER) - 1:
        return None
    return GATE_ORDER[idx + 1]


def gate_index(gate: Gate) -> int:
    """Return the 0-based position of a gate in the canonical order."""
    return GATE_ORDER.index(gate)


__all__ = ["GATE_ORDER", "gate_index", "next_gate"]
