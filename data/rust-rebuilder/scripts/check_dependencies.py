#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CODEX_SKILLS_DIR = Path.home() / ".codex" / "skills"
CODEX_CONFIG_FILE = Path.home() / ".codex" / "config.toml"

GROK_SKILL_REPO = "https://github.com/Frankieli123/grok-skill"
GROK_MCP_REPO = "https://github.com/GuDaStudio/GrokSearch"
GITHUB_HELPER_REPO = "https://github.com/dandandujie/github-helper"


def is_skill_installed(skill_name: str) -> bool:
    skill_path = CODEX_SKILLS_DIR / skill_name / "SKILL.md"
    return skill_path.exists()


def has_grok_mcp() -> bool:
    if not CODEX_CONFIG_FILE.exists():
        return False
    content = CODEX_CONFIG_FILE.read_text(encoding="utf-8", errors="ignore")
    return "[mcp_servers.grok-search]" in content


def build_report() -> dict[str, object]:
    has_grok_skill = is_skill_installed("grok-search")
    has_helper_skill = is_skill_installed("github-helper")
    report = {
        "has_grok_search_skill": has_grok_skill,
        "has_grok_search_mcp": has_grok_mcp(),
        "has_github_helper_skill": has_helper_skill,
        "ready": False,
        "install_guide": [],
    }
    if not (report["has_grok_search_skill"] or report["has_grok_search_mcp"]):
        report["install_guide"].append(
            "缺少 grok-search（skill 或 mcp）。skill 仓库: "
            f"{GROK_SKILL_REPO}；mcp 仓库: {GROK_MCP_REPO}"
        )
    if not has_helper_skill:
        report["install_guide"].append(
            "缺少 github-helper skill，请先安装后再执行重写。仓库地址: "
            f"{GITHUB_HELPER_REPO}"
        )
    report["ready"] = len(report["install_guide"]) == 0
    return report


def main() -> int:
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
