#!/usr/bin/env python3
"""
Serve HTML and generate screenshot using local HTTP server
"""

import http.server
import socketserver
import threading
import time
import sys
from pathlib import Path

PORT = 8765

def start_server(directory):
    """Start a simple HTTP server"""
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.directory = directory
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✓ Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, args=(str(output_dir),), daemon=True)
    server_thread.start()
    
    time.sleep(1)
    
    print(f"\n📸 Ready for screenshots!")
    print(f"Access files at: http://localhost:{PORT}/")
    print(f"\nPress Ctrl+C to stop server...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
