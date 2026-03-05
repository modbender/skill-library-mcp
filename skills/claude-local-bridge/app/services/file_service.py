"""Sandboxed file operations.

All paths are resolved against configured workspace roots.
No path traversal or access outside roots is permitted.
"""

from __future__ import annotations

import mimetypes
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.schemas import (
    BridgeConfig,
    FileNode,
    FileReadResponse,
    FileWriteRequest,
    FileWriteResponse,
)

# Language detection by extension (subset — extend as needed)
EXT_LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".jsx": "jsx",
    ".tsx": "tsx", ".rs": "rust", ".go": "go", ".java": "java", ".kt": "kotlin",
    ".rb": "ruby", ".php": "php", ".c": "c", ".cpp": "cpp", ".h": "c",
    ".cs": "csharp", ".swift": "swift", ".sh": "bash", ".yml": "yaml",
    ".yaml": "yaml", ".json": "json", ".toml": "toml", ".md": "markdown",
    ".html": "html", ".css": "css", ".sql": "sql", ".r": "r",
}


class FileService:
    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self.roots = [Path(r).resolve() for r in config.workspace_roots]

    # ── Path safety ───────────────────────────────────────────────────────

    def resolve_and_validate(self, raw_path: str) -> Path:
        """Resolve a path, ensuring it falls within an allowed workspace root."""
        p = Path(raw_path).expanduser().resolve()

        # Check extension deny-list
        if p.suffix.lower() in self.config.denied_extensions:
            raise PermissionError(f"File type {p.suffix} is blocked for security")

        for root in self.roots:
            try:
                p.relative_to(root)
                return p
            except ValueError:
                continue

        raise PermissionError(
            f"Path {p} is outside all workspace roots: {[str(r) for r in self.roots]}"
        )

    # ── Directory listing ─────────────────────────────────────────────────

    def list_tree(
        self,
        root_path: Optional[str] = None,
        max_depth: int = 3,
        approved_checker=None,
    ) -> list[FileNode]:
        """List files/dirs. If root_path is None, list all workspace roots."""
        targets = (
            [self.resolve_and_validate(root_path)]
            if root_path
            else self.roots
        )
        nodes = []
        for t in targets:
            nodes.append(self._walk(t, depth=0, max_depth=max_depth, checker=approved_checker))
        return nodes

    def _walk(
        self, path: Path, depth: int, max_depth: int, checker=None
    ) -> FileNode:
        is_dir = path.is_dir()
        stat = path.stat() if path.exists() else None
        approved = checker(str(path)) if checker else False

        node = FileNode(
            name=path.name or str(path),
            path=str(path),
            is_dir=is_dir,
            size=stat.st_size if stat and not is_dir else None,
            modified=datetime.fromtimestamp(stat.st_mtime) if stat else None,
            approved=approved,
        )

        if is_dir and depth < max_depth:
            try:
                for child in sorted(path.iterdir()):
                    if child.name.startswith("."):
                        continue  # skip hidden
                    if child.name in ("node_modules", "__pycache__", ".git", "venv", ".venv"):
                        continue
                    node.children.append(
                        self._walk(child, depth + 1, max_depth, checker)
                    )
            except PermissionError:
                pass

        return node

    # ── Read ──────────────────────────────────────────────────────────────

    def read_file(self, raw_path: str) -> FileReadResponse:
        p = self.resolve_and_validate(raw_path)
        if not p.is_file():
            raise FileNotFoundError(f"{p} is not a file")

        size = p.stat().st_size
        if size > self.config.max_file_size_mb * 1024 * 1024:
            raise ValueError(
                f"File exceeds max size of {self.config.max_file_size_mb}MB"
            )

        content = p.read_text(encoding="utf-8")
        lang = EXT_LANG_MAP.get(p.suffix.lower())

        return FileReadResponse(
            path=str(p),
            content=content,
            size=size,
            modified=datetime.fromtimestamp(p.stat().st_mtime),
            language=lang,
        )

    # ── Write ─────────────────────────────────────────────────────────────

    def write_file(self, req: FileWriteRequest) -> FileWriteResponse:
        p = self.resolve_and_validate(req.path)

        if not p.exists() and not req.create_if_missing:
            raise FileNotFoundError(
                f"{p} does not exist (set create_if_missing=true to create)"
            )

        backup_path = None
        if p.exists() and req.backup:
            backup = p.with_suffix(p.suffix + ".bak")
            shutil.copy2(p, backup)
            backup_path = str(backup)

        p.parent.mkdir(parents=True, exist_ok=True)
        written = p.write_text(req.content, encoding="utf-8")

        return FileWriteResponse(
            path=str(p),
            bytes_written=written,
            backup_path=backup_path,
        )
