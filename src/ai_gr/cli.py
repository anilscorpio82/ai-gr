"""
ai_gr.cli — Command-line interface for the AI-GR reference implementation.

Subcommands:

    ai-gr keypair           Generate a new Ed25519 keypair.
    ai-gr verify <path>     Verify a chain on the filesystem.
    ai-gr inspect <path>    Pretty-print a single GPR entry.
    ai-gr regimes           List supported regulatory regimes.
    ai-gr export            Export a regulator-ready dossier.
    ai-gr demo              Run the bundled clinical-decision-support demo.

All subcommands are designed for use in CI pipelines and produce structured
output where possible.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ai_gr import __version__
from ai_gr.crypto import (
    ChainVerificationError,
    KeyPair,
    SignatureVerificationError,
    verify_chain,
)
from ai_gr.export import DossierFormat, export_dossier, multi_regime_dossier
from ai_gr.jsonld import from_jsonld_string
from ai_gr.regimes import list_regimes
from ai_gr.store import FilesystemStore

console = Console()


@click.group()
@click.version_option(__version__, prog_name="ai-gr")
def cli() -> None:
    """AI-GR — The Agentic Governance Ribbon. Reference CLI."""


# ----- keypair -----


@cli.command("keypair")
@click.option("--out", "out_path", type=click.Path(), default=None,
              help="Write the keypair to a JSON file instead of stdout.")
def cmd_keypair(out_path: str | None) -> None:
    """Generate a new Ed25519 keypair.

    WARNING: This command emits an unencrypted private key. For demonstration
    and testing only. In production, use an HSM or KMS.
    """
    kp = KeyPair.generate()
    payload = {"private_key_b64": kp.private_key_b64, "public_key_b64": kp.public_key_b64}
    if out_path:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote keypair to {out_path}[/green]")
    else:
        console.print_json(json.dumps(payload))


# ----- verify -----


@cli.command("verify")
@click.argument("store_path", type=click.Path(exists=True, file_okay=False))
@click.argument("system_urn", type=str)
@click.option("--skip-signatures", is_flag=True, help="Verify chain integrity only, skip signature checks.")
def cmd_verify(store_path: str, system_urn: str, skip_signatures: bool) -> None:
    """Verify a GPR chain on the filesystem.

    STORE_PATH is the root of the filesystem store.
    SYSTEM_URN is of the form 'urn:gpr:<org>/<system>'.
    """
    store = FilesystemStore(store_path)
    chain = store.chain_for(system_urn)
    if not chain:
        console.print(f"[red]No chain found for {system_urn}[/red]")
        sys.exit(2)

    console.print(f"Verifying chain for [bold]{system_urn}[/bold] ({len(chain)} entries)...")
    try:
        verify_chain(chain, verify_signatures=not skip_signatures)
    except (ChainVerificationError, SignatureVerificationError) as exc:
        console.print(f"[red]VERIFICATION FAILED:[/red] {exc}")
        sys.exit(1)

    console.print("[green]OK[/green] — chain is intact, signatures verify.")


# ----- inspect -----


@cli.command("inspect")
@click.argument("entry_path", type=click.Path(exists=True, dir_okay=False))
def cmd_inspect(entry_path: str) -> None:
    """Pretty-print a single GPR entry from a JSON-LD file."""
    text = Path(entry_path).read_text(encoding="utf-8")
    entry = from_jsonld_string(text)

    console.rule(f"[bold]{entry.id}[/bold]")
    console.print(f"Subject       : {entry.subject.system} v{entry.subject.version} ({entry.subject.type.value})")
    console.print(f"Gate          : {entry.gate.value}")
    console.print(f"Risk tier     : {entry.risk_tier.value}")
    console.print(f"Decision      : {entry.decision.value}")
    console.print(f"Approver      : {entry.authority.approver}")
    console.print(f"Scope         : {entry.authority.delegated_scope}")
    if entry.authority.co_approvers:
        console.print(f"Co-approvers  : {', '.join(entry.authority.co_approvers)}")
    console.print(f"Regimes       : {', '.join(c.regime for c in entry.regime) or '(none)'}")
    if entry.linkage.prev_gpr:
        console.print(f"Prev GPR      : {entry.linkage.prev_gpr}")
    if entry.attestation.signature:
        console.print(f"Signature     : {entry.attestation.signature[:40]}...")
    console.print(f"Content hash  : {entry.content_hash()}")
    console.rule()


# ----- regimes -----


@cli.command("regimes")
def cmd_regimes() -> None:
    """List supported regulatory regimes."""
    table = Table(title="Supported regimes", show_lines=True)
    table.add_column("Identifier", style="bold cyan")
    table.add_column("Name")
    table.add_column("Requirements", justify="right")
    for r in list_regimes():
        table.add_row(r.identifier, r.name, str(len(r.requirements())))
    console.print(table)


# ----- export -----


@cli.command("export")
@click.argument("store_path", type=click.Path(exists=True, file_okay=False))
@click.argument("system_urn", type=str)
@click.option("--regime", "regime_id", required=False,
              help="Regime identifier (e.g. 'EU-AI-Act'). Omit for multi-regime dossier.")
@click.option("--format", "fmt",
              type=click.Choice(["json", "markdown"]), default="json")
@click.option("--out", "out_path", type=click.Path(), default=None)
@click.option("--organization", default="Organization")
def cmd_export(
    store_path: str,
    system_urn: str,
    regime_id: str | None,
    fmt: str,
    out_path: str | None,
    organization: str,
) -> None:
    """Export a regulator-ready dossier for a GPR chain."""
    store = FilesystemStore(store_path)
    chain = store.chain_for(system_urn)
    if not chain:
        console.print(f"[red]No chain found for {system_urn}[/red]")
        sys.exit(2)

    if regime_id:
        output = export_dossier(
            chain, regime_id,
            format=DossierFormat(fmt),
            organization=organization,
        )
    else:
        output = multi_regime_dossier(chain, organization=organization)

    if out_path:
        Path(out_path).write_text(output, encoding="utf-8")
        console.print(f"[green]Wrote dossier to {out_path}[/green]")
    else:
        click.echo(output)


# ----- demo -----


@cli.command("demo")
@click.option("--out-dir", "out_dir", default="./demo-store",
              help="Directory to write the demo store to.")
def cmd_demo(out_dir: str) -> None:
    """Run the bundled clinical-decision-support demo end-to-end."""
    # The demo lives in the repo's examples/ directory, which is not part
    # of the installed package. Locate it relative to the package install.
    import sys
    from pathlib import Path

    # Walk up from this file to find the repo root (the dir containing 'examples/').
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parent.parent  # src/ai_gr -> src -> repo root
    examples_dir = repo_root / "examples"
    if not examples_dir.is_dir():
        console.print(
            "[red]Could not locate the bundled examples/ directory.[/red] "
            "The demo command is only available when running from a source checkout."
        )
        sys.exit(2)

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from examples.clinical_decision_support import (
        run as run_cds_demo,  # type: ignore[import-not-found]
    )

    chain = run_cds_demo(store_root=out_dir)
    console.print(f"[green]Demo complete.[/green] Wrote {len(chain)} entries to {out_dir}.")
    console.print(f"Verify with: [bold]ai-gr verify {out_dir} urn:gpr:acme-health/cds-agent[/bold]")
    console.print(f"Export EU AI Act dossier: [bold]ai-gr export {out_dir} urn:gpr:acme-health/cds-agent --regime EU-AI-Act[/bold]")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
