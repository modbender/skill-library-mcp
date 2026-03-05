"""
Local web server for the Natural Language Planner dashboard.

Serves the dashboard single-page app and provides a JSON API for
reading task/project data from the workspace.

Uses only the Python standard library (http.server) so there are no
external dependencies.  For production-style usage consider replacing
with FastAPI or similar, but this works great for local use.
"""

import json
import logging
import mimetypes
import socket
import threading
import time
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs, unquote

from .config_manager import load_config, set_setting, get_setting
from .file_manager import list_projects, list_tasks, get_project, get_task
from .index_manager import rebuild_index, get_stats, search_tasks, get_tasks_due_soon, get_overdue_tasks

logger = logging.getLogger("nlplanner.dashboard")

_server: Optional[HTTPServer] = None
_thread: Optional[threading.Thread] = None
_started_at: float = 0.0


class DashboardHandler(SimpleHTTPRequestHandler):
    """
    HTTP request handler for the dashboard.

    Serves static files from the dashboard directory and handles
    /api/* routes for JSON data.
    """

    def __init__(self, *args, dashboard_dir: str = "", **kwargs):
        self._dashboard_dir = dashboard_dir
        super().__init__(*args, directory=dashboard_dir, **kwargs)

    def do_GET(self) -> None:
        """Route GET requests to the appropriate handler."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self._handle_api(path, parsed.query)
        else:
            # Serve static files from the dashboard directory
            super().do_GET()

    def _handle_api(self, path: str, query_string: str) -> None:
        """Dispatch API requests."""
        params = parse_qs(query_string)

        routes: dict[str, Any] = {
            "/api/stats": self._api_stats,
            "/api/projects": self._api_projects,
            "/api/tasks": self._api_tasks,
            "/api/search": self._api_search,
            "/api/due-soon": self._api_due_soon,
            "/api/overdue": self._api_overdue,
            "/api/health": self._api_health,
        }

        # Dynamic routes: /api/attachment/<project>/<file>, /api/project/<id>, /api/task/<id>
        if path.startswith("/api/attachment/"):
            parts = path.split("/api/attachment/")[1].strip("/").split("/", 1)
            if len(parts) == 2:
                self._api_serve_attachment(unquote(parts[0]), unquote(parts[1]))
            else:
                self._json_response({"error": "Bad attachment path"}, status=400)
            return
        if path.startswith("/api/project/"):
            project_id = path.split("/api/project/")[1].strip("/")
            self._api_single_project(project_id)
            return
        if path.startswith("/api/task/"):
            task_id = path.split("/api/task/")[1].strip("/")
            self._api_single_task(task_id)
            return

        handler = routes.get(path)
        if handler:
            handler(params)
        else:
            self._json_response({"error": "Not found"}, status=404)

    # ── API handlers ───────────────────────────────────────────

    def _api_health(self, params: dict) -> None:
        """Return server health status and uptime."""
        uptime = round(time.time() - _started_at, 1) if _started_at else 0
        self._json_response({
            "status": "ok",
            "uptime_seconds": uptime,
            "port": _server.server_address[1] if _server else None,
        })

    def _api_stats(self, params: dict) -> None:
        rebuild_index()
        self._json_response(get_stats())

    def _api_projects(self, params: dict) -> None:
        projects = list_projects()
        self._json_response(projects)

    def _api_tasks(self, params: dict) -> None:
        project = params.get("project", [None])[0]
        status = params.get("status", [None])[0]
        priority = params.get("priority", [None])[0]
        include_archived = params.get("include_archived", [""])[0].lower() in ("1", "true", "yes")

        filters: dict[str, Any] = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority

        tasks = list_tasks(filter_by=filters if filters else None, project_id=project,
                           include_archived=include_archived)
        self._json_response(tasks)

    def _api_search(self, params: dict) -> None:
        query = params.get("q", [""])[0]
        if not query:
            self._json_response([])
            return
        rebuild_index()
        results = search_tasks(query)
        self._json_response(results)

    def _api_due_soon(self, params: dict) -> None:
        try:
            days = max(1, min(365, int(params.get("days", ["7"])[0])))
        except (ValueError, TypeError):
            days = 7
        rebuild_index()
        self._json_response(get_tasks_due_soon(days))

    def _api_overdue(self, params: dict) -> None:
        rebuild_index()
        self._json_response(get_overdue_tasks())

    def _api_single_project(self, project_id: str) -> None:
        project = get_project(project_id)
        if project:
            self._json_response(project)
        else:
            self._json_response({"error": "Project not found"}, status=404)

    def _api_single_task(self, task_id: str) -> None:
        task = get_task(task_id)
        if task:
            self._json_response(task)
        else:
            self._json_response({"error": "Task not found"}, status=404)

    def _api_serve_attachment(self, project_id: str, filename: str) -> None:
        """Serve a file from project attachments or media directory."""
        config = load_config()
        ws = config.get("workspace_path", "")
        if not ws:
            self._json_response({"error": "Workspace not configured"}, status=500)
            return

        # Security: prevent path traversal in both project_id and filename
        safe_project = Path(project_id).name
        safe_name = Path(filename).name
        ws_root = Path(ws).resolve()

        # Check both locations (backwards compat + new media dir)
        paths_to_try = [
            (ws_root / "projects" / safe_project / "attachments" / safe_name).resolve(),
            (ws_root / "media" / safe_project / safe_name).resolve(),
        ]

        file_path = None
        for candidate in paths_to_try:
            # Ensure the resolved path is still within the workspace
            if not candidate.is_relative_to(ws_root):
                continue
            if candidate.is_file():
                file_path = candidate
                break

        if not file_path:
            self._json_response({"error": "Attachment not found"}, status=404)
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"

        try:
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=10")
            self.end_headers()
            self.wfile.write(data)
        except OSError as e:
            logger.error("Failed to serve attachment %s: %s", file_path, e)
            self._json_response({"error": "Failed to read file"}, status=500)

    # ── Response helpers ───────────────────────────────────────

    def _json_response(self, data: Any, status: int = 200) -> None:
        """Send a JSON response."""
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Redirect access logs to our logger instead of stderr."""
        logger.debug(format, *args)


# ── Internal helpers ──────────────────────────────────────────────

def _resolve_dashboard_dir() -> str:
    """
    Find the dashboard static files directory.

    Looks in the workspace .nlplanner/dashboard first, then falls back to
    the templates/dashboard shipped with the skill.
    """
    config = load_config()
    ws = config.get("workspace_path", "")

    if ws:
        ws_dashboard = Path(ws) / ".nlplanner" / "dashboard"
        if (ws_dashboard / "index.html").exists():
            return str(ws_dashboard)

    # Fallback: templates directory relative to this script
    templates = Path(__file__).parent.parent / "templates" / "dashboard"
    if (templates / "index.html").exists():
        return str(templates)

    raise FileNotFoundError(
        "Dashboard static files not found. Ensure the templates/dashboard/ "
        "directory exists or run init_workspace() first."
    )


def _is_port_available(host: str, port: int) -> bool:
    """Check if a TCP port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def _find_available_port(host: str, start_port: int, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port.

    Tries consecutive ports until one is available.

    Args:
        host: The host to bind to.
        start_port: Port to try first.
        max_attempts: How many consecutive ports to try.

    Returns:
        An available port number.

    Raises:
        OSError: If no port is available within the range.
    """
    for offset in range(max_attempts):
        port = start_port + offset
        if _is_port_available(host, port):
            return port
    raise OSError(
        f"No available port found in range {start_port}-{start_port + max_attempts - 1}"
    )


def _resolve_host() -> str:
    """Return the bind host based on configuration."""
    config = load_config()
    allow_network = config.get("settings", {}).get("dashboard_allow_network", False)
    return "0.0.0.0" if allow_network else "127.0.0.1"


def _get_lan_ip() -> str:
    """Best-effort detection of the machine's LAN IP address.

    Returns ``"127.0.0.1"`` if the address cannot be determined (e.g.
    no network interfaces are up).
    """
    try:
        # Open a UDP socket to an external address (nothing is actually sent)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


# ── Public functions ──────────────────────────────────────────────

def start_dashboard(port: Optional[int] = None, allow_network: Optional[bool] = None) -> str:
    """
    Start the dashboard web server in a background thread.

    If the requested port is occupied, automatically tries the next
    consecutive ports until one is available.

    Args:
        port: Port number (default: from config or 8080).
        allow_network: If True, bind to 0.0.0.0 (all interfaces).
                       If None, reads from config.

    Returns:
        The dashboard URL, or empty string on failure.

    Example:
        >>> url = start_dashboard()
        >>> print(url)
        http://localhost:8080
    """
    global _server, _thread, _started_at

    if _server is not None:
        logger.info("Dashboard is already running.")
        return get_dashboard_url()

    config = load_config()

    if port is None:
        port = config.get("settings", {}).get("dashboard_port", 8080)

    if allow_network is None:
        allow_network = config.get("settings", {}).get("dashboard_allow_network", False)

    host = "0.0.0.0" if allow_network else "127.0.0.1"
    try:
        dashboard_dir = _resolve_dashboard_dir()
    except FileNotFoundError as e:
        logger.error("%s", e)
        return ""
    handler = partial(DashboardHandler, dashboard_dir=dashboard_dir)

    # Try the configured port first, then search for an available one
    try:
        actual_port = _find_available_port(host, port)
        if actual_port != port:
            logger.info(
                "Port %d is occupied, using port %d instead.", port, actual_port
            )
    except OSError as e:
        logger.error("Could not find an available port: %s", e)
        return ""

    try:
        _server = HTTPServer((host, actual_port), handler)
    except OSError as e:
        logger.error("Could not start dashboard on port %d: %s", actual_port, e)
        return ""

    _started_at = time.time()
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()

    if allow_network:
        lan_ip = _get_lan_ip()
        url = f"http://{lan_ip}:{actual_port}"
    else:
        url = f"http://localhost:{actual_port}"
    logger.info("Dashboard started at %s (serving from %s)", url, dashboard_dir)

    # Persist the actual port so subsequent calls know where it is
    if actual_port != port:
        set_setting("dashboard_port", actual_port)

    return url


def ensure_dashboard(port: Optional[int] = None, allow_network: Optional[bool] = None) -> str:
    """
    Ensure the dashboard is running and healthy.

    This is the recommended function for the agent to call. It:
    1. Returns the existing URL if the server is already running.
    2. Starts a new server if not running, with automatic port recovery.
    3. Verifies the server is responsive.

    Args:
        port: Optional port override.
        allow_network: If True, bind to all interfaces (``0.0.0.0``)
                       so the dashboard is reachable from other devices
                       on the LAN.  If None, reads from config.

    Returns:
        The dashboard URL, or empty string on failure.

    Example:
        >>> url = ensure_dashboard()
        >>> print(url)
        http://localhost:8080
    """
    if is_running():
        return get_dashboard_url()

    url = start_dashboard(port=port, allow_network=allow_network)
    if not url:
        return ""

    # Brief pause to let the server thread start accepting connections
    time.sleep(0.1)

    if is_running():
        logger.info("Dashboard ensured at %s", url)
        return url

    logger.warning("Dashboard started but may not be healthy.")
    return url


def stop_dashboard() -> None:
    """Stop the running dashboard server and release its port."""
    global _server, _thread, _started_at

    if _server is None:
        logger.info("Dashboard is not running.")
        return

    _server.shutdown()       # Stop the serve_forever() loop
    _server.server_close()   # Close the socket — releases the port immediately
    _server = None
    _thread = None
    _started_at = 0.0
    logger.info("Dashboard stopped.")


def restart_dashboard(allow_network: Optional[bool] = None) -> str:
    """
    Stop and restart the dashboard server on the **same port**.

    Use this after skill updates that change Python scripts, dashboard
    templates, or any other server-side code.  It fully tears down the
    existing server (including closing the socket so the port is freed
    immediately) and starts a fresh one, re-resolving the dashboard
    directory and reloading configuration.

    Args:
        allow_network: If True, bind to all interfaces (``0.0.0.0``).
                       If None, reads from config.

    Returns:
        The new dashboard URL, or empty string on failure.

    Example:
        >>> url = restart_dashboard()
        >>> print(url)
        http://localhost:8080
    """
    port = get_dashboard_port() or None
    stop_dashboard()
    return ensure_dashboard(port=port, allow_network=allow_network)


def get_dashboard_url() -> str:
    """
    Get the URL of the running dashboard.

    When the server is bound to all interfaces (``0.0.0.0``), returns
    the LAN IP so the URL is directly usable from other devices on the
    network.  When bound to ``127.0.0.1``, returns ``localhost``.

    Returns:
        The dashboard URL, or an empty string if not running.
    """
    if _server is None:
        return ""
    host, port = _server.server_address
    if host == "0.0.0.0":
        return f"http://{_get_lan_ip()}:{port}"
    return f"http://localhost:{port}"


def get_dashboard_port() -> int:
    """
    Get the port of the running dashboard.

    Returns:
        The port number, or 0 if not running.
    """
    if _server is None:
        return 0
    return _server.server_address[1]


def is_running() -> bool:
    """Check whether the dashboard server is currently running."""
    return _server is not None


def get_uptime() -> float:
    """
    Get dashboard uptime in seconds.

    Returns:
        Uptime in seconds, or 0.0 if not running.
    """
    if not is_running() or _started_at == 0.0:
        return 0.0
    return time.time() - _started_at
