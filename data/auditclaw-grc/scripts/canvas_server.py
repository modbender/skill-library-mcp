#!/usr/bin/env python3
"""Lightweight static file server for OpenClaw Canvas.

Serves the ~/clawd/canvas/ directory on port 8080.
Used to make the GRC dashboard accessible via web browser.
"""

import http.server
import os
import socketserver

PORT = 8080
CANVAS_DIR = os.path.expanduser(os.environ.get("CANVAS_DIR", "~/clawd/canvas"))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves files from the canvas directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CANVAS_DIR, **kwargs)

    def log_message(self, format, *args):
        """Only log errors, not every request."""
        if args and isinstance(args[0], str) and args[0].startswith("4"):
            super().log_message(format, *args)

    def end_headers(self):
        """Add CORS and cache headers."""
        self.send_header("Access-Control-Allow-Origin", os.environ.get("CANVAS_CORS_ORIGIN", "http://localhost:8080"))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def list_directory(self, path):
        """Disable directory listing."""
        self.send_error(403, "Directory listing is not allowed")
        return None


def main():
    bind_host = os.environ.get("CANVAS_BIND_HOST", "127.0.0.1")
    with socketserver.TCPServer((bind_host, PORT), QuietHandler) as httpd:
        print(f"Canvas server running on http://{bind_host}:{PORT}")
        print(f"Serving directory: {CANVAS_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down canvas server")
            httpd.shutdown()


if __name__ == "__main__":
    main()
