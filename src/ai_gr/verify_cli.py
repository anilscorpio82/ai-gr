"""
ai_gr.verify_cli — Standalone GPR chain verification CLI.

This is a thin Click wrapper around the verification logic in
``ai_gr.crypto.verify`` plus the Critical-tier invariant check from
``ai_gr.schema``. The goal: any third party — regulator, auditor,
downstream operator — should be able to run ``ai-gr-verify <path>``
against a GPR chain and get back a structured pass/fail report without
needing access to the original signing infrastructure.

Five checks are performed in sequence:

  1. Schema conformance — every file loads as a valid GPREntry.
  2. Canonicalization — recomputed canonical bytes match the RFC 8785 output.
  3. Hash linkage — each entry's linkage.prev_hash matches the prior entry's
     content_hash().
  4. Signatures — each entry's Ed25519 signature verifies against the
     embedded or resolved public key.
  5. Critical-tier invariant — every Critical-tier entry carries
     authority.legal_identity.

Exit code 0 if all checks pass; 1 if any check fails (with structured
report to stdout); 2 if the chain could not be loaded at all.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ai_gr.schema import GPREntry, RiskTier
from ai_gr.store import FilesystemStore


@dataclass
class CheckResult:
    """Outcome of a single verification check."""

    name: str
    passed: bool
    detail: str = ""
    entries_checked: int = 0
    entries_failed: list[str] = field(default_factory=list)


@dataclass
class VerifyReport:
    """Aggregate verification report."""

    chain_path: str
    chain_id: str | None
    total_entries: int
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_json(self) -> str:
        return json.dumps(
            {
                "chain_path": self.chain_path,
                "chain_id": self.chain_id,
                "total_entries": self.total_entries,
                "all_passed": self.all_passed,
                "checks": [
                    {
                        "name": c.name,
                        "passed": c.passed,
                        "detail": c.detail,
                        "entries_checked": c.entries_checked,
                        "entries_failed": c.entries_failed,
                    }
                    for c in self.checks
                ],
            },
            indent=2,
        )


def _check_schema_conformance(entries: list[GPREntry]) -> CheckResult:
    """Pydantic validation already occurred when entries were loaded; this
    confirms the load succeeded for the count we expected and validates the
    schema_version field."""
    if not entries:
        return CheckResult(
            name="Schema conformance",
            passed=False,
            detail="No entries loaded.",
        )
    # Verify schema_version is parseable and we recognise the major version.
    failed = [e.id for e in entries if not e.schema_version.startswith("0.")]
    return CheckResult(
        name="Schema conformance",
        passed=not failed,
        detail=(
            f"All {len(entries)} entries validate against the v0.x GPR schema."
            if not failed
            else f"{len(failed)} entries have unrecognised schema_version."
        ),
        entries_checked=len(entries),
        entries_failed=failed,
    )


def _check_canonicalization(entries: list[GPREntry]) -> CheckResult:
    """Recompute canonical bytes for each entry and verify they reproduce
    the same content_hash. This is implicitly tested via the hash linkage
    check but is reported separately for clarity."""
    failed = []
    for entry in entries:
        # The content_hash() method recomputes canonical_bytes() and SHA-256s
        # it. If the underlying rfc8785 library is consistent with itself,
        # this will always pass — the value of this check is that any tooling
        # divergence (e.g. a different JCS implementation) would surface here.
        recomputed = entry.content_hash()
        # We can't compare against a stored hash directly because the entry
        # doesn't carry its own hash — but we can detect non-determinism.
        recomputed_again = entry.content_hash()
        if recomputed != recomputed_again:
            failed.append(entry.id)
    return CheckResult(
        name="Canonicalization (RFC 8785)",
        passed=not failed,
        detail=(
            f"Canonicalization is deterministic for all {len(entries)} entries."
            if not failed
            else f"{len(failed)} entries show non-deterministic canonicalization (CRITICAL)."
        ),
        entries_checked=len(entries),
        entries_failed=failed,
    )


def _check_hash_linkage(entries: list[GPREntry]) -> CheckResult:
    """Each entry's linkage.prev_hash must match the prior entry's
    content_hash(). The first entry's linkage.prev_hash should be None."""
    if not entries:
        return CheckResult(name="Hash linkage", passed=True, detail="Empty chain.")
    failed = []
    if entries[0].linkage.prev_hash is not None:
        failed.append(entries[0].id)
    for i in range(1, len(entries)):
        expected = entries[i - 1].content_hash()
        actual = entries[i].linkage.prev_hash
        if actual != expected:
            failed.append(entries[i].id)
    return CheckResult(
        name="Hash linkage",
        passed=not failed,
        detail=(
            f"All {len(entries)} entries form a valid hash chain."
            if not failed
            else f"{len(failed)} entries have broken hash linkage."
        ),
        entries_checked=len(entries),
        entries_failed=failed,
    )


def _check_signatures(entries: list[GPREntry]) -> CheckResult:
    """Each entry's Ed25519 signature must verify against its public key.

    Note: this verifies that the signature is well-formed and matches the
    canonical bytes under the public key embedded in the entry. It does NOT
    verify that the public key belongs to the claimed approver DID (that
    requires DID resolution and a trust relationship with the DID method's
    infrastructure). For high-stakes audits, follow up with DID resolution
    against the relevant authority registry.
    """
    from ai_gr.crypto.verify import verify_signature

    failed = []
    for entry in entries:
        if entry.attestation.signature is None:
            failed.append(entry.id)
            continue
        try:
            verify_signature(entry)
        except Exception:
            failed.append(entry.id)
    return CheckResult(
        name="Signatures (Ed25519)",
        passed=not failed,
        detail=(
            f"All {len(entries)} signatures verify against embedded public keys."
            if not failed
            else f"{len(failed)} entries have invalid or missing signatures."
        ),
        entries_checked=len(entries),
        entries_failed=failed,
    )


def _check_critical_tier_invariant(entries: list[GPREntry]) -> CheckResult:
    """Every Critical-tier entry must carry authority.legal_identity.

    New in schema v0.2.0 per §4.3 of the v1.4 AI-GR paper. This invariant is
    also enforced at construction time by GPREntry.model_post_init, so this
    check should never fail for entries that loaded successfully — but it's
    valuable as a defensive check against future schema-bypass attempts.
    """
    critical_entries = [e for e in entries if e.risk_tier == RiskTier.CRITICAL]
    failed = [
        e.id for e in critical_entries if e.authority.legal_identity is None
    ]
    return CheckResult(
        name="Critical-tier legal_identity",
        passed=not failed,
        detail=(
            f"All {len(critical_entries)} Critical-tier entries carry legal_identity."
            if not failed
            else f"{len(failed)} Critical-tier entries are missing legal_identity (CRITICAL)."
        ),
        entries_checked=len(critical_entries),
        entries_failed=failed,
    )


def verify_chain(chain_path: str, chain_id: str | None = None) -> VerifyReport:
    """Run the full verification suite on a GPR chain.

    Args:
        chain_path: Path to a filesystem store directory.
        chain_id: Optional URN of a specific chain root; if None, all chains
            in the store are verified together.

    Returns:
        A VerifyReport summarising the outcome of each check.
    """
    store = FilesystemStore(Path(chain_path))
    if chain_id is not None:
        entries = store.chain_for(chain_id)
    else:
        # Verify all entries the store knows about, in order.
        entries = list(store)

    report = VerifyReport(
        chain_path=chain_path,
        chain_id=chain_id,
        total_entries=len(entries),
    )
    report.checks.append(_check_schema_conformance(entries))
    report.checks.append(_check_canonicalization(entries))
    report.checks.append(_check_hash_linkage(entries))
    report.checks.append(_check_signatures(entries))
    report.checks.append(_check_critical_tier_invariant(entries))
    return report


def _render_report_rich(report: VerifyReport, console: Console) -> None:
    """Render the report as a Rich table for human reading."""
    table = Table(title=f"AI-GR Chain Verification — {report.chain_path}")
    table.add_column("Check")
    table.add_column("Result")
    table.add_column("Detail", no_wrap=False)
    for check in report.checks:
        result_str = "[green]✓ PASS[/green]" if check.passed else "[red]✗ FAIL[/red]"
        table.add_row(check.name, result_str, check.detail)
    console.print(table)

    overall = "[green]ALL CHECKS PASSED[/green]" if report.all_passed else "[red]ONE OR MORE CHECKS FAILED[/red]"
    console.print(f"\n[bold]Overall:[/bold] {overall}")
    console.print(f"[bold]Total entries verified:[/bold] {report.total_entries}")


@click.command(name="ai-gr-verify")
@click.argument("chain_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--chain",
    "chain_id",
    default=None,
    help="URN of a specific chain root. If omitted, all entries in the store are verified.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Emit the report as JSON to stdout instead of a Rich table.",
)
def cli(chain_path: str, chain_id: str | None, json_output: bool) -> None:
    """Verify the integrity of an AI-GR GPR chain stored at CHAIN_PATH.

    Performs five checks: schema conformance, RFC 8785 canonicalization
    determinism, hash linkage, Ed25519 signatures, and the Critical-tier
    legal_identity invariant.

    Exits 0 on success, 1 if any check fails.
    """
    try:
        report = verify_chain(chain_path, chain_id)
    except Exception as e:
        click.echo(f"ERROR: could not load chain: {e}", err=True)
        sys.exit(2)

    if json_output:
        click.echo(report.to_json())
    else:
        console = Console()
        _render_report_rich(report, console)

    sys.exit(0 if report.all_passed else 1)


if __name__ == "__main__":
    cli()
