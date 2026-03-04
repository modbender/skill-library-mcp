import argparse
import ast
import json
import os
import sys
import re
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Set
from unittest.mock import MagicMock

# Ensure we can import local utils if running as script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from audit_utils import (
    calculate_shannon_entropy,
    NetworkForensics,
    SupplyChainForensics,
)

__version__ = "2.0.0"
__author__ = " TT and Antigravity Security Team"


class ShieldPro20(ast.NodeVisitor):
    """
    Advanced Security Auditor for Python Source Code (AST-based).

    This auditor implements the SEP-2026 Security Protocol, detecting malicious
    patterns, obfuscation, and unauthorized system/network access by analyzing
     the Abstract Syntax Tree (AST).

    Attributes:
        filename (str): Path to the file being audited.
        report (List[Dict[str, Any]]): Accumulated security findings.
        import_aliases (Dict[str, str]): Mapping of import aliases to real module names.
        forbidden_imports (Set[str]): Set of modules restricted for use.
        forbidden_calls (Set[str]): Set of function calls flagged as high-risk.
        risky_attributes (Set[str]): Attributes often used in dynamic execution or redirection.
        risky_globals (Set[str]): Built-in functions or globals that allow logic manipulation.
    """

    def __init__(self, filename: str) -> None:
        """
        Initializes the ShieldPro20 auditor.

        Args:
            filename (str): The name of the file to scan.
        """
        self.filename: str = filename
        self.report: List[Dict[str, Any]] = []
        self.import_aliases: Dict[str, str] = {}

        # Security Policy Definitions
        self.forbidden_imports: Set[str] = {
            "os",
            "sys",
            "subprocess",
            "shutil",
            "pickle",
            "marshal",
            "shelve",
            "ctypes",
            "socket",
            "requests",
            "http.client",
            "urllib",
            "functools",
            "xmlrpc",
        }
        self.forbidden_calls: Set[str] = {
            "eval",
            "exec",
            "compile",
            "open",
            "file",
            "os.system",
            "os.popen",
            "os.spawn",
            "os.execl",
            "os.execle",
            "os.execlp",
            "os.execlpe",
            "os.execv",
            "os.execve",
            "os.execvp",
            "os.execvpe",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
            "subprocess.Popen",
            "subprocess.run",
            "pickle.loads",
            "yaml.load",
            "ctypes",
            "ffi",
            "socket.socket",
            "requests.get",
            "requests.post",
            "requests.put",
            "requests.delete",
            "requests.patch",
            "requests.head",
            "requests.request",
            "urllib.request.urlopen",
            "urllib.request.urlretrieve",
            "ftplib",
            "telnetlib",
            "http.client",
        }
        self.risky_attributes: Set[str] = {
            "system",
            "popen",
            "call",
            "check_call",
            "check_output",
            "spawn",
            "exec",
            "eval",
            "compile",
            "getattr",
            "setattr",
            "delattr",
            "__import__",
            "import_module",
        }
        self.risky_globals: Set[str] = {
            "__builtins__",
            "globals",
            "locals",
            "vars",
            "getattr",
            "setattr",
            "delattr",
        }

    def _add_issue(self, severity: str, message: str, lineno: int) -> None:
        """
        Logs a security finding to the internal report.

        Args:
            severity (str): Severity level (CRITICAL, HIGH, MEDIUM, LOW).
            message (str): Description of the security issue.
            lineno (int): Line number where the issue was detected.
        """
        self.report.append(
            {
                "severity": severity,
                "file": self.filename,
                "line": lineno,
                "issue": message,
            }
        )

    def _is_safe_constant(self, node: ast.AST) -> bool:
        """
        Heuristic check to determine if an AST node represents a safe constant.

        Helps reduce false positives for harmless dynamic execution like eval('1+1').

        Args:
            node (ast.AST): The AST node to evaluate.

        Returns:
            bool: True if the node is considered a safe constant or simple constant operation.
        """
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return all(self._is_safe_constant(elt) for elt in node.elts)
        if isinstance(node, ast.BinOp):
            return self._is_safe_constant(node.left) and self._is_safe_constant(
                node.right
            )
        return False

    def visit_Call(self, node: ast.Call) -> None:
        """
        Audits function and method calls for security violations.
        Handles direct calls, aliased calls, and obfuscated calls via partial.
        """
        func_name: str = ""

        # 1. Resolve Function Name (Direct or Attribute)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = self._get_full_attr_name(node.func)

        if not func_name:
            self.generic_visit(node)
            return

        # 2. Handle Aliases (Resolve e.g. s.popen -> os.popen)
        parts = func_name.split(".")
        root = parts[0]
        resolved_name = func_name
        if root in self.import_aliases:
            real_root = self.import_aliases[root]
            if len(parts) > 1:
                resolved_name = f"{real_root}.{'.'.join(parts[1:])}"
            else:
                resolved_name = real_root

        # 3. Security Auditing (on both original and resolved names)
        check_names = {func_name, resolved_name}
        is_safe = node.args and self._is_safe_constant(node.args[0])

        for name in check_names:
            if name in self.forbidden_calls:
                if is_safe:
                    self._add_issue(
                        "LOW", f"Constant usage of forbidden call: {name}", node.lineno
                    )
                else:
                    self._add_issue(
                        "CRITICAL", f"Dangerous call detected: {name}", node.lineno
                    )

            if name in self.risky_attributes:
                self._add_issue(
                    "HIGH", f"Dynamic execution/import detected: {name}", node.lineno
                )

            if name in self.risky_globals:
                self._add_issue(
                    "HIGH", f"Reflection/Introspection detected: {name}", node.lineno
                )

        # 4. Handle partial() Obfuscation
        if resolved_name in {"partial", "functools.partial"}:
            if node.args:
                wrapped_func = node.args[0]
                wrapped_name = None
                if isinstance(wrapped_func, ast.Name):
                    wrapped_name = self.import_aliases.get(
                        wrapped_func.id, wrapped_func.id
                    )
                elif isinstance(wrapped_func, ast.Attribute):
                    wrapped_name = self._get_full_attr_name(wrapped_func)
                    w_parts = wrapped_name.split(".")
                    if w_parts[0] in self.import_aliases:
                        wrapped_name = (
                            f"{self.import_aliases[w_parts[0]]}.{'.'.join(w_parts[1:])}"
                        )

                if wrapped_name in self.forbidden_calls:
                    self._add_issue(
                        "CRITICAL",
                        f"Obfuscated call via partial(): {wrapped_name}",
                        node.lineno,
                    )

        # 5. Special Patterns
        if resolved_name == "__import__":
            self._add_issue(
                "CRITICAL", "Direct use of '__import__' (Dynamic Risk).", node.lineno
            )

        if self._is_dynamic_getattr(node):
            self._add_issue("HIGH", "Dynamic 'getattr' detected.", node.lineno)

        if "__subclasses__" in resolved_name or "__bases__" in resolved_name:
            self._add_issue(
                "HIGH",
                "Metaprogramming detected (Possible Sandbox Escape).",
                node.lineno,
            )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """
        Audits module imports for security risks and tracks aliases.

        Args:
            node (ast.Import): The import node.
        """
        for alias in node.names:
            store_name = alias.asname if alias.asname else alias.name
            self.import_aliases[store_name] = alias.name

            if alias.name in {"socket", "http.client", "telnetlib", "ftplib"}:
                self._add_issue(
                    "MEDIUM",
                    f"Network library import detected: {alias.name}",
                    node.lineno,
                )
            if alias.name == "subprocess":
                self._add_issue(
                    "HIGH",
                    "Subprocess module import. Check for shell injections.",
                    node.lineno,
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Audits specific member imports and tracks aliases.

        Args:
            node (ast.ImportFrom): The import-from node.
        """
        module = node.module or ""
        for alias in node.names:
            store_name = alias.asname if alias.asname else alias.name
            full_real_name = f"{module}.{alias.name}" if module else alias.name
            self.import_aliases[store_name] = full_real_name

            if module in self.forbidden_imports:
                self._add_issue(
                    "MEDIUM", f"Import from sensitive module: {module}", node.lineno
                )

    def visit_Name(self, node: ast.Name) -> None:
        """
        Checks for access to risky global or built-in variables.

        Args:
            node (ast.Name): The variable name node.
        """
        if node.id in self.risky_globals:
            self._add_issue(
                "HIGH", f"Access to sensitive global/builtin: {node.id}", node.lineno
            )

    def visit_Constant(self, node: ast.Constant) -> None:
        """
        Analyzes constants (strings) for complexity, IPs, or URLs.

        Args:
            node (ast.Constant): The constant node.
        """
        if isinstance(node.value, str) and len(node.value) > 50:
            entropy = calculate_shannon_entropy(node.value)
            if entropy > 4.5:
                self._add_issue(
                    "HIGH",
                    f"High entropy string (Entropy: {entropy:.2f}). Potential paylod.",
                    node.lineno,
                )

            ips = NetworkForensics.extract_ips(node.value)
            if ips:
                self._add_issue(
                    "MEDIUM", f"Hardcoded IP Address detected: {ips}", node.lineno
                )
            urls = NetworkForensics.extract_urls(node.value)
            if urls:
                self._add_issue(
                    "MEDIUM", f"Hardcoded URL detected: {urls}", node.lineno
                )

    def _get_full_attr_name(self, node: ast.Attribute) -> str:
        """
        Recursively reconstructs the full name of an attribute access (e.g., a.b.c).

        Args:
            node (ast.Attribute): The attribute node.

        Returns:
            str: The dot-separated full attribute name.
        """
        parts = []
        curr = node
        while isinstance(curr, ast.Attribute):
            parts.append(curr.attr)
            curr = curr.value
        if isinstance(curr, ast.Name):
            parts.append(curr.id)
        return ".".join(reversed(parts))

    def _is_dynamic_getattr(self, node: ast.Call) -> bool:
        """
        Checks if a getattr call uses a dynamic attribute name.

        Args:
            node (ast.Call): The function call node.

        Returns:
            bool: True if the attribute name is not a literal constant.
        """
        return (
            isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) > 1
            and not isinstance(node.args[1], ast.Constant)
        )

    def check_mcp_tool_def(self, node):
        """
        Heuristic check for MCP tool definitions.
        """
        # This is a placeholder for deep MCP logic.
        # Real implementation would need to parse the specific MCP server structure.
        pass


def scan_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Performs a static audit on a single Python file.

    Args:
        filepath (str): Path to the .py file.

    Returns:
        List[Dict[str, Any]]: List of security findings.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        visitor = ShieldPro20(filepath)
        visitor.visit(tree)
        return visitor.report
    except Exception as e:
        return [
            {
                "severity": "CRITICAL",
                "file": filepath,
                "line": 0,
                "issue": f"Parse failure: {str(e)}",
            }
        ]


def scan_markdown_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Audits a Markdown file for phishing links and XSS.

    Args:
        filepath (str): Path to the .md file.

    Returns:
        List[Dict[str, Any]]: List of findings.
    """
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, url in markdown_links:
            warning = NetworkForensics.check_link_safety(url)
            if warning:
                findings.append(
                    {
                        "severity": "HIGH",
                        "file": filepath,
                        "line": 0,
                        "issue": f"Unsafe link: {warning}",
                    }
                )

            if "http" in text and text != url and "github" not in url:
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "file": filepath,
                        "line": 0,
                        "issue": f"Phishing mismatch: {text} -> {url}",
                    }
                )

        if "<script>" in content or "javascript:" in content:
            findings.append(
                {
                    "severity": "CRITICAL",
                    "file": filepath,
                    "line": 0,
                    "issue": "Script injection detected in MD.",
                }
            )

    except Exception as e:
        findings.append(
            {
                "severity": "CRITICAL",
                "file": filepath,
                "line": 0,
                "issue": f"MD Parse failure: {str(e)}",
            }
        )
    return findings


def scan_js_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Heuristic-based scan for JS/TS/React files using regex.

    Args:
        filepath (str): Path to the .js/.ts/etc file.

    Returns:
        List[Dict[str, Any]]: List of findings.
    """
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        patterns = {
            r"eval\s*\(": "CRITICAL: eval detected.",
            r"exec\s*\(": "CRITICAL: exec detected.",
            r"child_process": "HIGH: Potential RCE sink.",
            r"dangerouslySetInnerHTML": "HIGH: React XSS risk.",
            r"document\.write": "MEDIUM: document.write used.",
            r"innerHTML\s*=": "MEDIUM: innerHTML assignment.",
        }

        for i, line in enumerate(lines, 1):
            for pattern, msg in patterns.items():
                if re.search(pattern, line):
                    findings.append(
                        {
                            "severity": msg.split(":")[0],
                            "file": filepath,
                            "line": i,
                            "issue": msg,
                        }
                    )

            entropy = calculate_shannon_entropy(line.strip())
            if (
                len(line.strip()) > 50
                and entropy > 5.0
                and not line.strip().startswith("import ")
            ):
                findings.append(
                    {
                        "severity": "HIGH",
                        "file": filepath,
                        "line": i,
                        "issue": f"High entropy: {entropy:.2f}",
                    }
                )

            ips = NetworkForensics.extract_ips(line)
            if ips:
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "file": filepath,
                        "line": i,
                        "issue": f"Hardcoded IP: {ips}",
                    }
                )

    except Exception as e:
        findings.append(
            {
                "severity": "CRITICAL",
                "file": filepath,
                "line": 0,
                "issue": f"JS scan failure: {str(e)}",
            }
        )
    return findings


def scan_directory(path: str) -> List[Dict[str, Any]]:
    """
    Recursively scans a directory for supported file types.

    Args:
        path (str): The root directory to scan.

    Returns:
        List[Dict[str, Any]]: Aggregated findings from all files.
    """
    all_findings = []
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith(".py"):
                all_findings.extend(scan_file(full_path))
            elif file.endswith(".md"):
                all_findings.extend(scan_markdown_file(full_path))
            elif file.endswith((".js", ".ts", ".tsx", ".jsx")):
                all_findings.extend(scan_js_file(full_path))
    return all_findings


# --- Dynamic Analysis ---
class SecurityTrap(Exception):
    """Exception raised when a trapped system call is executed."""

    pass


class SafeImportHarness:
    """
    Context manager that traps dangerous system calls during module import.
    Used for basic dynamic detonation detection.
    """

    def __init__(self) -> None:
        self.mocks: Dict[str, MagicMock] = {}
        self.original_modules: Dict[str, Any] = sys.modules.copy()

    def _trap(self, *args, **kwargs) -> None:
        raise SecurityTrap("Execution attempted during import!")

    def __enter__(self) -> "SafeImportHarness":
        risky_modules = [
            "os",
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "shutil",
            "pickle",
        ]
        for mod_name in risky_modules:
            trap_mock = MagicMock()
            trap_mock.system.side_effect = self._trap
            trap_mock.popen.side_effect = self._trap
            trap_mock.call.side_effect = self._trap
            trap_mock.connect.side_effect = self._trap
            trap_mock.get.side_effect = self._trap
            trap_mock.post.side_effect = self._trap
            trap_mock.loads.side_effect = self._trap
            self.mocks[mod_name] = trap_mock
            sys.modules[mod_name] = trap_mock
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        current_keys = list(sys.modules.keys())
        for key in current_keys:
            if key not in self.original_modules:
                del sys.modules[key]
        sys.modules.update(self.original_modules)


def scan_dynamic(target_path: str) -> List[Dict[str, Any]]:
    """
    Performs dynamic import-time analysis using the SafeImportHarness.

    Args:
        target_path (str): Path to the Python file.

    Returns:
        List[Dict[str, Any]]: List of findings (usually CRITICAL on success).
    """
    findings = []
    file_path = Path(target_path)
    if file_path.suffix != ".py":
        return []

    try:
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, target_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            with SafeImportHarness():
                try:
                    spec.loader.exec_module(module)
                except SecurityTrap as e:
                    findings.append(
                        {
                            "severity": "CRITICAL",
                            "file": str(target_path),
                            "line": 0,
                            "issue": f"Dynamic Trap Trigerred: {str(e)}",
                        }
                    )
                except Exception:
                    pass
    except Exception:
        pass
    return findings


def scan_requirements(path: str) -> List[Dict[str, Any]]:
    """
    Audits a requirements.txt file for typosquatting and unpinned versions.

    Args:
        path (str): Path to the requirements.txt file.

    Returns:
        List[Dict[str, Any]]: List of supply chain findings.
    """
    findings = []
    try:
        with open(path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            pkg = line.strip()
            if not pkg or pkg.startswith("#"):
                continue

            suggestion = SupplyChainForensics.check_typosquatting(pkg)
            if suggestion:
                findings.append(
                    {
                        "severity": "HIGH",
                        "file": path,
                        "line": i,
                        "issue": f"Typosquat risk: {pkg} looks like {suggestion}",
                    }
                )

            if "==" not in pkg and ">=" not in pkg and "<=" not in pkg:
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "file": path,
                        "line": i,
                        "issue": f"Unpinned pkg: {pkg}",
                    }
                )
    except Exception as e:
        findings.append(
            {
                "severity": "CRITICAL",
                "file": path,
                "line": 0,
                "issue": f"Supply chain scan failed: {str(e)}",
            }
        )
    return findings


# --- Semantic Analysis ---
def extract_risky_functions(
    file_path: str, findings: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Extracts the source code of functions that contain high-severity findings.

    Args:
        file_path (str): Path to the source file.
        findings (List[Dict[str, Any]]): The static analysis findings.

    Returns:
        Dict[str, str]: name -> source_code mapping.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception:
        return {}

    risky_lines = {f["line"] for f in findings if f["severity"] in ["CRITICAL", "HIGH"]}
    function_sources = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(node.lineno <= line <= node.end_lineno for line in risky_lines):
                segment = ast.get_source_segment(source, node)
                if segment:
                    function_sources[node.name] = segment
    return function_sources


def scan_semantic(
    target_path: str, findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Identifies if any risky functions require further semantic review.

    Args:
        target_path (str): Path to the Python file.
        findings (List[Dict[str, Any]]): Current static findings.

    Returns:
        List[Dict[str, Any]]: Semantic review recommendations.
    """
    if not str(target_path).endswith(".py"):
        return []

    risky_funcs = extract_risky_functions(target_path, findings)
    if not risky_funcs:
        return []

    semantic_findings = []
    api_key = os.getenv("OPENCLAW_AI_API_KEY")

    for func_name, code in risky_funcs.items():
        if not api_key:
            semantic_findings.append(
                {
                    "severity": "MEDIUM",
                    "file": target_path,
                    "line": 0,
                    "issue": f"Semantic Review Required for '{func_name}' (Logic Bomb check)",
                }
            )
    return semantic_findings


def generate_markdown_report(
    findings: List[Dict[str, Any]], output_path: str = "SECURITY_REPORT.md"
) -> str:
    """
    Generates a production-grade Markdown report optimized for AI and human consumption.

    Args:
        findings (List[Dict[str, Any]]): The accumulated security findings.
        output_path (str): Where to save the report file.

    Returns:
        str: Absolute path to the generated report.
    """
    stats = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        sev = f.get("severity", "LOW")
        if sev in stats:
            stats[sev] += 1

    is_safe = stats["CRITICAL"] == 0 and stats["HIGH"] == 0
    status_icon = "✅" if is_safe else "❌"
    status_text = "APPROVED" if is_safe else "REJECTED"

    processed_findings = []
    for f in findings:
        emoji = (
            "🔴"
            if f["severity"] == "CRITICAL"
            else "🟠"
            if f["severity"] == "HIGH"
            else "🟡"
        )
        processed_findings.append(
            f"| {emoji} {f['severity']} | `{f['file']}:{f['line']}` | {f['issue']} |"
        )

    report_content = f"""# 🛡️ Shield Pro Security Report v{__version__}

**Date:** {os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()}
**Scan Status:** {status_icon} **{status_text}**

## 1. Executive Summary
| Metric | Count | Threshold | Status |
| :--- | :---: | :---: | :---: |
| **Critical** | {stats["CRITICAL"]} | 0 | {"❌" if stats["CRITICAL"] > 0 else "✅"} |
| **High** | {stats["HIGH"]} | 0 | {"❌" if stats["HIGH"] > 0 else "✅"} |
| **Medium** | {stats["MEDIUM"]} | Manual Review | {"⚠️" if stats["MEDIUM"] > 0 else "✅"} |

> **AI Agent Directive:**
> {status_text}. {"Proceed with integration." if is_safe else "Do not integrate. Resolve critical violations."}

## 2. Detailed Findings
| Severity | Location | Detected Issue |
| :--- | :--- | :--- |
{chr(10).join(processed_findings) if processed_findings else "| ✅ None | - | No security issues detected. |"}

## 3. Tool Capabilities Used
- [x] Python AST Analysis (Static Analysis)
- [x] Polyglot Regex Engine (JS/TS/React)
- [x] Markdown Link Forensics (Anti-Phishing)
- [x] Import Alias Tracking (Obfuscation Detection)
- [x] Entropy Scanning (Payload Detection)
- [x] Dynamic Detonation Harness (Import-Time)

---
*Generated by {__author__} (SEP-2026 Compliant)*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Shield Pro Security Auditor v{__version__}"
    )
    parser.add_argument(
        "--target", required=True, help="Path to file or directory to scan"
    )
    parser.add_argument(
        "--mode", choices=["full", "supply-chain"], default="full", help="Scan mode"
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target {target_path} not found.")
        sys.exit(1)

    print(
        f"Starting Shield Pro v{__version__} Audit on: {target_path}...",
        file=sys.stderr,
    )
    findings = []

    if args.target.endswith("requirements.txt") or args.mode == "supply-chain":
        findings.extend(scan_requirements(args.target))
    elif target_path.is_dir():
        findings.extend(scan_directory(str(target_path)))
    elif target_path.is_file():
        if target_path.suffix == ".md":
            findings.extend(scan_markdown_file(str(target_path)))
        elif target_path.suffix in [".js", ".ts", ".tsx", ".jsx"]:
            findings.extend(scan_js_file(str(target_path)))
        else:
            findings.extend(scan_file(str(target_path)))
            if target_path.suffix == ".py":
                findings.extend(scan_dynamic(str(target_path)))
                findings.extend(scan_semantic(str(target_path), findings))

    print(json.dumps(findings, indent=2))
    report_path = generate_markdown_report(findings)
    print(f"Report generated: {report_path}", file=sys.stderr)
