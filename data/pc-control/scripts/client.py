"""WSL 端 Python 客户端，封装 PC Control 所有 API 调用"""

import base64
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json


class PCControl:
    def __init__(self, host="127.0.0.1", port=18888, token_file=None):
        self.base_url = f"http://{host}:{port}"
        token_path = Path(token_file) if token_file else Path(__file__).parent.parent / ".auth_token"
        self.token = token_path.read_text().strip()

    def _request(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        if not path.startswith("/status"):
            req.add_header("Authorization", f"Bearer {self.token}")
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())

    def _post(self, path: str, data: dict = None) -> dict:
        return self._request("POST", path, data)

    def status(self) -> dict:
        return self._request("GET", "/status")

    def screenshot(self, scale: float = 0.5, quality: int = 50) -> str:
        """截图并保存到临时文件，返回文件路径"""
        resp = self._post(f"/screenshot?quality={quality}&scale={scale}")
        img_bytes = base64.b64decode(resp["base64"])
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(img_bytes)
        tmp.close()
        return tmp.name

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        return self._post("/mouse/click", {"x": x, "y": y, "button": button, "clicks": clicks})

    def double_click(self, x: int, y: int) -> dict:
        return self.click(x, y, clicks=2)

    def right_click(self, x: int, y: int) -> dict:
        return self.click(x, y, button="right")

    def move(self, x: int, y: int) -> dict:
        return self._post("/mouse/move", {"x": x, "y": y})

    def scroll(self, x: int, y: int, clicks: int) -> dict:
        return self._post("/mouse/scroll", {"x": x, "y": y, "clicks": clicks})

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> dict:
        return self._post("/mouse/drag", {
            "from_x": from_x, "from_y": from_y,
            "to_x": to_x, "to_y": to_y,
            "duration": duration,
        })

    def type_text(self, text: str, interval: float = 0.02) -> dict:
        return self._post("/keyboard/type", {"text": text, "interval": interval})

    def press(self, key: str) -> dict:
        return self._post("/keyboard/press", {"key": key})

    def hotkey(self, *keys: str) -> dict:
        return self._post("/keyboard/hotkey", {"keys": list(keys)})

    def shutdown(self) -> dict:
        return self._post("/shutdown")
