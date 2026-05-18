"""
ai_gr.ribbon.tiers — Risk tier classification.

The three Ribbon tiers (Critical, High, Managed) determine the depth of
attestation required at each gate. Tiering is itself a governance decision
and is recorded in the Conceive entry of the chain.

Classification heuristics implemented here reflect the framework's stated
mapping on slide 3 of the deck:

    Critical : EU AI Act high-risk, HIPAA PHI, FDA SaMD, ADMT/AEDT
    High     : Material business or consumer-facing impact
    Managed  : Internal productivity, low-stakes assistive AI
"""

from __future__ import annotations

from ai_gr.schema import RiskTier


def tier_color(tier: RiskTier) -> str:
    """Hex color (no leading '#') used to render the tier in UI/export contexts."""
    return {
        RiskTier.CRITICAL: "B91C1C",
        RiskTier.HIGH: "D97706",
        RiskTier.MANAGED: "0D9488",
    }[tier]


def classify_system(
    *,
    handles_phi: bool = False,
    is_samd: bool = False,
    is_eu_high_risk_use_case: bool = False,
    makes_consequential_decisions: bool = False,
    consumer_facing: bool = False,
    material_to_revenue: bool = False,
) -> RiskTier:
    """Best-effort tier classification based on common triggers.

    This is a starting heuristic. Production deployments will customize this
    function with organization-specific policy (e.g. tier-up for any system
    touching customer financial data, regardless of consequentiality).

    Args:
        handles_phi: Touches protected health information (HIPAA).
        is_samd: Software as a Medical Device (FDA classification triggers).
        is_eu_high_risk_use_case: Falls under EU AI Act Annex III (employment,
            biometrics, critical infrastructure, etc.).
        makes_consequential_decisions: Triggers state AEDT/ADMT laws (CA CCPA,
            NYC AEDT, CO SB 26-189, CT SB 5).
        consumer_facing: User-visible AI interaction subject to disclosure
            laws (CA SB 942, NY chatbot rules).
        material_to_revenue: System failure would materially affect revenue or
            customer trust.

    Returns:
        The recommended Ribbon tier.
    """
    if any([handles_phi, is_samd, is_eu_high_risk_use_case, makes_consequential_decisions]):
        return RiskTier.CRITICAL
    if consumer_facing or material_to_revenue:
        return RiskTier.HIGH
    return RiskTier.MANAGED


__all__ = ["classify_system", "tier_color"]
