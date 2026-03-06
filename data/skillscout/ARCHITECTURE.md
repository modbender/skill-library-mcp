# SkillScout Architecture

## Overview

SkillScout is a curated directory of AI agent skills with a security-first review pipeline. The key constraint: **the security review agent never executes any skill code.**

## System Design

```
┌─────────────────────────────────────────────────┐
│                  REVIEW PIPELINE                 │
│                                                  │
│  ┌──────────┐   ┌──────────────┐   ┌─────────┐ │
│  │ Stage 1   │──▶│ Stage 2       │──▶│ Stage 3 │ │
│  │ Auto Scan │   │ Isolated      │   │ Human   │ │
│  │           │   │ Agent Review  │   │ Approval│ │
│  └──────────┘   └──────────────┘   └─────────┘ │
│       │                │                  │      │
│  Cross-ref DBs   READ-ONLY agent    Spike reviews│
│  (blocklists,    (no exec, no      final output  │
│   VirusTotal)     network, minimal  before publish│
│                   context window)                 │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│               STATIC SITE (GitHub Pages)         │
│                                                  │
│  /reviews/{skill-name}.md    — Individual review │
│  /categories/{category}.md   — Browse by goal    │
│  /data/skills.json           — Machine-readable  │
│  /data/blocklist.json        — Known bad skills  │
│  index.html                  — Landing page      │
└─────────────────────────────────────────────────┘
```

## Stage 2: Isolated Security Review Agent

**This is the critical piece.** The review agent is a spawned sub-agent with strict constraints:

### Constraints
1. **Read-only** — can only read files, never write or execute
2. **No execution** — cannot run scripts, install packages, or invoke skills
3. **No network** — cannot make web requests or API calls
4. **Minimal context** — receives ONLY the skill files + review template
5. **Isolated session** — separate from main agent, no access to workspace secrets
6. **Time-boxed** — max 5 minutes per review, killed if exceeded

### What the Review Agent Receives
```
INPUT:
  - SKILL.md content (the skill's instruction file)
  - Any referenced scripts (source code as text)
  - _meta.json (skill metadata)
  - REVIEW_TEMPLATE.md (scoring rubric)

OUTPUT:
  - Completed review in structured markdown
  - Trust score (safe/caution/avoid)
  - Permission analysis
  - Risk flags
```

### What the Review Agent CANNOT Do
- ❌ Run any code
- ❌ Install any packages
- ❌ Access the internet
- ❌ Read workspace files outside the skill being reviewed
- ❌ Access credentials, API keys, or secrets
- ❌ Modify any files
- ❌ Spawn sub-agents

### Implementation

The review agent is spawned via `sessions_spawn` with:
- A dedicated review-focused system prompt
- Only the skill source files passed as context in the task message
- Model: `deepseek` (cheap, sufficient for code analysis)
- Timeout: 300 seconds
- No tool access beyond basic text analysis

```
sessions_spawn(
  task: "Review this OpenClaw skill for safety and quality. {skill_content}",
  model: "deepseek",
  label: "skill-review-{skill-name}",
  runTimeoutSeconds: 300
)
```

The spawned agent has no file system access to the actual skill — it receives the skill content inline in the task prompt. Pure text analysis.

## Directory Structure

```
skillscout/
├── README.md                    # Landing page / about
├── ARCHITECTURE.md              # This file
├── REVIEW_TEMPLATE.md           # Scoring rubric for reviews
├── scripts/
│   ├── fetch-skill.sh           # Download skill source (text only)
│   ├── scan-blocklists.sh       # Stage 1 automated scan
│   └── generate-site.sh         # Build static site from reviews
├── reviews/
│   ├── rationality.md           # Individual skill reviews
│   ├── cognitive-memory.md
│   └── ...
├── categories/
│   ├── research.md
│   ├── memory.md
│   ├── security.md
│   └── ...
├── data/
│   ├── skills.json              # All reviewed skills (structured)
│   ├── blocklist.json           # Known malicious skills
│   └── categories.json          # Category definitions
├── site/                        # Generated static site
│   ├── index.html
│   └── ...
└── .github/
    └── workflows/
        └── deploy.yml           # GitHub Pages deployment
```

## Data Schema

### skills.json
```json
{
  "skills": [
    {
      "name": "rationality",
      "slug": "rationality",
      "author": "xertrov",
      "source": "clawhub",
      "sourceUrl": "https://github.com/openclaw/skills/tree/main/skills/xertrov/rationality",
      "category": "memory",
      "subcategory": "reasoning",
      "description": "Structured framework for critical thinking, error detection, and decision-making.",
      "plainDescription": "Helps your agent think more carefully and catch its own mistakes before acting.",
      "trustScore": "safe",
      "rating": 4.5,
      "permissions": ["read"],
      "risks": [],
      "installCommand": "npx clawhub@latest install rationality",
      "reviewDate": "2026-02-27",
      "reviewUrl": "/reviews/rationality"
    }
  ]
}
```

## Monetization (Future)

Phase 1 (now): Free, build trust and catalog
Phase 2 (500+ users): Featured listings from skill developers ($49-197/mo)
Phase 3 (1000+ users): API access for agents to query programmatically
Phase 4: Verification badges for skill developers ($99 one-time)

## Tech Stack

- **Static site**: GitHub Pages (Jekyll or plain HTML)
- **Data**: JSON files (no database needed)
- **Reviews**: Markdown files (human-readable, git-tracked)
- **CI/CD**: GitHub Actions (auto-build on push)
- **Cost**: $0/month (GitHub Pages free tier)
