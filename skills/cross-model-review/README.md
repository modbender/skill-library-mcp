# cross-model-review

![CI](https://github.com/Don-GBot/adversarial-review/actions/workflows/ci.yml/badge.svg)

Runs implementation plans through an adversarial review loop between two different AI models — a reviewer and a planner — iterating until the reviewer approves or maximum rounds are hit. The reviewer challenges the plan, the planner (you, the main agent) revises it, and this continues until all CRITICAL and HIGH issues are resolved. Think of it as a built-in second opinion that can't be gamed because it's a different model from a different provider.

---

## When NOT to Use

Skip this skill for:
- Simple one-file fixes or quick scripts
- Pure research or investigation tasks
- Changes you can fully reverse in under 5 minutes
- Plans already reviewed by a human engineer in the last hour

Using it on trivial tasks adds overhead without benefit.

---

## Prerequisites

- **Node.js >= 18.0.0** (uses `structuredClone`, `fs.readSync` on fd 0, etc.)
- **OpenClaw** — the skill is invoked by the OpenClaw agent and relies on `sessions_spawn` for the reviewer
- No npm install needed — zero external dependencies

---

## Quick Start

**Install from ClawHub:**
```
/install cross-model-review
```

**Trigger phrases** (say any of these with a plan in context):
- "review this plan"
- "cross review"
- "challenge this"
- "is this plan solid?"

The skill activates automatically and manages the full loop. No manual setup needed.

---

## Complete CLI Transcript (end-to-end)

This shows what the agent runs under the hood for a 2-round review that ends in approval.

```
# Step 1: write plan to temp file
$ cat /tmp/review-1234/plan.md
# Auth Redesign Plan
...

# Step 2: initialize workspace
$ node scripts/review.js init \
    --plan /tmp/review-1234/plan.md \
    --reviewer-model openai/gpt-4 \
    --planner-model anthropic/claude-sonnet-4-6 \
    --out tasks/reviews
tasks/reviews/2026-02-21T15-00-00-a1b2c3d4

# Step 3: round 1 — agent spawns reviewer, saves response, parses it
$ node scripts/review.js parse-round \
    --workspace tasks/reviews/2026-02-21T15-00-00-a1b2c3d4 \
    --round 1 \
    --response /tmp/review-1234/round-1-response.json
{
  "verdict": "REVISE",
  "round": 1,
  "newIssues": 2,
  "dedupWarnings": 0,
  "blockers": 1,
  "dedupWarningDetails": []
}
# exit code: 1 (REVISE)

# Agent revises plan, saves to plan-v2.md, spawns reviewer for round 2

# Step 4: round 2
$ node scripts/review.js parse-round \
    --workspace tasks/reviews/2026-02-21T15-00-00-a1b2c3d4 \
    --round 2 \
    --response /tmp/review-1234/round-2-response.json
{
  "verdict": "APPROVED",
  "round": 2,
  "newIssues": 0,
  "dedupWarnings": 0,
  "blockers": 0,
  "dedupWarningDetails": []
}
# exit code: 0 (APPROVED)

# Step 5: finalize
$ node scripts/review.js finalize \
    --workspace tasks/reviews/2026-02-21T15-00-00-a1b2c3d4
{
  "verdict": "APPROVED",
  "planFinal": "tasks/reviews/2026-02-21T15-00-00-a1b2c3d4/plan-final.md",
  "summaryJson": "tasks/reviews/2026-02-21T15-00-00-a1b2c3d4/summary.json",
  "rounds": 2,
  "issuesFound": 2,
  "issuesResolved": 2,
  "forceApproved": false
}
# exit code: 0
```

---

## How It Works

```
You share a plan
      │
      ▼
┌─────────────────────────────────────────────┐
│  Round N (max 5)                            │
│                                             │
│  1. Agent builds reviewer prompt            │
│     (plan wrapped in UNTRUSTED delimiters)  │
│                                             │
│  2. Reviewer (different model) spawned      │
│     → outputs structured JSON verdict       │
│                                             │
│  3. review.js parses response:              │
│     - Assigns stable issue IDs (ISS-001...) │
│     - Runs dedup check (Jaccard ≥ 0.6)      │
│       (cross-round AND within same batch)   │
│     - Updates issue tracker                 │
│     - Checks CRITICAL/HIGH blockers         │
│                                             │
│  4a. APPROVED → finalize, present summary   │
│  4b. REVISE → agent revises plan, loop      │
└─────────────────────────────────────────────┘
      │
      ▼ (if max rounds hit without approval)
Present unresolved issues → ask user to override or manually revise
```

**Cross-provider enforcement:** reviewer and planner must be from different provider families (e.g. Anthropic + OpenAI). Same-provider reviews are rejected. Unrecognized model IDs produce a warning but are allowed — you are responsible for ensuring actual cross-provider separation.

**Prompt injection protection:** plan content is always wrapped in `<<<UNTRUSTED_PLAN_CONTENT>>>` delimiters and the reviewer is instructed to treat it as data only.

---

## Why Not Single-Model Review?

A model reviewing its own output has a systematic blind spot: it tends to agree with the reasoning that generated the plan in the first place, since the reasoning style is identical. It will flag syntax errors but miss architectural mistakes rooted in assumptions it shares with the planner.

A different model from a different provider was trained on different data, with different RLHF preferences, and will often disagree with the first model on style, safety posture, and architectural trade-offs. That disagreement is the signal. This skill forces that disagreement to surface as structured, actionable issues rather than letting it stay hidden.

---

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| Reviewer model | `openai/gpt-4` | Must be different provider from planner |
| Planner model | Your current model | Detected automatically |
| Max rounds | `5` | Override via `--max-rounds` in `init` |
| Token budget | `8000` | For codebase context via `--token-budget` in `init` |

To use a different reviewer model, ask: *"cross review this plan using gemini as reviewer"*

---

## Output Structure

Each review run creates a workspace in `tasks/reviews/<timestamp>-<uuid>/`:

```
tasks/reviews/2026-02-21T15-00-00-abc12345/
├── plan-v1.md          # Original plan
├── plan-v2.md          # After round 1 revisions
├── plan-final.md       # Clean final plan (no review comments)
├── changelog.md        # What changed each round
├── issues.json         # Full issue tracker with lifecycle
├── meta.json           # Run metadata (models, rounds, verdict, maxRounds, tokenBudget)
├── round-1-response.json  # Raw reviewer response
├── round-1-output.json    # Parsed round output + dedup warnings
└── summary.json        # Final stats and verdict
```

**Verdict location:** `meta.json` (field: `verdict`) and in the JSON printed to stdout by `parse-round`. Do NOT read verdict from `issues.json` — that file contains issue records only.

**summary.json:**
```json
{
  "rounds": 2,
  "plannerModel": "anthropic/claude-sonnet-4-6",
  "reviewerModel": "openai/gpt-4",
  "totalIssuesFound": 2,
  "issuesBySeverity": { "critical": 0, "high": 1, "medium": 1, "low": 0 },
  "issuesResolved": 2,
  "issuesUnresolved": 0,
  "finalVerdict": "APPROVED",
  "completedAt": "2026-02-21T15-03:45.000Z",
  "force_approve_log": null
}
```

---

## Force-Approve (Override)

If max rounds hit and CRITICAL/HIGH issues remain unresolved:

**Interactive (TTY):**
```bash
node scripts/review.js finalize \
  --workspace tasks/reviews/<run> \
  --override-reason "Deadline constraint, will fix post-launch"
# Prompts: Type "CONFIRM" to proceed
```

**Non-interactive (CI / agent loop):**
```bash
node scripts/review.js finalize \
  --workspace tasks/reviews/<run> \
  --override-reason "Emergency hotfix, security team notified" \
  --ci-force
```

Force-approvals are logged in `summary.json` under `force_approve_log` with actor, reason, timestamp, and unresolved issue IDs.

---

## Integration with coding-agent

When `coding-agent` dispatches a plan that touches auth, payments, or data models, `cross-model-review` runs as a pre-flight gate. Coding-agent only proceeds if `review.js` exits with code 0.

Exit codes:
- `0` — Approved, all blockers resolved
- `1` — Revise (max rounds hit or unresolved issues)
- `2` — Error (parse failure, bad flags, same-provider rejection)

---

## Issue Tracking

Issues get stable IDs on first detection (`ISS-001`, `ISS-002`, ...):

```json
{
  "id": "ISS-003",
  "severity": "HIGH",
  "location": "Auth module",
  "problem": "No rate limiting on login endpoint",
  "fix": "Add rate-limit middleware, 5 attempts per 15 min",
  "status": "resolved",
  "round_found": 1,
  "round_resolved": 2,
  "last_evidence": "Rate limiting added in section 3.2"
}
```

Statuses: `open` → `resolved | still-open | regressed | not-applicable | force-approved`

Dedup: script flags new issues with Jaccard similarity ≥ 0.6 vs open issues AND vs other new issues in the same batch as `dedup_warnings`. Human reviews the flags — no auto-merge.

---

## Troubleshooting

**Parse failure (exit code 2 from parse-round)**
The reviewer returned malformed JSON. `review.js` will print the schema errors. Re-prompt the reviewer with: "Your response was not valid JSON. Please respond with ONLY the JSON schema specified, no other text." If it fails twice, stop and escalate.

**Reviewer timeout or model unavailable**
The spawned reviewer session did not return a response within the timeout. Retry once with the same model. If it fails again, consider switching reviewer models via a fresh `init` with `--reviewer-model`. Do not proceed to coding-agent without a valid review.

**Same-provider rejection (exit code 2 from init)**
The reviewer and planner resolved to the same provider family. Use a reviewer from a different provider. Example: if your planner is `anthropic/claude-*`, use `openai/gpt-*`, `google/gemini-*`, or `mistral/*` as reviewer.

**Unrecognized model ID (warning, not failure)**
If the model ID doesn't match any known provider keywords, the script warns but allows. Check that you're actually using a different provider — the warning means the cross-provider constraint cannot be verified automatically.

**File paths with spaces**
Always quote `--plan` and `--workspace` arguments if the path contains spaces:
```bash
node scripts/review.js init --plan "/my projects/plan.md" ...
```

---

## Publishing

Built by Don-GBot for the OpenClaw ecosystem. v1.0.1 targets single-reviewer, sessions_spawn backend only. Parallel multi-reviewer and Codex CLI resume mode are v2 scope.

ClawHub slug: `cross-model-review`
Tags: `code-review` `multi-model` `adversarial` `planning` `quality`
