#!/usr/bin/env python3
"""
Security review checker for OpenClaw skills.
Scans skills for common security issues that affect ClawHub security reviews.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityReviewer:
    def __init__(self, skill_dir: Path):
        self.skill_dir = Path(skill_dir)
        self.issues = []
        self.warnings = []
        self.suggestions = []

    def check_requirements_declaration(self):
        """Check if runtime dependencies are declared in SKILL.md or _meta.json."""
        skill_md = self.skill_dir / "SKILL.md"
        meta_json = self.skill_dir / "_meta.json"
        
        # Read SKILL.md
        skill_content = ""
        if skill_md.exists():
            skill_content = skill_md.read_text(encoding="utf-8")
        
        # Read _meta.json
        meta = {}
        if meta_json.exists():
            try:
                meta = json.loads(meta_json.read_text(encoding="utf-8"))
            except:
                pass
        
        # Check for common CLI/system dependencies in scripts
        scripts_dir = self.skill_dir / "scripts"
        found_deps = set()
        
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                content = script_file.read_text(encoding="utf-8")
                # Check for subprocess calls to system tools
                if re.search(r"subprocess\.(run|call|Popen|check_output)", content):
                    # Look for common system tools in command arrays or strings
                    for tool in ["openclaw", "lsof", "ps", "launchctl", "curl", "wget", "git", "which", "kill", "killall"]:
                        # Check for tool in command arrays or subprocess calls
                        if re.search(rf"['\"]({tool})['\"]|\[.*['\"]({tool})['\"]", content, re.IGNORECASE):
                            found_deps.add(tool)
            
            # Also check shell scripts
            for script_file in scripts_dir.glob("*.sh"):
                content = script_file.read_text(encoding="utf-8")
                for tool in ["openclaw", "lsof", "ps", "launchctl", "curl", "wget", "git", "which", "kill", "killall"]:
                    if re.search(rf"\\b{tool}\\b", content, re.IGNORECASE):
                        found_deps.add(tool)
        
        # Check if Requirements section exists
        has_requirements = bool(re.search(r"##\s+Requirements?", skill_content, re.IGNORECASE))
        
        # Check if dependencies are mentioned in Requirements section
        deps_mentioned = False
        if has_requirements and found_deps:
            # Extract Requirements section content
            req_match = re.search(r"##\s+Requirements?.*?##", skill_content, re.IGNORECASE | re.DOTALL)
            if req_match:
                req_content = req_match.group(0).lower()
                deps_mentioned = all(dep.lower() in req_content for dep in found_deps)
        
        if found_deps:
            if not has_requirements:
                self.issues.append({
                    "type": "missing_requirements",
                    "severity": "medium",
                    "message": f"Skill uses system dependencies ({', '.join(sorted(found_deps))}) but no Requirements section found in SKILL.md",
                    "fix": "Add a ## Requirements section listing all CLI tools and system dependencies"
                })
            elif not deps_mentioned:
                self.warnings.append({
                    "type": "requirements_incomplete",
                    "severity": "low",
                    "message": f"Skill uses system dependencies ({', '.join(sorted(found_deps))}) but they're not all mentioned in Requirements section",
                    "fix": "Update Requirements section to list all CLI tools and system dependencies used by the skill"
                })

    def check_secret_logging(self):
        """Check for secrets being logged to files."""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        for script_file in scripts_dir.glob("*.py"):
            content = script_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Look for log file paths
            log_paths = []
            for i, line in enumerate(lines, 1):
                # Find log file paths
                match = re.search(r"['\"]([^'\"]+\.log)['\"]", line)
                if match:
                    log_paths.append((i, match.group(1)))
            
            # Check each log file usage
            for log_line_num, log_path in log_paths:
                # Look for writes to this log file
                for i, line in enumerate(lines, 1):
                    if log_path in line and ("write" in line.lower() or "logf" in line or "log_file" in line.lower() or "open" in line.lower()):
                        # Check if command with secrets is being written
                        # Look ahead and behind a few lines for command construction
                        context_start = max(0, i - 15)
                        context_end = min(len(lines), i + 10)
                        context = "\n".join(lines[context_start:context_end])
                        
                        # Pattern 1: Writing joined command array (e.g., ' '.join(cmd))
                        if re.search(r"['\"].*join\(.*cmd|' '.join\(.*cmd|\+.*cmd", context, re.IGNORECASE):
                            # Check if cmd contains secrets
                            if re.search(r"cmd.*--(token|password|auth)|--(token|password|auth).*cmd", context, re.IGNORECASE):
                                self.issues.append({
                                    "type": "secret_logging",
                                    "severity": "high",
                                    "message": f"{script_file.name}:{i} - Full command with secrets written to log file '{log_path}'",
                                    "fix": "Do not log full command strings containing secrets. Log only command name and masked arguments (e.g., log cmd[0] + '***' for args)"
                                })
                        
                        # Pattern 2: Direct write of command string with secrets
                        if re.search(r"write.*\(.*['\"].*--(token|password|auth)", line, re.IGNORECASE):
                            self.issues.append({
                                "type": "secret_logging",
                                "severity": "high",
                                "message": f"{script_file.name}:{i} - Command with secrets written to log file '{log_path}'",
                                "fix": "Do not log full command strings containing secrets. Log only command name and masked arguments"
                            })
                        
                        # Pattern 3: subprocess.Popen with stdout/stderr to log file and cmd contains secrets
                        if "subprocess" in context.lower() and ("Popen" in context or "run" in context):
                            # Check if cmd variable is passed and contains secrets
                            cmd_context = "\n".join(lines[max(0, i-20):min(len(lines), i+5)])
                            if re.search(r"cmd.*=.*\[.*--(token|password|auth)", cmd_context, re.IGNORECASE):
                                # Only flag if stdout/stderr are actually sent to the log (not DEVNULL)
                                if "devnull" in context.lower() and "stdout" in context.lower() and "stderr" in context.lower():
                                    continue  # Safe: output discarded
                                if "stdout" in line.lower() or "stderr" in line.lower() or log_path in line:
                                    self.issues.append({
                                        "type": "secret_logging",
                                        "severity": "high",
                                        "message": f"{script_file.name}:{i} - Command with secrets passed to subprocess with output to log file '{log_path}'",
                                        "fix": "Do not pass commands with secrets to subprocess when stdout/stderr goes to log files. Mask secrets in command or redirect output elsewhere"
                                    })
                        
                        # Pattern 4: Direct secret/token/password variable in write statement
                        if re.search(r"write.*\(.*(secret|token|password)", line, re.IGNORECASE):
                            self.issues.append({
                                "type": "secret_logging",
                                "severity": "high",
                                "message": f"{script_file.name}:{i} - Potential secret value written to log file '{log_path}'",
                                "fix": "Mask secrets before logging (e.g., log only hash or '***') or avoid logging command arguments containing secrets"
                            })

    def check_missing_files(self):
        """Check for referenced files that don't exist in the skill."""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        for script_file in scripts_dir.glob("*.sh"):
            content = script_file.read_text(encoding="utf-8")
            
            # Look for file references
            for match in re.finditer(r"([\"'])([^\"']+\.(plist|json|py|sh))\\1", content):
                ref_file = match.group(2)
                # Check if it's a relative path
                if not ref_file.startswith("/") and not ref_file.startswith("$"):
                    full_path = self.skill_dir / ref_file
                    if not full_path.exists():
                        # Check if it's in scripts/
                        script_path = scripts_dir / ref_file
                        if not script_path.exists():
                            self.issues.append({
                                "type": "missing_file",
                                "severity": "medium",
                                "message": f"{script_file.name} references '{ref_file}' which doesn't exist",
                                "fix": f"Add the missing file or update the reference"
                            })

    def check_env_vars_declaration(self):
        """Check if environment variables are declared."""
        scripts_dir = self.skill_dir / "scripts"
        skill_md = self.skill_dir / "SKILL.md"
        
        if not scripts_dir.exists():
            return
        
        # Find env vars used in scripts
        found_env_vars = set()
        for script_file in scripts_dir.glob("*.py"):
            content = script_file.read_text(encoding="utf-8")
            for match in re.finditer(r"os\.environ\.get\(['\"]([^'\"]+)['\"]", content):
                found_env_vars.add(match.group(1))
            for match in re.finditer(r"os\.getenv\(['\"]([^'\"]+)['\"]", content):
                found_env_vars.add(match.group(1))
        
        if found_env_vars:
            doc_content = ""
            if skill_md.exists():
                doc_content += skill_md.read_text(encoding="utf-8") + "\n"
            readme = self.skill_dir / "README.md"
            if readme.exists():
                doc_content += readme.read_text(encoding="utf-8")
            # Check if env vars are mentioned in SKILL.md or README
            env_vars_mentioned = any(
                re.search(rf"\b{re.escape(var)}\b", doc_content, re.IGNORECASE)
                for var in found_env_vars
            )
            
            if not env_vars_mentioned:
                self.warnings.append({
                    "type": "env_vars_not_declared",
                    "severity": "low",
                    "message": f"Scripts use environment variables ({', '.join(sorted(found_env_vars))}) but they're not documented",
                    "fix": "Document required environment variables in SKILL.md Requirements section"
                })

    def check_persistent_behavior(self):
        """Check for LaunchAgent/daemon behavior without always:true."""
        scripts_dir = self.skill_dir / "scripts"
        meta_json = self.skill_dir / "_meta.json"
        
        if not scripts_dir.exists():
            return
        
        # Check for LaunchAgent install scripts
        has_launchagent = False
        for script_file in scripts_dir.glob("*.sh"):
            content = script_file.read_text(encoding="utf-8")
            if "launchctl" in content.lower() or "plist" in content.lower():
                has_launchagent = True
                break
        
        if has_launchagent:
            meta = {}
            if meta_json.exists():
                try:
                    meta = json.loads(meta_json.read_text(encoding="utf-8"))
                except:
                    pass
            
            if not meta.get("always"):
                self.warnings.append({
                    "type": "persistent_behavior",
                    "severity": "low",
                    "message": "Skill installs LaunchAgent/daemon but _meta.json doesn't have 'always': true",
                    "fix": "Add 'always': true to _meta.json if the skill runs persistently"
                })

    def check_file_permissions(self):
        """Check for log files that might need restricted permissions."""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        for script_file in scripts_dir.glob("*.py"):
            content = script_file.read_text(encoding="utf-8")
            
            # Look for log file creation
            for match in re.finditer(r"open\(['\"]([^'\"]+\.log)['\"]", content):
                log_file = match.group(1)
                # Check if permissions are set
                context_lines = content[:content.find(match.group(0))].split("\n")
                has_permissions = any("chmod" in line or "os.chmod" in line for line in context_lines[-10:])
                
                if not has_permissions and "secret" in log_file.lower() or "auth" in log_file.lower():
                    self.suggestions.append({
                        "type": "log_file_permissions",
                        "severity": "low",
                        "message": f"{script_file.name} creates log file '{log_file}' - consider restricting permissions",
                        "fix": "Set restrictive permissions on log files containing sensitive data: os.chmod(log_path, 0o600)"
                    })

    def check_metadata_docs_env_consistency(self):
        """Check that _meta.json env/optionalEnv matches SKILL.md and README (required vs optional)."""
        meta_json = self.skill_dir / "_meta.json"
        if not meta_json.exists():
            return
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
        except Exception:
            return
        requires = meta.get("requires") or {}
        required_env = set(requires.get("env") or [])
        optional_env = set(requires.get("optionalEnv") or [])
        all_declared = required_env | optional_env
        if not all_declared:
            return
        doc_content = ""
        for name in ("SKILL.md", "README.md"):
            p = self.skill_dir / name
            if p.exists():
                doc_content += "\n" + p.read_text(encoding="utf-8")
        for var in all_declared:
            if not re.search(rf"\b{re.escape(var)}\b", doc_content, re.IGNORECASE):
                continue
            in_required = var in required_env
            in_optional = var in optional_env
            # Look at a window around each occurrence of the var to avoid section headers like "Required:" + list with optional items
            says_optional = False
            says_required = False
            for m in re.finditer(rf"\b{re.escape(var)}\b", doc_content, re.IGNORECASE):
                start = max(0, m.start() - 80)
                end = min(len(doc_content), m.end() + 80)
                window = doc_content[start:end]
                if re.search(r"optional|not required|if unset|defaults to", window, re.IGNORECASE):
                    says_optional = True
                # Only treat as "docs say required" if var is explicitly marked required, e.g. "(required)" or "is required"
                if re.search(r"\((required|mandatory)\)|is (required|mandatory)\b|\b(required|mandatory)\s*:", window, re.IGNORECASE):
                    if not re.search(r"optional|not required", window, re.IGNORECASE):
                        says_required = True
            if in_required and says_optional:
                self.issues.append({
                    "type": "metadata_docs_mismatch",
                    "severity": "medium",
                    "message": f"_meta.json lists {var} in required 'env' but docs describe it as optional",
                    "fix": "Either move " + var + " to optionalEnv in _meta.json or remove 'optional'/'not required' from SKILL.md/README"
                })
            if in_optional and says_required:
                self.warnings.append({
                    "type": "metadata_docs_mismatch",
                    "severity": "low",
                    "message": f"_meta.json lists {var} in optionalEnv but docs say it is required/mandatory",
                    "fix": "Either add " + var + " to requires.env in _meta.json or state in SKILL.md/README that it is optional (e.g. defaults to ~/.openclaw)"
                })

    def check_openclaw_json_read_disclosure(self):
        """If scripts read openclaw.json, docs must disclose it and recommend verifying read access."""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        reads_openclaw_json = False
        for script_file in scripts_dir.glob("*.py"):
            content = script_file.read_text(encoding="utf-8")
            if "openclaw.json" in content or ("openclaw" in content and "json" in content and ("open(" in content or "read" in content.lower())):
                reads_openclaw_json = True
                break
        if not reads_openclaw_json:
            return
        doc_content = ""
        for name in ("SKILL.md", "README.md"):
            p = self.skill_dir / name
            if p.exists():
                doc_content += "\n" + p.read_text(encoding="utf-8")
        # Must mention reading openclaw.json (or tools.exec)
        discloses_read = (
            "openclaw.json" in doc_content
            and ("tools.exec" in doc_content or "read" in doc_content.lower() or "access" in doc_content.lower())
        )
        trust_note = bool(
            re.search(r"comfortable granting read access|verify you are comfortable|before installing", doc_content, re.IGNORECASE)
        )
        if not discloses_read:
            self.issues.append({
                "type": "openclaw_json_not_disclosed",
                "severity": "medium",
                "message": "Scripts read openclaw.json but SKILL.md/README do not clearly disclose it and which fields are used",
                "fix": "Document in SKILL.md/README that the skill reads openclaw.json (e.g. tools.exec.host/node only) and only those fields"
            })
        elif not trust_note:
            self.warnings.append({
                "type": "openclaw_json_trust_note_missing",
                "severity": "low",
                "message": "Skill reads openclaw.json but docs don't ask installers to verify they're comfortable granting read access",
                "fix": "Add a 'Before installing' or Requirements note: 'Verify you are comfortable granting read access to that file.'"
            })

    def check_cli_safe_subprocess_warning(self):
        """If docs show CLI examples with user-supplied args, they must warn to use subprocess with list args (no shell)."""
        doc_content = ""
        for name in ("SKILL.md", "README.md"):
            p = self.skill_dir / name
            if p.exists():
                doc_content += "\n" + p.read_text(encoding="utf-8")
        # CLI examples that pass a quoted string (user message / task) as last or only arg
        has_user_arg_cli = bool(
            re.search(r"(python|python3).*\.py\s+[^\n]*--(json|spawn|classify)\s+[\"'].*[\"']", doc_content)
            or re.search(r"spawn\s+--json\s+[\"']", doc_content)
        )
        safe_keywords = (
            "subprocess" in doc_content
            and ("list of arguments" in doc_content or "list arguments" in doc_content or "shell interpolation" in doc_content.lower()
                 or "manual/cli use only" in doc_content.lower() or "manual use only" in doc_content.lower()
                 or "do not build a shell command" in doc_content.lower())
        )
        if has_user_arg_cli and not safe_keywords:
            self.warnings.append({
                "type": "cli_safe_subprocess_warning_missing",
                "severity": "medium",
                "message": "Docs show CLI examples with user-supplied task/message in quotes but no warning to use subprocess with list args for programmatic use",
                "fix": "Add above Commands/CLI: 'Manual/CLI use only. From code with user input, use subprocess.run(..., [..., user_message], ...) with a list of arguments; do not build a shell command string.'"
            })

    def run_all_checks(self):
        """Run all security checks."""
        self.check_requirements_declaration()
        self.check_secret_logging()
        self.check_missing_files()
        self.check_env_vars_declaration()
        self.check_persistent_behavior()
        self.check_file_permissions()
        self.check_metadata_docs_env_consistency()
        self.check_openclaw_json_read_disclosure()
        self.check_cli_safe_subprocess_warning()

    def generate_report(self, json_output: bool = False) -> str:
        """Generate a security review report."""
        self.run_all_checks()
        
        if json_output:
            return json.dumps({
                "issues": self.issues,
                "warnings": self.warnings,
                "suggestions": self.suggestions,
                "summary": {
                    "total_issues": len(self.issues),
                    "total_warnings": len(self.warnings),
                    "total_suggestions": len(self.suggestions),
                    "high_severity": len([i for i in self.issues if i["severity"] == "high"]),
                    "medium_severity": len([i for i in self.issues if i["severity"] == "medium"]),
                }
            }, indent=2)
        
        # Text report
        lines = []
        lines.append("=" * 70)
        lines.append("SECURITY REVIEW REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        if not self.issues and not self.warnings and not self.suggestions:
            lines.append("✓ No security issues found!")
            lines.append("")
            return "\n".join(lines)
        
        if self.issues:
            lines.append(f"ISSUES ({len(self.issues)}):")
            lines.append("-" * 70)
            for issue in self.issues:
                lines.append(f"[{issue['severity'].upper()}] {issue['type']}")
                lines.append(f"  {issue['message']}")
                lines.append(f"  Fix: {issue['fix']}")
                lines.append("")
        
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            lines.append("-" * 70)
            for warning in self.warnings:
                lines.append(f"[{warning['severity'].upper()}] {warning['type']}")
                lines.append(f"  {warning['message']}")
                lines.append(f"  Fix: {warning['fix']}")
                lines.append("")
        
        if self.suggestions:
            lines.append(f"SUGGESTIONS ({len(self.suggestions)}):")
            lines.append("-" * 70)
            for suggestion in self.suggestions:
                lines.append(f"[{suggestion['severity'].upper()}] {suggestion['type']}")
                lines.append(f"  {suggestion['message']}")
                lines.append(f"  Fix: {suggestion['fix']}")
                lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Security review checker for OpenClaw skills")
    ap.add_argument("skill_dir", type=Path, help="Path to skill directory")
    ap.add_argument("--json", action="store_true", help="Output JSON format")
    args = ap.parse_args()
    
    skill_dir = Path(args.skill_dir)
    if not skill_dir.exists():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    
    reviewer = SecurityReviewer(skill_dir)
    report = reviewer.generate_report(json_output=args.json)
    print(report)
    
    # Exit with error code if there are high-severity issues
    if reviewer.issues:
        high_severity = [i for i in reviewer.issues if i["severity"] == "high"]
        if high_severity:
            sys.exit(1)


if __name__ == "__main__":
    main()
