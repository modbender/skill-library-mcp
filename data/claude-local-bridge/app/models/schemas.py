"""Data models for the Claude Local Bridge API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class ApprovalScope(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"            # recursive
    DIRECTORY_SHALLOW = "directory_shallow"  # single level only


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


class AccessLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"


class AuditAction(str, Enum):
    READ = "read"
    WRITE = "write"
    LIST = "list"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    APPROVAL_REVOKED = "approval_revoked"


# ── Approval Models ───────────────────────────────────────────────────────────

class ApprovalRequest(BaseModel):
    """Inbound request from Claude to access a file or directory."""
    path: str = Field(..., description="Absolute or workspace-relative path")
    scope: ApprovalScope = ApprovalScope.FILE
    access: AccessLevel = AccessLevel.READ
    reason: str = Field("", description="Why Claude needs access (shown to user)")
    ttl_minutes: Optional[int] = Field(
        60, description="Auto-expire approval after N minutes (null = permanent)"
    )


class Approval(BaseModel):
    """A stored approval record."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    path: str
    resolved_path: str = ""
    scope: ApprovalScope
    access: AccessLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    reason: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    file_patterns: list[str] = Field(
        default_factory=list,
        description="Glob patterns to restrict within a directory approval, e.g. ['*.py', '*.js']",
    )


class ApprovalDecision(BaseModel):
    """User's response to an approval request."""
    approved: bool
    file_patterns: list[str] = Field(
        default_factory=list,
        description="Optionally restrict directory approval to specific patterns",
    )
    ttl_minutes: Optional[int] = None  # Override the requested TTL


# ── File Models ───────────────────────────────────────────────────────────────

class FileNode(BaseModel):
    """Single node in a file tree listing."""
    name: str
    path: str
    is_dir: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None
    children: list[FileNode] = Field(default_factory=list)
    approved: bool = False


class FileReadResponse(BaseModel):
    path: str
    content: str
    size: int
    encoding: str = "utf-8"
    modified: datetime
    language: Optional[str] = None  # Detected language hint


class FileWriteRequest(BaseModel):
    path: str
    content: str
    create_if_missing: bool = False
    backup: bool = True  # Create .bak before overwriting


class FileWriteResponse(BaseModel):
    path: str
    bytes_written: int
    backup_path: Optional[str] = None


# ── Audit Models ──────────────────────────────────────────────────────────────

class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: AuditAction
    path: str
    detail: str = ""
    success: bool = True


# ── Config ────────────────────────────────────────────────────────────────────

class BridgeConfig(BaseModel):
    """Runtime configuration."""
    workspace_roots: list[str] = Field(
        default_factory=list,
        description="Directories the bridge is allowed to serve files from",
    )
    host: str = "127.0.0.1"
    port: int = 9120
    token: str = Field(default_factory=lambda: uuid.uuid4().hex)
    max_file_size_mb: int = 10
    default_ttl_minutes: int = 60
    denied_extensions: list[str] = Field(
        default_factory=lambda: [".env", ".pem", ".key", ".p12", ".pfx", ".secret"]
    )
