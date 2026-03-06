"""Claude Local Bridge — main entry point.

Usage:
    python -m app.main --roots ~/projects ~/code
    python -m app.main --roots . --port 9120
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.middleware.auth import set_token
from app.models.schemas import BridgeConfig
from app.routers import approvals, audit, files, ws
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.file_service import FileService


def create_app(config: BridgeConfig) -> FastAPI:
    app = FastAPI(
        title="Claude Local Bridge",
        description="Secure local API for Claude mobile app to access code files with approval gating.",
        version="0.1.0",
    )

    # CORS — allow Claude mobile / web to connect
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Lock down in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Services ──────────────────────────────────────────────────────────
    approval_svc = ApprovalService()
    file_svc = FileService(config)
    audit_svc = AuditService()

    # ── Auth ──────────────────────────────────────────────────────────────
    set_token(config.token)

    # ── Wire up HTTP routers ─────────────────────────────────────────────
    files.init(file_svc, approval_svc, audit_svc)
    approvals.init(
        approval_svc,
        file_svc,
        audit_svc,
        notify_callback=ws.broadcast_approval_request,
    )
    audit.init(audit_svc)
    ws.init(approval_svc)

    app.include_router(files.router)
    app.include_router(approvals.router)
    app.include_router(audit.router)
    app.include_router(ws.router)

    # ── MCP Server (mounted on /mcp) ────────────────────────────────────
    try:
        from app.mcp.server import mcp as mcp_server, init as mcp_init

        mcp_init(
            file_svc=file_svc,
            approval_svc=approval_svc,
            audit_svc=audit_svc,
            notify_callback=ws.broadcast_approval_request,
        )

        # Mount the MCP SSE app as a sub-application
        mcp_app = mcp_server.sse_app()
        app.mount("/mcp", mcp_app)

    except ImportError as e:
        import logging
        logging.getLogger("bridge").warning(
            f"MCP server not available (missing deps?): {e}. "
            "Install with: pip install 'mcp[cli]>=1.2.0'"
        )

    # ── Health ────────────────────────────────────────────────────────────
    @app.get("/health", tags=["system"])
    async def health():
        return {
            "status": "ok",
            "workspace_roots": config.workspace_roots,
            "version": "0.1.0",
            "mcp_endpoint": f"http://{config.host}:{config.port}/mcp/sse",
        }

    # ── Dashboard static files (must be last — catch-all mount) ─────────
    dashboard_dir = pathlib.Path(__file__).resolve().parent.parent / "dashboard"
    if dashboard_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

    # Store config on app for reference
    app.state.config = config

    return app


def parse_args() -> BridgeConfig:
    parser = argparse.ArgumentParser(description="Claude Local Bridge API")
    parser.add_argument(
        "--roots",
        nargs="+",
        required=True,
        help="Workspace root directories to expose",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9120)
    parser.add_argument("--max-file-size-mb", type=int, default=10)
    args = parser.parse_args()

    return BridgeConfig(
        workspace_roots=args.roots,
        host=args.host,
        port=args.port,
        max_file_size_mb=args.max_file_size_mb,
    )


def main():
    config = parse_args()
    app = create_app(config)

    mcp_port = config.port
    mcp_url = f"http://{config.host}:{mcp_port}/mcp/sse"

    # Pretty startup banner
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print(Panel.fit(
            f"[bold green]Claude Local Bridge[/bold green]\n\n"
            f"  HTTP API:   http://{config.host}:{config.port}\n"
            f"  MCP (SSE):  {mcp_url}\n"
            f"  Dashboard:  http://{config.host}:{config.port}/\n"
            f"  Roots:      {', '.join(config.workspace_roots)}\n"
            f"  Token:      [bold yellow]{config.token}[/bold yellow]\n\n"
            f"[dim]Add this MCP config to your claude_desktop_config.json:[/dim]\n"
            f'[dim]{{"mcpServers": {{"local-bridge": {{"url": "{mcp_url}"}}}}}}[/dim]',
            title="🔗 Bridge Ready",
            border_style="blue",
        ))
    except ImportError:
        print(f"\n=== Claude Local Bridge ===")
        print(f"  HTTP API:  http://{config.host}:{config.port}")
        print(f"  MCP (SSE): {mcp_url}")
        print(f"  Dashboard: http://{config.host}:{config.port}/")
        print(f"  Token:     {config.token}")
        print(f"  Roots:     {', '.join(config.workspace_roots)}\n")

    uvicorn.run(app, host=config.host, port=config.port, log_level="info")


if __name__ == "__main__":
    main()
