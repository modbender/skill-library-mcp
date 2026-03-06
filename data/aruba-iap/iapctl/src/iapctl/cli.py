"""iapctl CLI - Aruba IAP Configuration Management."""
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from .operations import discover, snapshot, diff, apply, verify, rollback
from .monitor import monitor

app = typer.Typer(
    name="iapctl",
    help="Aruba IAP Configuration Management CLI",
    add_completion=False,
)

console = Console()


def print_result(result: dict, quiet: bool = False) -> None:
    """Print result in formatted way.

    Args:
        result: Result dictionary
        quiet: If True, only print success/failure
    """
    if quiet:
        console.print("✅ OK" if result["ok"] else "❌ FAILED")
        return

    # Print summary panel
    status = "✅ SUCCESS" if result["ok"] else "❌ FAILED"
    panel = Panel(
        f"{status}\n"
        f"Action: {result['action']}\n"
        f"Cluster: {result['cluster']}\n"
        f"VC: {result['vc']}\n"
        f"Duration: {result['timing']['total_seconds']:.2f}s",
        title="iapctl Result",
        border_style="green" if result["ok"] else "red",
    )
    console.print(panel)

    # Print warnings
    if result.get("warnings"):
        console.print("\n⚠️  Warnings:", style="yellow")
        for warning in result["warnings"]:
            console.print(f"  • {warning}", style="yellow")

    # Print errors
    if result.get("errors"):
        console.print("\n❌ Errors:", style="red")
        for error in result["errors"]:
            console.print(f"  • {error}", style="red")

    # Print artifacts
    if result.get("artifacts"):
        console.print("\n📦 Artifacts:", style="cyan")
        for artifact in result["artifacts"]:
            console.print(f"  • {artifact['name']}: {artifact['path']}")

    # Print checks
    if result.get("checks"):
        console.print("\n✓ Checks:", style="green")
        for check in result["checks"]:
            style = "green" if check["status"] == "pass" else "red"
            console.print(f"  • [{check['status']}] {check['name']}: {check['message']}", style=style)

    # Print full JSON if verbose
    if "--verbose" in sys.argv or "-v" in sys.argv:
        console.print("\n📄 Full Result JSON:", style="blue")
        console.print(JSON.from_data(result))


@app.command()
def discover_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Discover IAP cluster and gather basic information."""
    console.print(f"🔍 Discovering cluster '{cluster}' at {vc}...", style="blue")

    result_dict = discover(
        cluster=cluster,
        vc=vc,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def snapshot_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Take a full configuration snapshot of IAP cluster."""
    console.print(f"📸 Taking snapshot of cluster '{cluster}' at {vc}...", style="blue")

    result_dict = snapshot(
        cluster=cluster,
        vc=vc,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def diff_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    changes_file: Path = typer.Option(..., "--in", help="Changes JSON file"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    change_id: Optional[str] = typer.Option(None, "--change-id", help="Change ID (auto-generated if not provided)"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Generate diff between current config and desired changes."""
    console.print(f"🔍 Generating diff for cluster '{cluster}' at {vc}...", style="blue")

    result_dict = diff(
        cluster=cluster,
        vc=vc,
        changes_file=changes_file,
        out_dir=out,
        change_id=change_id,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def apply_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    change_id: str = typer.Option(..., "--change-id", help="Change ID for audit trail"),
    commands_file: Path = typer.Option(..., "--in", help="Commands JSON file"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode (don't apply changes)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Apply configuration changes."""
    console.print(f"⚙️  Applying changes to cluster '{cluster}' at {vc}...", style="blue")

    result_dict = apply(
        cluster=cluster,
        vc=vc,
        change_id=change_id,
        commands_file=commands_file,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
        dry_run=dry_run,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def verify_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    level: str = typer.Option("basic", "--level", help="Verification level (basic/full)"),
    expect_file: Optional[Path] = typer.Option(None, "--expect", help="Expected state file"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Verify configuration state."""
    console.print(f"✓ Verifying cluster '{cluster}' at {vc}...", style="blue")

    result_dict = verify(
        cluster=cluster,
        vc=vc,
        level=level,
        expect_file=expect_file,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def rollback_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    from_change_id: str = typer.Option(..., "--from-change-id", help="Change ID to rollback from"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Rollback to previous configuration."""
    console.print(f"⏪ Rolling back cluster '{cluster}' at {vc}...", style="blue")

    result_dict = rollback(
        cluster=cluster,
        vc=vc,
        from_change_id=from_change_id,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


@app.command()
def monitor_cmd(
    cluster: str = typer.Option(..., "--cluster", help="Cluster name"),
    vc: str = typer.Option(..., "--vc", help="Virtual controller IP address"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    ssh_host: Optional[str] = typer.Option(None, "--ssh-host", help="SSH host (default: vc)"),
    ssh_user: str = typer.Option("admin", "--ssh-user", help="SSH username"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password", help="SSH password"),
    ssh_port: int = typer.Option(22, "--ssh-port", help="SSH port"),
    ssh_config: Optional[Path] = typer.Option(None, "--ssh-config", help="SSH config file"),
    categories: Optional[list[str]] = typer.Option(None, "--categories", "-c", help="Monitor categories (default: all)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet output"),
) -> None:
    """Comprehensive IAP monitoring and telemetry collection.

    Categories (default: all):
    - system: System info (version, summary, clock, configuration)
    - ap: AP info (active, database, allowed-ap)
    - clients: Client info (clients, user-table, station-table)
    - wlan: WLAN info (ssid-profile, access-rule, auth-server)
    - rf: RF info (radio stats)
    - arm: ARM info (arm, band-steering, arm history)
    - advanced: Advanced features (client-match, DPI, IDS, Clarity)
    - wired: Wired/uplink info (ports, interfaces, routes)
    - logging: Logging info (syslog-level, logs)
    - security: Security info (blacklist, auth-tracebuf, snmp-server)

    Example:
        iapctl monitor --cluster office-iap --vc 192.168.20.56 --categories system ap clients
    """
    console.print(f"📊 Monitoring cluster '{cluster}' at {vc}...", style="blue")

    result_dict = monitor(
        cluster=cluster,
        vc=vc,
        out_dir=out,
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_port=ssh_port,
        ssh_config=ssh_config,
        categories=categories,
    ).model_dump()

    print_result(result_dict, quiet)

    # Exit with error code if failed
    if not result_dict["ok"]:
        raise typer.Exit(1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
