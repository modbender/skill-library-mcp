# god-mode OpenClaw Skill: Agent Handover

**Last Updated:** 2026-01-31
**Status:** Pre-development, architecture complete
**Goal:** Build MVP in ~14 hours

---

## What We're Building

An OpenClaw skill that gives developers a **bird's-eye view** of all their coding projects and **coaches them to write better AI agent instructions**.

**Target users:** Solo devs, vibecoders, anyone juggling multiple repos who uses AI coding assistants.

**The hook:** "Make your AI coding assistant smarter by analyzing your actual work patterns."

---

## MVP Commands (v0.1.0)

### 1. `god status` - Project Overview
Shows all configured projects at a glance:
```
🔭 god-mode

tandem-evaluator
  Last: 2h ago • fix: evaluation metrics
  PRs: 2 open (1 needs review) • Issues: 5

tada  
  Last: 1d ago • feat: API endpoints
  PRs: 0 • Issues: 3
  
content-engine ⚠️
  Last: 5d ago • No activity
  PRs: 1 stale • Issues: 8

This week: 23 commits • 3 PRs merged
```

### 2. `god sync` - Fetch/Update Data
Incrementally syncs data from configured repos:
```
god sync              # All projects
god sync tandem       # Just one
god sync --force      # Full refresh
```

### 3. `god projects` - List Configuration
```
god projects          # Show configured projects
god projects add github:user/repo
god projects remove tandem
```

### 4. `god agents analyze` - The Killer Feature
Analyzes your agents.md against your commit history:
```
🧠 Analyzing tandem-evaluator...

⚠️ GAPS FOUND

Testing (not mentioned)
  But 31% of your commits touch tests
  → Add: "Write tests for new code"

Error handling (vague)  
  12 commits fixing error handling
  → Add: "Use typed errors, include context"

✅ WORKING WELL

"TypeScript strict mode" → 0 type errors

📝 SUGGESTED ADDITIONS

## Testing
- Unit tests for all new functions
- Run tests before commits
```

---

## Architecture

### Credential Strategy: Delegate to Native CLIs

**We never store tokens.** Use CLIs users already authenticated:

| Provider | CLI | Auth Check |
|----------|-----|------------|
| GitHub | `gh` | `gh auth status` |
| Azure DevOps | `az` | `az account show` |
| GitLab | `glab` | `glab auth status` |

Fallback: `GITHUB_TOKEN`, `AZURE_DEVOPS_PAT`, `GITLAB_TOKEN` env vars.

### Data Storage: SQLite

**Location:** `~/.god-mode/cache.db`

```sql
-- Core tables
providers       -- CLI auth status (not tokens!)
projects        -- Configured repos  
commits         -- Cached commits (incremental)
pull_requests   -- Cached PRs
issues          -- Cached issues
agent_files     -- Agent file snapshots (for diff)
analyses        -- Cached LLM results
sync_state      -- Last sync timestamps per project
```

### Provider Abstraction

Each provider implements:
```bash
provider_check_auth()                    # -> {available, authenticated, user}
provider_list_repos()                    # -> [{id, name, url}]
provider_fetch_commits(repo, since)      # -> [{sha, author, message, date}]
provider_fetch_prs(repo, state)          # -> [{number, title, state, author}]
provider_fetch_issues(repo, state)       # -> [{number, title, state, labels}]
```

**MVP:** GitHub only. Azure/GitLab stubbed with interface.

### Configuration

**User config:** `~/.config/god-mode/config.yaml`

```yaml
projects:
  - github:user/repo
    name: My Project        # Optional display name
    priority: high          # high/medium/low
    tags: [work, ai]
    local: ~/code/myproject # Optional local path

sync:
  initialDays: 90           # First sync lookback
  commitsCacheMinutes: 60
  prsCacheMinutes: 15

analysis:
  agentFiles:               # Patterns to search
    - agents.md
    - AGENTS.md
    - CLAUDE.md
    - .github/copilot-instructions.md
    - .cursorrules
```

---

## File Structure

```
god-mode-skill/
├── SKILL.md                    # OpenClaw agent instructions
├── README.md                   # Human documentation
├── config.example.yaml
│
├── scripts/
│   ├── god                     # Main entry point (routes commands)
│   ├── setup.sh                # First-run setup
│   │
│   ├── commands/
│   │   ├── status.sh
│   │   ├── sync.sh
│   │   ├── projects.sh
│   │   └── agents.sh
│   │
│   └── lib/
│       ├── config.sh           # Config loading (YAML → env)
│       ├── db.sh               # SQLite operations
│       ├── output.sh           # Colors, formatting
│       │
│       ├── providers/
│       │   ├── base.sh         # Interface definition
│       │   ├── github.sh       # GitHub via gh CLI
│       │   ├── azure.sh        # Stubbed
│       │   └── gitlab.sh       # Stubbed
│       │
│       └── analysis/
│           ├── patterns.sh     # Extract commit patterns
│           └── agents.sh       # Agent file analysis
│
├── sql/
│   └── schema.sql              # Database schema
│
└── prompts/
    └── agent-analysis.md       # LLM prompt for gap detection
```

---

## Implementation Tasks

### Phase 1: Foundation (~4 hours)

#### T1.1: Project Scaffold
- [ ] Create directory structure above
- [ ] Write `scripts/god` entry point (command router)
- [ ] Create `config.example.yaml`

#### T1.2: Database Layer
- [ ] Write `sql/schema.sql` with tables above
- [ ] Implement `lib/db.sh`:
  - `db_init()` - Create database if not exists
  - `db_query()` - Run SQL, return results
  - `db_upsert_project()` - Insert/update project
  - `db_upsert_commits()` - Batch insert commits
  - `db_get_sync_state()` - Get last sync timestamp
  - `db_set_sync_state()` - Update sync timestamp

#### T1.3: Config Layer
- [ ] Implement `lib/config.sh`:
  - `config_load()` - Parse YAML config
  - `config_get_projects()` - List configured projects
  - `config_get_project()` - Get single project config
- [ ] Use `yq` for YAML parsing (or pure bash if simple)

#### T1.4: GitHub Provider
- [ ] Implement `lib/providers/github.sh`:
  - `github_check_auth()` - Check `gh auth status`
  - `github_fetch_commits()` - `gh api repos/{}/commits`
  - `github_fetch_prs()` - `gh pr list --json`
  - `github_fetch_issues()` - `gh issue list --json`

### Phase 2: Core Commands (~4 hours)

#### T2.1: `god sync`
- [ ] Implement `commands/sync.sh`:
  - Load config
  - For each project: check provider, fetch incremental data
  - Store in SQLite
  - Update sync_state
  - Report: "Synced N projects, M new commits"

#### T2.2: `god status`
- [ ] Implement `commands/status.sh`:
  - Query SQLite for latest data per project
  - Calculate stats (commits this week, open PRs, etc.)
  - Format output with colors
  - Show warnings for stale projects

#### T2.3: `god projects`
- [ ] Implement `commands/projects.sh`:
  - `god projects` - List all with status
  - `god projects add <uri>` - Add to config
  - `god projects remove <name>` - Remove from config

### Phase 3: Agent Analysis (~4 hours)

#### T3.1: Agent File Detection
- [ ] Implement `lib/analysis/agents.sh`:
  - `find_agent_file(project)` - Search for agents.md etc.
  - `hash_agent_file(path)` - MD5/SHA for cache invalidation
  - `get_agent_content(project)` - Read and return content

#### T3.2: Commit Pattern Extraction
- [ ] Implement `lib/analysis/patterns.sh`:
  - `extract_commit_types(project)` - feat/fix/test/docs breakdown
  - `extract_file_patterns(project)` - Which files change most
  - `extract_churn_commits(project)` - Reverts, "fix typo", etc.
  - `build_pattern_summary(project)` - JSON for LLM prompt

#### T3.3: LLM Prompt
- [ ] Write `prompts/agent-analysis.md`:
  - Template with project context
  - Current agent file content
  - Commit pattern summary
  - Instructions for gap detection
  - Output format (JSON with recommendations)

#### T3.4: `god agents analyze`
- [ ] Implement `commands/agents.sh`:
  - Check analysis cache (valid if agent file unchanged)
  - Build prompt from template + data
  - Call LLM (write to stdout, OpenClaw handles it)
  - Cache result
  - Format and display recommendations

### Phase 4: Polish (~2 hours)

#### T4.1: Output Formatting
- [ ] Implement `lib/output.sh`:
  - Color helpers (red, green, yellow, bold)
  - Box drawing for sections
  - Progress indicators
  - Error formatting

#### T4.2: Error Handling
- [ ] Graceful errors for:
  - `gh` CLI not installed
  - Not authenticated
  - Network failures
  - No projects configured
- [ ] Helpful suggestions in error messages

#### T4.3: Documentation
- [ ] Write `SKILL.md` for OpenClaw agents
- [ ] Write `README.md` with:
  - Installation
  - Quick start
  - Configuration reference
  - Command reference
  - Examples

#### T4.4: First-Run Experience
- [ ] Implement `setup.sh`:
  - Create config directory
  - Initialize database
  - Check for `gh` CLI
  - Guide through adding first project

---

## Key Files to Reference

### Existing god-mode Python CLI
**Location:** `/home/caddy/god-mode/`

Useful for:
- `prompts/` - LLM prompt templates (can adapt)
- `god_mode/analyzers/` - Analysis logic (reference)
- `README.md` - Feature ideas

### Architecture Docs
- `/home/caddy/openclaw/god-mode-strategy.md` - Strategic analysis
- `/home/caddy/openclaw/god-mode-architecture.md` - Full architecture
- `/home/caddy/openclaw/god-mode-skill-plan.md` - Roadmap

### OpenClaw Skill Examples
- `/home/caddy/.npm-global/lib/node_modules/openclaw/skills/` - Existing skills

---

## Dependencies

**Required:**
- `gh` - GitHub CLI (authenticated)
- `sqlite3` - Database
- `jq` - JSON processing

**Optional:**
- `yq` - YAML parsing (or use simple grep/awk)
- `glab` - GitLab CLI (for future)
- `az` - Azure CLI (for future)

---

## Testing Checklist

### Manual Testing Flow
1. `god setup` - Should create config dir and database
2. `god projects add github:octocat/Hello-World` - Should add to config
3. `god sync` - Should fetch commits, PRs, issues
4. `god status` - Should show project overview
5. `god agents analyze` - Should analyze (if agents.md exists)

### Edge Cases
- [ ] No `gh` CLI installed
- [ ] `gh` not authenticated
- [ ] No projects configured
- [ ] Project has no commits
- [ ] Project has no agents.md
- [ ] Network timeout during sync
- [ ] Large repo (1000+ commits)

---

## Design Decisions

### Why Shell Scripts?
- Zero dependencies beyond standard CLI tools
- Easy for community to contribute
- Portable across platforms
- OpenClaw skills are typically shell-based

### Why SQLite?
- Single file, no server
- Incremental updates natural
- Fast queries for dashboards
- Easy backup/portability

### Why Delegate Auth to CLIs?
- Users already authenticated these tools
- We inherit their security (keychain, SSO, 2FA)
- No token storage = no token leaks
- Simpler code

### Why Cache Analysis Results?
- LLM calls are slow/expensive
- Agent files don't change often
- Invalidate on content hash change
- Force refresh available

---

## Future Roadmap (Post-MVP)

### v0.2.0 - Context & Activity
- `god context save/restore` - Workspace context
- `god today/week` - Activity summaries
- `god agents generate` - Bootstrap new projects

### v0.3.0 - Proactive
- Heartbeat integration
- Daily briefing agent
- Stale PR alerts

### v1.0.0 - Platform
- Full Azure DevOps support
- Full GitLab support
- Cross-project intelligence
- Integration ecosystem

---

## Questions for Implementing Agent

If unclear on anything:
1. Check architecture docs in `/home/caddy/openclaw/`
2. Reference existing Python CLI in `/home/caddy/god-mode/`
3. Look at other OpenClaw skills for patterns
4. Ask - don't assume

**Priority:** Ship clean MVP. Don't over-engineer, but don't cut corners on:
- Security (never store tokens)
- Extensibility (provider abstraction)
- Caching (incremental sync)

---

*Ready to build. Start with Phase 1: Foundation.*
