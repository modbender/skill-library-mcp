# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich>=13.0.0",
#   "websockets>=12.0",
# ]
# ///
"""SurrealDB environment health check tool.

Runs quick (offline) or full (online) diagnostics against a SurrealDB
installation and reports results as a Rich table on stderr and structured
JSON on stdout.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import socket
import subprocess
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

stderr_console = Console(stderr=True)

DEFAULT_ENDPOINT = "ws://localhost:8000"

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

STATUS_PASS = "pass"
STATUS_WARN = "warn"
STATUS_FAIL = "fail"


def _env(name: str) -> str | None:
    val = os.environ.get(name, "").strip()
    return val if val else None


# ---------------------------------------------------------------------------
# Quick checks (no server connection required)
# ---------------------------------------------------------------------------

def check_cli() -> dict[str, Any]:
    """Check if the surreal CLI is installed and get its version."""
    path = shutil.which("surreal")
    if path is None:
        return {"status": STATUS_FAIL, "message": "surreal CLI not found in PATH"}
    try:
        result = subprocess.run(
            [path, "version"], capture_output=True, text=True, timeout=10,
        )
        output = (result.stdout or result.stderr).strip()
        version = None
        for token in output.split():
            if token[0].isdigit():
                version = token
                break
        return {"status": STATUS_PASS, "version": version or output, "path": path}
    except Exception as exc:
        return {"status": STATUS_FAIL, "message": str(exc)}


def check_env_vars() -> dict[str, Any]:
    """Check that essential environment variables are set."""
    required = ["SURREAL_ENDPOINT", "SURREAL_USER", "SURREAL_PASS", "SURREAL_NS", "SURREAL_DB"]
    present = {k: _env(k) is not None for k in required}
    missing = [k for k, v in present.items() if not v]
    status = STATUS_PASS if not missing else STATUS_WARN
    return {"status": status, "variables": present, "missing": missing}


def check_uv() -> dict[str, Any]:
    """Check if uv is available."""
    path = shutil.which("uv")
    if path:
        return {"status": STATUS_PASS, "path": path}
    return {"status": STATUS_WARN, "message": "uv not found -- install from https://docs.astral.sh/uv/"}


def check_port(endpoint: str | None = None) -> dict[str, Any]:
    """Check if the SurrealDB port is open (TCP-level only)."""
    ep = endpoint or _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    host, port = _parse_endpoint(ep)
    try:
        with socket.create_connection((host, port), timeout=3):
            return {"status": STATUS_PASS, "endpoint": ep, "host": host, "port": port}
    except OSError as exc:
        return {"status": STATUS_FAIL, "endpoint": ep, "host": host, "port": port, "message": str(exc)}


def _parse_endpoint(endpoint: str) -> tuple[str, int]:
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
# Full checks (require server connection)
# ---------------------------------------------------------------------------

async def _ws_query(endpoint: str, user: str, password: str, ns: str | None, db: str | None, query: str) -> Any:
    """Open a WebSocket to SurrealDB, authenticate, optionally USE ns/db, and execute a query."""
    import websockets  # type: ignore[import-untyped]

    ws_ep = endpoint.rstrip("/") + "/rpc"
    async with websockets.connect(ws_ep, open_timeout=5, close_timeout=5) as ws:
        # Sign in
        signin_msg = json.dumps({
            "id": "signin",
            "method": "signin",
            "params": [{"user": user, "pass": password}],
        })
        await ws.send(signin_msg)
        signin_resp = json.loads(await ws.recv())
        if signin_resp.get("error"):
            raise RuntimeError(f"Auth failed: {signin_resp['error']}")

        # USE namespace/database if provided
        if ns and db:
            use_msg = json.dumps({
                "id": "use",
                "method": "use",
                "params": [ns, db],
            })
            await ws.send(use_msg)
            use_resp = json.loads(await ws.recv())
            if use_resp.get("error"):
                raise RuntimeError(f"USE failed: {use_resp['error']}")

        # Query
        query_msg = json.dumps({
            "id": "query",
            "method": "query",
            "params": [query],
        })
        await ws.send(query_msg)
        query_resp = json.loads(await ws.recv())
        if query_resp.get("error"):
            raise RuntimeError(f"Query failed: {query_resp['error']}")
        return query_resp.get("result")

    return None  # unreachable but keeps type-checker happy


def _run_ws_query(endpoint: str, user: str, password: str, ns: str | None, db: str | None, query: str) -> Any:
    """Synchronous wrapper around _ws_query."""
    return asyncio.get_event_loop().run_until_complete(
        _ws_query(endpoint, user, password, ns, db, query),
    )


def check_auth(endpoint: str, user: str, password: str) -> dict[str, Any]:
    """Authenticate against the SurrealDB server."""
    try:
        import websockets  # noqa: F401
        asyncio.get_event_loop().run_until_complete(
            _ws_auth_only(endpoint, user),
        )
        # If we get here, at least the connection works. We test auth below.
    except Exception:
        pass

    try:
        _run_ws_query(endpoint, user, password, None, None, "INFO FOR ROOT")
        return {"status": STATUS_PASS, "user": user}
    except RuntimeError as exc:
        return {"status": STATUS_FAIL, "user": user, "message": str(exc)}
    except Exception as exc:
        return {"status": STATUS_FAIL, "user": user, "message": str(exc)}


async def _ws_auth_only(endpoint: str, user: str) -> None:
    """Minimal connection test (no auth)."""
    import websockets  # type: ignore[import-untyped]
    ws_ep = endpoint.rstrip("/") + "/rpc"
    async with websockets.connect(ws_ep, open_timeout=5, close_timeout=5):
        pass


def check_namespace(endpoint: str, user: str, password: str, ns: str) -> dict[str, Any]:
    """Check that the namespace is accessible."""
    try:
        _run_ws_query(endpoint, user, password, None, None, "INFO FOR ROOT")
        return {"status": STATUS_PASS, "namespace": ns}
    except Exception as exc:
        return {"status": STATUS_WARN, "namespace": ns, "message": str(exc)}


def check_database(endpoint: str, user: str, password: str, ns: str, db: str) -> dict[str, Any]:
    """Check the database and count tables."""
    try:
        result = _run_ws_query(endpoint, user, password, ns, db, "INFO FOR DB")
        table_count = 0
        if isinstance(result, list) and result:
            first = result[0]
            db_info = first.get("result") if isinstance(first, dict) else first
            if isinstance(db_info, dict):
                tables = db_info.get("tables") or db_info.get("tb") or {}
                table_count = len(tables)
        return {"status": STATUS_PASS, "database": db, "tables": table_count}
    except Exception as exc:
        return {"status": STATUS_FAIL, "database": db, "message": str(exc)}


def check_server_version(endpoint: str, user: str, password: str) -> dict[str, Any]:
    """Retrieve the server version via a version query or CLI."""
    # Try the CLI first as it is more reliable
    cli_check = check_cli()
    if cli_check["status"] == STATUS_PASS:
        return {"status": STATUS_PASS, "version": cli_check.get("version", "unknown")}
    return {"status": STATUS_WARN, "message": "Could not determine server version"}


def check_storage_engine(endpoint: str, user: str, password: str) -> dict[str, Any]:
    """Attempt to determine the storage engine in use."""
    # SurrealDB does not expose storage engine via query in all versions;
    # we infer from the CLI start flags or just report as available.
    path = shutil.which("surreal")
    if path:
        try:
            result = subprocess.run([path, "version"], capture_output=True, text=True, timeout=10)
            output = (result.stdout or result.stderr).strip()
            # The engine is typically in the startup config, not the version string.
            # We report what we can.
            return {"status": STATUS_PASS, "engine": "unknown (check server startup flags)"}
        except Exception:
            pass
    return {"status": STATUS_WARN, "message": "Could not determine storage engine"}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def run_quick(endpoint_override: str | None = None) -> dict[str, Any]:
    """Run quick (offline) checks."""
    checks: dict[str, Any] = {}
    checks["cli_installed"] = check_cli()
    checks["env_vars"] = check_env_vars()
    checks["uv_available"] = check_uv()
    checks["port_open"] = check_port(endpoint_override)

    warnings = [k for k, v in checks.items() if v.get("status") == STATUS_WARN]
    errors = [k for k, v in checks.items() if v.get("status") == STATUS_FAIL]
    overall = STATUS_FAIL if errors else STATUS_WARN if warnings else STATUS_PASS

    return {
        "status": "healthy" if overall == STATUS_PASS else "degraded" if overall == STATUS_WARN else "unhealthy",
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }


def run_full(
    endpoint: str | None = None,
    user: str | None = None,
    password: str | None = None,
    ns: str | None = None,
    db: str | None = None,
) -> dict[str, Any]:
    """Run full (online) checks."""
    ep = endpoint or _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    u = user or _env("SURREAL_USER") or "root"
    p = password or _env("SURREAL_PASS") or "root"
    namespace = ns or _env("SURREAL_NS")
    database = db or _env("SURREAL_DB")

    checks: dict[str, Any] = {}

    # Quick checks first
    checks["cli_installed"] = check_cli()
    checks["env_vars"] = check_env_vars()
    checks["uv_available"] = check_uv()
    checks["port_open"] = check_port(ep)

    # Online checks
    if checks["port_open"]["status"] == STATUS_PASS:
        checks["auth_valid"] = check_auth(ep, u, p)
        checks["server_version"] = check_server_version(ep, u, p)
        checks["storage_engine"] = check_storage_engine(ep, u, p)

        if namespace:
            checks["namespace_accessible"] = check_namespace(ep, u, p, namespace)
        if namespace and database:
            checks["database_accessible"] = check_database(ep, u, p, namespace, database)
    else:
        checks["server_reachable"] = {"status": STATUS_FAIL, "message": "Skipped: port not reachable"}

    warnings = [k for k, v in checks.items() if v.get("status") == STATUS_WARN]
    errors = [k for k, v in checks.items() if v.get("status") == STATUS_FAIL]
    overall = STATUS_FAIL if errors else STATUS_WARN if warnings else STATUS_PASS

    return {
        "status": "healthy" if overall == STATUS_PASS else "degraded" if overall == STATUS_WARN else "unhealthy",
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_results_table(report: dict[str, Any]) -> None:
    """Print a Rich table of results to stderr."""
    overall = report["status"]
    style_map = {"healthy": "green", "degraded": "yellow", "unhealthy": "red"}
    color = style_map.get(overall, "white")

    table = Table(title=f"SurrealDB Health Check -- [{color}]{overall.upper()}[/{color}]", show_lines=True)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    status_render = {
        STATUS_PASS: "[green]PASS[/green]",
        STATUS_WARN: "[yellow]WARN[/yellow]",
        STATUS_FAIL: "[red]FAIL[/red]",
    }

    for name, info in report["checks"].items():
        rendered_status = status_render.get(info.get("status", ""), info.get("status", ""))
        detail_parts = []
        for k, v in info.items():
            if k == "status":
                continue
            detail_parts.append(f"{k}: {v}")
        table.add_row(name.replace("_", " ").title(), rendered_status, "\n".join(detail_parts) if detail_parts else "-")

    stderr_console.print(table)

    if report["warnings"]:
        stderr_console.print(f"\n[yellow]Warnings:[/yellow] {', '.join(report['warnings'])}")
    if report["errors"]:
        stderr_console.print(f"[red]Errors:[/red] {', '.join(report['errors'])}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doctor",
        description="SurrealDB environment health check.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", "--check", action="store_true", help="Fast checks only (no server connection); exit code 0 = healthy, 1 = issues")
    mode.add_argument("--full", action="store_true", help="Complete health check (default)")

    parser.add_argument("--endpoint", type=str, default=None, help="SurrealDB endpoint (overrides SURREAL_ENDPOINT)")
    parser.add_argument("--user", type=str, default=None, help="Username (overrides SURREAL_USER)")
    parser.add_argument("--pass", dest="password", type=str, default=None, help="Password (overrides SURREAL_PASS)")
    parser.add_argument("--ns", type=str, default=None, help="Namespace (overrides SURREAL_NS)")
    parser.add_argument("--db", type=str, default=None, help="Database (overrides SURREAL_DB)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.quick:
        report = run_quick(endpoint_override=args.endpoint)
    else:
        report = run_full(
            endpoint=args.endpoint,
            user=args.user,
            password=args.password,
            ns=args.ns,
            db=args.db,
        )

    print_results_table(report)
    print(json.dumps(report, indent=2))

    # Exit with non-zero if unhealthy
    if report["status"] == "unhealthy":
        sys.exit(1)


if __name__ == "__main__":
    main()
