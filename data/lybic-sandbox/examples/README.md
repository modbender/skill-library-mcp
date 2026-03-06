# Lybic Skill Examples

This directory contains practical examples demonstrating the Lybic Python SDK capabilities.

## Prerequisites

Before running these examples, ensure you have:

1. **Installed the Lybic SDK**:
   ```bash
   pip install lybic
   ```

2. **Set up credentials** (choose one method):
   
   **Method A: Environment Variables** (recommended)
   ```bash
   export LYBIC_ORG_ID="your_org_id"
   export LYBIC_API_KEY="your_api_key"
   ```
   
   **Method B: In Code**
   ```python
   from lybic import LybicClient, LybicAuth
   
   client = LybicClient(
       LybicAuth(
           org_id="your_org_id",
           api_key="your_api_key"
       )
   )
   ```

## Examples

### 01_execute_code.py
**Basic Sandbox Management and Code Execution**

Creates a sandbox, executes Python code, and cleans up.

```bash
python 01_execute_code.py
```

**What it demonstrates:**
- Creating a sandbox with specific configuration
- Waiting for sandbox readiness
- Executing Python code via process execution
- Handling base64-encoded stdin/stdout
- Cleaning up resources

### 02_gui_automation.py
**Desktop GUI Automation**

Performs mouse and keyboard actions on an existing sandbox.

```bash
python 02_gui_automation.py
```

**What it demonstrates:**
- Taking screenshots
- Mouse clicking with fractional coordinates
- Keyboard typing
- Hotkey combinations
- Wait actions

**Requirements:** Existing sandbox ID (Linux or Windows)

### 03_file_processing.py
**File Download and Processing**

Downloads a file from URL and processes it with Python.

```bash
python 03_file_processing.py
```

**What it demonstrates:**
- File copy API usage
- Downloading files from HTTP URLs
- Executing code in specific working directories
- Processing CSV data in sandbox

**Requirements:** Existing sandbox ID

### 04_manage_sandboxes.py
**Sandbox and Project Management**

Lists and manages sandboxes and projects.

```bash
python 04_manage_sandboxes.py
```

**What it demonstrates:**
- Getting organization statistics
- Listing all projects
- Listing all sandboxes
- Getting detailed sandbox information
- Creating new projects

### 05_android_automation.py
**Android Mobile Automation**

Demonstrates touch gestures and app management on Android.

```bash
python 05_android_automation.py
```

**What it demonstrates:**
- Touch tap gestures
- Swipe actions
- Android system buttons (back, home)
- App management (list, start, close apps)
- Keyboard input on mobile

**Requirements:** Existing Android sandbox ID

### 06_http_port_mapping.py
**HTTP Port Mapping**

Creates public URLs for sandbox services.

```bash
python 06_http_port_mapping.py
```

**What it demonstrates:**
- Creating HTTP port mappings
- Listing active mappings
- Deleting mappings
- Accessing sandbox services externally

**Requirements:** Existing sandbox ID

## Running Examples

### Quick Start

```bash
# Set credentials
export LYBIC_ORG_ID="ORG-xxxx"
export LYBIC_API_KEY="lysk-xxxx"

# Run an example
python 01_execute_code.py
```

### With Existing Sandbox

Some examples require an existing sandbox:

```bash
# First, create a sandbox via the Lybic dashboard or API
# Note the sandbox ID (e.g., SBX-abc123)

# Then run examples that need a sandbox ID
python 02_gui_automation.py
# Enter: SBX-abc123
```

## Tips

1. **Sandbox Readiness**: After creating a sandbox, wait 10-30 seconds before interacting with it.

2. **Fractional Coordinates**: Use fractional coordinates for resolution-independent GUI automation:
   ```python
   {"type": "/", "numerator": 1, "denominator": 2}  # 50%
   ```

3. **Error Handling**: All examples include basic error handling. Add more robust error handling for production use.

4. **Resource Cleanup**: Remember to delete sandboxes when done to avoid unnecessary charges:
   ```python
   await client.sandbox.delete(sandbox_id)
   ```

5. **Screenshots**: Take screenshots before and after GUI actions to verify results.

6. **Base64 Encoding**: Process I/O uses base64 encoding:
   ```python
   # Encode input
   stdin_b64 = base64.b64encode(code.encode()).decode()
   
   # Decode output
   output = base64.b64decode(result.stdoutBase64).decode()
   ```

## Common Issues

### Authentication Failed
- Verify your `LYBIC_ORG_ID` and `LYBIC_API_KEY` are correct
- Check that environment variables are set in your current shell

### Sandbox Not Ready
- Wait longer after creation (increase `asyncio.sleep()` duration)
- Check sandbox status with `client.sandbox.get(sandbox_id)`

### Action Failed
- Verify coordinates are within screen bounds
- Ensure the sandbox type matches the action (desktop vs mobile)
- Take a screenshot to verify the current state

### Process Timeout
- Long-running processes need special handling
- See the Lybic documentation for long-running task support

## Learn More

- [Lybic Documentation](https://docs.lybic.cn)
- [Python SDK Reference](https://docs.lybic.cn/en/sdk/python)
- [Action Space Guide](https://docs.lybic.cn/en/sandbox/action)
- [Main Skill Documentation](../skill.md)

## License

MIT
