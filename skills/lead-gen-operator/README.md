# Lead Gen Operator

Your AI that finds leads, enriches data, drafts outreach, sends emails, and tracks follow-ups — while you sleep.

## Quick Setup (5 minutes)

### 1. Install OpenClaw
If you haven't already:
```bash
npm install -g openclaw
openclaw setup
```

### 2. Install Required Skills
```bash
clawhub install web_search
clawhub install web_fetch
clawhub install gog
```

### 3. Install Memory Manager Skill
```bash
mkdir -p ~/.openclaw/workspace/skills/memory-manager
# Copy memory-manager.js and SKILL.md from the package
```

### 4. Copy Files
Copy these files to your OpenClaw workspace:
- `SOUL.md` → `~/.openclaw/workspace/SOUL.md`
- `memory-manager/` → `~/.openclaw/workspace/skills/memory-manager/`
- `memory/leads.json` → `~/.openclaw/workspace/memory/leads.json`

### 5. Configure API Keys
Add to your `~/.openclaw/openclaw.json`:
```json
{
  "env": {
    "GOOGLE_API_KEY": "your-google-api-key",
    "SEARCH_API_KEY": "your-search-api-key"
  }
}
```

### 6. Start
```bash
openclaw start
```

## Features

### Find Leads
```
Find [number] [industry] companies in [location]
```
Example: "Find 5 SaaS companies in USA"

### Auto-Save
Leads are automatically saved after finding. No manual save needed.

### Enrich
```
Enrich [company name]
```
Get contact info, funding details, and more.

### Write Outreach
```
Write outreach for [company name]
```
Creates personalized email drafts.

### Send Email
```
Send to [company name]
```
Sends the outreach email directly via Gmail.

### Track Status
Leads automatically track status: new → enriched → drafted → sent → replied → closed

### Export
```
Export leads
```
Export your leads to CSV format.

### Follow-ups
```
What should I follow up on?
```
Shows leads that need follow-up (sent >7 days ago).

### Stats
```
Show stats
```
View your pipeline statistics.

## What's Included

| File | Purpose |
|------|---------|
| SOUL.md | Persona and all commands |
| memory-manager/ | Skill for persistence |
| memory-manager.js | Script with all features |
| memory/leads.json | Lead tracking database |
| README.md | This file |

## Price
$19 (this package)
