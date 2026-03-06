---
name: buffer
description: "Session management for OpenClaw agents. Context monitoring, structured handoffs, and performance optimization — so you never lose context again."
---

# Buffer

## First Run

Check if `buffer-optimizer` exists as a sibling skill directory. Look for `skills/buffer-optimizer/SKILL.md` relative to your workspace.

**If it does NOT exist**, extract it now:

1. Create directory `skills/buffer-optimizer/`
2. Write `skills/buffer-optimizer/SKILL.md` with the exact contents of the **Embedded: buffer-optimizer** section below.
3. If the skill references shell scripts (`{baseDir}/scripts/measure-boot.sh` and `{baseDir}/scripts/audit-agents-md.sh`), create those too from the **Embedded Scripts** section.
4. Run the **Setup** steps from the embedded optimizer (create HANDOFF.md if missing, validate MEMORY.md, check AGENTS.md structure).
5. Tell the owner what was set up and that workspace audits are now available via `buffer-optimizer`.

**If extraction fails** (sandbox, read-only filesystem, write tool denied):
- Tell the owner: "I can't write files to the skills directory. Install the optimizer separately: `clawhub install buffer-optimizer`"
- Continue with normal session management below.

**If buffer-optimizer already exists**, skip extraction. Proceed to the mode that matches your situation.

---

## Start

Run at every new session. Goal: recover context instantly.

1. Read HANDOFF.md — where you left off, outcomes, next steps.
2. Read MEMORY.md — priorities, projects, people.
3. Start working. Do not read other files unless the task requires them.

**No HANDOFF.md?** Check recent `memory/*.md` files, try `memory_search`, then ask the owner. Run `buffer-optimizer` to set up your workspace.

---

## Monitor

Apply continuously during the session.

### Intake
Before loading content:
- **Changed?** Don't re-read unmodified files.
- **Need all of it?** Use `grep`, `head`, `limit`/`offset` over full reads.
- **Can reference instead?** Write large output to file, read summary.
- **Cache impact?** Don't edit AGENTS.md/SOUL.md/USER.md/MEMORY.md mid-session (breaks prompt cache, 10x cost).

### Output
- Redirect heavy output (>20 lines) to `/tmp`, read tail/summary.
- Pipe long commands through `tail`/`head`/`grep`.

### Context Thresholds

Thresholds are percentages of your model's context window. Run `session_status` — the Context line shows current usage.

| Usage | Action |
|---|---|
| **<25%** | No concern. Full performance. |
| **25-40%** | Be intentional about what you load. |
| **40-50%** | ⚠️ Warn owner. Degradation begins on complex tasks. |
| **>50%** | 🔴 Wrap now. |

### Degradation signals — warn the owner and recommend wrapping if you notice:
- Repeating yourself (context distraction)
- Forgetting earlier decisions (retrieval failure)
- Ignoring relevant earlier context (recency bias)
- Confusion from conflicting information (context clash)
- Referencing something that was wrong earlier (context poisoning)

Do not wrap unilaterally — warn first, let the owner decide when to wrap.

### Continuous persistence
Don't wait for wrap to save important information. As decisions happen, append key outcomes to HANDOFF.md or a scratch file. If you have a long-term memory system, write decisions there immediately.

Test: if this session crashed now, would important stuff survive?

---

## Wrap

Run when: owner says "wrap session", you hit 50% context, or conversation concludes.

### Step 1: Extract from the session
Scan for: decisions, outcomes, open questions, corrections, next steps.

### Step 2: Write HANDOFF.md
Overwrite with current state:

```markdown
# HANDOFF.md

## Current Work
[One line — focus area.]

## Stopping Point
[One line — where you left off.]

## Key Outcomes
- [Conclusions, not activities. "X works because Y" not "tested X".]

## Open Questions
- [Each must be actionable by the next session.]

## Next Steps
1. [Most important first. ≤5 items.]
```

**Rules:**
- ≤2KB. Over? Compress outcomes to conclusions only.
- Outcomes = conclusions, not activities.
- Cut anything that doesn't affect future work.
- No architecture docs, standing policies, or issue lists.

### Step 3: Update MEMORY.md only if structure changed
New project, priority shift, new key person, or week rollover. Most sessions: don't touch it.

### Step 4: Persist unpersisted decisions
Scan for decisions or outcomes not yet captured in HANDOFF.md.

### Step 5: Confirm to owner
What was saved. Whether MEMORY.md was updated. Top next step.

---

## Quick Reference

| File | Purpose | Target | Updated |
|---|---|---|---|
| HANDOFF.md | Session state — recovery file | ≤2KB | Every wrap |
| MEMORY.md | Big picture — priorities, projects, people | ≤1.5KB | When structure changes |
| AGENTS.md | Behavioral rules | ≤4KB | Rarely |

| Zone | Range | Behavior |
|---|---|---|
| Green | <25% | Full performance |
| Yellow | 25-40% | Intentional loading |
| Orange | 40-50% | Warn owner, prepare to wrap |
| Red | >50% | Wrap immediately |

---

## Embedded: buffer-optimizer

On first run, write this as `skills/buffer-optimizer/SKILL.md`:

```
---
name: buffer-optimizer
description: "Workspace auditing and setup for Buffer. Measures boot payload, checks AGENTS.md structure, classifies skills, validates memory files. Run on first install, when things feel off, or every week or two. Companion to the buffer skill."
---

# Buffer Optimizer

Two modes: **setup** (first install) and **audit** (periodic maintenance).

---

## Setup

Run on first install, or when the owner asks to configure their workspace.

### 1. Create HANDOFF.md
If missing, create:

# HANDOFF.md
## Current Work
## Stopping Point
## Key Outcomes
## Open Questions
## Next Steps

### 2. Validate MEMORY.md
Must contain only: this week (2-3 lines), priorities (≤5), project states (one line each), key people. Target: ≤1.5KB. If missing, create a minimal version with the owner's name and current focus.

### 3. Check AGENTS.md structure
Verify these exist. If missing, draft them and present to owner for approval:

**Pre-response checkpoint** (must be the first section):

## Before Every Response
1. Does this message match a skill trigger? → Load that skill.
2. Am I about to do something a skill already handles? → Use the skill.

**Skill trigger table** (immediately after checkpoint):

## Skill Triggers
| Event | Skill |
|---|---|
| [event] | [skill-name] |

**Negative triggers:**

## Don't Reinvent Skills
- [manual pattern] → Use [skill-name]

**Context management rules:**

## Context Management
- Heavy output (>20 lines): redirect to file, read summary.
- Use targeted reads (limit/offset, grep, tail) over full file loads.
- 40-50% context: Warn owner. >50%: Wrap immediately.
- Don't edit boot files mid-session (breaks prompt cache, 10x cost).

### 4. Classify skills
List all loaded skills. Classify as DAILY/WEEKLY/RARE/NEVER. Draft a daily driver list. Flag NEVER skills for potential exclusion.

### 5. Report setup status
Tell the owner what was created, what was validated, and what needs their review.

---

## Audit

Run periodically (weekly or bi-weekly), after major changes, or when the owner asks.

### Step 1: Measure Boot Payload

Run `bash {baseDir}/scripts/measure-boot.sh` if the script exists. Otherwise measure manually.

#### Thresholds

| File | Target | Action if exceeded |
|---|---|---|
| AGENTS.md | ≤4KB | Convert descriptions to directives. Move reference content out. |
| MEMORY.md | ≤1.5KB | Keep only: this week, priorities, projects, people. |
| HANDOFF.md | ≤2KB | Apply template: current work, stopping point, outcomes, questions, next steps. |
| Each memory/*.md | ≤2KB | Summarize transcripts. |
| Total boot | ≤12KB | Something doesn't belong in boot. |
| Skills loaded | <20 | Exclude unused skills (~75 tokens each). |

### Step 2: Audit AGENTS.md

Run `bash {baseDir}/scripts/audit-agents-md.sh` if the script exists. Otherwise check manually.

Verify:
- 2.1 Pre-response checkpoint is the first section.
- 2.2 Skill trigger table immediately follows.
- 2.3 Negative triggers section exists.
- 2.4 No weak patterns ("You have access to", "Consider", "Try to", "If appropriate" → rewrite as imperatives).
- 2.5 Sections grouped by trigger, not topic.

### Step 3: Audit Skills

- Count skills from available_skills in system prompt.
- Classify each: DAILY / WEEKLY / RARE / NEVER.
- Draft daily driver list for AGENTS.md.
- Draft exclusion list. Present to owner — do not exclude unilaterally.

### Step 4: Audit Memory Files

- MEMORY.md — only: this week, priorities, projects, people. Flag old history, architecture, URLs.
- HANDOFF.md — only: current work, stopping point, outcomes, questions, next steps. Outcomes = conclusions, not activities.
- memory/*.md — over 2KB → summarize. Over 3 days → archive. Duplicates → remove.
- Ghost files — flag any .md in workspace root not in: AGENTS.md, SOUL.md, USER.md, MEMORY.md, HANDOFF.md, IDENTITY.md.

### Step 5: Check Reliability

- Compaction flush: Enabled? If unknown, flag.
- Wrap ritual: Does buffer skill exist? If missing, recommend install.
- Automated persistence: Write hooks, observers, auto-commit? If none, flag as priority gap.

### Step 6: Self-Tests

- Recovery: Read HANDOFF.md — does it reflect current state?
- Skill bypass: Did you recently do manually what a daily driver skill handles?
- Drift: Re-read AGENTS.md. Flag any instruction you're not following.

### Step 7: Report

## Buffer Audit Report — [date]

### Boot Payload
- Total: X bytes (~Y tokens) [PASS/OVER 12KB]
- [file-by-file with pass/fail]

### AGENTS.md Structure
- Pre-response checkpoint: [YES/NO]
- Triggers first: [YES/NO]
- Negative triggers: [YES/NO]
- Weak patterns: [count]
- Organization: [trigger/topic]

### Skills
- Loaded: N (target: <20)
- Daily drivers: [list]
- Exclusion candidates: [list] (~X tokens saved)

### Memory
- MEMORY.md: X bytes [PASS/OVER]
- HANDOFF.md: X bytes [PASS/OVER]
- Ghost files: [list or none]
- Files needing work: [list or none]

### Reliability
- Compaction flush: [enabled/disabled/unknown]
- Wrap ritual: [exists/missing]
- Persistence: [exists/missing]

### Self-Tests
- Recovery: [yes/no]
- Skill bypasses: [list or none]
- Drift: [list or none]

### Proposed Changes
1. [Change] — [rationale]. Saves ~X tokens.

Wait for owner approval before implementing.
```

---

## Embedded Scripts

If shell access is available, also create these scripts in `skills/buffer-optimizer/scripts/`:

### measure-boot.sh
```bash
#!/bin/bash
set -e
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
echo "=== BOOT FILE SIZES ==="
total=0
for f in AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md; do
  path="$WORKSPACE/$f"
  if [ -f "$path" ]; then
    size=$(wc -c < "$path")
    lines=$(wc -l < "$path")
    tokens=$((size / 4))
    total=$((total + size))
    printf "  %-15s %6d bytes  %4d lines  ~%5d tokens\n" "$f" "$size" "$lines" "$tokens"
  fi
done
echo "  ---"
printf "  %-15s %6d bytes              ~%5d tokens\n" "TOTAL" "$total" "$((total / 4))"
echo ""
echo "=== MEMORY FILES ==="
mem_count=$(ls "$WORKSPACE"/memory/*.md 2>/dev/null | wc -l | tr -d ' ')
mem_bytes=$(wc -c "$WORKSPACE"/memory/*.md 2>/dev/null | tail -1 | awk '{print $1}')
echo "  Files: $mem_count"
echo "  Total: ${mem_bytes:-0} bytes"
echo ""
echo "=== SKILLS ==="
builtin_dir="/opt/homebrew/lib/node_modules/openclaw/skills"
custom_dir="$WORKSPACE/skills"
builtin_count=$(ls "$builtin_dir" 2>/dev/null | wc -l | tr -d ' ')
custom_count=$(ls "$custom_dir" 2>/dev/null | wc -l | tr -d ' ')
echo "  Built-in: $builtin_count"
echo "  Custom: $custom_count"
echo "  Total: $((builtin_count + custom_count))"
echo ""
echo "=== GHOST FILE CHECK ==="
recognized="AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md"
for f in "$WORKSPACE"/*.md; do
  name=$(basename "$f")
  if ! echo "$recognized" | grep -qw "$name"; then
    echo "  ⚠️  $name — NOT auto-loaded by OpenClaw"
  fi
done
echo ""
echo "=== THRESHOLDS ==="
check() {
  local name="$1" size="$2" limit="$3"
  if [ "$size" -gt "$limit" ]; then
    echo "  🔴 $name: ${size}B > ${limit}B limit"
  else
    echo "  ✅ $name: ${size}B (under ${limit}B)"
  fi
}
for f in AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md; do
  path="$WORKSPACE/$f"
  [ -f "$path" ] || continue
  size=$(wc -c < "$path")
  case "$f" in
    AGENTS.md) check "$f" "$size" 4000 ;;
    MEMORY.md) check "$f" "$size" 1500 ;;
    HANDOFF.md) check "$f" "$size" 2000 ;;
    *) check "$f" "$size" 1500 ;;
  esac
done
check "Total boot" "$total" 12000
echo "  Skills: $((builtin_count + custom_count)) (target: <20)"
```

### audit-agents-md.sh
```bash
#!/bin/bash
set -e
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
AGENTS="$WORKSPACE/AGENTS.md"
if [ ! -f "$AGENTS" ]; then
  echo "ERROR: AGENTS.md not found at $AGENTS"
  exit 1
fi
echo "=== AGENTS.MD STRUCTURE AUDIT ==="
echo ""
first_h2=$(grep -n "^## " "$AGENTS" | head -1)
echo "First section: $first_h2"
if echo "$first_h2" | grep -qi "skill\|trigger"; then
  echo "  ✅ Skill triggers are the first section"
else
  echo "  🔴 Skill triggers are NOT first."
fi
echo ""
if grep -qi "before every response\|pre-response\|checkpoint" "$AGENTS"; then
  echo "  ✅ Pre-response checkpoint found"
else
  echo "  🔴 No pre-response checkpoint."
fi
if grep -qi "don't reinvent\|don't bypass\|never manually" "$AGENTS"; then
  echo "  ✅ Negative triggers found"
else
  echo "  🔴 No negative triggers."
fi
echo ""
echo "=== INSTRUCTION QUALITY ==="
weak=0
while IFS= read -r line; do
  [[ -z "$line" || "$line" =~ ^# || "$line" =~ ^\<!-- ]] && continue
  for pattern in "You have access" "you might want" "consider " "try to " "if appropriate" "you could" "feel free" "it.s recommended"; do
    if echo "$line" | grep -qi "$pattern"; then
      echo "  ⚠️  Weak: \"$(echo "$line" | head -c 100)\""
      weak=$((weak + 1))
    fi
  done
done < "$AGENTS"
if [ "$weak" -eq 0 ]; then
  echo "  ✅ No weak patterns found"
else
  echo "  Found $weak weak patterns."
fi
echo ""
echo "=== SECTIONS ==="
grep "^## " "$AGENTS" | while read -r line; do
  echo "  $line"
done
```
