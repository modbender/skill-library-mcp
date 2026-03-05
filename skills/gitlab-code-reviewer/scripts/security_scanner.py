"""
Security Scanner Module

Detects common security vulnerabilities in code changes.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from diff_parser import FileChange, DiffLine, ParsedDiff


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    SSRF = "ssrf"
    XXE = "xxe"
    AUTH_BYPASS = "auth_bypass"
    INSECURE_CONFIG = "insecure_config"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    UNSAFE_FILE_OPERATION = "unsafe_file_operation"
    MEMORY_SAFETY = "memory_safety"
    RACE_CONDITION = "race_condition"


@dataclass
class SecurityIssue:
    """Represents a detected security issue."""
    vulnerability_type: VulnerabilityType
    severity: Severity
    file_path: str
    line_number: int
    line_content: str
    description: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            'type': self.vulnerability_type.value,
            'severity': self.severity.value,
            'file': self.file_path,
            'line': self.line_number,
            'content': self.line_content.strip(),
            'description': self.description,
            'recommendation': self.recommendation,
            'cwe_id': self.cwe_id,
            'cvss_score': self.cvss_score,
        }


@dataclass
class SecurityReport:
    """Complete security scan report."""
    issues: List[SecurityIssue] = field(default_factory=list)
    files_scanned: int = 0
    lines_scanned: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.LOW)

    def get_by_severity(self, severity: Severity) -> List[SecurityIssue]:
        return [i for i in self.issues if i.severity == severity]

    def get_by_type(self, vuln_type: VulnerabilityType) -> List[SecurityIssue]:
        return [i for i in self.issues if i.vulnerability_type == vuln_type]


class SecurityScanner:
    """
    Scans code changes for security vulnerabilities.

    Uses pattern-based detection for common vulnerability types.
    """

    # SQL Injection patterns
    SQL_KEYWORDS = r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|FROM|WHERE|HAVING|ORDER BY|GROUP BY)'
    SQL_INJECTION_PATTERNS = [
        # String concatenation with SQL
        (r'["\']?\s*\+\s*\w+\s*\+\s*["\']?' + SQL_KEYWORDS, 
         "SQL query built with string concatenation"),
        # Format strings with SQL
        (r'(\.format\(|f["\']|%s|%d).*' + SQL_KEYWORDS,
         "SQL query built with format string"),
        # Raw SQL execution with variables
        (r'(execute|cursor\.execute|raw\(|executeQuery|executeUpdate)\s*\([^)]*[\+%f]',
         "Raw SQL execution with potential variable interpolation"),
        # Django ORM raw queries
        (r'\.raw\(|\.extra\(|\.to_sql\(',
         "Raw SQL in ORM - ensure proper parameterization"),
    ]

    # XSS patterns
    XSS_PATTERNS = [
        (r'innerHTML\s*=', "Direct innerHTML assignment - potential XSS"),
        (r'document\.write\s*\(', "document.write() - potential XSS"),
        (r'\$?\s*\(\s*[\'"]<[^>]*\+', "jQuery/DOM with string concatenation - potential XSS"),
        (r'v-html\s*=', "Vue v-html directive - renders raw HTML"),
        (r'ng-bind-html\s*=', "Angular ng-bind-html - renders raw HTML"),
        (r'dangerouslySetInnerHTML', "React dangerouslySetInnerHTML - renders raw HTML"),
        (r'\<script.*\+', "Script tag with concatenation - potential XSS"),
        (r'eval\s*\([^)]*request', "eval() with user input - critical XSS"),
    ]

    # Command Injection patterns
    CMD_INJECTION_PATTERNS = [
        (r'(exec|system|popen|subprocess\.(call|run|Popen))\s*\([^)]*[\+%]',
         "Command execution with string formatting - potential injection"),
        (r'os\.system\s*\([^)]*\+', "os.system with concatenation - potential injection"),
        (r'child_process\.(exec|spawn)\s*\([^)]*\+', "Node child_process with concatenation"),
        (r'Runtime\.getRuntime\(\)\.exec', "Java Runtime.exec - potential injection"),
        (r'`\s*\$\{[^}]+\}\s*`', "Template literal in shell command"),
        (r'shell:\s*true', "Shell execution enabled in spawn/exec"),
    ]

    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        (r'(readFile|writeFile|open|fopen|file_get_contents)\s*\([^)]*[\+%]',
         "File operation with dynamic path - potential traversal"),
        (r'\.\./', "Path traversal sequence detected"),
        (r'(include|require|require_once|include_once)\s*\([^)]*[\+%]',
         "Dynamic include/require - potential LFI/RFI"),
        (r'Path\.combine\s*\([^)]*request', "Path.Combine with user input"),
    ]

    # Hardcoded secrets patterns
    SECRET_PATTERNS = [
        (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']',
         "Hardcoded password detected"),
        (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']+["\']',
         "Hardcoded API key detected"),
        (r'(?i)(secret|token)\s*[=:]\s*["\'][^"\']{8,}["\']',
         "Hardcoded secret/token detected"),
        (r'(?i)(aws_access_key|aws_secret)\s*[=:]\s*["\'][^"\']+["\']',
         "Hardcoded AWS credential detected"),
        (r'(?i)private[_-]?key\s*[=:]\s*["\']-----BEGIN',
         "Hardcoded private key detected"),
        (r'(?i)(database_url|db_url|connection_string)\s*[=:]\s*["\'][^"\']+["\']',
         "Hardcoded database connection string"),
        (r'Bearer\s+[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+',
         "Hardcoded JWT token detected"),
    ]

    # Weak cryptography patterns
    WEAK_CRYPTO_PATTERNS = [
        (r'(MD5|md5)\s*\(', "MD5 hash - cryptographically broken"),
        (r'(SHA1|sha1)\s*\(', "SHA1 hash - deprecated for security"),
        (r'(DES|des|RC4|rc4|RC2|rc2)\s*\(', "Weak encryption algorithm"),
        (r'Random\s*\(\s*\)', "Non-cryptographic random number generator"),
        (r'math\.random\s*\(', "Non-cryptographic random (Python)"),
        (r'Math\.random\s*\(', "Non-cryptographic random (JS)"),
        (r'crypto\.createHash\s*\(\s*[\'"]md5', "MD5 hash in Node.js"),
        (r'crypto\.createHash\s*\(\s*[\'"]sha1', "SHA1 hash in Node.js"),
    ]

    # Insecure deserialization patterns
    DESERIALIZATION_PATTERNS = [
        (r'pickle\.loads?\s*\(', "Python pickle deserialization - potentially unsafe"),
        (r'yaml\.load\s*\([^)]*\)', "YAML load without safe_load - potential RCE"),
        (r'ObjectInputStream\s*\(', "Java ObjectInputStream - insecure deserialization"),
        (r'unserialize\s*\(', "PHP unserialize - potential code execution"),
        (r'JSON\.parse\s*\([^)]*eval', "JSON.parse with eval - dangerous"),
        (r'reviver\s*:', "JSON reviver function - potential prototype pollution"),
    ]

    # SSRF patterns
    SSRF_PATTERNS = [
        (r'(requests\.get|urllib\.urlopen|http\.get|axios\.get)\s*\([^)]*request',
         "HTTP request with user-controlled URL - potential SSRF"),
        (r'fetch\s*\([^)]*\+', "Fetch with concatenation - potential SSRF"),
        (r'(curl|wget)\s+.*\$', "curl/wget with variable - potential SSRF"),
        (r'127\.0\.0\.1|localhost|0\.0\.0\.0', "Internal address access detected"),
        (r'169\.254\.', "Link-local address access (AWS metadata)"),
    ]

    # XXE patterns (XML External Entity)
    XXE_PATTERNS = [
        (r'XMLParser\s*\(\s*\{[^}]*resolveEntity', "XML parser with entity resolution enabled"),
        (r'DocumentBuilderFactory.*setFeature.*false', "XML feature disabled - check XXE protection"),
        (r'xml\.etree\.ElementTree', "ElementTree - ensure XXE protection"),
        (r'lxml\.etree', "lxml - verify XXE protection settings"),
    ]

    # Authentication bypass patterns
    AUTH_BYPASS_PATTERNS = [
        (r'if\s*\(\s*user\s*==\s*["\']admin', "String comparison for admin check"),
        (r'password\s*==\s*["\'][^"\']+["\']', "Hardcoded password comparison"),
        (r'isAdmin\s*=\s*true', "Hardcoded admin flag"),
        (r'skip.*auth|bypass.*auth|disable.*security', "Authentication bypass keyword"),
        (r'@PreAuthorize\s*\(\s*["\']false', "Spring Security disabled"),
    ]

    # Insecure configuration patterns
    CONFIG_PATTERNS = [
        (r'DEBUG\s*=\s*True', "Debug mode enabled in production"),
        (r'ALLOWED_HOSTS\s*=\s*\[\s*["\']\*', "Wildcard allowed hosts"),
        (r'CORS.*ORIGIN.*\*', "Wildcard CORS origin"),
        (r'ssl.*verify.*False|verify.*ssl.*False', "SSL verification disabled"),
        (r'tls.*verify.*false', "TLS verification disabled"),
        (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', "Hardcoded secret key"),
        (r'cookieSecure\s*:\s*false', "Insecure cookie configuration"),
        (r'httpOnly\s*:\s*false', "HTTPOnly cookie disabled"),
    ]

    # Sensitive data exposure patterns
    SENSITIVE_DATA_PATTERNS = [
        (r'console\.log\s*\([^)]*(password|secret|token|key)', "Logging sensitive data"),
        (r'log.*password|log.*secret|log.*token', "Logging sensitive information"),
        (r'print\s*\([^)]*(password|secret|token|key)', "Printing sensitive data"),
        (r'return.*password|return.*secret', "Returning sensitive data"),
    ]

    # Unsafe file operations
    UNSAFE_FILE_PATTERNS = [
        (r'chmod\s*\([^)]*0?777', "Overly permissive file permissions (777)"),
        (r'umask\s*\(\s*0\s*\)', "Umask set to 0 - no permission restrictions"),
        (r'open\s*\([^)]*["\']w["\'].*system', "Writing to system file"),
        (r'deleteRecursive|rm\s+-rf', "Recursive delete operation"),
    ]

    # Race condition patterns
    RACE_CONDITION_PATTERNS = [
        (r'if\s*\(\s*exists\s*\([^)]+\)\s*\)\s*\{[^}]*open', "TOCTOU race condition pattern"),
        (r'check.*then.*act|validate.*then.*execute', "Check-then-act pattern"),
        (r'File\.exists\s*\([^)]+\).*File\.read', "File exists check before read - TOCTOU"),
        (r'os\.path\.exists\s*\([^)]+\).*open', "Path exists check before open - TOCTOU"),
    ]

    def __init__(self, enabled_checks: Optional[List[str]] = None):
        """
        Initialize security scanner.

        Args:
            enabled_checks: List of check categories to enable.
                           If None, all checks are enabled.
                           Categories: sql, xss, cmd, path, secret, crypto, 
                                      deserialize, ssrf, xxe, auth, config, sensitive, file, race
        """
        self.enabled_checks = enabled_checks
        self.compiled_patterns: Dict[str, List[Tuple[re.Pattern, str]]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile all regex patterns for performance."""
        pattern_maps = {
            'sql': self.SQL_INJECTION_PATTERNS,
            'xss': self.XSS_PATTERNS,
            'cmd': self.CMD_INJECTION_PATTERNS,
            'path': self.PATH_TRAVERSAL_PATTERNS,
            'secret': self.SECRET_PATTERNS,
            'crypto': self.WEAK_CRYPTO_PATTERNS,
            'deserialize': self.DESERIALIZATION_PATTERNS,
            'ssrf': self.SSRF_PATTERNS,
            'xxe': self.XXE_PATTERNS,
            'auth': self.AUTH_BYPASS_PATTERNS,
            'config': self.CONFIG_PATTERNS,
            'sensitive': self.SENSITIVE_DATA_PATTERNS,
            'file': self.UNSAFE_FILE_PATTERNS,
            'race': self.RACE_CONDITION_PATTERNS,
        }

        for category, patterns in pattern_maps.items():
            if self.enabled_checks and category not in self.enabled_checks:
                continue
            self.compiled_patterns[category] = [
                (re.compile(pattern, re.IGNORECASE), desc)
                for pattern, desc in patterns
            ]

    def scan(self, parsed_diff: ParsedDiff) -> SecurityReport:
        """
        Scan parsed diff for security vulnerabilities.

        Args:
            parsed_diff: ParsedDiff object from DiffParser

        Returns:
            SecurityReport with all detected issues
        """
        report = SecurityReport()
        report.files_scanned = len(parsed_diff.files)

        for file_change in parsed_diff.files:
            report.lines_scanned += len(file_change.lines)
            issues = self._scan_file(file_change)
            report.issues.extend(issues)

        # Sort by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        report.issues.sort(key=lambda i: severity_order[i.severity])

        return report

    def _scan_file(self, file_change: FileChange) -> List[SecurityIssue]:
        """Scan a single file for vulnerabilities."""
        issues = []

        # Check file extension for context
        ext = file_change.extension
        is_backend = ext in ['py', 'php', 'rb', 'java', 'js', 'ts', 'go', 'cs']
        is_frontend = ext in ['js', 'ts', 'jsx', 'tsx', 'vue', 'html']
        is_config = ext in ['json', 'yaml', 'yml', 'toml', 'ini', 'env']

        for diff_line in file_change.lines:
            if not diff_line.is_addition:
                continue  # Only scan added/modified lines

            content = diff_line.content
            line_num = diff_line.line_number_new or diff_line.line_number_old or 0

            for category, patterns in self.compiled_patterns.items():
                for pattern, description in patterns:
                    if pattern.search(content):
                        issue = self._create_issue(
                            category=category,
                            description=description,
                            file_path=file_change.path,
                            line_number=line_num,
                            line_content=content,
                            is_backend=is_backend,
                            is_frontend=is_frontend,
                            is_config=is_config,
                        )
                        if issue:
                            issues.append(issue)

        return issues

    def _create_issue(
        self,
        category: str,
        description: str,
        file_path: str,
        line_number: int,
        line_content: str,
        is_backend: bool,
        is_frontend: bool,
        is_config: bool,
    ) -> Optional[SecurityIssue]:
        """Create a SecurityIssue from a pattern match."""
        vuln_type_map = {
            'sql': VulnerabilityType.SQL_INJECTION,
            'xss': VulnerabilityType.XSS,
            'cmd': VulnerabilityType.COMMAND_INJECTION,
            'path': VulnerabilityType.PATH_TRAVERSAL,
            'secret': VulnerabilityType.HARDCODED_SECRET,
            'crypto': VulnerabilityType.WEAK_CRYPTO,
            'deserialize': VulnerabilityType.INSECURE_DESERIALIZATION,
            'ssrf': VulnerabilityType.SSRF,
            'xxe': VulnerabilityType.XXE,
            'auth': VulnerabilityType.AUTH_BYPASS,
            'config': VulnerabilityType.INSECURE_CONFIG,
            'sensitive': VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
            'file': VulnerabilityType.UNSAFE_FILE_OPERATION,
            'race': VulnerabilityType.RACE_CONDITION,
        }

        severity_map = {
            'sql': Severity.HIGH,
            'xss': Severity.HIGH,
            'cmd': Severity.CRITICAL,
            'path': Severity.MEDIUM,
            'secret': Severity.CRITICAL,
            'crypto': Severity.MEDIUM,
            'deserialize': Severity.HIGH,
            'ssrf': Severity.HIGH,
            'xxe': Severity.HIGH,
            'auth': Severity.CRITICAL,
            'config': Severity.MEDIUM,
            'sensitive': Severity.LOW,
            'file': Severity.MEDIUM,
            'race': Severity.MEDIUM,
        }

        recommendation_map = {
            'sql': "Use parameterized queries or prepared statements. Never concatenate user input into SQL queries.",
            'xss': "Sanitize and escape all user input before rendering. Use framework-provided escaping mechanisms.",
            'cmd': "Avoid shell commands with user input. Use safe APIs and validate/sanitize all inputs.",
            'path': "Validate and sanitize file paths. Use allowlists for permitted directories.",
            'secret': "Move secrets to environment variables or a secrets manager. Never commit credentials.",
            'crypto': "Use modern cryptographic algorithms (SHA-256+, AES-256, bcrypt/argon2 for passwords).",
            'deserialize': "Use safe deserialization methods. Validate input data structure before parsing.",
            'ssrf': "Validate URLs against an allowlist. Block internal IP ranges. Use a proxy for external requests.",
            'xxe': "Disable DTD processing in XML parsers. Use safe parsing libraries.",
            'auth': "Use proper authentication frameworks. Never hardcode credentials or bypass security checks.",
            'config': "Use secure defaults. Never enable debug mode in production. Restrict CORS origins.",
            'sensitive': "Remove sensitive data from logs. Use structured logging with field masking.",
            'file': "Use least privilege for file permissions. Validate file operations.",
            'race': "Use atomic operations. Implement proper locking mechanisms for shared resources.",
        }

        cwe_map = {
            'sql': 'CWE-89',
            'xss': 'CWE-79',
            'cmd': 'CWE-78',
            'path': 'CWE-22',
            'secret': 'CWE-798',
            'crypto': 'CWE-327',
            'deserialize': 'CWE-502',
            'ssrf': 'CWE-918',
            'xxe': 'CWE-611',
            'auth': 'CWE-287',
            'config': 'CWE-16',
            'sensitive': 'CWE-532',
            'file': 'CWE-732',
            'race': 'CWE-362',
        }

        vuln_type = vuln_type_map.get(category)
        if not vuln_type:
            return None

        # Adjust severity based on context
        base_severity = severity_map.get(category, Severity.LOW)
        severity = base_severity

        # Some patterns are more severe in certain contexts
        if category == 'xss' and is_backend:
            severity = Severity.CRITICAL
        if category == 'secret' and 'private' in line_content.lower():
            severity = Severity.CRITICAL

        return SecurityIssue(
            vulnerability_type=vuln_type,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            line_content=line_content,
            description=description,
            recommendation=recommendation_map.get(category, "Review and fix this security issue."),
            cwe_id=cwe_map.get(category),
        )

    def scan_content(self, content: str, file_path: str) -> List[SecurityIssue]:
        """
        Scan raw content for security issues.

        Args:
            content: Raw file content to scan
            file_path: Path to the file (for context)

        Returns:
            List of detected security issues
        """
        issues = []
        lines = content.split('\n')

        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        is_backend = ext in ['py', 'php', 'rb', 'java', 'js', 'ts', 'go', 'cs']
        is_frontend = ext in ['js', 'ts', 'jsx', 'tsx', 'vue', 'html']
        is_config = ext in ['json', 'yaml', 'yml', 'toml', 'ini', 'env']

        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.compiled_patterns.items():
                for pattern, description in patterns:
                    if pattern.search(line):
                        issue = self._create_issue(
                            category=category,
                            description=description,
                            file_path=file_path,
                            line_number=line_num,
                            line_content=line,
                            is_backend=is_backend,
                            is_frontend=is_frontend,
                            is_config=is_config,
                        )
                        if issue:
                            issues.append(issue)

        return issues


def generate_security_summary(report: SecurityReport) -> str:
    """Generate a human-readable security summary."""
    if not report.issues:
        return "✅ No security issues detected!"

    lines = [
        f"🔒 Security Scan Results",
        f"Files scanned: {report.files_scanned}",
        f"Lines scanned: {report.lines_scanned}",
        f"",
        f"Summary:",
        f"  🔴 Critical: {report.critical_count}",
        f"  🟠 High: {report.high_count}",
        f"  🟡 Medium: {report.medium_count}",
        f"  🟢 Low: {report.low_count}",
        f"",
    ]

    # Group by severity
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        issues = report.get_by_severity(severity)
        if not issues:
            continue

        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity.value]
        lines.append(f"{emoji} {severity.value.upper()} ({len(issues)}):")

        for issue in issues[:10]:  # Limit to 10 per severity
            lines.append(
                f"  - `{issue.file_path}:{issue.line_number}` - {issue.description}"
            )
            lines.append(f"    CWE: {issue.cwe_id} | {issue.recommendation}")

        if len(issues) > 10:
            lines.append(f"  ... and {len(issues) - 10} more")

        lines.append("")

    return "\n".join(lines)
