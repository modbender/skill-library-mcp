"""File Browser app routes.

Provides:
  GET  /list?path=<rel>&show_hidden=0|1  → directory listing
  GET  /read?path=<rel>                  → file content (text)
  GET  /download?path=<rel>              → file download
"""
from __future__ import annotations

import mimetypes
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

# Root path — defaults to home directory
_root: Path = Path.home()


def configure(root: str | None = None, **kwargs) -> None:
    """Called by server.py at startup to inject configuration."""
    global _root
    if root:
        _root = Path(root).expanduser().resolve()
    else:
        _root = Path.home()


def _resolve_safe(rel_path: str) -> Path:
    """Resolve rel_path under the root. Raises 403 if path escapes."""
    if not rel_path or rel_path == "/":
        return _root

    candidate = (_root / rel_path).resolve()
    try:
        candidate.relative_to(_root)
    except ValueError:
        raise HTTPException(403, "Path outside allowed root")
    return candidate


def _entry_info(p: Path) -> dict:
    """Build a file entry dict."""
    try:
        st = p.stat()
    except OSError:
        return {"name": p.name, "is_dir": False, "size": None, "modified": None, "mime": None}

    is_dir = stat.S_ISDIR(st.st_mode)
    mime = None
    if not is_dir:
        guessed, _ = mimetypes.guess_type(p.name)
        mime = guessed

    return {
        "name": p.name,
        "is_dir": is_dir,
        "size": st.st_size if not is_dir else None,
        "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        "mime": mime,
    }


def _fmt_size(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    if b < 1024 ** 3:
        return f"{b / 1024**2:.1f} MB"
    return f"{b / 1024**3:.1f} GB"


@router.get("/list")
async def list_dir(
    path: str = Query(default=""),
    show_hidden: int = Query(default=0),
):
    """List a directory."""
    resolved = _resolve_safe(path)

    if not resolved.exists():
        raise HTTPException(404, f"Not found: {path}")

    if not resolved.is_dir():
        raise HTTPException(400, "Not a directory")

    try:
        children = list(resolved.iterdir())
    except PermissionError:
        raise HTTPException(403, "Permission denied")

    entries = []
    for child in sorted(children, key=lambda p: (not p.is_dir(), p.name.lower())):
        if child.name in ('.', '..'):
            continue
        if not show_hidden and child.name.startswith("."):
            continue
        entries.append(_entry_info(child))

    # Return full absolute path for display
    return {
        "path": str(resolved),
        "root": str(_root),
        "entries": entries,
    }


@router.get("/read")
async def read_file(path: str = Query(...)):
    """Read text file content (first 500KB)."""
    resolved = _resolve_safe(path)

    if not resolved.exists():
        raise HTTPException(404, "File not found")
    if resolved.is_dir():
        raise HTTPException(400, "Cannot read a directory")

    # Check size
    size = resolved.stat().st_size
    if size > 512 * 1024:
        content = resolved.read_bytes()[:512 * 1024].decode("utf-8", errors="replace")
        truncated = True
    else:
        content = resolved.read_text(errors="replace")
        truncated = False

    mime, _ = mimetypes.guess_type(resolved.name)

    return {
        "name": resolved.name,
        "path": path,
        "size": size,
        "size_human": _fmt_size(size),
        "mime": mime,
        "content": content,
        "truncated": truncated,
    }


@router.get("/download")
async def download(path: str = Query(...)):
    """Download a file."""
    resolved = _resolve_safe(path)

    if not resolved.exists():
        raise HTTPException(404, "File not found")
    if resolved.is_dir():
        raise HTTPException(400, "Cannot download a directory")

    mime, _ = mimetypes.guess_type(resolved.name)
    media_type = mime or "application/octet-stream"

    return FileResponse(
        path=str(resolved),
        filename=resolved.name,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{resolved.name}"'},
    )


if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn

    standalone_app = FastAPI(title="File Browser")
    standalone_app.include_router(router, prefix="/api/files")
    configure()

    from fastapi.staticfiles import StaticFiles
    dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.isdir(dist):
        standalone_app.mount("/app/file-browser", StaticFiles(directory=dist, html=True), name="static")

    uvicorn.run(standalone_app, host="0.0.0.0", port=8802)
