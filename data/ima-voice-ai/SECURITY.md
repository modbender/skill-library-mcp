# Security & Privacy Policy — ima-voice-ai

## Overview

This skill generates music via the IMA Open API. This document explains what data is collected, where it's stored, and how to control it.

---

## Required Permissions

### 1. Network Access ✅

**Purpose:** Call IMA Open API endpoints

**Endpoints accessed:**
- `https://api.imastudio.com/open/v1/product/list`
- `https://api.imastudio.com/open/v1/tasks/create`
- `https://api.imastudio.com/open/v1/tasks/detail`

**Data sent:**
- API key (IMA_API_KEY)
- Generation prompts (music descriptions)
- Model selection parameters
- User ID (if provided via --user-id flag)

**Verification:**
```bash
# Inspect network calls in the script:
grep -n "https://" scripts/ima_voice_create.py
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
  2026-02-27 12:34:56 | INFO  | create_task         | Creating music task: model=sonic, credit=25
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
[Agent reads prompt: "Generate lo-fi music"]
    ↓
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
   # Confirm script only calls IMA API:
   grep -E "https://[^\"']+" scripts/ima_voice_create.py
   ```

   Expected output:
   ```
   https://api.imastudio.com
   ```

---

## Code Transparency

### Inspect the Script

**Review network calls:**
```bash
# Show all HTTP requests:
grep -A 3 "requests\.(get|post)" scripts/ima_voice_create.py
```

**Verify endpoints:**
```bash
# Confirm only api.imastudio.com is accessed:
rg "https://" scripts/ima_voice_create.py
```

**Check file writes:**
```bash
# Find all file operations:
grep -E "(open\(|with open)" scripts/ima_voice_create.py
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
