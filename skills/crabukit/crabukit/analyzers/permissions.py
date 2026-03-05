"""Enhanced permission and metadata analyzer with tool combination detection."""

import re
from typing import List, Dict, Any, Set
from pathlib import Path

from crabukit.rules.patterns import (
    Finding, Severity,
    PERMISSION_CHECKS,
    DANGEROUS_TOOL_COMBINATIONS,
    TOOL_RISK_LEVELS,
)
from crabukit.parsers.skill_md import SkillMetadata


class PermissionAnalyzer:
    """Analyze skill permissions and metadata with combination detection."""
    
    # High-risk operations that should have safety guidance
    SAFETY_SENSITIVE_KEYWORDS = [
        'delete', 'remove', 'drop', 'destroy', 'clean', 'truncate',
        'overwrite', 'format', 'reset', 'restart', 'reboot',
        'kill', 'terminate', 'stop', 'disable', 'uninstall',
    ]
    
    def __init__(self, metadata: SkillMetadata, skill_path: Path):
        self.metadata = metadata
        self.skill_path = skill_path
        self.findings: List[Finding] = []
        
    def analyze(self) -> List[Finding]:
        """Analyze permissions and metadata."""
        self.findings = []
        
        self._check_allowed_tools()
        self._check_tool_combinations()
        self._check_description_quality()
        self._check_script_permissions()
        self._check_safety_guidance()
        self._check_typosquatting()
        
        return self.findings
    
    def _check_allowed_tools(self):
        """Check for potentially dangerous tool permissions."""
        for tool in self.metadata.allowed_tools:
            if tool in TOOL_RISK_LEVELS:
                tool_info = TOOL_RISK_LEVELS[tool]
                self.findings.append(Finding(
                    rule_id=f"PERM_SENSITIVE_TOOL_{tool.upper()}",
                    title=f"Skill requests '{tool}' tool",
                    description=f"This skill requests access to the '{tool}' tool which can {tool_info['description']}",
                    severity=tool_info["severity"],
                    file_path=str(self.metadata.file_path),
                    line_number=1,
                    code_snippet=f"allowed-tools: {tool}",
                ))
        
        # Check for exec without safety guidance
        if 'exec' in self.metadata.allowed_tools:
            content_lower = self.metadata.content.lower()
            has_safety_warning = any(phrase in content_lower for phrase in [
                'ask before', 'prompt before', 'confirm before',
                'be careful', 'caution', 'warning', 'dangerous',
                'destructive', 'irreversible', 'cannot be undone',
            ])
            
            if not has_safety_warning:
                self.findings.append(Finding(
                    rule_id="PERM_EXEC_NO_SAFETY",
                    title="exec permission without safety guidance",
                    description="Skill requests exec tool but doesn't mention safety precautions in instructions. This violates the Confused Deputy protection principle.",
                    severity=Severity.MEDIUM,
                    file_path=str(self.metadata.file_path),
                    line_number=1,
                    remediation="Add warnings about destructive operations and confirmation requirements",
                ))
    
    def _check_tool_combinations(self):
        """Check for dangerous tool combinations."""
        tools_set = set(self.metadata.allowed_tools)
        
        # Check predefined dangerous combinations
        for combo in DANGEROUS_TOOL_COMBINATIONS:
            if combo.issubset(tools_set):
                combo_list = sorted(combo)
                self.findings.append(Finding(
                    rule_id=f"PERM_DANGEROUS_COMBO_{'_'.join(combo_list).upper()}",
                    title=f"Dangerous tool combination: {', '.join(combo_list)}",
                    description=f"Combination of {', '.join(combo_list)} enables download-and-execute or reconfigure-and-execute attack chains",
                    severity=Severity.CRITICAL,
                    file_path=str(self.metadata.file_path),
                    line_number=1,
                    code_snippet=f"allowed-tools: {', '.join(self.metadata.allowed_tools)}",
                    remediation="Remove unnecessary tools; implement confirmation for sensitive operations",
                ))
        
        # Check for network + execution (classic download & execute)
        network_tools = {'browser', 'web_search', 'web_fetch', 'curl', 'wget'}
        execution_tools = {'exec', 'process', 'nodes'}
        
        has_network = bool(network_tools & tools_set)
        has_execution = bool(execution_tools & tools_set)
        
        if has_network and has_execution:
            self.findings.append(Finding(
                rule_id="PERM_NETWORK_EXEC_COMBO",
                title="Network + Execution tool combination",
                description="Skill has both network access and execution capabilities - potential download-and-execute attack vector",
                severity=Severity.HIGH,
                file_path=str(self.metadata.file_path),
                line_number=1,
                code_snippet=f"allowed-tools: {', '.join(self.metadata.allowed_tools)}",
                remediation="Implement strict input validation; use ask mode for execution",
            ))
        
        # Check for gateway + anything (very powerful)
        if 'gateway' in tools_set:
            self.findings.append(Finding(
                rule_id="PERM_GATEWAY_WARNING",
                title="Gateway tool grants system-level control",
                description="gateway tool can restart and reconfigure the Clawdbot daemon - highest privilege level",
                severity=Severity.CRITICAL,
                file_path=str(self.metadata.file_path),
                line_number=1,
                remediation="Ensure this is absolutely necessary; implement strict access controls",
            ))
        
        # Check for many tools (principle of least privilege violation)
        if len(self.metadata.allowed_tools) > 5:
            self.findings.append(Finding(
                rule_id="PERM_TOO_MANY_TOOLS",
                title="Many tools requested",
                description=f"Skill requests {len(self.metadata.allowed_tools)} tools - violates principle of least privilege",
                severity=Severity.LOW,
                file_path=str(self.metadata.file_path),
                line_number=1,
                remediation="Remove unnecessary tools; only request what is essential",
            ))
    
    def _check_description_quality(self):
        """Check description for quality and potential issues."""
        desc = self.metadata.description
        
        if not desc:
            self.findings.append(Finding(
                rule_id="META_NO_DESCRIPTION",
                title="Missing description",
                description="Skill has no description - cannot assess intent",
                severity=Severity.MEDIUM,
                file_path=str(self.metadata.file_path),
                line_number=1,
            ))
            return
        
        # Length checks
        if len(desc) < 50:
            self.findings.append(Finding(
                rule_id="META_SHORT_DESC",
                title="Short skill description",
                description=f"Description is only {len(desc)} characters - should be more detailed for security review",
                severity=Severity.INFO,
                file_path=str(self.metadata.file_path),
                line_number=1,
            ))
        
        if len(desc) > 500:
            self.findings.append(Finding(
                rule_id="META_LONG_DESC",
                title="Very long skill description",
                description=f"Description is {len(desc)} characters - unusually long, possible obfuscation",
                severity=Severity.INFO,
                file_path=str(self.metadata.file_path),
                line_number=1,
            ))
        
        # Check for URLs in description
        import re
        urls = re.findall(r'https?://[^\s<>"\']+', desc)
        for url in urls:
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']
            if any(url.endswith(tld) for tld in suspicious_tlds):
                self.findings.append(Finding(
                    rule_id="META_SUSPICIOUS_URL",
                    title="Suspicious URL in description",
                    description=f"Description contains URL with suspicious TLD: {url}",
                    severity=Severity.MEDIUM,
                    file_path=str(self.metadata.file_path),
                    line_number=1,
                    code_snippet=url,
                ))
    
    def _check_script_permissions(self):
        """Check for executable scripts with concerning permissions."""
        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            return
        
        import stat
        
        for script in scripts_dir.rglob("*"):
            if not script.is_file():
                continue
            
            try:
                mode = script.stat().st_mode
                is_executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
                
                if is_executable and script.suffix in ['.py', '.sh']:
                    # Check if it has a shebang
                    try:
                        with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                            first_line = f.readline().strip() if script.stat().st_size < 100000 else ""
                        
                        if not first_line.startswith('#!'):
                            self.findings.append(Finding(
                                rule_id="PERM_EXEC_NO_SHEBANG",
                                title="Executable script without shebang",
                                description=f"{script.name} is executable but lacks a proper shebang line",
                                severity=Severity.INFO,
                                file_path=str(script),
                                line_number=1,
                            ))
                        
                        # Check if world-writable
                        if mode & stat.S_IWOTH:
                            self.findings.append(Finding(
                                rule_id="PERM_WORLD_WRITABLE",
                                title="World-writable executable",
                                description=f"{script.name} is world-writable - any user can modify it",
                                severity=Severity.HIGH,
                                file_path=str(script),
                                line_number=1,
                                remediation="Remove world write permission: chmod o-w",
                                cwe_id="CWE-732",
                            ))
                    except (IOError, UnicodeDecodeError):
                        pass
            except (OSError, IOError):
                continue
    
    def _check_safety_guidance(self):
        """Check if skill provides appropriate safety guidance."""
        content_lower = self.metadata.content.lower()
        
        # Check for destructive keywords without safety warnings
        for keyword in self.SAFETY_SENSITIVE_KEYWORDS:
            if keyword in content_lower:
                # Check if there's a warning near it
                # Simple check: is there a warning keyword anywhere?
                safety_keywords = ['warning', 'caution', 'careful', 'destructive', 'irreversible', 'confirm']
                has_safety = any(s in content_lower for s in safety_keywords)
                
                if not has_safety:
                    self.findings.append(Finding(
                        rule_id=f"SAFETY_NO_WARNING_{keyword.upper()}",
                        title=f"Destructive operation without warning: '{keyword}'",
                        description=f"Skill mentions '{keyword}' but doesn't provide safety warnings",
                        severity=Severity.MEDIUM,
                        file_path=str(self.metadata.file_path),
                        line_number=1,
                        remediation=f"Add warning about {keyword} being destructive/irreversible",
                    ))
                break  # Only report once
    
    def _check_typosquatting(self):
        """Check if skill name might be typosquatting a popular skill."""
        skill_name = self.metadata.name.lower()
        
        # Common typosquatting patterns
        typosquat_patterns = [
            (r'^(\w+)s$', "singular vs plural"),  # requests vs request
            (r'^(\w+)ing$', "verb form"),  # running vs run
            (r'^(\w+)ed$', "past tense"),  # started vs start
            (r'^(\w+)-core$', "core variant"),  # lodash-core vs lodash
            (r'^(\w+)-utils$', "utils variant"),
        ]
        
        # Check for homoglyphs (similar-looking characters)
        homoglyphs = {
            'a': ['а', 'ɑ', 'α'],  # Cyrillic а, Latin ɑ, Greek α
            'e': ['е', 'ε', 'ɛ'],  # Cyrillic е, Greek ε
            'o': ['о', 'ο', 'σ'],  # Cyrillic о, Greek ο
            'p': ['р', 'ρ'],       # Cyrillic р, Greek ρ
            'c': ['с', 'ϲ'],       # Cyrillic с
            'x': ['х', 'χ'],       # Cyrillic х
            'y': ['у', 'γ'],       # Cyrillic у
        }
        
        for char, variants in homoglyphs.items():
            for variant in variants:
                if variant in skill_name:
                    self.findings.append(Finding(
                        rule_id="TYPO_HOMOGLYPH",
                        title="Potential homoglyph attack",
                        description=f"Skill name contains character '{variant}' that looks like '{char}' - possible typosquatting",
                        severity=Severity.HIGH,
                        file_path=str(self.metadata.file_path),
                        line_number=1,
                        remediation="Use ASCII characters only in skill names",
                    ))
        
        # Check for excessive repeated characters (e.g., lodash vs loodash)
        if re.search(r'(.)\1{2,}', skill_name):
            self.findings.append(Finding(
                rule_id="TYPO_REPEATED_CHARS",
                title="Repeated characters in name",
                description="Skill name has repeated characters - possible typosquatting",
                severity=Severity.LOW,
                file_path=str(self.metadata.file_path),
                line_number=1,
            ))
