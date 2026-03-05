"""Windows 桌面远程控制 FastAPI 服务"""

import base64
import io
import secrets
import signal
import sys
import os
from pathlib import Path

import mss
import pyautogui
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from PIL import Image
from pydantic import BaseModel

pyautogui.FAILSAFE = False

app = FastAPI(title="PC Control Server")
security = HTTPBearer()

AUTH_TOKEN = secrets.token_urlsafe(32)
AUTH_TOKEN_FILE = Path(__file__).parent.parent / ".auth_token"


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Models ---

class MouseMove(BaseModel):
    x: int
    y: int

class MouseClick(BaseModel):
    x: int
    y: int
    button: str = "left"
    clicks: int = 1

class MouseScroll(BaseModel):
    x: int
    y: int
    clicks: int

class MouseDrag(BaseModel):
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    duration: float = 0.5

class KeyboardType(BaseModel):
    text: str
    interval: float = 0.02

class KeyboardPress(BaseModel):
    key: str

class KeyboardHotkey(BaseModel):
    keys: list[str]


# --- Endpoints ---

@app.get("/status")
def status():
    screen = pyautogui.size()
    return {"status": "ok", "screen": {"width": screen.width, "height": screen.height}}


@app.post("/screenshot")
def screenshot(
    quality: int = Query(50, ge=1, le=100),
    scale: float = Query(0.5, gt=0, le=1.0),
    _=Depends(verify_token),
):
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # 全屏
        img = sct.grab(monitor)

    image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

    if scale != 1.0:
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {"base64": b64, "width": image.width, "height": image.height}


@app.post("/mouse/move")
def mouse_move(data: MouseMove, _=Depends(verify_token)):
    pyautogui.moveTo(data.x, data.y)
    return {"ok": True}


@app.post("/mouse/click")
def mouse_click(data: MouseClick, _=Depends(verify_token)):
    pyautogui.click(data.x, data.y, button=data.button, clicks=data.clicks)
    return {"ok": True}


@app.post("/mouse/scroll")
def mouse_scroll(data: MouseScroll, _=Depends(verify_token)):
    pyautogui.moveTo(data.x, data.y)
    pyautogui.scroll(data.clicks)
    return {"ok": True}


@app.post("/mouse/drag")
def mouse_drag(data: MouseDrag, _=Depends(verify_token)):
    pyautogui.moveTo(data.from_x, data.from_y)
    pyautogui.drag(
        data.to_x - data.from_x,
        data.to_y - data.from_y,
        duration=data.duration,
    )
    return {"ok": True}


@app.post("/keyboard/type")
def keyboard_type(data: KeyboardType, _=Depends(verify_token)):
    pyautogui.typewrite(data.text, interval=data.interval) if data.text.isascii() else pyautogui.write(data.text)
    return {"ok": True}


@app.post("/keyboard/press")
def keyboard_press(data: KeyboardPress, _=Depends(verify_token)):
    pyautogui.press(data.key)
    return {"ok": True}


@app.post("/keyboard/hotkey")
def keyboard_hotkey(data: KeyboardHotkey, _=Depends(verify_token)):
    pyautogui.hotkey(*data.keys)
    return {"ok": True}


@app.post("/shutdown")
def shutdown(_=Depends(verify_token)):
    os.kill(os.getpid(), signal.SIGINT)
    return {"ok": True, "message": "shutting down"}


def main():
    AUTH_TOKEN_FILE.write_text(AUTH_TOKEN)
    print(f"Auth token written to {AUTH_TOKEN_FILE}")
    print(f"Server starting on http://127.0.0.1:18888")
    uvicorn.run(app, host="127.0.0.1", port=18888, log_level="warning")


if __name__ == "__main__":
    main()
