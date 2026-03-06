#!/usr/bin/env python3
"""
Python LSP Client - Simple wrapper for pylsp interactions

Usage:
    python lsp-python.py <command> [args]
    
Commands:
    init <file_path>     - Initialize LSP session for a file
    completion <file> <line> <char> - Get completions
    diagnostics <file>   - Get diagnostics/errors
    hover <file> <line> <char> - Get hover info
    definition <file> <line> <char> - Go to definition
"""

import json
import subprocess
import sys
import os
from pathlib import Path

LSP_TIMEOUT = 5

def send_request(pylsp, request, timeout=5):
    """Send JSON-RPC request to pylsp"""
    import time
    
    content = json.dumps(request)
    header = f"Content-Length: {len(content)}\r\n\r\n"
    pylsp.stdin.write(header.encode() + content.encode())
    pylsp.stdin.flush()
    
    # Read response headers
    content_length = 0
    start = time.time()
    while time.time() - start < timeout:
        line = pylsp.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        if line.startswith(b'Content-Length:'):
            content_length = int(line.split(b':')[1].strip())
        if line == b'\r\n':
            break
    
    if content_length == 0:
        return None
    
    # Read response body
    response = pylsp.stdout.read(content_length).decode()
    return json.loads(response)

def lsp_init(pylsp, root_path):
    """Initialize LSP session"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": os.getpid(),
            "rootUri": f"file://{root_path}",
            "capabilities": {
                "textDocument": {
                    "completion": {"dynamicRegistration": True},
                    "hover": {"dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True}
                }
            },
            "trace": "off"
        }
    }
    return send_request(pylsp, request)

def lsp_open_file(pylsp, file_path, content):
    """Notify server that file is open"""
    request = {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": f"file://{file_path}",
                "languageId": "python",
                "version": 1,
                "text": content
            }
        }
    }
    pylsp.stdin.write((f"Content-Length: {len(json.dumps(request))}\r\n\r\n" + json.dumps(request)).encode())
    pylsp.stdin.flush()

def lsp_completion(pylsp, file_path, line, char):
    """Get code completions"""
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "textDocument/completion",
        "params": {
            "textDocument": {"uri": f"file://{file_path}"},
            "position": {"line": line, "character": char}
        }
    }
    return send_request(pylsp, request)

def lsp_diagnostics(pylsp, file_path):
    """Get diagnostics (errors/warnings)"""
    # Diagnostics are pushed by server, we need to wait or check publishDiagnostics
    # For now, request it via workspace diagnostic pull if supported
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "textDocument/diagnostic",
        "params": {
            "textDocument": {"uri": f"file://{file_path}"}
        }
    }
    return send_request(pylsp, request)

def lsp_hover(pylsp, file_path, line, char):
    """Get hover information"""
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "textDocument/hover",
        "params": {
            "textDocument": {"uri": f"file://{file_path}"},
            "position": {"line": line, "character": char}
        }
    }
    return send_request(pylsp, request)

def lsp_definition(pylsp, file_path, line, char):
    """Go to definition"""
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "textDocument/definition",
        "params": {
            "textDocument": {"uri": f"file://{file_path}"},
            "position": {"line": line, "character": char}
        }
    }
    return send_request(pylsp, request)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Start pylsp process
    pylsp = subprocess.Popen(
        ["pylsp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )
    
    try:
        if command == "init":
            file_path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
            result = lsp_init(pylsp, file_path)
            print(json.dumps(result, indent=2))
        
        elif command == "completion":
            if len(sys.argv) < 5:
                print("Usage: lsp-python.py completion <file> <line> <char>")
                sys.exit(1)
            file_path = os.path.abspath(sys.argv[2])
            line = int(sys.argv[3])
            char = int(sys.argv[4])
            content = Path(file_path).read_text()
            lsp_init(pylsp, os.path.dirname(file_path))
            lsp_open_file(pylsp, file_path, content)
            result = lsp_completion(pylsp, file_path, line, char)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "diagnostics":
            if len(sys.argv) < 3:
                print("Usage: lsp-python.py diagnostics <file>")
                sys.exit(1)
            file_path = os.path.abspath(sys.argv[2])
            content = Path(file_path).read_text()
            lsp_init(pylsp, os.path.dirname(file_path))
            lsp_open_file(pylsp, file_path, content)
            # Wait a bit for diagnostics
            import time
            time.sleep(1)
            result = lsp_diagnostics(pylsp, file_path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "hover":
            if len(sys.argv) < 5:
                print("Usage: lsp-python.py hover <file> <line> <char>")
                sys.exit(1)
            file_path = os.path.abspath(sys.argv[2])
            line = int(sys.argv[3])
            char = int(sys.argv[4])
            content = Path(file_path).read_text()
            lsp_init(pylsp, os.path.dirname(file_path))
            lsp_open_file(pylsp, file_path, content)
            result = lsp_hover(pylsp, file_path, line, char)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "definition":
            if len(sys.argv) < 5:
                print("Usage: lsp-python.py definition <file> <line> <char>")
                sys.exit(1)
            file_path = os.path.abspath(sys.argv[2])
            line = int(sys.argv[3])
            char = int(sys.argv[4])
            content = Path(file_path).read_text()
            lsp_init(pylsp, os.path.dirname(file_path))
            lsp_open_file(pylsp, file_path, content)
            result = lsp_definition(pylsp, file_path, line, char)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
    
    finally:
        # Shutdown gracefully
        shutdown_req = {"jsonrpc": "2.0", "id": 99, "method": "shutdown", "params": {}}
        pylsp.stdin.write((f"Content-Length: {len(json.dumps(shutdown_req))}\r\n\r\n" + json.dumps(shutdown_req)).encode())
        pylsp.stdin.flush()
        pylsp.terminate()
        pylsp.wait(timeout=2)

if __name__ == "__main__":
    main()
