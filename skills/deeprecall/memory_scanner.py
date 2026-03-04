"""
Memory Scanner — Discovers and indexes agent memory/workspace files.

Scans the OpenClaw agent workspace to find memory-related files,
builds a lightweight manifest for RLM to navigate efficiently.
"""

import json
import re
from pathlib import Path
from typing import Optional


# Files that are part of the agent's "soul" (identity)
SOUL_FILES = {"SOUL.md", "IDENTITY.md"}

# Files that are part of the agent's "mind" (memory + context)
MIND_FILES = {"MEMORY.md", "USER.md", "TOOLS.md", "HEARTBEAT.md", "AGENTS.md"}

# Directories to skip when scanning workspace
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", "target", "dist", "build",
    "fast-rlm", "deep-recall", ".deno", ".cache", ".npm",
}

# File extensions to skip (binary / non-readable)
SKIP_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".pyc", ".pyo", ".so", ".dylib", ".dll",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".woff", ".woff2", ".ttf", ".eot",
    ".lock",
}

# Max file size to include (skip very large files)
MAX_FILE_SIZE = 100_000  # 100KB


def extract_headers(content: str, max_headers: int = 15) -> list[str]:
    """Extract markdown headers from content."""
    headers = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            header = line.lstrip("#").strip()
            if header and len(header) > 1:
                headers.append(header)
                if len(headers) >= max_headers:
                    break
    return headers


def extract_key_terms(content: str, max_terms: int = 10) -> list[str]:
    """Extract bold terms from markdown as key topics."""
    terms = re.findall(r'\*\*(.+?)\*\*', content)
    # Filter out very short or very long terms
    terms = [t for t in terms if 2 < len(t) < 60]
    return terms[:max_terms]


class MemoryFile:
    """Represents a single discovered memory file."""
    
    def __init__(self, path: Path, workspace: Path):
        self.path = path
        self.rel_path = str(path.relative_to(workspace))
        self.content = path.read_text(errors="replace")
        self.size = len(self.content)
        self.headers = extract_headers(self.content)
        self.key_terms = extract_key_terms(self.content)
        
        # Classify the file
        if path.name in SOUL_FILES:
            self.category = "soul"
        elif path.name in MIND_FILES:
            self.category = "mind"
        elif "memory" in str(path.relative_to(workspace)).lower():
            self.category = "daily-log"
        else:
            self.category = "workspace"
    
    def to_dict(self) -> dict:
        return {
            "path": self.rel_path,
            "category": self.category,
            "chars": self.size,
            "headers": self.headers,
            "key_terms": self.key_terms[:5],
        }
    
    def to_context_block(self) -> str:
        """Format as a context block for RLM ingestion."""
        return (
            f"\n=== FILE: {self.rel_path} "
            f"({self.category}, {self.size:,} chars) ===\n"
            f"{self.content}"
        )


class MemoryScanner:
    """
    Scans an OpenClaw workspace to discover and index memory files.
    
    Categorizes files into:
    - soul: Identity files (SOUL.md, IDENTITY.md) — who the agent IS
    - mind: Memory files (MEMORY.md, USER.md, etc.) — what the agent KNOWS
    - daily-log: Daily memory logs (memory/*.md) — what HAPPENED
    - workspace: Other relevant files — project context
    """
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or Path(
            os.environ.get("OPENCLAW_WORKSPACE", 
                          os.path.expanduser("~/.openclaw/workspace"))
        )
        self.files: list[MemoryFile] = []
        self._scanned = False
    
    def scan(self, scope: str = "memory") -> "MemoryScanner":
        """
        Scan the workspace for memory files.
        
        Scopes:
            - "memory": MEMORY.md + daily logs (memory/*.md) + mind files
            - "identity": Soul + mind files only (small, fast)
            - "project": All readable workspace files
            - "all": Everything
        
        Returns self for chaining.
        """
        self.files = []
        
        if scope in ("memory", "identity", "all"):
            # Soul files
            for name in SOUL_FILES:
                f = self.workspace / name
                if f.exists():
                    self.files.append(MemoryFile(f, self.workspace))
            
            # Mind files
            for name in MIND_FILES:
                f = self.workspace / name
                if f.exists():
                    self.files.append(MemoryFile(f, self.workspace))
        
        if scope in ("memory", "all"):
            # Daily logs
            memory_dir = self.workspace / "memory"
            if memory_dir.exists():
                for f in sorted(memory_dir.glob("*.md"), reverse=True):
                    self.files.append(MemoryFile(f, self.workspace))
        
        if scope in ("project", "all"):
            # Workspace files (skip already-added files)
            already_added = {f.path for f in self.files}
            for f in sorted(self.workspace.rglob("*")):
                if (f.is_file() 
                    and f not in already_added
                    and not any(sd in f.parts for sd in SKIP_DIRS)
                    and f.suffix.lower() not in SKIP_EXTENSIONS
                    and f.stat().st_size <= MAX_FILE_SIZE):
                    try:
                        self.files.append(MemoryFile(f, self.workspace))
                    except Exception:
                        pass  # Skip unreadable files
        
        self._scanned = True
        return self
    
    def get_manifest(self) -> str:
        """
        Generate a text manifest of all discovered files.
        This goes at the top of the RLM context so it can plan navigation.
        """
        if not self._scanned:
            self.scan()
        
        total_chars = sum(f.size for f in self.files)
        
        lines = [
            f"=== MEMORY MANIFEST ===",
            f"Total: {len(self.files)} files, {total_chars:,} characters",
            f"",
        ]
        
        # Group by category
        categories = {}
        for f in self.files:
            categories.setdefault(f.category, []).append(f)
        
        for cat in ["soul", "mind", "daily-log", "workspace"]:
            if cat in categories:
                lines.append(f"[{cat.upper()}]")
                for f in categories[cat]:
                    topics = ", ".join(f.headers[:3]) if f.headers else "(no headers)"
                    lines.append(f"  {f.rel_path} ({f.size:,} chars) — {topics}")
                lines.append("")
        
        lines.append("Use Python string operations to search through file contents below.")
        lines.append("Each file is delimited by '=== FILE: <path> ===' headers.")
        
        return "\n".join(lines)
    
    def get_context(self) -> str:
        """
        Build the full context string for RLM: manifest + all file contents.
        """
        if not self._scanned:
            self.scan()
        
        parts = [self.get_manifest()]
        for f in self.files:
            parts.append(f.to_context_block())
        
        return "\n".join(parts)
    
    def get_index(self) -> dict:
        """Return a JSON-serializable index of all files."""
        if not self._scanned:
            self.scan()
        
        return {
            "total_files": len(self.files),
            "total_chars": sum(f.size for f in self.files),
            "files": [f.to_dict() for f in self.files],
        }


# Need this for the import in MemoryScanner.__init__
import os

if __name__ == "__main__":
    scanner = MemoryScanner()
    scanner.scan(scope="memory")
    
    print(scanner.get_manifest())
    print(f"\n{'='*60}")
    
    idx = scanner.get_index()
    print(f"\n📋 Index: {idx['total_files']} files, {idx['total_chars']:,} chars")
    for f in idx["files"]:
        terms = ", ".join(f["headers"][:3]) if f["headers"] else "—"
        print(f"  [{f['category']:10s}] {f['path']:30s} {f['chars']:>6,} chars | {terms}")
