import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from bark_push.bark_api import BarkClient


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        data = json.loads(raw) if raw else {}
        body = json.dumps({"code": 200, "message": "success", "echo": data}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class TestBarkClient(unittest.TestCase):
    def test_push_json(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _Handler)
        host, port = server.server_address
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            client = BarkClient(base_url=f"http://{host}:{port}")
            resp = client.push_json({"device_key": "k", "_use_push_path": True, "body": "hi"})
            self.assertTrue(resp.ok)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data["code"], 200)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
