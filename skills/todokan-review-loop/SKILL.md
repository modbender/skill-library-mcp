---
name: todokan-review-loop
version: 1.3.0
description: Process Todokan task and thought boards with a review-loop workflow. Use when a task enters doing and the agent should pick it up, read latest comments, respond to the newest comment with a high-quality context-aware reply, add an execution update comment, and move the task back to done (Review). Use for recurring polling/cron automation with Todokan MCP.
homepage: https://todokan.com
metadata: {"category":"productivity","tags":["tasks","kanban","mcp","review-loop","automation"],"requires":{"env":["TODOKAN_API_KEY","TODOKAN_MCP_URL"],"mcp":true},"openclaw":{"homepage":"https://todokan.com","requires":{"env":["TODOKAN_API_KEY","TODOKAN_MCP_URL"]}}}
---

# Todokan Review Loop

Use this workflow for autonomous handling of `doing` items.

**Note:** The MCP server only returns tasks where `aiEnabled: true` by default. Users send tasks to AI via a "Send to AI" button, which sets `aiEnabled: true`, `assignee: 'ai'`, and `status: 'doing'`. This skill will only see tasks that users have explicitly sent to AI.

## Role Model

- Act as the Key Account Manager (KAM) as the single user-facing voice.
- Keep one consistent tone and ownership in comments.
- Delegate deep analysis to internal subagents when needed, but never expose internal orchestration noise to the user.

## Workflow

1. List habitats.
2. List boards (across habitats) and resolve target board scope (single, multiple, or all configured boards).
3. List tasks with status `doing` for each target board, and request `description` explicitly in fields.
4. For each task:
   - Read task fields (title, description, labels, dueDate, priority, status).
   - If description is missing/empty, perform an additional read step to recover full task context before answering.
   - Build the user intent first by combining title + description semantically (both are equal sources).
   - Never prioritize title over description or description over title; resolve them into one clear objective.
   - Read the entire comment thread (not only latest comment).
   - Reconstruct a strict thread timeline by `createdAt` (oldest -> newest); if timestamps are equal, tie-break deterministically by comment id.
   - Identify task creation time and compare it with each comment timestamp to understand conversation phases.
   - Identify the latest comment by `createdAt`.
   - Count total comments.
   - Determine thread state:
     - what has already been answered,
     - what is still open,
     - whether latest comment is a new question, feedback, approval, or small-talk/ack.
   - Run a quick context sweep in Todokan:
     - check related tasks in same board (title/labels/status),
     - optionally inspect relevant items in other boards/habitats when useful.
   - Decide if direct answer is enough or internal research is needed.
   - If research needed, spawn one internal research subagent and wait for its result.
   - Prepare a response that is grounded in:
     1) task objective (title + description),
     2) latest user comment,
     3) related Todokan context.
   - Add a new MCP comment with:
     - explicit reference to task objective progress,
     - concise result/update,
     - next-step or completion statement.
   - Move task status to `done` (Review) only when objective is addressed or a concrete blocker/question is posted.

## Response Quality Rules

- Treat comments as a chat thread: short, direct, and contextual.
- Always anchor to task title + description before reacting to comments.
- Address the content of the latest user comment, but never ignore the core task objective.
- Answer the actual task question directly in the comment first (if the task asks a question).
- Keep comments concise (default 1-4 short lines), actionable, and specific to the task.
- Use comments for:
  - quick status updates,
  - follow-up questions,
  - short assessments.
- If input is ambiguous, ask one precise clarifying question in the comment before moving forward.

### Anti-template rule

- Do not post generic placeholders like "Understood... Goal... Action... Result..." without substantive content.
- If a factual question is asked (e.g., name/place), include the factual answer explicitly.

## Conversation-aware reply policy (mandatory)

- Use the full thread to avoid repeating already answered content.
- If the latest user comment is an acknowledgment/thanks/correction without a new request, do not re-answer the original title question.
- In that case, respond to the new comment intent only (e.g., confirm, adjust, ask one targeted follow-up if needed).
- Re-answer title/description only when:
  1. no prior answer exists in thread, or
  2. user explicitly asks to revisit/clarify/correct it.

### Latest unresolved question selection (mandatory, deterministic)

Before drafting a comment, run this selection logic over the thread:

1. Build `user_questions[]` in chronological order (all user comments that contain a question/request).
2. Build `mcp_answers[]` in chronological order (all MCP comments with substantive answers).
3. Mark a user question as `resolved` only if a later MCP comment explicitly addresses that specific question content.
4. Select `active_question` as the newest unresolved user question.
5. If `active_question` exists, answer it directly first line.
6. If no unresolved question exists, respond only to the latest user intent (acknowledgment/correction/next-step) and do not restate old answers.

Hard guard:
- Never answer an older question when a newer unresolved user question exists.
- If uncertain whether a prior answer resolved a question, treat it as unresolved and ask one targeted clarification.
- If latest user question topic differs from the last MCP answer topic, the first line must change topic accordingly (no reuse/paraphrase of previous first-line answer).
- Follow-up questions (e.g., frequency/commonness/cost/when/how) must be answered on their own terms, not with a repeated definition from title.

### Turn-lock before posting (mandatory)

Immediately before writing the MCP comment, compute and lock:
- `latest_user_comment_id`
- `active_question_id` (if any)
- `planned_reply_scope` (`active_question` or `latest_user_intent`)

Then enforce:
1. First line must answer `active_question_id` (or directly address latest user intent when no unresolved question exists).
2. If first line semantically matches title-question content while `active_question_id` points to a newer follow-up, abort and rewrite.
3. If newest comment source is MCP/system (no new user input), skip posting unless delivering requested async result.

This turn-lock check is a hard preflight gate; do not post until it passes.

## Temporal Context Gate (mandatory before commenting)

Use timestamps as first-class context, not optional metadata:

1. Build a compact event log for this task cycle:
   - `T0` = task created time,
   - `U[n]` = each user comment time,
   - `A[n]` = each MCP answer time.
2. Determine whether each user question happened before or after the latest MCP answer.
3. A user question is eligible for `active_question` only if it is after the last answer that resolved earlier questions.
4. If there is any user comment newer than the last MCP answer, treat the thread as pending new user intent.
5. Never treat title text as latest intent when newer user comments exist.

Mandatory preflight output (internal):
- `last_answer_at`
- `latest_user_comment_at`
- `newer_user_input_exists` (true/false)
- `active_question_id`

If `newer_user_input_exists=true`, the outgoing comment must address that newer input directly.

## Objective Alignment Check (mandatory before commenting)

Before posting, verify all three are present:
- `Objective`: one sentence stating what the task asks for (from title/description).
- `Action`: what was done this cycle toward that objective.
- `Outcome`: result, blocker, or next step.

Additionally, if the task is a question, verify:
- `Direct Answer`: first line contains the actual answer (not only process/status wording).
- `Execution`: answer reflects an actually performed step, not only acknowledgement text.

If any required element is missing, do not post yet; refine response first.

## Comment vs Document Policy

Use this decision rule per task update:

1. Comment only (default)
   - Use when response is short and clear.
   - Keep it compact; avoid long essays.

2. Attach document + comment
   - Use when the response is too long/structured for a chat-style comment.
   - Create a task document with the full content (`add_document_to_task`).
   - Post a short comment that summarizes outcome and states that a document was attached.

### Suggested thresholds for document usage

Attach a document when at least one is true:
- response would exceed ~600 characters,
- needs sections/checklists/code/logs,
- requires durable reference for review.

### Required short comment after document attach

Comment template:
- `Quick update: <1-2 line summary>. I've attached a document with the full details.`

## Safety Rules

- Respect task access control:
  - Skip updates if `protectionLevel` is `read_only` or `protected`.
- Never delete tasks automatically.
- Never close tasks automatically (`closed` is human approval).
- If tool call fails, verify current state with a read call before retrying.
- Retry write operations at most once.

## Internal Delegation Policy

Use one subagent role initially:
- Research Subagent (internal only)
  - gather supporting context,
  - compare related tasks/thoughts,
  - produce concise findings for KAM.

KAM responsibilities:
- decide whether to delegate,
- synthesize final user-facing answer,
- post final comment and status change.

### Direct-answer first rule (critical)

- The KAM must answer the user question directly without spawning research when the question is straightforward or can be answered confidently from known context.
- Spawn research only when at least one is true:
  1. missing factual certainty,
  2. multi-step analysis is required,
  3. cross-task/habitat synthesis is needed.
- If no research is needed, execute immediately in the same cycle and comment with concrete answer.

### Explicit research-intent override (mandatory)

If the latest user message explicitly requests research/deep-dive/analysis (e.g., "research this", "please investigate", "do deep research", "compare sources"), this overrides direct-answer-first:

1. Spawn exactly one internal Research Subagent for that task cycle.
2. Do not post a final factual answer before the research result returns.
3. Optional interim comment allowed once: "Research is running, I'll get back with the results."
4. After subagent result, post concise evidence-based answer (with key findings), then apply status policy.

Hard guard:
- When explicit research intent is present, a quick direct-answer comment without delegation is invalid.

## Status Policy

- `todo` -> only claim if explicitly configured.
- `doing` -> primary working state for this skill.
- `done` -> target after KAM update when work package is ready for review.
- `closed` -> human-only transition.

### Done/Review Gate

Move `doing` -> `done` only if one of these is true:
1. requested deliverable from title/description is completed, or
2. deliverable cannot continue until user answers a concrete question that was posted.

Additionally:
- If latest user comment is just conversational acknowledgment and no new work was performed in this cycle, keep current status unchanged.
- Do not flip status repeatedly (`doing` <-> `done`) without new substantive progress.

Critical completion guard:
- Never move to `done` unless the thread already contains at least one substantive MCP answer.
- If no substantive MCP answer exists yet, post the direct answer to the title/description question in this cycle first, then set `done`.
- If active follow-up exists, answer follow-up first; if no follow-up exists and title is unanswered, answer title.

Otherwise keep `doing` and post a short progress comment.

## Idempotency

- Before adding a new comment, check whether the latest MCP comment already reflects the current latest user comment.
- Avoid duplicate comments for unchanged input.
- Avoid repeated `done` writes if task is already `done`.

## Regression Examples (must pass)

Example A (follow-up question):
- Title: `What is the best CRM strategy for KAM?`
- User comment #1: `Thanks. And how do I concretely start tomorrow?`
- MCP previously answered title question.
- Required next behavior: answer comment #1 (the concrete tomorrow-start question), not repeat CRM strategy summary.

Example B (ack only):
- User latest comment: `Perfect, thanks!`
- Required next behavior: brief acknowledgment or no-op; do not restate previous answer.

Example C (correction):
- User latest comment: `No, I meant B2B SaaS, not E-Commerce.`
- Required next behavior: adapt answer to corrected scope; do not re-send old generic answer.

## Subagent Execution Notes

- Use `sessions_spawn` for internal research runs.
- Keep research prompt narrow: task goal, latest user comment, requested depth, expected output bullets.
- Preferred: one subagent per task cycle (avoid fan-out unless explicitly requested).
- Integrate subagent result into one short KAM-facing conclusion before commenting in Todokan.

## Minimal Per-Task Output Format (for logs/summaries)

- Task: `<title>` (`<id>`)
- Latest comment source: `<user|mcp|system>`
- Comment count: `<n>`
- Action: `commented` / `skipped` / `error`
- Status change: `<from> -> <to>` or `none`
