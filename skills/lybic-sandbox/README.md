# Lybic Skill

An Agent Skill that provides AI agents with the ability to control Lybic cloud sandboxes through the Python SDK.

## Overview

This skill enables agents to:

1. **Sandbox Management**
   - Create, list, get, and delete sandboxes
   - Support for Windows, Linux, and Android sandboxes
   - Monitor sandbox state and lifecycle

2. **GUI Automation**
   - **Computer Use**: Mouse and keyboard operations for desktop (Windows/Linux)
   - **Mobile Use**: Touch operations for mobile (Android)
   - Screenshot capture and visual feedback

3. **Code Execution**
   - Run Python, Node.js, Go, Rust, Java, and other languages
   - Execute shell commands and scripts
   - Support for long-running processes

4. **File Operations**
   - Download files from URLs into sandbox
   - Upload/download files between sandbox and external storage
   - Copy files within sandbox

5. **Network Features**
   - HTTP port mapping for web services
   - Forward sandbox ports to public URLs

6. **Project Management**
   - Create and manage projects
   - Organize sandboxes by project

## Installation

### Prerequisites

- Python 3.10 or higher
- A lybic account with API key

### Setup

1. Install the Lybic Python SDK:
```bash
pip install lybic
```

2. Set up your Lybic credentials:
```bash
export LYBIC_ORG_ID="your_org_id"
export LYBIC_API_KEY="your_api_key"
```

Or configure in code:
```python
from lybic import LybicClient, LybicAuth

client = LybicClient(
    LybicAuth(
        org_id="your_org_id",
        api_key="your_api_key",
        endpoint="https://api.lybic.cn"
    )
)
```

## Usage Examples

### Create a Sandbox

```python
from lybic import LybicClient

async with LybicClient() as client:
    sandbox = await client.sandbox.create(
        name="my-workspace",
        shape="beijing-2c-4g-cpu-linux",  # linux sandbox with 2 vCPU and 4GB RAM
        maxLifeSeconds=7200     # 2 hours
    )
    print(f"Sandbox ID: {sandbox.id}")
```

### Execute GUI Actions

```python
# Click at coordinates
await client.sandbox.execute_sandbox_action(
    sandbox_id="SBX-xxxx",
    action={
        "type": "mouse:click",
        "x": {"type": "/", "numerator": 1, "denominator": 2},
        "y": {"type": "/", "numerator": 1, "denominator": 2},
        "button": 1
    }
)

# Type text
await client.sandbox.execute_sandbox_action(
    sandbox_id="SBX-xxxx",
    action={
        "type": "keyboard:type",
        "content": "Hello, Lybic!"
    }
)
```

### Run Code in Sandbox

```python
import base64

# Execute Python code
code = "print('Hello from sandbox!')"
result = await client.sandbox.execute_process(
    sandbox_id="SBX-xxxx",
    executable="python3",
    stdinBase64=base64.b64encode(code.encode()).decode()
)

output = base64.b64decode(result.stdoutBase64).decode()
print(output)
```

### Take Screenshot

```python
url, image, base64_str = await client.sandbox.get_screenshot(
    sandbox_id="SBX-xxxx"
)
image.show()  # Display with PIL
```

### Download File into Sandbox

```python
from lybic.dto import FileCopyItem, HttpGetLocation, SandboxFileLocation

await client.sandbox.copy_files(
    sandbox_id="SBX-xxxx",
    files=[
        FileCopyItem(
            id="download-dataset",
            src=HttpGetLocation(url="https://example.com/data.csv"),
            dest=SandboxFileLocation(path="/home/agent/data.csv")
        )
    ]
)
```

## Action Types Reference

### Computer Use (Desktop)

**Mouse Actions:**
- `mouse:click` - Click at coordinates
- `mouse:doubleClick` - Double-click
- `mouse:tripleClick` - Triple-click
- `mouse:move` - Move cursor
- `mouse:drag` - Drag from start to end
- `mouse:scroll` - Scroll wheel

**Keyboard Actions:**
- `keyboard:type` - Type text
- `keyboard:hotkey` - Press hotkey combination (e.g., "ctrl+c")
- `key:down` / `key:up` - Press/release single key

**Common Actions:**
- `screenshot` - Take screenshot
- `wait` - Wait for duration
- `finished` - Mark task complete
- `failed` - Mark task failed

### Mobile Use (Android)

**Touch Actions:**
- `touch:tap` - Tap at coordinates
- `touch:longPress` - Long press
- `touch:drag` - Drag gesture
- `touch:swipe` - Swipe in direction

**System Actions:**
- `android:back` - Press back button
- `android:home` - Press home button

**App Management:**
- `os:startApp` - Start app by package name
- `os:startAppByName` - Start app by display name
- `os:closeApp` - Close app by package name
- `os:closeAppByName` - Close app by display name
- `os:listApps` - List installed apps

## Coordinate Systems

Lybic supports two coordinate formats:

1. **Fractional** (recommended for resolution independence):
```python
{"type": "/", "numerator": 500, "denominator": 1000}  # 50% of screen
```

2. **Pixel** (absolute positioning):
```python
{"type": "px", "value": 500}
```

## Environment Variables

- `LYBIC_ORG_ID` - Your Lybic organization ID
- `LYBIC_API_KEY` - Your Lybic API key
- `LYBIC_API_ENDPOINT` - API endpoint (default: https://api.lybic.cn)

## Supported Languages in Sandbox

- Python 3.12 (Linux) / 3.13 (Windows)
- Node.js v24
- Go 1.25
- Rust 1.92
- Java 25
- GCC 13 (Linux) / MSVC 14.50 (Windows)

## Documentation

For detailed API documentation, visit:
- [Lybic Documentation](https://docs.lybic.cn)
- [Python SDK Reference](https://docs.lybic.cn/en/sdk/python)
- [Sandbox Actions](https://docs.lybic.cn/en/sandbox/action)

## License

MIT
