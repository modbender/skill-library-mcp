---
name: token-management
description: "Centralized API token management workflow. Store tokens in .env with expiration dates, test permissions via script battery, document capabilities in connections/, set calendar renewal reminders. Prevents re-asking for credentials, ensures token security, tracks expiration."
type: public
version: 1.0.1
status: published
dependencies:
  - python3
  - requests
  - gog (for calendar reminders)
author: nonlinear
license: MIT
---

# Token Management

**Published:** https://clawhub.com/skills/token-management

**Purpose:** Centralize API token management - storage, testing, documentation, expiration tracking.

**Triggers:**
- "adiciona token X"
- "salva API key pra Y"
- "preciso de token Z"

---

## 🔴 CRITICAL RULE

**ALWAYS check `~/Documents/life/.env` FIRST before asking for tokens!**

---

## Workflow

### When receiving a new token:

0. **Git commit (if applicable)**
   - If .env is in a git repo: `cd ~/Documents/life && git add -A && git commit -m "Before updating TOKEN_NAME"`
   - Safety first!

1. **Ask for expiration date**
   - "Quando esse token expira?"
   - Format: YYYY-MM-DD or "1 year" / "never"

2. **Store in .env**
   - **Location:** `~/Documents/life/.env` (canonical location)
   - Format: `SERVICE_NAME_TOKEN=value  # Expires: YYYY-MM-DD`
   - Example: `WILEY_JIRA_TOKEN=abc123  # Expires: 2027-02-12`

3. **Create calendar reminder (if expires)**
   - **When:** 7 days before expiration (1 week warning)
   - **Event:** "⚠️ Renew [SERVICE] API token (expires in 7 days)"
   - **Format:** All-day event
   - **Command:** 
     ```bash
     gog calendar create primary \
       --summary "⚠️ Renew SERVICE token" \
       --from "YYYY-MM-DDT00:00:00-05:00" \
       --to "YYYY-MM-DDT23:59:59-05:00" \
       --description "Token expires YYYY-MM-DD. Renew at: [RENEWAL_URL]"
     ```

4. **Test token permissions**
   - Run test battery to discover what token can do
   - **Script:** Use template below (adapt per service)
   - Document results in connections/ file
   - **Example:**
     ```python
     # Test Jira token
     import requests, base64
     
     TOKEN = "..."
     EMAIL = "user@example.com"
     auth = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
     
     tests = [
         ("Get user", "GET", "/rest/api/3/myself"),
         ("List projects", "GET", "/rest/api/3/project"),
         ("Search issues", "GET", "/rest/api/3/search", {"jql": "assignee=currentUser()"}),
     ]
     
     for name, method, endpoint, *params in tests:
         r = requests.get(f"https://DOMAIN{endpoint}", 
                         headers={'Authorization': f'Basic {auth}'},
                         params=params[0] if params else None)
         print(f"{'✅' if r.ok else '❌'} {name}: {r.status_code}")
     ```

5. **Document in connections/**
   - Create or update `~/Documents/life/connections/SERVICE.md`
   - **Include:**
     - What token offers (read/write/scope)
     - **When obtained:** YYYY-MM-DD
     - **Expiry date:** YYYY-MM-DD
     - **Renewal link:** URL to get new token
     - How to use (code examples)
   - Link to .env variable name
   - **Example:**
     ```markdown
     ## Token Info
     - **Obtained:** 2026-02-12
     - **Expires:** 2027-02-12
     - **Renew at:** https://id.atlassian.com/manage-profile/security/api-tokens
     - **Scope:** read-write
     - **Variable:** `WILEY_JIRA_TOKEN` (~/Documents/life/.env)
     ```

5. **Update token index**
   - Maintain list in this SKILL.md (see below)

### When needing API access:

1. **✅ ALWAYS check .env first:** `~/Documents/life/.env`
2. **If not found:** Check connections/ for setup instructions
3. **If still missing:** Ask Nicholas for token

---

## Token Index

**Location:** `~/Documents/life/.env`

**Example tokens:**

| Service | Variable | Scope | Expires | Connection Doc |
|---------|----------|-------|---------|----------------|
| Figma | `FIGMA_TOKEN` | read-write | YYYY-MM-DD | [figma.md](~/Documents/life/connections/figma.md) |
| Jira | `JIRA_TOKEN` | read-write | YYYY-MM-DD | [jira.md](~/Documents/life/connections/jira.md) |
| Slack | `SLACK_TOKEN` | bot permissions | Never | [slack.md](~/Documents/life/connections/slack.md) |
| GitHub | `GITHUB_TOKEN` | repo, gist | YYYY-MM-DD | [github.md](~/Documents/life/connections/github.md) |

**Your index:** Keep your own list in this section (local copy of skill).

---

## Commands

### Add token
```bash
# Append to .env (skill will automate)
echo "SERVICE_TOKEN=value" >> ~/Documents/life/.env
```

### Check token exists
```bash
grep SERVICE_TOKEN ~/Documents/life/.env
```

### List all tokens
```bash
cat ~/Documents/life/.env
```

---

## .env Location

**Canonical location:** `~/Documents/life/.env`

**Why here:**
- ✅ Life infrastructure (shareable, public)
- ✅ Survives workspace wipes
- ✅ Consistent with connections/ folder
- ✅ Not tied to OpenClaw workspace

**Python usage:**
```python
from dotenv import load_dotenv
load_dotenv('~/Documents/life/.env')  # Or absolute path
```

**Shell usage:**
```bash
source ~/Documents/life/.env
echo $YOUR_TOKEN_NAME
```

---

**Created:** 2026-02-12  
**Updated:** 2026-02-13 (sanitized for publication)
