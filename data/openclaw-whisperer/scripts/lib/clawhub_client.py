"""ClawHub CLI wrapper for skill discovery."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .utils import load_json, which_binary
from .clawhub_cache import load_cache, save_cache, search_cache


@dataclass
class SkillInfo:
    """Represents a ClawHub skill with metadata."""
    slug: str
    name: str
    description: str
    version: str
    author: str
    tags: list[str]
    downloads: int
    verified: bool
    updated_at: str | None


class ClawHubClient:
    """ClawHub CLI wrapper with local caching for skill discovery."""

    def __init__(self):
        """Initialize client and load cache if available."""
        self.cache_data = load_cache()

    def _run_clawhub(self, args: list[str]) -> dict | None:
        """Safe subprocess wrapper for clawhub CLI."""
        try:
            result = subprocess.run(
                ["clawhub"] + args,
                capture_output=True, text=True,
                timeout=30, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    def is_cli_available(self) -> bool:
        """Check if clawhub binary exists in PATH."""
        return which_binary("clawhub") is not None

    def _parse_skill_data(self, data: dict) -> SkillInfo:
        """Convert raw skill data to SkillInfo object."""
        return SkillInfo(
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "0.0.0"),
            author=data.get("author", "unknown"),
            tags=data.get("tags", []),
            downloads=data.get("downloads", 0),
            verified=data.get("verified", False),
            updated_at=data.get("updated_at")
        )

    def search(self, query: str, limit: int = 20) -> list[SkillInfo]:
        """Search for skills using CLI or cache fallback."""
        if self.is_cli_available():
            result = self._run_clawhub(["search", query, "--json", "--limit", str(limit)])
            if result and "skills" in result:
                skills = [self._parse_skill_data(s) for s in result["skills"]]
                if skills:
                    self.cache_data["skills"] = result["skills"]
                    self.cache_data = save_cache(self.cache_data)
                return skills

        # Fallback to cache search
        matches = search_cache(self.cache_data, query, limit)
        return [self._parse_skill_data(s) for s in matches]

    def list_installed(self) -> list[SkillInfo]:
        """List installed skills from CLI or lock file."""
        if self.is_cli_available():
            result = self._run_clawhub(["list", "--json"])
            if result and "skills" in result:
                return [self._parse_skill_data(s) for s in result["skills"]]

        try:
            lock_file = Path.home() / ".clawhub" / "lock.json"
            if lock_file.exists():
                lock_data = load_json(lock_file)
                if "skills" in lock_data:
                    return [self._parse_skill_data(s) for s in lock_data["skills"]]
        except Exception:
            pass
        return []

    def get_skill_info(self, slug: str) -> SkillInfo | None:
        """Lookup skill information by slug."""
        if "skills" in self.cache_data:
            for skill_data in self.cache_data["skills"]:
                if skill_data.get("slug") == slug:
                    return self._parse_skill_data(skill_data)

        if self.is_cli_available():
            result = self._run_clawhub(["info", slug, "--json"])
            if result:
                return self._parse_skill_data(result)
        return None

    def refresh_cache(self) -> bool:
        """Refresh cache by fetching latest skills from registry."""
        if not self.is_cli_available():
            return False

        result = self._run_clawhub(["search", "", "--limit", "100", "--json"])
        if result and "skills" in result:
            self.cache_data["skills"] = result["skills"]
            self.cache_data = save_cache(self.cache_data)
            return True
        return False
