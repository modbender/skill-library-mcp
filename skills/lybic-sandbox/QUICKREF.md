# Lybic SDK Quick Reference

A condensed reference for the most commonly used Lybic Python SDK operations.

## Setup

```python
import asyncio
from lybic import LybicClient

async def main():
    async with LybicClient() as client:
        # Your code here
        pass

if __name__ == '__main__':
    asyncio.run(main())
```

## Sandbox Management

```python
# Create sandbox
sandbox = await client.sandbox.create(
    name="my-sandbox",
    shape="beijing-2c-4g-cpu-linux",
    maxLifeSeconds=3600
)

# List sandboxes
sandboxes = await client.sandbox.list()

# Get sandbox details
details = await client.sandbox.get("SBX-xxxx")

# Delete sandbox
await client.sandbox.delete("SBX-xxxx")
```

## Execute Code

```python
import base64

# Python
code = "print('Hello')"
result = await client.sandbox.execute_process(
    "SBX-xxxx",
    executable="python3",
    stdinBase64=base64.b64encode(code.encode()).decode()
)
output = base64.b64decode(result.stdoutBase64).decode()

# Shell command
result = await client.sandbox.execute_process(
    "SBX-xxxx",
    executable="ls",
    args=["-la", "/home"],
    workingDirectory="/home"
)
```

## GUI Actions

### Mouse (Desktop)

```python
# Click
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "mouse:click",
    "x": {"type": "/", "numerator": 500, "denominator": 1000},
    "y": {"type": "/", "numerator": 500, "denominator": 1000},
    "button": 1
})

# Drag
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "mouse:drag",
    "startX": {"type": "px", "value": 100},
    "startY": {"type": "px", "value": 100},
    "endX": {"type": "px", "value": 500},
    "endY": {"type": "px", "value": 500}
})

# Scroll
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "mouse:scroll",
    "x": {"type": "/", "numerator": 500, "denominator": 1000},
    "y": {"type": "/", "numerator": 500, "denominator": 1000},
    "stepVertical": -5
})
```

### Keyboard (Desktop)

```python
# Type text
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "keyboard:type",
    "content": "Hello World"
})

# Hotkey
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "keyboard:hotkey",
    "keys": "ctrl+c"
})
```

### Touch (Android)

```python
# Tap
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "touch:tap",
    "x": {"type": "/", "numerator": 500, "denominator": 1000},
    "y": {"type": "/", "numerator": 500, "denominator": 1000}
})

# Swipe
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "touch:swipe",
    "x": {"type": "/", "numerator": 500, "denominator": 1000},
    "y": {"type": "/", "numerator": 750, "denominator": 1000},
    "direction": "up",
    "distance": {"type": "px", "value": 300}
})

# Android buttons
await client.sandbox.execute_sandbox_action("SBX-xxxx", action={
    "type": "android:back"
})
```

## Screenshots

```python
url, image, base64_str = await client.sandbox.get_screenshot("SBX-xxxx")
# image is a PIL.Image.Image object
image.show()
```

## File Operations

```python
from lybic.dto import FileCopyItem, HttpGetLocation, SandboxFileLocation

# Download file from URL
await client.sandbox.copy_files(
    "SBX-xxxx",
    files=[
        FileCopyItem(
            id="my-file",
            src=HttpGetLocation(url="https://example.com/file.txt"),
            dest=SandboxFileLocation(path="/tmp/file.txt")
        )
    ]
)
```

## HTTP Port Mapping

```python
# Create mapping
mapping = await client.sandbox.create_http_port_mapping(
    sandbox_id="SBX-xxxx",
    target_endpoint="127.0.0.1:8000"
)
print(f"Public URL: https://{mapping.domain}")

# List mappings
mappings = await client.sandbox.list_http_port_mappings("SBX-xxxx")

# Delete mapping
await client.sandbox.delete_http_port_mapping(
    sandbox_id="SBX-xxxx",
    target_endpoint="127.0.0.1:8000"
)
```

## Projects

```python
# List projects
projects = await client.project.list()

# Create project
project = await client.project.create(name="My Project")

# Delete project
await client.project.delete(project_id="PRJ-xxxx")
```

## Organization Stats

```python
stats = await client.stats.get()
print(f"Sandboxes: {stats.sandboxes}")
print(f"Projects: {stats.projects}")
```

## Coordinate Formats

```python
# Fractional (recommended - resolution independent)
{"type": "/", "numerator": 500, "denominator": 1000}  # 50%

# Pixel (absolute)
{"type": "px", "value": 500}
```

## Common Hotkeys

```python
"Return"        # Enter
"ctrl+c"        # Copy
"ctrl+v"        # Paste
"ctrl+s"        # Save
"ctrl+shift+s"  # Save as
"alt+Tab"       # Switch window
"F5"            # Refresh
"Escape"        # Escape
```

## Error Handling

```python
try:
    result = await client.sandbox.create(name="test", shape="beijing-2c-4g-cpu-linux")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. Use `async with` for automatic cleanup
2. Wait 10-30s after sandbox creation
3. Use fractional coordinates for portability
4. Always base64 encode/decode process I/O
5. Check `exitCode` (0 = success)
6. Delete sandboxes when done
7. Take screenshots to verify GUI state
