---
name: modelshow
description: Double-blind multi-model comparison with automatic de-anonymization and progress polling. Trigger with "mdls" or "modelshow".
metadata: {"openclaw": {"homepage": "https://github.com/schbz/modelshow", "emoji": "🕶️"}}
---

# ModelShow — Blind Multi-Model Comparison

## Purpose

ModelShow runs your prompt through multiple AI models simultaneously, then has an independent judge evaluate the responses without knowing which model wrote which — ensuring unbiased rankings. Results are de-anonymized and presented with model names, scores, and the judge's reasoning.

---

## Detection

Trigger: message starts with `mdls` or `modelshow` (case-insensitive). Strip the keyword to get the prompt.

Examples:
- `mdls what is the best way to learn Rust?`
- `modelshow explain quantum entanglement simply`

---

## Workflow

```
Step 1  → Acknowledge
Step 2  → Load Config
Step 3  → Spawn Model Agents (parallel)
Step 4  → Collect Responses (auto-poll until complete)
Step 5  → Anonymize via judge_pipeline.py
Step 6  → Spawn Judge+Deanon Sub-Agent
          └─ Sub-agent runs judge, then runs judge_pipeline.py finalize
          └─ Sub-agent returns ONLY deanonymized output
Step 7  → Receive + Parse de-anonymized results → BUILD formatted output
Step 8  → Save Results
Step 9  → Present pre-built formatted output (NEVER raw JSON)
```

---

### Step 1: Acknowledge

Send immediately:

```
🔄 ModelShow comparison starting...
Querying models in parallel — results in 30-90 seconds.
```

---

### Step 2: Load Config

Read `{baseDir}/config.json`.

---

### Step 3: Spawn Model Agents

For each model in `config.models`, spawn a sub-agent:
- model: the model alias
- label: `mdls-{model}-{timestamp}`
- runTimeoutSeconds: from `modelTimeouts[model]` or `config.timeoutSeconds`
- task:

```
{config.systemPrompt}

{extracted user prompt}
```

If `parallel: true`, spawn all at once. Agents produce **pure text only** — no tools.

If the user's prompt explicitly requests context (e.g. "using my preferences"), YOU fetch it first and prepend it to the task. External URLs or files: fetch them yourself and include content in the task.

After spawning, note the start timestamp and the set of pending agent labels.

---

### Step 4: Collect Responses (Auto-Polling)

**You must actively poll for sub-agent completion. Do NOT wait passively.**

After spawning all model agents, enter a polling loop:

```
POLL LOOP (repeat until done or timeout):

  1. Check agent statuses using the `subagents` tool (action: "list")
     - Filter for agents matching label prefix "mdls-{model}-{timestamp}"
     - Mark any agent as DONE if its status is "completed" or "failed" or "timeout"

  2. For each DONE agent, collect its response:
     - Status "completed": record response text + duration
     - Status "failed" or "timeout": record as failed, no response text

  3. If ALL spawned agents are now DONE → exit loop immediately

  4. If elapsed_time >= config.timeoutSeconds → exit loop (treat remaining as timed out)

  5. Otherwise: wait 30 seconds, then repeat from step 1
     - Send a status update to the user every 2nd poll cycle:
       "⏳ Waiting for models... {N}/{total} complete so far."
```

**After loop exits:**

- Count successful responses (status = "completed" with non-empty text)
- Count timed-out/failed agents
- If successful < `config.minSuccessful`:
  - Tell the user: "❌ Only {N} models responded (minimum {min} required). Aborting."
  - Stop here.
- If some timed out but >= minSuccessful succeeded: continue, note the timed-out models for later

**Store per-model results:**
```
collected_responses = {
  "model_name": {
    "status": "completed" | "failed" | "timeout",
    "text": "response text or empty string",
    "duration_seconds": 45
  },
  ...
}
```

---

### Step 5: Anonymize

Run:
```bash
echo '<json>' | python3 {baseDir}/judge_pipeline.py
```

With payload:
```json
{
  "action": "anonymize",
  "responses": {
    "model1": "response text 1",
    "model2": "response text 2"
  },
  "label_style": "alphabetic",
  "shuffle": true
}
```

**Only include models with status "completed" and non-empty text.**

Parse output and store:
- `anonymization_map` — `{"Response A": "deepseek", "Response B": "grok", ...}`
- `blind_responses_for_judge` — `{"Response A": "response text", ...}`

**Store `anonymization_map` — you'll pass it to the judge sub-agent in Step 6.**

---

### Step 6: Spawn Judge+Deanon Sub-Agent

You spawn ONE sub-agent whose job is:
1. Evaluate the blind responses
2. Run `judge_pipeline.py finalize` on its own output
3. Return ONLY the de-anonymized results

**The sub-agent task:**

```
You are an impartial judge AND a data processor.

Your task has TWO parts. Complete BOTH before returning anything.

═══════════════════════════════════════════════════════════
PART 1: JUDGE THE RESPONSES
═══════════════════════════════════════════════════════════

You are evaluating responses from multiple AI systems under blind conditions.
The responses are labeled Response A, Response B, etc. You do not know which
AI system produced which response. Use ONLY these labels throughout your evaluation.

**Original Prompt:** {extracted_prompt}

**Responses to evaluate:**
{for each placeholder, text in blind_responses_for_judge.items():}
### {placeholder}
{text}

{end for}

**Evaluation criteria:** accuracy, clarity, completeness, usefulness

**Required output format for Part 1:**

### Rankings

1st: {placeholder} — Score: X/10
Brief justification (2-3 sentences).

2nd: {placeholder} — Score: X/10
Brief justification (2-3 sentences).

[continue for all responses]

### Overall Summary
[Key differences and winner's strengths, using only placeholder labels]

═══════════════════════════════════════════════════════════
PART 2: DE-ANONYMIZE YOUR OWN OUTPUT
═══════════════════════════════════════════════════════════

After writing your judge evaluation above, you MUST run this command
using the `exec` tool. Do NOT skip this step. Do NOT return Part 1 output
to the requester. Return ONLY the result of this command.

Run exactly this command (fill in the JSON values):

```bash
python3 {baseDir}/judge_pipeline.py <<'ENDJSON'
{
  "action": "finalize",
  "judge_output": "<YOUR COMPLETE PART 1 OUTPUT — paste it here verbatim>",
  "anonymization_map": {anonymization_map_json}
}
ENDJSON
```

The command will output JSON. Return that JSON verbatim as your ENTIRE response.
Your response must be ONLY the JSON output of that command. Nothing else.
No preamble, no explanation, no Part 1 text — just the raw JSON.

If the command fails, return: {"error": "pipeline_failed", "raw_judge_output": "<part1>"}
```

**Sub-agent spawn parameters:**
- model: `config.judgeModel`
- label: `mdls-judge-{timestamp}`
- runTimeoutSeconds: `config.timeoutSeconds`
- The sub-agent HAS access to exec tools (it needs to run judge_pipeline.py)

**After spawning the judge sub-agent, poll for its completion the same way as Step 4:**
- Check every 30 seconds using `subagents list`
- Send "⚖️ Judge deliberating..." status after the first 30s check
- Timeout after `config.timeoutSeconds` seconds

---

### Step 7: Receive, Parse, and Format Results

**This step builds the complete formatted output. Step 9 only sends it.**

**7a. Get the judge sub-agent's response**

The sub-agent returns a string. That string should be pure JSON. Parse it.

**7b. Handle parse errors**

If the string is not valid JSON, or contains `"error"` key:
- Check if `raw_judge_output` is available in the error object
- If yes, run the fallback finalize command yourself:
  ```bash
  python3 {baseDir}/judge_pipeline.py <<'ENDJSON'
  {
    "action": "finalize",
    "judge_output": "<raw_judge_output value>",
    "anonymization_map": {your stored anonymization_map}
  }
  ENDJSON
  ```
- Parse that output instead
- If that also fails: set `fallback_mode = true` (will present unranked results)

**7c. Extract fields from parsed JSON**

```
parsed = JSON.parse(judge_response)

deanonymized_judge_output   = parsed["deanonymized_judge_output"]   # string
ranked_models_deanonymized  = parsed["ranked_models_deanonymized"]  # array of objects
deanonymization_complete    = parsed["deanonymization_complete"]    # boolean
```

Each item in `ranked_models_deanonymized` looks like:
```json
{"rank": 1, "model": "grok", "score": 9.2, "placeholder": "Response A"}
```

**7d. Verify de-anonymization worked**

Check that `ranked_models_deanonymized` contains REAL model names, not "Response A/B/C":
- If any `model` field matches pattern `Response [A-Z]` → de-anonymization incomplete
- Run fallback finalize exec (same as 7b fallback above)
- If still unresolved → set `fallback_mode = true`

**7e. ⚠️ BUILD THE FORMATTED OUTPUT NOW — store in variable `formatted_output`**

Do NOT proceed to Step 8/9 without building this variable.

Sort `ranked_models_deanonymized` by `rank` ascending (rank 1 = best).

Build the formatted output string:

```
MEDAL MAP: rank 1 → 🏆 | rank 2 → 🥈 | rank 3 → 🥉 | rank 4+ → (no medal)

formatted_output = "🕶️ **Blind Judging Results:**\n\n"

FOR EACH item in ranked_models_deanonymized (sorted by rank):

  medal = MEDAL MAP[item.rank] or ""
  header = "{medal} **{item.model}** (Score: {item.score}/10)"

  response_text = collected_responses[item.model]["text"]
    (from your Step 4 data — the FULL model response text)

  judge_assessment = EXTRACT from deanonymized_judge_output:
    Find the section mentioning item.model (look for **{item.model}**) and grab
    the justification sentences that follow, until the next model section starts.
    If extraction is uncertain, include the full deanonymized_judge_output at the end instead.

  formatted_output += header + "\n\n"
  formatted_output += response_text + "\n\n"
  formatted_output += "**Judge's assessment:** " + judge_assessment + "\n\n"
  formatted_output += "---\n\n"

END FOR

formatted_output += "🕶️ *Blind judging was active — the judge evaluated anonymized responses without knowing which model produced each.*\n\n"
formatted_output += "📊 Full judge analysis available — reply \"show analysis\" to see it.\n"
formatted_output += "📄 Results saved to: `{filepath}`\n"

IF any models timed out:
  formatted_output += "\n⏱️ Timed out (excluded): {list of timed-out model names}\n"
```

**STOP AND VERIFY before continuing:**
- [ ] `formatted_output` is a populated string (not empty, not JSON)
- [ ] It contains medal emojis (🏆, 🥈, 🥉) where applicable
- [ ] It contains actual model names (not "Response A")
- [ ] It contains response text from Step 4
- [ ] It ends with the file path line

---

### Step 8: Save Results

Save to `{config.outputDir}/{slug}-{YYYY-MM-DD-HHMM}.md`.

Slug = first 5 words of prompt, lowercased, hyphenated.

```markdown
# ModelShow Results
**Date:** {timestamp}
**Prompt:** {prompt}
**Models:** {model names}
**Judge:** {judge model}
**Judging Mode:** Blind (model identities hidden from judge)

---

## Rankings

{for each item in ranked_models_deanonymized (sorted by rank):}
### {medal} **{item.model}** — {item.score}/10
{judge notes for this model from deanonymized_judge_output}
{full response text}
{end for}

---

## Judge's Full Analysis
{deanonymized_judge_output}

---

## Blind Judging Key (Audit)
{for placeholder, model in anonymization_map.items():}
- {placeholder} → {model}
{end for}

---

## Metadata
- Total duration, models queried, successful/failed counts
```

Update `filepath` in `formatted_output` with the actual saved path.

---

### Step 9: Present Results

**Send `formatted_output` to the user. That's it.**

`formatted_output` was built in Step 7e. It is a formatted string with medal emojis,
model names, response text, and judge assessments.

**⛔ DO NOT send the raw JSON from the judge sub-agent.**
**⛔ DO NOT send the `parsed` dict or any JSON object.**
**⛔ DO NOT send `deanonymized_judge_output` as a bare string.**
**✅ ONLY send `formatted_output`.**

If the user later replies "show analysis" or "full analysis", send `deanonymized_judge_output`.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| < minSuccessful models respond | Tell user, abort |
| judge sub-agent returns error | Run fallback finalize exec, then format and present |
| deanonymization_complete = false | Run fallback finalize exec |
| model names still show as "Response X" after fallback | Present unranked with warning |
| file save fails | Present results, note save failure |
| all models fail | Report error with details |

---

## Architecture

```
Orchestrator
    │
    ├── spawns model agents → polls every 30s until all done → collects responses
    │
    ├── exec: judge_pipeline.py anonymize → gets anonymization_map + blind_responses
    │
    └── spawns judge+deanon sub-agent → polls every 30s until done
            │
            ├── evaluates blind responses (internal)
            │
            └── exec: judge_pipeline.py finalize → returns de-anonymized JSON
                        │
                        └── Orchestrator receives JSON → PARSES it → FORMATS it → SENDS formatted_output
                            (never raw JSON to user)
```
