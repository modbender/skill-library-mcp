# Analysis Checks by Category

## Workspace

### Files & Structure
- [ ] Required files exist: SOUL.md, USER.md, AGENTS.md, TOOLS.md, MEMORY.md
- [ ] memory/ folder structure valid, INDEX.md up to date
- [ ] No orphaned memory files (exist but not indexed)
- [ ] BOARD.md and BACKLOG.md not bloated (>100 lines of stale entries)
- [ ] No secrets in plaintext files (.env with real values, hardcoded credentials)
- [ ] No secrets accidentally committed to git history

### Memory Health
- [ ] Memory files not duplicating information across dates
- [ ] Recent entries being consolidated into MEMORY.md
- [ ] memory/*.md files parseable (no broken markdown)
- [ ] Total memory size reasonable (<5MB unless justified)

---

## Config

### Credentials
- [ ] Keychain secrets referenced in secrets-registry.json actually exist
- [ ] API tokens not expired (Cloudflare, Hetzner, etc.)
- [ ] SSH keys have correct permissions (600, not world-readable)
- [ ] VPN configuration exists and matches expected servers

### Gateway & Cron
- [ ] OpenClaw gateway service running and healthy
- [ ] Cron jobs have valid schedules (no syntax errors)
- [ ] No timing conflicts (multiple jobs same minute causing contention)
- [ ] Recent cron executions completed without errors
- [ ] Heartbeat interval appropriate for activity level

### Sessions
- [ ] No zombie subagent sessions (spawned >24h ago, no completion)
- [ ] Active session count reasonable (not hundreds)
- [ ] No sessions with error states that weren't handled

---

## Skills

### Installation & Health
- [ ] Installed skills have valid SKILL.md files
- [ ] No duplicate or conflicting skill triggers
- [ ] Skill dependency chains valid (if A calls B, B exists)
- [ ] EXTRA_FILES.txt references all exist

### Usage Efficiency
- [ ] Skills being loaded aren't causing redundant file reads
- [ ] No skills with broken external references (dead URLs, missing binaries)

---

## Integrations

### APIs & Services
- [ ] Configured APIs reachable (Brave, Telegram, etc.)
- [ ] Bot tokens valid (can authenticate)
- [ ] Rate limits not being hit chronically
- [ ] Webhook endpoints responding

### Resources & Performance
- [ ] Token usage patterns normal (no sudden 3x spikes)
- [ ] Model routing following defined rules (Haiku/Sonnet/Opus split)
- [ ] Browser sessions not accumulating (zombie tabs)
- [ ] No redundant tool calls (same file read 5x in one conversation)

### Nodes & External
- [ ] Paired nodes reachable
- [ ] Server SSH connections working
- [ ] Docker services on servers healthy (if applicable)

---

## Detection Methods

| Check Type | Method | Cost |
|------------|--------|------|
| File existence/size/age | `ls`, `stat`, `find` | Free |
| File content patterns | `grep`, `head`, `read` | Free |
| Process/service status | `ps`, `docker ps`, `launchctl` | Free |
| Git status | `git status`, `git log` | Free |
| API health | `curl` with timeout | Cheap |
| Full API validation | Authenticated requests | Expensive |

Always try free methods first. Only escalate to expensive checks when free methods indicate a problem.
