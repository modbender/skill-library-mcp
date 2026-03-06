# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///
"""SurrealDB skill onboarding: setup wizard, configuration check, and capabilities manifest."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

stderr_console = Console(stderr=True)
stdout_console = Console(file=sys.stdout)

SKILL_VERSION = "1.0.0"
DEFAULT_ENDPOINT = "ws://localhost:8000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
    """Run a subprocess, capturing output."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _surreal_version() -> str | None:
    """Return the surreal CLI version string, or None if not found."""
    path = shutil.which("surreal")
    if path is None:
        return None
    try:
        result = _run([path, "version"])
        output = (result.stdout or result.stderr).strip()
        # surreal CLI may print "surreal 3.x.x" or just the version
        for token in output.split():
            if token[0].isdigit():
                return token
        return output or None
    except Exception:
        return None


def _env(name: str) -> str | None:
    """Return an environment variable or None."""
    val = os.environ.get(name, "").strip()
    return val if val else None


def _check_uv() -> bool:
    """Return True if uv is available."""
    return shutil.which("uv") is not None


def _check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Return True if a TCP connection can be made to host:port."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _parse_endpoint(endpoint: str) -> tuple[str, int]:
    """Extract host and port from a SurrealDB endpoint URL."""
    url = endpoint
    for prefix in ("ws://", "wss://", "http://", "https://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
            break
    url = url.rstrip("/")
    if ":" in url:
        host, port_str = url.rsplit(":", 1)
        try:
            return host, int(port_str)
        except ValueError:
            pass
    return url, 8000


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------

def run_check() -> dict:
    """Run configuration checks and return a results dict."""
    results: dict = {}

    # surreal CLI
    version = _surreal_version()
    results["cli_installed"] = {
        "status": "pass" if version else "fail",
        "version": version,
        "path": shutil.which("surreal"),
    }

    # Endpoint
    endpoint = _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    host, port = _parse_endpoint(endpoint)
    reachable = _check_port(host, port)
    results["server_reachable"] = {
        "status": "pass" if reachable else "fail",
        "endpoint": endpoint,
    }

    # Credentials
    user = _env("SURREAL_USER")
    password = _env("SURREAL_PASS")
    results["credentials_configured"] = {
        "status": "pass" if user and password else "warn" if user or password else "fail",
        "user_set": user is not None,
        "pass_set": password is not None,
    }

    # Namespace / Database
    ns = _env("SURREAL_NS")
    db = _env("SURREAL_DB")
    results["namespace_database"] = {
        "status": "pass" if ns and db else "warn" if ns or db else "fail",
        "namespace": ns,
        "database": db,
    }

    # uv
    results["uv_available"] = {
        "status": "pass" if _check_uv() else "warn",
        "path": shutil.which("uv"),
    }

    return results


def print_check_table(results: dict) -> None:
    """Render a Rich table of check results to stderr."""
    table = Table(title="SurrealDB Configuration Check", show_lines=True)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    status_style = {"pass": "[green]PASS[/green]", "warn": "[yellow]WARN[/yellow]", "fail": "[red]FAIL[/red]"}

    for name, info in results.items():
        status = status_style.get(info["status"], info["status"])
        details_parts = []
        for k, v in info.items():
            if k == "status":
                continue
            details_parts.append(f"{k}: {v}")
        table.add_row(name.replace("_", " ").title(), status, "\n".join(details_parts))

    stderr_console.print(table)


# ---------------------------------------------------------------------------
# --agent mode
# ---------------------------------------------------------------------------

CAPABILITIES_MANIFEST: dict = {
    "skill": "surrealdb",
    "version": SKILL_VERSION,
    "description": "Expert SurrealDB 3 architect and developer",
    "commands": [
        {"name": "onboard", "subcommands": ["--check", "--agent", "--interactive"], "description": "Setup and capabilities"},
        {"name": "doctor", "subcommands": ["--full", "--quick"], "description": "Environment health check"},
        {"name": "schema", "subcommands": ["export", "inspect", "diff"], "description": "Schema introspection"},
    ],
    "rules": [
        {"file": "surrealql.md", "topic": "SurrealQL syntax, statements, functions, operators"},
        {"file": "data-modeling.md", "topic": "Multi-model data modeling patterns"},
        {"file": "graph-queries.md", "topic": "Graph traversal and RELATE patterns"},
        {"file": "vector-search.md", "topic": "Vector indexes, HNSW, RAG patterns"},
        {"file": "security.md", "topic": "Authentication, permissions, access control"},
        {"file": "performance.md", "topic": "Indexing, query optimization, storage engines"},
        {"file": "sdks.md", "topic": "SDK patterns for JS, Python, Go, Rust, Java, .NET"},
        {"file": "deployment.md", "topic": "Docker, Kubernetes, cloud, distributed deployment"},
        {"file": "surrealism.md", "topic": "WASM extension development"},
        {"file": "surreal-sync.md", "topic": "Data migration from other databases"},
        {"file": "surrealist.md", "topic": "Surrealist IDE/GUI"},
        {"file": "surrealfs.md", "topic": "AI agent virtual filesystem"},
    ],
    "decision_trees": {
        "new_project": "Run doctor -> Design schema (data-modeling.md) -> Choose deployment (deployment.md) -> Configure security (security.md)",
        "data_modeling": "Identify models needed -> Read data-modeling.md -> Use graph-queries.md for relationships -> Use vector-search.md for AI features",
        "performance_issue": "Run doctor -> Check indexes (performance.md) -> Review queries (surrealql.md) -> Consider storage engine change",
        "migration": "Identify source DB -> Read surreal-sync.md -> Plan schema mapping (data-modeling.md) -> Execute migration",
        "extension_development": "Read surrealism.md -> Write Rust module -> Compile WASM -> Register with DEFINE MODULE",
    },
    "environment_variables": {
        "SURREAL_ENDPOINT": "SurrealDB server endpoint (default: ws://localhost:8000)",
        "SURREAL_USER": "Root/admin username",
        "SURREAL_PASS": "Root/admin password",
        "SURREAL_NS": "Default namespace",
        "SURREAL_DB": "Default database",
    },
}


def run_agent() -> dict:
    """Return the capabilities manifest dict."""
    return CAPABILITIES_MANIFEST


# ---------------------------------------------------------------------------
# --interactive mode
# ---------------------------------------------------------------------------

def run_interactive() -> dict:
    """Guided setup interview. Returns a summary dict."""
    stderr_console.print(Panel("SurrealDB Skill -- Interactive Setup", style="bold cyan"))

    result: dict = {"steps": []}

    # 1. Check surreal CLI
    version = _surreal_version()
    if version:
        stderr_console.print(f"  surreal CLI found: v{version}")
        result["steps"].append({"step": "cli_check", "status": "pass", "version": version})
    else:
        stderr_console.print("[red]  surreal CLI not found.[/red] Install from https://surrealdb.com/install")
        result["steps"].append({"step": "cli_check", "status": "fail"})

    # 2. Endpoint
    default_ep = _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    endpoint = Prompt.ask("SurrealDB endpoint", default=default_ep, console=stderr_console)
    result["endpoint"] = endpoint

    # 3. Connectivity
    host, port = _parse_endpoint(endpoint)
    reachable = _check_port(host, port)
    if reachable:
        stderr_console.print(f"  Server reachable at {endpoint}")
        result["steps"].append({"step": "connectivity", "status": "pass"})
    else:
        stderr_console.print(f"[yellow]  Cannot reach {endpoint}. Continue anyway.[/yellow]")
        result["steps"].append({"step": "connectivity", "status": "fail"})

    # 4. Credentials
    default_user = _env("SURREAL_USER") or "root"
    user = Prompt.ask("Username", default=default_user, console=stderr_console)
    password = Prompt.ask("Password", password=True, default=_env("SURREAL_PASS") or "", console=stderr_console)
    result["user"] = user
    result["steps"].append({"step": "credentials", "status": "pass"})

    # 5. Namespace / Database
    ns = Prompt.ask("Namespace", default=_env("SURREAL_NS") or "test", console=stderr_console)
    db = Prompt.ask("Database", default=_env("SURREAL_DB") or "test", console=stderr_console)
    result["namespace"] = ns
    result["database"] = db
    result["steps"].append({"step": "namespace_database", "status": "pass"})

    # 6. Generate .env
    if Confirm.ask("Generate a .env file?", default=True, console=stderr_console):
        env_path = Path.cwd() / ".env"
        lines = [
            f"SURREAL_ENDPOINT={endpoint}",
            f"SURREAL_USER={user}",
            f"SURREAL_PASS={password}",
            f"SURREAL_NS={ns}",
            f"SURREAL_DB={db}",
        ]
        env_path.write_text("\n".join(lines) + "\n")
        stderr_console.print(f"  Wrote {env_path}")
        result["env_file"] = str(env_path)
        result["steps"].append({"step": "env_file", "status": "pass"})
    else:
        result["steps"].append({"step": "env_file", "status": "skipped"})

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="onboard",
        description="SurrealDB skill onboarding: setup wizard, configuration check, and capabilities manifest.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check configuration status (non-interactive)")
    mode.add_argument("--agent", action="store_true", help="Output JSON capabilities manifest")
    mode.add_argument("--interactive", action="store_true", help="Guided setup interview (default for TTY)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.agent:
        manifest = run_agent()
        stderr_console.print("[bold]Capabilities manifest:[/bold]")
        print(json.dumps(manifest, indent=2))
        return

    if args.check:
        results = run_check()
        print_check_table(results)
        print(json.dumps(results, indent=2))
        return

    if args.interactive:
        result = run_interactive()
        print(json.dumps(result, indent=2))
        return

    # Default: interactive if TTY, otherwise check
    if sys.stdin.isatty():
        result = run_interactive()
        print(json.dumps(result, indent=2))
    else:
        results = run_check()
        print_check_table(results)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
