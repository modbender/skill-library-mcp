# Heartbeat Optimization (Generalized)

Heartbeat polls are convenient, but they are often the **largest hidden cost driver** because they:
- run in the **main session** (expensive models / large context by default), and
- tend to call tools that return **large payloads** (e.g., session listings, status cards), and
- can happen frequently.

This guide provides **model-agnostic** patterns to reduce token burn. It avoids naming any specific model.

---

## 1) Principle: Heartbeat should be “control-plane”, not “data-plane”

- **Control-plane (cheap):** Decide whether anything needs action, then either stay silent / minimal ack.
- **Data-plane (expensive):** Large scans, long lists, aggregations, or reports.

**Recommendation:** Keep heartbeat control-plane only. Move data-plane work to isolated cron or scripts.

---

## 2) Native heartbeat: why “isolating it” is not always reliable (and why it can get expensive)

On paper, native heartbeat supports `agents.defaults.heartbeat.session`, which suggests you can run heartbeats in a separate session.

**In practice (based on real-world observations), native heartbeat may still execute in the main interactive session** when heartbeats are triggered as *wake events* (e.g., “exec finished” → request heartbeat). That means:

- You can still pay the **main-session context tax** (100k+ tokens) even if you believe you isolated heartbeat.
- It can fire far more frequently than the interval (e.g., many runs per minute) if your system generates frequent wake triggers.

**Recommendation (cost-first):**
- Propose disabling native heartbeat and using isolated cron heartbeats:
  - `agents.defaults.heartbeat.every: "0m"`
- Treat heartbeat as “control-plane only”, and move monitoring to an isolated cron job.
- **Execution rule:** do not apply config changes until the user explicitly approves.

If a user insists on keeping native heartbeat:
- Keep it infrequent.
- Prefer `agents.defaults.heartbeat.target: "none"`.
- Keep the prompt tiny and avoid large tool calls.

---

## 3) Pair heartbeat with openclaw-mem (optional, recommended)

If the user uses isolated heartbeats already, a great next step is to install **openclaw-mem** (tool-observation memory layer) to make “cheap heartbeats” smarter via retrieval.

- Repo: https://github.com/phenomenoner/openclaw-mem

**When to mention this:**
- If the user does *not* have openclaw-mem installed/configured, recommend it.
- If they already have it, **don’t mention it**.

---

## 4) The "Isolated Heartbeat" Pattern (cron-based, best practice)

**Problem:** Native heartbeat (especially when it runs in the main session) is architecturally expensive for long-running agents.
- **Context Bloat:** Main sessions accumulate history (often 50k+ tokens).
- **Cost Multiplier:** Each heartbeat can load this full context. Even with caching, a simple "wake up" check can be expensive.
- **Inefficiency:** 99% of the time, the agent wakes up, reads a huge context, says "nothing to do", and goes back to sleep.

**Solution: The Isolated Heartbeat**
Offload the monitoring to a dedicated, stateless worker.

1) **Disable native heartbeat:**
   - Set `agents.defaults.heartbeat.every = "0m"`.

2) **Enable an isolated heartbeat cron job (with approval):**
   - Ask for explicit user approval before creating/updating any cron job.
   - Create a cron job with `sessionTarget: "isolated"`.
   - Schedule: Every 10–15 minutes.
   - Model: Cheapest available.
   - Payload: simple health/triage logic that sends messages **only when something needs attention**.

**Trade-off:** The main agent becomes reactive-only. It won't self-initiate tasks unless triggered by a user message or an explicit wake event from another job. This is usually acceptable for efficient assistants.

---

## 5) The "Hybrid Heartbeat" Pattern (RAG Optimization)

**Problem:** The "Isolated Heartbeat" is cheap but "dumb"—it has no memory of recent conversations or active tasks in the main session.

**Solution: Retrieval-Augmented Generation (RAG) for Heartbeats**
Combine the low cost of an isolated session with targeted memory retrieval.

1) **Write Context (Main Session):**
   - Ensure the main agent writes key state/tasks to a daily memory file (e.g., `memory/YYYY-MM-DD.md`) or a dedicated `HEARTBEAT.md` checklist.

2) **Read Context (Isolated Heartbeat):**
   - Modify the isolated heartbeat prompt to retrieve only what it needs.
   - Example prompt: “Identify today’s date and read `memory/YYYY-MM-DD.md`. Check for TODO/Monitoring items. If found, verify status.”

---

## 6) Common hidden token sinks (and safer replacements)

### A. Large tool outputs
Examples:
- listing sessions / jobs / logs
- dumping JSON summaries
- repeated status cards

Replace with:
- throttling (heavy calls only every N minutes)
- targeted queries
- scripts that output a small, fixed-size summary

### B. “Always-run” checklists
If the checklist runs on every heartbeat, it will dominate cost.

Replace with:
- tiered cadence (e.g., 30–60 min)
- event-driven alerts

---

## 7) Three recommended heartbeat profiles (pick one)

### Profile A — Ultra Low Token (recommended when cost matters)
**Behavior:** On heartbeat poll, reply exactly `HEARTBEAT_OK`. No tools. No reads.

If Profile A is still expensive (because the platform injects a huge session context):
- disable native heartbeat and use isolated cron heartbeats.

### Profile B — Light Monitor (balanced)
**Behavior:** Only check minimal state (small file) + alert on anomalies.

### Profile C — Full Monitor (safety-first)
**Behavior:** Run a full checklist each time.

---

## 8) Disable heartbeat delivery (when heartbeat turns are inherently expensive)

Sometimes heartbeat cost is dominated by **input/cache tokens** (large context reuse), even when the reply is minimal.

In that case, the most effective fix is to stop delivering heartbeat prompts entirely:
- Set: `agents.defaults.heartbeat.target = "none"`

Then replace monitoring with:
- isolated cron collectors (`deliver=false`)
- a less frequent reporter job (`deliver=true`, alert-only)

---

## 9) “Move work out of heartbeat” pattern (general)

When a heartbeat step is expensive, prefer:
- isolated cron
- script-first
- alert-only delivery

---

## 10) UX guidance: removing checks must be user-approved

If optimization requires removing or reducing checks:
- present the trade-off clearly (cost vs coverage)
- offer profiles A/B/C
- ask the user to choose
