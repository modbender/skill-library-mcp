"""CLI interface for tokenmeter."""

import typer
from typing import Optional, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import __version__
from .pricing import calculate_cost, get_pricing, list_supported_models
from .db import log_usage, get_summary, get_model_breakdown, get_usage
from .importer import import_sessions, find_session_dirs
from .time_utils import resolve_time_range
from .fetcher import scan_env_vars, fetch_provider, fetch_all

app = typer.Typer(
    name="tokenmeter",
    help="Track your AI API usage and costs across all providers — locally, privately.",
    no_args_is_help=True,
)
console = Console()


def format_tokens(n: int) -> str:
    """Format token count with K/M suffixes."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_cost(cost: float) -> str:
    """Format cost in dollars."""
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


@app.command()
def log(
    provider: str = typer.Option(..., "--provider", "-p", help="Provider (anthropic, openai, google, azure)"),
    model: str = typer.Option(..., "--model", "-m", help="Model name"),
    input_tokens: int = typer.Option(..., "--input", "-i", help="Input tokens"),
    output_tokens: int = typer.Option(..., "--output", "-o", help="Output tokens"),
    app_name: Optional[str] = typer.Option(None, "--app", "-a", help="Application name"),
):
    """Log a usage event manually."""
    cost = calculate_cost(provider, model, input_tokens, output_tokens)
    
    pricing = get_pricing(provider, model)
    if not pricing:
        console.print(f"[yellow]⚠️  Unknown model {provider}/{model} - cost set to $0[/yellow]")
    
    record_id = log_usage(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        source="manual",
        app=app_name,
    )
    
    console.print(f"[green]✓[/green] Logged usage #{record_id}")
    console.print(f"  Provider: {provider}")
    console.print(f"  Model: {model}")
    console.print(f"  Tokens: {format_tokens(input_tokens)} in / {format_tokens(output_tokens)} out")
    console.print(f"  Cost: [bold]{format_cost(cost)}[/bold]")


@app.command()
def summary(
    period: Optional[str] = typer.Option(None, "--period", "-p", help="Time period (day, week, month)"),
    since: Optional[str] = typer.Option(None, "--since", help="Start time (e.g., '9am', 'yesterday', '2026-02-06 09:00')"),
    after: Optional[str] = typer.Option(None, "--after", help="Start time (alias for --since)"),
    between: Optional[List[str]] = typer.Option(None, "--between", help="Time range (e.g., '9am' '5pm')"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Filter by provider"),
    exclude_zero_cost: bool = typer.Option(False, "--exclude-zero-cost", help="Exclude records with zero cost"),
    min_cost: Optional[float] = typer.Option(None, "--min-cost", help="Minimum cost threshold"),
):
    """Show usage summary."""
    try:
        start, end = resolve_time_range(
            period=period or "day",
            since=since,
            after=after,
            between=tuple(between) if between and len(between) == 2 else None,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    console.print()
    data = _render_summary_table(start=start, end=end, provider=provider, min_cost=min_cost, exclude_zero_cost=exclude_zero_cost)
    
    if data["totals"]["requests"] == 0:
        console.print("\n[dim]No usage recorded for this period. Use 'tokenmeter log' to add records.[/dim]")
    elif data.get("excluded_count", 0) > 0:
        console.print(f"\n[dim]({data['excluded_count']} zero-cost records excluded)[/dim]")
    console.print()


@app.command()
def costs(
    period: Optional[str] = typer.Option(None, "--period", "-p", help="Time period (day, week, month)"),
    since: Optional[str] = typer.Option(None, "--since", help="Start time (e.g., '9am', 'yesterday')"),
    after: Optional[str] = typer.Option(None, "--after", help="Start time (alias for --since)"),
    between: Optional[List[str]] = typer.Option(None, "--between", help="Time range (e.g., '9am' '5pm')"),
    exclude_zero_cost: bool = typer.Option(False, "--exclude-zero-cost", help="Exclude records with zero cost"),
    min_cost: Optional[float] = typer.Option(None, "--min-cost", help="Minimum cost threshold"),
):
    """Show cost breakdown by model."""
    try:
        start, end = resolve_time_range(
            period=period or "day",
            since=since,
            after=after,
            between=tuple(between) if between and len(between) == 2 else None,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    data = get_model_breakdown(start=start, end=end, min_cost=min_cost, exclude_zero_cost=exclude_zero_cost)
    
    # Generate label
    if start and end:
        period_label = f"{start.strftime('%m/%d %H:%M')} - {end.strftime('%m/%d %H:%M')}"
    elif start:
        period_label = f"since {start.strftime('%m/%d %H:%M')}"
    else:
        period_label = {"day": "today", "week": "this week", "month": "this month"}.get(period or "day", period or "day")
    
    table = Table(
        title=f"💰 Cost Breakdown — {period_label}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Model", style="bold")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("% of Total", justify="right")
    
    total_cost = sum(m["cost"] for m in data["models"])
    
    # Sort by cost descending
    for model in sorted(data["models"], key=lambda x: x["cost"], reverse=True):
        pct = (model["cost"] / total_cost * 100) if total_cost > 0 else 0
        table.add_row(
            f"{model['provider']}/{model['model']}",
            format_tokens(model["input_tokens"]),
            format_tokens(model["output_tokens"]),
            format_cost(model["cost"]),
            f"{pct:.1f}%",
        )
    
    console.print()
    console.print(table)
    
    if not data["models"]:
        console.print("\n[dim]No usage recorded. Use 'tokenmeter log' to add records.[/dim]")
    elif data.get("excluded_count", 0) > 0:
        console.print(f"\n[dim]({data['excluded_count']} zero-cost records excluded)[/dim]")
    console.print()


@app.command()
def models():
    """List supported models and their pricing."""
    table = Table(
        title="📋 Supported Models & Pricing",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column("Model")
    table.add_column("Input ($/1M)", justify="right", style="yellow")
    table.add_column("Output ($/1M)", justify="right", style="green")
    
    current_provider = None
    for provider, model in list_supported_models():
        pricing = get_pricing(provider, model)
        if pricing:
            # Add section between providers
            if current_provider and provider != current_provider:
                table.add_section()
            current_provider = provider
            
            table.add_row(
                provider.capitalize(),
                pricing.model,
                f"${pricing.input_per_1m:.2f}",
                f"${pricing.output_per_1m:.2f}",
            )
    
    console.print()
    console.print(table)
    console.print()


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of records to show"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """Show recent usage history."""
    records = get_usage(provider=provider)[:limit]
    
    table = Table(
        title="📜 Recent Usage",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Time", style="dim")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Source", style="dim")
    
    for r in records:
        table.add_row(
            r.timestamp.strftime("%m/%d %H:%M"),
            r.provider,
            r.model,
            f"{format_tokens(r.input_tokens)}/{format_tokens(r.output_tokens)}",
            format_cost(r.cost),
            r.source,
        )
    
    console.print()
    console.print(table)
    
    if not records:
        console.print("\n[dim]No usage history. Use 'tokenmeter log' to add records.[/dim]")
    console.print()


def _render_summary_table(
    period: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    provider: Optional[str] = None,
    min_cost: Optional[float] = None,
    exclude_zero_cost: bool = False,
):
    """Render summary table (internal helper)."""
    data = get_summary(period=period, start=start, end=end, provider=provider, min_cost=min_cost, exclude_zero_cost=exclude_zero_cost)
    
    # Generate label
    if start and end:
        period_label = f"{start.strftime('%m/%d %H:%M')} - {end.strftime('%m/%d %H:%M')}"
    elif start:
        period_label = f"since {start.strftime('%m/%d %H:%M')}"
    else:
        period_label = {"day": "today", "week": "this week", "month": "this month"}.get(period or "day", period or "day")
    
    table = Table(
        title=f"🪙 tokenmeter — {period_label}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache R", justify="right", style="dim")
    table.add_column("Cache W", justify="right", style="dim")
    table.add_column("Total", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Requests", justify="right")
    
    for prov, stats in sorted(data["by_provider"].items()):
        table.add_row(
            prov.capitalize(),
            format_tokens(stats["input_tokens"]),
            format_tokens(stats["output_tokens"]),
            format_tokens(stats.get("cache_read_tokens", 0)),
            format_tokens(stats.get("cache_write_tokens", 0)),
            format_tokens(stats["total_tokens"]),
            format_cost(stats["cost"]),
            str(stats["requests"]),
        )
    
    totals = data["totals"]
    if totals["requests"] > 0:
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            format_tokens(totals["input_tokens"]),
            format_tokens(totals["output_tokens"]),
            format_tokens(totals.get("cache_read_tokens", 0)),
            format_tokens(totals.get("cache_write_tokens", 0)),
            format_tokens(totals["total_tokens"]),
            f"[bold green]{format_cost(totals['cost'])}[/bold green]",
            str(totals["requests"]),
        )
    
    console.print(table)
    return data


@app.command()
def dashboard():
    """Show interactive dashboard (summary + costs + recent)."""
    console.print()
    
    # Today's summary
    today = get_summary(period="day")
    week = get_summary(period="week")
    
    # Quick stats panel
    stats_text = Text()
    stats_text.append("TODAY  ", style="bold cyan")
    stats_text.append(f"{format_cost(today['totals']['cost'])}  ", style="bold green")
    stats_text.append(f"({format_tokens(today['totals']['total_tokens'])} tokens)\n", style="dim")
    stats_text.append("WEEK   ", style="bold cyan")
    stats_text.append(f"{format_cost(week['totals']['cost'])}  ", style="bold green")
    stats_text.append(f"({format_tokens(week['totals']['total_tokens'])} tokens)", style="dim")
    
    console.print(Panel(
        stats_text,
        title="🪙 tokenmeter",
        border_style="cyan",
        padding=(1, 2),
    ))
    
    # Provider breakdown
    if today["totals"]["requests"] > 0:
        console.print()
        _render_summary_table(period="day")
    
    # Recent activity
    recent = get_usage()[:5]
    if recent:
        console.print("\n[bold]Recent Activity[/bold]")
        for r in recent:
            console.print(
                f"  [dim]{r.timestamp.strftime('%H:%M')}[/dim] "
                f"{r.provider}/{r.model} — "
                f"[green]{format_cost(r.cost)}[/green]"
            )
    
    console.print()


@app.command(name="import")
def import_cmd(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Path to sessions directory"),
    app_name: str = typer.Option("clawdbot", "--app", "-a", help="App name (clawdbot, openclaw, claude-code)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be imported without writing"),
    auto: bool = typer.Option(False, "--auto", help="Auto-discover and import all session directories"),
    full: bool = typer.Option(False, "--full", help="Force full re-scan (ignore checkpoint)"),
    incremental: Optional[bool] = typer.Option(None, "--incremental/--no-incremental", help="Use incremental import (default: auto-detect from checkpoint)"),
):
    """Import usage from Clawdbot/OpenClaw session files."""
    from pathlib import Path as P
    
    console.print()
    
    if auto:
        # Auto-discover all session directories
        dirs = find_session_dirs()
        if not dirs:
            console.print("[yellow]No session directories found.[/yellow]")
            console.print("Expected locations:")
            console.print("  ~/.clawdbot/agents/*/sessions/")
            console.print("  ~/.openclaw/agents/*/sessions/")
            console.print("  ~/.claude/projects/*/")
            return
        
        console.print(f"[bold]Found {len(dirs)} session source(s):[/bold]")
        for d in dirs:
            console.print(f"  📁 {d['base']}/{d['agent']} — {d['files']} files")
        console.print()
        
        # Determine incremental mode
        inc_mode = False if full else incremental
        if full:
            console.print("[yellow]⚠️  Full re-scan mode (ignoring checkpoint)[/yellow]\n")
        
        # Load checkpoint once and share across all import_sessions calls
        from .checkpoint import load_checkpoint, save_checkpoint
        shared_checkpoint = load_checkpoint()
        
        total_imported = 0
        total_cost = 0.0
        total_skipped = 0
        
        for d in dirs:
            agent_app = "claude-code" if ".claude" in str(d["path"]) else app_name
            console.print(f"[cyan]Importing {d['agent']}...[/cyan]")
            result = import_sessions(d["path"], app_name=agent_app, dry_run=dry_run, incremental=inc_mode, _checkpoint=shared_checkpoint)
            total_imported += result["records_imported"]
            total_cost += result["total_cost"]
            
            skipped = result.get("files_skipped", 0)
            total_skipped += skipped
            
            if result["records_imported"] > 0:
                inc_label = ""
                if result.get("incremental"):
                    inc_label = f" [dim]({result.get('files_incremental', 0)} incremental, {result.get('files_full', 0)} full, {skipped} skipped)[/dim]"
                console.print(f"  ✅ {result['records_imported']} records ({format_cost(result['total_cost'])}){inc_label}")
            elif skipped > 0:
                console.print(f"  ⏭️  {skipped} files unchanged (checkpoint)")
            elif result.get("records_skipped_dup", 0) > 0:
                console.print(f"  ⏭️  {result['records_skipped_dup']} already imported")
            else:
                console.print(f"  ⚪ No new records")
        
        # Save shared checkpoint once after all directories processed
        if not dry_run:
            save_checkpoint(shared_checkpoint)
        
        console.print()
        prefix = "[DRY RUN] " if dry_run else ""
        skip_note = f"\nFiles skipped (unchanged): {total_skipped}" if total_skipped > 0 else ""
        checkpoint_note = f"\nCheckpoint: {len(shared_checkpoint.get('files', {}))} files tracked" if not dry_run else ""
        console.print(Panel(
            f"{prefix}Imported [bold green]{total_imported}[/bold green] records\n"
            f"Total cost: [bold green]{format_cost(total_cost)}[/bold green]{skip_note}{checkpoint_note}",
            title="🪙 Import Complete",
            border_style="green",
        ))
        return
    
    if not path:
        # Show available directories
        dirs = find_session_dirs()
        if dirs:
            console.print("[bold]Available session directories:[/bold]")
            for i, d in enumerate(dirs, 1):
                console.print(f"  {i}. {d['path']} ({d['files']} files)")
            console.print()
            console.print("Use [bold]--path[/bold] to specify a directory, or [bold]--auto[/bold] to import all.")
        else:
            console.print("[yellow]No session directories found.[/yellow]")
            console.print("Use [bold]--path[/bold] to specify the sessions directory manually.")
        return
    
    sessions_dir = P(path)
    prefix = "[DRY RUN] " if dry_run else ""
    inc_mode = False if full else incremental
    console.print(f"{prefix}Importing from: [bold]{sessions_dir}[/bold]")
    if full:
        console.print("[yellow]⚠️  Full re-scan mode[/yellow]")
    console.print()
    
    result = import_sessions(sessions_dir, app_name=app_name, dry_run=dry_run, incremental=inc_mode)
    
    if result.get("error"):
        console.print(f"[red]Error: {result['error']}[/red]")
        return
    
    # Summary table
    table = Table(
        title=f"📥 {prefix}Import Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    
    table.add_row("Files scanned", str(result["files_scanned"]))
    table.add_row("Records found", f"{result['records_found']:,}")
    table.add_row("Records imported", f"[green]{result['records_imported']:,}[/green]")
    table.add_row("Duplicates skipped", f"[dim]{result['records_skipped_dup']:,}[/dim]")
    table.add_row("Input tokens", format_tokens(result["total_input_tokens"]))
    table.add_row("Output tokens", format_tokens(result["total_output_tokens"]))
    table.add_row("Cache read tokens", format_tokens(result["total_cache_read_tokens"]))
    table.add_row("Total cost (embedded)", f"[bold green]{format_cost(result['total_cost'])}[/bold green]")
    table.add_row("API-equivalent cost", f"[yellow]{format_cost(result['total_api_equivalent_cost'])}[/yellow]")
    
    console.print(table)
    
    # Model breakdown
    if result["by_model"]:
        console.print()
        model_table = Table(
            title="By Model",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        model_table.add_column("Model", style="bold")
        model_table.add_column("Calls", justify="right")
        model_table.add_column("Input", justify="right")
        model_table.add_column("Output", justify="right")
        model_table.add_column("Cache Read", justify="right")
        model_table.add_column("Cost", justify="right", style="green")
        
        for model_key, data in sorted(result["by_model"].items(), key=lambda x: x[1]["cost"], reverse=True):
            model_table.add_row(
                model_key,
                f"{data['calls']:,}",
                format_tokens(data["input"]),
                format_tokens(data["output"]),
                format_tokens(data["cache_read"]),
                format_cost(data["cost"]),
            )
        
        console.print(model_table)
    
    if result["errors"]:
        console.print()
        console.print("[yellow]Warnings:[/yellow]")
        for err in result["errors"][:5]:
            console.print(f"  ⚠️  {err}")
    
    console.print()


@app.command()
def scan():
    """Discover available session directories to import from."""
    console.print()
    dirs = find_session_dirs()
    
    if not dirs:
        console.print("[yellow]No session directories found.[/yellow]")
        console.print("\nExpected locations:")
        console.print("  ~/.clawdbot/agents/*/sessions/")
        console.print("  ~/.openclaw/agents/*/sessions/")
        console.print("  ~/.claude/projects/*/")
        return
    
    table = Table(
        title="🔍 Discovered Session Sources",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Source", style="bold")
    table.add_column("Agent")
    table.add_column("Files", justify="right")
    table.add_column("Path", style="dim")
    
    for d in dirs:
        table.add_row(
            d["base"],
            d["agent"],
            str(d["files"]),
            str(d["path"]),
        )
    
    console.print(table)
    console.print()
    console.print("Run [bold]tokenmeter import --auto[/bold] to import all, or [bold]--path <dir>[/bold] for specific ones.")
    console.print()


@app.command()
def fetch(
    provider: Optional[str] = typer.Argument(None, help="Provider to fetch (anthropic, openai, google, azure). Omit for auto-detect."),
    scan: bool = typer.Option(True, "--scan/--no-scan", help="Auto-scan env vars for API keys"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be fetched without importing"),
):
    """Fetch usage from provider APIs (auto-detects API keys in environment)."""
    import os
    
    console.print()
    
    if provider:
        # Fetch from specific provider
        provider = provider.lower()
        env_vars = scan_env_vars()
        env_var = env_vars.get(provider)
        
        if not env_var:
            console.print(f"[red]❌ No API key found for {provider}[/red]")
            console.print(f"Set one of: {', '.join(scan_env_vars.__code__.co_consts)}")
            raise typer.Exit(1)
        
        api_key = os.environ.get(env_var)
        console.print(f"[cyan]Fetching from {provider.capitalize()}...[/cyan]")
        
        result = fetch_provider(provider, api_key, dry_run=dry_run)
        _print_fetch_result(provider, result)
    else:
        # Auto-detect and fetch from all providers
        console.print("[bold]🔍 Scanning environment...[/bold]")
        env_vars = scan_env_vars()
        
        found_any = False
        for prov, env_var in env_vars.items():
            if env_var:
                console.print(f"  [green]✅[/green] {env_var} found")
                found_any = True
            else:
                console.print(f"  [dim]❌ {prov.upper()}_API_KEY not set[/dim]")
        
        if not found_any:
            console.print()
            console.print("[yellow]No API keys found in environment.[/yellow]")
            console.print("Set environment variables like ANTHROPIC_API_KEY or OPENAI_API_KEY")
            raise typer.Exit(1)
        
        console.print()
        
        # Fetch from all available providers
        results = fetch_all(dry_run=dry_run)
        
        total_imported = 0
        total_cost = 0.0
        
        for prov, result in results.items():
            if result.get("env_var"):
                console.print(f"[cyan]Fetching from {prov.capitalize()}...[/cyan]")
                _print_fetch_result(prov, result)
                total_imported += result.get("records_imported", 0)
                total_cost += result.get("total_cost", 0.0)
        
        console.print()
        if total_imported > 0:
            prefix = "[DRY RUN] " if dry_run else ""
            console.print(f"[bold green]{prefix}✅ Fetching complete! {total_imported} records imported ({format_cost(total_cost)})[/bold green]")
        else:
            console.print("[bold]Fetching complete![/bold]")
    
    console.print()


def _print_fetch_result(provider: str, result: dict):
    """Print the result of a fetch operation."""
    if result.get("no_api"):
        console.print(f"  [yellow]ℹ️  {result.get('message', 'No usage API available')}[/yellow]")
    elif result.get("not_found"):
        pass  # Already printed during scan
    elif not result.get("success"):
        console.print(f"  [red]❌ {result.get('error', 'Unknown error')}[/red]")
    else:
        imported = result.get("records_imported", 0)
        skipped = result.get("records_skipped", 0)
        cost = result.get("total_cost", 0.0)
        
        if imported > 0:
            console.print(f"  [green]✅ {imported} usage records imported ({format_cost(cost)})[/green]")
        elif skipped > 0:
            console.print(f"  [dim]⏭️  {skipped} records already imported[/dim]")
        else:
            console.print(f"  [dim]⚪ No new records[/dim]")


@app.command()
def version():
    """Show version information."""
    console.print(f"tokenmeter v{__version__}")


@app.callback()
def main():
    """
    🪙 tokenmeter - Track your AI API usage and costs
    
    All data is stored locally in ~/.tokenmeter/usage.db
    """
    pass


if __name__ == "__main__":
    app()
