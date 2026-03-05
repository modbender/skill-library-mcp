# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Agent-friendly onboarding and setup wizard for agent-deep-research.

Three modes:
  --agent       Output a JSON capabilities manifest (for AI agents, non-TTY default)
  --interactive Run a guided setup interview (for humans, TTY default)
  --check       Quick configuration status check
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Shared helpers (duplicated for PEP 723 standalone -- no cross-imports)
# ---------------------------------------------------------------------------

def _get_state_path() -> Path:
    return Path(".gemini-research.json")


def _load_state() -> dict:
    path = _get_state_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(state: dict) -> None:
    _get_state_path().write_text(json.dumps(state, indent=2) + "\n")


def _resolve_api_key() -> str | None:
    """Return the first available API key, or None."""
    for var in ("GEMINI_DEEP_RESEARCH_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        key = os.environ.get(var)
        if key:
            return key
    return None


def _api_key_var() -> str | None:
    """Return the name of the env var that holds the API key, or None."""
    for var in ("GEMINI_DEEP_RESEARCH_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        if os.environ.get(var):
            return var
    return None


def _check_uv() -> bool:
    """Check whether uv is available on PATH."""
    import shutil
    return shutil.which("uv") is not None


def _validate_api_key(key: str) -> bool:
    """Test the API key with a lightweight Gemini call."""
    try:
        from google import genai
        client = genai.Client(api_key=key)
        # Use a minimal call to validate -- list models is lightweight
        models = client.models.list()
        # Consume at least one item to confirm the key works
        for _ in models:
            return True
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Config status
# ---------------------------------------------------------------------------

def _build_config_status() -> dict:
    """Build a configuration status object."""
    api_key = _resolve_api_key()
    api_key_var = _api_key_var()
    state = _load_state()
    has_uv = _check_uv()
    state_path = _get_state_path()

    return {
        "api_key_configured": api_key is not None,
        "api_key_source": api_key_var,
        "uv_installed": has_uv,
        "state_file_exists": state_path.exists(),
        "state_file_path": str(state_path),
        "research_count": len(state.get("researchIds", [])),
        "store_count": len(state.get("fileSearchStores", {})),
        "history_count": len(state.get("researchHistory", [])),
        "preferences": state.get("preferences", {}),
    }


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------

def cmd_check() -> None:
    """Quick configuration status check."""
    status = _build_config_status()

    # Human-readable on stderr
    from rich.console import Console
    from rich.table import Table
    console = Console(stderr=True)

    table = Table(title="Configuration Status", show_header=True)
    table.add_column("Item", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    # API Key
    if status["api_key_configured"]:
        table.add_row("API Key", "[green]OK[/green]", f"via ${status['api_key_source']}")
    else:
        table.add_row(
            "API Key", "[red]MISSING[/red]",
            "Set GOOGLE_API_KEY, GEMINI_API_KEY, or GEMINI_DEEP_RESEARCH_API_KEY",
        )

    # uv
    if status["uv_installed"]:
        table.add_row("uv", "[green]OK[/green]", "Available on PATH")
    else:
        table.add_row(
            "uv", "[red]MISSING[/red]",
            "Install: https://docs.astral.sh/uv/getting-started/installation/",
        )

    # State file
    if status["state_file_exists"]:
        table.add_row(
            "State File", "[green]EXISTS[/green]",
            f"{status['research_count']} research IDs, {status['store_count']} stores, "
            f"{status['history_count']} history entries",
        )
    else:
        table.add_row("State File", "[dim]NOT YET[/dim]", "Created on first use")

    console.print(table)

    # Machine-readable on stdout
    print(json.dumps(status))


# ---------------------------------------------------------------------------
# --agent mode
# ---------------------------------------------------------------------------

CAPABILITIES_MANIFEST = {
    "skill": "deep-research",
    "version": "2.1.2",
    "description": "Deep research and RAG-grounded file search powered by Google Gemini",
    "commands": {
        "research": {
            "script": "scripts/research.py",
            "description": "Start, monitor, and save deep research interactions",
            "subcommands": {
                "start": {
                    "usage": 'uv run {baseDir}/scripts/research.py start "your question"',
                    "description": "Launch a background deep research job",
                    "key_flags": {
                        "--output FILE": "Block until complete, save report to file",
                        "--output-dir DIR": "Block until complete, save structured output",
                        "--context PATH": "Auto-upload local files for RAG-grounded research",
                        "--store NAME": "Use existing file search store for grounding",
                        "--dry-run": "Preview estimated costs without starting research",
                        "--format FMT": "md | html | pdf (default: md; pdf requires weasyprint)",
                        "--prompt-template TPL": "typescript | python | general | auto (default: auto)",
                        "--report-format FMT": "executive_summary | detailed_report | comprehensive",
                        "--follow-up ID": "Continue a previous research session",
                        "--depth LVL": "quick | standard | deep (default: standard)",
                        "--max-cost USD": "Abort if estimated cost exceeds limit",
                        "--input-file PATH": "Read query from file",
                        "--no-cache": "Skip research cache, force fresh run",
                        "--timeout SECS": "Max wait time when blocking (default: 1800)",
                    },
                    "stdout_contract": {
                        "non_blocking": {"id": "string", "status": "string"},
                        "blocking_output_dir": {
                            "id": "string",
                            "status": "string",
                            "output_dir": "string",
                            "report_file": "string",
                            "report_size_bytes": "int",
                            "duration_seconds": "int",
                            "estimated_cost_usd": "float",
                            "summary": "string (first 200 chars)",
                        },
                        "dry_run": {
                            "type": "cost_estimate",
                            "disclaimer": "string",
                            "currency": "USD",
                            "estimates": "object",
                        },
                    },
                },
                "status": {
                    "usage": "uv run {baseDir}/scripts/research.py status <interaction-id>",
                    "description": "Check research progress",
                    "stdout_contract": {"id": "string", "status": "string", "outputCount": "int"},
                },
                "report": {
                    "usage": "uv run {baseDir}/scripts/research.py report <interaction-id>",
                    "description": "Save report from completed research",
                    "key_flags": {
                        "--output FILE": "Save to specific file",
                        "--output-dir DIR": "Save structured output",
                    },
                },
            },
        },
        "store": {
            "script": "scripts/store.py",
            "description": "Manage file search stores for RAG grounding",
            "subcommands": {
                "create": {"usage": 'uv run {baseDir}/scripts/store.py create "name"'},
                "list": {"usage": "uv run {baseDir}/scripts/store.py list"},
                "query": {"usage": 'uv run {baseDir}/scripts/store.py query <name> "question"'},
                "delete": {"usage": "uv run {baseDir}/scripts/store.py delete <name>"},
            },
        },
        "upload": {
            "script": "scripts/upload.py",
            "description": "Upload files/directories to a store",
            "usage": "uv run {baseDir}/scripts/upload.py <path> <store-name> [--smart-sync]",
        },
        "state": {
            "script": "scripts/state.py",
            "description": "View/clear workspace state",
            "subcommands": {
                "show": {"usage": "uv run {baseDir}/scripts/state.py --json show"},
                "research": {"usage": "uv run {baseDir}/scripts/state.py --json research"},
                "stores": {"usage": "uv run {baseDir}/scripts/state.py --json stores"},
                "clear": {"usage": "uv run {baseDir}/scripts/state.py clear -y"},
            },
        },
        "onboard": {
            "script": "scripts/onboard.py",
            "description": "Setup wizard and capabilities manifest",
            "usage": "uv run {baseDir}/scripts/onboard.py --check",
        },
    },
    "decision_tree": {
        "research_a_topic": {
            "quick_answer": 'uv run {baseDir}/scripts/research.py start "question" --output report.md',
            "grounded_in_files": 'uv run {baseDir}/scripts/research.py start "question" --context ./path --output report.md',
            "estimate_cost_first": 'uv run {baseDir}/scripts/research.py start "question" --context ./path --dry-run',
            "non_blocking": 'uv run {baseDir}/scripts/research.py start "question"  # returns JSON with id',
        },
        "ask_about_uploaded_docs": {
            "direct_query": 'uv run {baseDir}/scripts/store.py query <store-name> "question"',
            "deep_research": 'uv run {baseDir}/scripts/research.py start "question" --store <name> --output report.md',
        },
        "check_if_ready": "uv run {baseDir}/scripts/onboard.py --check",
    },
    "output_convention": {
        "stderr": "Rich-formatted human-readable output",
        "stdout": "Machine-readable JSON",
        "tip": "Pipe 2>/dev/null to suppress human output",
    },
    "exit_codes": {
        "0": "Success",
        "1": "Error (missing API key, invalid arguments, API failure, timeout)",
    },
    "requirements": {
        "api_key": "Set GOOGLE_API_KEY, GEMINI_API_KEY, or GEMINI_DEEP_RESEARCH_API_KEY",
        "runtime": "uv (https://docs.astral.sh/uv/)",
    },
}


def cmd_agent() -> None:
    """Output a JSON capabilities manifest for agent consumption."""
    status = _build_config_status()
    manifest = {**CAPABILITIES_MANIFEST, "config_status": status}

    # Brief summary on stderr
    from rich.console import Console
    console = Console(stderr=True)

    if status["api_key_configured"] and status["uv_installed"]:
        console.print("[green]Ready.[/green] API key and uv configured.")
    else:
        missing = []
        if not status["api_key_configured"]:
            missing.append("API key")
        if not status["uv_installed"]:
            missing.append("uv")
        console.print(f"[yellow]Setup needed:[/yellow] {', '.join(missing)} missing.")

    # Full manifest on stdout
    print(json.dumps(manifest, indent=2))


# ---------------------------------------------------------------------------
# --interactive mode
# ---------------------------------------------------------------------------

def cmd_interactive() -> None:
    """Run a guided interactive setup interview."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    console = Console(stderr=True)

    console.print(Panel(
        "agent-deep-research Setup Wizard\n"
        "Deep research and RAG-grounded file search powered by Google Gemini",
        style="bold blue",
    ))
    console.print()

    # Step 1: API Key
    console.print("[bold]Step 1: API Key[/bold]")
    api_key = _resolve_api_key()
    if api_key:
        var_name = _api_key_var()
        console.print(f"  [green]Found[/green] API key via ${var_name}")
        if Confirm.ask("  Validate the key with a test API call?", default=True):
            console.print("  Testing...", end=" ")
            if _validate_api_key(api_key):
                console.print("[green]Valid[/green]")
            else:
                console.print("[red]Failed[/red]")
                console.print("  The key may be invalid or expired. Check your Google AI Studio dashboard.")
    else:
        console.print("  [red]No API key found.[/red]")
        console.print("  Set one of these environment variables:")
        console.print("    export GOOGLE_API_KEY='your-key-here'")
        console.print("    export GEMINI_API_KEY='your-key-here'")
        console.print("    export GEMINI_DEEP_RESEARCH_API_KEY='your-key-here'")
        console.print()
        console.print("  Get a key at: https://aistudio.google.com/apikey")
        raw_key = Prompt.ask("  Paste your API key to validate (or press Enter to skip)")
        if raw_key.strip():
            console.print("  Testing...", end=" ")
            if _validate_api_key(raw_key.strip()):
                console.print("[green]Valid[/green]")
                console.print(f"  Add to your shell profile:")
                console.print(f"    export GOOGLE_API_KEY='<your-key>'")
            else:
                console.print("[red]Failed[/red] -- check the key and try again.")

    console.print()

    # Step 2: uv
    console.print("[bold]Step 2: Runtime (uv)[/bold]")
    if _check_uv():
        console.print("  [green]Found[/green] uv on PATH")
    else:
        console.print("  [red]Not found.[/red] Install with:")
        console.print("    See: https://docs.astral.sh/uv/getting-started/installation/")
    console.print()

    # Step 3: Preferences
    console.print("[bold]Step 3: Preferences[/bold]")
    state = _load_state()
    prefs = state.get("preferences", {})

    # Report format
    fmt = Prompt.ask(
        "  Default report format",
        choices=["executive_summary", "detailed_report", "comprehensive", "none"],
        default=prefs.get("report_format", "none"),
    )
    if fmt != "none":
        prefs["report_format"] = fmt
    elif "report_format" in prefs:
        del prefs["report_format"]

    # Timeout
    timeout_str = Prompt.ask(
        "  Default timeout (seconds)",
        default=str(prefs.get("timeout", 1800)),
    )
    try:
        prefs["timeout"] = int(timeout_str)
    except ValueError:
        prefs["timeout"] = 1800

    # Adaptive polling
    adaptive = Confirm.ask(
        "  Enable adaptive polling (learns from history)?",
        default=prefs.get("adaptive_polling", True),
    )
    prefs["adaptive_polling"] = adaptive

    # Save preferences
    state["preferences"] = prefs
    _save_state(state)
    console.print()
    console.print("[green]Preferences saved[/green] to .gemini-research.json")

    # Step 4: Example commands
    console.print()
    console.print("[bold]Step 4: Try It[/bold]")
    console.print()
    console.print("  # Quick research (blocks until done)")
    console.print('  uv run scripts/research.py "What is quantum error correction?" --output report.md')
    console.print()
    console.print("  # Research grounded in your code")
    console.print('  uv run scripts/research.py start "How does auth work?" --context ./src --output report.md')
    console.print()
    console.print("  # Estimate cost before running")
    console.print('  uv run scripts/research.py start "Analyze the codebase" --context ./src --dry-run')
    console.print()
    console.print("  # Non-blocking (for automation)")
    console.print('  uv run scripts/research.py start "Deep analysis"')
    console.print()

    # Final status on stdout
    print(json.dumps(_build_config_status()))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="onboard",
        description="Agent-friendly onboarding and setup for agent-deep-research",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--agent", action="store_true",
        help="Output a JSON capabilities manifest (default for non-TTY)",
    )
    group.add_argument(
        "--interactive", action="store_true",
        help="Run a guided setup interview (default for TTY)",
    )
    group.add_argument(
        "--check", action="store_true",
        help="Quick configuration status check",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check:
        cmd_check()
    elif args.agent:
        cmd_agent()
    elif args.interactive:
        cmd_interactive()
    else:
        # Auto-detect: TTY -> interactive, non-TTY -> agent
        if sys.stdin.isatty() and sys.stdout.isatty():
            cmd_interactive()
        else:
            cmd_agent()


if __name__ == "__main__":
    main()
