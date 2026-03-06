#!/usr/bin/env python3
"""
audit-code: Project code security reviewer.

Scans source code for hardcoded secrets, dangerous function calls,
SQL injection patterns, dependency risks, sensitive files, and
overly permissive file permissions.
"""

import sys
import os
import stat
from pathlib import Path

# Add local scripts dir to path for patterns.py
Script_Dir = Path(__file__).parent
sys.path.insert(0, str(Script_Dir))

from patterns import (
	Audit_Code_Patterns,
	Secrets_Patterns,
	Dangerous_Call_Patterns,
	Exfiltration_Patterns,
	Supply_Chain_Patterns,
	File_Permission_Patterns,
	Finding,
	Severity,
	Category,
	Scan_Content,
	Format_Report,
)


# File extensions to scan
Scannable_Extensions: set[str] = {
	".py", ".js", ".ts", ".jsx", ".tsx",
	".cs", ".java", ".go", ".rs", ".rb",
	".c", ".cpp", ".h", ".hpp",
	".sh", ".bash", ".zsh", ".ps1",
	".php", ".pl", ".lua",
	".yaml", ".yml", ".json", ".toml", ".xml",
	".env", ".cfg", ".conf", ".ini",
	".sql",
	".tf", ".hcl",
	".dockerfile",
}

# Directories to skip
Skip_Dirs: set[str] = {
	".git", "node_modules", "__pycache__", ".venv", "venv",
	"env", ".env", ".tox", ".mypy_cache", ".pytest_cache",
	"dist", "build", "target", "bin", "obj",
	".next", ".nuxt", ".svelte-kit",
	"vendor", "packages",
}

# Maximum file size to scan (1 MB)
Max_File_Size: int = 1_048_576


def Should_Scan(file_path: Path) -> bool:
	"""Determine if a file should be scanned based on extension and size."""
	# Always scan .env files regardless of extension matching
	if file_path.name.startswith(".env"):
		return True

	# Check Dockerfile (no extension)
	if file_path.name.lower() in ("dockerfile", "makefile", "rakefile", "gemfile"):
		return True

	if file_path.suffix.lower() not in Scannable_Extensions:
		return False

	try:
		if file_path.stat().st_size > Max_File_Size:
			return False
	except OSError:
		return False

	return True


def Is_Skipped_Dir(dir_path: Path) -> bool:
	"""Check if directory should be skipped."""
	return dir_path.name in Skip_Dirs


def Find_Env_Files(target_path: Path) -> list[Finding]:
	"""Find .env files that might be committed to git."""
	findings: list[Finding] = []

	for env_file in target_path.rglob(".env*"):
		if not env_file.is_file():
			continue

		# Skip dirs in skip list
		if any(Is_Skipped_Dir(parent) for parent in env_file.parents):
			continue

		# Skip .env.example and .env.template (these are safe)
		if env_file.name in (".env.example", ".env.template", ".env.sample"):
			continue

		findings.append(Finding(
			pattern_name="env_file_in_repo",
			severity=Severity.HIGH,
			category=Category.SECRETS,
			description=f"Environment file found in repository: {env_file.name} -- may contain secrets",
			file_path=str(env_file),
			line_number=0,
			matched_text=env_file.name,
		))

		# Also scan its contents for actual secrets
		try:
			content = env_file.read_text(encoding="utf-8", errors="replace")
			findings.extend(Scan_Content(content, Secrets_Patterns, str(env_file)))
		except (PermissionError, OSError):
			pass

	return findings


def Check_File_Permissions(target_path: Path) -> list[Finding]:
	"""Check for overly permissive file permissions on sensitive files."""
	findings: list[Finding] = []

	Sensitive_Patterns = [
		"*.pem", "*.key", "*.p12", "*.pfx",
		"*.env", "*.secret", "*.credentials",
		"id_rsa", "id_ed25519", "id_ecdsa",
	]

	for file_path in target_path.rglob("*"):
		if not file_path.is_file():
			continue

		if any(Is_Skipped_Dir(parent) for parent in file_path.parents):
			continue

		# Check if this is a sensitive file type
		is_sensitive = False
		for pat in Sensitive_Patterns:
			if pat.startswith("*"):
				if file_path.suffix == pat[1:]:
					is_sensitive = True
					break
			else:
				if file_path.name == pat:
					is_sensitive = True
					break

		if not is_sensitive:
			continue

		try:
			file_stat = os.stat(file_path)
			mode = file_stat.st_mode

			# Check world-readable
			if mode & stat.S_IROTH:
				findings.append(Finding(
					pattern_name="sensitive_file_world_readable",
					severity=Severity.HIGH,
					category=Category.FILE_PERMISSIONS,
					description=f"Sensitive file is world-readable: {file_path.name}",
					file_path=str(file_path),
					line_number=0,
					matched_text=f"mode: {oct(mode)}",
				))

			# Check world-writable
			if mode & stat.S_IWOTH:
				findings.append(Finding(
					pattern_name="sensitive_file_world_writable",
					severity=Severity.CRITICAL,
					category=Category.FILE_PERMISSIONS,
					description=f"Sensitive file is world-writable: {file_path.name}",
					file_path=str(file_path),
					line_number=0,
					matched_text=f"mode: {oct(mode)}",
				))

		except OSError:
			pass

	return findings


def Scan_Source_Files(target_path: Path) -> list[Finding]:
	"""Scan all source files for security patterns."""
	findings: list[Finding] = []
	files_scanned = 0

	for file_path in target_path.rglob("*"):
		if not file_path.is_file():
			continue

		# Skip excluded directories
		if any(Is_Skipped_Dir(parent) for parent in file_path.parents):
			continue

		if not Should_Scan(file_path):
			continue

		try:
			content = file_path.read_text(encoding="utf-8", errors="replace")
		except (PermissionError, OSError):
			continue

		file_findings = Scan_Content(content, Audit_Code_Patterns, str(file_path))
		findings.extend(file_findings)
		files_scanned += 1

		if file_findings:
			print(f"  [{len(file_findings)} finding(s)] {file_path}")

	print(f"\n  Total files scanned: {files_scanned}")
	return findings


def Check_Gitignore_Coverage(target_path: Path) -> list[Finding]:
	"""Check if .gitignore covers common sensitive patterns."""
	findings: list[Finding] = []
	gitignore = target_path / ".gitignore"

	if not gitignore.exists():
		# Only flag if this looks like a git repo
		if (target_path / ".git").exists():
			findings.append(Finding(
				pattern_name="missing_gitignore",
				severity=Severity.MEDIUM,
				category=Category.SECRETS,
				description="Git repository has no .gitignore -- sensitive files may be committed",
				file_path=str(gitignore),
				line_number=0,
				matched_text="(file missing)",
			))
		return findings

	try:
		content = gitignore.read_text(encoding="utf-8", errors="replace")
	except (PermissionError, OSError):
		return findings

	Essential_Patterns = [
		(".env", "Environment files with secrets"),
		("*.pem", "PEM certificate/key files"),
		("*.key", "Private key files"),
	]

	for pattern, description in Essential_Patterns:
		if pattern not in content:
			findings.append(Finding(
				pattern_name="gitignore_missing_pattern",
				severity=Severity.LOW,
				category=Category.SECRETS,
				description=f".gitignore does not exclude '{pattern}' -- {description}",
				file_path=str(gitignore),
				line_number=0,
				matched_text=f"missing: {pattern}",
			))

	return findings


def Main() -> None:
	if len(sys.argv) < 2:
		print("Usage: audit_code.py <path>", file=sys.stderr)
		print("\nDefaults to project root if called without arguments.", file=sys.stderr)
		sys.exit(1)

	target_path = Path(sys.argv[1]).resolve()
	if not target_path.exists():
		print(f"Error: {target_path} does not exist", file=sys.stderr)
		sys.exit(1)

	print(f"Auditing code: {target_path}\n")

	all_findings: list[Finding] = []

	# Run all audit checks
	print("[*] Scanning source files for vulnerabilities...")
	all_findings.extend(Scan_Source_Files(target_path))

	print("\n[*] Checking for .env files...")
	env_findings = Find_Env_Files(target_path)
	all_findings.extend(env_findings)
	print(f"    {len(env_findings)} issue(s)")

	print("[*] Checking file permissions on sensitive files...")
	perm_findings = Check_File_Permissions(target_path)
	all_findings.extend(perm_findings)
	print(f"    {len(perm_findings)} issue(s)")

	print("[*] Checking .gitignore coverage...")
	gitignore_findings = Check_Gitignore_Coverage(target_path)
	all_findings.extend(gitignore_findings)
	print(f"    {len(gitignore_findings)} issue(s)")

	print()

	# Generate report
	report = Format_Report(
		title="audit-code",
		scanned_target=str(target_path),
		findings=all_findings,
	)
	print(report)


if __name__ == "__main__":
	Main()
