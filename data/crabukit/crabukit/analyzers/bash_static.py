"""Enhanced Bash script analyzer with supply chain and backdoor detection."""

import re
from typing import List
from pathlib import Path

from crabukit.rules.patterns import Finding, Severity, BASH_PATTERNS


class BashAnalyzer:
    """Analyze Bash scripts for security issues."""
    
    # Additional risky commands beyond the patterns
    RISKY_COMMANDS = {
        'sudo': Severity.HIGH,
        'su': Severity.HIGH,
        'passwd': Severity.MEDIUM,
        'chown': Severity.MEDIUM,
        'chmod': Severity.LOW,
        'mkfs': Severity.CRITICAL,
        'dd': Severity.HIGH,
        'fdisk': Severity.CRITICAL,
        'kill': Severity.MEDIUM,
        'killall': Severity.MEDIUM,
        'pkill': Severity.MEDIUM,
        'iptables': Severity.HIGH,
        'ufw': Severity.HIGH,
        'sysctl': Severity.HIGH,
        'modprobe': Severity.HIGH,
        'insmod': Severity.HIGH,
    }
    
    def __init__(self, content: str, file_path: Path):
        self.content = content
        self.file_path = file_path
        self.findings: List[Finding] = []
        self.lines = content.split('\n')
        
    def analyze(self) -> List[Finding]:
        """Run all Bash analyses."""
        self.findings = []
        
        # Core dangerous patterns
        self._check_dangerous_patterns()
        
        # Additional security checks
        self._check_sudo_usage()
        self._check_temp_file_security()
        self._check_command_substitution()
        self._check_exported_functions()
        self._check_aliases()
        self._check_source_injection()
        self._check_environment_manipulation()
        self._check_network_connections()
        self._check_backdoor_indicators()
        
        return self.findings
    
    def _check_dangerous_patterns(self):
        """Check for known dangerous patterns."""
        for rule_id, rule in BASH_PATTERNS.items():
            matches = list(re.finditer(rule["pattern"], self.content, re.IGNORECASE | re.MULTILINE))
            
            for match in matches:
                line_num = self.content[:match.start()].count('\n') + 1
                
                # Avoid duplicate findings
                if any(f.line_number == line_num and f.rule_id.startswith(f"BASH_{rule_id.upper()}") for f in self.findings):
                    continue
                
                self.findings.append(Finding(
                    rule_id=f"BASH_{rule_id.upper()}",
                    title=rule["title"],
                    description=rule["description"],
                    severity=rule["severity"],
                    file_path=str(self.file_path),
                    line_number=line_num,
                    code_snippet=self._get_line_snippet(line_num),
                    remediation=rule.get("remediation"),
                    cwe_id=rule.get("cwe"),
                ))
    
    def _check_sudo_usage(self):
        """Check for problematic sudo usage."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
                
            # Check for sudo without full path
            sudo_match = re.search(r'\bsudo\s+(-[A-Za-z]+\s+)*(\w+)', line)
            if sudo_match:
                cmd = sudo_match.group(2)
                if cmd not in ['-S', '-u', '-i', '-H', 'bash', 'sh', 'zsh', 'su']:
                    # Check if full path is used
                    if not cmd.startswith('/'):
                        self.findings.append(Finding(
                            rule_id="BASH_SUDO_NO_PATH",
                            title="sudo without full path",
                            description=f"Using 'sudo {cmd}' without full path - could be shadowed by malicious binary in PATH",
                            severity=Severity.MEDIUM,
                            file_path=str(self.file_path),
                            line_number=i,
                            code_snippet=line.strip(),
                            remediation="Use full path: /usr/bin/{cmd} or verify PATH integrity",
                        ))
            
            # Check for sudo with environment variables
            if re.search(r'sudo\s+\w+=\w+', line):
                self.findings.append(Finding(
                    rule_id="BASH_SUDO_ENV",
                    title="sudo with environment variable",
                    description="Setting environment variables with sudo can modify command behavior",
                    severity=Severity.LOW,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                ))
    
    def _check_temp_file_security(self):
        """Check for insecure temp file handling."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for predictable temp files
            if '/tmp/' in line and not re.search(r'mktemp|\$\(mktemp|\`mktemp', line):
                if any(cmd in line for cmd in ['>', 'cat', 'tee', 'cp', 'mv', 'echo']):
                    # Check if it's writing to a predictable filename
                    tmp_match = re.search(r'/tmp/([a-zA-Z0-9_\-\.]+)', line)
                    if tmp_match:
                        filename = tmp_match.group(1)
                        # Check if it uses PID or random suffix
                        if not re.search(r'\$\$|\$\{[^}]+\}|\`[^`]+\`|\$\([^)]+\)', line):
                            self.findings.append(Finding(
                                rule_id="BASH_PREDICTABLE_TEMP",
                                title="Predictable temp file path",
                                description=f"Using predictable path '/tmp/{filename}' - race condition vulnerability (TOCTOU)",
                                severity=Severity.MEDIUM,
                                file_path=str(self.file_path),
                                line_number=i,
                                code_snippet=line.strip(),
                                remediation="Use mktemp: TEMPFILE=$(mktemp /tmp/XXXXXX)",
                                cwe_id="CWE-377",
                            ))
            
            # Check for temp file without cleanup
            if '/tmp/' in line and 'rm' not in line:
                # Track if this is a creation without deletion
                pass  # Complex to detect without multi-pass analysis
    
    def _check_command_substitution(self):
        """Check for dangerous command substitution."""
        for i, line in enumerate(self.lines, 1):
            # Check for backtick command substitution (deprecated)
            if '`' in line and '$(' not in line:
                self.findings.append(Finding(
                    rule_id="BASH_BACKTICK_DEPRECATED",
                    title="Deprecated backtick command substitution",
                    description="Backticks are deprecated; use $() instead for clarity and nesting",
                    severity=Severity.INFO,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Replace `command` with $(command)",
                ))
            
            # Check for nested command substitution that might be confusing
            nested = re.findall(r'\$\([^)]*\$\([^)]*\)', line)
            if nested:
                self.findings.append(Finding(
                    rule_id="BASH_NESTED_COMMAND_SUB",
                    title="Nested command substitution",
                    description="Deeply nested command substitution can be hard to audit",
                    severity=Severity.LOW,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                ))
    
    def _check_exported_functions(self):
        """Check for exported functions that could be exploited."""
        for i, line in enumerate(self.lines, 1):
            # Check for export -f (function export)
            if re.search(r'export\s+-f\s+\w+', line):
                func_match = re.search(r'export\s+-f\s+(\w+)', line)
                if func_match:
                    func_name = func_match.group(1)
                    self.findings.append(Finding(
                        rule_id="BASH_EXPORTED_FUNCTION",
                        title=f"Exported function: {func_name}",
                        description=f"Function '{func_name}' is exported and can affect child processes",
                        severity=Severity.LOW,
                        file_path=str(self.file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        remediation="Only export functions when necessary; verify child process security",
                    ))
            
            # Check for function definitions that override builtins
            builtin_override = re.search(r'(function\s+)?(cd|echo|test|\[|source|\.)\s*\(\)', line)
            if builtin_override:
                func_name = builtin_override.group(2)
                self.findings.append(Finding(
                    rule_id="BASH_BUILTIN_OVERRIDE",
                    title=f"Function overrides builtin: {func_name}",
                    description=f"Function '{func_name}' overrides a shell builtin - possible confusion attack",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Use different function name to avoid confusion",
                ))
    
    def _check_aliases(self):
        """Check for alias definitions that could be malicious."""
        for i, line in enumerate(self.lines, 1):
            alias_match = re.search(r'alias\s+(\w+)=', line)
            if alias_match:
                alias_name = alias_match.group(1)
                # Check if aliasing dangerous commands
                if alias_name in ['sudo', 'su', 'ssh', 'scp', 'curl', 'wget']:
                    self.findings.append(Finding(
                        rule_id=f"BASH_ALIAS_{alias_name.upper()}",
                        title=f"Alias overrides {alias_name}",
                        description=f"Alias '{alias_name}' may intercept and modify command behavior",
                        severity=Severity.MEDIUM,
                        file_path=str(self.file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        remediation="Avoid aliasing security-sensitive commands",
                    ))
    
    def _check_source_injection(self):
        """Check for source/command injection vulnerabilities."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for source with variable
            source_match = re.search(r'(?:source|\.)\s+["\']?\$\w+', line)
            if source_match:
                self.findings.append(Finding(
                    rule_id="BASH_SOURCE_VARIABLE",
                    title="Source with variable path",
                    description="Sourcing file from variable path - injection risk if variable is user-controlled",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Validate source path before sourcing; use absolute paths",
                    cwe_id="CWE-78",
                ))
            
            # Check for eval with variable
            if re.search(r'\beval\s+["\']?\$', line):
                self.findings.append(Finding(
                    rule_id="BASH_EVAL_VARIABLE",
                    title="eval with variable",
                    description="eval with variable content - arbitrary code execution risk",
                    severity=Severity.CRITICAL,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Avoid eval; use functions or case statements",
                    cwe_id="CWE-95",
                ))
    
    def _check_environment_manipulation(self):
        """Check for suspicious environment variable manipulation."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for PATH manipulation
            path_match = re.search(r'PATH\s*[=:]', line)
            if path_match:
                # Check if adding relative directories
                if re.search(r'PATH.*[=:].*\.:', line) or re.search(r'PATH.*[=:].*["\']\.["\']', line):
                    self.findings.append(Finding(
                        rule_id="BASH_PATH_RELATIVE",
                        title="PATH includes current directory",
                        description="PATH includes '.' or relative directories - command hijacking risk",
                        severity=Severity.CRITICAL,
                        file_path=str(self.file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                        remediation="Never include '.' in PATH; use absolute paths only",
                        cwe_id="CWE-426",
                    ))
                else:
                    self.findings.append(Finding(
                        rule_id="BASH_PATH_MODIFIED",
                        title="PATH environment modified",
                        description="Script modifies PATH - ensure only trusted directories are added",
                        severity=Severity.LOW,
                        file_path=str(self.file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                    ))
            
            # Check for LD_PRELOAD
            if 'LD_PRELOAD' in line:
                self.findings.append(Finding(
                    rule_id="BASH_LD_PRELOAD",
                    title="LD_PRELOAD manipulation",
                    description="LD_PRELOAD can inject malicious shared libraries into processes",
                    severity=Severity.CRITICAL,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Avoid LD_PRELOAD unless absolutely necessary; validate library paths",
                    cwe_id="CWE-114",
                ))
    
    def _check_network_connections(self):
        """Check for network connection attempts."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Check for nc/ncat
            nc_match = re.search(r'\b(nc|ncat|netcat)\s+', line)
            if nc_match:
                cmd = nc_match.group(1)
                self.findings.append(Finding(
                    rule_id="BASH_NETCAT",
                    title=f"{cmd} network connection",
                    description=f"{cmd} can create network connections or backdoors",
                    severity=Severity.MEDIUM,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                ))
            
            # Check for /dev/tcp (bash built-in)
            if '/dev/tcp/' in line:
                self.findings.append(Finding(
                    rule_id="BASH_DEV_TCP",
                    title="Bash /dev/tcp connection",
                    description="Using bash's /dev/tcp feature for network connections",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                ))
            
            # Check for ssh with options that bypass security
            if re.search(r'ssh\s+.*-[oO]\s*StrictHostKeyChecking\s*=\s*no', line):
                self.findings.append(Finding(
                    rule_id="BASH_SSH_NO_VERIFY",
                    title="SSH host key verification disabled",
                    description="SSH connection without host key verification - MITM risk",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Do not disable StrictHostKeyChecking",
                ))
    
    def _check_backdoor_indicators(self):
        """Check for potential backdoor patterns."""
        # Check for cron job installation
        for i, line in enumerate(self.lines, 1):
            if 'crontab' in line or '/etc/cron' in line:
                self.findings.append(Finding(
                    rule_id="BASH_CRON_INSTALL",
                    title="Cron job installation",
                    description="Script installs cron job - persistent execution mechanism",
                    severity=Severity.MEDIUM,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Verify cron job is legitimate and from trusted source",
                ))
            
            # Check for SSH key installation
            if '.ssh/authorized_keys' in line:
                self.findings.append(Finding(
                    rule_id="BASH_SSH_KEY_INSTALL",
                    title="SSH authorized_keys modification",
                    description="Script modifies SSH authorized_keys - potential backdoor",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Verify any SSH key additions are intentional and authorized",
                ))
            
            # Check for systemd service installation
            if '/etc/systemd/system' in line or 'systemctl enable' in line:
                self.findings.append(Finding(
                    rule_id="BASH_SYSTEMD_INSTALL",
                    title="Systemd service installation",
                    description="Script installs systemd service - persistent execution mechanism",
                    severity=Severity.MEDIUM,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                ))
            
            # Check for startup file modification
            startup_files = ['.bashrc', '.bash_profile', '.zshrc', '.profile']
            for startup in startup_files:
                if startup in line:
                    self.findings.append(Finding(
                        rule_id=f"BASH_STARTUP_{startup.upper().replace('.', '_')}",
                        title=f"Shell startup file modification: {startup}",
                        description=f"Script modifies {startup} - persistent execution mechanism",
                        severity=Severity.MEDIUM,
                        file_path=str(self.file_path),
                        line_number=i,
                        code_snippet=line.strip(),
                    ))
            
            # Check for setuid/setgid
            if re.search(r'chmod\s+.*[47]\d{3}', line) or 'u+s' in line or 'g+s' in line:
                self.findings.append(Finding(
                    rule_id="BASH_SETUID",
                    title="setuid/setgid bit set",
                    description="Setting setuid/setgid bits can create privilege escalation vulnerabilities",
                    severity=Severity.HIGH,
                    file_path=str(self.file_path),
                    line_number=i,
                    code_snippet=line.strip(),
                    remediation="Avoid setuid/setgid; use proper privilege separation",
                    cwe_id="CWE-250",
                ))
    
    def _get_line_snippet(self, line_num: int) -> str:
        """Get a snippet of code around a line."""
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()[:100]
        return ""
