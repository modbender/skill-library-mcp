---
name: honcho-memory-mux-setup
description: >
  Install and enable Honcho + the @alloralabs/honcho-memory-mux extension,
  migrate legacy file memory, and update workspace instructions so agents use
  memory via Honcho-first multiplexed retrieval with local-file fallback.
metadata:
  openclaw:
    emoji: "🧠"
    optional_env:
      - name: HONCHO_API_KEY
        description: "API key. Optional for many local/self-hosted setups."
      - name: HONCHO_BASE_URL
        description: "Base URL for self-hosted Honcho (example: http://localhost:8000)."
      - name: HONCHO_WORKSPACE_ID
        description: "Honcho workspace ID (default: openclaw)."
      - name: WORKSPACE_ROOT
        description: "OpenClaw workspace root. Auto-detected if unset."
    required_binaries:
      - node
      - npm
    optional_binaries:
      - git
      - docker
      - docker-compose
    writes_to_disk: true
    network_access:
      - "User-configured HONCHO_BASE_URL (self-hosted mode)"
  homepage: "https://honcho.dev"
  source:
    - "https://github.com/plastic-labs/honcho"
    - "https://github.com/allora-network/honcho-memory-mux"
---

# Honcho + Memory Mux Setup

This skill installs and enables:
1) `@honcho-ai/openclaw-honcho` (Honcho tools + integration)
2) `@alloralabs/honcho-memory-mux` (multiplexed memory behavior)

Then it migrates legacy memory files, updates agent docs, and validates runtime behavior.

---

## What “memory mux” means in practice

After setup, memory behavior should be:
- **Primary retrieval:** Honcho tools (`honcho_context`, `honcho_search`, etc.)
- **Secondary retrieval:** local memory files (`MEMORY.md`, `memory/*.md`) via `memory_search` / `memory_get`
- **Durability:** pre-compaction flush writes significant session learnings to `memory/YYYY-MM-DD.md`
- **Fallback safety:** if Honcho is unavailable, file-based memory still works

This is intentionally **complementary**, not a hard cutover.

---

## Step 0: Preflight and safety checks

Before doing anything destructive:
- Resolve workspace root from:
  1. `WORKSPACE_ROOT`
  2. `~/.openclaw/openclaw.json` (`agent.workspace` or `agents.defaults.workspace`)
  3. `~/.openclaw/workspace`
- Confirm directory exists
- Inform user this process can upload memory files to Honcho

---

## Step 1: Install + enable Honcho plugin

Use OpenClaw plugin manager (not workspace `npm install`):

```bash
openclaw plugins install @honcho-ai/openclaw-honcho
openclaw plugins enable openclaw-honcho
```

If gateway logs show missing SDK deps:

```bash
cd ~/.openclaw/extensions/openclaw-honcho
npm install
```

Restart gateway if required.

---

## Step 2: Install + enable memory mux extension

Install and enable the memory-mux extension:

```bash
openclaw plugins install @alloralabs/honcho-memory-mux
openclaw plugins enable @alloralabs/honcho-memory-mux
```

If the extension is local/unpublished, install from path or git URL per your release flow.

After enabling:
- Verify plugin appears in `openclaw plugins list`
- Verify gateway boots cleanly (no extension load errors)
- Verify both Honcho tools and `memory_search` / `memory_get` are present at runtime

---

## Step 3: Verify Honcho connectivity (self-hosted)

- Set `HONCHO_BASE_URL` (example: `http://localhost:8000`)
- `HONCHO_API_KEY` may be optional depending on auth config

If user needs local Honcho quickly:

```bash
git clone https://github.com/plastic-labs/honcho
cd honcho
cp .env.template .env
cp docker-compose.yml.example docker-compose.yml
docker compose up -d
```

Do not migrate until connection is verified.

---

## Step 4: Detect and classify legacy memory files

Scan workspace for:

### User/owner memory inputs
- `USER.md`
- `IDENTITY.md`
- `MEMORY.md`
- `memory/**` (recursive)
- `canvas/**` (recursive)

### Agent/self memory inputs
- `SOUL.md`
- `AGENTS.md` (and `AGENT.md` if present in this workspace)
- `TOOLS.md`
- `BOOTSTRAP.md`
- `HEARTBEAT.md`

Present a clear preview before upload:
- count files per class
- total bytes per class
- any unreadable/skipped files

Ask for explicit confirmation.

---

## Step 5: Upload to Honcho using peer-separated sessions

Create/ensure:
- workspace (`HONCHO_WORKSPACE_ID` or `openclaw`)
- peer `owner`
- peer `openclaw`
- migration session (e.g. `migration-upload-<timestamp>`)

Add both peers to session, then upload files:
- user/owner files → `owner`
- agent/self files → `openclaw`

If any upload fails:
- stop
- report exact file and error
- keep local files unchanged

Report summary:
- uploaded user file count
- uploaded agent file count
- failed/skipped files

---

## Step 6: Update workspace docs (including AGENT.md compatibility)

Update/create memory instructions in:
- `AGENTS.md`
- `SOUL.md`
- `BOOTSTRAP.md`
- `AGENT.md` (if this workspace uses it)

Preserve custom content; only replace memory-specific sections.

### Required policy text to add

1. **Memory retrieval order**
   - First try `honcho_context` / `honcho_search` / `honcho_recall`
   - If needed, use `memory_search` + `memory_get` for local file recall
   - Use `honcho_session` for same-session recall

2. **Memory write behavior**
   - Important durable facts can be written via `honcho_write`
   - Pre-compaction flush writes concise durable notes to `memory/YYYY-MM-DD.md`

3. **Failure handling**
   - If Honcho unavailable: continue with local memory tools, state degraded mode
   - Never claim memory certainty without retrieval evidence

4. **Transparency**
   - When memory influences an answer, be able to explain source class
     (Honcho recall vs local file recall vs current-session context)

---

## Step 7: Add/refresh practical memory operating conventions

Ensure docs reflect these conventions the agent has been using:

- **Do not preload everything** into active reasoning if not needed
- **Prefer targeted retrieval** over huge static context injection
- **Treat disagreement as signal:** preserve conflicting observations; do not silently average
- **Use pre-compaction flushes** to avoid losing high-value context during long sessions
- **Separate memory types conceptually:**
  - durable facts
  - episodic notes
  - scratch/working notes

Even if physical storage is mixed, behavior should preserve this distinction.

---

## Step 8: Optional (recommended) no-fork observability add-on

Without modifying OpenClaw gateway source, the memory-mux extension can emit:
- a small **memory load manifest** per session start (what memory sources were pulled)
- a **pre-compaction write report** (what was persisted)

Store under:
- `memory/manifests/YYYY-MM-DD/<session>.json`

This makes memory behavior debuggable while keeping upstream updates painless.

---

## Step 9: Validate end-to-end behavior

Run a quick live test:
1. Ask agent about a known historical fact only in migrated memory
2. Confirm retrieval path works (Honcho first, fallback available)
3. Trigger/perform pre-compaction flush
4. Confirm new note appears in `memory/YYYY-MM-DD.md`
5. Re-ask fact in a new turn/session to validate durability

---

## Wrap-up report to user

Provide:
- installed/enabled plugin list
- Honcho connectivity mode (managed vs self-hosted)
- files discovered, uploaded, skipped
- docs updated (`AGENTS.md`, `SOUL.md`, `BOOTSTRAP.md`, `AGENT.md` if present)
- any follow-up actions

Reference docs:
- https://docs.honcho.dev
- https://github.com/plastic-labs/honcho

---

## Guardrails

- Never delete user memory files automatically unless user explicitly asks
- Never proceed with migration on failed Honcho connectivity
- Never silently ignore upload errors
- Prefer reversible edits and clear summaries
