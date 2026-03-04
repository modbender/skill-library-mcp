#!/usr/bin/env python3
"""Self-update checker and executor for OpenClaw Doctor Pro."""
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

from scripts.lib.clawhub_client import ClawHubClient
from scripts.lib.doc_fetcher import DocFetcher
from scripts.lib.utils import which_binary

console = Console()


@click.command()
@click.option("--check", is_flag=True, help="Check what's outdated without updating")
@click.option("--update", is_flag=True, help="Fetch and apply updates")
@click.option("--docs-only", is_flag=True, help="Only update documentation references")
@click.option("--skills-only", is_flag=True, help="Only update skill cache")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def main(check, update, docs_only, skills_only, json_output):
    """OpenClaw Self-Update Management Tool."""
    doc_fetcher = DocFetcher()
    clawhub = ClawHubClient()

    # Check mode (default if no flags)
    if check or (not update and not docs_only and not skills_only):
        console.print("[bold]Checking for updates...[/bold]\n")

        status_data = {}

        # Check OpenClaw version
        version_info = doc_fetcher.get_version_info()
        status_data["openclaw"] = version_info

        # Check ClawHub CLI
        clawhub_available = which_binary("clawhub") is not None
        status_data["clawhub_cli"] = {"available": clawhub_available}

        # Check docs reachability
        docs_reachable = doc_fetcher.check_reachability()
        status_data["docs"] = {"reachable": docs_reachable}

        # Check cache freshness
        cache_fresh = clawhub._is_cache_fresh()
        status_data["cache"] = {"fresh": cache_fresh}

        if json_output:
            console.print_json(data=status_data)
            return

        # Display status table
        table = Table(title="Update Status", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Latest", style="green")
        table.add_column("Status")

        # OpenClaw version
        update_badge = "[red]UPDATE AVAILABLE[/red]" if version_info["update_available"] else "[green]✓ Up to date[/green]"
        table.add_row(
            "OpenClaw",
            version_info["current"],
            version_info["latest"],
            update_badge
        )

        # ClawHub CLI
        cli_status = "[green]✓ Installed[/green]" if clawhub_available else "[red]✗ Not found[/red]"
        table.add_row("ClawHub CLI", "-", "-", cli_status)

        # Docs
        docs_status = "[green]✓ Reachable[/green]" if docs_reachable else "[yellow]⚠ Unreachable[/yellow]"
        table.add_row("Documentation", "-", "-", docs_status)

        # Cache
        cache_status = "[green]✓ Fresh[/green]" if cache_fresh else "[yellow]⚠ Stale[/yellow]"
        table.add_row("Skill Cache", "-", "-", cache_status)

        console.print(table)

        # Show update command if available
        if version_info["update_available"]:
            console.print("\n[bold yellow]To update OpenClaw:[/bold yellow]")
            console.print("  npm install -g openclaw@latest")

        return

    # Update mode
    if update or docs_only or skills_only:
        updates = []

        # Update docs
        if (update and not skills_only) or docs_only:
            console.print("[bold]Updating documentation...[/bold]")
            success, new_count = doc_fetcher.update_error_patterns()
            if success and new_count > 0:
                updates.append(f"Added {new_count} new error patterns from docs")
                console.print(f"[green]✓[/green] Added {new_count} new error patterns")
            elif success:
                console.print("[green]✓[/green] Documentation already up to date")
            else:
                console.print("[yellow]⚠[/yellow] Could not fetch documentation updates")

        # Update skill cache
        if (update and not docs_only) or skills_only:
            console.print("\n[bold]Refreshing skill cache...[/bold]")
            if clawhub.is_cli_available():
                if clawhub.refresh_cache():
                    updates.append("Refreshed ClawHub skill cache")
                    console.print("[green]✓[/green] Skill cache refreshed")
                else:
                    console.print("[yellow]⚠[/yellow] Could not refresh skill cache")
            else:
                console.print("[red]✗[/red] ClawHub CLI not available")

        # Update summary
        if updates:
            panel = Panel(
                "\n".join(f"• {u}" for u in updates),
                title="[bold green]Update Summary[/bold green]",
                border_style="green"
            )
            console.print("\n")
            console.print(panel)
        else:
            console.print("\n[yellow]No updates applied[/yellow]")


if __name__ == "__main__":
    main()
