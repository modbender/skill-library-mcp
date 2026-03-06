#!/usr/bin/env python3
"""Smart ClawHub skill recommendations for OpenClaw."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.table import Table

from scripts.lib.clawhub_client import ClawHubClient
from scripts.lib.config_analyzer import ConfigAnalyzer
from scripts.lib.recommendation_engine import RecommendationEngine

console = Console()


@click.command()
@click.option("--channel", help="Filter by channel (whatsapp, telegram, discord, slack, etc.)")
@click.option("--use-case", help="Use case keyword (e.g., 'calendar', 'image generation')")
@click.option("--top", default=10, help="Number of results")
@click.option("--check-updates", is_flag=True, help="Check installed skills for updates")
@click.option("--auto-detect", is_flag=True, help="Auto-detect channels from config and recommend")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def main(channel, use_case, top, check_updates, auto_detect, json_output):
    """ClawHub Skill Recommendation System."""
    engine = RecommendationEngine()
    client = ClawHubClient()

    # Check updates mode
    if check_updates:
        console.print("[bold]Checking for skill updates...[/bold]\n")
        updates = engine.check_updates()

        if not updates:
            console.print("[green]All skills are up to date![/green]")
            return

        if json_output:
            data = [
                {
                    "slug": inst.slug,
                    "current_version": inst.version,
                    "latest_version": latest.version
                }
                for inst, latest in updates
            ]
            console.print_json(data=data)
            return

        table = Table(title="Skills with Available Updates")
        table.add_column("Skill", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Latest", style="green")
        table.add_column("Update Command", style="dim")

        for inst, latest in updates:
            table.add_row(
                inst.name,
                inst.version,
                latest.version,
                f"clawhub update {inst.slug}"
            )

        console.print(table)
        return

    # Auto-detect mode
    if auto_detect:
        console.print("[bold]Auto-detecting channels and generating recommendations...[/bold]\n")
        recommendations = engine.suggest_for_config()
    else:
        # Manual search mode
        recommendations = engine.recommend(channel=channel, use_case=use_case, top=top)

    if not recommendations:
        console.print("[yellow]No recommendations found. Try different search criteria.[/yellow]")
        return

    # JSON output
    if json_output:
        data = [
            {
                "rank": i + 1,
                "slug": rec.skill.slug,
                "name": rec.skill.name,
                "score": rec.score,
                "description": rec.skill.description,
                "verified": rec.skill.verified,
                "downloads": rec.skill.downloads,
                "reasons": rec.reasons
            }
            for i, rec in enumerate(recommendations)
        ]
        console.print_json(data=data)
        return

    # Rich table output
    cache_status = "[green]fresh[/green]" if client._is_cache_fresh() else "[yellow]stale[/yellow]"
    table = Table(
        title=f"Recommended Skills (cache: {cache_status})",
        show_header=True,
        header_style="bold magenta"
    )

    table.add_column("Rank", justify="right", style="cyan", width=4)
    table.add_column("Skill", style="bold")
    table.add_column("Score", justify="right", style="yellow", width=6)
    table.add_column("Description")
    table.add_column("Install Command", style="dim")

    for i, rec in enumerate(recommendations, 1):
        verified_badge = " [green]✓[/green]" if rec.skill.verified else ""
        score_str = f"{rec.score:.1f}"

        # Truncate description
        desc = rec.skill.description
        if len(desc) > 50:
            desc = desc[:47] + "..."

        table.add_row(
            str(i),
            f"{rec.skill.name}{verified_badge}",
            score_str,
            desc,
            f"clawhub install {rec.skill.slug}"
        )

    console.print(table)

    # Show reasons for top 3
    if not json_output:
        console.print("\n[bold]Top Recommendations Reasoning:[/bold]")
        for i, rec in enumerate(recommendations[:3], 1):
            console.print(f"\n[cyan]{i}. {rec.skill.name}[/cyan] (score: {rec.score:.1f})")
            for reason in rec.reasons:
                console.print(f"   • {reason}")

    # Cache refresh hint
    if not client._is_cache_fresh():
        console.print("\n[dim]Hint: Run 'clawhub refresh' to update skill cache[/dim]")


if __name__ == "__main__":
    main()
