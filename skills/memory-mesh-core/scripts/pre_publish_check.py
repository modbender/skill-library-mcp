#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


TEXT_EXT = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".toml",
    ".ini",
    ".cfg",
}

SECRET_PATTERNS = [
    re.compile(r"clh_[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"hf_[A-Za-z0-9]{16,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{10,}", re.IGNORECASE),
]

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


def should_scan(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    if path.suffix.lower() in TEXT_EXT:
        return True
    if path.name in {"SKILL.md", "README.md", "package.json"}:
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-publish compliance check for ClawHub skill.")
    parser.add_argument("--skill-dir", required=True, help="Skill directory path")
    parser.add_argument("--allow-cjk", action="store_true", help="Allow Chinese/CJK characters")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise SystemExit(f"Skill dir not found: {skill_dir}")

    violations = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {"node_modules", ".git", "__pycache__"} for part in path.parts):
            continue
        if not should_scan(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(skill_dir))
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                violations.append({"type": "secret_pattern", "file": rel})
                break
        if not args.allow_cjk and CJK_RE.search(text):
            violations.append({"type": "cjk_detected", "file": rel})

    result = {"ok": len(violations) == 0, "violations": violations}
    print(json.dumps(result, ensure_ascii=False))
    if violations:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
