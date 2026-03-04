#!/usr/bin/env python3
"""
prepare_release.py -- Prepare a skill release by bumping version, generating
changelog, validating quality, and producing a release summary.

Usage:
    python prepare_release.py .agents/skills/clean-code --minor
    python prepare_release.py .agents/skills/clean-code --major
    python prepare_release.py --all --minor       # bump all skills
    python prepare_release.py --dry-run --minor    # preview without writing

No external dependencies required (stdlib only).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILLS_DIR = Path(".agents/skills")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
VERSION_LINE_RE = re.compile(r"^(version:\s*)[\"']?(\d+(?:\.\d+)*)(?:\.\d+)?[\"']?\s*$", re.MULTILINE)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
TWO_PART_RE = re.compile(r"^(\d+)\.(\d+)$")

# Validation constants (mirrors validate_all_skills.py)
ALLOWED_FM_KEYS = {"name", "description", "license", "allowed-tools", "metadata",
                   "version", "priority", "category", "color", "displayName"}
LINE_WARN = 500
LINE_ERROR = 800


# ---------------------------------------------------------------------------
# Terminal colors
# ---------------------------------------------------------------------------
def _has_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _has_color()

def _c(code: str, t: str) -> str:
    return f"\033[{code}m{t}\033[0m" if _COLOR else t

def red(t: str) -> str:    return _c("31", t)
def green(t: str) -> str:  return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def cyan(t: str) -> str:   return _c("36", t)
def bold(t: str) -> str:   return _c("1", t)
def dim(t: str) -> str:    return _c("2", t)


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------
@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, raw: str) -> Optional["Version"]:
        raw = raw.strip().strip("\"'")
        m = SEMVER_RE.match(raw)
        if m:
            return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m2 = TWO_PART_RE.match(raw)
        if m2:
            return cls(int(m2.group(1)), int(m2.group(2)), 0)
        return None

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------
def git_root() -> Path:
    """Find the repository root."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def last_version_tag(skill_name: str) -> Optional[str]:
    """Find the most recent tag matching the skill name pattern."""
    patterns = [f"{skill_name}/v*", f"{skill_name}-v*", "v*"]
    for pattern in patterns:
        try:
            out = subprocess.check_output(
                ["git", "tag", "-l", pattern, "--sort=-v:refname"],
                stderr=subprocess.DEVNULL, text=True
            ).strip()
            if out:
                return out.splitlines()[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def git_log_since(ref: Optional[str], skill_path: str) -> list[str]:
    """Get commit messages since a ref, scoped to the skill path."""
    cmd = ["git", "log", "--oneline", "--no-merges"]
    if ref:
        cmd.append(f"{ref}..HEAD")
    cmd.extend(["--", skill_path])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
        return [line for line in out.splitlines() if line.strip()] if out else []
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


# ---------------------------------------------------------------------------
# Skill discovery and frontmatter parsing
# ---------------------------------------------------------------------------
def discover_skills(root: Path, skill_arg: Optional[str] = None) -> list[Path]:
    """Find skill directories. If skill_arg is given, resolve that one skill."""
    if skill_arg:
        # Accept both relative path and bare name
        candidate = root / skill_arg
        if not candidate.is_dir():
            candidate = root / SKILLS_DIR / skill_arg
        if not candidate.is_dir() or not (candidate / "SKILL.md").exists():
            print(red(f"Skill not found: {skill_arg}"), file=sys.stderr)
            sys.exit(1)
        return [candidate]

    base = root / SKILLS_DIR
    if not base.is_dir():
        print(red(f"Skills directory not found: {base}"), file=sys.stderr)
        sys.exit(1)
    return sorted(p for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def read_frontmatter_version(skill_path: Path) -> tuple[str, Optional[Version]]:
    """Read SKILL.md and extract the version from frontmatter. Returns (content, version)."""
    content = (skill_path / "SKILL.md").read_text()
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return content, None
    fm_block = fm_match.group(1)
    ver_match = re.search(r"^version:\s*[\"']?(\d+(?:\.\d+)*)[\"']?\s*$", fm_block, re.MULTILINE)
    if not ver_match:
        return content, None
    return content, Version.parse(ver_match.group(1))


def write_bumped_version(skill_path: Path, content: str, new_version: Version) -> str:
    """Replace the version in frontmatter and write the file. Returns updated content."""
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return content
    fm_block = fm_match.group(1)
    new_fm = re.sub(
        r"^(version:\s*)[\"']?\d+(?:\.\d+)*[\"']?\s*$",
        f"\\g<1>{new_version}",
        fm_block,
        flags=re.MULTILINE,
    )
    updated = content[:fm_match.start(1)] + new_fm + content[fm_match.end(1):]
    (skill_path / "SKILL.md").write_text(updated)
    return updated


# ---------------------------------------------------------------------------
# Validation (lightweight, inline — mirrors key checks from validate_all_skills.py)
# ---------------------------------------------------------------------------
@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_skill(skill_path: Path) -> ValidationResult:
    """Run core quality checks on a skill. Returns a ValidationResult."""
    result = ValidationResult(passed=True)
    md = skill_path / "SKILL.md"
    if not md.exists():
        result.passed = False
        result.errors.append("SKILL.md not found")
        return result

    content = md.read_text()

    # Frontmatter exists
    if not content.startswith("---"):
        result.passed = False
        result.errors.append("No YAML frontmatter (must start with '---')")
        return result

    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        result.passed = False
        result.errors.append("Invalid frontmatter (missing closing '---')")
        return result

    # Parse frontmatter fields manually (no yaml dependency)
    fm_text = fm_match.group(1)
    has_name = bool(re.search(r"^name:", fm_text, re.MULTILINE))
    has_desc = bool(re.search(r"^description:", fm_text, re.MULTILINE))
    if not has_name:
        result.passed = False
        result.errors.append("Missing required 'name' field in frontmatter")
    if not has_desc:
        result.passed = False
        result.errors.append("Missing required 'description' field in frontmatter")

    # Name matches directory
    name_match = re.search(r"^name:\s*(.+)$", fm_text, re.MULTILINE)
    if name_match:
        name_val = name_match.group(1).strip().strip("\"'")
        if name_val != skill_path.name:
            result.passed = False
            result.errors.append(f"Name '{name_val}' does not match directory '{skill_path.name}'")

    # Line count
    line_count = content.count("\n") + 1
    if line_count > LINE_ERROR:
        result.passed = False
        result.errors.append(f"{line_count} lines exceeds maximum of {LINE_ERROR}")
    elif line_count > LINE_WARN:
        result.warnings.append(f"{line_count} lines exceeds recommended {LINE_WARN}")

    # Broken internal links
    broken_links: list[str] = []
    for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", content):
        target = m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = target.split("#")[0]
        if path_part and not (skill_path / path_part).exists():
            broken_links.append(f"[{m.group(1)}]({target})")
    if broken_links:
        result.passed = False
        result.errors.append(f"Broken links: {'; '.join(broken_links)}")

    # Headings exist
    body_match = re.match(r"^---\n.*?\n---\n?(.*)", content, re.DOTALL)
    body = body_match.group(1) if body_match else content
    headings = re.findall(r"^##\s+(.+)$", body, re.MULTILINE)
    if not headings:
        result.warnings.append("No ## headings found in body")

    return result


# ---------------------------------------------------------------------------
# Changelog generation
# ---------------------------------------------------------------------------
def generate_changelog(skill_name: str, old_ver: Optional[Version],
                       new_ver: Version, commits: list[str]) -> str:
    """Generate a markdown changelog entry from commit messages."""
    today = date.today().isoformat()
    lines = [f"## {new_ver} - {today}", ""]

    if not commits:
        lines.append("- Version bump (no new commits)")
        lines.append("")
        return "\n".join(lines)

    # Categorize by conventional commit prefix
    categories: dict[str, list[str]] = {
        "Features": [], "Fixes": [], "Documentation": [],
        "Refactor": [], "Performance": [], "Other": [],
    }
    prefix_map = {
        "feat": "Features", "fix": "Fixes", "docs": "Documentation",
        "refactor": "Refactor", "perf": "Performance",
    }

    for commit in commits:
        # Strip leading hash
        msg = re.sub(r"^[a-f0-9]+\s+", "", commit)
        matched = False
        for prefix, category in prefix_map.items():
            pattern = re.compile(rf"^{prefix}(?:\(.*?\))?:\s*(.+)", re.IGNORECASE)
            m = pattern.match(msg)
            if m:
                categories[category].append(m.group(1).strip())
                matched = True
                break
        if not matched:
            # Skip chore/style/test from changelog
            if re.match(r"^(chore|style|test|ci|build)(\(.*?\))?:", msg, re.IGNORECASE):
                continue
            categories["Other"].append(msg)

    for section, items in categories.items():
        if items:
            lines.append(f"### {section}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Release summary
# ---------------------------------------------------------------------------
def print_release_summary(results: list[dict[str, object]]) -> None:
    """Print a formatted release summary for all processed skills."""
    print(f"\n{bold('=' * 70)}")
    print(f"{bold('  Release Summary')}")
    print(f"{bold('=' * 70)}\n")

    for r in results:
        status = green("READY") if r["valid"] else red("BLOCKED")
        print(f"  [{status}] {bold(str(r['name']))}")
        print(f"           Version: {r['old_version']} -> {r['new_version']}")
        if r["commits_count"]:
            print(f"           Commits: {r['commits_count']}")
        if r["validation_warnings"]:
            for w in r["validation_warnings"]:  # type: ignore[union-attr]
                print(f"           {yellow('WARN')}: {w}")
        if r["validation_errors"]:
            for e in r["validation_errors"]:  # type: ignore[union-attr]
                print(f"           {red('ERROR')}: {e}")
        print()

    ready = sum(1 for r in results if r["valid"])
    blocked = sum(1 for r in results if not r["valid"])
    print(f"{bold('-' * 70)}")
    print(f"  {green('Ready')}: {ready}   {red('Blocked')}: {blocked}   Total: {len(results)}")
    print(f"{bold('-' * 70)}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Prepare a skill release: bump version, generate changelog, validate quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python prepare_release.py .agents/skills/clean-code --minor\n"
            "  python prepare_release.py .agents/skills/clean-code --major\n"
            "  python prepare_release.py --all --minor\n"
            "  python prepare_release.py --dry-run --minor\n"
        ),
    )
    p.add_argument("skill", nargs="?", default=None,
                   help="Path to skill directory (e.g. .agents/skills/clean-code)")
    p.add_argument("--all", action="store_true",
                   help="Process all skills in .agents/skills/")

    bump = p.add_mutually_exclusive_group(required=True)
    bump.add_argument("--major", action="store_true", help="Major version bump (X.0.0)")
    bump.add_argument("--minor", action="store_true", help="Minor version bump (x.Y.0)")

    p.add_argument("--dry-run", action="store_true",
                   help="Preview changes without writing files")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.skill and not args.all:
        parser.error("Provide a skill path or use --all")

    root = git_root()
    os.chdir(root)

    if args.all:
        skill_paths = discover_skills(root)
    else:
        skill_paths = discover_skills(root, args.skill)

    if not skill_paths:
        print(red("No skills found."), file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"\n{cyan('=== DRY RUN MODE ===')}\n")

    results: list[dict[str, object]] = []

    for skill_path in skill_paths:
        name = skill_path.name
        content, current_ver = read_frontmatter_version(skill_path)

        if current_ver is None:
            # No version in frontmatter — default to 0.0.0
            current_ver = Version(0, 0, 0)

        new_ver = current_ver.bump_major() if args.major else current_ver.bump_minor()

        # Git log
        tag = last_version_tag(name)
        rel_path = str(skill_path.relative_to(root))
        commits = git_log_since(tag, rel_path)

        # Validation
        vr = validate_skill(skill_path)

        # Changelog
        changelog = generate_changelog(name, current_ver, new_ver, commits)

        result: dict[str, object] = {
            "name": name,
            "old_version": str(current_ver),
            "new_version": str(new_ver),
            "commits_count": len(commits),
            "valid": vr.passed,
            "validation_errors": vr.errors,
            "validation_warnings": vr.warnings,
            "changelog": changelog,
        }
        results.append(result)

        if args.dry_run:
            print(f"  {bold(name)}: {current_ver} -> {new_ver}")
            if commits:
                print(f"    {len(commits)} commit(s) since {tag or 'beginning'}")
            print(f"    Validation: {'PASS' if vr.passed else 'FAIL'}")
            if vr.errors:
                for e in vr.errors:
                    print(f"      {red('ERROR')}: {e}")
            if vr.warnings:
                for w in vr.warnings:
                    print(f"      {yellow('WARN')}: {w}")
            print(f"\n    Changelog preview:\n")
            for line in changelog.splitlines():
                print(f"      {line}")
            print()
            continue

        # Write version bump
        write_bumped_version(skill_path, content, new_ver)

        # Write changelog
        changelog_path = skill_path / "CHANGELOG.md"
        if changelog_path.exists():
            existing = changelog_path.read_text()
            changelog_path.write_text(changelog + "\n" + existing)
        else:
            changelog_path.write_text(changelog)

        print(f"  {green('✓')} {bold(name)}: {current_ver} -> {new_ver}")

    # Summary
    if args.dry_run:
        print(f"{cyan('No changes made. Run without --dry-run to execute.')}\n")
    else:
        print_release_summary(results)

    # Return non-zero if any skill failed validation
    if any(not r["valid"] for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
