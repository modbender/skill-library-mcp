# OpenClaw Skill: Intelligence Ingestion

> You're feeding something smarter than you.
> This Skill makes sure you know what it ate, and what it became.

**Zero-loss information ingestion pipeline** — Analyze URLs, articles, and tweets for strategic value. Classify, score, store structured notes in **Obsidian**, and update the **Strategic Landscape** capability map.

## Why This Skill?

Most people collect information but never process it. They bookmark 100 links and read 3.

This Skill flips the model: **every piece of information is analyzed, classified, scored, and mapped to your system before it enters your knowledge base.** You always know what your Agent learned and how its capabilities changed.

## Core Flow

```
READ → CLASSIFY → ANALYZE → MAP → STORE → SYNTHESIZE → REMEMBER → RESPOND
```

8-step pipeline. From "I saw it" to "my Agent literally learned a new ability." Zero information loss.

## Prerequisites

| Tool | Purpose | Required? |
|------|---------|-----------|
| **Obsidian** | Knowledge storage (notes land here) | ✅ Required |
| **OpenClaw** | Skill host + Agent orchestration | ✅ Required |
| **Chrome** | For reading login-required pages (X/Twitter) | 🟡 Recommended |

## Quick Start

```bash
# 1) Install
openclaw skills install github:sarahmirrand001-oss/openclaw-skill-intelligence-ingestion

# 2) Configure
cp config.example.json config.json
# Edit config.json — set your Obsidian Vault path

# 3) Initialize Strategic Landscape (optional, auto-created on first use)
cp STRATEGIC_LANDSCAPE.template.md /path/to/your/workspace/STRATEGIC_LANDSCAPE.md

# 4) Use it — just share a link
"Analyze this: https://example.com/article"

# 5) Verify
ls /path/to/your/Obsidian_Vault/20_Intelligence/
# You should see a new note with today's date
```

## What It Produces

Each ingestion creates:
- 📄 **Structured Obsidian note** (category + strategic value score + capability change)
- 📝 **Daily memory log update**
- 🗺️ **Strategic Landscape update** (for critical information)
- 🔄 **Capability boundary assessment** (what can your Agent do now that it couldn't before?)
- 🧬 **Auto-generated Skill draft** (when a new usable capability is detected)

## 🧬 Auto-Skill Synthesis

The killer feature: when the ingested content describes a **usable tool, API, or protocol** that your Agent doesn't have yet, the pipeline automatically generates a draft `SKILL.md` file.

```
You share a link about Firecrawl API
  → Intelligence Ingestion analyzes it
  → Detects: "Agent doesn't have structured web scraping yet"
  → Auto-generates: skills/_drafts/firecrawl-scraper/SKILL.md
  → You review → move to skills/ → Agent can now do it
```

**Safety boundary:** Drafts land in `skills/_drafts/` and are NOT auto-loaded. You must review and approve before the Agent gains the capability.

## File Structure

```
intelligence-ingestion/
├── SKILL.md                          # Skill behavior + 8-step pipeline
├── README.md                         # This file
├── manifest.json                     # MCP-compatible capability declaration
├── config.example.json               # Configuration template (copy to config.json)
├── config.json                       # Your local config (gitignored)
├── STRATEGIC_LANDSCAPE.template.md   # Landscape template for first-time setup
├── index.html                        # Public landing page (deployable to Vercel)
└── vercel.json                       # Static deployment config
```

## 🛡️ Trust, Safety & Permissions

> *"giving my private data/keys to 400K lines of vibe coded monster is not very appealing at all"* — Andrej Karpathy

This Skill is designed with security and transparency as first-class concerns:

- **No self-modification**: Agent cannot install its own synthesized Skills. All drafts require human review.
- **Isolation**: Auto-generated Skills land in `_drafts/`, never in the active `skills/` directory.
- **Auditability**: Every ingestion is logged. Every Skill draft includes its source URL and generation date.
- **Transparency**: Full `manifest.json` declares exactly what this Skill can read, write, and produce.

### What This Skill Writes

| Target | Path | When |
|--------|------|------|
| Obsidian notes | `{vault}/{intelligence_folder}/` | Every ingestion |
| Memory logs | `{workspace}/memory/` | Every ingestion |
| Strategic Landscape | `{workspace}/STRATEGIC_LANDSCAPE.md` | When info is rated Critical |
| Skill drafts | `{workspace}/skills/_drafts/` | When a new capability gap is detected |

### Network Behavior

- The Skill fetches content from user-provided URLs via HTTP.
- The "never return empty-handed" policy means the Skill may make **multiple external requests** per ingestion (direct fetch → xurl API → web search).
- All fetched content is stored **locally** in your Obsidian vault. No data is sent to third-party servers beyond the original URL fetch.

### Before You Install

1. Ensure your `obsidian_vault_path` in `config.json` is correct and backed up.
2. Review any auto-generated Skill drafts carefully before moving them from `_drafts/` to `skills/`.
3. Consider running with a read-only vault copy if you want to test first.

## 🔌 MCP Compatibility

This Skill ships with `manifest.json` — a machine-readable capability declaration following the MCP (Model Context Protocol) standard.

This means:
- ✅ Any MCP-compatible Agent can **discover** this Skill
- ✅ Any MCP-compatible Agent can **understand** its inputs/outputs without reading SKILL.md
- ✅ Cross-ecosystem compatibility (not locked to OpenClaw)

## Companion: Strategic Landscape

Intelligence Ingestion is not standalone — it works with a **Strategic Landscape** (capability map):

- **Intelligence Ingestion** = the "input" for information
- **Strategic Landscape** = the "map" of your system

Every critical piece of information automatically updates the Landscape, so you always see your Agent's full capability picture — what it can do, what's in progress, what's missing.

## X/Twitter Support

X has aggressive anti-scraping. This Skill uses a 4-level fallback chain:

1. **xurl Skill** (OpenClaw built-in) → Authenticated X API v2 access
2. **Web search** → Search engine cache
3. **User paste** → Last resort

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill doesn't trigger when I share a URL | Start a new session (Skills snapshot is cached per session) |
| Obsidian note not created | Check `config.json` — is `obsidian_vault_path` correct? Does the folder exist? |
| X/Twitter link fails | Ensure `xurl` is configured, or log into X in Chrome |
| "config.json not found" | Run `cp config.example.json config.json` and edit paths |
| Strategic Landscape not updating | Check `landscape_path` in config.json matches your actual file location |

## Upgrade

```bash
# Pull latest version
openclaw skills install github:sarahmirrand001-oss/openclaw-skill-intelligence-ingestion

# Your config.json is gitignored, so it won't be overwritten
```

## Deploy Landing Page

```bash
vercel --prod
```

---

*Built for pragmatic operators who build for agents. No hype, no fluff, only strategic signal.*

*"Skills are the new Config. Build. For. Agents."*
