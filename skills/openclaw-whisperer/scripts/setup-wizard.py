#!/usr/bin/env python3
"""Interactive onboarding wizard for OpenClaw."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from scripts.lib.setup_helpers import (
    AI_PROVIDERS,
    AVAILABLE_CHANNELS,
    generate_config,
    get_model_suggestion,
    install_openclaw,
    install_pnpm,
    save_config_with_backup,
)
from scripts.lib.system_checks import check_binary, check_docker, check_node_version
from scripts.lib.utils import CONFIG_FILE, check_mark, run_command

console = Console()


def show_welcome():
    """Display welcome banner."""
    console.print(Panel(
        "[bold cyan]OpenClaw Interactive Setup\nSelf-hosted AI Gateway[/bold cyan]\n\nThis wizard will help you set up OpenClaw.",
        border_style="cyan"
    ))


def check_prerequisites() -> dict[str, bool]:
    """Check and display prerequisites."""
    console.print("\n[bold]Checking prerequisites...[/bold]\n")

    checks = {}
    table = Table(show_header=False)
    table.add_column("Requirement", style="cyan")
    table.add_column("Status")
    table.add_column("Action")

    node_ok, _ = check_node_version()
    checks["node"] = node_ok
    table.add_row("Node.js (>=22)", check_mark(node_ok), "" if node_ok else "Install via fnm")

    for name, key, action in [
        ("pnpm", "pnpm", "npm install -g pnpm"),
        ("openclaw CLI", "openclaw", "npm install -g openclaw"),
        ("git", "git", "git-scm.com"),
    ]:
        ok = check_binary(key)
        checks[key] = ok
        table.add_row(name, check_mark(ok), "" if ok else action)

    docker_ok, _ = check_docker()
    checks["docker"] = docker_ok
    table.add_row("docker (optional)", check_mark(docker_ok), "" if docker_ok else "docker.com")

    console.print(table)
    console.print()
    return checks


def select_channels(preselected: tuple = ()) -> list[str]:
    """Interactive channel selection."""
    if preselected:
        return list(preselected)

    console.print("\n[bold]Select channels (1,2,4 or Enter to skip):[/bold]")
    for i, ch in enumerate(AVAILABLE_CHANNELS, 1):
        console.print(f"  {i}. {ch}")

    selection = Prompt.ask("Channels", default="")
    if not selection:
        return []

    selected = []
    for num_str in selection.split(","):
        try:
            idx = int(num_str.strip()) - 1
            if 0 <= idx < len(AVAILABLE_CHANNELS):
                selected.append(AVAILABLE_CHANNELS[idx])
        except ValueError:
            pass

    return selected


def configure_ai_provider(provider: str | None = None) -> dict:
    """Configure AI provider."""
    console.print("\n[bold]Configure AI Provider:[/bold]")

    if not provider:
        for i, p in enumerate(AI_PROVIDERS, 1):
            console.print(f"  {i}. {p}")
        provider_idx = Prompt.ask("Select provider", choices=["1", "2", "3"], default="1")
        provider = AI_PROVIDERS[int(provider_idx) - 1]

    console.print(f"[cyan]Selected: {provider}[/cyan]")
    api_key = Prompt.ask(f"Enter {provider} API key", password=True)
    model = Prompt.ask("Model name", default=get_model_suggestion(provider))

    return {"provider": provider, "api_key": api_key, "model": model}


@click.command()
@click.option("--non-interactive", is_flag=True, help="Use defaults")
@click.option("--channel", multiple=True, help="Pre-select channels")
@click.option("--provider", type=click.Choice(AI_PROVIDERS), help="AI provider")
@click.option("--check-only", is_flag=True, help="Only check prerequisites")
def main(non_interactive, channel, provider, check_only):
    """OpenClaw Interactive Setup Wizard."""
    show_welcome()
    checks = check_prerequisites()

    if check_only:
        return

    if not non_interactive:
        if not checks.get("pnpm") and checks.get("node") and Confirm.ask("Install pnpm?"):
            console.print("Installing pnpm...")
            console.print("[green]✓ pnpm installed[/green]" if install_pnpm() else "[red]✗ Failed[/red]")

        if not checks.get("openclaw") and checks.get("node") and Confirm.ask("Install openclaw?"):
            console.print("Installing openclaw...")
            console.print("[green]✓ openclaw installed[/green]" if install_openclaw() else "[red]✗ Failed[/red]")

    if not check_binary("openclaw"):
        console.print("[red]Error: openclaw CLI required. Run: npm install -g openclaw[/red]")
        sys.exit(1)

    selected_channels = list(channel) if non_interactive or channel else select_channels(channel)

    if non_interactive:
        if not provider:
            console.print("[red]Error: --provider required in non-interactive mode[/red]")
            sys.exit(1)
        ai_config = {"provider": provider, "api_key": "your-api-key-here", "model": "default-model"}
    else:
        ai_config = configure_ai_provider(provider)

    console.print("\n[bold]Generating configuration...[/bold]")
    config = generate_config(selected_channels, ai_config)

    if save_config_with_backup(config):
        console.print(f"[green]✓ Config saved to {CONFIG_FILE}[/green]")
    else:
        console.print("[red]✗ Failed to save config[/red]")
        sys.exit(1)

    if check_binary("openclaw") and not non_interactive:
        console.print("\n[bold]Running openclaw doctor...[/bold]")
        run_command(["openclaw", "doctor"], timeout=30)

    steps = f"""[bold green]Setup Complete![/bold green]

1. Configure credentials in ~/.openclaw/credentials/
2. Start: openclaw start
3. Check: openclaw doctor
4. Explore: clawhub search <keyword>
5. Docs: https://docs.openclaw.ai

[bold]Enabled:[/bold] {', '.join(selected_channels) if selected_channels else 'None'}"""

    console.print(Panel(steps, border_style="green"))


if __name__ == "__main__":
    main()
