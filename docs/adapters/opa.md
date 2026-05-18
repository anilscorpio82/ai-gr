# OPA Adapter

`ai_gr.adapters.opa` — Open Policy Agent integration reference pattern.

!!! warning "Reference pattern, not production"
    This adapter demonstrates how an AI-GR deployment would enforce capability-scope policy decisions using OPA, and how to translate an OPA decision into a GPR `authority.delegated_scope` value. Production deployments must add error handling, retries, real endpoint configuration, and policy bundle authentication.

## What this adapter provides

- **`build_opa_request(...)`** — construct the OPA decision request body for an authorization check.
- **`parse_opa_response(body)`** — translate an OPA REST response into a typed `OpaDecision`.
- **`OpaDecision`** — typed result with `allowed`, `reasons`, and `raw_response` fields.
- **`EXAMPLE_REGO_POLICY`** — a documented Rego policy fragment showing the expected OPA-side contract.

## Wire shape

```python
from ai_gr.adapters.opa import build_opa_request, parse_opa_response

# 1. Construct the request body
req = build_opa_request(
    approver_did="did:web:acme-health:caio",
    requested_capability="tier:critical;phi:read",
    risk_tier="Critical",
    gate="Build",
    context={"co_approvers": ["did:web:acme-health:ciso"]},
)

# req == {"url": "/v1/data/ai_gr/authority/allow", "body": {"input": {...}}}

# 2. Caller makes the HTTP call
import requests
response = requests.post(f"http://opa:8181{req['url']}", json=req["body"])

# 3. Parse the response
decision = parse_opa_response(response.json())
if not decision.allowed:
    raise PermissionError(f"OPA denied: {decision.reasons}")
```

## Expected Rego policy contract

The `build_opa_request()` function assumes a Rego policy package called `ai_gr.authority` with a rule `allow`. Adapt to your deployment's actual policy structure.

```rego
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
    startswith(input.requested_capability, "tier:")
}
```

The full example Rego is available in the module as `EXAMPLE_REGO_POLICY`.

## What this adapter does not do

- It does **not** make HTTP requests to OPA.
- It does **not** embed Rego policies. Policies are deployment-specific.
- It does **not** handle bundle service authentication, policy hot-reload, or decision logging.

## Installing

```bash
pip install -e ".[adapters]"
```

Run OPA as a sidecar with the REST API enabled. See [the OPA REST API docs](https://www.openpolicyagent.org/docs/latest/rest-api/) for deployment guidance.
