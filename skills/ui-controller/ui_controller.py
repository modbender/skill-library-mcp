import sys
import json
import pyautogui

data = sys.stdin.read()

if not data.strip():
    sys.exit(0)

cmd = json.loads(data)

action = cmd.get("action")

if action == "click":
    x = int(cmd["x"])
    y = int(cmd["y"])
    pyautogui.click(x, y)

elif action == "move":
    x = int(cmd["x"])
    y = int(cmd["y"])
    pyautogui.moveTo(x, y, duration=0.2)

elif action == "type":
    text = cmd["text"]
    pyautogui.write(text, interval=0.02)

elif action == "hotkey":
    keys = cmd["keys"]
    pyautogui.hotkey(*keys)

else:
    print("Unknown action", file=sys.stderr)
