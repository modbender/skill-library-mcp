---
name: orgo-desktop-control
description: Provision and control Orgo cloud computers using the orgo_client Python SDK. Use when launching remote desktops, automating browsers, running bash/python remotely, interacting with UI, managing files, or controlling streaming.
compatibility: Requires internet access and ORGO_API_KEY.
metadata:
  author: custom
  version: "1.0.0"
---

# Orgo Desktop Control Skill (Python SDK)

This skill uses `orgo_client.py` to create and control Orgo cloud computers safely.

Always use the SDK — do NOT manually construct HTTP requests.

---

# When to Use This Skill

Activate when user requests:

- Launch a remote desktop
- Automate browser or UI
- Click, drag, type, scroll
- Execute bash or Python remotely
- Take screenshots
- Upload/export files
- Start/stop/restart environments
- Stream desktop output
- Access VNC credentials
- Build a computer-use agent

Do NOT activate for local-only code.

---

# High-Level Workflow

1. Instantiate client
2. Ensure workspace exists
3. Create computer
4. `wait_until_ready()`
5. Perform actions
6. Export results
7. Stop computer

---

# Initialization

```python
from orgo_client import OrgoClient

client = OrgoClient(api_key=os.environ["ORGO_API_KEY"])
```

---

# Workspace Management

Create:
```python
ws = client.create_workspace("browser-agent")
```

List:
```python
client.list_workspaces()
```

Delete (requires force):
```python
client.delete_workspace(ws.id, force=True)
```

Never delete without explicit user confirmation.

---

# Computer Lifecycle

Create:
```python
computer = client.create_computer(
    workspace_id=ws.id,
    name="agent-1",
    ram=4,
    cpu=2,
    wait_until_ready=True
)
```

Manual wait:
```python
computer.start()
computer.stop()
computer.restart()
```

Start / Stop / Restart:
```python
computer.start()
computer.stop()
computer.restart()
```

Delete (irreversible):
```python
computer.delete(force=True)
```

Always stop computers when idle.

---

# UI Interaction

Click:
```python
computer.click(100, 200)
```

Right-click:
```python
computer.right_click(100, 200)
```

Double-click:
```python
computer.double_click(100, 200)
```

Drag:
```python
computer.drag(100, 200, 400, 500)
```

Scroll:
```python
computer.scroll("down", amount=3)
```

Type:
```python
computer.type("Hello world")
```

Key:
```python
computer.key("Enter")
computer.key("ctrl+c")
```

Wait:
```python
computer.wait(2.0)
```

---

# Screenshots

```python
img_b64 = computer.screenshot()
```

Save to file:
```python
computer.save_screenshot("screen.png")
```

---

# Execution

Bash:
```python
result = computer.run_bash("ls -la")
print(result.output)
```

Python:
```python
result = computer.run_python("print('hi')")
```

Errors raise OrgoError subclasses automatically.

---

# Streaming

Start:
```python
computer.stream_start("my-rtmp-connection")
```

Status:
```python
computer.stream_status()
```

Stop:
```python
computer.stream_stop()
```

---

# VNC

```python
password = computer.vnc_password()
```

---

# Files

Upload:
```python
client.upload_file("local.txt", ws.id, computer_id=computer.id)
```

Export from VM:
```python
file_record, url = computer.export_file("Desktop/output.txt")
```

List:
```python
computer.list_files(ws.id)
```

Delete:
```python
client.delete_file(file_id)
```

---

# Error Handling

All errors raise typed exceptions:
* OrgoAuthError
*	OrgoForbiddenError
*	OrgoNotFoundError
*	OrgoBadRequestError
*	OrgoServerError
*	OrgoTimeoutError
*	OrgoConfirmationError

Always handle destructive confirmations explicitly.

# Recommended Automation Loop

For UI tasks:
1. screenshot()
2. analyze state
3. click / type / drag
4. wait()
5. screenshot()
6. repeat

Never assume UI state.

---

# Efficiency Rules

* Use minimal RAM/CPU
* Stop instead of delete if continuing later
* Use wait_until_ready() instead of manual polling
* Avoid unnecessary screenshots
* Prefer run_bash over UI when possible

---

# End of Skill

