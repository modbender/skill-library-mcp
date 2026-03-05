# Security & Privacy Policy — ima-image-ai

## Overview

This skill generates images via the IMA Open API. This document explains what data is collected, where it's stored, and how to control it.

---

## Required Permissions

### 1. Network Access ✅

**Purpose:** Call IMA Open API endpoints

**Endpoints accessed:**
- `https://api.imastudio.com/open/v1/product/list` — Query available models
- `https://api.imastudio.com/open/v1/tasks/create` — Create image generation task
- `https://api.imastudio.com/open/v1/tasks/detail` — Poll task status
- `https://imapi.liveme.com/api/rest/oss/getuploadtoken` — Get image upload token (for image_to_image tasks)
- OSS presigned URLs (dynamic, returned by imapi.liveme.com) — Upload image files

**Domain ownership:**
Both `api.imastudio.com` and `imapi.liveme.com` are **owned and operated by IMA Studio**.
The split architecture separates API logic (api.imastudio.com) from media storage (imapi.liveme.com).

**Data sent to api.imastudio.com:**
- API key (IMA_API_KEY)
- Generation prompts (image descriptions)
- Model selection parameters
- Task IDs for status polling

**Data sent to imapi.liveme.com:**
- IMA API key (as `appUid` and `cmimToken` for authentication)
- Image file bytes (for image_to_image tasks)
- File metadata (content type, file extension)

**Verification:**
```bash
# Inspect network calls in the script:
grep -n "https://" scripts/ima_image_create.py

# Expected output:
# 60: DEFAULT_BASE_URL = "https://api.imastudio.com"
# 61: DEFAULT_IM_BASE_URL = "https://imapi.liveme.com"
```

---

### 2. File Read/Write ✅

**Purpose:** Store user preferences and logs locally

#### Files Created:

**A. User Preferences**
- **Path**: `~/.openclaw/memory/ima_prefs.json`
- **Content**: Model preferences (JSON)
- **Example**:
  ```json
  {
    "user_123": {
      "text_to_music": {
        "model_id": "sonic",
        "model_name": "Suno",
        "credit": 25,
        "last_used": "2026-02-27T12:34:56Z"
      }
    }
  }
  ```
- **Size**: < 1 KB
- **Rotation**: Never (until manually deleted)
- **Purpose**: Remember your favorite model
- **Contains**: Model IDs, credit costs, timestamps
- **Does NOT contain**: API keys, prompts, generated content, personal info

**B. Generation Logs**
- **Path**: `~/.openclaw/logs/ima_skills/ima_create_YYYYMMDD.log`
- **Content**: Timestamped operation logs
- **Example**:
  ```
  2026-02-27 12:34:56 | INFO  | create_task         | Creating image task: model=seedream, credit=5
  2026-02-27 12:35:23 | INFO  | poll_task           | Task completed: task_id=xxx, duration=27s
  ```
- **Size**: ~10-50 KB per day
- **Rotation**: Auto-delete logs older than 7 days
- **Purpose**: Debug issues, track API usage
- **Contains**: Timestamps, model IDs, task IDs, HTTP status codes
- **Does NOT contain**: API keys, full prompts, user data

---

## Data Flow Diagram

```
User Input
    ↓
[Agent reads prompt: "Generate sunset image"]
    ↓
[Script: ima_image_create.py]
    ↓
├── Read preference: ~/.openclaw/memory/ima_prefs.json (optional)
├── Call API: https://api.imastudio.com/open/v1/product/list (with IMA_API_KEY)
├── [If image_to_image task] Upload image: https://imapi.liveme.com (with IMA_API_KEY)
├── Call API: https://api.imastudio.com/open/v1/tasks/create (with IMA_API_KEY)
├── Poll API: https://api.imastudio.com/open/v1/tasks/detail (with IMA_API_KEY)
├── Write log: ~/.openclaw/logs/ima_skills/ (optional)
└── Save preference: ~/.openclaw/memory/ima_prefs.json (optional)
[Script: ima_voice_create.py]
    ↓
├── Read preference: ~/.openclaw/memory/ima_prefs.json (optional)
├── Call API: https://api.imastudio.com (with IMA_API_KEY)
├── Write log: ~/.openclaw/logs/ima_skills/ (optional)
└── Save preference: ~/.openclaw/memory/ima_prefs.json (optional)
    ↓
[API returns MP3 URL]
    ↓
User receives music file
```

---

## What This Skill Does NOT Do

❌ **Does NOT collect personal information** — no emails, names, addresses  
❌ **Does NOT store API keys** — only in environment variables (IMA_API_KEY)  
❌ **Does NOT store prompts** — only model preferences  
❌ **Does NOT store generated content** — music URLs are ephemeral  
❌ **Does NOT send data to third parties** — only IMA API  
❌ **Does NOT modify other skills** — isolated to its own directory  
❌ **Does NOT require sudo** — runs with user permissions  
❌ **Does NOT install background services** — runs on-demand only  

---

## User Control & Transparency

### View Stored Data

**Check preferences:**
```bash
cat ~/.openclaw/memory/ima_prefs.json
```

**Check logs:**
```bash
ls -lh ~/.openclaw/logs/ima_skills/
tail -20 ~/.openclaw/logs/ima_skills/ima_create_$(date +%Y%m%d).log
```

### Delete Stored Data

**Delete preferences (reset to defaults):**
```bash
rm ~/.openclaw/memory/ima_prefs.json
```

**Delete logs:**
```bash
rm -rf ~/.openclaw/logs/ima_skills/
```

**Delete everything:**
```bash
rm -rf ~/.openclaw/memory/ima_prefs.json ~/.openclaw/logs/ima_skills/
```

---

## Disable File Storage (Optional)

If you don't want local file writes:

### Method 1: Remove Write Permissions
```bash
touch ~/.openclaw/memory/ima_prefs.json
chmod 444 ~/.openclaw/memory/ima_prefs.json  # Read-only

mkdir -p ~/.openclaw/logs/ima_skills
chmod 555 ~/.openclaw/logs/ima_skills  # No write
```

**Effect:** Skill will skip writing preferences/logs, but will still function.

### Method 2: Use Null Device
```bash
ln -s /dev/null ~/.openclaw/memory/ima_prefs.json
```

**Effect:** Writes are discarded silently.

---

## API Key Security

### Best Practices

1. **Never hardcode API keys in code**
   ```bash
   # ❌ BAD
   --api-key ima_abc123xyz

   # ✅ GOOD
   export IMA_API_KEY=ima_abc123xyz
   ```

2. **Use scoped keys** (if provider supports)
   - Request read-only keys for testing
   - Use separate keys for different environments

3. **Rotate keys periodically**
   - Regenerate keys every 90 days
   - Revoke compromised keys immediately

4. **Verify endpoints**
   ```bash
   # Confirm script calls IMA domains only:
   grep -E "https://[^\"']+" scripts/ima_image_create.py
   ```

   Expected output:
   ```
   https://api.imastudio.com
   https://imapi.liveme.com
   ```

   **Both domains are owned by IMA Studio.** See "Network Endpoints" section for details.

---

## Hardcoded APP_KEY Disclosure

### What is APP_KEY?

The script contains a hardcoded `APP_KEY = "32jdskjdk320eew"` visible in the source code (line 74 of `ima_image_create.py`).

**Purpose**: This key is used to generate request signatures when authenticating to the image upload service (`imapi.liveme.com`).

**Is this a security risk?**
- ❌ **NOT a secret**: This is a shared, public key used by all IMA skill-based uploads
- ✅ **Intentionally visible**: IMA Studio provides this key for skill integrations
- ✅ **Limited scope**: Only used for upload authentication, not a personal credential
- ✅ **Additional auth required**: Upload requests also require your IMA API key

**Why is it hardcoded?**
- Simplifies setup (no additional configuration needed)
- Standard practice for SDK-like integrations
- Your personal IMA API key provides the actual authentication

**Privacy implications**:
- The APP_KEY itself doesn't grant access to your account
- It's paired with your IMA API key for authenticated uploads
- Think of it like a "client ID" in OAuth flows (public, not sensitive)

**If you're still concerned**:
1. Review the upload flow in `ima_image_create.py` lines 108-185
2. Verify APP_KEY is only used for signature generation, not transmitted alone
3. Contact IMA support to confirm this is the correct shared key: support@imastudio.com

---

## Network Traffic Verification

To verify where your data is sent, monitor network traffic during the first run:

### macOS/Linux:
```bash
# Terminal 1: Start packet capture
sudo tcpdump -i any -n 'host api.imastudio.com or host imapi.liveme.com' -w ima_traffic.pcap

# Terminal 2: Run a test generation
python3 scripts/ima_image_create.py \
  --api-key "$IMA_API_KEY" \
  --task-type text_to_image \
  --model-id doubao-seedream-4.5 \
  --prompt "test image"

# Terminal 1: Stop capture (Ctrl+C), then analyze
tcpdump -r ima_traffic.pcap -A | grep -i "host:"
```

**Expected output:**
- Connections to `api.imastudio.com` (API calls)
- Connections to `imapi.liveme.com` (image upload, only for i2i tasks)

**Red flags:**
- Connections to unknown domains
- Data sent to domains other than imastudio.com or liveme.com

### Windows:
Use [Wireshark](https://www.wireshark.org/) with filter: `http.host contains "imastudio" or http.host contains "liveme"`

### Alternative: Use mitmproxy
```bash
# Install mitmproxy:
pip install mitmproxy

# Start proxy:
mitmproxy -p 8080

# In another terminal, route traffic through proxy:
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
python3 scripts/ima_image_create.py --task-type text_to_image --model-id doubao-seedream-4.5 --prompt "test"

# In mitmproxy UI, verify only imastudio.com and liveme.com are contacted
```

---

## Code Transparency

### Inspect the Script

**Review network calls:**
```bash
# Show all HTTP requests:
grep -A 3 "requests\.(get|post)" scripts/ima_image_create.py
```

**Verify endpoints:**
```bash
# Confirm only IMA domains are accessed:
rg "https://" scripts/ima_image_create.py
```

Expected output:
```
60: DEFAULT_BASE_URL = "https://api.imastudio.com"
61: DEFAULT_IM_BASE_URL = "https://imapi.liveme.com"
```

**Check file writes:**
```bash
# Find all file operations:
grep -E "(open\(|with open)" scripts/ima_image_create.py
```

---

## Compliance & Standards

### GDPR (EU)
- ✅ **Right to access**: View files anytime (`cat ~/.openclaw/...`)
- ✅ **Right to erasure**: Delete files anytime (`rm ~/.openclaw/...`)
- ✅ **Data minimization**: Only stores necessary preferences
- ✅ **Transparency**: This document explains everything

### CCPA (California)
- ✅ **Right to know**: Full disclosure in this document
- ✅ **Right to delete**: User can delete all data
- ✅ **No selling data**: Skill never sells user data

### COPPA (Children's Privacy)
- ⚠️ **Not designed for children** — requires API key management
- Parental supervision recommended for users under 13

---

## Third-Party Services

### IMA Open API
- **Provider**: IMA Studio (https://imastudio.com)
- **Privacy Policy**: https://imastudio.com/privacy
- **Data sent**: Prompts, model selections, user IDs (optional)
- **Data received**: Generated music URLs
- **Data retention**: Per IMA's policy (check their website)

**User responsibility:**
- Review IMA's privacy policy before use
- Understand IMA's data retention practices
- Contact IMA support for data deletion requests

---

## Incident Response

### If You Suspect a Security Issue

1. **Stop using the skill immediately**
2. **Revoke your API key** at https://imastudio.com
3. **Report the issue**:
   - GitHub: https://git.joyme.sg/imagent/skills/ima-voice-ai/-/issues
   - Email: security@imastudio.com (for critical vulnerabilities)
4. **Delete local files**:
   ```bash
   rm -rf ~/.openclaw/memory/ima_prefs.json ~/.openclaw/logs/ima_skills/
   ```

### What We Will Do

- Acknowledge report within 24 hours
- Investigate and patch within 7 days
- Publish security advisory if needed
- Notify affected users via ClawHub

---

## Audit Trail

### Version History & Security Changes

| Version | Date | Security Changes |
|---------|------|------------------|
| v1.0.0 | 2026-02-27 | Initial release, basic logging |
| v1.0.1 | 2026-02-27 | Added this SECURITY.md document |

---

## Contact

- **Security Issues**: security@imastudio.com
- **General Support**: https://git.joyme.sg/imagent/skills/ima-voice-ai/-/issues
- **IMA API Support**: https://imastudio.com/support

---

## Acknowledgments

This skill follows security best practices inspired by:
- OWASP Top 10
- CWE/SANS Top 25
- OpenClaw Security Guidelines

---

**Last Updated:** 2026-02-27  
**Review Frequency:** Quarterly
