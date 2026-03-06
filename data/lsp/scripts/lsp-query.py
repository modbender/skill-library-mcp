#!/usr/bin/env python3
"""
Multi-language LSP client for AI agent code navigation.

Manages per-language background daemons (pyright for Python, typescript-language-server
for JS/TS, rust-analyzer for Rust, gopls for Go, clangd for C/C++, bash-language-server
for shell scripts). Auto-detects language from file extension and routes to the correct
daemon. Each daemon idles out independently after a configurable timeout.

Usage:
    lsp-query definition <file> <line> <col>
    lsp-query references <file> <line> <col>
    lsp-query hover <file> <line> <col>
    lsp-query symbols <file>
    lsp-query diagnostics <file>
    lsp-query completions <file> <line> <col>
    lsp-query signature <file> <line> <col>
    lsp-query rename <file> <line> <col> <new_name>
    lsp-query workspace-symbols <query>
    lsp-query servers                              List running language daemons
    lsp-query shutdown [language]                   Stop one or all daemons
    lsp-query languages                             Show supported languages

Lines and columns are 1-indexed (human-friendly).

Environment:
    LSP_WORKSPACE   Override workspace root (default: git root or cwd)
    LSP_SERVER      Override LSP server command for ALL languages
    LSP_TIMEOUT     Server idle timeout in seconds (default: 300)
    LSP_LANG        Force a specific language (bypass auto-detection)
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import signal
import shutil
from pathlib import Path


# ---------------------------------------------------------------------------
# Language configuration
# ---------------------------------------------------------------------------

LANGUAGES = {
    "python": {
        "extensions": {".py", ".pyi", ".pyx"},
        "server_cmd": ["pyright-langserver", "--stdio"],
        "lang_id": "python",
        "install": "npm install -g pyright",
    },
    "typescript": {
        "extensions": {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"},
        "server_cmd": ["typescript-language-server", "--stdio"],
        "lang_id_map": {
            ".ts": "typescript",
            ".tsx": "typescriptreact",
            ".js": "javascript",
            ".jsx": "javascriptreact",
            ".mjs": "javascript",
            ".cjs": "javascript",
        },
        "lang_id": "typescript",
        "install": "npm install -g typescript-language-server typescript",
    },
    "rust": {
        "extensions": {".rs"},
        "server_cmd": ["rust-analyzer"],
        "lang_id": "rust",
        "install": "rustup component add rust-analyzer",
    },
    "go": {
        "extensions": {".go"},
        "server_cmd": ["gopls", "serve"],
        "lang_id": "go",
        "install": "go install golang.org/x/tools/gopls@latest",
    },
    "c": {
        "extensions": {".c", ".h", ".cpp", ".cxx", ".cc", ".hpp", ".hxx", ".hh"},
        "server_cmd": ["clangd"],
        "lang_id_map": {
            ".c": "c", ".h": "c",
            ".cpp": "cpp", ".cxx": "cpp", ".cc": "cpp",
            ".hpp": "cpp", ".hxx": "cpp", ".hh": "cpp",
        },
        "lang_id": "c",
        "install": "apt install clangd  # or brew install llvm",
    },
    "bash": {
        "extensions": {".sh", ".bash", ".zsh"},
        "server_cmd": ["bash-language-server", "start"],
        "lang_id": "shellscript",
        "install": "npm install -g bash-language-server",
    },
    "java": {
        "extensions": {".java"},
        "server_cmd": ["jdtls"],
        "lang_id": "java",
        "install": "https://github.com/eclipse-jdtls/eclipse.jdt.ls#installation",
    },
    "css": {
        "extensions": {".css", ".scss", ".less"},
        "server_cmd": ["vscode-css-language-server", "--stdio"],
        "lang_id_map": {
            ".css": "css", ".scss": "scss", ".less": "less",
        },
        "lang_id": "css",
        "install": "npm install -g vscode-langservers-extracted",
    },
    "html": {
        "extensions": {".html", ".htm"},
        "server_cmd": ["vscode-html-language-server", "--stdio"],
        "lang_id": "html",
        "install": "npm install -g vscode-langservers-extracted",
    },
    "json": {
        "extensions": {".json", ".jsonc"},
        "server_cmd": ["vscode-json-language-server", "--stdio"],
        "lang_id": "json",
        "install": "npm install -g vscode-langservers-extracted",
    },
}

# Build extension -> language lookup.
_EXT_TO_LANG = {}
for _lang, _cfg in LANGUAGES.items():
    for _ext in _cfg["extensions"]:
        _EXT_TO_LANG[_ext] = _lang


def detect_language(filepath):
    """Detect language from file extension."""
    ext = Path(filepath).suffix.lower()
    return _EXT_TO_LANG.get(ext)


def get_lang_id(filepath, lang):
    """Get the LSP languageId for a specific file."""
    cfg = LANGUAGES.get(lang, {})
    ext = Path(filepath).suffix.lower()
    lang_id_map = cfg.get("lang_id_map", {})
    return lang_id_map.get(ext, cfg.get("lang_id", lang))


def get_server_cmd(lang):
    """Get the server command for a language, checking if the binary exists."""
    override = os.environ.get("LSP_SERVER")
    if override:
        return override.split()
    cfg = LANGUAGES.get(lang)
    if not cfg:
        return None
    cmd = cfg["server_cmd"]
    binary = cmd[0]
    if shutil.which(binary):
        return cmd
    return None


# ---------------------------------------------------------------------------
# JSON-RPC / LSP protocol helpers
# ---------------------------------------------------------------------------

def encode_msg(obj):
    body = json.dumps(obj).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    return header + body


def read_msg(stream):
    """Read one LSP JSON-RPC message from a byte stream."""
    headers = {}
    while True:
        line = b""
        while not line.endswith(b"\r\n"):
            ch = stream.read(1)
            if not ch:
                return None
            line += ch
        line = line.strip()
        if not line:
            break
        k, v = line.decode("ascii").split(":", 1)
        headers[k.strip().lower()] = v.strip()
    length = int(headers.get("content-length", 0))
    if length == 0:
        return None
    body = b""
    while len(body) < length:
        chunk = stream.read(length - len(body))
        if not chunk:
            return None
        body += chunk
    return json.loads(body.decode("utf-8"))


def uri(path):
    p = os.path.abspath(path)
    return "file://" + p


def path_from_uri(u):
    if u.startswith("file://"):
        return u[7:]
    return u


# ---------------------------------------------------------------------------
# LSP Client (manages a single language server subprocess)
# ---------------------------------------------------------------------------

class LSPClient:
    def __init__(self, workspace, server_cmd, lang="python"):
        self.workspace = os.path.abspath(workspace)
        self.server_cmd = server_cmd
        self.lang = lang
        self._id = 0
        self._pending = {}
        self._lock = threading.Lock()
        self._proc = None
        self._reader_thread = None
        self._initialized = False
        self._open_files = set()
        self._diagnostics = {}

    def start(self):
        self._proc = subprocess.Popen(
            self.server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()
        self._initialize()

    def _reader_loop(self):
        while self._proc and self._proc.poll() is None:
            try:
                msg = read_msg(self._proc.stdout)
            except Exception:
                break
            if msg is None:
                break
            if "method" in msg and "id" not in msg:
                self._handle_notification(msg)
                continue
            msg_id = msg.get("id")
            if msg_id is not None:
                with self._lock:
                    ev = self._pending.pop(msg_id, None)
                if ev:
                    ev["result"] = msg
                    ev["event"].set()

    def _handle_notification(self, msg):
        method = msg.get("method", "")
        if method == "textDocument/publishDiagnostics":
            params = msg.get("params", {})
            self._diagnostics[params.get("uri", "")] = params.get("diagnostics", [])

    def _send_request(self, method, params, timeout=30):
        with self._lock:
            self._id += 1
            rid = self._id
        msg = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params}
        ev = {"event": threading.Event(), "result": None}
        with self._lock:
            self._pending[rid] = ev
        self._proc.stdin.write(encode_msg(msg))
        self._proc.stdin.flush()
        ev["event"].wait(timeout=timeout)
        return ev["result"]

    def _send_notification(self, method, params):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        self._proc.stdin.write(encode_msg(msg))
        self._proc.stdin.flush()

    def _initialize(self):
        result = self._send_request("initialize", {
            "processId": os.getpid(),
            "rootUri": uri(self.workspace),
            "rootPath": self.workspace,
            "capabilities": {
                "textDocument": {
                    "definition": {"dynamicRegistration": False},
                    "references": {"dynamicRegistration": False},
                    "hover": {"contentFormat": ["plaintext", "markdown"]},
                    "completion": {"completionItem": {"snippetSupport": False}},
                    "signatureHelp": {"signatureInformation": {"parameterInformation": {"labelOffsetSupport": True}}},
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "rename": {"prepareSupport": True},
                    "publishDiagnostics": {"relatedInformation": True},
                },
                "workspace": {
                    "symbol": {"dynamicRegistration": False},
                },
            },
        }, timeout=60)
        self._send_notification("initialized", {})
        self._initialized = True
        return result

    def _open_file(self, filepath):
        furi = uri(filepath)
        if furi in self._open_files:
            return furi
        try:
            text = Path(filepath).read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            return furi
        lang_id = get_lang_id(filepath, self.lang)
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": furi,
                "languageId": lang_id,
                "version": 1,
                "text": text,
            }
        })
        self._open_files.add(furi)
        time.sleep(0.5)
        return furi

    def definition(self, filepath, line, col):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/definition", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
        })
        return self._format_locations(resp)

    def references(self, filepath, line, col):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/references", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
            "context": {"includeDeclaration": True},
        })
        return self._format_locations(resp)

    def hover(self, filepath, line, col):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/hover", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
        })
        if not resp or "result" not in resp:
            return "No hover info"
        result = resp["result"]
        if result is None:
            return "No hover info"
        contents = result.get("contents", "")
        if isinstance(contents, dict):
            return contents.get("value", str(contents))
        if isinstance(contents, list):
            parts = []
            for c in contents:
                parts.append(c.get("value", str(c)) if isinstance(c, dict) else str(c))
            return "\n".join(parts)
        return str(contents)

    def symbols(self, filepath):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/documentSymbol", {
            "textDocument": {"uri": furi},
        })
        if not resp or "result" not in resp:
            return "No symbols"
        return self._format_symbols(resp["result"], filepath)

    def workspace_symbols(self, query):
        resp = self._send_request("workspace/symbol", {"query": query})
        if not resp or "result" not in resp:
            return "No symbols found"
        result = resp["result"]
        if not result:
            return "No symbols found"
        lines = []
        for sym in result:
            loc = sym.get("location", {})
            fpath = path_from_uri(loc.get("uri", ""))
            rng = loc.get("range", {}).get("start", {})
            ln = rng.get("line", 0) + 1
            kind = _SYMBOL_KINDS.get(sym.get("kind", 0), "unknown")
            container = sym.get("containerName", "")
            prefix = f"{container}." if container else ""
            lines.append(f"  {kind:12s} {prefix}{sym['name']:30s} {fpath}:{ln}")
        return "\n".join(lines)

    def diagnostics(self, filepath):
        furi = self._open_file(filepath)
        time.sleep(1.0)
        diags = self._diagnostics.get(furi, [])
        if not diags:
            return "No diagnostics"
        lines = []
        for d in diags:
            rng = d.get("range", {}).get("start", {})
            ln = rng.get("line", 0) + 1
            col = rng.get("character", 0) + 1
            sev = {1: "error", 2: "warning", 3: "info", 4: "hint"}.get(d.get("severity", 3), "info")
            msg = d.get("message", "")
            rule = d.get("code", "")
            lines.append(f"  {sev:8s} L{ln}:{col:3d}  {msg}" + (f"  [{rule}]" if rule else ""))
        return "\n".join(lines)

    def completions(self, filepath, line, col):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/completion", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
        })
        if not resp or "result" not in resp:
            return "No completions"
        result = resp["result"]
        items = result.get("items", []) if isinstance(result, dict) else result
        if not items:
            return "No completions"
        lines = []
        for item in items[:20]:
            kind = _COMPLETION_KINDS.get(item.get("kind", 0), "")
            detail = item.get("detail", "")
            label = item.get("label", "")
            lines.append(f"  {kind:12s} {label:30s} {detail}")
        if len(items) > 20:
            lines.append(f"  ... and {len(items) - 20} more")
        return "\n".join(lines)

    def signature(self, filepath, line, col):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/signatureHelp", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
        })
        if not resp or "result" not in resp or resp["result"] is None:
            return "No signature info"
        result = resp["result"]
        sigs = result.get("signatures", [])
        if not sigs:
            return "No signature info"
        lines = []
        active = result.get("activeSignature", 0)
        for i, sig in enumerate(sigs):
            marker = ">> " if i == active else "   "
            label = sig.get("label", "")
            doc = sig.get("documentation", "")
            if isinstance(doc, dict):
                doc = doc.get("value", "")
            lines.append(f"{marker}{label}")
            if doc:
                lines.append(f"      {doc[:200]}")
        return "\n".join(lines)

    def rename(self, filepath, line, col, new_name):
        furi = self._open_file(filepath)
        resp = self._send_request("textDocument/rename", {
            "textDocument": {"uri": furi},
            "position": {"line": line, "character": col},
            "newName": new_name,
        })
        if not resp or "result" not in resp or resp["result"] is None:
            return "Rename not available"
        result = resp["result"]
        changes = result.get("changes", {})
        if not changes:
            doc_changes = result.get("documentChanges", [])
            if not doc_changes:
                return "No changes"
            lines = []
            for dc in doc_changes:
                fpath = path_from_uri(dc.get("textDocument", {}).get("uri", ""))
                edits = dc.get("edits", [])
                lines.append(f"  {fpath}: {len(edits)} edit(s)")
                for e in edits[:10]:
                    rng = e.get("range", {})
                    start = rng.get("start", {})
                    lines.append(f"    L{start.get('line',0)+1}:{start.get('character',0)+1} -> {e.get('newText','')!r}")
            return "\n".join(lines)
        lines = []
        for furi_key, edits in changes.items():
            fpath = path_from_uri(furi_key)
            lines.append(f"  {fpath}: {len(edits)} edit(s)")
            for e in edits[:10]:
                rng = e.get("range", {})
                start = rng.get("start", {})
                lines.append(f"    L{start.get('line',0)+1}:{start.get('character',0)+1} -> {e.get('newText','')!r}")
        return "\n".join(lines)

    def shutdown(self):
        if self._proc and self._proc.poll() is None:
            try:
                self._send_request("shutdown", {}, timeout=5)
                self._send_notification("exit", {})
                self._proc.wait(timeout=5)
            except Exception:
                self._proc.kill()
        self._initialized = False

    def _format_locations(self, resp):
        if not resp or "result" not in resp:
            return "Not found"
        result = resp["result"]
        if result is None:
            return "Not found"
        if isinstance(result, dict):
            result = [result]
        if not result:
            return "Not found"
        lines = []
        for loc in result:
            if "targetUri" in loc:
                fpath = path_from_uri(loc["targetUri"])
                rng = loc.get("targetSelectionRange", loc.get("targetRange", {})).get("start", {})
            else:
                fpath = path_from_uri(loc.get("uri", ""))
                rng = loc.get("range", {}).get("start", {})
            ln = rng.get("line", 0) + 1
            col = rng.get("character", 0) + 1
            try:
                fpath = os.path.relpath(fpath, self.workspace)
            except ValueError:
                pass
            lines.append(f"  {fpath}:{ln}:{col}")
        return "\n".join(lines)

    def _format_symbols(self, symbols, filepath, indent=0):
        if not symbols:
            return "No symbols"
        lines = []
        prefix = "  " * indent
        for sym in symbols:
            name = sym.get("name", "")
            kind = _SYMBOL_KINDS.get(sym.get("kind", 0), "unknown")
            rng = sym.get("selectionRange", sym.get("range", {}))
            start = rng.get("start", {})
            ln = start.get("line", 0) + 1
            detail = sym.get("detail", "")
            detail_str = f"  ({detail})" if detail else ""
            lines.append(f"{prefix}  {kind:12s} {name:30s} L{ln}{detail_str}")
            children = sym.get("children", [])
            if children:
                lines.append(self._format_symbols(children, filepath, indent + 1))
        return "\n".join(lines)


_SYMBOL_KINDS = {
    1: "file", 2: "module", 3: "namespace", 4: "package", 5: "class",
    6: "method", 7: "property", 8: "field", 9: "constructor", 10: "enum",
    11: "interface", 12: "function", 13: "variable", 14: "constant",
    15: "string", 16: "number", 17: "boolean", 18: "array", 19: "object",
    20: "key", 21: "null", 22: "enummember", 23: "struct", 24: "event",
    25: "operator", 26: "typeparam",
}

_COMPLETION_KINDS = {
    1: "text", 2: "method", 3: "function", 4: "constructor", 5: "field",
    6: "variable", 7: "class", 8: "interface", 9: "module", 10: "property",
    11: "unit", 12: "value", 13: "enum", 14: "keyword", 15: "snippet",
    16: "color", 17: "file", 18: "reference", 19: "folder", 20: "enummember",
    21: "constant", 22: "struct", 23: "event", 24: "operator", 25: "typeparam",
}


# ---------------------------------------------------------------------------
# Multi-language daemon (one LSPClient per language, single process)
# ---------------------------------------------------------------------------

SOCK_DIR = os.path.expanduser("~/.cache/lsp-query")
DEFAULT_TIMEOUT = 300


def _sock_path():
    return os.environ.get("LSP_SOCK", os.path.join(SOCK_DIR, "daemon.sock"))


def _workspace_root():
    ws = os.environ.get("LSP_WORKSPACE")
    if ws:
        return ws
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        if root:
            return root
    except Exception:
        pass
    return os.getcwd()


def _idle_timeout():
    return int(os.environ.get("LSP_TIMEOUT", DEFAULT_TIMEOUT))


class MultiLangDaemon:
    """Manages multiple LSP clients, one per language. Lazy-starts servers on demand."""

    def __init__(self, workspace):
        self.workspace = workspace
        self._clients = {}  # lang -> LSPClient
        self._last_used = {}  # lang -> timestamp
        self._lock = threading.Lock()

    def get_client(self, lang):
        """Get or start an LSP client for the given language."""
        with self._lock:
            if lang in self._clients:
                self._last_used[lang] = time.time()
                return self._clients[lang]

            server_cmd = get_server_cmd(lang)
            if not server_cmd:
                cfg = LANGUAGES.get(lang, {})
                install_hint = cfg.get("install", "unknown")
                return None, f"Server not found for '{lang}'. Install with: {install_hint}"

            client = LSPClient(self.workspace, server_cmd, lang=lang)
            try:
                client.start()
            except Exception as e:
                return None, f"Failed to start {lang} server: {e}"

            self._clients[lang] = client
            self._last_used[lang] = time.time()
            return client

    def shutdown_lang(self, lang):
        with self._lock:
            client = self._clients.pop(lang, None)
            self._last_used.pop(lang, None)
        if client:
            client.shutdown()
            return True
        return False

    def shutdown_all(self):
        with self._lock:
            langs = list(self._clients.keys())
        for lang in langs:
            self.shutdown_lang(lang)

    def cleanup_idle(self, timeout):
        """Shut down servers that have been idle longer than timeout."""
        now = time.time()
        with self._lock:
            idle_langs = [
                lang for lang, ts in self._last_used.items()
                if now - ts > timeout
            ]
        for lang in idle_langs:
            self.shutdown_lang(lang)

    def active_servers(self):
        """Return list of (lang, uptime_seconds) for active servers."""
        now = time.time()
        with self._lock:
            return [
                (lang, now - self._last_used.get(lang, now))
                for lang in self._clients
            ]

    @property
    def has_clients(self):
        with self._lock:
            return len(self._clients) > 0


def _run_daemon():
    """Run the multi-language LSP daemon."""
    sock_path = _sock_path()
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)

    if os.path.exists(sock_path):
        os.unlink(sock_path)

    workspace = _workspace_root()
    daemon = MultiLangDaemon(workspace)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(5)
    server.settimeout(1.0)

    idle_timeout = _idle_timeout()
    last_activity = time.time()

    def _shutdown_handler(signum, frame):
        daemon.shutdown_all()
        server.close()
        if os.path.exists(sock_path):
            os.unlink(sock_path)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    pid_path = sock_path + ".pid"
    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))

    try:
        while True:
            try:
                conn, _ = server.accept()
            except socket.timeout:
                # Periodic idle cleanup.
                daemon.cleanup_idle(idle_timeout)
                if time.time() - last_activity > idle_timeout and not daemon.has_clients:
                    break
                continue

            last_activity = time.time()
            try:
                data = b""
                while True:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n\n" in data:
                        break

                request = json.loads(data.decode("utf-8").strip())
                result = _handle_request(daemon, request)
                response = json.dumps(result).encode("utf-8")
                conn.sendall(response)
            except Exception as e:
                try:
                    conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
                except Exception:
                    pass
            finally:
                conn.close()
    finally:
        daemon.shutdown_all()
        server.close()
        if os.path.exists(sock_path):
            os.unlink(sock_path)
        if os.path.exists(pid_path):
            os.unlink(pid_path)


def _handle_request(daemon, req):
    cmd = req.get("command", "")

    # Commands that don't need a language.
    if cmd == "ping":
        return {"result": "pong"}
    if cmd == "shutdown":
        lang = req.get("language")
        if lang:
            ok = daemon.shutdown_lang(lang)
            return {"result": f"shutdown {lang}" if ok else f"{lang} not running"}
        daemon.shutdown_all()
        return {"result": "shutdown all"}
    if cmd == "servers":
        active = daemon.active_servers()
        if not active:
            return {"result": "No active servers"}
        lines = []
        for lang, idle in active:
            lines.append(f"  {lang:15s}  idle {idle:.0f}s")
        return {"result": "\n".join(lines)}
    if cmd == "languages":
        lines = []
        for lang, cfg in sorted(LANGUAGES.items()):
            exts = ", ".join(sorted(cfg["extensions"]))
            binary = cfg["server_cmd"][0]
            installed = "installed" if shutil.which(binary) else "not found"
            lines.append(f"  {lang:15s}  {exts:35s}  {binary} ({installed})")
        return {"result": "\n".join(lines)}

    # Commands that need a file -> language resolution.
    filepath = req.get("file")
    forced_lang = req.get("language") or os.environ.get("LSP_LANG")
    lang = forced_lang or (detect_language(filepath) if filepath else None)

    if not lang:
        ext = Path(filepath).suffix if filepath else "?"
        return {"error": f"Unsupported file type: {ext}. Use LSP_LANG=<language> to force. Supported: {', '.join(sorted(LANGUAGES.keys()))}"}

    result = daemon.get_client(lang)
    if isinstance(result, tuple):
        # Error case: (None, error_message)
        return {"error": result[1]}
    client = result

    line = req.get("line", 1) - 1
    col = req.get("col", 1) - 1

    if cmd == "definition":
        return {"result": client.definition(filepath, line, col)}
    elif cmd == "references":
        return {"result": client.references(filepath, line, col)}
    elif cmd == "hover":
        return {"result": client.hover(filepath, line, col)}
    elif cmd == "symbols":
        return {"result": client.symbols(filepath)}
    elif cmd == "diagnostics":
        return {"result": client.diagnostics(filepath)}
    elif cmd == "completions":
        return {"result": client.completions(filepath, line, col)}
    elif cmd == "signature":
        return {"result": client.signature(filepath, line, col)}
    elif cmd == "rename":
        new_name = req.get("new_name", "")
        return {"result": client.rename(filepath, line, col, new_name)}
    elif cmd == "workspace-symbols":
        query = req.get("query", "")
        return {"result": client.workspace_symbols(query)}
    else:
        return {"error": f"Unknown command: {cmd}"}


# ---------------------------------------------------------------------------
# Client: connect to daemon (start it if needed)
# ---------------------------------------------------------------------------

def _ensure_daemon():
    sock_path = _sock_path()
    pid_path = sock_path + ".pid"

    if os.path.exists(pid_path):
        try:
            pid = int(Path(pid_path).read_text().strip())
            os.kill(pid, 0)
            result = _send_to_daemon({"command": "ping"})
            if result and result.get("result") == "pong":
                return True
        except (OSError, ValueError, ConnectionRefusedError):
            pass

    for f in [sock_path, pid_path]:
        if os.path.exists(f):
            os.unlink(f)

    pid = os.fork()
    if pid == 0:
        os.setsid()
        devnull = os.open(os.devnull, os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.close(devnull)
        _run_daemon()
        sys.exit(0)
    else:
        for _ in range(50):
            time.sleep(0.1)
            if os.path.exists(sock_path):
                try:
                    result = _send_to_daemon({"command": "ping"})
                    if result and result.get("result") == "pong":
                        return True
                except Exception:
                    continue
        print("Warning: daemon did not start in time", file=sys.stderr)
        return False


def _send_to_daemon(request):
    sock_path = _sock_path()
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.settimeout(30)
    conn.connect(sock_path)
    try:
        data = json.dumps(request).encode("utf-8") + b"\n\n"
        conn.sendall(data)
        response = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            response += chunk
        return json.loads(response.decode("utf-8"))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

USAGE = """Usage: lsp-query <command> [args...]

Navigation:
  definition <file> <line> <col>          Go to definition
  references <file> <line> <col>          Find all references
  hover <file> <line> <col>               Type/docstring info
  symbols <file>                          List document symbols
  diagnostics <file>                      Show errors/warnings
  completions <file> <line> <col>         Code completions
  signature <file> <line> <col>           Function signature help
  rename <file> <line> <col> <new_name>   Preview rename
  workspace-symbols <query>               Search symbols across workspace

Management:
  languages                               Show supported languages + install status
  servers                                 List running language server daemons
  shutdown [language]                     Stop one or all daemons

Lines and columns are 1-indexed. Language is auto-detected from file extension.

Supported: python, typescript/js, rust, go, c/c++, bash, java, css, html, json

Environment:
  LSP_WORKSPACE   Workspace root (default: git root or cwd)
  LSP_SERVER      Override server command for all languages
  LSP_LANG        Force a specific language (bypass auto-detection)
  LSP_TIMEOUT     Daemon idle timeout in seconds (default: 300)
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd in ("-h", "--help", "help"):
        print(USAGE)
        return

    if cmd == "daemon":
        _run_daemon()
        return

    if cmd == "languages":
        _ensure_daemon()
        result = _send_to_daemon({"command": "languages"})
        print(result.get("result", result.get("error", "")))
        return

    if cmd == "servers":
        try:
            result = _send_to_daemon({"command": "servers"})
            print(result.get("result", result.get("error", "")))
        except Exception:
            print("No daemon running")
        return

    if cmd == "shutdown":
        lang = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            result = _send_to_daemon({"command": "shutdown", "language": lang})
            print(result.get("result", result.get("error", "")))
        except Exception:
            print("No daemon running")
        return

    _ensure_daemon()

    request = {"command": cmd}

    if cmd in ("definition", "references", "hover", "completions", "signature"):
        if len(sys.argv) < 5:
            print(f"Usage: lsp-query {cmd} <file> <line> <col>")
            sys.exit(1)
        request["file"] = os.path.abspath(sys.argv[2])
        request["line"] = int(sys.argv[3])
        request["col"] = int(sys.argv[4])

    elif cmd == "rename":
        if len(sys.argv) < 6:
            print(f"Usage: lsp-query {cmd} <file> <line> <col> <new_name>")
            sys.exit(1)
        request["file"] = os.path.abspath(sys.argv[2])
        request["line"] = int(sys.argv[3])
        request["col"] = int(sys.argv[4])
        request["new_name"] = sys.argv[5]

    elif cmd in ("symbols", "diagnostics"):
        if len(sys.argv) < 3:
            print(f"Usage: lsp-query {cmd} <file>")
            sys.exit(1)
        request["file"] = os.path.abspath(sys.argv[2])

    elif cmd == "workspace-symbols":
        if len(sys.argv) < 3:
            print(f"Usage: lsp-query {cmd} <query>")
            sys.exit(1)
        request["query"] = sys.argv[2]

    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)
        sys.exit(1)

    try:
        result = _send_to_daemon(request)
    except ConnectionRefusedError:
        print("Error: could not connect to LSP daemon", file=sys.stderr)
        sys.exit(1)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(result.get("result", ""))


if __name__ == "__main__":
    main()
