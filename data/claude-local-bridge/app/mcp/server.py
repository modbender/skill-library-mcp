"""MCP Server for Claude Local Bridge.

Exposes local file operations as MCP tools with approval gating.
Runs alongside the FastAPI HTTP server, sharing the same services.

Uses the FastMCP library for protocol handling.
Transport: SSE (Server-Sent Events) for remote access from Claude web/mobile.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from app.models.schemas import (
    AccessLevel,
    ApprovalRequest,
    ApprovalScope,
    ApprovalStatus,
    AuditAction,
    FileWriteRequest,
)
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.file_service import FileService

logger = logging.getLogger("bridge.mcp")

# ── FastMCP instance ─────────────────────────────────────────────────────────

mcp = FastMCP(
    "Claude Local Bridge",
    instructions=(
        "Bridge to a developer's local workspace. You can browse, read, and "
        "write files — but EVERY file access requires explicit approval from "
        "the workspace owner first. Always request approval before reading or "
        "writing. Approvals are scoped: file, directory, or directory_shallow. "
        "Check existing approvals before making redundant requests."
    ),
)

# ── Service references (set by init()) ────────────────────────────────────────

_file_svc: Optional[FileService] = None
_approval_svc: Optional[ApprovalService] = None
_audit_svc: Optional[AuditService] = None
_notify_callback = None


def init(
    file_svc: FileService,
    approval_svc: ApprovalService,
    audit_svc: AuditService,
    notify_callback=None,
):
    """Wire up services. Called once from main.py before the server starts."""
    global _file_svc, _approval_svc, _audit_svc, _notify_callback
    _file_svc = file_svc
    _approval_svc = approval_svc
    _audit_svc = audit_svc
    _notify_callback = notify_callback


# ═════════════════════════════════════════════════════════════════════════════
#  TOOLS
# ═════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def browse_files(
    path: Optional[str] = None,
    depth: int = 3,
) -> str:
    """Browse the workspace file tree.

    Returns a directory listing showing files and folders in the connected
    workspace. No approval is needed to browse — this only shows names and
    structure, not file contents.

    Args:
        path: Subdirectory to list (omit to list all workspace roots).
        depth: How many levels deep to traverse (1-10, default 3).
    """
    depth = max(1, min(10, depth))

    def checker(p: str) -> bool:
        return _approval_svc.is_approved(p, AccessLevel.READ)

    try:
        nodes = _file_svc.list_tree(
            root_path=path, max_depth=depth, approved_checker=checker
        )
    except PermissionError as e:
        return f"Error: {e}"

    _audit_svc.log(AuditAction.LIST, path or "<all roots>")
    return _format_tree(nodes)


@mcp.tool()
async def request_file_access(
    path: str,
    scope: str = "file",
    access: str = "read",
    reason: str = "",
    ttl_minutes: int = 60,
) -> str:
    """Request approval to access a file or directory.

    The workspace owner must approve before you can read or write.
    This call BLOCKS until the owner approves, denies, or it times out (5 min).

    Args:
        path: File or directory path to request access for.
        scope: "file" for a single file, "directory" for recursive access,
               or "directory_shallow" for one level only.
        access: "read", "write", or "read_write".
        reason: Explain WHY you need access (shown to the workspace owner).
        ttl_minutes: Auto-expire the approval after N minutes (default 60).
    """
    # Validate enums
    try:
        scope_enum = ApprovalScope(scope)
    except ValueError:
        return f"Error: invalid scope '{scope}'. Use: file, directory, directory_shallow"
    try:
        access_enum = AccessLevel(access)
    except ValueError:
        return f"Error: invalid access '{access}'. Use: read, write, read_write"

    # Resolve path
    try:
        resolved = str(_file_svc.resolve_and_validate(path))
    except PermissionError as e:
        return f"Error: {e}"

    # Check if already approved
    existing = _approval_svc.get_approval_for(resolved, access_enum)
    if existing:
        return (
            f"Already approved! Approval {existing.id} covers this path.\n"
            f"  Scope: {existing.scope.value}\n"
            f"  Access: {existing.access.value}\n"
            f"  Expires: {existing.expires_at or 'never'}"
        )

    # Create request
    req = ApprovalRequest(
        path=path,
        scope=scope_enum,
        access=access_enum,
        reason=reason,
        ttl_minutes=ttl_minutes,
    )
    approval = _approval_svc.create_request(req, resolved)
    _audit_svc.log(AuditAction.APPROVAL_REQUESTED, resolved, detail=reason)

    # Notify dashboard
    if _notify_callback:
        try:
            await _notify_callback(approval)
        except Exception:
            pass

    # Wait for decision
    try:
        result = await _approval_svc.wait_for_decision(approval.id, timeout=300)
    except asyncio.TimeoutError:
        return (
            "Timed out — the workspace owner did not respond within 5 minutes.\n"
            "Try again, or ask them to open the dashboard."
        )

    if result.status == ApprovalStatus.APPROVED:
        return (
            f"Approved! You now have {result.access.value} access.\n"
            f"  Path: {result.resolved_path}\n"
            f"  Scope: {result.scope.value}\n"
            f"  Expires: {result.expires_at or 'never'}\n"
            f"  Approval ID: {result.id}"
        )
    else:
        return f"Denied. The workspace owner declined access to {path}."


@mcp.tool()
async def read_file(path: str) -> str:
    """Read the contents of a file.

    Requires an active READ approval. If you don't have one, use
    request_file_access first.

    Args:
        path: Path to the file to read.
    """
    try:
        resolved = str(_file_svc.resolve_and_validate(path))
    except PermissionError as e:
        return f"Error: {e}"

    if not _approval_svc.is_approved(resolved, AccessLevel.READ):
        _audit_svc.log(
            AuditAction.READ, resolved, detail="DENIED — no approval", success=False
        )
        return (
            f"No active read approval for {path}.\n"
            f"Use request_file_access to get approval first."
        )

    try:
        result = _file_svc.read_file(path)
    except FileNotFoundError as e:
        return f"Error: {e}"
    except ValueError as e:
        return f"Error: {e}"

    _audit_svc.log(AuditAction.READ, resolved)

    header = f"── {result.path} ({result.size} bytes"
    if result.language:
        header += f", {result.language}"
    header += ") ──"

    return f"{header}\n{result.content}"


@mcp.tool()
async def write_file(
    path: str,
    content: str,
    create_if_missing: bool = False,
    backup: bool = True,
) -> str:
    """Write content to a file.

    Requires an active WRITE or READ_WRITE approval. If you don't have one,
    use request_file_access first.

    Args:
        path: Path to the file to write.
        content: The full content to write.
        create_if_missing: Create the file if it doesn't exist (default False).
        backup: Create a .bak backup before overwriting (default True).
    """
    try:
        resolved = str(_file_svc.resolve_and_validate(path))
    except PermissionError as e:
        return f"Error: {e}"

    if not _approval_svc.is_approved(resolved, AccessLevel.WRITE):
        _audit_svc.log(
            AuditAction.WRITE, resolved, detail="DENIED — no approval", success=False
        )
        return (
            f"No active write approval for {path}.\n"
            f"Use request_file_access with access='write' first."
        )

    req = FileWriteRequest(
        path=path, content=content, create_if_missing=create_if_missing, backup=backup
    )
    try:
        result = _file_svc.write_file(req)
    except (FileNotFoundError, PermissionError) as e:
        return f"Error: {e}"

    _audit_svc.log(
        AuditAction.WRITE, resolved, detail=f"{result.bytes_written} bytes"
    )

    msg = f"Wrote {result.bytes_written} bytes to {result.path}"
    if result.backup_path:
        msg += f"\nBackup saved: {result.backup_path}"
    return msg


@mcp.tool()
async def list_approvals(include_expired: bool = False) -> str:
    """List all current approvals.

    Shows which files/directories are approved, pending, or denied.

    Args:
        include_expired: Include expired and revoked approvals (default False).
    """
    all_approvals = _approval_svc.list_all(include_expired=include_expired)

    if not all_approvals:
        return "No approvals found. Use request_file_access to request access."

    lines = [f"{'ID':<14} {'Status':<10} {'Access':<12} {'Scope':<18} Path"]
    lines.append("─" * 80)

    for a in all_approvals:
        lines.append(
            f"{a.id:<14} {a.status.value:<10} {a.access.value:<12} "
            f"{a.scope.value:<18} {a.resolved_path}"
        )

    return "\n".join(lines)


@mcp.tool()
async def revoke_approval(approval_id: str) -> str:
    """Revoke an existing approval.

    After revoking, you'll need to request access again.

    Args:
        approval_id: The approval ID to revoke (from list_approvals).
    """
    try:
        approval = _approval_svc.revoke(approval_id)
    except KeyError:
        return f"Error: Approval '{approval_id}' not found."

    _audit_svc.log(AuditAction.APPROVAL_REVOKED, approval.resolved_path)
    return f"Revoked approval {approval_id} for {approval.resolved_path}."


@mcp.tool()
async def view_audit_log(limit: int = 50, path: Optional[str] = None) -> str:
    """View the audit log of all file access events.

    Shows who accessed what, when, and whether it succeeded.

    Args:
        limit: Max entries to return (default 50).
        path: Filter to a specific file path (optional).
    """
    if path:
        entries = _audit_svc.for_path(path, limit)
    else:
        entries = _audit_svc.recent(limit)

    if not entries:
        return "No audit entries yet."

    lines = [f"{'Time':<22} {'Action':<22} {'OK':<5} Path"]
    lines.append("─" * 90)

    for e in entries:
        ts = e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ok = "yes" if e.success else "NO"
        lines.append(f"{ts:<22} {e.action.value:<22} {ok:<5} {e.path}")
        if e.detail:
            lines.append(f"{'':>22} └─ {e.detail}")

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
#  RESOURCES
# ═════════════════════════════════════════════════════════════════════════════


@mcp.resource("bridge://status")
async def bridge_status() -> str:
    """Current bridge server status and configuration."""
    roots = [str(r) for r in _file_svc.roots] if _file_svc else []
    all_approvals = _approval_svc.list_all() if _approval_svc else []
    pending = [a for a in all_approvals if a.status == ApprovalStatus.PENDING]
    active = [a for a in all_approvals if a.status == ApprovalStatus.APPROVED]

    return json.dumps({
        "server": "Claude Local Bridge",
        "workspace_roots": roots,
        "pending_approvals": len(pending),
        "active_approvals": len(active),
        "total_audit_entries": len(_audit_svc.recent(5000)) if _audit_svc else 0,
    }, indent=2)


# ═════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════════════════


def _format_tree(nodes: list, indent: int = 0) -> str:
    """Format FileNode list into a readable tree string."""
    lines = []
    for node in nodes:
        prefix = "  " * indent
        if node.is_dir:
            approved_mark = " [approved]" if node.approved else ""
            lines.append(f"{prefix}📁 {node.name}/{approved_mark}")
            if node.children:
                lines.append(_format_tree(node.children, indent + 1))
        else:
            size_str = f" ({node.size} B)" if node.size is not None else ""
            approved_mark = " ✓" if node.approved else ""
            lines.append(f"{prefix}📄 {node.name}{size_str}{approved_mark}")
    return "\n".join(lines)
