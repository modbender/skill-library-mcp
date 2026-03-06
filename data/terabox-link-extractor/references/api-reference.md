# TeraBox API Reference (v1.3.8)

## 📡 CLI Commands
The skill utilizes a high-performance Node.js extraction engine.

### 1. Extract Links
```bash
node scripts/extract.js "<url>"
```
- **Description**: Connects to XAPIverse to fetch direct high-speed links.
- **Output**: Pipe-delimited strings for LLM parsing (or JSON with `--json`).

### 2. Download Mode
```bash
node scripts/extract.js "<url>" --download [--out <path>]
```
- **Flags**:
  - `--download`: Triggers binary fetch of the asset.
  - `--out`: Subdirectory within `Downloads/` (Security-enforced).
  - `--json`: Return structured output for automation.

## 🔒 Security Protocols
1. **Path Isolation**: All downloads are restricted to the local `Downloads/` root. Path traversal (`../`) is automatically blocked.
2. **Credential Safety**: `TERABOX_API_KEY` is read from the environment and never logged or exposed in stdout.
3. **Primary Domain**: All network requests are native `https` to `xapiverse.com`.
