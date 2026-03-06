# ORGO ACTION PATTERNS

Reusable recipes built on top of `orgo_client.py`. Each pattern is a copy-paste-ready sequence for a common agent task. For raw API reference see `SKILL.md`; for implementation details see `orgo_client.py`.

---

## 1. Browser Automation Pattern

Open a URL, wait for the page to load, screenshot, then interact.

```python
import os
from orgo_client import OrgoClient

client = OrgoClient(api_key=os.environ["ORGO_API_KEY"])
ws = client.create_workspace("browser-agent")
computer = client.create_computer(
    workspace_id=ws.id,
    name="browser-1",
    wait_until_ready=True,
)

# Open URL via bash (faster than clicking the address bar)
computer.run_bash("xdg-open 'https://example.com'")
computer.wait(3.0)  # let the page render

img = computer.screenshot()
# … pass img to a vision model, then interact …
computer.click(760, 400)
computer.type("search query")
computer.key("Enter")
computer.wait(2.0)
computer.save_screenshot("result.png")

computer.stop()
```

**Login flow variant:**

```python
computer.run_bash("xdg-open 'https://app.example.com/login'")
computer.wait(3.0)
computer.click(760, 330)        # username field
computer.type("user@example.com")
computer.key("Tab")
computer.type("password123")
computer.key("Enter")
computer.wait(2.0)
img = computer.screenshot()     # verify logged-in state
```

---

## 2. Screenshot-Driven Decision Loop

The canonical perception → action loop for open-ended UI tasks.  
**Never assume UI state** — always re-screenshot after each action.

```python
import base64

MAX_STEPS = 20

for step in range(MAX_STEPS):
    img_b64 = computer.screenshot()           # base-64 data-URI string
    png_bytes = computer.screenshot(decode=True)  # raw PNG bytes (for vision APIs)

    # --- pass png_bytes to your vision/LLM layer ---
    action = decide_next_action(png_bytes)    # returns dict or None

    if action is None or action["type"] == "done":
        break
    elif action["type"] == "click":
        computer.click(action["x"], action["y"])
    elif action["type"] == "type":
        computer.type(action["text"])
    elif action["type"] == "key":
        computer.key(action["key"])
    elif action["type"] == "scroll":
        computer.scroll(action["direction"], amount=action.get("amount", 3))

    computer.wait(1.0)   # let UI settle; max 60 s per call
```

Key details from the SDK:
- `screenshot()` returns a base-64 data-URI string by default.
- `screenshot(decode=True)` returns raw PNG `bytes` (strips the data-URI prefix automatically).
- `wait(duration)` is an on-device pause; max 60 seconds — split longer waits across multiple calls.

---

## 3. File Workflow Patterns

### Upload → process → export

```python
import urllib.request

# 1. Upload a local file to the workspace
client.upload_file("input.csv", ws.id, computer_id=computer.id)

# 2. Process it on the VM
computer.run_bash("python3 -c \""
    "import csv; "
    "rows = list(csv.reader(open('/root/input.csv'))); "
    "open('/root/output.txt','w').write(str(len(rows))+' rows')"
    "\"")

# 3. Export the result back to local disk
file_record, download_url = computer.export_file("output.txt")
# download_url is a signed URL (expires ~1 hour)
urllib.request.urlretrieve(download_url, "output.txt")
print(f"Exported file id: {file_record.id}, name: {file_record.filename}")
```

### Download a previously exported file by ID

```python
url = client.download_file_url(file_record.id)   # signed URL, ~1 hour TTL
urllib.request.urlretrieve(url, "local_copy.txt")
```

### List and clean up files

```python
files = computer.list_files(ws.id)   # list[dict] for this computer
for f in files:
    client.delete_file(f["id"])
```

---

## 4. Safe Teardown Patterns

### Preferred: context manager (auto-stops, never deletes)

`OrgoComputer.__exit__` calls `stop()` — state is preserved for the next session.

```python
with client.create_computer(workspace_id=ws.id, name="agent-1",
                             wait_until_ready=True) as computer:
    computer.run_bash("echo hello")
    computer.save_screenshot("done.png")
# computer.stop() is called automatically; computer still exists
```

### Stop vs. delete decision

| Situation | Action |
|-----------|--------|
| Done for now, resuming later | `computer.stop()` |
| Job finished, VM no longer needed | `computer.stop()` then `computer.delete(force=True)` |
| Entire project teardown | `client.delete_workspace(ws.id, force=True)` |

```python
# Stop only (state preserved, billing paused)
computer.stop()

# Permanent delete — irreversible
computer.delete(force=True)

# Workspace delete — destroys ALL computers inside it
client.delete_workspace(ws.id, force=True)
```

Both `delete` calls raise `OrgoConfirmationError` if `force=True` is omitted.

### Cleanup on error

```python
computer = client.create_computer(workspace_id=ws.id, name="agent-1",
                                  wait_until_ready=True)
try:
    run_task(computer)
except Exception:
    computer.save_screenshot("error_state.png")
    raise
finally:
    computer.stop()   # always stop; never leave a computer running
```

---

## 5. Error Recovery Patterns

### Retry around OrgoTimeoutError (computer cold-start)

```python
from orgo_client import OrgoTimeoutError

computer = client.create_computer(workspace_id=ws.id, name="agent-1")
try:
    computer.wait_until_ready(timeout=180, poll_interval=5.0)
except OrgoTimeoutError:
    computer.restart()
    computer.wait_until_ready(timeout=120)   # one more chance
```

`wait_until_ready` uses adaptive polling internally (doubles interval every 5 polls, capped at 15 s).

### Re-screenshot after OrgoError

If an action fails mid-task, capture the screen before deciding to retry or abort:

```python
from orgo_client import OrgoError

try:
    computer.click(760, 400)
    computer.type("hello")
    computer.key("Enter")
except OrgoError as exc:
    img = computer.screenshot()
    # inspect img to decide whether to retry or escalate
    raise
```

### Handle stale UI state

```python
computer.wait(2.0)
img = computer.screenshot()

if is_loading_spinner_visible(img):
    computer.wait(5.0)
    img = computer.screenshot()   # re-check before acting

if is_error_dialog_visible(img):
    computer.key("Escape")
    computer.wait(1.0)
    # resume from a known-good state
```

### Bash failure guard

`run_bash` raises `OrgoError` automatically when `success=False`:

```python
from orgo_client import OrgoError

try:
    result = computer.run_bash("pip install pandas")
except OrgoError as exc:
    # exc message contains the captured stderr/stdout
    computer.run_bash("pip install --upgrade pip && pip install pandas")
```

---

## 6. Multi-Computer Orchestration

### Fan out to parallel computers

```python
import concurrent.futures

TASKS = ["task_a.py", "task_b.py", "task_c.py"]

def run_on_computer(task_script: str) -> str:
    computer = client.create_computer(
        workspace_id=ws.id,
        name=task_script.replace(".py", ""),
        wait_until_ready=True,
    )
    try:
        client.upload_file(task_script, ws.id, computer_id=computer.id)
        result = computer.run_python(open(task_script).read(), timeout=60)
        return result.output
    finally:
        computer.stop()

with concurrent.futures.ThreadPoolExecutor(max_workers=len(TASKS)) as pool:
    outputs = list(pool.map(run_on_computer, TASKS))
```

### Inspect existing computers before creating more

```python
computers = client.list_computers(ws.id)   # list[ComputerInfo]
running = [c for c in computers if c.status == "running"]

if len(running) >= 4:
    # reuse an existing one instead of creating a new computer
    computer = client.get_computer(running[0].id)
else:
    computer = client.create_computer(workspace_id=ws.id, name="new-worker",
                                      wait_until_ready=True)
```

`ComputerInfo` fields: `id`, `name`, `workspace_id`, `status`, `os`, `ram`, `cpu`, `gpu`, `url`, `created_at`.

---

## 7. Long-Running Task Patterns

### Poll a bash job via run_bash

`run_bash` blocks until the command exits. For long commands, run them in the background and poll:

```python
# Start the job in the background, write output to a log
computer.run_bash("nohup python3 train.py > /tmp/train.log 2>&1 &")

# Poll for completion
import time
for _ in range(60):
    result = computer.run_bash("pgrep -f train.py && echo running || echo done")
    if "done" in result.output:
        break
    time.sleep(10)

log = computer.run_bash("cat /tmp/train.log").output
file_record, url = computer.export_file("model.pkl")
```

### Monitor an RTMP stream

```python
from orgo_client import StreamStatus

computer.stream_start("my-rtmp-connection")

# Poll stream health
for _ in range(10):
    status: StreamStatus = computer.stream_status()
    # status.status is one of: "idle" | "streaming" | "terminated"
    if status.status == "streaming":
        print(f"Live since {status.start_time}, pid={status.pid}")
        break
    computer.wait(3.0)

# … later …
computer.stream_stop()
```

---

## 8. Coordinate Anchoring

Pixel coordinates are screen-absolute. The Orgo Linux desktop is typically **1920 × 1080**.

### Principles

- **Always screenshot first** — derive coordinates from the current frame, not hardcoded values.
- Use `run_bash` with `xdotool` or `wmctrl` to get window positions programmatically when precision matters.
- Prefer keyboard shortcuts (`computer.key("ctrl+l")` for address bar) over clicking hardcoded positions.

### Common reference points (1920×1080 desktop)

| Element | Approximate coordinates |
|---------|------------------------|
| Screen center | `(960, 540)` |
| Top taskbar | y ≈ `20` |
| Browser address bar (maximised) | `(760, 45)` |
| Desktop background | `(960, 600)` |

### Derive coordinates at runtime

```python
# Take a screenshot and locate an element before clicking
img_bytes = computer.screenshot(decode=True)
x, y = find_element_center(img_bytes, label="Submit button")  # your vision fn
computer.click(x, y)
```

### Drag example (move a window)

```python
# Drag the title bar of a window from one position to another
computer.drag(
    start_x=400, start_y=30,
    end_x=800,   end_y=30,
    duration=0.5,           # smooth drag over 0.5 s
)
```
