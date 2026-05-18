"""
ai_gr.adapters.opa — Open Policy Agent integration reference pattern.

**This is a reference pattern, not a production-grade integration.** It
demonstrates how an AI-GR deployment would enforce capability-scope policy
decisions using OPA (Open Policy Agent), and how to translate an OPA
decision into a GPR ``authority.delegated_scope`` value.

What this module does:
  - Defines the wire shape for an OPA decision request and response.
  - Provides a helper to construct an OPA input document from an
    ``Authority`` and a requested capability.
  - Provides a helper to translate an OPA "allow"/"deny" decision into a
    GPR ``decision`` field value.

What this module does NOT do:
  - It does not make actual HTTP requests to an OPA sidecar or remote OPA
    server. ``build_opa_request()`` returns the request body; the caller
    makes the HTTP call.
  - It does not embed Rego policies. Policies are deployment-specific and
    are expected to be authored by the operator's policy team.
  - It does not handle bundle service authentication, policy hot-reload,
    or decision logging.

For production deployments:
  - https://www.openpolicyagent.org/docs/latest/integration/
  - Run OPA as a sidecar with the REST API enabled, and use the
    ``/v1/data/<package>/<rule>`` endpoint pattern from build_opa_request().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OpaDecision:
    """The outcome of an OPA policy evaluation."""

    allowed: bool
    reasons: tuple[str, ...] = ()
    """Human-readable reasons for the decision (populated by the policy if it returns metadata)."""

    raw_response: dict[str, Any] | None = None
    """The raw OPA response body, for audit storage in evidence.additional."""


def build_opa_request(
    *,
    approver_did: str,
    requested_capability: str,
    risk_tier: str,
    gate: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct the OPA decision request body for an AI-GR authorization check.

    The shape below assumes a Rego policy package called ``ai_gr.authority``
    with a rule ``allow``. Adapt to the deployment's actual policy structure.

    Args:
        approver_did: DID of the approver requesting authorization.
        requested_capability: Capability string (e.g. ``"tier:critical;phi:read"``).
        risk_tier: Risk tier of the system being governed.
        gate: Ribbon gate at which authorization is being requested.
        context: Additional context attributes the policy may need.

    Returns:
        A dict with ``url`` (the OPA endpoint to POST to) and ``body`` (the
        request body to send as JSON).
    """
    return {
        "url": "/v1/data/ai_gr/authority/allow",
        "body": {
            "input": {
                "approver_did": approver_did,
                "requested_capability": requested_capability,
                "risk_tier": risk_tier,
                "gate": gate,
                "context": context or {},
            }
        },
    }


def parse_opa_response(response_body: dict[str, Any]) -> OpaDecision:
    """Translate an OPA REST response into an ``OpaDecision``.

    Assumes the policy returns either a boolean (``true``/``false``) or an
    object of the shape ``{"allow": bool, "reasons": [str, ...]}``.
    """
    result = response_body.get("result")
    if isinstance(result, bool):
        return OpaDecision(allowed=result, raw_response=response_body)
    if isinstance(result, dict):
        allowed = bool(result.get("allow", False))
        reasons_field = result.get("reasons", [])
        reasons = tuple(str(r) for r in reasons_field)
        return OpaDecision(allowed=allowed, reasons=reasons, raw_response=response_body)
    return OpaDecision(allowed=False, reasons=("opa returned unexpected shape",), raw_response=response_body)


# An example Rego policy fragment showing the shape callers should write.
# This is a docstring, not executable code — it documents the expected
# OPA-side contract.
EXAMPLE_REGO_POLICY = '''
package ai_gr.authority

import future.keywords.if
import future.keywords.in

default allow := false

# Critical-tier approvals require co-approver(s) at Conceive and Build.
allow if {
    input.risk_tier == "Critical"
    input.gate in {"Conceive", "Build"}
    has_co_approver
    has_required_scope
}

# Managed-tier approvals at Operate gate proceed without co-approver.
allow if {
    input.risk_tier == "Managed"
    input.gate == "Operate"
    has_required_scope
}

has_co_approver if {
    input.context.co_approvers
    count(input.context.co_approvers) >= 1
}

has_required_scope if {
    # Implementation depends on capability-scope syntax in use.
    startswith(input.requested_capability, "tier:")
}
'''
