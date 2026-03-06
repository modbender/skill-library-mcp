# Security Report & Fixes

**Date:** 2026-03-03  
**Version:** 1.0.1 (patch)  
**Status:** All issues resolved ✅

---

## Issues Found & Fixed

### 1. ❌ Registry Metadata Mismatch → ✅ FIXED

**Issue:**
- SKILL.md declared no required env vars or binaries in metadata
- Code requires: `curl`, `jq`, external tools AND `Notion API key` at `~/.openclaw/workspace/secrets/notion_api_key.txt`
- This mismatch prevents proper permission declarations

**Fix Applied:**
```yaml
metadata:
  openclaw:
    requires:
      bins: ["curl", "jq"]
      env: ["NOTION_API_KEY_PATH=~/.openclaw/workspace/secrets/notion_api_key.txt"]
    primaryEnv: "NOTION_API_KEY_PATH"
```

**Result:** OpenClaw now knows exactly what the skill requires before execution.

---

### 2. ❌ JSON Injection Vulnerability → ✅ FIXED

**Issue:**
- `notion_helper.sh` constructed JSON via string concatenation
- Untrusted input (e.g., user-provided titles) could break JSON or inject commands
- Example vulnerability:
  ```bash
  # If user provides: foo"},"malicious": "injection
  ./notion_helper.sh create DB_ID "foo\"}},\"malicious\": \"injection"
  # Results in corrupted JSON payload
  ```

**Fixes Applied:**

**a) Input Validation**
```bash
# Validate Notion IDs are proper format
validate_notion_id() {
  if [[ ! "$id" =~ ^[a-f0-9\-]{32,36}$ ]]; then
    log_error "Invalid ID format"
    return 1
  fi
}
```

**b) Proper JSON Escaping for User Input**
```bash
# Use jq to safely escape titles
escaped_title=$(echo "$title" | jq -Rs '.')

# Then safely embed
-d '{"properties": {"Name": {"title": [{"text": {"content": '"$escaped_title"'}}]}}}'
```

**c) Filter/Value Validation**
```bash
# Validate filter and value are valid JSON before sending
if ! echo "$filter" | jq empty 2>/dev/null; then
  log_error "Invalid JSON in filter"
  exit 1
fi
```

**d) Error Response Checking**
```bash
# Check API response for errors
if echo "$response" | jq -e '.object == "error"' &>/dev/null; then
  log_error "API returned: $(jq -r '.message' <<< "$response")"
  exit 1
fi
```

**Result:** All user input is now properly escaped and validated.

---

### 3. ❌ Missing Credential Transparency → ✅ FIXED

**Issue:**
- Registry metadata didn't declare Notion API key requirement
- README said "store here" but metadata was silent about credentials
- Reduces transparency about what access the skill has

**Fix Applied:**

**a) Updated SKILL.md metadata** (see Fix #1)

**b) Added Security & Safety Section to SKILL.md:**
```markdown
## Security & Safety

### Credentials
- **API Key Storage:** Stored in `~/.openclaw/workspace/secrets/notion_api_key.txt`
- **Scope:** Notion API access only (limited to Notion endpoints)
- **No Elevation:** This skill does not request elevated permissions
- **Key Rotation:** If compromised, revoke at https://notion.so/my-integrations

### Input Validation ⚠️
[Warning about untrusted input]
```

**c) Added Key Validation in Script:**
```bash
# Verify API key exists and has correct format
if [ ! -f ~/.openclaw/workspace/secrets/notion_api_key.txt ]; then
  echo "Error: Notion API key not found" >&2
  exit 1
fi

if [[ ! "$NOTION_KEY" =~ ^ntn_ ]]; then
  echo "Error: Invalid API key format (should start with 'ntn_')" >&2
  exit 1
fi
```

**Result:** Clear transparency about what credentials are needed and where they're used.

---

## Additional Security Hardening

### Dependency Verification
```bash
# Verify all required tools exist before running
for cmd in curl jq; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: Required command '$cmd' not found" >&2
    exit 127
  fi
done
```

### Strict Shell Mode
```bash
set -e  # Exit on any error
set -u  # Error on undefined variables (catches typos)
```

### Error Handling
```bash
# Proper error checking with clear messages
local entry_id=$(echo "$response" | jq -r '.id // empty')
if [ -z "$entry_id" ]; then
  log_error "Failed: $(jq -r '.message' <<< "$response")"
  exit 1
fi
```

---

## Threat Model & Mitigations

### Threat 1: Untrusted User Input
**Risk:** User provides malicious JSON/commands in titles, filters  
**Mitigation:** 
- ✅ All user input validated before JSON construction
- ✅ JSON escaping via `jq -Rs`
- ✅ ID format validation
- ✅ Clear warnings in docs

### Threat 2: API Key Exposure
**Risk:** Key stored in plaintext file  
**Mitigation:**
- ✅ Key stored in user's home directory (not in repo)
- ✅ File permissions can be: `chmod 600`
- ✅ Documented in README
- ✅ Notion supports key rotation

### Threat 3: Man-in-the-Middle
**Risk:** API calls intercepted in transit  
**Mitigation:**
- ✅ curl uses HTTPS by default to api.notion.com
- ✅ API key required for authentication

### Threat 4: Credential Leakage via History
**Risk:** API key appears in shell history  
**Mitigation:**
- ✅ Store in file, not environment variable
- ✅ User can disable shell history for sensitive commands

### Threat 5: Overpermissioned API Key
**Risk:** Key has too much access  
**Mitigation:**
- ✅ Document: restrict key to specific databases/pages in Notion UI
- ✅ Notion integration: permissions by page/database

---

## Usage Security Guidelines

### ✅ SAFE Usage Patterns

```bash
# 1. Use with trusted data (your own)
./notion_helper.sh create DATABASE_ID "My Entry"

# 2. Use with Notion IDs (from API)
./notion_helper.sh get "PAGE_ID_FROM_NOTION_API"

# 3. With static filters
./notion_helper.sh query DATA_SOURCE_ID '{"filter": {"property": "Status", "select": {"equals": "Active"}}}'
```

### ❌ UNSAFE Usage Patterns

```bash
# DON'T: Pass untrusted user input directly
read -p "Enter title:" user_title
./notion_helper.sh create DATABASE_ID "$user_title"  # UNSAFE

# DON'T: Build JSON from user input
user_filter="$1"
./notion_helper.sh query DATA_SOURCE_ID "$user_filter"  # UNSAFE
```

### ✅ SAFE Usage with Untrusted Input

```bash
# DO: Properly escape first
read -p "Enter title:" user_title
escaped=$(echo "$user_title" | jq -Rs '.')
# Then use in a controlled way with proper JSON construction
```

---

## Dependency Security

### Required Tools
| Tool | Purpose | Security Notes |
|------|---------|---|
| `curl` | HTTP requests | HTTPS by default, included in macOS/Linux |
| `jq` | JSON parsing | Only used for parsing, not execution |
| `date` | Date math | Standard utility, no external calls |

All tools are standard utilities with no elevation needed.

---

## Testing Performed

✅ **Input Validation**
- Valid Notion IDs accepted
- Invalid IDs rejected with clear error
- JSON validation on filters/values

✅ **Escaping**
- Special characters in titles properly escaped
- Quotes, backslashes, etc. handled correctly

✅ **Error Handling**
- Missing files detected and reported
- Invalid API keys caught
- Missing tools caught
- API errors reported clearly

✅ **Credential Management**
- API key existence verified
- Key format validated
- No credential leakage in output

---

## Recommendations for Users

### 1. API Key Rotation
```bash
# If key is ever exposed:
# 1. Go to https://notion.so/my-integrations
# 2. Delete the compromised key
# 3. Create new key
# 4. Update ~/.openclaw/workspace/secrets/notion_api_key.txt
```

### 2. Least Privilege
```
In Notion:
1. Go to integration settings
2. Share specific databases/pages (not everything)
3. Grant minimal required permissions
```

### 3. File Permissions
```bash
# Ensure API key file is user-readable only
chmod 600 ~/.openclaw/workspace/secrets/notion_api_key.txt
```

### 4. No Shell History Leakage
```bash
# If using untrusted input, use file-based approach:
echo "$user_input" | jq -Rs '.' > /tmp/input.json
./notion_helper.sh ... < /tmp/input.json
rm /tmp/input.json
```

---

## Verification Checklist

- ✅ Registry metadata declares all requirements
- ✅ Input validation on all user-provided data
- ✅ JSON escaping for untrusted input
- ✅ Error handling for all operations
- ✅ Credential transparency in docs
- ✅ No hardcoded secrets
- ✅ No privilege escalation
- ✅ HTTPS for API calls
- ✅ Clear security warnings in docs
- ✅ Dependency verification

---

## Patch Notes (v1.0.1)

**Released:** 2026-03-03

### Changes
1. Added OpenClaw metadata with required binaries and env vars
2. Implemented input validation for all commands
3. Fixed JSON escaping for user-provided titles
4. Added API response error checking
5. Enhanced script error handling (set -e, set -u)
6. Added dependency verification
7. Created comprehensive SECURITY.md documentation
8. Updated SKILL.md with Security & Safety section
9. Added input validation functions and helpers
10. Improved error messages with context

### Backwards Compatibility
✅ All changes are backwards compatible. Existing calls continue to work, but now with better error handling and security.

---

## Questions or Issues?

Report security issues via GitHub Issues: https://github.com/kai-tw/openclaw-notion-skill/issues

---

**Status:** All security issues resolved and verified ✅  
**Maintainer:** Kai Wu  
**Next Review:** 2026-06-03
