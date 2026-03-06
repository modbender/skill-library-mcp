#!/usr/bin/env python3
"""
scan-skill: Deep security analyzer for individual Claude Code skills.

Performs comprehensive analysis of a skill directory, checking SKILL.md
frontmatter, hidden comments, shell patterns, persistence triggers,
supporting scripts, and encoding/obfuscation techniques.
"""

import sys
import os
import re
import stat
from pathlib import Path

# Add local scripts dir to path for patterns.py
Script_Dir = Path(__file__).parent
sys.path.insert(0, str(Script_Dir))

from patterns import (
	Scan_Skill_Patterns,
	Skill_Injection_Patterns,
	Encoding_Obfuscation_Patterns,
	Instruction_Override_Patterns,
	Dangerous_Call_Patterns,
	Exfiltration_Patterns,
	Supply_Chain_Patterns,
	Pattern,
	Finding,
	Severity,
	Category,
	Scan_Content,
	Format_Report,
)


def Parse_Frontmatter(content: str) -> dict[str, str]:
	"""Extract YAML frontmatter from SKILL.md content."""
	frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
	if not frontmatter_match:
		return {}

	frontmatter: dict[str, str] = {}
	for line in frontmatter_match.group(1).split("\n"):
		line = line.strip()
		if ":" in line:
			key, _, value = line.partition(":")
			frontmatter[key.strip()] = value.strip()

	return frontmatter


def Analyze_Frontmatter(
	frontmatter: dict[str, str],
	file_path: str,
) -> list[Finding]:
	"""Analyze SKILL.md frontmatter for dangerous configurations."""
	findings: list[Finding] = []

	# Check model invocation
	if frontmatter.get("disable-model-invocation", "").lower() == "false":
		findings.append(Finding(
			pattern_name="frontmatter_model_invocation_enabled",
			severity=Severity.MEDIUM,
			category=Category.SKILL_INJECTION,
			description="disable-model-invocation is false -- skill can auto-invoke without user action",
			file_path=file_path,
			line_number=1,
			matched_text="disable-model-invocation: false",
		))

	# Check if model invocation is not set (defaults to false=auto-invocable)
	if "disable-model-invocation" not in frontmatter:
		findings.append(Finding(
			pattern_name="frontmatter_model_invocation_missing",
			severity=Severity.LOW,
			category=Category.SKILL_INJECTION,
			description="disable-model-invocation not set -- defaults to allowing model auto-invocation",
			file_path=file_path,
			line_number=1,
			matched_text="(field missing)",
		))

	# Check user-invocable: false
	if frontmatter.get("user-invocable", "").lower() == "false":
		findings.append(Finding(
			pattern_name="frontmatter_hidden_from_user",
			severity=Severity.MEDIUM,
			category=Category.SKILL_INJECTION,
			description="user-invocable is false -- skill hidden from user menu but may be auto-invoked",
			file_path=file_path,
			line_number=1,
			matched_text="user-invocable: false",
		))

	# Check allowed-tools for Bash
	allowed_tools = frontmatter.get("allowed-tools", "")
	if "Bash" in allowed_tools:
		findings.append(Finding(
			pattern_name="frontmatter_bash_pre_approved",
			severity=Severity.MEDIUM,
			category=Category.SKILL_INJECTION,
			description="Skill pre-approves Bash tool -- shell execution without per-command consent",
			file_path=file_path,
			line_number=1,
			matched_text=f"allowed-tools: {allowed_tools}",
		))

	# Dangerous combination: auto-invocable + Bash + hidden
	is_auto_invocable = frontmatter.get("disable-model-invocation", "").lower() != "true"
	has_bash = "Bash" in allowed_tools
	is_hidden = frontmatter.get("user-invocable", "").lower() == "false"

	if is_auto_invocable and has_bash and is_hidden:
		findings.append(Finding(
			pattern_name="frontmatter_dangerous_combination",
			severity=Severity.CRITICAL,
			category=Category.SKILL_INJECTION,
			description="Dangerous combination: auto-invocable + Bash pre-approved + hidden from user -- stealth shell execution",
			file_path=file_path,
			line_number=1,
			matched_text="(combined frontmatter analysis)",
		))
	elif is_auto_invocable and has_bash:
		findings.append(Finding(
			pattern_name="frontmatter_risky_combination",
			severity=Severity.HIGH,
			category=Category.SKILL_INJECTION,
			description="Risky combination: auto-invocable + Bash pre-approved -- model can execute shell commands without user triggering the skill",
			file_path=file_path,
			line_number=1,
			matched_text="(combined frontmatter analysis)",
		))

	return findings


def Check_Html_Comments(content: str, file_path: str) -> list[Finding]:
	"""Extract and analyze HTML comments for hidden instructions."""
	findings: list[Finding] = []
	comment_pattern = re.compile(r"<!--([\s\S]*?)-->")

	for match in comment_pattern.finditer(content):
		comment_body = match.group(1)
		line_number = content[:match.start()].count("\n") + 1

		# Check if comment contains imperative instructions
		imperative_patterns = [
			(r"(run|execute|call|invoke|perform)\s+(the\s+)?(following|this|these)", "imperative execution instruction"),
			(r"(curl|wget|bash|sh|python|node)\s+", "command execution reference"),
			(r"(read|access|get|fetch|send|post)\s+[^\n]*(key|token|secret|credential|password|ssh|aws)", "credential access instruction"),
			(r"(ignore|override|forget|disregard)\s+", "instruction override"),
		]

		for imp_pattern, desc in imperative_patterns:
			if re.search(imp_pattern, comment_body, re.IGNORECASE):
				findings.append(Finding(
					pattern_name=f"html_comment_{desc.replace(' ', '_')}",
					severity=Severity.CRITICAL,
					category=Category.SKILL_INJECTION,
					description=f"Hidden HTML comment contains {desc}",
					file_path=file_path,
					line_number=line_number,
					matched_text=match.group(0)[:200] + ("..." if len(match.group(0)) > 200 else ""),
				))

	return findings


def Scan_Supporting_Files(skill_dir: Path) -> list[Finding]:
	"""Scan all supporting files in the skill directory."""
	findings: list[Finding] = []

	# Scan all files in scripts/ and other subdirectories
	Scannable_Extensions = {".py", ".sh", ".bash", ".js", ".ts", ".rb", ".pl"}

	for file_path in skill_dir.rglob("*"):
		if not file_path.is_file():
			continue
		if file_path.name == "SKILL.md":
			continue

		str_path = str(file_path)

		# Check for executable permissions on non-standard files
		if file_path.suffix not in Scannable_Extensions:
			try:
				file_stat = os.stat(file_path)
				if file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
					findings.append(Finding(
						pattern_name="executable_non_script",
						severity=Severity.MEDIUM,
						category=Category.SKILL_INJECTION,
						description=f"Non-standard file has executable permission: {file_path.name}",
						file_path=str_path,
						line_number=0,
						matched_text=f"mode: {oct(file_stat.st_mode)}",
					))
			except OSError:
				pass

		# Scan content of script files
		if file_path.suffix in Scannable_Extensions:
			try:
				content = file_path.read_text(encoding="utf-8", errors="replace")
			except (PermissionError, OSError):
				continue

			print(f"  Scanning supporting file: {file_path}")
			patterns = (
				Dangerous_Call_Patterns
				+ Exfiltration_Patterns
				+ Encoding_Obfuscation_Patterns
				+ Supply_Chain_Patterns
			)
			findings.extend(Scan_Content(content, patterns, str_path))

	return findings


def Inventory_Supporting_Files(skill_dir: Path) -> str:
	"""Generate an inventory of supporting files in the skill."""
	lines: list[str] = ["### Supporting File Inventory\n"]
	file_count = 0

	for file_path in sorted(skill_dir.rglob("*")):
		if not file_path.is_file():
			continue
		if file_path.name == "SKILL.md":
			continue

		file_count += 1
		relative = file_path.relative_to(skill_dir)
		size = file_path.stat().st_size

		# Check executable
		is_exec = os.access(file_path, os.X_OK)
		exec_marker = " [EXECUTABLE]" if is_exec else ""

		lines.append(f"- `{relative}` ({size} bytes){exec_marker}")

	if file_count == 0:
		lines.append("- (no supporting files)")

	lines.append("")
	return "\n".join(lines)


def Main() -> None:
	if len(sys.argv) < 2:
		print("Usage: scan_skill.py <path-to-skill-directory>", file=sys.stderr)
		print("\nProvide the path to a skill directory containing SKILL.md", file=sys.stderr)
		sys.exit(1)

	skill_dir = Path(sys.argv[1]).resolve()

	if not skill_dir.is_dir():
		print(f"Error: {skill_dir} is not a directory", file=sys.stderr)
		sys.exit(1)

	skill_md = skill_dir / "SKILL.md"
	if not skill_md.exists():
		print(f"Error: No SKILL.md found in {skill_dir}", file=sys.stderr)
		sys.exit(1)

	print(f"Analyzing skill: {skill_dir}\n")

	all_findings: list[Finding] = []
	str_skill_md = str(skill_md)

	# Read SKILL.md
	content = skill_md.read_text(encoding="utf-8", errors="replace")

	# 1. Frontmatter analysis
	print("[*] Frontmatter analysis...")
	frontmatter = Parse_Frontmatter(content)
	if frontmatter:
		print(f"    Fields: {', '.join(frontmatter.keys())}")
	else:
		print("    No frontmatter found")
	fm_findings = Analyze_Frontmatter(frontmatter, str_skill_md)
	all_findings.extend(fm_findings)
	print(f"    {len(fm_findings)} issue(s)")

	# 2. HTML comment analysis
	print("[*] HTML comment analysis...")
	comment_findings = Check_Html_Comments(content, str_skill_md)
	all_findings.extend(comment_findings)
	print(f"    {len(comment_findings)} issue(s)")

	# 3. Pattern-based content scan
	print("[*] Pattern-based content scan...")
	content_findings = Scan_Content(content, Scan_Skill_Patterns, str_skill_md)
	all_findings.extend(content_findings)
	print(f"    {len(content_findings)} issue(s)")

	# 4. Supporting files
	print("[*] Supporting files scan...")
	support_findings = Scan_Supporting_Files(skill_dir)
	all_findings.extend(support_findings)
	print(f"    {len(support_findings)} issue(s)")

	# Deduplicate findings (same pattern + same line)
	seen: set[tuple[str, str, int]] = set()
	unique_findings: list[Finding] = []
	for f in all_findings:
		key = (f.pattern_name, f.file_path, f.line_number)
		if key not in seen:
			seen.add(key)
			unique_findings.append(f)

	print()

	# Generate report
	report = Format_Report(
		title="scan-skill",
		scanned_target=str(skill_dir),
		findings=unique_findings,
	)
	print(report)

	# Add supporting file inventory
	inventory = Inventory_Supporting_Files(skill_dir)
	print(inventory)


if __name__ == "__main__":
	Main()
