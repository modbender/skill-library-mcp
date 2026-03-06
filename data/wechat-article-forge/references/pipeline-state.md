# Pipeline State Machine (Compaction-Safe)

The orchestrator persists state to `~/.wechat-article-writer/drafts/<slug>/pipeline-state.json` **before every subagent spawn and after every step completion**. This file is the single source of truth for resuming after context compaction or session restart.

## Schema

```json
{
  "slug": "growth-mindset-ai-20260219",
  "step": 5,
  "phase": "reviewing",
  "purpose": "One-sentence 初心 statement",
  "revision_cycle": 2,
  "max_revisions": 3,
  "pass_threshold": 9.5,
  "min_dimension": 8,
  "last_score": 8.60,
  "last_review_file": "review-v2.json",
  "last_draft_file": "draft-v3.md",
  "subagent_label": "reviewer-growth-mindset-v3",
  "subagent_status": "pending",
  "pending_action": "spawn_reviewer",
  "illustrations_done": false,
  "cover_done": false,
  "html_rendered": false,
  "published": false,
  "error": null,
  "updated_at": "2026-02-19T13:50:00Z"
}
```

| Field | Values |
|-------|--------|
| `phase` | `preparing` \| `writing` \| `reviewing` \| `revising` \| `awaiting_human` \| `fact_checking` \| `formatting` \| `previewing` \| `illustrating` \| `publishing` \| `done` \| `blocked` |
| `subagent_status` | `pending` \| `done` \| `failed` \| `null` |
| `publishing_sub` | `preparing` \| `chunking` \| `text_injected` \| `images_inserting` \| `images_done` \| `saving` \| `null` |

### Publishing Sub-Phase Tracking

When `phase` is `publishing`, use `publishing_sub` to track progress within browser injection. This enables resume after session compaction.

```json
{
  "phase": "publishing",
  "publishing_sub": "chunking",
  "publishing_path": "browser_tool",
  "chunks_total": 5,
  "chunks_stored": 3,
  "images_total": 4,
  "images_inserted": 0,
  "wechat_token": "1829963357",
  "editor_target_id": "13142245C7278BD45ECDCE0ED7FF1056"
}
```

| Sub-phase | What happened | Resume action |
|-----------|--------------|---------------|
| `preparing` | Editor page opened, login verified | Verify token still valid |
| `chunking` | Storing base64 chunks in page context | Re-store from `chunks_stored` onward |
| `text_injected` | HTML content pasted into ProseMirror | Skip to image insertion |
| `images_inserting` | Inserting images one by one | Resume from `images_inserted` |
| `images_done` | All images inserted and verified | Proceed to save |
| `saving` | Save button clicked | Check if save succeeded |

**CRITICAL:** If session compacts during `chunking`, the page context (`window._b`) may be lost if the page reloaded. Verify `window._b` length before continuing — if lost, re-store all chunks.

## Resume Protocol (MANDATORY at start of every turn)

1. Check if any `pipeline-state.json` exists with `phase` ≠ `done`/`blocked`.
2. If found, read it — this is your current task.
3. If `subagent_label` is set and `subagent_status` is `pending`:
   - Check via `subagents list`.
   - Done → read result, save output, advance step.
   - Running → report and wait. Do NOT re-spawn.
   - Failed → set `error`, set `phase: "blocked"`, notify user.
4. If no subagent pending → execute `pending_action`.
5. **Before spawning**: write state with label + `pending` FIRST.
6. **After completion**: save output, update state, then proceed.

## State Transitions

```
research+prep (1) → write (2) → review (3)
  ↓ (score < threshold AND cycle < max)
revise-auto (4a) → review (3) [loop, max 2 automated]
  ↓ (score < threshold AND cycle >= 2)
revise-human (4b) → review (3) [pipeline pauses for user direction]
  ↓ (score >= threshold)
fact-check (5) [max 2 cycles: verify → fix → re-verify]
  ↓ (if >3 text changes: spot re-review on changed paragraphs)
format (6) → preview (7)
  ↓ (user approves text)
illustrate+embed (8) → publish+metadata (9) → done
```

## File Naming

- Drafts: `draft.md` (initial), `draft-v2.md`, `draft-v3.md`, ...
- Reviews: `review-v1.json`, `review-v2.json`, ...
- `last_draft_file` and `last_review_file` always point to current version.
