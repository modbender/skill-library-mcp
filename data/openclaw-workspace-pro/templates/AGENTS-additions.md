

## 📦 Artifact Workflow

When producing deliverables (reports, code, datasets, exports):

**Standard Output Location:** `/data/.openclaw/workspace/artifacts/`

**Structure:**
- `artifacts/reports/` — analysis reports, summaries, documentation
- `artifacts/code/` — generated scripts, apps, configuration files
- `artifacts/data/` — cleaned datasets, processed files
- `artifacts/exports/` — exports from tools (database dumps, API responses)

**Pattern:**
1. Write all deliverables to the appropriate artifacts subdirectory
2. Use descriptive filenames with dates: `YYYY-MM-DD-project-name-description.ext`
3. Log artifact location in daily memory
4. **Treat artifacts as review boundaries** — don't auto-deploy or auto-send without approval

**Example:**
```
artifacts/reports/2026-02-13-jigsaw-compliance-analysis.md
artifacts/code/2026-02-13-youtube-transcript-fetcher.py
artifacts/data/2026-02-13-task-export.csv
```

**Why:** Clean handoff boundary, easy retrieval, version tracking, explicit review point.

## 🔄 Long-Running Work Pattern

For multi-step tasks that span multiple messages or sessions:

**Container Reuse:**
- You're already in a persistent Docker container — use it!
- Install dependencies once, reuse across steps
- Write intermediate outputs to workspace files
- Don't restart from scratch each time

**Continuity Protocol:**
1. **Log progress** in daily memory after each major step
2. **Use Vikunja** for task tracking across sessions (create tasks, update status)
3. **Checkpoint artifacts** before major transitions (write to `/artifacts/`)
4. **Document decisions** in MEMORY.md for long-term recall
5. **Reference previous work** by reading workspace files, not relying on chat history

**Multi-Day Work:**
- Day 1: Research, plan, document in daily memory
- Day 2: Read yesterday's memory, continue where you left off
- Day 3+: Same pattern — memory files are your continuity

**Example Flow:**
```
1. Task starts: Create Vikunja task, log in daily memory
2. Step 1 done: Write intermediate output to workspace, log progress
3. Step 2 done: Write artifact to /artifacts/, update Vikunja
4. Final: Mark Vikunja task complete, summarize in MEMORY.md
```

## 🔒 Secrets Management

**Rule:** Never store API keys, tokens, or passwords in plaintext in committed files.

**Pattern:**
- Secrets live in `.env` file (gitignored)
- Reference as `$VARIABLE_NAME` in documentation
- Load from environment variables at runtime
- TOOLS.md documents what secrets exist, not their values

**Current .env secrets:**
- (List your secrets here as you add them)

**Never:**
- Commit `.env` to git
- Paste raw secrets in chat logs
- Include secrets in artifacts meant for sharing
