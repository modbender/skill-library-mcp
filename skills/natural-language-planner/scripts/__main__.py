"""
CLI entry point for the Natural Language Planner.

Usage:
    python -m scripts <command> [arguments]

Commands:
    init <workspace_path>       Initialise a new workspace
    dashboard [--port PORT]     Start the dashboard server
    list-tasks [--project ID]   List all tasks
    list-projects               List all projects
    stats                       Show summary statistics
    search <query>              Search tasks
    rebuild-index               Rebuild the search index
    tunnel [workspace_path]     Start a tunnel for remote dashboard access
    export [--output DIR]       Export dashboard as a static HTML snapshot
"""

import sys
import argparse
import json

from .utils import setup_logging
from .file_manager import init_workspace, list_tasks, list_projects
from .config_manager import load_config, set_config_path
from .index_manager import rebuild_index, search_tasks, get_stats
from .dashboard_server import start_dashboard, ensure_dashboard, get_dashboard_url, get_dashboard_port
from .tunnel import start_tunnel, stop_tunnel, get_tunnel_url, detect_tunnel_tool, get_install_instructions
from .export import export_dashboard


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="python -m scripts",
        description="Natural Language Planner — CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = sub.add_parser("init", help="Initialise a new workspace")
    p_init.add_argument("workspace_path", help="Directory for planner data")

    # dashboard
    p_dash = sub.add_parser("dashboard", help="Start the dashboard server")
    p_dash.add_argument("--port", type=int, default=None, help="Port (default: 8080)")
    p_dash.add_argument("--network", action="store_true", help="Bind to all interfaces (0.0.0.0)")
    p_dash.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # list-tasks
    p_lt = sub.add_parser("list-tasks", help="List tasks")
    p_lt.add_argument("--project", default=None, help="Filter by project ID")
    p_lt.add_argument("--status", default=None, help="Filter by status")
    p_lt.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # list-projects
    p_lp = sub.add_parser("list-projects", help="List projects")
    p_lp.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # stats
    p_st = sub.add_parser("stats", help="Show summary statistics")
    p_st.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # search
    p_se = sub.add_parser("search", help="Search tasks")
    p_se.add_argument("query", help="Search query")
    p_se.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # rebuild-index
    p_ri = sub.add_parser("rebuild-index", help="Rebuild the search index")
    p_ri.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # tunnel
    p_tn = sub.add_parser("tunnel", help="Start a tunnel for remote dashboard access")
    p_tn.add_argument("--tool", choices=["cloudflared", "ngrok", "lt"], default=None,
                       help="Tunnel tool to use (default: auto-detect)")
    p_tn.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    # export
    p_ex = sub.add_parser("export", help="Export dashboard as static HTML snapshot")
    p_ex.add_argument("--output", default=None, help="Output directory (default: <workspace>/.nlplanner/export/)")
    p_ex.add_argument("workspace_path", nargs="?", default=None, help="Workspace directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # ── Dispatch ────────────────────────────────────────────

    if args.command == "init":
        path = args.workspace_path
        ok = init_workspace(path)
        if ok:
            print(f"Workspace initialised at: {path}")
        else:
            print("Failed to initialise workspace.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "dashboard":
        _ensure_workspace(args)
        allow_network = getattr(args, "network", False)
        url = start_dashboard(port=args.port, allow_network=allow_network or None)
        if url:
            print(f"Dashboard running at {url}")
            print("Press Ctrl+C to stop.")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping dashboard.")
        else:
            print("Failed to start dashboard.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list-tasks":
        _ensure_workspace(args)
        filters = {}
        if args.status:
            filters["status"] = args.status
        tasks = list_tasks(filter_by=filters or None, project_id=args.project)
        if not tasks:
            print("No tasks found.")
        for t in tasks:
            status = t.get("status", "?")
            priority = t.get("priority", "?")
            due = t.get("due", "")
            due_str = f"  due {due}" if due else ""
            print(f"  [{status}] {t.get('id', '?')}  {t.get('title', '?')}  ({priority}){due_str}")

    elif args.command == "list-projects":
        _ensure_workspace(args)
        projects = list_projects()
        if not projects:
            print("No projects found.")
        for p in projects:
            print(f"  {p.get('id', '?')}  —  {p.get('title', '?')}  [{p.get('status', '?')}]")

    elif args.command == "stats":
        _ensure_workspace(args)
        rebuild_index()
        s = get_stats()
        print(json.dumps(s, indent=2))

    elif args.command == "search":
        _ensure_workspace(args)
        rebuild_index()
        results = search_tasks(args.query)
        if not results:
            print("No results.")
        for t in results:
            print(f"  {t.get('id', '?')}  {t.get('title', '?')}  [{t.get('status', '?')}]")

    elif args.command == "rebuild-index":
        _ensure_workspace(args)
        rebuild_index()
        print("Index rebuilt.")

    elif args.command == "tunnel":
        _ensure_workspace(args)

        # Ensure the dashboard is running first
        dash_url = ensure_dashboard()
        if not dash_url:
            print("Failed to start dashboard. Cannot create tunnel.", file=sys.stderr)
            sys.exit(1)

        port = get_dashboard_port()
        print(f"Dashboard running at {dash_url}")

        # Check if a tool is available
        tool = getattr(args, "tool", None) or detect_tunnel_tool()
        if not tool:
            print("\nNo tunnel tool found on your system.\n")
            print(get_install_instructions())
            sys.exit(1)

        print(f"Starting {tool} tunnel on port {port}...")
        tunnel_url = start_tunnel(port, tool=tool)
        if tunnel_url:
            print(f"\nPublic URL: {tunnel_url}")
            print("\nAnyone with this URL can access your dashboard.")
            print("WARNING: The dashboard has no authentication — share this URL carefully.")
            print("Press Ctrl+C to stop the tunnel.")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping tunnel...")
                stop_tunnel()
                print("Tunnel stopped.")
        else:
            print("Failed to start tunnel.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "export":
        _ensure_workspace(args)
        output_dir = getattr(args, "output", None)
        path = export_dashboard(output_dir=output_dir)
        if path:
            print(f"Dashboard exported to: {path}")
            print("Open this file in a browser, or deploy it to any static hosting service.")
        else:
            print("Failed to export dashboard.", file=sys.stderr)
            sys.exit(1)


def _ensure_workspace(args: argparse.Namespace) -> None:
    """Point the config manager at the workspace, if provided."""
    ws = getattr(args, "workspace_path", None)
    if ws:
        set_config_path(ws)
    else:
        # Try loading existing config to find workspace path
        config = load_config()
        if not config.get("workspace_path"):
            print(
                "No workspace specified. Either pass a path or run 'init' first.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
