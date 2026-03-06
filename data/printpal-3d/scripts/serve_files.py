#!/usr/bin/env python3
"""
Simple HTTP file server for serving generated PrintPal files.

Starts a local HTTP server to serve files from the output directory,
making them downloadable via clickable URLs in chat.
"""

import argparse
import os
import sys
import socket
from pathlib import Path

def find_available_port(start_port=8765, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def start_server(directory, port=None, host="0.0.0.0"):
    """Start HTTP server serving files from directory."""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    directory = Path(directory).resolve()
    os.chdir(directory)
    
    if port is None:
        port = find_available_port()
        if port is None:
            print("Error: Could not find available port", file=sys.stderr)
            sys.exit(1)
    
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    
    print(f"Serving files from: {directory}")
    print(f"Server running at: http://{host}:{port}")
    print(f"Local access: http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    parser = argparse.ArgumentParser(
        description="Start HTTP file server for PrintPal output files"
    )
    parser.add_argument(
        "--directory", "-d",
        default=os.environ.get("PRINTPAL_OUTPUT_DIR", str(Path(__file__).resolve().parent.parent.parent / "printpal-output")),
        help="Directory to serve files from (default: ./printpal-output or PRINTPAL_OUTPUT_DIR)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8765,
        help="Port to run server on (default: 8765)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 - localhost only for security)"
    )
    parser.add_argument(
        "--url-only",
        action="store_true",
        help="Just print the URL and exit (don't start server)"
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Bind to 0.0.0.0 to allow network access (default is localhost only)"
    )
    
    args = parser.parse_args()
    
    # Handle --public flag
    host = "0.0.0.0" if args.public else args.host
    
    directory = Path(args.directory)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    
    if args.url_only:
        port = args.port
        local_ip = get_local_ip()
        print(f"http://localhost:{port}")
        print(f"http://{local_ip}:{port}")
        return
    
    start_server(directory, args.port, host)

if __name__ == "__main__":
    main()
