from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class ManagerAdapter:
    name: str
    title: str
    track_path: Path
    check_fn: Callable[[], dict[str, Any]]


def build_manager_registry(
    *,
    npm_path: Path,
    pnpm_path: Path,
    brew_path: Path,
    check_npm: Callable[[], dict[str, Any]],
    check_pnpm: Callable[[], dict[str, Any]],
    check_brew: Callable[[], dict[str, Any]],
) -> list[ManagerAdapter]:
    """Build canonical manager registry for pkg_maint orchestration."""
    return [
        ManagerAdapter(name="npm", title="NPM", track_path=npm_path, check_fn=check_npm),
        ManagerAdapter(name="pnpm", title="PNPM", track_path=pnpm_path, check_fn=check_pnpm),
        ManagerAdapter(name="brew", title="Brew", track_path=brew_path, check_fn=check_brew),
    ]
