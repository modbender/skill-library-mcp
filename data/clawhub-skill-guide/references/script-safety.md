# Script Safety Patterns

Patterns for including scripts in ClawHub skills that pass the security scanner.

The scanner evaluates scripts under **INSTALL MECHANISM** and checks for:
- External downloads or network calls
- Writes outside the skill workspace
- Obfuscated or unreadable code
- Missing documentation and inspection warnings

---

## Safe Script Checklist

Before publishing scripts, verify:

- [ ] Scripts only write within the skill workspace (relative paths or `$SKILL_DIR`)
- [ ] No network calls (`curl`, `wget`, `nc`, `fetch`, `requests.get`, etc.)
- [ ] No obfuscated, minified, or encoded code
- [ ] Each script's purpose and line count documented in SKILL.md
- [ ] "Inspect before running" warning in SKILL.md
- [ ] Plain bash/python/node — no compiled binaries

---

## Safe Patterns

### Workspace-scoped writes

```bash
#!/usr/bin/env bash
# Only write within the skill directory
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="$SKILL_DIR/output"
mkdir -p "$OUTPUT_DIR"
echo "result" > "$OUTPUT_DIR/result.txt"
```

### Relative path operations

```bash
#!/usr/bin/env bash
# Use relative paths from script location
cd "$(dirname "$0")"
mkdir -p ../data
cp ../assets/template.json ../data/config.json
```

### Read-only analysis

```python
#!/usr/bin/env python3
"""Analyze a file and print results. No writes, no network."""
import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)
print(f"Records: {len(data)}")
```

### Environment variable usage

```bash
#!/usr/bin/env bash
# Use declared env vars — never hardcode credentials
if [ -z "$MY_API_KEY" ]; then
    echo "Error: MY_API_KEY not set. See Prerequisites in SKILL.md."
    exit 1
fi
# Use $MY_API_KEY in operations...
```

---

## Unsafe Patterns (Trigger Scanner Warnings)

### Network downloads

```bash
# BAD — downloads external code
curl -sL https://example.com/installer.sh | bash
wget https://example.com/tool.tar.gz
pip install some-package
npm install some-module
```

### Writing outside workspace

```bash
# BAD — writes to system locations
cp config.json /etc/myapp/config.json
echo "alias myskill='...'" >> ~/.bashrc
sudo mv binary /usr/local/bin/
```

### Obfuscated code

```bash
# BAD — base64 encoded execution
eval "$(echo 'c29tZSBjb2Rl' | base64 -d)"
```

### Hardcoded credentials

```python
# BAD — credentials in source
API_KEY = "sk-abc123def456"
```

---

## Documentation Template

Add this to SKILL.md for any skill with scripts:

```markdown
## Bundled Scripts

| Script | Purpose | Lines |
|--------|---------|-------|
| `scripts/setup.sh` | Creates workspace directory structure | 25 |
| `scripts/analyze.py` | Parses input data and generates report | 80 |

The included scripts only create files within the skill workspace. They make
no network calls and write no files outside the skill directory. **Inspect
them before running** — all scripts are plain, readable code with no
obfuscation.
```

Adapt the table to list your actual scripts with accurate line counts.

---

## When Scripts Must Make Network Calls

Some skills legitimately need network access (API integrations, data fetching).
If scripts must make network calls:

### 1. Declare endpoints explicitly

In SKILL.md, document exactly which endpoints are contacted:

```markdown
## Network Access

The `scripts/fetch-data.sh` script contacts the following endpoints:
- `https://api.example.com/v2/data` — retrieves user data
- `https://api.example.com/v2/status` — checks service health

No other network calls are made.
```

### 2. Declare env vars for credentials

```yaml
env:
  - name: EXAMPLE_API_KEY
    description: "API key for Example service (used by fetch-data.sh)"
    required: true
    sensitive: true
```

### 3. Explain why network access is needed

```markdown
## Why Network Access

This skill integrates with the Example API to retrieve live data.
The `fetch-data.sh` script makes authenticated HTTPS requests to the
Example API. No data is sent to any other endpoint.
```

### 4. Recommend sandboxed execution

```markdown
## Security Notes

For production use, run this skill's scripts in a sandboxed environment
or review each network call before execution. The scripts use only the
declared API endpoints and transmit only the data described above.
```

---

## Script Testing Before Publish

Before publishing, run each script and verify:

1. **No files created outside the skill directory**
   ```bash
   # Watch filesystem writes during script execution
   find /tmp -newer /tmp/timestamp-file  # check for temp files
   ```

2. **No unexpected network connections**
   ```bash
   # Run with network monitoring (macOS)
   nettop -p $(pgrep -f your_script)
   ```

3. **Exit codes are correct**
   ```bash
   ./scripts/your-script.sh; echo "Exit: $?"
   ```

4. **Output matches documentation**
   - Verify files are created where documented
   - Verify no side effects beyond documented behavior
