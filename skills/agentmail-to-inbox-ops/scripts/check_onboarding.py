#!/usr/bin/env python3
"""Validate OpenClaw onboarding readiness for this skill."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = ROOT / "SKILL.md"
ENV_EXAMPLE = ROOT / ".env.example"


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def ok(self, message: str) -> None:
        self.passes.append(message)

    def err(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_frontmatter(text: str) -> dict[str, str]:
    # Minimal parser: key: value pairs from YAML frontmatter block.
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return {}

    block = m.group(1)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def main() -> int:
    c = Check()

    if not SKILL_FILE.exists():
        c.err("Missing SKILL.md")
        return finish(c)

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)

    # Required frontmatter fields
    skill_name = fm.get("name", "")
    if skill_name:
        c.ok(f"frontmatter name found: {skill_name}")
    else:
        c.err("SKILL.md frontmatter missing required `name`")

    if fm.get("description"):
        c.ok("frontmatter description found")
    else:
        c.err("SKILL.md frontmatter missing required `description`")

    # OpenClaw metadata checks (best-practice for onboarding/preflight)
    metadata_raw = fm.get("metadata", "")
    if metadata_raw:
        c.ok("frontmatter metadata found")
        if "openclaw" in metadata_raw:
            c.ok("metadata contains openclaw block")
        else:
            c.warn("metadata present but does not include `openclaw` block")

        if "requires" in metadata_raw:
            c.ok("metadata includes requires preflight")
        else:
            c.warn("metadata missing `requires` (bins/env preflight)")

        if "primaryEnv" in metadata_raw:
            c.ok("metadata includes primaryEnv")
        else:
            c.warn("metadata missing `primaryEnv`")
    else:
        c.warn("SKILL.md frontmatter missing `metadata` (recommended for onboarding checks)")

    # Folder name consistency
    folder_name = ROOT.name
    if skill_name:
        if folder_name == skill_name:
            c.ok("folder name matches SKILL name")
        else:
            c.warn(
                f"folder name mismatch: current `{folder_name}` vs required `{skill_name}`; "
                "install/sync into a folder named exactly as SKILL name"
            )

    # Required skill resources used by this project
    required_files = [
        ROOT / "scripts" / "list_messages.py",
        ROOT / "scripts" / "get_message.py",
        ROOT / "scripts" / "download_attachments.py",
        ROOT / "scripts" / "analyze_attachment.py",
        ROOT / "scripts" / "reply_messages.py",
        ROOT / "scripts" / "set_read_state.py",
        ROOT / "references" / "agentmail-api-notes.md",
    ]
    for path in required_files:
        if path.exists():
            c.ok(f"found: {path.relative_to(ROOT)}")
        else:
            c.err(f"missing required file: {path.relative_to(ROOT)}")

    if ENV_EXAMPLE.exists():
        env_text = ENV_EXAMPLE.read_text(encoding="utf-8")
        if "AGENTMAIL_API_KEY" in env_text:
            c.ok(".env.example includes AGENTMAIL_API_KEY")
        else:
            c.err(".env.example missing AGENTMAIL_API_KEY")
    else:
        c.warn(".env.example missing")

    return finish(c)


def finish(c: Check) -> int:
    for msg in c.passes:
        print(f"✅ {msg}")
    for msg in c.warnings:
        print(f"⚠️  {msg}")
    for msg in c.errors:
        print(f"❌ {msg}")

    print("\n---")
    print(f"pass={len(c.passes)} warn={len(c.warnings)} error={len(c.errors)}")

    if c.errors:
        print("NOT READY")
        return 1

    if c.warnings:
        print("READY WITH WARNINGS")
        return 0

    print("READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
