---
name: skill-cortex
description: >
  Skill Cortex is the system's capability cortex.
  When lacking ability, it autonomously acquires Skills from ClawHub or GitHub, then releases them after use.
  Every invocation is learned and reinforced by the cortex — future identical tasks fire as reflexes, bypassing search.
  Manages only short-term capability memory; never interferes with long-term Skills.
  Continuously restructures its own capability architecture through reinforcement and decay, achieving ongoing evolution.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - clawhub
---

# Skill Cortex

Triggers when installed Skills cannot complete the current task. If you can handle it yourself, just do it — do not trigger this flow.

Cortex data file: `~/.openclaw/skill-cortex/cortex.json` (schema in `docs/DESIGN.md`).

---

## Phase 1: Perception

1. Read `cortex.json` (if missing or corrupt, skip to step 3).
2. **Semantically match** the user's task description against `sensory.patterns` signals (no exact match required — use your own judgment on intent alignment). On hit, look up the corresponding region in `motor`, sort candidates by effective weight (`effective_weight = weight * max(0.3, 1 - days_since_last_used / 180)`), filter out blacklisted and effective_weight < 0.3 entries, then proceed to Phase 2.
3. On miss, search ClawHub: `clawhub search "<3-5 English keywords>"`. Read summaries only, pick up to **3** candidates. If fewer than 2 relevant results, supplement with a GitHub search (mark as unreviewed source).

---

## Phase 2: Validation & Authorization

### Reflex Fast Path

The top candidate may enter reflex mode when ALL of the following hold:
- `reflex: true` AND effective_weight >= 0.90 AND consecutive successes >= 5
- **No write side effects** (side_effects contains no `write:`/`delete:`/`shell:` prefix)
- **Version unchanged** (slug + version match the stored record)

Reflex mode **skips only the execution plan confirmation**. Installation still requires user notification:

```
⚡ Skill Cortex reflex: todoist-cli v1.2.0 (96% success rate)
   Task: query today's todos (read-only) | Will install and execute. Say cancel to abort.
```

Version change automatically downgrades to standard mode.

### Standard Mode

Present candidates to the user (name, description, stars, downloads, source, security scan status, history). **Wait for explicit approval before installing.**

If `prefrontal.lessons` contain experiences matching the current region, retain them for use in Phase 3.

---

## Phase 3: Execution

### 3.1 Install

```bash
clawhub install <slug>
```

On failure, auto-switch to the next candidate. Max **2** switches, then stop and report.

### 3.2 Execution Plan

Read the installed Skill's SKILL.md and present to the user:
- Step summary
- Side-effect severity: 🟢 read-only 🟡 write 🔴 destructive 🔑 sensitive credentials ⚙️ shell commands
- Relevant prefrontal lessons (if any) — e.g., proactively check for a dependency known to be commonly missing

**Reflex mode skips this step. Standard mode waits for user confirmation.**

### 3.3 Execute

Follow the Skill's instructions to complete the task.

### 3.4 Failure Recovery

| Type | Handling |
|---|---|
| `dependency_missing` | **Show the user what needs to be installed, proceed only after confirmation** |
| `api_error` | Wait 3 seconds, retry once |
| `auth_error` | Prompt user to check credentials, do not auto-retry |
| `task_mismatch` | Uninstall, suggest switching to next candidate |
| `runtime_error` | Uninstall, suggest switching to next candidate |

Switching candidates requires user consent. After all candidates fail, provide a full report with each failure reason and suggested remediation.

---

## Phase 4: Learning & Cleanup

Execute regardless of success or failure.

### 4.1 Update Motor

Success: `new_weight = old + (1 - old) * 0.15 * (1 / (1 + successes_in_last_7d))`
Failure: `new_weight = old * decay` (task_mismatch: 0.4 / runtime: 0.6 / auth: 0.8 / dependency: 0.85 / api: 0.9)
New Skill initial weight = 0.5. Record `skill_md_chars` (SKILL.md character count) and `version`.
Create region if it doesn't exist. Update `last_used`.

### 4.2 Update Sensory

When this task was resolved via search (sensory miss), extract 2–4 signal words from the task description and merge into the corresponding region's pattern. Merge into existing patterns; do not create duplicates.

**Entity Filtering (mandatory):** Before writing signal words, strip all concrete entities — personal names, company names, place names, dates, numeric values, filenames, URLs, emails, etc. Retain only verbs and abstract nouns.
Example: user says "Look up Alice's Q3 sales report" → signals should be `["query", "sales", "report"]`, NOT `["Alice", "Q3"]`.

### 4.3 Update Prefrontal

Record **structured** lessons only in the following cases (no free-form):

```jsonc
// Type 1: Same failure type occurs 2+ times → dependency pre-check
{ "type": "dependency_warning", "region": "...", "key": "imagemagick", "action": "check_bin_before_install", "confidence": 0.6 }
// Type 2: Skill description does not match actual capability
{ "type": "skill_quality_warning", "slug": "xxx", "detail": "does not support batch ops", "confidence": 0.6 }
// Type 3: User environment is typically ready
{ "type": "env_ready", "region": "...", "key": "TODOIST_API_KEY", "confidence": 0.6 }
```

Confidence +0.1 each time validated (cap 1.0). Remove when < 0.3 during pruning.

### 4.4 Reflex Promotion

Set `reflex: true` when ALL conditions are met: success >= 5, weight >= 0.90, no write side effects.
Immediately reset `reflex: false` on any failure or version change.

### 4.5 Cleanup

**Default: uninstall.** `clawhub uninstall <slug>`

**Suggest retention** (when ALL met): success >= 3, weight >= 0.8, skill_md_chars < 8000.
Approved → keep installed, remove record from motor (transfers to OpenClaw native management). Declined → uninstall normally.

### 4.6 Pruning

- Motor: max 5 candidates per region / max 80 regions / remove effective_weight < 0.1
- Sensory: remove pattern when its region is pruned / max 10 signals per pattern
- Prefrontal: max 30 lessons / remove confidence < 0.3 / remove if linked region is pruned

---

## Boundary Rules

1. Never interfere with long-term Skills.
2. Installation requires user confirmation (including reflex mode).
3. System dependency installation requires separate confirmation.
4. Write operations never enter reflex. Reflex locks version; version change auto-downgrades.
5. Max 2 candidate switches.
6. On cortex file corruption, degrade to direct ClawHub search; rebuild after task.
7. Read latest cortex file before writing; merge changes, never overwrite.
8. Single-session design; cortex data may be inconsistent under concurrent sessions.
