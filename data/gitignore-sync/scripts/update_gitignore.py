#!/usr/bin/env python3
"""
Update .gitignore by combining:
1) Templates found in user prompt text / explicit template list
2) Templates detected from repository files

Then fetch canonical rules from the gitignore.io API and write them into a
managed block in .gitignore.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_BASE = "https://www.toptal.com/developers/gitignore/api"
BEGIN_MARKER = "# >>> gitignore-sync managed block >>>"
END_MARKER = "# <<< gitignore-sync managed block <<<"

TOKEN_ALIASES = {
    "flutter": "flutter",
    "dart": "dart",
    "firebase": "firebase",
    "android": "android",
    "ios": "xcode",
    "xcode": "xcode",
    "swift": "swift",
    "kotlin": "kotlin",
    "java": "java",
    "python": "python",
    "node": "node",
    "nodejs": "node",
    "javascript": "node",
    "typescript": "node",
    "react": "node",
    "nextjs": "node",
    "next": "node",
    "pnpm": "node",
    "yarn": "node",
    "npm": "node",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "terraform": "terraform",
    "vscode": "visualstudiocode",
    "visualstudiocode": "visualstudiocode",
    "idea": "jetbrains",
    "jetbrains": "jetbrains",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create/update .gitignore")
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository root that contains .gitignore (default: current directory).",
    )
    parser.add_argument(
        "--prompt-text",
        default="",
        help="Raw user prompt text used to infer template names.",
    )
    parser.add_argument(
        "--services",
        default="",
        help="Comma-separated template names explicitly requested by user.",
    )
    parser.add_argument(
        "--api-base",
        default=API_BASE,
        help=f"API base URL (default: {API_BASE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected templates and fetched content without writing .gitignore.",
    )
    parser.add_argument(
        "--rules-file",
        default="",
        help="Optional local file with ignore rules. Use instead of API fetch for offline testing.",
    )
    return parser.parse_args()


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        v = value.strip().lower()
        if not v or v in seen:
            continue
        out.append(v)
        seen.add(v)
    return out


def extract_templates_from_text(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9_+-]+", text.lower())
    templates = [TOKEN_ALIASES[t] for t in tokens if t in TOKEN_ALIASES]
    return unique_preserve_order(templates)


def parse_services_arg(services: str) -> list[str]:
    if not services:
        return []
    raw = [part.strip().lower() for part in services.split(",")]
    normalized: list[str] = []
    for item in raw:
        if not item:
            continue
        normalized.append(TOKEN_ALIASES.get(item, item))
    return unique_preserve_order(normalized)


def detect_repo_templates(repo: Path) -> list[str]:
    detected: list[str] = []

    def add(template: str) -> None:
        if template not in detected:
            detected.append(template)

    if (repo / "pubspec.yaml").exists():
        add("flutter")
        add("dart")
    if (repo / "android").exists():
        add("android")
    if (repo / "ios").exists():
        add("xcode")
    if (repo / "firebase.json").exists():
        add("firebase")
    if (repo / "package.json").exists():
        add("node")
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists():
        add("python")
    if (repo / "go.mod").exists():
        add("go")
    if (repo / "Cargo.toml").exists():
        add("rust")
    if (repo / ".terraform").exists() or list(repo.glob("*.tf")):
        add("terraform")
    if (repo / ".vscode").exists():
        add("visualstudiocode")
    if (repo / ".idea").exists():
        add("jetbrains")
    return detected


def fetch_gitignore(templates: list[str], api_base: str) -> str:
    joined = ",".join(templates)
    url = f"{api_base.rstrip('/')}/{quote(joined, safe=',')}"
    request = Request(
        url,
        headers={
            "User-Agent": "gitignore-sync/1.0 (+https://www.toptal.com/developers/gitignore)",
            "Accept": "text/plain",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            data = response.read().decode("utf-8")
            if not data.strip():
                raise RuntimeError("API returned empty response.")
            return data.strip() + "\n"
    except HTTPError as exc:
        raise RuntimeError(f"API HTTP error {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"API connection error: {exc.reason}") from exc


def render_managed_block(templates: list[str], rules: str) -> str:
    header = f"{BEGIN_MARKER} templates={','.join(templates)}\n"
    return f"{header}{rules.rstrip()}\n{END_MARKER}\n"


def replace_or_append_managed_block(existing: str, block: str) -> str:
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(BEGIN_MARKER)}.*?^\s*{re.escape(END_MARKER)}\s*\n?"
    )
    if pattern.search(existing):
        return pattern.sub(block, existing, count=1)

    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing:
        existing += "\n"
    return existing + block


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    gitignore_path = repo / ".gitignore"

    if not repo.exists() or not repo.is_dir():
        print(f"Repository path is invalid: {repo}", file=sys.stderr)
        return 2

    templates = unique_preserve_order(
        parse_services_arg(args.services)
        + extract_templates_from_text(args.prompt_text)
        + detect_repo_templates(repo)
    )

    if not templates:
        print(
            "No templates detected. Pass --services or --prompt-text with tool names.",
            file=sys.stderr,
        )
        return 2

    if args.rules_file:
        rules_path = Path(args.rules_file).resolve()
        if not rules_path.exists():
            print(f"Rules file does not exist: {rules_path}", file=sys.stderr)
            return 2
        rules = rules_path.read_text(encoding="utf-8")
    else:
        try:
            rules = fetch_gitignore(templates, args.api_base)
        except RuntimeError as exc:
            print(f"Failed to fetch template rules: {exc}", file=sys.stderr)
            return 1

    block = render_managed_block(templates, rules)
    existing = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    updated = replace_or_append_managed_block(existing, block)

    if args.dry_run:
        print("Templates:", ",".join(templates))
        print(block)
        return 0

    gitignore_path.write_text(updated, encoding="utf-8")
    print(f"Updated {gitignore_path} with templates: {','.join(templates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
