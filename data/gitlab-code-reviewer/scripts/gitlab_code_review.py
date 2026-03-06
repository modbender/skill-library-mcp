#!/usr/bin/env python3
"""
GitLab Code Reviewer - Main Orchestrator

Performs senior-level code review on GitLab merge requests.
Analyzes code for architecture, security, performance, readability, tests, and best practices.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Import local modules
from diff_parser import DiffParser, ParsedDiff, FileChange, ChangeType
from security_scanner import SecurityScanner, SecurityReport, Severity, generate_security_summary


class Priority(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class ReviewComment:
    """Represents a single review comment."""
    priority: Priority
    category: str
    file_path: str
    line_number: Optional[int]
    description: str
    suggestion: Optional[str] = None
    context: Optional[str] = None
    code_example: Optional[str] = None

    def to_gitlab_note(self, position: Optional[Dict] = None) -> Dict:
        """Convert to GitLab note format."""
        body = self._format_comment()
        note = {"body": body}

        if position:
            note["position"] = position

        return note

    def _format_comment(self) -> str:
        """Format comment for GitLab."""
        emoji = {"critical": "🔴", "major": "🟡", "minor": "🟢"}[self.priority.value]
        lines = [f"{emoji} **{self.category}**"]
        lines.append(self.description)

        if self.suggestion:
            lines.append(f"\n**Suggestion:** {self.suggestion}")

        if self.code_example:
            lines.append(f"\n```{self._get_language()}\n{self.code_example}\n```")

        return "\n".join(lines)

    def _get_language(self) -> str:
        """Get code language for syntax highlighting."""
        ext = self.file_path.rsplit(".", 1)[-1].lower() if "." in self.file_path else ""
        lang_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "jsx": "javascript",
            "rb": "ruby",
            "java": "java",
            "go": "go",
            "rs": "rust",
            "php": "php",
            "cpp": "cpp",
            "c": "c",
            "cs": "csharp",
            "swift": "swift",
            "kt": "kotlin",
            "scala": "scala",
            "sh": "bash",
            "sql": "sql",
            "html": "html",
            "css": "css",
            "scss": "scss",
            "json": "json",
            "yaml": "yaml",
            "yml": "yaml",
            "xml": "xml",
            "md": "markdown",
        }
        return lang_map.get(ext, "")


@dataclass
class CodeReviewReport:
    """Complete code review report."""
    merge_request_info: Optional[Dict] = None
    comments: List[ReviewComment] = field(default_factory=list)
    security_report: Optional[SecurityReport] = None
    files_reviewed: int = 0
    total_additions: int = 0
    total_deletions: int = 0

    def add_comment(self, comment: ReviewComment) -> None:
        self.comments.append(comment)

    def get_comments_by_priority(self, priority: Priority) -> List[ReviewComment]:
        return [c for c in self.comments if c.priority == priority]

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Code Review Report",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        if self.merge_request_info:
            mr = self.merge_request_info
            lines.extend([
                "## Merge Request",
                f"- **Project:** {mr.get('project_id', 'N/A')}",
                f"- **MR:** !{mr.get('iid', 'N/A')}",
                f"- **Title:** {mr.get('title', 'N/A')}",
                f"- **Branch:** `{mr.get('source_branch', 'N/A')}` → `{mr.get('target_branch', 'N/A')}`",
                "",
            ])

        lines.extend([
            "## Summary",
            f"- **Files reviewed:** {self.files_reviewed}",
            f"- **Additions:** +{self.total_additions}",
            f"- **Deletions:** -{self.total_deletions}",
            f"- **Total comments:** {len(self.comments)}",
            "",
        ])

        if self.security_report:
            lines.extend([
                "## 🔒 Security",
                generate_security_summary(self.security_report),
                "",
            ])

        for priority in [Priority.CRITICAL, Priority.MAJOR, Priority.MINOR]:
            comments = self.get_comments_by_priority(priority)
            if not comments:
                continue

            emoji = {"critical": "🔴", "major": "🟡", "minor": "🟢"}[priority.value]
            lines.extend([
                f"## {emoji} {priority.value.upper()} ({len(comments)})",
                "",
            ])

            for comment in comments:
                lines.append(f"### `{comment.file_path}`" + (f":{comment.line_number}" if comment.line_number else ""))
                lines.append(comment.description)
                if comment.suggestion:
                    lines.append(f"\n**Suggestion:** {comment.suggestion}")
                if comment.code_example:
                    lines.append(f"\n```{comment._get_language()}\n{comment.code_example}\n```")
                lines.append("")

        return "\n".join(lines)


class GitLabClient:
    """GitLab API client."""

    def __init__(self, token: str, host: str = "https://gitlab.com"):
        self.token = token
        self.host = host.rstrip("/")
        self.session = self._create_session()

    def _create_session(self):
        """Create requests session with auth."""
        try:
            import requests
        except ImportError:
            print("Error: 'requests' library required. Install with: pip install requests")
            sys.exit(1)

        session = requests.Session()
        session.headers.update({
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json",
        })

        return session

    def validate_token(self) -> bool:
        """
        Validate the GitLab token by fetching current user.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            url = f"{self.host}/api/v4/user"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                return False
            else:
                # Other errors - assume valid but warn
                return True

        except Exception:
            return True  # Assume valid on network errors

    def get_current_user(self) -> Optional[Dict]:
        """
        Get current authenticated user info.

        Returns:
            User dict or None if authentication failed
        """
        try:
            url = f"{self.host}/api/v4/user"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def get_project(self, project_id: str) -> Dict:
        """Get project info."""
        url = f"{self.host}/api/v4/projects/{project_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_merge_request(self, project_id: str, mr_iid: int) -> Dict:
        """Get merge request info."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_iid}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_mr_changes(self, project_id: str, mr_iid: int) -> Dict:
        """Get merge request changes (diff)."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_mr_commits(self, project_id: str, mr_iid: int) -> List[Dict]:
        """Get merge request commits."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/commits"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def post_comment(self, project_id: str, mr_iid: int, body: str, position: Optional[Dict] = None) -> Dict:
        """Post a comment to MR."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
        data = {"body": body}
        if position:
            data["position"] = position
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def post_discussion(self, project_id: str, mr_iid: int, body: str, position: Optional[Dict] = None) -> Dict:
        """Post a new discussion to MR."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/discussions"
        data = {"body": body}
        if position:
            data["position"] = position
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()


class CodeReviewer:
    """
    Main code reviewer class.

    Performs comprehensive analysis of code changes.
    """

    def __init__(
        self,
        ignore_patterns: Optional[List[str]] = None,
        enabled_security_checks: Optional[List[str]] = None,
    ):
        self.diff_parser = DiffParser(ignore_patterns or [])
        self.security_scanner = SecurityScanner(enabled_security_checks)

    def review_parsed_diff(self, parsed_diff: ParsedDiff) -> CodeReviewReport:
        """
        Perform code review on parsed diff.

        Args:
            parsed_diff: ParsedDiff from DiffParser

        Returns:
            CodeReviewReport with all findings
        """
        report = CodeReviewReport(
            merge_request_info=parsed_diff.merge_request_info,
            files_reviewed=len(parsed_diff.files),
            total_additions=parsed_diff.total_additions,
            total_deletions=parsed_diff.total_deletions,
        )

        # Run security scan
        report.security_report = self.security_scanner.scan(parsed_diff)

        # Add security issues as comments
        if report.security_report:
            for issue in report.security_report.issues:
                priority = self._security_severity_to_priority(issue.severity)
                report.add_comment(ReviewComment(
                    priority=priority,
                    category="Security",
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    description=issue.description,
                    suggestion=issue.recommendation,
                    context=f"CWE: {issue.cwe_id}" if issue.cwe_id else None,
                ))

        # Analyze each file
        for file_change in parsed_diff.files:
            self._analyze_file(file_change, report)

        return report

    def _security_severity_to_priority(self, severity: Severity) -> Priority:
        """Convert security severity to review priority."""
        if severity in [Severity.CRITICAL, Severity.HIGH]:
            return Priority.CRITICAL
        elif severity == Severity.MEDIUM:
            return Priority.MAJOR
        return Priority.MINOR

    def _analyze_file(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Analyze a single file change."""
        # Check for large files
        if file_change.additions > 500:
            report.add_comment(ReviewComment(
                priority=Priority.MAJOR,
                category="Code Quality",
                file_path=file_change.path,
                line_number=None,
                description=f"Large change: {file_change.additions} additions. Consider splitting into smaller MRs.",
                suggestion="Break this into smaller, focused merge requests for easier review.",
            ))

        # Check for high complexity (many additions in one file)
        if file_change.additions > 100:
            report.add_comment(ReviewComment(
                priority=Priority.MINOR,
                category="Code Quality",
                file_path=file_change.path,
                line_number=None,
                description=f"Significant changes ({file_change.additions} additions). Ensure adequate test coverage.",
            ))

        # File-specific checks
        ext = file_change.extension

        if ext == "py":
            self._analyze_python(file_change, report)
        elif ext in ["js", "ts", "jsx", "tsx"]:
            self._analyze_javascript(file_change, report)
        elif ext == "java":
            self._analyze_java(file_change, report)
        elif ext == "go":
            self._analyze_go(file_change, report)
        elif ext == "rb":
            self._analyze_ruby(file_change, report)
        elif ext == "php":
            self._analyze_php(file_change, report)
        elif ext in ["yml", "yaml"]:
            self._analyze_yaml(file_change, report)
        elif ext == "json":
            self._analyze_json(file_change, report)

        # General checks
        self._check_debug_code(file_change, report)
        self._check_todo_comments(file_change, report)
        self._check_hardcoded_values(file_change, report)
        self._check_error_handling(file_change, report)

    def _analyze_python(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Python-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for print statements
            if re.search(r'^print\s*\(', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Print statement found. Use logging module instead.",
                    suggestion="Replace with logging.debug/info/warning/error as appropriate.",
                ))

            # Check for bare except
            if re.search(r'^except\s*:', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MAJOR,
                    category="Error Handling",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Bare except clause catches all exceptions including SystemExit and KeyboardInterrupt.",
                    suggestion="Use 'except Exception:' or catch specific exceptions.",
                    code_example="try:\n    # code\nexcept SpecificError as e:\n    # handle",
                ))

            # Check for eval/exec
            if re.search(r'\b(eval|exec)\s*\(', content):
                report.add_comment(ReviewComment(
                    priority=Priority.CRITICAL,
                    category="Security",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="eval/exec can execute arbitrary code. Avoid if possible.",
                    suggestion="Use ast.literal_eval for safe parsing or find alternative approaches.",
                ))

            # Check for missing type hints on new functions
            if re.search(r'^def\s+\w+\s*\([^)]*\)\s*:', content) and '->' not in content:
                if not re.search(r'^\s*def\s+__\w+__\s*\(', content):  # Skip dunder methods
                    report.add_comment(ReviewComment(
                        priority=Priority.MINOR,
                        category="Code Style",
                        file_path=file_change.path,
                        line_number=line.line_number_new,
                        description="Function without type hints.",
                        suggestion="Add type hints for better code documentation and IDE support.",
                        code_example="def my_function(param: str) -> int:\n    ...",
                    ))

    def _analyze_javascript(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """JavaScript/TypeScript-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for var instead of let/const
            if re.search(r'^\s*var\s+', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Style",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Using 'var' instead of 'let' or 'const'.",
                    suggestion="Prefer 'const' by default, use 'let' for variables that change.",
                ))

            # Check for console.log
            if re.search(r'console\.(log|debug|info|warn|error)\s*\(', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Console statement found.",
                    suggestion="Remove console statements before merging or use a proper logging library.",
                ))

            # Check for any instead of specific types (TypeScript)
            if re.search(r':\s*any\b', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="TypeScript",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Using 'any' type defeats TypeScript's type safety.",
                    suggestion="Use specific types, interfaces, or generics instead.",
                ))

            # Check for missing await
            if re.search(r'await\s+', content) is None and re.search(r'\.then\s*\(', content) is None:
                if re.search(r'(async\s+\w+\s*\([^)]*\))', content):
                    # Async function without await might be missing await
                    report.add_comment(ReviewComment(
                        priority=Priority.MINOR,
                        category="Code Quality",
                        file_path=file_change.path,
                        line_number=line.line_number_new,
                        description="Async function without await. Did you forget to await a promise?",
                    ))

    def _analyze_java(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Java-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for System.out.println
            if re.search(r'System\.out\.(print|println)', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="System.out.println found. Use a logging framework instead.",
                    suggestion="Use SLF4J, Log4j, or java.util.logging.",
                ))

            # Check for empty catch blocks
            if re.search(r'}\s*catch\s*\([^)]+\)\s*\{\s*\}', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MAJOR,
                    category="Error Handling",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Empty catch block swallows exceptions silently.",
                    suggestion="Log the exception or handle it appropriately.",
                ))

    def _analyze_go(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Go-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for ignored errors
            if re.search(r'=\s*_\s*$', content) and 'err' in content.lower():
                report.add_comment(ReviewComment(
                    priority=Priority.MAJOR,
                    category="Error Handling",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Error value is explicitly ignored. Ensure this is intentional.",
                    suggestion="Handle the error or document why it's safe to ignore.",
                ))

            # Check for missing error check after function call
            # This is a simplified check

    def _analyze_ruby(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Ruby-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for puts/p in production code
            if re.search(r'^(puts|p)\s+', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Debug output found. Use Rails.logger or a logging library.",
                ))

            # Check for rescue without specific exception
            if re.search(r'^rescue\s*$', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MAJOR,
                    category="Error Handling",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Bare rescue catches all exceptions including SignalException.",
                    suggestion="Rescue specific exceptions: rescue StandardError => e",
                ))

    def _analyze_php(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """PHP-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for var_dump/print_r
            if re.search(r'(var_dump|print_r|echo\s+["\'].*debug)', content, re.IGNORECASE):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Debug output found. Remove before merging.",
                ))

            # Check for @ error suppression
            if re.search(r'@\s*\w+\s*\(', content):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description="Error suppression operator (@) hides errors.",
                    suggestion="Handle errors properly instead of suppressing them.",
                ))

    def _analyze_yaml(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """YAML-specific analysis."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content

            # Check for hardcoded secrets in YAML
            if re.search(r'(password|secret|token|key)\s*:\s*\S+', content, re.IGNORECASE):
                if not re.search(r'\$\{|\{\{|\(env', content, re.IGNORECASE):
                    report.add_comment(ReviewComment(
                        priority=Priority.CRITICAL,
                        category="Security",
                        file_path=file_change.path,
                        line_number=None,
                        description="Potential hardcoded secret in YAML configuration.",
                        suggestion="Use environment variables or a secrets manager.",
                    ))

    def _analyze_json(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """JSON-specific analysis."""
        # Check for sensitive data in JSON files
        content = file_change.diff
        if re.search(r'(password|secret|token|api_key|apikey)', content, re.IGNORECASE):
            report.add_comment(ReviewComment(
                priority=Priority.MAJOR,
                category="Security",
                file_path=file_change.path,
                line_number=None,
                description="JSON file may contain sensitive data.",
                suggestion="Ensure this file doesn't contain secrets and is safe to commit.",
            ))

    def _check_debug_code(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Check for debug code that should be removed."""
        debug_patterns = [
            (r'(?i)debugger\s*;', "JavaScript debugger statement"),
            (r'(?i)binding\.break\s*\(', "Ruby debugger"),
            (r'(?i)import\s+pdb', "Python debugger import"),
            (r'(?i)logging\.setLevel\s*\(\s*DEBUG', "Debug logging level in code"),
        ]

        for line in file_change.lines:
            if not line.is_addition:
                continue

            for pattern, description in debug_patterns:
                if re.search(pattern, line.content):
                    report.add_comment(ReviewComment(
                        priority=Priority.MAJOR,
                        category="Code Quality",
                        file_path=file_change.path,
                        line_number=line.line_number_new,
                        description=f"{description} found. Remove before merging.",
                        suggestion="Remove debug code before merging to production.",
                    ))

    def _check_todo_comments(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Check for TODO/FIXME comments."""
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content
            if re.search(r'#?\s*(TODO|FIXME|XXX|HACK)\s*[:\(]', content, re.IGNORECASE):
                report.add_comment(ReviewComment(
                    priority=Priority.MINOR,
                    category="Code Quality",
                    file_path=file_change.path,
                    line_number=line.line_number_new,
                    description=f"TODO comment: {content.strip()}",
                    suggestion="Consider addressing this TODO or creating a tracking issue.",
                ))

    def _check_hardcoded_values(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Check for hardcoded values that should be configurable."""
        # Check for hardcoded URLs
        for line in file_change.lines:
            if not line.is_addition:
                continue

            content = line.content
            if re.search(r'https?://[^\s"\']+', content):
                if not re.search(r'(env|process\.env|config|settings)', content, re.IGNORECASE):
                    # Might be a hardcoded URL
                    pass  # Could add a warning here

    def _check_error_handling(self, file_change: FileChange, report: CodeReviewReport) -> None:
        """Check for proper error handling patterns."""
        # This is a placeholder for more sophisticated error handling analysis
        pass


def load_credentials() -> Tuple[str, str, Optional[List[str]]]:
    """Load GitLab credentials from config file."""
    # Priority 1: Environment variables
    token = os.environ.get("GITLAB_TOKEN")
    host = os.environ.get("GITLAB_HOST", "https://gitlab.com")

    if token:
        return token, host, None

    # Priority 2: Credentials file
    cred_paths = [
        Path.home() / ".openclaw" / "credentials" / "gitlab.json",
        Path.home() / ".config" / "openclaw" / "credentials" / "gitlab.json",
    ]

    for cred_path in cred_paths:
        if cred_path.exists():
            with open(cred_path, "r") as f:
                creds = json.load(f)
                token = creds.get("token")
                host = creds.get("host", "https://gitlab.com")
                ignore_patterns = creds.get("ignore_patterns")
                if token:
                    return token, host, ignore_patterns

    return None, host, None


@dataclass
class GitLabUrl:
    """Parsed GitLab URL components."""
    host: str
    project: str
    mr_iid: int
    url: str


def parse_gitlab_url(url: str) -> Optional[GitLabUrl]:
    """
    Parse a GitLab merge request URL into components.

    Supported formats:
    - https://gitlab.com/group/project/-/merge_requests/123
    - https://git.company.com/group/subgroup/project/-/merge_requests/123
    - https://git.company.com/group/project/merge_requests/123 (older format)

    Args:
        url: Full GitLab MR URL

    Returns:
        GitLabUrl object or None if parsing fails
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
    except Exception:
        return None

    # Must have a valid scheme and netloc
    if not parsed.scheme or not parsed.netloc:
        return None

    # Extract host
    host = f"{parsed.scheme}://{parsed.netloc}"

    # Extract path components
    path = parsed.path.strip("/")
    if not path:
        return None

    parts = path.split("/")

    # Look for merge_requests pattern
    mr_index = -1
    for i, part in enumerate(parts):
        if part == "merge_requests":
            mr_index = i
            break

    if mr_index == -1 or mr_index + 1 >= len(parts):
        return None

    # Extract MR IID
    try:
        mr_iid = int(parts[mr_index + 1])
    except ValueError:
        return None

    # Extract project path (everything before /-/merge_requests or /merge_requests)
    # Handle both /-/merge_requests and /merge_requests formats
    if mr_index > 0 and parts[mr_index - 1] == "-":
        project_parts = parts[:mr_index - 1]
    else:
        project_parts = parts[:mr_index]

    if not project_parts:
        return None

    project = "/".join(project_parts)

    return GitLabUrl(
        host=host,
        project=project,
        mr_iid=mr_iid,
        url=url
    )


def load_diff_from_file(file_path: str) -> str:
    """Load diff from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        data = json.loads(content)
        if "changes" in data:
            return content  # GitLab API format
        if "diff" in data:
            return data["diff"]
    except json.JSONDecodeError:
        pass

    return content


def main():
    parser = argparse.ArgumentParser(
        description="GitLab Code Reviewer - Senior-level code review for MRs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project group/project --mr 42
  %(prog)s --project group/project --mr 42 --post-comments
  %(prog)s --diff-file changes.json
  %(prog)s --project group/project --mr 42 --output review.md
  %(prog)s --project group/project --mr 42 --ignore "*.json" "*.lock"
  %(prog)s --url "https://gitlab.com/group/project/-/merge_requests/123"
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--project", "-p",
        help="GitLab project (format: group/project or project_id)",
    )
    input_group.add_argument(
        "--diff-file", "-d",
        help="Path to diff/changes JSON file",
    )
    input_group.add_argument(
        "--url", "-u",
        help="Full GitLab MR URL (e.g., https://gitlab.com/group/project/-/merge_requests/123)",
    )

    parser.add_argument(
        "--mr", "-m",
        type=int,
        help="Merge request IID",
    )

    # Auth options
    parser.add_argument(
        "--token", "-t",
        help="GitLab token (overrides env/file)",
    )
    parser.add_argument(
        "--host",
        help="GitLab host URL (overrides env/file)",
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output file path for markdown report",
    )
    parser.add_argument(
        "--post-comments",
        action="store_true",
        help="Post comments to GitLab MR",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    # Filter options
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="File patterns to ignore (e.g., '*.json' '*.lock')",
    )
    parser.add_argument(
        "--no-default-ignores",
        action="store_true",
        help="Disable default ignore patterns",
    )
    parser.add_argument(
        "--security-checks",
        nargs="*",
        help="Enable specific security checks (default: all)",
    )

    args = parser.parse_args()

    # Validate arguments and extract MR info
    project_id = None
    mr_iid = None

    if args.url:
        # Parse URL to extract components
        print(f"Parsing GitLab URL: {args.url}")
        gitlab_url = parse_gitlab_url(args.url)
        
        if not gitlab_url:
            print("Error: Could not parse GitLab URL.")
            print("Expected format: https://host/group/project/-/merge_requests/123")
            sys.exit(1)
        
        project_id = gitlab_url.project
        mr_iid = gitlab_url.mr_iid
        
        # Override host from URL if not specified via --host
        if not args.host:
            host_from_url = gitlab_url.host
        else:
            host_from_url = args.host
            
        print(f"  Host: {gitlab_url.host}")
        print(f"  Project: {gitlab_url.project}")
        print(f"  MR: !{gitlab_url.mr_iid}")
        
    elif args.project:
        project_id = args.project
        mr_iid = args.mr
        host_from_url = args.host or None
        
        if not mr_iid:
            parser.error("--mr is required when using --project")
            
    else:
        # diff-file mode
        project_id = None
        mr_iid = None
        host_from_url = args.host or None

    # Load credentials
    creds = load_credentials()
    token = args.token or creds[0]
    
    # Host priority: --host arg > URL > credentials file > env > default
    host = args.host or host_from_url or creds[1]
    
    creds_ignore_patterns = creds[2]

    if not token and project_id:
        print("Error: GitLab token required. Set GITLAB_TOKEN env var or create ~/.openclaw/credentials/gitlab.json")
        sys.exit(1)

    # Validate token if we have one and are connecting to GitLab
    if token and project_id:
        print("Validating GitLab token...")
        temp_client = GitLabClient(token, host)
        if not temp_client.validate_token():
            print("❌ Error: GitLab token is invalid or expired.")
            print("   Please check your token in ~/.openclaw/credentials/gitlab.json")
            print("   Or generate a new one at: https://gitlab.com/-/profile/personal_access_tokens")
            sys.exit(1)
        
        user = temp_client.get_current_user()
        if user:
            print(f"✅ Authenticated as: {user.get('name', 'Unknown')} (@{user.get('username', 'unknown')})")

    # Initialize reviewer
    # Priority: --ignore argument > credentials file > defaults
    if args.ignore:
        ignore_patterns = args.ignore
    elif creds_ignore_patterns:
        ignore_patterns = creds_ignore_patterns
    elif args.no_default_ignores:
        ignore_patterns = []
    else:
        ignore_patterns = None

    reviewer = CodeReviewer(
        ignore_patterns=ignore_patterns,
        enabled_security_checks=args.security_checks,
    )

    # Get diff
    parsed_diff = None
    mr_info = None
    commits = None

    if args.diff_file:
        print(f"Loading diff from {args.diff_file}...")
        diff_content = load_diff_from_file(args.diff_file)
        try:
            data = json.loads(diff_content)
            if "changes" in data:
                parsed_diff = reviewer.diff_parser.parse_from_gitlab_response(data)
            else:
                parsed_diff = reviewer.diff_parser.parse(diff_content)
        except json.JSONDecodeError:
            parsed_diff = reviewer.diff_parser.parse(diff_content)
    else:
        print(f"Fetching MR !{mr_iid} from {project_id}...")
        client = GitLabClient(token, host)

        # Get project ID (handle group/project format)
        if "/" in project_id and not project_id.isdigit():
            project_id = requests.utils.quote(project_id, safe="")

        try:
            mr_changes = client.get_mr_changes(project_id, mr_iid)
            mr_info = client.get_merge_request(project_id, mr_iid)
            mr_changes["title"] = mr_info.get("title")
            mr_changes["source_branch"] = mr_info.get("source_branch")
            mr_changes["target_branch"] = mr_info.get("target_branch")
            parsed_diff = reviewer.diff_parser.parse_from_gitlab_response(mr_changes)
            
            # Fetch commits for inline comments
            print(f"Fetching commits for MR !{mr_iid}...")
            commits = client.get_mr_commits(project_id, mr_iid)
            
        except Exception as e:
            print(f"Error fetching MR: {e}")
            sys.exit(1)

    if not parsed_diff:
        print("Error: Could not parse diff")
        sys.exit(1)

    # Perform review
    print(f"Reviewing {len(parsed_diff.files)} files ({parsed_diff.total_additions} additions, {parsed_diff.total_deletions} deletions)...")
    report = reviewer.review_parsed_diff(parsed_diff)

    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())
        print(f"Report saved to {args.output}")
    else:
        print("\n" + report.to_markdown())

    # Post comments to GitLab
    if args.post_comments:
        if not project_id or not mr_iid:
            print("Error: --project/--url required for --post-comments")
            sys.exit(1)

        print(f"\nPosting comments to GitLab MR !{mr_iid}...")
        client = GitLabClient(token, host)

        # Get project ID (handle group/project format)
        proj_id = project_id
        if "/" in proj_id and not proj_id.isdigit():
            proj_id = requests.utils.quote(proj_id, safe="")

        # Prepare commit SHAs for inline comments
        base_sha = None
        start_sha = None
        head_sha = None
        
        if mr_info and commits:
            base_sha = mr_info.get("diff_refs", {}).get("base_sha")
            start_sha = commits[0]["id"] if commits else None
            head_sha = commits[-1]["id"] if commits else None
            
            if not base_sha:
                # Fallback: use target_branch sha
                base_sha = mr_info.get("target_branch_sha")

        # Post summary comment
        summary = f"## Code Review Summary\n\n"
        summary += f"- Files reviewed: {report.files_reviewed}\n"
        summary += f"- Total comments: {len(report.comments)}\n"
        summary += f"- Critical: {len(report.get_comments_by_priority(Priority.CRITICAL))}\n"
        summary += f"- Major: {len(report.get_comments_by_priority(Priority.MAJOR))}\n"
        summary += f"- Minor: {len(report.get_comments_by_priority(Priority.MINOR))}\n"

        try:
            client.post_comment(proj_id, mr_iid, summary)
            print("✅ Summary comment posted")

            # Post individual inline comments (limit to avoid spam)
            inline_count = 0
            skipped_count = 0
            
            for comment in report.comments[:20]:
                if not comment.line_number:
                    skipped_count += 1
                    continue
                    
                # Build position for inline comment
                position = {
                    "base_sha": base_sha or "",
                    "start_sha": start_sha or "",
                    "head_sha": head_sha or "",
                    "position_type": "text",
                    "new_path": comment.file_path,
                    "new_line": comment.line_number,
                }
                
                # Check if all SHAs are available
                if not all([base_sha, start_sha, head_sha]):
                    print(f"  ⚠️  Skipping inline comment (missing commit SHAs)")
                    break
                
                try:
                    client.post_discussion(proj_id, mr_iid, comment._format_comment(), position)
                    inline_count += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to post inline comment at {comment.file_path}:{comment.line_number}: {e}")
                    skipped_count += 1

            if inline_count > 0:
                print(f"✅ Posted {inline_count} inline comment(s)")
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} comment(s) without line numbers")

        except Exception as e:
            print(f"Error posting comments: {e}")

    # Exit with error if critical issues found
    critical_count = len(report.get_comments_by_priority(Priority.CRITICAL))
    if critical_count > 0:
        print(f"\n⚠️  {critical_count} critical issue(s) found!")
        sys.exit(2)

    print("\n✅ Review complete!")
    sys.exit(0)


if __name__ == "__main__":
    # Import requests here to avoid error if not needed
    try:
        import requests
    except ImportError:
        pass

    main()
