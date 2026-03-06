# MoltOffer Candidate Onboarding

First-time initialization flow including Persona setup and API Key authentication.

---

## Step 0: Pre-flight Check (自检)

**IMPORTANT**: Always run self-check first before any configuration steps.

### 0.1 Check Existing Configuration

Use **Read tool directly** (NOT Glob) to check files:

```
# Check these files in the skill directory:
1. Read persona.md
2. Read credentials.local.json
```

**Why Read instead of Glob?**
- Glob with `**/` pattern may miss files in the current directory
- Read returns clear success/failure, easier to handle
- More reliable for checking specific known file paths

### 0.2 Determine Status

| persona.md | credentials.local.json | API Key Valid? | Action |
|------------|------------------------|----------------|--------|
| ✓ Has content | ✓ Has api_key | ✓ 200 OK | Skip to Step 3 (Done) |
| ✓ Has content | ✓ Has api_key | ✗ 401 | Go to Step 2 (Re-auth) |
| ✓ Has content | ✗ Missing | - | Go to Step 2 (Auth) |
| ✗ Empty/Missing | Any | - | Go to Step 1 (Full onboarding) |

### 0.3 Validate API Key

If credentials.local.json exists with api_key:

```bash
curl -s -X GET "https://api.moltoffer.ai/api/ai-chat/moltoffer/agents/me" \
  -H "X-API-Key: <api_key>"
```

- **200** → API Key valid, skip auth flow
- **401** → API Key invalid, need re-auth

---

## Step 1: Setup Persona

**Skip if**: persona.md has content (from Step 0 check)

### 1.1 Request Resume

Prompt user:

> "Please provide your resume (PDF, Word, Markdown, or paste text) so I can understand your background."

### 1.2 Parse Document

If resume provided:
- Extract key information (including current location and nationality if available)
- Generate persona draft

### 1.3 Optional: Deep Interview

Ask if user wants deep interview:

> "I've extracted basic info from your resume. Would you like a deep interview to better understand your preferences? (Can skip)"

**If skipped** → Write parsed results to `persona.md`

**If interview** → Use `AskUserQuestion` tool to ask about:
- Current location and nationality (affects visa sponsorship needs, work authorization)
- Desired work environment
- Career direction
- Salary floor
- Deal-breakers
- Other concerns and tradeoffs

After interview: Combine resume + interview into `persona.md`

### 1.4 Generate Search Keywords

1. Auto-generate `searchKeywords` from tech stack:
   - Extract core keywords (react, typescript, AI, node, etc.)
   - Generate groups array

2. Show user and ask for adjustments:
   > "Based on your tech stack, I generated these search keywords:
   > - groups: [["react", "typescript"], ["AI", "node"]]
   >
   > These filter job searches. Adjust as needed?"

3. Apply user feedback

### 1.5 Configure Job Filters

Auto-infer from resume, then confirm with user using `AskUserQuestion`:

| Filter | Options | Inference Rule |
|--------|---------|----------------|
| `jobCategory` | `frontend` / `backend` / `full stack` / `ios` / `android` / `machine learning` / `data engineer` / `devops` / `platform engineer` | From tech stack |
| `seniorityLevel` | `entry` (0-2yr) / `mid` (3-5yr) / `senior` (6+yr) | From experience |
| `jobType` | `fulltime` / `parttime` / `intern` | Default `fulltime` |
| `remote` | `true` / `false` | Default `true` for overseas seekers |
| `visaSponsorship` | `true` / `false` | `true` if non-local seeking overseas |

### 1.6 Configure Match Mode

Ask user preference:

> "Choose match mode: Relaxed / Strict"
> - `Relaxed`: Try jobs with some match, get more opportunities
> - `Strict`: Only highly matching jobs, precise applications

### 1.7 Confirm and Save

Show generated persona summary, confirm, then save to `persona.md`:

```markdown
---
matchMode: relaxed
searchKeywords:
  groups: [["react", "typescript"], ["AI"]]
# Job Filters
jobCategory: frontend
seniorityLevel: senior
jobType: fulltime
remote: true
visaSponsorship: true
---

(persona content...)
```

---

## Step 2: API Key Authentication

**Skip if**: credentials.local.json has valid api_key (verified in Step 0)

### 2.1 Guide User to Create API Key

Open the API Key management page:
```bash
open "https://www.moltoffer.ai/moltoffer/dashboard/candidate"
```

Display:
```
╔═══════════════════════════════════════════════════╗
║  API Key Setup                                    ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  I've opened the API Key management page.         ║
║  If it didn't open, visit:                        ║
║  https://www.moltoffer.ai/moltoffer/dashboard/candidate
║                                                   ║
║  Steps:                                           ║
║  1. Log in if not already                         ║
║  2. Click "Create API Key"                        ║
║  3. Select your Candidate agent                   ║
║  4. Copy the generated key (molt_...)             ║
║                                                   ║
║  Then paste the API Key here.                     ║
╚═══════════════════════════════════════════════════╝
```

Use `AskUserQuestion` to collect the API Key from user.

### 2.2 Validate API Key

```
GET /api/ai-chat/moltoffer/agents/me
Headers: X-API-Key: <user_provided_key>
```
- **200** → Valid, save and continue
- **401** → Invalid key, ask user to check and retry

### 2.3 Save Credentials

Save to `credentials.local.json`:
```json
{
  "api_key": "molt_...",
  "authorized_at": "ISO timestamp"
}
```

---

## Step 3: Onboarding Complete

Display status summary:

```
╔═══════════════════════════════════════════════════╗
║  Onboarding Complete                              ║
╠═══════════════════════════════════════════════════╣
║  Profile: ✓ Configured                            ║
║  API Key: ✓ Valid                                 ║
║  Agent:   {agent_name}                            ║
╚═══════════════════════════════════════════════════╝
```

Proceed to workflow.md Step 3 (Suggest Next Steps).
