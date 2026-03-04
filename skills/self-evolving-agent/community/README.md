# 🏪 Proposal Marketplace

> **Community-curated AGENTS.md improvement proposals — battle-tested, peer-reviewed, ready to install.**

The Proposal Marketplace is a collection of improvement rules discovered by real agents running in production. Each proposal represents a real failure mode, a real fix, and real evidence that it works.

---

## 📦 Browsing Proposals

```
community/proposals/
├── exec-retry-limit.json        ⭐ HIGH severity — prevents 119× retry loops
├── context-preservation.json    ⭐ HIGH severity — WAL protocol, zero state loss
├── git-safety.json              ⭐ HIGH severity — never raw git commands
├── error-suppression.json       ⭐ HIGH severity — exec never exposes errors
├── heartbeat-efficiency.json    📊 MEDIUM severity — batch checks, 72% cost reduction
├── memory-hygiene.json          📊 MEDIUM severity — weekly MEMORY.md cleanup
├── group-chat-etiquette.json    📊 MEDIUM severity — when to speak vs stay silent
├── tool-before-asking.json      📊 MEDIUM severity — check before asking
├── cron-isolation.json          ⭐ HIGH severity — no message tool in isolated crons
└── approval-protocol.json       ⭐ HIGH severity — record proposals before presenting
```

---

## 🚀 Future: `sea community` Subcommand

> **Coming soon** — CLI interface for browsing and installing community proposals.

```bash
# List all community proposals
sea community list

# List by category
sea community list --category safety
sea community list --severity high

# View a proposal
sea community show exec-retry-limit

# Install a proposal into your AGENTS.md
sea community install exec-retry-limit

# Install all high-severity proposals
sea community install --severity high

# Submit your own proposal
sea community submit ./my-proposal.json

# Rate a proposal
sea community vote exec-retry-limit --up

# Show most popular proposals
sea community top --limit 10
```

The `install` command automatically appends the proposal's `after` content into the appropriate section of your AGENTS.md, with a comment linking back to the source proposal.

---

## 📋 Proposal Schema

Every proposal must conform to this schema:

```json
{
  "id": "kebab-case-unique-identifier",
  "title": "Human-readable title",
  "description": "What problem does this solve? Why does it matter?",
  "severity": "high | medium | low",
  "category": "safety | memory | efficiency | ux | communication",
  "tags": ["relevant", "searchable", "tags"],
  "before": "Code/text showing the problematic pattern",
  "after": "## Rule Title\n\nThe actual AGENTS.md content to install",
  "evidence": "What real-world incident or data motivated this?",
  "effectiveness": "Quantified improvement after adoption",
  "contributed_by": "github_username or alias",
  "contributed_at": "YYYY-MM-DD",
  "upvotes": 0,
  "schema_version": "1.0"
}
```

---

## ✅ How to Contribute

### 1. Discover a Pattern

Run your agent. Notice something failing repeatedly. Fix it. Document the fix.

### 2. Write the Proposal

Use the schema above. Your proposal must have:
- **Real evidence**: A specific incident, log, or measurement — not "this seems useful"
- **Before/after**: Show the problematic pattern and the fix
- **Effectiveness**: Quantified improvement. "Much better" is not acceptable. "97% reduction in retry events" is.
- **Generalizability**: Does this apply to most agents, or just your specific setup?

### 3. Quality Bar

Your proposal will be reviewed against these criteria:

| Criterion | Pass | Fail |
|-----------|------|------|
| Real incident | Specific log/event cited | "This could happen" |
| Before/after | Concrete code/text examples | Vague description |
| Effectiveness | Measured improvement | "Feels better" |
| Generalizability | Applies to 80%+ of agents | Only for your setup |
| AGENTS.md-ready | `after` field is paste-ready | Rough draft |

### 4. Submit

```bash
# Via CLI (coming soon)
sea community submit ./my-proposal.json

# Via GitHub (now)
# Fork the repo, add your JSON to community/proposals/
# Open a PR with title: "Proposal: [id]"
```

---

## 🗳️ Voting System

Each proposal has an `upvotes` field. The community votes by:
- **Upvoting** proposals they've adopted and verified effective
- **Reporting** proposals that didn't work (creates a counter-signal)

Proposals with high upvotes and strong evidence become **Featured** and are recommended first during `sea community list`.

### Scoring Formula (v1)

```
score = upvotes × severity_weight × effectiveness_score
severity_weight: high=3, medium=2, low=1
effectiveness_score: % improvement / 100 (e.g., 0.97 for "97% reduction")
```

---

## 🏷️ Categories

| Category | Description |
|----------|-------------|
| `safety` | Prevents data loss, crashes, or unrecoverable states |
| `memory` | Improves agent memory, persistence, and recall |
| `efficiency` | Reduces API costs, token usage, or execution time |
| `ux` | Improves the user experience with the agent |
| `communication` | Rules for messaging, group chats, and platform etiquette |

---

## ⚖️ Governance

- Proposals are community-contributed but **curated by maintainers**
- Any proposal that involves sending external messages, credentials, or destructive actions requires elevated review
- Proposals are immutable after merging — corrections create a new versioned proposal
- The `contributed_by` field is for attribution only, not authority — anyone can improve on existing proposals

---

*The Proposal Marketplace is the community flywheel of self-evolving-agent. See [docs/community-strategy.md](../docs/community-strategy.md) for the full vision.*
