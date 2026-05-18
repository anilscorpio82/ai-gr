"""ai_gr.ribbon — The Ribbon framework: gates, risk tiers, and the policy matrix."""

from ai_gr.ribbon.gates import GATE_ORDER, next_gate
from ai_gr.ribbon.policy import (
    GateRequirement,
    PolicyViolation,
    check_entry,
    requirements_for,
)
from ai_gr.ribbon.tiers import classify_system, tier_color

__all__ = [
    "GATE_ORDER",
    "GateRequirement",
    "PolicyViolation",
    "check_entry",
    "classify_system",
    "next_gate",
    "requirements_for",
    "tier_color",
]
