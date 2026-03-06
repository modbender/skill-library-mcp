---
name: git-repo-to-book
description: >
  Write a full-length technical book using multi-agent AI orchestration. Spawns parallel
  research, writing, and review agents to produce 60K-100K+ word manuscripts. Also supports
  revising individual chapters of existing books. Based on the real workflow that produced
  an 88,000-word, 14-chapter book in under 18 hours.
triggers:
  - write a book
  - book writing
  - write a technical book
  - multi-chapter
  - manuscript
  - 写书
  - 写一本书
  - book project
  - long-form document
  - revise chapter
  - rewrite chapter
  - improve chapter
  - 修改章节
---

# Git Repo to Book

Write a full-length technical book using multi-agent AI orchestration. Based on the
real workflow that produced [The OpenClaw Paradigm](https://github.com/chunhualiao/openclaw-paradigm-book)
— 88,000+ words, 14 chapters, 42 diagrams in under 18 hours.

## Scope & Boundaries

**This skill handles:**
- Planning, researching, writing, reviewing, and publishing multi-chapter technical books
- **Revising individual chapters** of existing books (review → rewrite → re-integrate)
- Orchestrating parallel sub-agents for each phase
- Merging chapters into a polished manuscript with TOC, metadata, and HTML export
- Managing the WORKLOG protocol for agent coordination

**This skill does NOT handle:**
- Cover design or artwork generation (use an illustration skill)
- Publishing to Amazon/Kindle/bookstores (output is Markdown + HTML)
- Fiction/creative writing (optimized for technical/non-fiction)
- Translation to other languages

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Topic/subject | Yes | What the book is about |
| Source repo | No | GitHub URL to analyze as source material |
| Chapter count | No | Auto-scaled from repo size (see below), or user override |
| Target length | No | Auto-scaled from repo size (see below), or user override |
| Budget limit | No | Max API cost in dollars. Default: $100. Agent pauses if exceeded |
| Output formats | No | Markdown (always), HTML (optional), PDF (optional) |
| Model preferences | No | Defaults in Agent Model Recommendations section |

## Outputs

- `book/final-manuscript.md` — polished, publication-ready manuscript
- `book/illustrated-manuscript.md` — manuscript with scrapbook illustrations (if article-illustrator available)
- `book/metadata.json` — title, author, word count, chapter count, date
- `book/book.html` — HTML export (optional)
- Git repository with full project history

## Auto-Scaling: Repo Size → Book Size

When a source repo is provided, automatically assess its scope before planning:

```bash
# Count source files and total lines
find <repo> -name '*.py' -o -name '*.ts' -o -name '*.js' -o -name '*.go' -o -name '*.rs' -o -name '*.md' | wc -l
find <repo> -name '*.py' -o -name '*.ts' -o -name '*.js' -o -name '*.go' -o -name '*.rs' -o -name '*.md' | xargs wc -l 2>/dev/null | tail -1
```

| Repo Size | Source Files | Lines of Code | Recommended Chapters | Target Words | Estimated Cost |
|-----------|-------------|---------------|---------------------|-------------|---------------|
| Small | <50 files | <5K lines | 5-6 chapters | ~30,000 | $5-15 |
| Medium | 50-200 files | 5K-30K lines | 8-10 chapters | ~55,000 | $15-35 |
| Large | 200-500 files | 30K-100K lines | 12-14 chapters | ~80,000 | $30-60 |
| Very Large | >500 files | >100K lines | 14-18 chapters | ~100,000+ | $50-100 |

If no source repo is provided (topic-only book), default to Medium (10 chapters, ~55K words).

The user can always override these defaults.

## Pre-Flight Cost Estimation

**Before starting any work**, present the user with a cost estimate and get confirmation:

```markdown
## Book Project Estimate

**Topic:** [topic]
**Source:** [repo URL or "topic-only"]
**Repo size:** [Small/Medium/Large/Very Large] ([N] files, [N] lines)

**Plan:**
- Chapters: [N]
- Target words: ~[N]
- Writing agents: [N] parallel
- Estimated API cost: $[X]-$[Y]

**Budget limit:** $[user-set or 100 default]

**Models:**
- Writing: claude-sonnet-4-6 (~$0.003/1K input, $0.015/1K output)
- Research: gemini-2.5-pro (~$0.002/1K input, $0.012/1K output)
- Review: deepseek-v3.2 (~$0.001/1K input, $0.003/1K output)

Proceed? (yes / adjust budget / change chapter count)
```

**Cost tracking during execution:** After each phase, log cumulative spend in WORKLOG.md:

```markdown
## Cost Checkpoint - Phase [N] Complete
**Phase cost:** $X.XX
**Cumulative:** $XX.XX / $[budget] budget
**Remaining budget:** $XX.XX
**Projected total:** $XX.XX (on track / over budget)
```

If projected total exceeds budget by >20%, pause and ask the user before continuing.

## Architecture

### Why an Orchestrator Subagent (not direct Director control)

The naive approach is: Director spawns research agents, waits for completion announce,
spawns writing agents, waits again, etc. **This breaks in practice** because:

1. **Announce-to-action gap:** When a subagent finishes, OpenClaw sends a completion
   message to the parent session. The parent gets a new turn, but it must *choose* to
   chain the next phase. If it treats the announce as informational (reports results to
   user and stops), the pipeline stalls. There is no guaranteed hook that forces the
   next action.

2. **Context loss between turns:** Each turn the Director takes is a fresh LLM call.
   Between subagent completion and the next turn, there's no persistent state machine
   tracking "we're in phase 3 of 7." The Director must re-derive pipeline state from
   WORKLOG.md every time, which is fragile.

3. **User messages interrupt:** If the user sends a message between phases, the Director's
   next turn handles that message instead of continuing the pipeline. The pipeline stalls
   until another trigger arrives.

**Solution: Orchestrator subagent pattern.** The Director spawns a single orchestrator
subagent (`maxSpawnDepth: 2`) that owns the entire pipeline lifecycle. The orchestrator
runs as a continuous session, spawning worker sub-sub-agents for each phase and
immediately chaining the next phase when workers complete. Because it's a single
continuous run, there's no announce-to-action gap — the orchestrator never yields
control between phases.

```
Director (main agent, depth 0)
    │
    └── Orchestrator (subagent, depth 1) ← owns entire pipeline
        │
        ├── Phase 1: RESEARCH workers (depth 2, parallel)
        │   └── research/*.md → pattern-synthesis.md
        │
        ├── Phase 2: OUTLINE workers (depth 2, parallel)
        │   └── chapters/*-outline.md
        │
        ├── Phase 3: WRITING workers (depth 2, 3 chapters each)
        │   └── chapters/chapter-NN.md
        │
        ├── Phase 4: REVIEW workers (depth 2, parallel)
        │   └── reviews/quality-review-*.md
        │
        ├── Phase 5: INTEGRATION (orchestrator does this directly)
        │   └── book/manuscript.md
        │
        ├── Phase 6: POLISH (orchestrator does this directly)
        │   └── book/final-manuscript.md + metadata.json
        │
        ├── Phase 7: ILLUSTRATE (orchestrator invokes article-illustrator per chapter)
        │   └── book/illustrated-manuscript.md (scrapbook images at section breaks)
        │
        └── Phase 8: PUBLISH (orchestrator does this directly)
            └── git commit + push + report
```

### Depth Model

| Depth | Role | Spawns children? | Has session tools? |
|-------|------|------------------|--------------------|
| 0 | Director (main agent) | Yes — spawns orchestrator | Full tools |
| 1 | Orchestrator | Yes — spawns workers | Gets `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history` |
| 2 | Workers (research, writing, review) | No | File I/O + exec only |

**Requires:** `agents.defaults.subagents.maxSpawnDepth: 2` in OpenClaw config.

If `maxSpawnDepth` is 1 (default), the skill falls back to Director-controlled mode
(see Fallback section below).

### Fallback: Director-Controlled Mode (maxSpawnDepth: 1)

If nested subagents are not available, the Director orchestrates directly:
- Spawns each phase's workers as depth-1 subagents
- When completion announces arrive, **must immediately chain the next phase**
- Pipeline state tracked via WORKLOG.md
- Risk: announce-to-action gap if Director doesn't chain (see justification above)

To mitigate, set a cron safety net after spawning:
```
cron: "Check book pipeline state in WORKLOG.md. If last phase completed but next
phase not started, resume the pipeline." (fire 15 minutes after spawn)
```

### Agent Coordination

All agents coordinate via `WORKLOG.md` (append-only). The orchestrator (or Director
in fallback mode) reads WORKLOG to track progress. Workers append entries when starting
and finishing work.

## End-to-End Example

User says: **"Write a technical book about AI-native software development. Source: https://github.com/openclaw/openclaw"**

**Step 1 — Gather requirements:**
- Topic: AI-native software development
- Source repo: openclaw/openclaw
- Chapters: 12 (default)
- Target: ~80,000 words

**Step 2 — Set up repo and spawn orchestrator:**
```bash
mkdir -p book-project/{chapters,book,diagrams,research,reviews,scripts,project-notes}
cd book-project && git init
```
Copy templates, then spawn the orchestrator subagent (depth 1) which manages all
remaining phases. The orchestrator spawns worker sub-sub-agents (depth 2) in parallel.

**Step 3 — Research phase (orchestrator spawns 3 parallel workers):**
```
Agent A task: "Analyze openclaw/openclaw architecture. Focus on session management,
tool system, and agent lifecycle. Output: research/architecture-analysis.md. 
Read WORKLOG.md first. Update WORKLOG.md when complete."

Agent B task: "Analyze openclaw/openclaw skills system and plugin architecture.
Output: research/skills-analysis.md. Read WORKLOG.md first."

Agent C (synthesis): "Read all files in research/. Synthesize into 
research/pattern-synthesis.md. Identify 6-10 core patterns and 3-5 anti-patterns."
```

**Step 4 — Outline phase (spawn 2 agents):**
```
Agent 1: "Write detailed outlines for intro + chapters 1-6. Reference pattern-synthesis.md.
Output: chapters/chapter-NN-outline.md per chapter."

Agent 2: "Write detailed outlines for chapters 7-12."
```
Review and commit outlines.

**Step 5 — Writing phase (spawn 4 parallel agents, 3 chapters each):**
```
Agent 1: "Write intro + chapters 1-3. Read outlines and pattern-synthesis.md.
Target: 6,000-8,000 words per chapter. Update WORKLOG.md when each chapter is complete."

Agent 2: "Write chapters 4-6."
Agent 3: "Write chapters 7-9."
Agent 4: "Write chapters 10-12."
```
Model: `anthropic/claude-sonnet-4-6`

**Step 6 — Review phase (spawn 2 agents):**
```
Agent A: "Review intro + chapters 1-6. Check: logical flow, unsupported claims,
contradictions, missing examples. Output: reviews/quality-review-01-06.md.
Mark issues CRITICAL or MINOR."
```
Fix CRITICAL issues before proceeding.

**Step 7 — Integration:**
```bash
python3 <skill_dir>/scripts/merge_chapters.py --title "AI-Native Development" --author "Author Name"
```

**Step 8 — Polish:**
```bash
python3 <skill_dir>/scripts/polish_manuscript.py --title "AI-Native Development" --author "Author Name"
```

**Step 9 — HTML export:**
```bash
python3 <skill_dir>/scripts/convert_to_html.py
```

**Step 10 — Commit and report:**
```bash
git add -A && git commit -m "book: complete manuscript" && git push
```
Report: chapter count, word count, file locations, GitHub URL.

## Chapter Revision Mode

Revise a single chapter of an existing book without regenerating the entire manuscript.

### When to Use

- A chapter is outdated (new features, changed APIs)
- Quality is below standard (reviewer scored it low)
- User wants a different angle or deeper coverage
- New information needs to be incorporated

### Revision Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Book repo | Yes | Local path or GitHub URL of the existing book |
| Chapter number | Yes | Which chapter to revise (e.g., `3` or `chapter-03`) |
| Revision instructions | No | Specific guidance: "add more examples", "update for v2 API", "make it more practical" |
| Budget limit | No | Default: $5 per chapter revision |

### Revision Workflow

#### Step R1 — Clone and Analyze

```bash
git clone <repo_url> /tmp/book-revision
cd /tmp/book-revision
```

Read the target chapter + its outline + adjacent chapters (N-1 and N+1) for context continuity.

#### Step R2 — Review Current Chapter

Spawn a **reviewer agent** to score the existing chapter on the standard rubric:
- Technical accuracy
- Completeness (are topics from the outline covered?)
- Code examples (working? up to date?)
- Flow and readability
- Consistency with adjacent chapters

The reviewer produces `reviews/revision-review-chapter-NN.md` with:
- Score per dimension
- Specific issues found
- Recommended changes

#### Step R3 — Research Updates (if needed)

If the revision requires new information (updated APIs, new features, recent events):

Spawn a **research agent** to:
- **Query DeepWiki MCP** (`curl https://api.deepwiki.com/v1/chat`) for current repo architecture and features
- Analyze the source repo (if provided) for changes since the chapter was written
- Web search for updated information and external context
- Produce `research/revision-research-chapter-NN.md`

DeepWiki is the preferred research source for GitHub repo-based books — it provides deep, structured answers about architecture, components, and patterns.

**Skip if** the revision is purely stylistic (rewrite for clarity, add examples from existing content).

#### Step R4 — Rewrite

Spawn a **writer agent** with:
- The existing chapter text
- The review (from R2)
- Research updates (from R3, if any)
- The chapter outline
- Adjacent chapters (for tone/style consistency)
- User's revision instructions

The writer produces a new version: `chapters/chapter-NN-revised.md`

**Key constraints for the writer:**
- Preserve the chapter's position in the book narrative (don't contradict adjacent chapters)
- Keep the same heading structure unless the outline changed
- Maintain consistent terminology with the rest of the book
- If the original had diagrams, preserve or update diagram references

#### Step R5 — Review (Mobile-Friendly)

Users often review from a phone (iPhone/Android via Discord, Signal, or Telegram). The review workflow adapts to the platform:

**Path A — GitHub PR (preferred, best for diff review):**

```bash
cd /tmp/book-revision
git checkout -b revise/chapter-NN

# Backup original
cp chapters/chapter-NN.md chapters/chapter-NN-pre-revision.md

# Replace with revised version
cp chapters/chapter-NN-revised.md chapters/chapter-NN.md

git add -A
git commit -m "revise: chapter NN - [summary of changes]"
git push origin revise/chapter-NN

# Open PR with summary as description
gh pr create --title "Revise Chapter NN: [title]" \
  --body "$(cat reviews/revision-summary-chapter-NN.md)" \
  --base main --head revise/chapter-NN
```

The user reviews the diff in **GitHub mobile app** (excellent diff viewer), then:
- Comments "LGTM" or "approve" → agent merges PR and re-generates manuscript
- Comments with feedback → agent makes changes, pushes to same branch
- Closes PR → revision discarded

**Path B — Obsidian sync (for offline reading):**

If the user has Obsidian configured (e.g., via `save-to-obsidian.sh`):
```bash
# Send revised chapter + summary to Obsidian vault
save-to-obsidian.sh chapters/chapter-NN-revised.md
save-to-obsidian.sh reviews/revision-summary-chapter-NN.md
```
User reads the full chapter on Obsidian mobile, replies via chat.

**Path C — Chat summary (quickest):**

Post a concise summary (≤500 words) directly in chat:
```
📝 Chapter NN Revision Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Words: 3,510 → 5,200 (+48%)

✅ Sections rewritten:
  - 2.1: Updated architecture description
  - 2.3: Added 3 new code examples

➕ Sections added:
  - 2.6: New "Deployment Models" section

🔗 Full diff: [GitHub PR link]
📖 Full chapter: [Obsidian / GitHub link]

Reply "approve", "changes needed", or specific feedback.
```

**Auto-detect by content type:**
- **Text-only revision (no new diagrams/images):** Default to Path A (PR) + Path C (chat summary). GitHub diff is ideal for text changes.
- **Illustrated revision (new or updated diagrams/images):** Default to Path B (Obsidian) + Path C (chat summary). Obsidian renders images inline — you see the chapter exactly as it appears in the book. GitHub PR diffs show images as "binary file changed" which is useless for review.
- **User preference overrides** — if they ask for a specific path, use it.

**Recommendation:** For chapters with diagrams (most technical books), Obsidian preview is the best experience on mobile. Use the PR for the final merge step after Obsidian review.

#### Step R6 — Integrate

On user approval (via PR merge, chat reply, or Obsidian feedback):

**Best practice: Replace in-place, never create `-new` or `-v2` suffixes.**

- `chapters/chapter-NN.md` ← always overwrite the current file
- `diagrams/chapter-NN/` ← always replace diagrams in the same directory
- **No backups** (`-pre-revision`, `-old`, `-v2`) — git history IS the backup
- **No new directories** (`chapter-02-new/`) — the PR diff shows what changed

This prevents suffix accumulation (`-new`, `-new-new`, `-new-v3`) across revisions.

```bash
# If using PR workflow, the merge already happened. Just regenerate manuscript:
cd /tmp/book-revision
git checkout main && git pull

# Re-merge all chapters into manuscript
python3 <skill_dir>/scripts/merge_chapters.py --title "[Title]" --author "[Author]" --output book/manuscript.md
python3 <skill_dir>/scripts/polish_manuscript.py --title "[Title]" --author "[Author]" --output book/final-manuscript.md

# Commit updated manuscript
git add book/
git commit -m "book: regenerate manuscript after chapter NN revision"
git push
```

#### Step R6.5 — Validate Links (automated)

After integration, run the link validator to catch broken references:

```bash
python3 <skill_dir>/scripts/validate_links.py --book-dir /path/to/book
```

This checks:
- All `![image](path)` references point to existing files
- All `[link](file.md)` references resolve
- No orphaned diagram directories
- Suggests fixes for broken links (fuzzy match on filenames)

**Must pass with 0 broken links before proceeding to R7 or committing.**

**Also verify metadata block exists:**
```bash
grep -c "## Chapter Metadata" chapters/chapter-NN.md || echo "ERROR: Missing metadata block"
```
If missing, add it before committing.

If broken links are found:
1. Fix image paths to match actual filenames in `diagrams/chapter-NN/`
2. Re-run validator until clean
3. Also run on `book/final-manuscript-with-diagrams.md` if it exists (merged manuscript may have stale refs)

#### Step R7 — Re-illustrate (Optional)

If the chapter content changed significantly (>30% rewritten), regenerate diagrams:
- **With image API key:** Re-run article-illustrator for the revised chapter
- **Without image API key:** Re-run skill-mermaid-diagrams for the revised chapter

### Revision Cost Estimate

| Component | Model | Est. Cost |
|-----------|-------|-----------|
| Review | deepseek | $0.01-0.02 |
| Research (if needed) | gemini-pro | $0.05-0.10 |
| Rewrite | claude-sonnet | $0.10-0.30 |
| Re-illustrate (if needed) | Z.AI | $0.03-0.06 |
| **Total per chapter** | | **$0.15-0.50** |

### Example: Revise Chapter 3

```
User: "Revise chapter 3 of https://github.com/chunhualiao/openclaw-paradigm-book
       — it needs more real-world case studies and the code examples are outdated"

Agent:
1. Clone repo, read chapter-03.md + chapter-02.md + chapter-04.md + chapter-03-outline.md
2. Spawn reviewer → scores chapter, finds: "only 2 case studies, code uses deprecated API"
3. Spawn research agent → checks OpenClaw repo for current API, finds 3 new case studies
4. Spawn writer → rewrites chapter with 5 case studies, updated code, same structure
5. Present diff summary to user
6. On approval: replace chapter, re-merge manuscript, commit + push
```


### Chapter Metadata Block (Required)

Every chapter must end with a metadata block providing provenance and reproducibility information. This is critical because source repos evolve fast — readers need to know which version the chapter describes.

**Template (append to end of each chapter):**

```markdown
---

## Chapter Metadata

> **This section is auto-generated by the book-writer skill.**

| Field | Value |
|-------|-------|
| **Subject Repo** | [owner/repo](https://github.com/owner/repo) |
| **Subject Repo Commit** | [`abc1234`](https://github.com/owner/repo/commit/abc1234) |
| **Subject Repo Version** | vX.Y.Z (or "latest as of YYYY-MM-DD") |
| **Book Repo** | [owner/book-repo](https://github.com/owner/book-repo) |
| **Book-Writer Skill** | [git-repo-to-book](https://clawhub.ai/YOUR_HANDLE/git-repo-to-book) |
| **Research Source** | DeepWiki / web search / direct repo analysis |
| **Diagrams** | N × type (skill used) |
| **Writer Model** | model name |
| **Reviewer Model** | model name |
| **Generated/Revised** | YYYY-MM-DD |
| **Word Count** | X,XXX |

**⚠️ Freshness Note:** This chapter describes [repo] as of commit `abc1234`.
Verify current state at [docs link] or [DeepWiki link].
```

**Why this matters:**
- Source repos change daily — without a commit pin, the chapter becomes unreproducible
- Model attribution helps readers understand potential biases
- Freshness warnings prevent readers from treating outdated info as current
- Skill version enables reproducing the exact pipeline

**When revising:** Update all metadata fields. The old commit → new commit change is the most important field to update.


## Setup & Configuration

### Step 0 — Environment Discovery (run before every book/revision)

Before starting any pipeline, discover available API keys and expose them as environment variables. The skill uses multiple external services — some required, some optional.

**Run this discovery check:**

```bash
# === REQUIRED ===
# At least one LLM provider must be configured (check OpenClaw config)
echo "=== LLM Providers ==="
grep -o '"openrouter_api_key"\|"anthropic_api_key"\|"openai_api_key"' ~/.openclaw/config.json 2>/dev/null && echo "✅ LLM provider found" || echo "❌ No LLM provider in config"

# === OPTIONAL: Image Generation ===
echo "=== Image Generation (for scrapbook illustrations) ==="
# Check all possible locations: env vars, config.json, .env files
ZAI=$(grep -o '"zai_api_key"' ~/.openclaw/config.json 2>/dev/null)
GLM=$(grep -o '"glm_api_key"' ~/.openclaw/config.json 2>/dev/null)
OR=$(grep -o '"openrouter_api_key"' ~/.openclaw/config.json 2>/dev/null)
[ -n "$ZAI" ] && echo "✅ Z.AI ($0.015/image)" || echo "⬜ Z.AI not configured"
[ -n "$GLM" ] && echo "✅ GLM ($0.014/image)" || echo "⬜ GLM not configured"
[ -n "$OR" ] && echo "✅ OpenRouter ($0.045/image)" || echo "⬜ OpenRouter not configured"
[ -z "$ZAI" ] && [ -z "$GLM" ] && [ -z "$OR" ] && echo "→ Will use Mermaid diagrams (free) instead of scrapbook images"

# === OPTIONAL: Mermaid Diagrams ===
echo "=== Mermaid CLI (for diagram generation) ==="
which mmdc >/dev/null 2>&1 && echo "✅ mmdc $(mmdc --version 2>/dev/null)" || echo "⬜ mmdc not installed (run: npm install -g @mermaid-js/mermaid-cli)"

# === OPTIONAL: DeepWiki ===
echo "=== DeepWiki MCP (for repo research) ==="
curl -s --max-time 3 https://api.deepwiki.com/v1/health >/dev/null 2>&1 && echo "✅ DeepWiki API reachable" || echo "⬜ DeepWiki unreachable (will use direct repo analysis)"

# === OPTIONAL: GitHub CLI ===
echo "=== GitHub CLI (for PR workflow) ==="
gh auth status >/dev/null 2>&1 && echo "✅ gh authenticated as $(gh api user -q .login 2>/dev/null)" || echo "⬜ gh not authenticated (PR review workflow unavailable)"

# === OPTIONAL: Obsidian sync ===
echo "=== Obsidian (for mobile preview) ==="
[ -f ~/.openclaw/scripts/save-to-obsidian.sh ] && echo "✅ Obsidian sync script found" || echo "⬜ No Obsidian sync (chat-only review)"
```

**Expose keys as env vars** (so subagents/scripts can access them):

```bash
# Extract from OpenClaw config and export
export ZAI_API_KEY=$(python3 -c "import json; c=json.load(open('$HOME/.openclaw/config.json')); print(c.get('zai_api_key',''))" 2>/dev/null)
export GLM_API_KEY=$(python3 -c "import json; c=json.load(open('$HOME/.openclaw/config.json')); print(c.get('glm_api_key',''))" 2>/dev/null)
export OPENROUTER_API_KEY=$(python3 -c "import json; c=json.load(open('$HOME/.openclaw/config.json')); print(c.get('openrouter_api_key',''))" 2>/dev/null)
```

### What Happens When Keys Are Missing

| Missing Key | Impact | Fallback |
|-------------|--------|----------|
| All LLM providers | **Fatal** — cannot proceed | Ask user to configure at least one provider in `~/.openclaw/config.json` |
| All image keys (ZAI, GLM, OR) | No scrapbook illustrations | Mermaid diagrams via `skill-mermaid-diagrams` (free) |
| mmdc CLI | No rendered diagram PNGs/SVGs | Raw mermaid code blocks in markdown (still renders in GitHub/Obsidian) |
| DeepWiki | Weaker research for repo-based books | Direct repo analysis + web search |
| gh CLI | No PR review workflow | Obsidian preview or chat summary only |
| Obsidian sync | No mobile preview with images | GitHub PR + chat summary |

**The skill always works** — missing optional keys degrade gracefully to free alternatives. Only LLM provider keys are required.


## Full Book Workflow (New Books)

### Step 1 — Gather Requirements and Estimate Cost

Ask the user (or infer from context):
- **Topic/subject** — what is the book about?
- **Source repo** (optional) — GitHub URL to analyze as source material
- **Budget limit** — how much are they willing to spend? (default: $100)
- **Output formats** — Markdown (always), HTML, PDF (optional)

If a source repo is provided, run the auto-scaling assessment (see above) to determine chapter count and target length. Then present the Pre-Flight Cost Estimation and **wait for user confirmation before proceeding**.

If the user sets a budget below the estimated cost, suggest reducing chapter count or using cheaper models (e.g., deepseek for writing instead of claude).

### Step 2 — Set Up Repo and Spawn Orchestrator

```bash
mkdir -p book-project/{chapters,book,diagrams,research,reviews,scripts,project-notes}
cd book-project && git init
```

Copy templates from `<skill_dir>/templates/` into `project-notes/` and edit for your project. Replace `<skill_dir>` with the directory containing this SKILL.md.

**Then spawn the orchestrator subagent** (preferred, requires `maxSpawnDepth: 2`):

```
sessions_spawn(
  task: "You are the book pipeline orchestrator. Run all phases (research → outlines →
    writing → review → integration → polish → publish) for [Book Title].
    
    Project dir: /path/to/book-project
    Chapters: [N]
    Target: ~[N] words
    Budget: $[N]
    Source: [repo URL or topic]
    
    You have sessions_spawn to create worker subagents. Spawn workers in parallel
    for each phase. When workers finish, immediately start the next phase. Never
    stop between phases. Track costs in WORKLOG.md after each phase.
    
    When all phases complete, report: chapter count, word count, total cost, file paths.",
  model: "anthropic/claude-sonnet-4-6",
  mode: "run"
)
```

The orchestrator handles Steps 3-10 autonomously. The Director only needs to relay
the final report to the user.

**If `maxSpawnDepth` is 1** (fallback), the Director runs Steps 3-10 directly,
spawning workers as depth-1 subagents and chaining phases on each completion announce.

### Step 3 — Research Phase

**DeepWiki MCP (preferred for GitHub repos):**

If the book's source material is a GitHub repo, use the `deepwiki-mcp` skill (`clawhub install deepwiki-mcp`) for deep research:

```bash
# Query DeepWiki for detailed repo analysis
curl -s https://api.deepwiki.com/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "owner/repo",
    "messages": [{"role": "user", "content": "Describe the architecture, key components, and design patterns"}]
  }'
```

DeepWiki provides structured, authoritative answers about any public GitHub repo — its architecture, components, patterns, and implementation details. This is far more reliable than generic web search for repo-specific questions.

**Research agent should query DeepWiki for each chapter's topics**, then supplement with web_search for broader context (industry trends, comparisons, external references).

**Fallback:** If DeepWiki is unavailable, fall back to direct repo analysis (clone + read files) and web search.

Spawn 2-3 research agents in parallel:

```
Task: Analyze [source_repo/topic]. Identify key patterns, concepts, and examples.
Output: research/[topic-area]-analysis.md
Format: Numbered findings, specific examples, 2000-4000 words.
Read WORKLOG.md first to avoid duplicating work.
Update WORKLOG.md when complete.
```

Then spawn one synthesis agent:

```
Task: Read all files in research/. Synthesize into research/pattern-synthesis.md.
Identify 6-10 core patterns and 3-5 anti-patterns.
```

**Done when:** `research/pattern-synthesis.md` exists and covers 6+ patterns.

### Step 4 — Outline Phase

Spawn outline agents (batch 5-6 outlines per agent):

```
Task: Write detailed chapter outlines for Chapters N through M.
Reference: research/pattern-synthesis.md
Output: chapters/chapter-NN-outline.md per chapter
Format: H2 sections, 6-8 sections, 1-2 sentence description each
```

Review and commit outlines before writing.

**Done when:** All `chapter-NN-outline.md` files exist and reviewed.

### Step 5 — Writing Phase

Assign 3 chapters per writing agent — this is where parallelism pays off:

```
Task: Write Chapters X, Y, Z of [Book Title].
Read outlines and research/pattern-synthesis.md.
Output: chapters/chapter-NN.md per chapter.
Target: ~6,000-8,000 words per chapter.
Style: Technical but accessible. Use concrete examples, headers, code blocks, tables.
Update WORKLOG.md when each chapter is complete.
```

Model: `anthropic/claude-sonnet-4-6`

**Done when:** All chapter files exist and WORKLOG shows completion.

### Step 6 — Review Phase

Spawn 1-2 review agents:

```
Task: Review chapters [list]. Check: logical flow, unsupported claims, contradictions,
missing examples. Output: reviews/quality-review-[range].md
Format: Per-chapter bullet list. Mark CRITICAL / MINOR.
```

Fix CRITICAL issues. MINOR issues can be addressed in polish.

**Done when:** Reviews exist and no open CRITICAL issues.

### Step 7 — Integration Phase

Run the merge script:

```bash
python3 <skill_dir>/scripts/merge_chapters.py --title "[Title]" --author "[Author]" --output book/manuscript.md
```

Or spawn an integration agent to merge manually and fix cross-references.

**Done when:** `book/manuscript.md` exists with all chapters in order.

### Step 8 — Polish Phase

Run the polish script:

```bash
python3 <skill_dir>/scripts/polish_manuscript.py --title "[Title]" --author "[Author]" --output book/final-manuscript.md
```

This adds title page, copyright, TOC with anchor links, and writes `book/metadata.json`.

**Done when:** `book/final-manuscript.md` and `book/metadata.json` exist.

**Then validate links:**
```bash
python3 <skill_dir>/scripts/validate_links.py --book-dir .
```
Must pass with 0 broken links before publishing.

### Step 8.5 — Illustrate (Optional)

Add scrapbook-style illustrations to the manuscript using the **article-illustrator** skill.

**Prerequisites:** article-illustrator skill installed, at least one image API key set (ZAI_API_KEY, GLM_API_KEY, or OPENROUTER_API_KEY).

**Process:**

1. **Check for image API key** — if none found, skip this step (book works fine without images).

2. **Split manuscript into chapters** for illustration planning:
   The orchestrator processes each chapter section from `book/final-manuscript.md` directly.
   No splitting needed — feed each `chapters/chapter-NN.md` file to the illustrator.


3. **Determine diagram count and placement (REQUIRED before generating):**

   **Diagram count by chapter length:**
   | Chapter Length | Min Diagrams | Target |
   |---------------|-------------|--------|
   | < 3,000 words | 2 | 3 |
   | 3,000–5,000 words | 3 | 4–5 |
   | 5,000–8,000 words | 4 | 5–7 |
   | > 8,000 words | 5 | 7–10 |

   **Placement rules:**
   - **Overview diagram:** Always first — within the first 200 words / before first H2. Type: concept-map, radial-concept, or architecture. Purpose: bird's-eye view of the whole chapter.
   - **Per-section diagrams:** 1 per major H2 section, placed after the first paragraph of that section.
   - **Max gap:** No stretch longer than 2,000 words without a diagram.

   **Diagram type by section content:**
   | Content Type | Z.AI (scrapbook) | Mermaid |
   |-------------|-----------------|---------|
   | System/architecture | abstract tech scrapbook | architecture |
   | Process/workflow | steps/flow scrapbook | flowchart, sequence |
   | Comparison/tradeoffs | balance/scale scrapbook | comparison-table |
   | Data/trends/metrics | chart/graph scrapbook | timeline, gantt |
   | Concepts/relationships | abstract concept scrapbook | concept-map, radial-concept |

4. **For each chapter**, invoke the article-illustrator workflow:
   - Read `article-illustrator/references/scrapbook-prompt.md` for the system prompt
   - Read the scrapbook system prompt from the article-illustrator skill:
     ```bash
     cat <article_illustrator_dir>/references/scrapbook-prompt.md
     ```
   - Analyze the chapter text and generate a JSON illustration plan:
     ```json
     {
       "project_title": "Chapter N — Scrapbook Style",
       "style": "Physical Mixed-Media Scrapbook",
       "total_images": 2,
       "images": [
         {
           "image_id": 1,
           "title": "Caption",
           "description": "300-500 char scrapbook visual description...",
           "insert_after": "Exact heading or sentence"
         }
       ]
     }
     ```
   - Target: **1 image per 1,500-2,000 words** (books are less dense than articles)
   - Generate all images in parallel using the article-illustrator script:
     ```bash
     cd <article_illustrator_dir>
     python3 scripts/generate.py "<description_1>" --language en --size 1088x1920 &
     python3 scripts/generate.py "<description_2>" --language en --size 1088x1920 &
     wait  # Both images generate concurrently (~20-40s each)
     ```
     The script reads ZAI_API_KEY, GLM_API_KEY, or OPENROUTER_API_KEY automatically.
   - Insert images at designated anchor points

4. **Compose illustrated manuscript:**
   Insert each image after its designated `insert_after` anchor:
   ```markdown
   ![Caption](diagrams/chapter-NN/image-01.png)
   ```
   Save the illustrated chapter to `chapters/chapter-NN.md` (replace in-place).
   Then re-run merge to update the full manuscript:
   ```bash
   python3 <skill_dir>/scripts/merge_chapters.py --title "Title" --author "Author" \
     --output book/illustrated-manuscript.md
   ```


6. **Cost tracking:** ~$0.015/image (Z.AI) × images. For a 10-chapter book with 1-2 images each: ~$0.15-0.30.

**Image count guidelines by book size:**

| Book Size | Chapters | Images/Chapter | Total Images | Est. Cost (Z.AI) |
|-----------|----------|----------------|--------------|-------------------|
| Small (2-3) | 2-3 | 1-2 | 2-6 | $0.03-0.09 |
| Medium (5-8) | 5-8 | 1-2 | 5-16 | $0.08-0.24 |
| Large (10-15) | 10-15 | 1-2 | 10-30 | $0.15-0.45 |

**Done when:** `book/illustrated-manuscript.md` exists with images embedded.

**Fallback — Mermaid diagrams via `skill-mermaid-diagrams` (no image API key needed):**

If no image API key is available (ZAI_API_KEY, GLM_API_KEY, OPENROUTER_API_KEY all missing), use the **skill-mermaid-diagrams** skill (`clawhub install skill-mermaid-diagrams`) to generate professional, template-based diagrams:

1. **Install if needed:**
   ```bash
   clawhub install skill-mermaid-diagrams
   ```

2. **For each chapter**, spawn a subagent:
   ```
   Generate 2-3 Mermaid diagrams for /path/to/chapters/chapter-NN.md
   and save to /path/to/diagrams/chapter-NN/
   ```

3. The subagent will:
   - Read chapter content
   - Select from 12 available templates: architecture, flowchart, sequence, concept-map, radial-concept, timeline, comparison, comparison-table, gantt, mindmap, class-diagram, state-diagram
   - Generate content.json with placeholder values
   - Run `node $SKILL_DIR/scripts/generate.mjs --content content.json --out diagrams/chapter-NN`
   - Validate: `node $SKILL_DIR/scripts/validate.mjs --dir diagrams/chapter-NN`
   - Output: `.mmd` source + `.svg` vector + `.png` raster for each diagram

4. **Insert into manuscript:** Reference generated images in markdown:
   ```markdown
   ![Architecture Overview](diagrams/chapter-01/diagram-01-architecture.png)
   ```

5. **Cost:** ~$0.002/chapter (LLM tokens only) — rendering is free (local mmdc).
   For a 10-chapter book: **~$0.02 total** (vs $0.15-0.45 for AI images).

6. **Consistent styling:** All diagrams share a unified color scheme across chapters.

**Decision logic:**
```
if image API key exists AND user did not pass --no-illustrations:
    → Path A: scrapbook illustrations (article-illustrator, ~$0.015/image)
elif user passed --no-illustrations:
    → skip entirely
else:
    → Path B: Mermaid diagrams (free, LLM-generated)
```

**Skip entirely when:** User specified `--no-illustrations --no-diagrams`.

### Step 9 — HTML Export (Optional)

```bash
python3 <skill_dir>/scripts/convert_to_html.py --input book/illustrated-manuscript.md --output book/book.html
# Falls back to final-manuscript.md if illustrated version doesn't exist
```

Requires either `pandoc` or `pip install markdown2`.

### Step 10 — Commit and Report

```bash
git add -A
git commit -m "book: complete manuscript - [word_count] words, [chapter_count] chapters"
git push
```

Report to user: chapter count, word count, file locations, GitHub URL.

## Agent Model Recommendations

| Role | Model | Why |
|------|-------|-----|
| Director (you) | `anthropic/claude-sonnet-4-6` | Planning, coordination |
| Research | `openrouter/google/gemini-2.5-pro-preview` | Large context, data synthesis |
| Writing | `anthropic/claude-sonnet-4-6` | Coherent long-form prose |
| Review | `openrouter/deepseek/deepseek-v3.2` | Cost-effective, thorough |
| Integration/Polish | `anthropic/claude-sonnet-4-6` | Consistent merging |

## Cost Estimates

| Book Size | Approx. API Cost | Time (parallel) |
|-----------|-----------------|-----------------|
| 5 chapters, ~30K words | $5-15 | 2-4 hours |
| 10 chapters, ~60K words | $15-35 | 4-8 hours |
| 14 chapters, ~88K words | $30-60 | 6-12 hours |

## Directory Structure

```
book-project/
├── project-notes/
│   ├── SYSTEM.md         # State machine, agent roles, safety rules
│   ├── AGENDA.md         # Sprint plan, daily tasks, success metrics
│   └── WORKLOG.md        # Append-only execution log
├── chapters/
│   ├── introduction.md
│   ├── chapter-01-outline.md
│   ├── chapter-01.md
│   └── ...
├── book/
│   ├── manuscript.md        # Merged pre-polish
│   ├── final-manuscript.md  # Final polished
│   ├── book.html
│   └── metadata.json
├── diagrams/
├── research/
│   ├── [topic]-analysis.md
│   └── pattern-synthesis.md
├── reviews/
│   └── quality-review-*.md
└── scripts/
    ├── merge_chapters.py
    ├── polish_manuscript.py
    └── convert_to_html.py
```

## WORKLOG Protocol

Every agent **must** append to `WORKLOG.md` at start and finish:

```markdown
## [YYYY-MM-DD HH:MM TZ] - [Agent Name] - [Action]
**State:** WRITING
**Completed:** chapter-07.md (6,847 words)
**Next:** chapter-08.md
**Issues:** None
```

Director reads this to know what's done without polling agents.

## Error Handling

| Problem | Detection | Action |
|---------|-----------|--------|
| Agent fails mid-chapter | WORKLOG shows no update for >2 hours | Respawn agent with same task |
| Chapter too short | <4,000 words | Respawn writing agent with explicit "expand" instruction |
| Quality review fails | >3 CRITICAL issues per chapter | Respawn writing agent to rewrite section |
| Merge script fails | Python error | Check chapter file naming (must be `chapter-NN.md`) |
| Cost exceeds budget | Track cumulative spend | Pause and consult user |
| Cross-reference broken | Review shows "Chapter N" pointing nowhere | Fix manually in integration phase |

## Success Criteria

- All chapters drafted (target: ~6,000-8,000 words each)
- Quality review: >85% of issues marked RESOLVED
- Final manuscript: single cohesive document with TOC
- HTML export renders correctly (if requested)
- Git committed and pushed
- Total word count within 20% of target

## Configuration

No persistent configuration required. The skill uses:

**Recommended config** (enables orchestrator pattern):

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 5,
        "maxConcurrent": 8
      }
    }
  }
}
```

Without `maxSpawnDepth: 2`, the skill falls back to Director-controlled mode (see
Architecture section for tradeoffs).

**Required tools:**

| Tool | Purpose |
|------|---------|
| `exec` | Run Python scripts, git commands |
| `sessions_spawn` | Spawn orchestrator and/or worker sub-agents |
| `read` / `write` | Read/write chapter files |

**Optional tools:**

| Tool | Purpose |
|------|---------|
| `web_search` | Research phase (if no source repo provided) |
| `web_fetch` | Fetch source repo content |

**System dependencies:**

| Dependency | Purpose |
|------------|---------|
| Python 3.8+ | merge, polish, HTML conversion scripts |
| git | Version control |
| pandoc (optional) | Better HTML conversion |

## Notes

- Set `cost_limit: $100` in SYSTEM.md as a safety guard
- The WORKLOG protocol is critical — agents that don't update WORKLOG create blind spots
- Commit to git after every phase, not just at the end
- For very long books (>100K words), increase chapter count rather than word-per-chapter target
- The reference implementation at [openclaw-paradigm-book](https://github.com/chunhualiao/openclaw-paradigm-book) includes all project notes for study
