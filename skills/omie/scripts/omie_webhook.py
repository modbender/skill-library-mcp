#!/usr/bin/env python3
"""Omie ERP Webhook Receiver."""

import json
import sys
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class OmieWebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for Omie webhooks."""
    
    def do_POST(self):
        """Handle POST requests from Omie."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            event_type = payload.get('event', 'unknown')
            timestamp = datetime.now().isoformat()
            
            # Log event
            log_entry = {
                "timestamp": timestamp,
                "event": event_type,
                "data": payload
            }
            
            print(json.dumps(log_entry, indent=2, ensure_ascii=False), file=sys.stderr)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "received",
                "event": event_type,
                "timestamp": timestamp
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start the webhook receiver."""
    parser = argparse.ArgumentParser(description='Omie ERP Webhook Receiver')
    parser.add_argument('--port', type=int, default=8089, help='Port to listen on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    
    args = parser.parse_args()
    
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, OmieWebhookHandler)
    
    print(f"Omie Webhook Receiver listening on {args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    main()
