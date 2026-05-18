"""
ai_gr.adapters — Reference-pattern integration adapters.

This subpackage provides reference-pattern adapters for the most common
surrounding tools that an AI-GR deployment integrates with:

  - ``ai_gr.adapters.sigstore`` — Sigstore Cosign + Rekor for signed model
    artifact attestation.
  - ``ai_gr.adapters.opa`` — Open Policy Agent for capability-scope policy
    enforcement.
  - ``ai_gr.adapters.otel`` — OpenTelemetry for downstream observability
    and SIEM integration.

**IMPORTANT — these are reference patterns, not production-grade
integrations.** They demonstrate the wire-level interface and the
integration shape, but they assume callers will add error handling,
retries, real endpoint configuration, credential management, and
production observability before use in regulated deployments. Read each
module's docstring for a clear statement of what is and is not
implemented.

To install the optional dependencies that these adapters require::

    pip install -e ".[adapters]"

If the optional dependencies are not present, each adapter module will
raise an ``ImportError`` at first use with a clear message pointing to
the install command above.
"""
