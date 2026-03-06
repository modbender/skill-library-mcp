# god-mode Testing Checklist

## Pre-Flight Checks

### Environment Setup
- [ ] Running in OpenClaw environment (check `OPENCLAW_SERVICE_MARKER` is set)
- [ ] GitHub CLI installed: `gh --version`
- [ ] GitHub CLI authenticated: `gh auth status`
- [ ] sqlite3 available: `sqlite3 --version`
- [ ] jq available: `jq --version`
- [ ] yq available (optional): `yq --version`

### Clean Slate Test
```bash
# Start fresh for clean testing
rm -rf ~/.god-mode
rm -rf ~/.config/god-mode
```

## Core Functionality Tests

### 1. Setup Command
```bash
god setup
```

**Expected:**
- [x] Creates `~/.god-mode/` directory
- [x] Creates `~/.god-mode/logs/` directory
- [x] Creates `~/.config/god-mode/` directory
- [x] Initializes `~/.god-mode/cache.db`
- [x] Creates default `~/.config/god-mode/config.yaml`
- [x] Checks dependencies (gh, sqlite3, jq, yq)
- [x] Reports authentication status
- [x] Shows "Next steps" guidance

**Verify:**
```bash
ls -la ~/.god-mode
ls -la ~/.config/god-mode
sqlite3 ~/.god-mode/cache.db ".tables"
```

### 2. Projects Command

#### Add Project (GitHub)
```bash
god projects add github:InfantLab/tada
```

**Expected:**
- [ ] Validates repository exists via `gh api`
- [ ] Adds to config.yaml
- [ ] Suggests running `god sync`

**Verify:**
```bash
cat ~/.config/god-mode/config.yaml | grep tada
god projects list
```

#### Add Project (Azure DevOps)
```bash
god projects add azure:playtandem/ParentBench/ParentBench
```

**Expected:**
- [ ] Warns about Azure provider (or accepts it)
- [ ] Adds to config.yaml

#### List Projects
```bash
god projects
```

**Expected:**
- [ ] Shows all configured projects
- [ ] Displays project IDs clearly

#### Remove Project
```bash
god projects remove github:InfantLab/tada
```

**Expected:**
- [ ] Removes from config.yaml
- [ ] Confirms removal

### 3. Sync Command

#### Initial Sync (GitHub)
```bash
god sync github:InfantLab/tada
```

**Expected:**
- [ ] Shows "Full sync (90 days)" message
- [ ] Fetches commits (count shown)
- [ ] Fetches PRs (count shown, X open)
- [ ] Fetches issues (count shown, X open)
- [ ] Creates entries in database
- [ ] Logs activity to `~/.god-mode/logs/activity.log`

**Verify:**
```bash
sqlite3 ~/.god-mode/cache.db "SELECT COUNT(*) FROM commits WHERE project_id='github:InfantLab/tada';"
sqlite3 ~/.god-mode/cache.db "SELECT COUNT(*) FROM pull_requests WHERE project_id='github:InfantLab/tada';"
god logs -n 10
```

#### Incremental Sync
```bash
god sync github:InfantLab/tada
```

**Expected:**
- [ ] Shows "Cache valid" or "Incremental since X"
- [ ] Only fetches new data
- [ ] Faster than initial sync

#### Force Sync
```bash
god sync github:InfantLab/tada --force
```

**Expected:**
- [ ] Shows "Full sync (90 days)"
- [ ] Re-fetches all data
- [ ] Updates cache

#### Sync All Projects
```bash
god sync
```

**Expected:**
- [ ] Syncs all configured projects
- [ ] Shows summary at end
- [ ] Reports errors gracefully

#### Azure DevOps Sync
```bash
god sync azure:playtandem/ParentBench/ParentBench
```

**Expected:**
- [ ] Uses Azure provider
- [ ] Fetches commits, PRs
- [ ] Handles Azure state names ("active" not "open")

### 4. Status Command

#### Overview (All Projects)
```bash
god status
```

**Expected:**
- [ ] Shows all projects sorted by weekly commit activity
- [ ] Displays "This week: X commits • Y PRs • Z issues" per project
- [ ] Shows last commit timestamp and message
- [ ] Highlights commit counts > 0 in green
- [ ] Shows summary at bottom: total commits, total PRs
- [ ] Most active projects appear first

**Verify:**
```bash
# Most active project should be at top
god status | head -20
```

#### Single Project Detail
```bash
god status github:InfantLab/tada
```

**Expected:**
- [ ] Shows project name header
- [ ] Displays weekly stats (commits, authors, last activity)
- [ ] Lists open PRs (up to 5, with "...and N more")
- [ ] Lists open issues (up to 5)
- [ ] Shows recent commits (up to 5)
- [ ] Displays timestamps in relative format ("3d ago")

#### JSON Output
```bash
god status --json | jq
god status github:InfantLab/tada --json | jq
```

**Expected:**
- [ ] Valid JSON output
- [ ] Contains all expected fields
- [ ] No terminal formatting codes

### 5. Logs Command

#### View Recent Logs
```bash
god logs
```

**Expected:**
- [ ] Shows last 50 lines by default
- [ ] Timestamps in format: [YYYY-MM-DD HH:MM:SS]
- [ ] Log levels: COMMAND, INFO, ERROR
- [ ] Readable activity summary

#### Custom Line Count
```bash
god logs -n 100
```

**Expected:**
- [ ] Shows last 100 lines

#### Show Log Path
```bash
god logs --path
```

**Expected:**
- [ ] Outputs: `~/.god-mode/logs/activity.log`

#### Clear Logs
```bash
god logs --clear
```

**Expected:**
- [ ] Empties activity.log
- [ ] Shows success message

## Agent Analysis Tests

### 6. Agent Analysis (OpenClaw Mode)

#### Analyze Existing AGENTS.md
```bash
god agents analyze github:InfantLab/tada
```

**Expected:**
- [ ] Detects OpenClaw environment (shows "Using OpenClaw's LLM")
- [ ] Fetches AGENTS.md from remote repo
- [ ] Analyzes 155 commits (or actual count)
- [ ] Generates comprehensive prompt showing:
  - Complete AGENTS.md content
  - Commit type breakdown
  - Most changed files
  - Pain points
  - Commit samples
- [ ] Displays prompt to OpenClaw agent
- [ ] Saves prompt to `~/.god-mode/analysis-prompt.txt`
- [ ] Returns empty `{}` (normal for OpenClaw mode)
- [ ] Logs analysis start/complete

**Manual Test (as OpenClaw agent):**
- [ ] Read the displayed prompt
- [ ] Provide JSON response with gaps/strengths/recommendations
- [ ] Verify format matches expected schema

#### Analysis with No AGENTS.md
```bash
god agents analyze github:InfantLab/onemonkey  # repo without AGENTS.md
```

**Expected:**
- [ ] Reports "No agent file found"
- [ ] Lists files to create (agents.md, CLAUDE.md, etc.)
- [ ] Exits gracefully

#### Cached Analysis
```bash
# Run twice in a row
god agents analyze github:InfantLab/tada
god agents analyze github:InfantLab/tada
```

**Expected:**
- [ ] Second run shows "Using cached analysis"
- [ ] Faster execution
- [ ] Same results

#### Force Re-Analysis
```bash
god agents analyze github:InfantLab/tada --force
```

**Expected:**
- [ ] Ignores cache
- [ ] Re-analyzes fresh

### 7. Agent Analysis (Standalone Mode)

**Setup:**
```bash
# Temporarily unset OpenClaw marker
unset OPENCLAW_SERVICE_MARKER
export ANTHROPIC_API_KEY="sk-ant-..."  # Use real key for testing
```

```bash
god agents analyze github:InfantLab/tada
```

**Expected:**
- [ ] Detects API key
- [ ] Shows "Analyzing with Anthropic (Claude 3.5 Sonnet)"
- [ ] Calls Claude API
- [ ] Receives JSON response
- [ ] Displays gaps, strengths, recommendations
- [ ] Prompts to apply recommendations
- [ ] Caches LLM response

**Re-set OpenClaw mode:**
```bash
export OPENCLAW_SERVICE_MARKER="openclaw"
```

## OpenClaw Chat-First Tests

### 8. Conversational Workflow (Manual Tests)

These require you (OpenClaw agent) to execute based on user messages.

#### Test: New User Onboarding

**User says:** "Set up god-mode for my tada repository"

**You should:**
1. [ ] Run `god setup`
2. [ ] Run `god projects add github:InfantLab/tada`
3. [ ] Run `god sync github:InfantLab/tada`
4. [ ] Summarize results conversationally:
   - "Found 155 commits"
   - "30 commits this week"
   - "Most active repo!"

**Verify your response:**
- [ ] Natural language, not CLI commands
- [ ] Explains what was found
- [ ] Suggests next step ("Want me to analyze your agents.md?")

#### Test: Status Request

**User says:** "What's happening across my projects?"

**You should:**
1. [ ] Run `god status`
2. [ ] Translate output to conversation:
   - "Your most active repo is X with Y commits this week"
   - "Z repo hasn't seen activity in N days"
   - "You have M open PRs"

**Verify your response:**
- [ ] Not just echoing CLI output
- [ ] Conversational summary
- [ ] Highlights important info

#### Test: Agent Analysis Request

**User says:** "Analyze my agents.md for the tada project"

**You should:**
1. [ ] Run `god agents analyze github:InfantLab/tada`
2. [ ] Receive the analysis prompt
3. [ ] Provide JSON response with gaps/strengths/recommendations
4. [ ] Summarize conversationally
5. [ ] Offer to apply recommendations

**Verify your response:**
- [ ] Plain English explanation of gaps
- [ ] Concrete examples from commit history
- [ ] Actionable suggestions
- [ ] Asks if user wants to apply changes

## Error Handling Tests

### 9. Edge Cases & Errors

#### Invalid Repository
```bash
god projects add github:notexist/fakerepo
```

**Expected:**
- [ ] Shows "Checking repository..."
- [ ] Reports "Repository not found" or API error
- [ ] Does not add to config
- [ ] Exits with error code

#### Not Authenticated
```bash
gh auth logout
god sync github:InfantLab/tada
```

**Expected:**
- [ ] Detects auth failure
- [ ] Shows helpful message: "Run: gh auth login"
- [ ] Does not crash

**Re-authenticate:**
```bash
gh auth login
```

#### Database Corruption
```bash
rm ~/.god-mode/cache.db
god status
```

**Expected:**
- [ ] Detects missing database
- [ ] Recreates it automatically
- [ ] Shows "No data" or suggests running sync

#### No Projects Configured
```bash
# Remove all projects from config
god status
```

**Expected:**
- [ ] Shows "No projects configured"
- [ ] Suggests: "Add a project with: god projects add github:user/repo"
- [ ] Does not crash

#### Network Timeout
```bash
# Disconnect network, then:
god sync github:InfantLab/tada
```

**Expected:**
- [ ] Shows error message
- [ ] Does not crash
- [ ] Logs error

## Database Integrity Tests

### 10. Data Validation

#### Check Schema
```bash
sqlite3 ~/.god-mode/cache.db ".schema" | head -50
```

**Expected:**
- [ ] Tables: projects, commits, pull_requests, issues, sync_state, analyses, agent_files
- [ ] Proper foreign keys
- [ ] Indexes created

#### Verify Data Types
```bash
sqlite3 ~/.god-mode/cache.db "SELECT * FROM commits LIMIT 1;"
sqlite3 ~/.god-mode/cache.db "SELECT * FROM projects LIMIT 1;"
```

**Expected:**
- [ ] Timestamps are Unix epoch integers
- [ ] JSON fields are valid JSON
- [ ] No NULL in required fields

#### Check Logs Integrity
```bash
god logs -n 1000 | grep ERROR
```

**Expected:**
- [ ] No unexpected errors
- [ ] All operations logged
- [ ] Timestamps sequential

## Performance Tests

### 11. Speed & Efficiency

#### Large Repo Sync
```bash
# Sync a repo with 1000+ commits
time god sync github:InfantLab/brain --force
```

**Expected:**
- [ ] Completes in reasonable time (<2 minutes)
- [ ] Shows progress indicators
- [ ] No memory issues

#### Status with Many Projects
```bash
# Add 10+ projects, then:
time god status
```

**Expected:**
- [ ] Displays quickly (<5 seconds)
- [ ] Sorted correctly
- [ ] All data shown

## Integration Tests

### 12. Multi-Provider Workflow

```bash
# Mix of GitHub and Azure
god projects add github:InfantLab/tada
god projects add azure:playtandem/ParentBench/ParentBench
god sync
god status
```

**Expected:**
- [ ] Both providers work
- [ ] Status shows both correctly
- [ ] Different state names handled ("active" vs "open")

### 13. Full Workflow Test

```bash
# Complete user journey
god setup
god projects add github:InfantLab/tada
god sync
god status
god status github:InfantLab/tada
god agents analyze github:InfantLab/tada
god logs
```

**Expected:**
- [ ] All commands work sequentially
- [ ] Data persists between commands
- [ ] No errors or warnings
- [ ] Activity logged

## Cleanup

```bash
# Remove test data if needed
rm -rf ~/.god-mode
rm -rf ~/.config/god-mode
```

## Test Results Summary

**Date:** ___________
**Tester:** ___________
**Environment:** OpenClaw / Standalone

### Pass/Fail Summary
- Setup: ___/___
- Projects: ___/___
- Sync: ___/___
- Status: ___/___
- Logs: ___/___
- Agent Analysis: ___/___
- Chat-First Workflow: ___/___
- Error Handling: ___/___
- Database: ___/___
- Performance: ___/___

### Issues Found
1. 
2. 
3. 

### Notes
