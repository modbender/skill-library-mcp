#!/usr/bin/env python3
"""
vet-repo: Repository agent configuration scanner.

Scans .claude/, .mcp.json, CLAUDE.md, and related agent config files
for known malicious patterns (injection, hook abuse, MCP poisoning, etc.)
"""

import sys
import os
from pathlib import Path

# Add the script directory to path so patterns.py can be imported
Script_Dir = Path(__file__).parent
sys.path.insert(0, str(Script_Dir))

from patterns import (
	Vet_Repo_Patterns,
	Skill_Injection_Patterns,
	Hook_Abuse_Patterns,
	Mcp_Config_Patterns,
	Instruction_Override_Patterns,
	Encoding_Obfuscation_Patterns,
	Finding,
	Scan_Content,
	Format_Report,
)


def Scan_File(file_path: Path, patterns: list) -> list[Finding]:
	"""Scan a single file against patterns, handling read errors gracefully."""
	if not file_path.exists() or not file_path.is_file():
		return []

	try:
		content = file_path.read_text(encoding="utf-8", errors="replace")
	except (PermissionError, OSError) as e:
		print(f"  [WARN] Cannot read {file_path}: {e}", file=sys.stderr)
		return []

	return Scan_Content(content, patterns, str(file_path))


def Scan_Settings_Json(repo_root: Path) -> list[Finding]:
	"""Scan .claude/settings.json for hook abuse patterns."""
	settings_path = repo_root / ".claude" / "settings.json"
	if not settings_path.exists():
		return []

	print(f"  Scanning {settings_path}")
	patterns = Hook_Abuse_Patterns + Encoding_Obfuscation_Patterns
	return Scan_File(settings_path, patterns)


def Scan_Skill_Files(repo_root: Path) -> list[Finding]:
	"""Scan all SKILL.md files in .claude/skills/ for injection patterns."""
	skills_dir = repo_root / ".claude" / "skills"
	if not skills_dir.exists():
		return []

	findings: list[Finding] = []
	patterns = (
		Skill_Injection_Patterns
		+ Instruction_Override_Patterns
		+ Encoding_Obfuscation_Patterns
	)

	for skill_md in skills_dir.rglob("SKILL.md"):
		print(f"  Scanning {skill_md}")
		findings.extend(Scan_File(skill_md, patterns))

	# Also scan supporting scripts in skills
	for script in skills_dir.rglob("*.py"):
		# Skip our own scanner scripts
		if "vet-repo" in str(script) or "scan-skill" in str(script) or "audit-code" in str(script):
			continue
		print(f"  Scanning {script}")
		findings.extend(Scan_File(script, Vet_Repo_Patterns))

	for script in skills_dir.rglob("*.sh"):
		print(f"  Scanning {script}")
		findings.extend(Scan_File(script, Vet_Repo_Patterns))

	return findings


def Scan_Mcp_Config(repo_root: Path) -> list[Finding]:
	"""Scan .mcp.json for MCP server configuration issues."""
	findings: list[Finding] = []
	patterns = Mcp_Config_Patterns + Instruction_Override_Patterns

	# Check both common locations
	mcp_paths = [
		repo_root / ".mcp.json",
		repo_root / ".claude" / "mcp.json",
	]

	for mcp_path in mcp_paths:
		if mcp_path.exists():
			print(f"  Scanning {mcp_path}")
			findings.extend(Scan_File(mcp_path, patterns))

	return findings


def Scan_Claude_Md(repo_root: Path) -> list[Finding]:
	"""Scan CLAUDE.md files for instruction injection."""
	findings: list[Finding] = []
	patterns = (
		Instruction_Override_Patterns
		+ Skill_Injection_Patterns
		+ Encoding_Obfuscation_Patterns
	)

	claude_md_paths = [
		repo_root / "CLAUDE.md",
		repo_root / ".claude" / "CLAUDE.md",
	]

	for md_path in claude_md_paths:
		if md_path.exists():
			print(f"  Scanning {md_path}")
			findings.extend(Scan_File(md_path, patterns))

	return findings


def Scan_Vscode_Settings(repo_root: Path) -> list[Finding]:
	"""Scan .vscode/settings.json for IDE config injection (CVE-2025-53773)."""
	vscode_settings = repo_root / ".vscode" / "settings.json"
	if not vscode_settings.exists():
		return []

	print(f"  Scanning {vscode_settings}")
	return Scan_File(vscode_settings, Hook_Abuse_Patterns)


def Scan_Cursor_Config(repo_root: Path) -> list[Finding]:
	"""Scan .cursor/ for Cursor IDE config injection (CVE-2025-54135)."""
	findings: list[Finding] = []
	cursor_mcp = repo_root / ".cursor" / "mcp.json"

	if cursor_mcp.exists():
		print(f"  Scanning {cursor_mcp}")
		findings.extend(Scan_File(
			cursor_mcp,
			Mcp_Config_Patterns + Instruction_Override_Patterns,
		))

	return findings


def Main() -> None:
	if len(sys.argv) < 2:
		print("Usage: vet_repo.py <repo_root>", file=sys.stderr)
		sys.exit(1)

	repo_root = Path(sys.argv[1]).resolve()
	if not repo_root.is_dir():
		print(f"Error: {repo_root} is not a directory", file=sys.stderr)
		sys.exit(1)

	print(f"Scanning repository: {repo_root}\n")

	all_findings: list[Finding] = []

	# Run all scanners
	scanners = [
		("Hook Configuration", Scan_Settings_Json),
		("Skill Files", Scan_Skill_Files),
		("MCP Configuration", Scan_Mcp_Config),
		("CLAUDE.md Instructions", Scan_Claude_Md),
		("VSCode Settings", Scan_Vscode_Settings),
		("Cursor Configuration", Scan_Cursor_Config),
	]

	for name, scanner_fn in scanners:
		print(f"[*] {name}...")
		findings = scanner_fn(repo_root)
		if findings:
			print(f"    Found {len(findings)} issue(s)")
		else:
			print(f"    Clean")
		all_findings.extend(findings)

	print()

	# Generate report
	report = Format_Report(
		title="vet-repo",
		scanned_target=str(repo_root),
		findings=all_findings,
	)
	print(report)


if __name__ == "__main__":
	Main()
