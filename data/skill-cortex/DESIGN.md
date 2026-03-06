# Skill Cortex — Design Document

This document contains the full cortex file schema, weight algorithm derivations, and design decision records.
The Agent does NOT need to read this file during normal operation. Consult only when:
- Creating `cortex.json` for the first time
- Rebuilding after cortex file corruption
- Debugging weight anomalies

---

## Cortex File Schema

File path: `~/.openclaw/skill-cortex/cortex.json`

```jsonc
{
  "version": 1,
  "cortex": {

    // ── Sensory Cortex: signal words → task region semantic mapping ──
    // Agent uses semantic matching (not exact) in Phase 1 to judge intent alignment
    // Signal words must pass entity filtering — retain only verbs and abstract nouns
    "sensory": {
      "patterns": [
        {
          "signal": ["manage", "todo", "task", "reminder"],
          "region": "task-management"
        },
        {
          "signal": ["image", "convert", "resize", "compress", "thumbnail"],
          "region": "image-processing"
        }
      ]
    },

    // ── Motor Cortex: task region → Skill candidate routing ──
    "motor": {
      "task-management": {
        "candidates": [
          {
            "slug": "todoist-cli",
            "source": "clawhub",          // "clawhub" | "github"
            "version": "1.2.0",            // locked version for reflex validation
            "weight": 0.85,                // 0.0 ~ 1.0
            "runs": {
              "success": 4,
              "fail": 1,
              "recent_successes_7d": 2     // successes in last 7 days, for frequency-sensitive calc
            },
            "last_fail": {                 // most recent failure, null if never failed
              "type": "auth_error",        // dependency_missing | auth_error | api_error | task_mismatch | runtime_error
              "detail": "TODOIST_API_KEY not set",
              "date": "2026-02-20"
            },
            "side_effects": [              // side-effect tags
              "read:env:TODOIST_API_KEY",
              "network:api.todoist.com"
              // write-op prefixes: "write:", "delete:", "shell:"
              // Skills with these prefixes can NEVER enter reflex mode
            ],
            "skill_md_chars": 1200,        // character count of SKILL.md
            "reflex": false                // whether promoted to reflex
          }
        ],
        "last_used": "2026-02-24"          // ISO date, for time-decay calculation
      }
    },

    // ── Prefrontal Cortex: structured experiences ──
    // Only the following three types are allowed — no free-form
    "prefrontal": {
      "lessons": [
        {
          "type": "dependency_warning",
          "region": "image-processing",
          "key": "imagemagick",
          "action": "check_bin_before_install",
          "confidence": 0.9,
          "created": "2026-02-18"
        },
        {
          "type": "skill_quality_warning",
          "slug": "fake-image-tool",
          "detail": "claims WebP support but actually does not",
          "confidence": 0.7,
          "created": "2026-02-19"
        },
        {
          "type": "env_ready",
          "region": "task-management",
          "key": "TODOIST_API_KEY",
          "confidence": 0.8,
          "created": "2026-02-20"
        }
      ]
    }
  },

  "blacklist": [
    "known-malicious-skill"
  ],

  "stats": {
    "searches": 12,
    "installs": 8,
    "cache_hits": 5,
    "reflexes_fired": 3
  }
}
```

---

## Weight Algorithm

### Effective Weight (computed at query time, never written back)

```
days = today - motor[region].last_used
decay = max(0.3, 1 - days / 180)
effective_weight = candidate.weight * decay
```

A region unused for 180 days sees its candidates' effective weights drop to stored_weight × 0.3.
This does not alter the stored weight — it only affects sorting and filtering.

### Success Update

```
boost = 0.15 * (1 / (1 + recent_successes_7d))
new_weight = old_weight + (1 - old_weight) * boost
```

Design intent: prevent inflated weights from short-term burst usage.
- 1st success within 7 days: boost = 0.15 (full)
- 2nd: boost = 0.075
- 3rd: boost = 0.05
Weight asymptotically approaches 1.0 but never reaches it.

Also: `recent_successes_7d += 1`.
On each cortex file read, if `last_used` is more than 7 days ago, reset `recent_successes_7d = 0`.

### Failure Update

```
new_weight = old_weight * decay_factor
```

| Type | decay_factor | Rationale |
|---|---|---|
| `task_mismatch` | 0.4 | Skill is fundamentally unsuitable — heavy penalty |
| `runtime_error` | 0.6 | Skill has defects |
| `auth_error` | 0.8 | Likely a user configuration issue |
| `dependency_missing` | 0.85 | Environmental issue, not the Skill's fault |
| `api_error` | 0.9 | Likely a transient external failure |

---

## Lesson Type Definitions

The prefrontal cortex accepts only these three structured types:

### dependency_warning
Trigger: The same `dependency_missing` with the same key occurs 2+ times in the same region.
Application: During Phase 3 execution plan, proactively run `which <key>` to check if the dependency exists.

### skill_quality_warning
Trigger: A Skill produces a `task_mismatch` and the Agent determines its description is misleading.
Application: Attach a warning when presenting this Skill as a candidate in Phase 2; lower its recommendation priority.

### env_ready
Trigger: The user has had the required environment variable pre-configured in 2 consecutive uses of a region.
Application: Note in Phase 3 execution plan that "user typically has this variable configured", reducing unnecessary alerts.
Note: Record only the variable name (e.g., TODOIST_API_KEY), never the value.

---

## Reflex Promotion & Demotion

### Promotion Conditions (ALL must be met)
1. `runs.success >= 5`
2. `weight >= 0.90`
3. `side_effects` contains no `write:`, `delete:`, or `shell:` prefix
4. Current `reflex == false`

### Demotion Triggers (ANY one)
- The Skill encounters any type of execution failure
- The Skill's version on ClawHub differs from the stored `version`

On demotion: set `reflex = false`, revert to standard confirmation flow.

### Reflex Safety Boundaries
- Reflex skips only the "execution plan confirmation", never the "installation notification"
- If the user says "cancel" after a reflex notification, abort immediately
- Skills with write operations can never enter reflex, regardless of weight

---

## Pruning Strategy

| Area | Limit | Eviction Rule |
|---|---|---|
| Motor regions | 80 | Evict by oldest `last_used` |
| Motor candidates / region | 5 | Evict by lowest effective_weight |
| Motor candidate | — | Remove if effective_weight < 0.1 |
| Sensory patterns | Follows motor | Remove when linked region is pruned |
| Sensory signals / pattern | 10 | Remove oldest-added |
| Prefrontal lessons | 30 | Evict by lowest confidence |
| Prefrontal lesson | — | Remove if confidence < 0.3 |
| Prefrontal lesson | — | Remove if linked region is pruned |

---

## Design Decision Records

### Why split into SKILL.md and DESIGN.md?
SKILL.md is read in full by the Agent every time it triggers, directly consuming tokens.
DESIGN.md is only consulted when creating or rebuilding the cortex file.
After splitting, SKILL.md stays under ~160 lines / ~6000 chars ≈ 1500 tokens.

### Why semantic matching instead of exact string matching?
Users express the same intent in countless ways. The LLM already has semantic understanding —
letting it judge whether "manage my to-do list" aligns with a signal list of ["manage", "todo", "task"]
is far more robust than exact keyword matching.

### Why limit lessons to three fixed types?
Free-form lessons are authored by the LLM, which may produce contradictory entries across sessions
and be misinterpreted later. Structured types have deterministic semantics and higher reliability.

### Why do signal words require entity filtering?
The cortex file is stored persistently on local disk. If signal words contain personal names ("Alice"),
company names ("Acme Corp"), place names ("NYC office"), specific values ("Q3", "$2M"), or other
identifiable entities, the file becomes a user behavior profile. If a third-party Skill reads,
uploads, or leaks this file, the privacy risk is severe.

Entity filtering rules:
- **Discard**: personal names, company/org names, place names, dates/times, numeric values/amounts, file paths/filenames, URLs, emails, phone numbers, project codenames, and other proper nouns
- **Retain**: verbs (query, convert, deploy), abstract nouns (report, task, image, database), generic tool/service names (todoist, imagemagick — these are Skill-routing keywords, not user privacy)

Examples:
| User Input | ❌ Unfiltered | ✅ Filtered |
|---|---|---|
| Look up Alice's Q3 sales report | Alice, Q3, sales report | query, sales, report |
| Compress /home/alice/photo.jpg | alice, photo.jpg, compress | image, compress |
| Deploy ProjectX to the NYC server | ProjectX, NYC | deploy, server |

Note: Generic tool/service names (todoist, slack, github) are not private entities and should be retained,
as they are critical routing keywords for Skill matching.

### Why use prefix tags for side_effects instead of booleans?
Prefix tags (e.g., `write:api.todoist.com`) carry more information than `has_write_ops: true`,
enabling the execution plan to generate more specific side-effect descriptions.
Reflex promotion checks only need to test for prefix existence — logic stays simple.

### Why replace avg_tokens with skill_md_chars?
The Agent cannot precisely measure token consumption, but it can objectively measure character count
via `wc -c SKILL.md`. Per OpenClaw's documentation (~4 chars/token), conversion is straightforward
and reproducible.

### Why merge instead of overwrite when writing the cortex file?
Concurrent multi-session writes or mid-write interruptions can cause data loss.
Read latest → merge changes → write back ensures other sessions' updates are not overwritten.

### Cached Skills vs. Long-term Skills
- Cached Skills: dynamically fetched by Skill Cortex, tracked in cortex.json, uninstalled by default after use
- Long-term Skills: manually installed by the user or promoted from cache, managed natively by OpenClaw, not tracked in cortex.json
- Skill Cortex never uninstalls long-term Skills and never modifies their configuration
- When a cached Skill is promoted to long-term, its record is removed from the motor section of cortex.json
