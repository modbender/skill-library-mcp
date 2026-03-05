# B2B Sales Prospecting & Lead Discovery Agent

Find and qualify B2B prospects using the AgentSource API. Search 200M+ companies and contacts by ICP criteria, get verified emails and phones, and build targeted outbound lists.

Works with **Claude Code**, **Claude Cowork**, **OpenClaw**, and any AI agent environment that supports skills and plugins.

## How It Works

1. Describe your ideal customer profile (industry, size, location, tech stack)
2. Define your buyer persona (title, seniority, department)
3. The agent searches the AgentSource database and shows you a preview
4. You confirm — then it fetches results, enriches with contact info, and exports CSV

All API responses are written to temp files so large payloads never appear in context.

## Requirements

- Python 3.8+ (standard library only)
- An Explorium AgentSource API key
- Any AI agent environment that supports skills/plugins

## Quick Start

### 1. Install
```bash
./setup.sh
```

### 2. Set your API key

**Do not share your API key in the AI chat.** Set it securely:

```bash
# Option A — Environment variable
export EXPLORIUM_API_KEY=your_api_key_here

# Option B — CLI config (saved to ~/.agentsource/config.json, mode 600)
python3 ~/.agentsource/bin/agentsource.py config --api-key your_api_key_here
```

### 3. Start prospecting
```
Find CTOs at Series B SaaS companies in California
```
```
Get emails for VP Sales at companies that recently raised Series A
```
```
Build a list of 500 product managers at healthcare companies in the US
```
```
Find companies hiring engineers that use Kubernetes
```
```
Show me fintech companies with buying intent for CRM software
```

## Key Features

- **ICP-Based Search** — Filter by industry, company size, revenue, location, tech stack, company age
- **Buyer Persona Targeting** — Search by job title, seniority, department
- **Verified Contact Info** — Professional emails, direct phones, LinkedIn profiles
- **Buying Intent Signals** — Find companies actively researching products like yours
- **Growth Signals** — Filter by recent funding, hiring activity, new products
- **Bulk List Building** — Up to 1,000+ prospects per query
- **CSV Export** — Ready for CRM import

## Data & Privacy

| Location | Contents | Permissions |
|---|---|---|
| `~/.agentsource/config.json` | API key (if saved) | 600 (owner read-only) |
| `/tmp/agentsource_*.json` | API result data | OS cleanup |

All API calls go to `https://api.explorium.ai/v1/`. See SKILL.md for full data handling details.
