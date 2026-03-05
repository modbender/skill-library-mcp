"""
orgo_client.py — Reusable Python wrapper for the Orgo API.

Usage:
    from orgo_client import OrgoClient, OrgoComputer

    client = OrgoClient(api_key="sk_live_...")
    computer = client.create_computer(workspace_id="...", name="agent-1")
    computer.wait_until_ready()
    computer.click(100, 200)
    computer.type("Hello world")
    result = computer.run_bash("ls -la")
    img_b64 = computer.screenshot()
    computer.stop()
    computer.delete(force=True)
"""

from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass
from typing import Any, Literal, Optional

import requests
from requests import Response, Session

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.orgo.ai/api"

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_DEFAULT_TIMEOUT = 30          # seconds per HTTP call
_MAX_RETRIES = 5
_BACKOFF_BASE = 1.5            # exponential backoff multiplier
_BACKOFF_MAX = 60.0            # cap on wait between retries

MouseButton = Literal["left", "right"]
ScrollDirection = Literal["up", "down"]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class OrgoError(Exception):
    """Base exception for all Orgo errors."""

class OrgoAuthError(OrgoError):
    """Raised on 401 – bad or missing API key."""

class OrgoNotFoundError(OrgoError):
    """Raised on 404 – resource does not exist."""

class OrgoForbiddenError(OrgoError):
    """Raised on 403 – caller lacks permission."""

class OrgoBadRequestError(OrgoError):
    """Raised on 400 – malformed request payload."""

class OrgoServerError(OrgoError):
    """Raised on 5xx after all retries are exhausted."""

class OrgoTimeoutError(OrgoError):
    """Raised when polling exceeds the requested timeout."""

class OrgoConfirmationError(OrgoError):
    """Raised when a destructive action is called without the required flag."""


# ---------------------------------------------------------------------------
# Low-level HTTP session with retry / backoff
# ---------------------------------------------------------------------------

class _OrgoSession:
    """Thin wrapper around :class:`requests.Session` with auth + retry logic."""

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(self, path: str, **kwargs: Any) -> dict:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, json: Optional[dict] = None, **kwargs: Any) -> dict:
        return self._request("POST", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> dict:
        return self._request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Internal retry loop
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: int = _DEFAULT_TIMEOUT,
        _attempt: int = 0,
        **kwargs: Any,
    ) -> dict:
        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            resp: Response = self._session.request(
                method, url, timeout=timeout, **kwargs
            )
        except requests.ConnectionError as exc:
            return self._maybe_retry(method, path, _attempt, exc, timeout=timeout, **kwargs)
        except requests.Timeout as exc:
            return self._maybe_retry(method, path, _attempt, exc, timeout=timeout, **kwargs)

        if resp.status_code in _RETRYABLE_STATUS:
            wait = self._backoff(resp, _attempt)
            logger.warning(
                "%s %s → %d (attempt %d/%d); retrying in %.1fs",
                method, url, resp.status_code, _attempt + 1, _MAX_RETRIES, wait,
            )
            if _attempt >= _MAX_RETRIES:
                raise OrgoServerError(
                    f"{method} {url} failed with {resp.status_code} after "
                    f"{_MAX_RETRIES} retries: {resp.text}"
                )
            time.sleep(wait)
            return self._request(method, path, timeout=timeout, _attempt=_attempt + 1, **kwargs)

        self._raise_for_status(resp)
        return resp.json() if resp.content else {}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _backoff(resp: Response, attempt: int) -> float:
        # Honour Retry-After header when present
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), _BACKOFF_MAX)
            except ValueError:
                pass
        return min(_BACKOFF_BASE ** attempt, _BACKOFF_MAX)

    def _maybe_retry(
        self, method: str, path: str, attempt: int, exc: Exception, **kwargs: Any
    ) -> dict:
        if attempt >= _MAX_RETRIES:
            raise OrgoServerError(
                f"{method} {self._base_url}/{path} failed after {_MAX_RETRIES} retries"
            ) from exc
        wait = min(_BACKOFF_BASE ** attempt, _BACKOFF_MAX)
        logger.warning(
            "%s %s/%s → network error (attempt %d/%d); retrying in %.1fs: %s",
            method, self._base_url, path, attempt + 1, _MAX_RETRIES, wait, exc,
        )
        time.sleep(wait)
        return self._request(method, path, _attempt=attempt + 1, **kwargs)

    @staticmethod
    def _raise_for_status(resp: Response) -> None:
        if resp.ok:
            return
        try:
            msg = resp.json().get("error", resp.text)
        except Exception:
            msg = resp.text

        status = resp.status_code
        if status == 400:
            raise OrgoBadRequestError(msg)
        if status == 401:
            raise OrgoAuthError(msg)
        if status == 403:
            raise OrgoForbiddenError(msg)
        if status == 404:
            raise OrgoNotFoundError(msg)
        raise OrgoError(f"HTTP {status}: {msg}")


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WorkspaceInfo:
    id: str
    name: str
    created_at: str
    computer_count: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "WorkspaceInfo":
        return cls(
            id=d["id"],
            name=d["name"],
            created_at=d["created_at"],
            computer_count=d.get("computer_count", 0),
        )


@dataclass
class ComputerInfo:
    id: str
    name: str
    workspace_id: str
    status: str
    os: str = "linux"
    ram: int = 4
    cpu: int = 2
    gpu: str = "none"
    url: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ComputerInfo":
        return cls(
            id=d["id"],
            name=d["name"],
            workspace_id=d["workspace_id"],
            status=d["status"],
            os=d.get("os", "linux"),
            ram=d.get("ram", 4),
            cpu=d.get("cpu", 2),
            gpu=d.get("gpu", "none"),
            url=d.get("url", ""),
            created_at=d.get("created_at", ""),
        )


@dataclass
class BashResult:
    output: str
    success: bool


@dataclass
class ExecResult:
    output: str
    success: bool


@dataclass
class StreamStatus:
    status: str          # idle | streaming | terminated
    start_time: Optional[str] = None
    pid: Optional[int] = None


@dataclass
class FileRecord:
    id: str
    filename: str


# ---------------------------------------------------------------------------
# OrgoComputer — actions on a single cloud VM
# ---------------------------------------------------------------------------

class OrgoComputer:
    """
    High-level handle for a single Orgo cloud computer.

    Obtain an instance via :class:`OrgoClient`:

        client = OrgoClient(api_key="...")
        computer = client.create_computer(workspace_id="...", name="agent-1")
        computer.wait_until_ready()

    Or wrap an existing computer ID:

        computer = OrgoComputer(session, computer_id="a3bb189e-...")
    """

    def __init__(self, session: _OrgoSession, computer_id: str) -> None:
        self._s = session
        self.id = computer_id

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def info(self) -> ComputerInfo:
        """Return current metadata / status for this computer."""
        return ComputerInfo.from_dict(self._s.get(f"/computers/{self.id}"))

    def start(self) -> None:
        """Start a stopped computer (state is preserved)."""
        self._s.post(f"/computers/{self.id}/start")
        logger.info("Computer %s starting.", self.id)

    def stop(self) -> None:
        """Stop the computer. Stopped computers don't incur charges."""
        self._s.post(f"/computers/{self.id}/stop")
        logger.info("Computer %s stopped.", self.id)

    def restart(self) -> None:
        """Restart the computer (stop + start)."""
        self._s.post(f"/computers/{self.id}/restart")
        logger.info("Computer %s restarting.", self.id)

    def delete(self, *, force: bool = False) -> None:
        """
        Permanently delete this computer.

        Requires ``force=True`` to prevent accidental nukes.

        Example::

            computer.delete(force=True)
        """
        if not force:
            raise OrgoConfirmationError(
                "Deleting a computer is irreversible. "
                "Pass force=True to confirm."
            )
        self._s.delete(f"/computers/{self.id}")
        logger.info("Computer %s deleted.", self.id)

    # ------------------------------------------------------------------
    # Smart polling
    # ------------------------------------------------------------------

    def wait_until_ready(
        self,
        *,
        timeout: float = 120,
        poll_interval: float = 3.0,
        ready_statuses: tuple[str, ...] = ("running",),
        terminal_error_statuses: tuple[str, ...] = ("error", "failed"),
    ) -> ComputerInfo:
        """
        Block until the computer reaches a *ready* status.

        Uses adaptive polling: starts at *poll_interval* seconds and doubles
        every 5 polls, capped at 15 s, to avoid hammering the API during
        long cold-starts.

        Args:
            timeout: Maximum seconds to wait before raising
                     :class:`OrgoTimeoutError`.
            poll_interval: Starting interval between status checks (seconds).
            ready_statuses: Statuses considered "ready" (default: ``running``).
            terminal_error_statuses: Statuses that abort polling immediately.

        Returns:
            The :class:`ComputerInfo` at the moment it became ready.

        Raises:
            OrgoTimeoutError: Timeout exceeded without reaching a ready status.
            OrgoError: Computer entered a terminal error state.
        """
        deadline = time.monotonic() + timeout
        interval = poll_interval
        polls = 0

        while True:
            info = self.info()
            if info.status in ready_statuses:
                logger.info("Computer %s is ready (status=%s).", self.id, info.status)
                return info
            if info.status in terminal_error_statuses:
                raise OrgoError(
                    f"Computer {self.id} entered terminal status '{info.status}'."
                )

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise OrgoTimeoutError(
                    f"Computer {self.id} did not become ready within {timeout}s "
                    f"(last status: {info.status!r})."
                )

            wait = min(interval, remaining)
            logger.debug(
                "Computer %s status=%r; polling again in %.1fs.",
                self.id, info.status, wait,
            )
            time.sleep(wait)
            polls += 1
            # Double interval every 5 polls, cap at 15 s
            if polls % 5 == 0:
                interval = min(interval * 2, 15.0)

    # ------------------------------------------------------------------
    # Mouse
    # ------------------------------------------------------------------

    def click(
        self,
        x: int,
        y: int,
        *,
        button: MouseButton = "left",
        double: bool = False,
    ) -> None:
        """
        Click at pixel coordinate *(x, y)*.

        Args:
            x: Pixels from the left edge.
            y: Pixels from the top edge.
            button: ``"left"`` (default) or ``"right"``.
            double: ``True`` for a double-click.
        """
        self._s.post(
            f"/computers/{self.id}/click",
            json={"x": x, "y": y, "button": button, "double": double},
        )

    def right_click(self, x: int, y: int) -> None:
        """Convenience wrapper for a right-click at *(x, y)*."""
        self.click(x, y, button="right")

    def double_click(self, x: int, y: int) -> None:
        """Convenience wrapper for a double-click at *(x, y)*."""
        self.click(x, y, double=True)

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        *,
        button: MouseButton = "left",
        duration: float = 0.5,
    ) -> None:
        """
        Click-drag from *(start_x, start_y)* to *(end_x, end_y)*.

        Args:
            duration: Drag duration in seconds.
        """
        self._s.post(
            f"/computers/{self.id}/drag",
            json={
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "button": button,
                "duration": duration,
            },
        )

    def scroll(
        self,
        direction: ScrollDirection,
        amount: int = 3,
    ) -> None:
        """
        Scroll the mouse wheel.

        Args:
            direction: ``"up"`` or ``"down"``.
            amount: Number of scroll clicks (default 3).
        """
        self._s.post(
            f"/computers/{self.id}/scroll",
            json={"direction": direction, "amount": amount},
        )

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def type(self, text: str) -> None:
        """
        Type *text* into the focused element.

        Args:
            text: The string to type (supports Unicode).
        """
        self._s.post(f"/computers/{self.id}/type", json={"text": text})

    def key(self, key: str) -> None:
        """
        Press a key or key combination.

        Examples::

            computer.key("Enter")
            computer.key("ctrl+c")
            computer.key("ctrl+shift+t")

        Supported keys: Enter, Tab, Escape, Backspace, Delete, Up, Down,
        Left, Right, Home, End, PageUp, PageDown, F1–F12, and combinations
        using ``ctrl+``, ``alt+``, ``shift+`` prefixes.
        """
        self._s.post(f"/computers/{self.id}/key", json={"key": key})

    # ------------------------------------------------------------------
    # Screen
    # ------------------------------------------------------------------

    def screenshot(self, *, decode: bool = False) -> str | bytes:
        """
        Capture the current screen.

        Args:
            decode: If ``True``, return raw PNG ``bytes``; otherwise return
                    the raw base-64 data-URI string.

        Returns:
            Base-64 encoded PNG data-URI, or decoded ``bytes`` when
            ``decode=True``.
        """
        data = self._s.get(f"/computers/{self.id}/screenshot")
        img: str = data["image"]
        if decode:
            # Strip the data-URI prefix if present
            if img.startswith("data:"):
                img = img.split(",", 1)[1]
            return base64.b64decode(img)
        return img

    def save_screenshot(self, path: str) -> None:
        """
        Capture a screenshot and save it to *path* as a PNG file.

        Args:
            path: Local filesystem path, e.g. ``"screen.png"``.
        """
        png_bytes = self.screenshot(decode=True)
        with open(path, "wb") as fh:
            fh.write(png_bytes)  # type: ignore[arg-type]
        logger.debug("Screenshot saved to %s.", path)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_bash(self, command: str) -> BashResult:
        """
        Execute *command* in a Bash shell on the computer.

        Returns:
            :class:`BashResult` with ``.output`` and ``.success``.

        Raises:
            OrgoError: If the server reports ``success=False``.
        """
        data = self._s.post(
            f"/computers/{self.id}/bash", json={"command": command}
        )
        result = BashResult(output=data.get("output", ""), success=data.get("success", False))
        if not result.success:
            raise OrgoError(f"Bash command failed:\n{result.output}")
        return result

    def run_python(self, code: str, *, timeout: int = 10) -> ExecResult:
        """
        Execute Python *code* on the computer.

        Args:
            code: Python source code to execute.
            timeout: Maximum execution time in seconds (default 10).

        Returns:
            :class:`ExecResult` with ``.output`` and ``.success``.

        Raises:
            OrgoError: If the server reports ``success=False``.
        """
        data = self._s.post(
            f"/computers/{self.id}/exec", json={"code": code, "timeout": timeout}
        )
        result = ExecResult(output=data.get("output", ""), success=data.get("success", False))
        if not result.success:
            raise OrgoError(f"Python exec failed:\n{result.output}")
        return result

    # ------------------------------------------------------------------
    # Wait
    # ------------------------------------------------------------------

    def wait(self, duration: float) -> None:
        """
        Instruct the computer to pause for *duration* seconds (max 60).

        This is an *on-device* wait sent to the computer; it differs from
        :meth:`wait_until_ready`, which polls for a status transition.
        """
        if duration > 60:
            raise ValueError("Orgo wait endpoint caps at 60 seconds.")
        self._s.post(f"/computers/{self.id}/wait", json={"duration": duration})

    # ------------------------------------------------------------------
    # VNC
    # ------------------------------------------------------------------

    def vnc_password(self) -> str:
        """Return the VNC password for direct client access."""
        return self._s.get(f"/computers/{self.id}/vnc-password")["password"]

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def stream_start(self, connection_name: str) -> None:
        """Start RTMP streaming to *connection_name*."""
        self._s.post(
            f"/computers/{self.id}/stream/start",
            json={"connection_name": connection_name},
        )

    def stream_status(self) -> StreamStatus:
        """Return current streaming status."""
        data = self._s.get(f"/computers/{self.id}/stream/status")
        return StreamStatus(
            status=data["status"],
            start_time=data.get("start_time"),
            pid=data.get("pid"),
        )

    def stream_stop(self) -> None:
        """Stop any active RTMP stream."""
        self._s.post(f"/computers/{self.id}/stream/stop")

    # ------------------------------------------------------------------
    # Files (computer-scoped helpers)
    # ------------------------------------------------------------------

    def export_file(self, remote_path: str) -> tuple[FileRecord, str]:
        """
        Export a file from the computer's filesystem.

        Args:
            remote_path: Path on the computer, e.g. ``"Desktop/results.txt"``.

        Returns:
            A tuple of (:class:`FileRecord`, signed_download_url).
        """
        data = self._s.post(
            "/files/export",
            json={"desktopId": self.id, "path": remote_path},
        )
        record = FileRecord(
            id=data["file"]["id"], filename=data["file"]["filename"]
        )
        return record, data["url"]

    def list_files(self, workspace_id: str) -> list[dict]:
        """List files associated with this computer in *workspace_id*."""
        return self._s.get(
            f"/files?projectId={workspace_id}&desktopId={self.id}"
        ).get("files", [])

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "OrgoComputer":
        return self

    def __exit__(self, *_: Any) -> None:
        """Stop (but do not delete) the computer when leaving the context."""
        try:
            self.stop()
        except OrgoError as exc:
            logger.warning("Could not stop computer %s on exit: %s", self.id, exc)

    def __repr__(self) -> str:
        return f"OrgoComputer(id={self.id!r})"


# ---------------------------------------------------------------------------
# OrgoClient — workspace + computer management
# ---------------------------------------------------------------------------

class OrgoClient:
    """
    Entry-point for the Orgo API.

    Args:
        api_key: Your ``sk_live_...`` secret key.
        base_url: Override the API base URL (useful for testing).

    Example::

        client = OrgoClient(api_key="sk_live_...")

        # Create a workspace
        ws = client.create_workspace("my-project")

        # Launch a computer
        computer = client.create_computer(
            workspace_id=ws.id,
            name="agent-1",
            ram=8,
            cpu=4,
        )
        computer.wait_until_ready()
        computer.click(100, 200)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
    ) -> None:
        self._s = _OrgoSession(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # Workspaces
    # ------------------------------------------------------------------

    def create_workspace(self, name: str) -> WorkspaceInfo:
        """Create a new workspace named *name*."""
        data = self._s.post("/workspaces", json={"name": name})
        logger.info("Workspace created: %s (%s)", data["name"], data["id"])
        return WorkspaceInfo.from_dict(data)

    def list_workspaces(self) -> list[WorkspaceInfo]:
        """Return all workspaces for the authenticated user."""
        data = self._s.get("/workspaces")
        return [WorkspaceInfo.from_dict(w) for w in data.get("workspaces", [])]

    def get_workspace(self, workspace_id: str) -> WorkspaceInfo:
        """Fetch a workspace by its UUID."""
        return WorkspaceInfo.from_dict(self._s.get(f"/workspaces/{workspace_id}"))

    def delete_workspace(self, workspace_id: str, *, force: bool = False) -> None:
        """
        Delete a workspace **and all its computers**.

        Requires ``force=True`` — this action **cannot be undone**.

        Example::

            client.delete_workspace(ws.id, force=True)
        """
        if not force:
            raise OrgoConfirmationError(
                "Deleting a workspace destroys all its computers and cannot be "
                "undone. Pass force=True to confirm."
            )
        self._s.delete(f"/workspaces/{workspace_id}")
        logger.info("Workspace %s deleted.", workspace_id)

    # ------------------------------------------------------------------
    # Computers
    # ------------------------------------------------------------------

    def create_computer(
        self,
        workspace_id: str,
        name: str,
        *,
        os: str = "linux",
        ram: int = 4,
        cpu: int = 2,
        gpu: str = "none",
        wait_until_ready: bool = False,
        ready_timeout: float = 120,
    ) -> OrgoComputer:
        """
        Create a new cloud computer and return an :class:`OrgoComputer` handle.

        Args:
            workspace_id: UUID of the parent workspace.
            name: Unique name within the workspace.
            os: Operating system (currently only ``"linux"``).
            ram: RAM in GB — one of 4, 8, 16, 32, 64.
            cpu: CPU cores — one of 2, 4, 8, 16.
            gpu: GPU type — ``"none"``, ``"a10"``, ``"l40s"``,
                 ``"a100-40gb"``, or ``"a100-80gb"``.
            wait_until_ready: If ``True``, block until the computer is
                              running before returning.
            ready_timeout: Seconds to wait when *wait_until_ready* is set.

        Returns:
            An :class:`OrgoComputer` bound to the new computer.
        """
        data = self._s.post(
            "/computers",
            json={
                "workspace_id": workspace_id,
                "name": name,
                "os": os,
                "ram": ram,
                "cpu": cpu,
                "gpu": gpu,
            },
        )
        logger.info("Computer created: %s (%s) — status=%s", name, data["id"], data["status"])
        computer = OrgoComputer(self._s, data["id"])
        if wait_until_ready:
            computer.wait_until_ready(timeout=ready_timeout)
        return computer

    def get_computer(self, computer_id: str) -> OrgoComputer:
        """
        Return an :class:`OrgoComputer` handle for an existing computer ID.

        Does not make a network call — use :meth:`OrgoComputer.info` to
        verify the computer still exists.
        """
        return OrgoComputer(self._s, computer_id)

    def list_computers(self, workspace_id: str) -> list[ComputerInfo]:
        """List all computers in *workspace_id*."""
        data = self._s.get(f"/workspaces/{workspace_id}")
        # GET /workspaces/{id} includes the workspace's computers
        return [ComputerInfo.from_dict(c) for c in data.get("computers", [])]

    # ------------------------------------------------------------------
    # Files (workspace-scoped)
    # ------------------------------------------------------------------

    def upload_file(
        self,
        local_path: str,
        workspace_id: str,
        *,
        computer_id: Optional[str] = None,
    ) -> dict:
        """
        Upload a local file (max 10 MB) to the workspace.

        Args:
            local_path: Path to the file on the local machine.
            workspace_id: Target workspace UUID.
            computer_id: Optional — associate the file with a specific computer.

        Returns:
            Raw response dict from the API.
        """
        # Use the underlying session directly so requests sets the multipart
        # boundary correctly (don't send Content-Type: application/json here).
        session = self._s._session
        url = f"{self._s._base_url}/files/upload"
        form: dict[str, str] = {"projectId": workspace_id}
        if computer_id:
            form["desktopId"] = computer_id
        with open(local_path, "rb") as fh:
            resp = session.post(url, files={"file": fh}, data=form)
        self._s._raise_for_status(resp)
        return resp.json()

    def download_file_url(self, file_id: str) -> str:
        """Return a signed download URL for *file_id* (expires in 1 hour)."""
        return self._s.get(f"/files/download?id={file_id}")["url"]

    def delete_file(self, file_id: str) -> None:
        """Permanently delete *file_id*."""
        self._s.delete(f"/files/delete?id={file_id}")

