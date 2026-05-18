# OpenTelemetry Adapter

`ai_gr.adapters.otel` — OpenTelemetry export reference pattern.

!!! warning "Reference pattern, not production"
    This adapter demonstrates how an AI-GR deployment would emit OpenTelemetry events when GPR entries are created, signed, and verified, so that downstream observability and SIEM systems can ingest them.

## What this adapter provides

- **Canonical attribute names** for AI-GR OTel events, all namespaced under `ai_gr.*`.
- **`gpr_event_attributes(entry)`** — construct an OTel attribute dict from a `GPREntry`.
- **`verification_event_attributes(...)`** — construct attributes for a verification-result event.
- **`EXAMPLE_PIPELINE_SETUP`** — documented pipeline setup showing where the adapter slots into a typical OpenTelemetry SDK configuration.

## Canonical attribute names

| Attribute | Meaning |
|---|---|
| `ai_gr.gpr.id` | The GPR entry's URN |
| `ai_gr.gpr.gate` | The Ribbon gate |
| `ai_gr.gpr.risk_tier` | Critical, High, or Managed |
| `ai_gr.gpr.decision` | approve, approve_with_conditions, reject, rollback, defer |
| `ai_gr.gpr.content_hash` | SHA-256 of canonical bytes |
| `ai_gr.subject.system` | System name |
| `ai_gr.subject.version` | System version |
| `ai_gr.subject.type` | predictive, generative, agentic, hybrid |
| `ai_gr.authority.approver` | Approver DID |
| `ai_gr.authority.legal_identity.name` | Legal entity name (corporate names only; not PII) |
| `ai_gr.regime.count` | Number of regime claims on this entry |
| `ai_gr.verification.passed` | Did a verification check pass? |
| `ai_gr.verification.check` | Which check (schema, canonicalization, linkage, signatures, legal_identity) |

## PII exclusion

By default, `gpr_event_attributes()` **excludes**:
- `authority.legal_identity.contact_email` (may be personal data under GDPR)
- `authority.legal_identity.address` (may be personal data under GDPR)

The legal name of a **corporate entity** is not personal data, so it is included. If your `legal_identity.name` carries individual names rather than corporate names (e.g., for sole proprietorships), you should configure your OpenTelemetry pipeline to strip this attribute at the collector layer.

## Usage pattern

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from ai_gr.adapters.otel import gpr_event_attributes

# Configure the SDK once at startup (deployment-specific)
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="https://otel.example.com:4317"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("ai_gr")

# Emit an event for every signed GPR entry
def on_gpr_signed(entry):
    with tracer.start_as_current_span("ai_gr.gpr.emit") as span:
        span.set_attributes(gpr_event_attributes(entry))
```

## What this adapter does not do

- It does **not** configure the OpenTelemetry SDK pipeline. The caller is responsible for setting up the TracerProvider and Exporter appropriate to their backend.
- It does **not** handle backpressure, sampling, or error handling for high-rate GPR-emit scenarios.

## Installing

```bash
pip install -e ".[adapters]"
```

This installs `opentelemetry-api` and `opentelemetry-sdk` as optional dependencies. You still need the appropriate exporter for your observability backend (OTLP, Jaeger, etc.).
