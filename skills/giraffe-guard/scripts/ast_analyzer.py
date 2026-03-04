#!/usr/bin/env python3
"""
🦒 Giraffe Guard AST Deep Analyzer
Semantic analysis of Python files using the built-in ast module.
Catches evasion techniques that grep-based detection cannot:
  - Variable concatenation for shell commands
  - eval/exec with dynamic (non-literal) content
  - Encoded payloads (base64 decode + exec chains)
  - Dynamic imports (__import__, importlib)
  - Obfuscated calls (getattr, globals()[], compile)
  - Network exfiltration patterns
  - File system tampering (writes to system paths)
  - Environment variable harvesting

Zero dependencies: uses only Python standard library.
Output: JSON lines compatible with audit.sh findings format.

Usage:
  python3 ast_analyzer.py <file.py>           # scan single file
  python3 ast_analyzer.py <directory>          # scan all .py files
  python3 ast_analyzer.py --json <file.py>     # JSON output
"""

import ast
import sys
import os
import json
import math
from collections import defaultdict


# ── Severity constants ──────────────────────────────────────────
CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

# ── Findings collector ──────────────────────────────────────────
findings = []


def add_finding(level, filepath, lineno, rule, message, remediation=""):
    findings.append({
        "level": level,
        "file": filepath,
        "line": lineno,
        "rule": rule,
        "content": message,
        "remediation": remediation,
    })


# ── Helper: check if an AST node is a literal (safe) value ─────
def is_literal(node):
    """Return True if the node is a simple literal (string, number, bool, None)."""
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(is_literal(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(is_literal(k) for k in node.keys if k) and all(is_literal(v) for v in node.values)
    # Python 3.6+ JoinedStr (f-string) is NOT a literal
    if isinstance(node, ast.JoinedStr):
        return False
    return False


def is_name(node, name):
    """Check if node is an ast.Name with given id."""
    return isinstance(node, ast.Name) and node.id == name


def get_string_value(node):
    """Extract string value from a Constant node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def get_attr_chain(node):
    """Get dotted attribute chain like 'os.system' from an AST node."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


# ── Shannon entropy ─────────────────────────────────────────────
def shannon_entropy(s):
    if not s:
        return 0.0
    freq = defaultdict(int)
    for c in s:
        freq[c] += 1
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


# ════════════════════════════════════════════════════════════════
#  AST Visitor — the core analysis engine
# ════════════════════════════════════════════════════════════════

class SecurityVisitor(ast.NodeVisitor):
    """Walk the AST and flag suspicious patterns."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.imports = {}        # name -> module  (e.g. {"os": "os", "sp": "subprocess"})
        self.from_imports = {}   # name -> (module, attr)
        self.assigned_strings = {}  # variable name -> string value
        self._in_class = False

    # ── Track imports ───────────────────────────────────────────
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for alias in node.names:
            name = alias.asname or alias.name
            self.from_imports[name] = (module, alias.name)
        self.generic_visit(node)

    # ── Track string assignments ────────────────────────────────
    def visit_Assign(self, node):
        # Track simple string assignments for concatenation detection
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            val = get_string_value(node.value)
            if val is not None:
                self.assigned_strings[node.targets[0].id] = val

        # Check for high-entropy string assignments (possible encoded payloads)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            s = node.value.value
            if len(s) >= 40 and shannon_entropy(s) > 4.5:
                add_finding(WARNING, self.filepath, node.lineno,
                            "ast-high-entropy-string",
                            f"High entropy string assigned (entropy={shannon_entropy(s):.1f}, len={len(s)})",
                            "Review whether this is an encoded payload or legitimate data")

        self.generic_visit(node)

    # ── Detect: eval / exec with dynamic content ────────────────
    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = get_attr_chain(node.func)

        # ── Rule: eval() / exec() with non-literal argument ────
        if func_name in ("eval", "exec"):
            if node.args:
                arg = node.args[0]
                if not is_literal(arg):
                    level = CRITICAL
                    detail = "dynamic content"
                    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                        detail = "string concatenation"
                    elif isinstance(arg, ast.JoinedStr):
                        detail = "f-string"
                    elif isinstance(arg, ast.Call):
                        inner = get_attr_chain(arg.func) if isinstance(arg.func, ast.Attribute) else (arg.func.id if isinstance(arg.func, ast.Name) else "unknown")
                        detail = f"result of {inner}()"
                    add_finding(level, self.filepath, node.lineno,
                                "ast-eval-dynamic",
                                f"{func_name}() called with {detail}",
                                f"Avoid {func_name}() with dynamic input; use safe alternatives")

        # ── Rule: compile() with exec/eval mode ────────────────
        if func_name == "compile":
            if len(node.args) >= 3:
                mode_arg = node.args[2]
                mode_val = get_string_value(mode_arg)
                if mode_val in ("exec", "eval"):
                    add_finding(WARNING, self.filepath, node.lineno,
                                "ast-compile-exec",
                                f"compile() with mode='{mode_val}' can execute arbitrary code",
                                "Review code being compiled; prefer static imports")

        # ── Rule: __import__() ─────────────────────────────────
        if func_name == "__import__":
            if node.args and not is_literal(node.args[0]):
                add_finding(CRITICAL, self.filepath, node.lineno,
                            "ast-dynamic-import",
                            "__import__() with dynamic module name",
                            "Use static imports; dynamic imports hide dependencies")
            elif node.args:
                mod = get_string_value(node.args[0])
                if mod and mod in ("os", "subprocess", "shutil", "ctypes", "socket"):
                    add_finding(WARNING, self.filepath, node.lineno,
                                "ast-dangerous-import",
                                f"__import__('{mod}') — dangerous module imported dynamically",
                                "Use normal import statement for transparency")

        # ── Rule: importlib.import_module with dynamic arg ─────
        if func_name in ("importlib.import_module", "import_module"):
            if node.args and not is_literal(node.args[0]):
                add_finding(CRITICAL, self.filepath, node.lineno,
                            "ast-dynamic-import",
                            "importlib.import_module() with dynamic argument",
                            "Use static imports; dynamic imports hide dependencies")

        # ── Rule: getattr / globals / locals obfuscation ───────
        if func_name == "getattr":
            if len(node.args) >= 2:
                attr_arg = node.args[1]
                if not is_literal(attr_arg):
                    add_finding(WARNING, self.filepath, node.lineno,
                                "ast-getattr-dynamic",
                                "getattr() with dynamic attribute name (possible obfuscation)",
                                "Use direct attribute access instead of getattr with variables")
                else:
                    attr_val = get_string_value(attr_arg)
                    if attr_val in ("system", "popen", "exec", "eval", "compile",
                                    "call", "Popen", "run", "check_output"):
                        add_finding(CRITICAL, self.filepath, node.lineno,
                                    "ast-getattr-dangerous",
                                    f"getattr(obj, '{attr_val}') — accessing dangerous function via getattr",
                                    "Call the function directly instead of using getattr obfuscation")

        # ── Rule: os.system / subprocess with concatenation ────
        if func_name in ("os.system", "os.popen", "subprocess.call",
                          "subprocess.Popen", "subprocess.run",
                          "subprocess.check_output", "subprocess.check_call"):
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    add_finding(CRITICAL, self.filepath, node.lineno,
                                "ast-command-concat",
                                f"{func_name}() with string concatenation (injection risk)",
                                "Use list form: subprocess.run(['cmd', arg]) instead of string concatenation")
                elif isinstance(arg, ast.JoinedStr):
                    add_finding(CRITICAL, self.filepath, node.lineno,
                                "ast-command-fstring",
                                f"{func_name}() with f-string (injection risk)",
                                "Use list form: subprocess.run(['cmd', arg]) instead of f-string")
                elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    # Static string — check for suspicious content
                    cmd = arg.value
                    if any(p in cmd for p in ("curl ", "wget ", "nc ", "/dev/tcp", "base64")):
                        add_finding(WARNING, self.filepath, node.lineno,
                                    "ast-suspicious-command",
                                    f"{func_name}() with suspicious static command: {cmd[:80]}",
                                    "Review command for malicious intent")

        # ── Rule: base64.b64decode chained with exec ───────────
        if func_name in ("base64.b64decode", "b64decode"):
            # Check if the result is passed to exec/eval
            parent = getattr(node, '_parent', None)
            if parent and isinstance(parent, ast.Call):
                parent_name = ""
                if isinstance(parent.func, ast.Name):
                    parent_name = parent.func.id
                if parent_name in ("exec", "eval"):
                    add_finding(CRITICAL, self.filepath, node.lineno,
                                "ast-b64-exec",
                                "base64.b64decode() result passed to exec/eval",
                                "Never execute decoded base64 content")

        # ── Rule: codecs.decode (rot13 / hex obfuscation) ──────
        if func_name in ("codecs.decode", "decode"):
            if len(node.args) >= 2:
                codec = get_string_value(node.args[1])
                if codec in ("rot_13", "rot13", "hex", "unicode_escape"):
                    add_finding(WARNING, self.filepath, node.lineno,
                                "ast-codec-obfuscation",
                                f"codecs.decode() with '{codec}' — possible obfuscation",
                                "Review decoded content; encoding is commonly used to hide malicious payloads")

        # ── Rule: socket.connect (network) ─────────────────────
        if func_name in ("socket.connect", "connect"):
            if isinstance(node.func, ast.Attribute) and get_attr_chain(node.func).endswith(".connect"):
                add_finding(INFO, self.filepath, node.lineno,
                            "ast-network-connect",
                            "Socket connect detected",
                            "Verify the connection target is legitimate")

        # ── Rule: open() to system paths ───────────────────────
        if func_name == "open":
            if node.args:
                path_arg = get_string_value(node.args[0])
                if path_arg:
                    sus_paths = ("/etc/", "/usr/", "/bin/", "/sbin/", "/var/",
                                 "/tmp/", "/root/", "~/.ssh", "~/.bashrc",
                                 "~/.bash_profile", "~/.profile", "~/.zshrc",
                                 "/Library/LaunchAgents", "/Library/LaunchDaemons")
                    for sp in sus_paths:
                        if path_arg.startswith(sp):
                            # Check write mode
                            write_mode = False
                            if len(node.args) >= 2:
                                mode = get_string_value(node.args[1])
                                if mode and ("w" in mode or "a" in mode):
                                    write_mode = True
                            for kw in node.keywords:
                                if kw.arg == "mode":
                                    m = get_string_value(kw.value)
                                    if m and ("w" in m or "a" in m):
                                        write_mode = True
                            if write_mode:
                                add_finding(CRITICAL, self.filepath, node.lineno,
                                            "ast-system-write",
                                            f"Writing to system path: {path_arg}",
                                            "Avoid writing to system directories from skill code")
                            else:
                                add_finding(INFO, self.filepath, node.lineno,
                                            "ast-system-read",
                                            f"Reading system path: {path_arg}",
                                            "Verify this file access is necessary")
                            break

        # ── Rule: environment variable harvesting ──────────────
        if func_name in ("os.environ.get", "os.getenv"):
            if node.args:
                env_name = get_string_value(node.args[0])
                if env_name:
                    sensitive_envs = ("AWS_SECRET", "AWS_ACCESS", "API_KEY", "SECRET_KEY",
                                      "TOKEN", "PASSWORD", "PRIVATE_KEY", "DATABASE_URL",
                                      "GITHUB_TOKEN", "STRIPE_SECRET", "OPENAI_API_KEY")
                    for se in sensitive_envs:
                        if se in env_name.upper():
                            add_finding(INFO, self.filepath, node.lineno,
                                        "ast-env-access",
                                        f"Accessing sensitive env var: {env_name}",
                                        "Ensure this env var access is expected and not exfiltrating credentials")
                            break

        self.generic_visit(node)

    # ── Detect: string concatenation building commands ──────────
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            # Check if both sides are strings that form a suspicious command
            left_val = get_string_value(node.left) if isinstance(node.left, ast.Constant) else self.assigned_strings.get(node.left.id, "") if isinstance(node.left, ast.Name) else ""
            right_val = get_string_value(node.right) if isinstance(node.right, ast.Constant) else self.assigned_strings.get(node.right.id, "") if isinstance(node.right, ast.Name) else ""

            if left_val and right_val:
                combined = left_val + right_val
                dangerous = ["curl ", "wget ", "bash ", "/bin/sh", "eval(", "exec(",
                             "os.system", "subprocess", "/dev/tcp", "nc -e",
                             "powershell", "import os"]
                for d in dangerous:
                    if d in combined:
                        add_finding(CRITICAL, self.filepath, node.lineno,
                                    "ast-string-concat-cmd",
                                    f"String concatenation builds dangerous command: '{combined[:60]}'",
                                    "Avoid building commands through string concatenation")
                        break
        self.generic_visit(node)

    # ── Detect: try/except that silences all errors ─────────────
    def visit_Try(self, node):
        for handler in node.handlers:
            if handler.type is None:  # bare except:
                # Check if the handler just passes
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    add_finding(INFO, self.filepath, node.lineno,
                                "ast-bare-except-pass",
                                "Bare except: pass — silences all errors (may hide malicious failures)",
                                "Catch specific exceptions instead of bare except")
        self.generic_visit(node)


# ════════════════════════════════════════════════════════════════
#  Parent annotator (needed for b64decode→exec chain detection)
# ════════════════════════════════════════════════════════════════

class ParentAnnotator(ast.NodeVisitor):
    """Annotate each AST node with a _parent reference."""
    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child._parent = node
            self.generic_visit(child)


# ════════════════════════════════════════════════════════════════
#  File scanner
# ════════════════════════════════════════════════════════════════

def scan_file(filepath):
    """Parse and analyze a single Python file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except (OSError, IOError) as e:
        add_finding(WARNING, filepath, 0, "ast-parse-error", f"Cannot read file: {e}")
        return

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        # Not a valid Python file — skip silently
        return

    # Annotate parents for chain detection
    ParentAnnotator().generic_visit(tree)

    # Run security visitor
    visitor = SecurityVisitor(filepath)
    visitor.visit(tree)


def scan_directory(dirpath):
    """Recursively scan all .py files in a directory."""
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv",
                 "env", ".env", ".tox", ".mypy_cache", ".pytest_cache",
                 "test", "tests", "__tests__", "spec", "fixtures", "testdata"}
    for root, dirs, files in os.walk(dirpath):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            if fname.endswith(".py"):
                scan_file(os.path.join(root, fname))


# ════════════════════════════════════════════════════════════════
#  Output formatters
# ════════════════════════════════════════════════════════════════

def output_text(findings_list):
    """Human-readable output."""
    colors = {
        CRITICAL: "\033[0;31m",
        WARNING: "\033[0;33m",
        INFO: "\033[0;36m",
    }
    nc = "\033[0m"
    bold = "\033[1m"
    dim = "\033[2m"

    if not findings_list:
        print(f"\n  {bold}🦒 AST Deep Analyzer: ✅ No issues found.{nc}\n")
        return

    print(f"\n  {bold}🦒 AST Deep Analyzer: {len(findings_list)} findings{nc}\n")
    for f in findings_list:
        color = colors.get(f["level"], nc)
        icon = "🔴" if f["level"] == CRITICAL else "🟡" if f["level"] == WARNING else "[i] "
        print(f"  {icon} {color}{f['level']}{nc} | {bold}{f['file']}:{f['line']}{nc} | {dim}{f['rule']}{nc}")
        print(f"     {f['content']}")
        if f.get("remediation"):
            print(f"     {dim}>> FIX: {f['remediation']}{nc}")
    print()


def output_json(findings_list):
    """JSON output compatible with audit.sh."""
    for f in findings_list:
        print(json.dumps(f, ensure_ascii=False))


# ════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════

def main():
    json_mode = False
    targets = []

    for arg in sys.argv[1:]:
        if arg == "--json":
            json_mode = True
        elif arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            targets.append(arg)

    if not targets:
        print("Usage: python3 ast_analyzer.py [--json] <file_or_directory> ...")
        sys.exit(1)

    for target in targets:
        if os.path.isfile(target):
            scan_file(target)
        elif os.path.isdir(target):
            scan_directory(target)
        else:
            print(f"Error: {target} not found", file=sys.stderr)
            sys.exit(1)

    if json_mode:
        output_json(findings)
    else:
        output_text(findings)

    # Exit code
    criticals = sum(1 for f in findings if f["level"] == CRITICAL)
    warnings = sum(1 for f in findings if f["level"] == WARNING)
    if criticals > 0:
        sys.exit(2)
    elif warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
