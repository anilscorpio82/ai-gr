"""
ai_gr.adapters.otel — OpenTelemetry export reference pattern.

**This is a reference pattern, not a production-grade integration.** It
demonstrates how an AI-GR deployment would emit OpenTelemetry events when
GPR entries are created, signed, and verified, so that downstream
observability and SIEM systems can ingest them.

What this module does:
  - Defines the canonical OTel attribute names AI-GR uses for GPR events.
  - Provides a helper to construct an OTel span event payload from a
    GPREntry.
  - Provides a helper for emitting verification-result events.

What this module does NOT do:
  - It does not configure an OpenTelemetry SDK pipeline. The caller is
    responsible for setting up the TracerProvider and Exporter appropriate
    to their observability backend.
  - It does not handle backpressure, sampling, or error handling for
    high-rate GPR-emit scenarios.

For production deployments:
  - https://opentelemetry.io/docs/languages/python/
  - Set up the SDK with the exporter for your backend (OTLP, Jaeger, etc.).
  - Inject the tracer and call ``emit_gpr_event(tracer, entry)``.

Optional dependency: install with ``pip install -e ".[adapters]"``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ai_gr.schema import GPREntry

# Canonical attribute names. These are namespaced under ``ai_gr.*`` to avoid
# collision with caller-defined attributes.
ATTR_GPR_ID = "ai_gr.gpr.id"
ATTR_GPR_GATE = "ai_gr.gpr.gate"
ATTR_GPR_RISK_TIER = "ai_gr.gpr.risk_tier"
ATTR_GPR_DECISION = "ai_gr.gpr.decision"
ATTR_GPR_CONTENT_HASH = "ai_gr.gpr.content_hash"
ATTR_SUBJECT_SYSTEM = "ai_gr.subject.system"
ATTR_SUBJECT_VERSION = "ai_gr.subject.version"
ATTR_SUBJECT_TYPE = "ai_gr.subject.type"
ATTR_AUTHORITY_APPROVER = "ai_gr.authority.approver"
ATTR_AUTHORITY_LEGAL_IDENTITY_NAME = "ai_gr.authority.legal_identity.name"
ATTR_REGIME_COUNT = "ai_gr.regime.count"
ATTR_VERIFICATION_PASSED = "ai_gr.verification.passed"
ATTR_VERIFICATION_CHECK = "ai_gr.verification.check"


def gpr_event_attributes(entry: GPREntry) -> dict[str, Any]:
    """Build the canonical attribute dict for a GPR-emit OTel event.

    Pass this to ``span.add_event("ai_gr.gpr.created", attributes=...)`` or
    ``tracer.start_as_current_span("ai_gr.gpr.emit", attributes=...)``.

    Note: this function does not include any personal-data-bearing fields.
    Specifically, ``authority.legal_identity.contact_email`` is omitted
    because it could be personal data subject to GDPR; only the legal name
    (which for corporate entities is not personal data) is included.
    """
    attrs: dict[str, Any] = {
        ATTR_GPR_ID: entry.id,
        ATTR_GPR_GATE: entry.gate.value,
        ATTR_GPR_RISK_TIER: entry.risk_tier.value,
        ATTR_GPR_DECISION: entry.decision.value,
        ATTR_GPR_CONTENT_HASH: entry.content_hash(),
        ATTR_SUBJECT_SYSTEM: entry.subject.system,
        ATTR_SUBJECT_VERSION: entry.subject.version,
        ATTR_SUBJECT_TYPE: entry.subject.type.value,
        ATTR_AUTHORITY_APPROVER: entry.authority.approver,
        ATTR_REGIME_COUNT: len(entry.regime),
    }
    if entry.authority.legal_identity is not None:
        # The legal name of a corporate entity is not personal data; the
        # contact_email and address may be, so they are omitted from the
        # observability stream by default.
        attrs[ATTR_AUTHORITY_LEGAL_IDENTITY_NAME] = entry.authority.legal_identity.name
    return attrs


def verification_event_attributes(
    *, check_name: str, passed: bool, entries_checked: int, entries_failed: list[str]
) -> dict[str, Any]:
    """Build the attribute dict for a verification-result OTel event."""
    return {
        ATTR_VERIFICATION_CHECK: check_name,
        ATTR_VERIFICATION_PASSED: passed,
        "ai_gr.verification.entries_checked": entries_checked,
        "ai_gr.verification.entries_failed_count": len(entries_failed),
    }


# ---------------------------------------------------------------------------
# A worked example of pipeline setup. Not exercised by AI-GR's own code; the
# caller is expected to set up their own pipeline. Reproduced here as
# documentation only.
# ---------------------------------------------------------------------------
EXAMPLE_PIPELINE_SETUP = '''
# Example pipeline setup for an AI-GR deployment using OpenTelemetry.
# This is documentation, not executable code in ai_gr.adapters.otel.

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from ai_gr.adapters.otel import gpr_event_attributes

# 1. Configure the SDK (deployment-specific).
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="https://otel.example.com:4317"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("ai_gr")

# 2. Emit an event for every signed GPR entry.
def on_gpr_signed(entry):
    with tracer.start_as_current_span("ai_gr.gpr.emit") as span:
        span.set_attributes(gpr_event_attributes(entry))
        # span.add_event("ai_gr.gpr.signed")  # Optional fine-grained event
'''
