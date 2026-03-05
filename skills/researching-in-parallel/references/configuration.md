# Configuration Reference

## Required capabilities

`sessions_spawn` is the only hard requirement and works with default OpenClaw config.

The following are strongly recommended — without them, sub-agents cannot retrieve
full-text sources and will be limited to search snippets, which significantly reduces
research depth:

- **web_fetch** — retrieves full page text for open web pages and open-access documents.
  Available in most OpenClaw configurations by default.
- **PDF tool** — extracts full text from PDF files. Academic papers, government reports,
  white papers, and systematic reviews are very commonly PDFs. Without this, the evidence
  pass in particular will be substantially weaker.
- **Browser tool** — loads JavaScript-rendered pages, handles soft paywalls and cookie
  walls, and acts as fallback when web_fetch returns thin content. Most important for
  institutional and journal sites.

These capabilities are not unusual requirements — a research agent that cannot read
documents and handle PDFs is working with one hand tied behind its back. If any of
these are unavailable in your OpenClaw setup, note it in AUTHORS.md and treat the
methodology section's access status breakdown as your indicator of impact.



## Model selection for sub-agents

There are three layers, in descending priority:

1. **`sessions_spawn` `model:` param** — set per spawn call at runtime; wins over everything. This is how the skill controls model selection, reading values from `skill-config.json`.
2. **`agents.defaults.subagents.model`** in `openclaw.json` — system-wide default for all sub-agents when `sessions_spawn` doesn't specify one.
3. **Caller inheritance** — if neither of the above is set, the sub-agent runs on the same model as the main agent.

**What `agents.defaults.subagents.model` actually does:** it sets a *default*, not an allowlist. Setting it to a cheap model does not prevent `sessions_spawn` from overriding to a different model — the `sessions_spawn.model` param always wins.

**What controls the allowlist** is a different key: `agents.defaults.models`. If this is set, only models listed there can be used anywhere in the system (including via `sessions_spawn`). If `sessions_spawn` passes a model not in that allowlist, OpenClaw silently falls back to the default and logs a warning — it does not error. This means a skill-config.json entry for a model the user hasn't provisioned will degrade gracefully rather than break.

**Recommended `openclaw.json` setup for this skill:**

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "archiveAfterMinutes": 180
      }
    }
  }
}
```

Leave `agents.defaults.subagents.model` unset and let `skill-config.json` drive model selection via `sessions_spawn`. This keeps openclaw.json clean and puts model choices where they belong — in the skill itself.

If you want to constrain which models the skill (or anything else) can use, add them to `agents.defaults.models`:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-haiku-4-5-20251001": { "alias": "Haiku" },
        "anthropic/claude-sonnet-4-6":         { "alias": "Sonnet" },
        "anthropic/claude-opus-4-6":            { "alias": "Opus" }
      }
    }
  }
}
```



## Model vintage warning

**Model vintage — not just tier — affects research quality.** An older model on a
research pass produces thinner, less current source coverage that synthesis cannot
compensate for. On serious runs, use frontier or near-frontier models for all four
roles. An older cheap model on the breadth pass will produce a weaker foundation
for the entire pipeline regardless of synthesis model quality.

As a rough guide: models released more than 12 months before your run date are
likely to show knowledge gaps on fast-moving topics. Check model cards for knowledge
cutoff dates and factor this into role assignment.

**Synthesis model must be set explicitly.** Do not leave `subagents.synthesis` as
null for important runs. If the main agent is subject to rate limit pressure and
fails over to a less capable model, a null synthesis inherits that degraded state.
Set it to a strong, explicit model string.



## Rate limit mitigation

Running three sub-agents in parallel against the same provider simultaneously
competes for rate limit pools and has caused failures in testing. Distribute
sub-agents across providers:

- Recommended pattern: breadth on Anthropic, critical and evidence on different
  Google Gemini model generations
- This is not just a performance optimisation — it is a failure avoidance strategy
- If you must use a single provider, consider running the three research passes
  sequentially (see Degraded operation below) — this loses parallelism but avoids
  rate limit collisions

**Sequential fallback order if rate limits are hit:**
1. breadth pass
2. critical pass
3. evidence pass
4. synthesis

If a sub-agent fails mid-run due to rate limits, retrieve whatever output it did
produce before retrying. Partial outputs may be usable as provided sources for a
targeted retry.



## Cost profile

| Step | Token load | Notes |
|---|---|---|
| 3× research sub-agents | Medium–high per agent | Parallel — wall-clock ~max(three), not sum. Full-text retrieval increases token usage vs. snippet-only. |
| 1× synthesis sub-agent | High | Reads three workspace files in full; token-heaviest step |
| Main agent orchestration | Low | Spawns sub-agents, retrieves, announces, coordinates — minimal LLM calls |
| Total per run | ~4–8× a standard research query | Varies with topic breadth and full-text retrieval success |

To reduce cost:
- Set cheaper models for research sub-agents in `skill-config.json`; use a stronger model for synthesis only
- Use *Brief* output length for exploratory research; *Comprehensive* only when depth is needed
- `runTimeoutSeconds: 480` is set to allow for full-text retrieval — reduce to 360 if browser/PDF tools are unavailable



## Degraded operation

If `sessions_spawn` is unavailable or denied:
1. Run the three research passes sequentially using the `llm_task` tool or direct web search in the main agent session
2. Save each pass output to the workspace as a file
3. Synthesise from those files

This loses parallelism but preserves triangulation. Output quality is similar; wall-clock time is roughly 3× longer.



## Sub-agent system prompt (promptMode)

Sub-agents automatically run with `promptMode: minimal` — this is set by the OpenClaw runtime and is not user-configurable. Under `minimal`, Skills, Memory Recall, User Identity, Heartbeats, and several other context blocks are stripped out. Sub-agents only receive `AGENTS.md` and `TOOLS.md` from your bootstrap files; `SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, and `MEMORY.md` are filtered out.

There is a leaner `promptMode: none` (returns only a base identity line) but the runtime assigns prompt modes — you cannot request it.

**Practical implication:** the main overhead in each sub-agent's starting context comes from `AGENTS.md` and `TOOLS.md`. If you want to reduce per-sub-agent token cost, keep those files concise. Run `/context` in your main session to see the injected sizes of each bootstrap file and check whether any truncation is occurring.



## Sub-agent model discovery

Each sub-agent is instructed to write its model ID on the first line of its output.
The synthesis agent reads this line from each research file and copies it into the
report's About This Report block. This is best-effort — some models may not accurately
report their own version string, and OpenRouter routing can make the actual model
ambiguous. The model ID in the output is better understood as "the model this agent
was configured to use" rather than a verified self-report.

The main agent can call `session_status` to confirm its own model ID if needed.
