"""Core static analyzer – safe for humans and agents alike (zero deps, no execution)
"""
import ast
import re
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Threat:
    severity: str  # "critical", "warning", "info"
    title: str
    description: str
    file: str = None
    line: int = None

def analyze_file(filepath: str) -> List[Threat]:
    threats = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return [Threat(severity="warning", title="File read error", description=str(e), file=filepath)]

    threats.extend(_scan_secrets(code, filepath))
    threats.extend(_scan_dangerous_imports(code, filepath))
    threats.extend(_scan_dangerous_calls(code, filepath))
    threats.extend(_scan_obfuscation(code, filepath))
    return threats

def _scan_secrets(code: str, file: str) -> List[Threat]:
    patterns = {
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "Generic API Key": r"(?i)(api_key|apikey|secret|token).{0,30}['\"][a-z0-9]{32,45}['\"]",
        "Private Key": r"-----BEGIN (RSA )?PRIVATE KEY-----",
        "Hardcoded IP": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b(?!\s*\/)"
    }
    threats = []
    for name, pattern in patterns.items():
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            threats.append(Threat(severity="critical", title=f"Hardcoded {name}", description=f"{match.group()[:30]}...", file=file, line=line_num))
    return threats

def _scan_dangerous_imports(code: str, file: str) -> List[Threat]:
    threats = []
    dangerous = {'os': "Direct OS access", 'subprocess': "Process execution", 'socket': "Network access", 'ctypes': "Low-level memory"}
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous:
                        threats.append(Threat(severity="warning", title=f"Risky import: {alias.name}", description=dangerous[alias.name], file=file, line=node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module in dangerous:
                    threats.append(Threat(severity="warning", title=f"Risky import: {node.module}", description=dangerous.get(node.module, "Potential risk"), file=file, line=node.lineno))
    except SyntaxError:
        threats.append(Threat(severity="warning", title="Syntax error", description="Possible obfuscation", file=file))
    return threats

def _scan_dangerous_calls(code: str, file: str) -> List[Threat]:
    threats = []
    dangerous_funcs = ['eval', 'exec', 'compile', 'open', 'input']
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in dangerous_funcs:
                sev = "critical" if node.func.id in ['eval', 'exec'] else "warning"
                threats.append(Threat(severity=sev, title=f"Dangerous call: {node.func.id}()", description="Arbitrary execution or sensitive access", file=file, line=node.lineno))
    except:
        pass
    return threats

def _scan_obfuscation(code: str, file: str) -> List[Threat]:
    threats = []
    base64_pattern = r'["\']([A-Za-z0-9+/]{50,}={0,2})["\']'
    for match in re.finditer(base64_pattern, code):
        line_num = code[:match.start()].count('\n') + 1
        threats.append(Threat(severity="warning", title="Potential obfuscation", description=f"Large base64: {match.group(1)[:30]}...", file=file, line=line_num))
    return threats

def calculate_risk_score(threats: List[Threat]) -> float:
    score = 10.0
    for t in threats:
        if t.severity == "critical": score -= 3.0
        elif t.severity == "warning": score -= 1.5
        else: score -= 0.5
    return max(0.0, score)
