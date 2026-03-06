# native_run.py – a tiny HTTP server that runs shell commands
# Put this next to skill.md / task.yml

import http.server
import json
import subprocess
from urllib.parse import urlparse, parse_qs

# ---------------------------------
PORT =  8080                      # matches the URL you hit from your WA/webchat
TOKEN = "272d22dec98da63a3362c6dc0a9c0eebf2aa9ed96d21775d"     # keep the same token you used in the earlier snippet
# ---------------------------------

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Health‑check endpoint
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"native-run online")


    def do_POST(self):
        # Verify the token
        qs = urlparse(self.path).query
        if parse_qs(qs).get("token", [None])[0] != TOKEN:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        # Grab the JSON body
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))

        if not payload.get("task") == "native_run" or "command" not in payload:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return

        # Run the command
        try:
            output = subprocess.check_output(
                payload["command"],
                shell=True,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            output = f"❌ {e.output}"

        self.send_response(200)
        self.end_headers()
        self.wfile.write(output.encode())

if __name__ == "__main__":
    httpd = http.server.HTTPServer(("localhost", PORT), Handler)
    print(f"✅  Running native runner on http://localhost:{PORT}")
    httpd.serve_forever()