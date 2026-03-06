# FileWave Credential & Multi-Server Architecture

## Problem Statement

1. **Security:** Server DNS and API tokens should NOT be stored in the skill code
2. **Multi-Server:** Users may have multiple FileWave servers (production, lab, test)
3. **Data Isolation:** Know which data came from which server (prevent confusion)
4. **Flexibility:** Support 1 server or many servers easily

## Proposed Solution: Profile-Based Config

### Architecture

Store credentials in **config file** with **named profiles** (similar to AWS CLI):

```
~/.filewave/config
```

**Format:**
```ini
[default]
profile = lab

[lab]
server = filewave.company.com
token = your_api_token_here

[production]
server = filewave.company.com
token = (production-token-here)

[test]
server = filewave-test.company.com
token = (test-token-here)
```

### Security Properties

✅ **Not in skill code** — All credentials in external config file  
✅ **Not in environment** — Avoids shell history exposure  
✅ **File permissions** — Can `chmod 600 ~/.filewave/config` (read-only by user)  
✅ **Per-machine** — Different tokens on dev vs prod machines  
✅ **Still supportable by env vars** — For CI/CD pipelines (override)  

### CLI Usage

**Default server (profile: lab):**
```bash
./filewave query devices --query-id 1
# Uses [lab] profile automatically
```

**Specific server:**
```bash
./filewave query devices --query-id 1 --profile production
# Uses [production] profile
```

**List available profiles:**
```bash
./filewave --list-profiles
# Output:
#   default → lab
#   lab
#   production
#   test
```

**Environment variable override (for CI/CD):**
```bash
export FILEWAVE_PROFILE="production"
./filewave query devices --query-id 1
# Override default profile
```

Or:
```bash
export FILEWAVE_SERVER="ci.filewave.net"
export FILEWAVE_TOKEN="ci-token"
./filewave query devices --query-id 1
# Uses env vars directly (skips config file)
```

## Data Isolation

### Response Format

Every response includes **server context**:

```json
{
  "server": "lab",
  "server_url": "https://filewave.company.com",
  "timestamp": "2026-02-12T14:07:00Z",
  "query_id": 1,
  "device_count": 5,
  "devices": [...]
}
```

Or in text output:

```
Server: lab (filewave.company.com)
Query: Inventory Query #1
Retrieved: 2026-02-12 14:07:00 UTC

Found 5 devices:
  • Device1
  • Device2
  ...
```

### Prevent Confusion

1. **Output includes server name** — Always clear which server data came from
2. **Multiple queries** — Can query different servers and compare:
   ```bash
   ./filewave query devices --query-id 1 --profile lab > lab-devices.json
   ./filewave query devices --query-id 1 --profile production > prod-devices.json
   # Compare with: diff lab-devices.json prod-devices.json
   ```

3. **JSON aggregation** — Script can merge data and track source:
   ```python
   [
     {"server": "lab", "device_name": "Device1", ...},
     {"server": "production", "device_name": "Device2", ...}
   ]
   ```

## Implementation Plan

### Phase 1: Config File Support
- [ ] Add `config_manager.py` module
  - Read/write `~/.filewave/config`
  - Parse INI format
  - Validate profiles
  - Cache in memory

- [ ] Update CLI:
  - Add `--profile` argument
  - Add `--list-profiles` command
  - Load credentials from config file

- [ ] Update FileWaveClient:
  - Include `server` and `profile_name` in responses
  - Add server context to all output

### Phase 2: Env Var Override
- [ ] Support `FILEWAVE_PROFILE` env var
- [ ] Support `FILEWAVE_SERVER` + `FILEWAVE_TOKEN` for direct override
- [ ] Priority: CLI args > env vars > config file

### Phase 3: Setup Wizard
- [ ] `./filewave setup` command
  - Interactive profile creation
  - Validate server connectivity
  - Save to config file with proper permissions (600)

## Config File Management

### Initial Setup

Manual creation:
```bash
mkdir -p ~/.filewave
touch ~/.filewave/config
chmod 600 ~/.filewave/config

# Edit with: nano ~/.filewave/config
```

Or with setup wizard (future):
```bash
./filewave setup
# Interactive prompts for server/token
```

### Example Config

```ini
# Default profile to use if --profile not specified
[default]
profile = lab

# Lab server (filewave.company.com)
[lab]
server = filewave.company.com
token = your_api_token_here

# Production server
[production]
server = filewave.company.com
token = (your-production-token)
description = Production FileWave instance

# Test server
[test]
server = filewave-test.company.com
token = (your-test-token)
description = Testing environment
```

### Permissions

```bash
ls -la ~/.filewave/config
# -rw------- 1 user group 2048 Feb 12 10:07 /Users/user/.filewave/config

# Only owner can read/write (no group/other access)
chmod 600 ~/.filewave/config
```

## Decision Matrix

| Aspect | Config File | Env Vars | Keychain |
|--------|-------------|----------|----------|
| **Persistent** | ✅ Yes | ❌ No | ✅ Yes |
| **Secure** | ✅ (chmod 600) | ⚠️ Shell history | ✅✅ Best |
| **Multi-server** | ✅ Profiles | ⚠️ Complex | ✅ Possible |
| **CI/CD compatible** | ✅ + env override | ✅ Yes | ❌ Not ideal |
| **UX familiar** | ✅ (AWS CLI style) | ✅ Simple | ❌ Less common |
| **Complexity** | 🟡 Medium | ✅ Low | 🔴 High |

**Recommendation:** Config file (INI format with profiles) + env var override for CI/CD

## Data Isolation Example

```bash
# Query lab server
./filewave query devices --query-id 1 --profile lab --format json > lab.json

# Query production server
./filewave query devices --query-id 1 --profile production --format json > prod.json

# Compare
jq '.server' lab.json         # Output: "lab"
jq '.server' prod.json        # Output: "production"

# Merge with server context preserved
jq -s 'add' lab.json prod.json | jq '.[] | {server, device_name}' | sort
```

Output:
```json
{"server": "lab", "device_name": "Device1"}
{"server": "lab", "device_name": "Device2"}
{"server": "production", "device_name": "Device3"}
{"server": "production", "device_name": "Device4"}
```

## What Doesn't Go in the Skill

❌ Hardcoded server/token  
❌ Server/token in README examples  
❌ Default tokens in config files (must be set by user)  
❌ Storing tokens in script/query history  

## What Goes in the Skill

✅ Config file path logic (`~/.filewave/config`)  
✅ Profile management code  
✅ Credential loading from file  
✅ Env var override logic  
✅ Server context in responses  
✅ Documentation on setup  

## Migration Path

**Current (v1):**
```bash
export FILEWAVE_SERVER="filewave.company.com"
export FILEWAVE_API_TOKEN="token"
./filewave query devices
```

**After Phase 1:**
```bash
# First time setup
mkdir -p ~/.filewave
cat > ~/.filewave/config << EOF
[lab]
server = filewave.company.com
token = token
EOF

# Usage
./filewave query devices              # Uses [lab] (or default)
./filewave query devices --profile lab
```

**Still works via env:**
```bash
export FILEWAVE_SERVER="filewave.company.com"
export FILEWAVE_API_TOKEN="token"
./filewave query devices              # Still works, env var override
```

## Summary

This architecture provides:

1. ✅ **Security** — Credentials outside skill, file-permission protected
2. ✅ **Multi-server** — Profiles for managing multiple servers
3. ✅ **Clarity** — Response includes server name/context
4. ✅ **Flexibility** — Config file + env var override + CLI args
5. ✅ **Familiarity** — Profile-based pattern like AWS CLI
6. ✅ **Backwards compatible** — Env var support for existing scripts

Ready to implement in Phase 1.
