#!/usr/bin/env python3
"""Extended diagnostics CLI for OpenClaw."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scripts.lib.config_analyzer import ConfigAnalyzer
from scripts.lib.error_database import ErrorDatabase
from scripts.lib.error_parser import ErrorParser
from scripts.lib.system_checks import (
    check_disk_space,
    check_docker,
    check_network_connectivity,
    check_node_version,
    check_port_available,
    check_binary,
)
from scripts.lib.utils import DEFAULT_PORT, OPENCLAW_DIR, check_mark

console = Console()


@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--report", is_flag=True, help="Generate full diagnostic report file")
@click.option("--deep", is_flag=True, help="Run deep diagnostics including log analysis")
def main(json_output, report, deep):
    """OpenClaw Extended Diagnostics Tool."""
    results = {"system": {}, "network": {}, "gateway": {}, "config": {}, "channels": {}, "disk": {}, "errors": []}

    # System requirements
    console.print("[bold]System Requirements:[/bold]")
    sys_table = Table(show_header=False)
    sys_table.add_column("Check", style="cyan")
    sys_table.add_column("Status")
    sys_table.add_column("Details")

    node_ok, node_ver = check_node_version()
    sys_table.add_row("Node.js (>=22)", check_mark(node_ok), node_ver)
    results["system"]["nodejs"] = {"ok": node_ok, "version": node_ver}

    for name, key in [("pnpm", "pnpm"), ("openclaw CLI", "openclaw"), ("clawhub CLI", "clawhub"), ("git", "git")]:
        ok = check_binary(key)
        sys_table.add_row(name, check_mark(ok), "Installed" if ok else "Not found")
        results["system"][key] = {"ok": ok}

    docker_ok, docker_msg = check_docker()
    sys_table.add_row("docker", check_mark(docker_ok), docker_msg)
    results["system"]["docker"] = {"ok": docker_ok, "message": docker_msg}

    console.print(sys_table)
    console.print()

    # Network
    console.print("[bold]Network Connectivity:[/bold]")
    net_table = Table(show_header=False)
    net_table.add_column("Endpoint", style="cyan")
    net_table.add_column("Status")

    for endpoint, key in [("api.anthropic.com:443", "anthropic"), ("api.openai.com:443", "openai")]:
        ok = check_network_connectivity(endpoint.split(":")[0])
        net_table.add_row(endpoint, check_mark(ok))
        results["network"][key] = ok

    console.print(net_table)
    console.print()

    # Gateway
    console.print("[bold]Gateway Status:[/bold]")
    gw_table = Table(show_header=False)
    gw_table.add_column("Check", style="cyan")
    gw_table.add_column("Status")
    gw_table.add_column("Details")

    port_used, port_msg = check_port_available(DEFAULT_PORT)
    gw_table.add_row(f"Port {DEFAULT_PORT}", check_mark(port_used), port_msg)
    results["gateway"]["port"] = {"used": port_used, "message": port_msg}

    console.print(gw_table)
    console.print()

    # Config
    console.print("[bold]Configuration:[/bold]")
    analyzer = ConfigAnalyzer()
    issues = analyzer.analyze()

    if issues:
        config_table = Table()
        config_table.add_column("Severity", style="yellow")
        config_table.add_column("Path", style="cyan")
        config_table.add_column("Message")

        for issue in issues[:10]:
            severity_color = "red" if issue.severity == "error" else "yellow"
            config_table.add_row(f"[{severity_color}]{issue.severity.upper()}[/{severity_color}]", issue.path, issue.message)

        console.print(config_table)
        results["config"]["issues"] = [{"severity": i.severity, "path": i.path, "message": i.message} for i in issues]
    else:
        console.print("[green]✓ Configuration valid[/green]")
        results["config"]["issues"] = []

    console.print()

    # Channels
    console.print("[bold]Channel Credentials:[/bold]")
    enabled_channels = analyzer.detect_channels()
    if enabled_channels:
        for channel in enabled_channels:
            console.print(f"[green]✓ {channel} enabled[/green]")
        results["channels"] = {ch: "enabled" for ch in enabled_channels}
    else:
        console.print("[yellow]No channels enabled[/yellow]")
        results["channels"] = {}
    console.print()

    # Disk
    console.print("[bold]Disk Space:[/bold]")
    total, used, free = check_disk_space(OPENCLAW_DIR)
    console.print(f"~/.openclaw: {free} GB free of {total} GB")
    results["disk"] = {"total_gb": total, "used_gb": used, "free_gb": free}
    console.print()

    # Deep diagnostics
    if deep:
        console.print("[bold]Deep Diagnostics (Log Analysis):[/bold]")
        log_files = list(OPENCLAW_DIR.glob("logs/*.log"))

        if log_files:
            parser = ErrorParser()
            all_errors = []

            for log_file in log_files[:3]:
                errors = parser.parse_log_file(log_file)
                all_errors.extend(errors[-10:])

            if all_errors:
                error_table = Table()
                error_table.add_column("Timestamp", style="dim")
                error_table.add_column("Code", style="red")
                error_table.add_column("Message")

                for err in all_errors[:20]:
                    msg = err.error_message[:60] + "..." if len(err.error_message) > 60 else err.error_message
                    error_table.add_row(err.timestamp or "N/A", err.error_code or "UNKNOWN", msg)

                console.print(error_table)
                results["errors"] = [{"timestamp": e.timestamp, "code": e.error_code, "message": e.error_message} for e in all_errors[:20]]
            else:
                console.print("[green]✓ No recent errors found[/green]")
        else:
            console.print("[yellow]No log files found[/yellow]")
        console.print()

    # Summary
    passed = sum([node_ok, check_binary("pnpm"), check_binary("openclaw"), check_binary("git"), port_used])
    warnings = 2 - sum([check_binary("clawhub"), docker_ok])
    failures = 6 - passed

    console.print(Panel(f"[bold]Summary:[/bold] {passed} passed, {warnings} warnings, {failures} failures", border_style="green" if failures == 0 else "yellow"))

    results["summary"] = {"passed": passed, "warnings": warnings, "failures": failures}

    if json_output:
        console.print_json(data=results)

    if report:
        print(f"# OpenClaw Diagnostic Report\n\n## Summary\n- Passed: {passed}\n- Warnings: {warnings}\n- Failures: {failures}\n")


if __name__ == "__main__":
    main()
