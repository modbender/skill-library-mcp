"""Enhanced Python AST-based analyzer with AI security patterns."""

import ast
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from crabukit.rules.patterns import (
    Finding, Severity,
    PYTHON_DANGEROUS_CALLS,
    PYTHON_SUBPROCESS_PATTERNS,
    PYTHON_NETWORK_PATTERNS,
    PYTHON_FILE_PATTERNS,
    PYTHON_OBFUSCATION_PATTERNS,
    SECRET_PATTERNS,
    AI_MALWARE_PATTERNS,
)


class PythonAnalyzer:
    """Analyze Python scripts for security issues with AI-aware detection."""
    
    def __init__(self, content: str, ast_tree: Optional[ast.AST], file_path: Path):
        self.content = content
        self.ast_tree = ast_tree
        self.file_path = file_path
        self.findings: List[Finding] = []
        self.lines = content.split('\n')
        self.has_user_input_flow = False
        
    def analyze(self) -> List[Finding]:
        """Run all Python analyses."""
        self.findings = []
        
        if self.ast_tree:
            self._analyze_ast()
            self._analyze_data_flow()
        
        # Text-based patterns
        self._analyze_text_patterns()
        self._analyze_obfuscation()
        self._analyze_ai_malware_patterns()
        
        return self.findings
    
    def _analyze_ast(self):
        """Walk the AST looking for dangerous patterns."""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Call):
                self._check_dangerous_call(node)
                self._check_subprocess_call(node)
                self._check_network_calls(node)
                self._check_file_calls(node)
                self._check_obfuscation_calls(node)
    
    def _check_dangerous_call(self, node: ast.Call):
        """Check for dangerous function calls."""
        func_name = self._get_call_name(node)
        
        if func_name in PYTHON_DANGEROUS_CALLS:
            rule = PYTHON_DANGEROUS_CALLS[func_name]
            line_num = getattr(node, 'lineno', 0)
            
            # Check if has arguments (user input concern)
            has_args = bool(node.args) or bool(node.keywords)
            
            if has_args:
                self.findings.append(Finding(
                    rule_id=f"PY_DANGEROUS_{func_name.upper()}",
                    title=rule["title"],
                    description=rule["description"],
                    severity=rule["severity"],
                    file_path=str(self.file_path),
                    line_number=line_num,
                    code_snippet=self._get_line_snippet(line_num),
                    remediation=rule.get("remediation"),
                    cwe_id=rule.get("cwe"),
                ))
    
    def _check_subprocess_call(self, node: ast.Call):
        """Check for subprocess calls with shell=True."""
        func_name = self._get_call_name(node)
        
        is_subprocess = False
        base_name = func_name.split('.')[-1] if '.' in func_name else func_name
        
        if func_name in PYTHON_SUBPROCESS_PATTERNS or \
           any(func_name.endswith(f'.{cmd}') for cmd in ['call', 'run', 'Popen', 'check_output', 'check_call']):
            is_subprocess = True
        
        if not is_subprocess and not func_name.startswith(('os.', 'subprocess.')):
            return
        
        line_num = getattr(node, 'lineno', 0)
        
        # Check for shell=True
        shell_true = False
        for keyword in node.keywords:
            if keyword.arg == 'shell':
                if isinstance(keyword.value, ast.Constant) and keyword.value.value == True:
                    shell_true = True
                elif isinstance(keyword.value, ast.NameConstant) and keyword.value.value == True:
                    shell_true = True
        
        if shell_true or func_name in ['os.system', 'os.popen']:
            self.findings.append(Finding(
                rule_id="PY_SUBPROCESS_SHELL",
                title="Subprocess with shell=True",
                description=f"{func_name}() uses shell=True which can lead to shell injection if user input is included",
                severity=Severity.CRITICAL,
                file_path=str(self.file_path),
                line_number=line_num,
                code_snippet=self._get_line_snippet(line_num),
                remediation="Use shell=False and pass arguments as a list; properly escape all inputs",
                cwe_id="CWE-78",
            ))
        elif is_subprocess:
            # Check if using string (shell-like) vs list
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                if ' ' in node.args[0].value and not shell_true:
                    self.findings.append(Finding(
                        rule_id="PY_SUBPROCESS_STRING",
                        title="Subprocess with string command",
                        description=f"{func_name}() uses string command that will be parsed by shell",
                        severity=Severity.MEDIUM,
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=self._get_line_snippet(line_num),
                        remediation="Pass command as list to avoid shell interpretation",
                    ))
            
            self.findings.append(Finding(
                rule_id="PY_SUBPROCESS",
                title="Subprocess execution",
                description=f"{func_name}() executes external commands - ensure inputs are validated",
                severity=Severity.MEDIUM,
                file_path=str(self.file_path),
                line_number=line_num,
                code_snippet=self._get_line_snippet(line_num),
            ))
    
    def _check_network_calls(self, node: ast.Call):
        """Check for network-related calls."""
        func_name = self._get_call_name(node)
        
        for pattern, info in PYTHON_NETWORK_PATTERNS.items():
            if func_name == pattern or func_name.endswith(f'.{pattern.split(".")[-1]}'):
                line_num = getattr(node, 'lineno', 0)
                self.findings.append(Finding(
                    rule_id=f"PY_NETWORK_{pattern.replace('.', '_').upper()}",
                    title=info["title"],
                    description=f"{info['title']} detected - ensure destination is trusted",
                    severity=info["severity"],
                    file_path=str(self.file_path),
                    line_number=line_num,
                    code_snippet=self._get_line_snippet(line_num),
                ))
    
    def _check_file_calls(self, node: ast.Call):
        """Check for file operations."""
        func_name = self._get_call_name(node)
        
        for pattern, info in PYTHON_FILE_PATTERNS.items():
            if func_name == pattern or func_name.endswith(f'.{pattern.split(".")[-1]}'):
                line_num = getattr(node, 'lineno', 0)
                snippet = self._get_line_snippet(line_num)
                
                # Check for path traversal
                if self._has_path_traversal(node):
                    self.findings.append(Finding(
                        rule_id="PY_PATH_TRAVERSAL",
                        title="Potential path traversal",
                        description="File operation may allow path traversal (../)",
                        severity=Severity.HIGH,
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=snippet,
                        remediation="Validate and sanitize file paths; use pathlib.Path.resolve()",
                        cwe_id="CWE-22",
                    ))
                else:
                    self.findings.append(Finding(
                        rule_id=f"PY_FILE_{pattern.replace('.', '_').upper()}",
                        title=info["title"],
                        description=f"{info['title']} detected",
                        severity=info["severity"],
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=snippet,
                    ))
    
    def _check_obfuscation_calls(self, node: ast.Call):
        """Check for obfuscation-related calls."""
        func_name = self._get_call_name(node)
        
        for pattern, info in PYTHON_OBFUSCATION_PATTERNS.items():
            if func_name == pattern or func_name.endswith(f'.{pattern.split(".")[-1]}'):
                line_num = getattr(node, 'lineno', 0)
                
                # Check if it's followed by execution
                if self._is_obfuscation_before_exec(line_num):
                    self.findings.append(Finding(
                        rule_id=f"PY_OBFUSCATION_EXEC_{pattern.replace('.', '_').upper()}",
                        title=f"{info['title']} followed by execution",
                        description=f"{info['title']} immediately followed by code execution - possible evasion",
                        severity=Severity.CRITICAL,
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=self._get_line_snippet(line_num),
                        remediation="Never execute decoded/decompressed content without inspection",
                        cwe_id="CWE-94",
                    ))
                else:
                    self.findings.append(Finding(
                        rule_id=f"PY_OBFUSCATION_{pattern.replace('.', '_').upper()}",
                        title=info["title"],
                        description=info["title"],
                        severity=info["severity"],
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=self._get_line_snippet(line_num),
                    ))
    
    def _analyze_data_flow(self):
        """Analyze data flow from user input to dangerous functions."""
        if not self.ast_tree:
            return
        
        # Find user input sources
        input_sources = set()
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in ['input', 'sys.stdin.read', 'socket.recv']:
                    # Track where this data flows
                    input_sources.add(node)
        
        # Check if user input reaches dangerous functions
        if input_sources:
            self.has_user_input_flow = True
            # This is a simplified check - full taint analysis would be more complex
    
    def _analyze_text_patterns(self):
        """Analyze raw text for patterns (secrets, etc.)."""
        for rule_id, rule in SECRET_PATTERNS.items():
            matches = list(re.finditer(rule["pattern"], self.content, re.IGNORECASE))
            
            for match in matches:
                line_num = self.content[:match.start()].count('\n') + 1
                
                # Avoid duplicate findings on same line
                if any(f.line_number == line_num and 'SECRET_' in f.rule_id for f in self.findings):
                    continue
                
                # Skip if it looks like a placeholder
                if self._is_placeholder(match.group(0)):
                    continue
                
                self.findings.append(Finding(
                    rule_id=f"SECRET_{rule_id.upper()}",
                    title=rule["title"],
                    description=rule["description"],
                    severity=rule["severity"],
                    file_path=str(self.file_path),
                    line_number=line_num,
                    code_snippet=self._mask_secret(match.group(0)),
                    cwe_id=rule.get("cwe"),
                ))
    
    def _analyze_obfuscation(self):
        """Check for code obfuscation techniques."""
        # Check for hex-encoded strings that decode to executable code
        hex_strings = re.findall(r"['\"]([0-9a-fA-F]{40,})['\"]", self.content)
        for hex_str in hex_strings[:3]:  # Limit to first 3
            try:
                decoded = bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
                if any(keyword in decoded for keyword in ['import', 'exec', 'eval', 'os.', 'subprocess']):
                    line_num = self.content.find(hex_str)
                    line_num = self.content[:line_num].count('\n') + 1
                    self.findings.append(Finding(
                        rule_id="PY_OBFUSCATION_HEX_CODE",
                        title="Hex-encoded executable code",
                        description="Contains hex string that decodes to code-like content",
                        severity=Severity.HIGH,
                        file_path=str(self.file_path),
                        line_number=line_num,
                        code_snippet=hex_str[:50] + "...",
                        remediation="Do not encode executable code in hex strings",
                    ))
            except:
                pass
        
        # Check for excessive string concatenation (obfuscation)
        concat_pattern = r"['\"]\w+['\"]\s*\+\s*['\"]\w+['\"]"
        if len(re.findall(concat_pattern, self.content)) > 10:
            self.findings.append(Finding(
                rule_id="PY_OBFUSCATION_CONCAT",
                title="Excessive string concatenation",
                description="Multiple string concatenations - possible obfuscation",
                severity=Severity.LOW,
                file_path=str(self.file_path),
                line_number=1,
            ))
    
    def _analyze_ai_malware_patterns(self):
        """Check for AI-enabled malware patterns (PROMPTFLUX-style)."""
        for rule_id, rule in AI_MALWARE_PATTERNS.items():
            matches = list(re.finditer(rule["pattern"], self.content, re.IGNORECASE))
            
            for match in matches:
                line_num = self.content[:match.start()].count('\n') + 1
                
                self.findings.append(Finding(
                    rule_id=f"AI_MALWARE_{rule_id.upper()}",
                    title=rule["title"],
                    description=rule["description"],
                    severity=rule["severity"],
                    file_path=str(self.file_path),
                    line_number=line_num,
                    code_snippet=self._get_line_snippet(line_num),
                ))
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Get the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return "<unknown>"
    
    def _get_line_snippet(self, line_num: int) -> str:
        """Get a snippet of code around a line."""
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()[:100]
        return ""
    
    def _mask_secret(self, text: str) -> str:
        """Mask a secret in the output."""
        if len(text) > 20:
            return text[:8] + "***" + text[-4:]
        return "***"
    
    def _is_placeholder(self, text: str) -> bool:
        """Check if a secret is likely a placeholder."""
        placeholders = ['example', 'placeholder', 'your_key', 'xxx', 'xxx', 'changeme', 'test']
        return any(p in text.lower() for p in placeholders)
    
    def _has_path_traversal(self, node: ast.Call) -> bool:
        """Check if a file operation may have path traversal."""
        # Simplified check - look for string concatenation or formatting
        for arg in node.args:
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                return True
            if isinstance(arg, ast.Call):
                func_name = self._get_call_name(arg)
                if 'format' in func_name or 'join' in func_name:
                    return True
        return False
    
    def _is_obfuscation_before_exec(self, line_num: int) -> bool:
        """Check if obfuscation is followed by execution."""
        if line_num >= len(self.lines):
            return False
        
        # Check next few lines for execution
        for i in range(line_num, min(line_num + 5, len(self.lines))):
            line = self.lines[i].lower()
            if any(keyword in line for keyword in ['exec', 'eval', 'compile', 'exec(']):
                return True
        return False
