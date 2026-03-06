# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Upload files to a Gemini File Search store.

Supports single files and recursive directory uploads with MIME type
validation, smart-sync (skip unchanged), and progress tracking.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import time
import uuid
from pathlib import Path

from google import genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console(stderr=True)

# ---------------------------------------------------------------------------
# MIME type maps (derived from docs/file-search-mime-types.md)
# ---------------------------------------------------------------------------

# Tier 1: validated MIME types that work natively
VALIDATED_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".xml": "application/xml",
    ".txt": "text/plain",
    ".text": "text/plain",
    ".log": "text/plain",
    ".out": "text/plain",
    ".env": "text/plain",
    ".gitignore": "text/plain",
    ".gitattributes": "text/plain",
    ".dockerignore": "text/plain",
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".mdown": "text/markdown",
    ".mkd": "text/markdown",
    ".c": "text/x-c",
    ".h": "text/x-c",
    ".java": "text/x-java",
    ".kt": "text/x-kotlin",
    ".kts": "text/x-kotlin",
    ".go": "text/x-go",
    ".py": "text/x-python",
    ".pyw": "text/x-python",
    ".pyx": "text/x-python",
    ".pyi": "text/x-python",
    ".pl": "text/x-perl",
    ".pm": "text/x-perl",
    ".t": "text/x-perl",
    ".pod": "text/x-perl",
    ".lua": "text/x-lua",
    ".erl": "text/x-erlang",
    ".hrl": "text/x-erlang",
    ".tcl": "text/x-tcl",
    ".bib": "text/x-bibtex",
    ".diff": "text/x-diff",
}

# Tier 2: known text extensions that fall back to text/plain
TEXT_FALLBACK_EXTENSIONS: set[str] = {
    # JavaScript / TypeScript
    ".js", ".mjs", ".cjs", ".jsx",
    ".ts", ".mts", ".cts", ".tsx",
    ".json", ".jsonc", ".json5",
    # Web
    ".css", ".scss", ".sass", ".less", ".styl",
    ".vue", ".svelte", ".astro",
    # Shell / Scripting
    ".sh", ".bash", ".zsh", ".fish", ".ksh",
    ".bat", ".cmd", ".ps1", ".psm1",
    # Config
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".properties", ".editorconfig", ".prettierrc",
    ".eslintrc", ".babelrc", ".npmrc",
    # Other languages
    ".rb", ".php", ".rs", ".swift", ".scala", ".clj",
    ".ex", ".exs", ".hs", ".ml", ".fs", ".fsx",
    ".r", ".jl", ".nim", ".zig", ".dart",
    ".coffee", ".elm", ".v", ".cr", ".groovy",
    ".gradle", ".cmake", ".makefile", ".mk",
    ".dockerfile", ".tf", ".hcl",
    ".sql", ".graphql", ".gql", ".proto",
    ".csv", ".tsv", ".rst", ".adoc", ".tex", ".latex",
    ".sbt", ".pom",
}

# Tier 3: binary extensions that must be rejected
BINARY_EXTENSIONS: set[str] = {
    ".exe", ".dll", ".so", ".dylib", ".a", ".lib",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mkv", ".mov", ".flac", ".ogg",
    ".class", ".pyc", ".pyo", ".o", ".obj",
    ".wasm", ".bin", ".dat",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    for var in ("GEMINI_DEEP_RESEARCH_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        key = os.environ.get(var)
        if key:
            return key
    console.print("[red]Error:[/red] No API key found.")
    console.print("Set one of: GEMINI_DEEP_RESEARCH_API_KEY, GOOGLE_API_KEY, GEMINI_API_KEY")
    sys.exit(1)


def get_client() -> genai.Client:
    return genai.Client(api_key=get_api_key())


def get_state_path() -> Path:
    return Path(".gemini-research.json")


def load_state() -> dict:
    path = get_state_path()
    if not path.exists():
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}


def save_state(state: dict) -> None:
    get_state_path().write_text(json.dumps(state, indent=2) + "\n")


def resolve_mime(filepath: Path) -> str | None:
    """Return MIME type for a file, or None if unsupported.

    Tier 1: validated native types.
    Tier 2: known text files -> text/plain fallback.
    Tier 3: binary -> None (rejected).
    """
    ext = filepath.suffix.lower()
    # Check special dotfiles (no suffix but known names)
    name_lower = filepath.name.lower()
    if name_lower in (".gitignore", ".gitattributes", ".dockerignore",
                       ".editorconfig", ".prettierrc", ".eslintrc",
                       ".babelrc", ".npmrc", ".env"):
        return VALIDATED_MIME.get(name_lower, "text/plain")

    if ext in VALIDATED_MIME:
        return VALIDATED_MIME[ext]
    if ext in TEXT_FALLBACK_EXTENSIONS:
        return "text/plain"
    if ext in BINARY_EXTENSIONS:
        return None

    # Unknown extension: try system mimetypes, accept text/* only
    guessed, _ = mimetypes.guess_type(str(filepath))
    if guessed and guessed.startswith("text/"):
        return "text/plain"

    # Default: reject unknown
    return None


def file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file for smart-sync."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# Sensitive files that should never be uploaded
_SENSITIVE_NAMES: set[str] = {
    ".env", ".env.local", ".env.production", ".env.development",
    "credentials.json", "service-account.json", "secrets.json",
    "secrets.yaml", "secrets.yml", ".npmrc", ".pypirc", ".netrc",
    "id_rsa", "id_ed25519", "id_ecdsa",
}
_SENSITIVE_EXTENSIONS: set[str] = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks"}
_SKIP_DIRS: set[str] = {"__pycache__", "node_modules", ".git", ".tox", "dist", "build"}


def collect_files(
    root: Path,
    extensions: set[str] | None = None,
) -> list[Path]:
    """Recursively collect uploadable files from a directory.

    Filters out sensitive files and common build directories.
    """
    files: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        if extensions and p.suffix.lower() not in extensions:
            continue
        name_lower = p.name.lower()
        if name_lower in _SENSITIVE_NAMES or name_lower.startswith(".env"):
            console.print(f"[yellow]Skipping sensitive file:[/yellow] {p.name}")
            continue
        if p.suffix.lower() in _SENSITIVE_EXTENSIONS:
            console.print(f"[yellow]Skipping sensitive file:[/yellow] {p.name}")
            continue
        if resolve_mime(p) is not None:
            files.append(p)
    return files


def load_hash_cache(state: dict, store_name: str) -> dict[str, str]:
    """Load the per-store file hash cache from state."""
    return state.get("_hashCache", {}).get(store_name, {})


def save_hash_cache(state: dict, store_name: str, cache: dict[str, str]) -> None:
    state.setdefault("_hashCache", {})[store_name] = cache
    save_state(state)

# ---------------------------------------------------------------------------
# Upload logic
# ---------------------------------------------------------------------------

def upload_files(
    client: genai.Client,
    files: list[Path],
    store_name: str,
    smart_sync: bool = False,
) -> dict:
    """Upload a list of files to a store, returning an operation summary."""
    state = load_state()
    hash_cache = load_hash_cache(state, store_name)

    completed = 0
    skipped = 0
    failed = 0
    failed_list: list[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Uploading...", total=len(files))

        for filepath in files:
            rel = str(filepath)
            mime = resolve_mime(filepath)
            if mime is None:
                failed += 1
                failed_list.append({"file": rel, "error": "Unsupported file type"})
                progress.advance(task)
                continue

            # Compute hash for smart-sync comparison and cache update
            current_hash = file_hash(filepath)

            # Smart-sync: skip if hash unchanged
            if smart_sync and hash_cache.get(rel) == current_hash:
                skipped += 1
                progress.update(task, description=f"Skipped: {filepath.name}")
                progress.advance(task)
                continue

            try:
                progress.update(task, description=f"Uploading: {filepath.name}")
                operation = client.file_search_stores.upload_to_file_search_store(
                    file=str(filepath),
                    file_search_store_name=store_name,
                    config={"display_name": filepath.name},
                )
                # Poll until done
                while not operation.done:
                    time.sleep(2)
                    operation = client.operations.get(operation)

                completed += 1
                # Always update hash cache on successful upload (enables future smart-sync)
                hash_cache[rel] = current_hash
            except Exception as exc:
                failed += 1
                failed_list.append({"file": rel, "error": str(exc)})

            progress.advance(task)

    # Always persist hash cache so future --smart-sync runs can skip unchanged files
    save_hash_cache(state, store_name, hash_cache)

    return {
        "totalFiles": len(files),
        "completedFiles": completed,
        "skippedFiles": skipped,
        "failedFiles": failed,
        "failedFilesList": failed_list,
    }

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_upload(args: argparse.Namespace) -> None:
    """Upload files or directories to a file search store."""
    client = get_client()
    target = Path(args.path).resolve()
    store_name: str = args.store_name
    smart_sync: bool = args.smart_sync
    extensions: set[str] | None = None
    if args.extensions:
        # Accept both comma-separated and space-separated (via nargs)
        raw = args.extensions if isinstance(args.extensions, list) else [args.extensions]
        parts: list[str] = []
        for item in raw:
            parts.extend(item.replace(",", " ").split())
        extensions = {
            ext if ext.startswith(".") else f".{ext}"
            for ext in parts
            if ext.strip()
        }

    if not target.exists():
        console.print(f"[red]Error:[/red] Path not found: {target}")
        sys.exit(1)

    # Collect files
    if target.is_file():
        mime = resolve_mime(target)
        if mime is None:
            console.print(f"[red]Error:[/red] Unsupported file type: {target.suffix}")
            sys.exit(1)
        files = [target]
    elif target.is_dir():
        files = collect_files(target, extensions)
        if not files:
            console.print("[yellow]No uploadable files found.[/yellow]")
            sys.exit(0)
        console.print(f"Found [bold]{len(files)}[/bold] files to upload.")
    else:
        console.print(f"[red]Error:[/red] Path is not a file or directory: {target}")
        sys.exit(1)

    # Record operation in state
    op_id = str(uuid.uuid4())[:8]
    state = load_state()
    state.setdefault("uploadOperations", {})[op_id] = {
        "id": op_id,
        "status": "in_progress",
        "path": str(target),
        "storeName": store_name,
        "smartSync": smart_sync,
        "totalFiles": len(files),
        "completedFiles": 0,
        "skippedFiles": 0,
        "failedFiles": 0,
        "failedFilesList": [],
        "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    save_state(state)

    console.print(f"Upload operation: [bold]{op_id}[/bold]")
    result = upload_files(client, files, store_name, smart_sync)

    # Update operation in state
    state = load_state()
    op = state["uploadOperations"][op_id]
    op.update(result)
    op["status"] = "failed" if result["failedFiles"] == result["totalFiles"] else "completed"
    op["completedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_state(state)

    # Summary
    console.print()
    console.print(f"[green]Completed:[/green] {result['completedFiles']}")
    console.print(f"[yellow]Skipped:[/yellow]   {result['skippedFiles']}")
    console.print(f"[red]Failed:[/red]    {result['failedFiles']}")
    if result["failedFilesList"]:
        console.print("[red]Failed files:[/red]")
        for f in result["failedFilesList"]:
            console.print(f"  {f['file']}: {f['error']}")

    print(json.dumps({"operationId": op_id, **result}))


def cmd_status(args: argparse.Namespace) -> None:
    """Check upload operation status from local state."""
    state = load_state()
    ops = state.get("uploadOperations", {})
    op = ops.get(args.operation_id)
    if not op:
        console.print(f"[red]Error:[/red] Operation not found: {args.operation_id}")
        sys.exit(1)
    print(json.dumps(op, indent=2))

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="upload",
        description="Upload files to a Gemini File Search store",
    )
    parser.add_argument("path", nargs="?", help="Path to file or directory to upload")
    parser.add_argument("store_name", nargs="?", help="Resource name of the file search store")
    parser.add_argument(
        "--smart-sync", action="store_true",
        help="Skip uploading files that have not changed (hash comparison)",
    )
    parser.add_argument(
        "--extensions", nargs="*",
        help="File extensions to include (comma or space separated, e.g. py,ts,md or .py .ts .md)",
    )
    parser.add_argument(
        "--status",
        dest="operation_id",
        help="Check status of an upload operation instead of uploading",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.operation_id:
        cmd_status(args)
        return

    if not args.path or not args.store_name:
        parser.error("path and store_name are required for upload (or use --status)")

    cmd_upload(args)


if __name__ == "__main__":
    main()
