---
name: parliament
description: Multi-model collaboration skill. Spawns parallel sub-agents using different LLM models to review, analyze, or debate a given task. Collects and synthesizes outputs into a unified report. Use when you need diverse model perspectives on code review, document analysis, decision-making, or any task that benefits from multi-model consensus.
---

# Parliament — Multi-Model Collaboration

Spawn parallel sub-agents across different LLM models, collect their outputs, and synthesize a unified report. Like a parliament where each model is a delegate with its own perspective.

## When to Use

- Code review from multiple model perspectives
- Document/paper review with diverse viewpoints
- Decision-making that benefits from consensus
- Quality assurance through model disagreement detection
- Any task where "second opinions" from different models add value

## Inputs

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| task | yes | — | The review prompt or question |
| content | yes | — | File path or inline text to review |
| models | no | all 4 | Comma-separated model aliases |
| timeout | no | 120s | Max seconds per delegate |
| mode | no | review | `review`, `debate`, or `quick` |

## Available Models

| Alias | Full Model ID | Emoji | Strengths |
|-------|--------------|-------|-----------|
| `opus46` | `anthropic/claude-opus-4-6` | 🟣 | Deep reasoning, nuanced analysis |
| `gpt53` | `openai/gpt-5.3-codex` | 🟢 | Code analysis, structured output |
| `gemini` | `google/gemini-3.1-pro-preview` | 🔵 | Broad reasoning, multimodal |
| `glm5` | `glm/claude-opus-4-6` | 🟡 | GLM-5 via MMKG routing |

⚠️ Model availability depends on configured API keys. Parliament gracefully handles unavailable models (see Error Handling).

⚠️ GLM-5 model ID is `glm/claude-opus-4-6` — the `glm/` prefix routes through MMKG, NOT Anthropic direct.

Default parliament: all 4 models. Quick mode: opus46 + one other.

## Execution Protocol

When the user asks for a parliament review, follow these steps exactly:

### Step 1: Prepare the Delegate Prompt

Read the file (if a path is given), then construct the delegate prompt:

```
You are one delegate in a multi-model parliament review. Other models are reviewing the same content independently.

Your role: Give your honest, thorough, independent analysis. Do not hedge or be diplomatic — be direct.

Task: {user's prompt}

Content to review:
{file content or inline content}

Structure your response as:
1. **Key Observations** — what stands out immediately
2. **Issues Found** — bugs, risks, gaps, errors (with severity: high/medium/low)
3. **Strengths** — what's done well
4. **Recommendations** — specific, actionable improvements
5. **Confidence** — your overall confidence level (high/medium/low) with reasoning
```

### Step 2: Spawn All Delegates in Parallel

Use `sessions_spawn` for each model. Spawn ALL at once (do not wait sequentially):

```
sessions_spawn(
  task=<delegate prompt>,
  model="anthropic/claude-opus-4-6",
  label="parliament-opus46",
  mode="run",
  runTimeoutSeconds=120
)
```

Labels: `parliament-opus46`, `parliament-gpt53`, `parliament-gemini`, `parliament-glm5`.

### Step 3: Collect Results

Sub-agents auto-announce when done. As each result arrives, note it. Proceed to synthesis when:
- All delegates have returned, OR
- Timeout reached and at least 2 delegates responded

### Step 4: Synthesize (Host Agent Does This)

The host agent (you) produces the final Parliament Report by comparing all delegate outputs:

**How to identify consensus:** Points raised by 3+ delegates with similar conclusions.

**How to identify divergence:** Points where delegates reach different conclusions or assign different severity.

**How to identify unique insights:** Points raised by only 1 delegate that others missed.

**How to derive recommendation:** Weight by consensus strength. If 3/4 agree, follow the majority. If split 2/2, present both positions and recommend the more conservative option.

### Step 5: Deliver Report

Output the report in this format:

```markdown
# 🏛️ Parliament Report

**Task:** {summary}
**Models:** {list of models that responded}
**Date:** {timestamp}
**Quorum:** {N}/{total} delegates responded

---

## Delegate Responses

### 🟣 Opus 4.6
{response}

### 🟢 GPT-5.3 Codex
{response}

### 🔵 Gemini 3.1 Pro
{response}

### 🟡 GLM-5
{response}

---

## Synthesis

### ✅ Consensus (3+ delegates agree)
- {point 1}
- {point 2}

### ⚠️ Divergence (delegates disagree)
- {topic}: {model A} says X, {model B} says Y
- Recommendation: {which position and why}

### 💡 Unique Insights (only one delegate caught this)
- {model}: {insight}

### 📊 Confidence Matrix

| Model | Confidence | Top Concern |
|-------|-----------|-------------|
| Opus 4.6 | high/med/low | ... |
| GPT-5.3 | high/med/low | ... |
| Gemini | high/med/low | ... |
| GLM-5 | high/med/low | ... |

### 📋 Final Recommendation
{synthesized recommendation based on weighted consensus}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Model API key not configured | Skip model, note in report as "❌ unavailable (no API key)" |
| Model times out | Note as "⏱️ timed out", proceed with available results |
| Model returns error | Note error, proceed with available results |
| Only 1 delegate responds | Deliver single response with note: "⚠️ Insufficient quorum for synthesis" |
| 0 delegates respond | Report failure, suggest checking API keys with `/status` |

Minimum quorum for synthesis: 2 delegates.

## Modes

### Review Mode (default)
Independent analysis from each model. Best for code review, document review, architecture decisions.

### Quick Mode
Only 2 models (opus46 + gemini). Faster, still catches most issues. Use when time matters more than breadth.

### Debate Mode
Frame the task as a debate: "Take a strong position and argue for it."
Synthesis highlights strongest arguments from each side. Best for decision-making with tradeoffs.

## Permissions

- `sessions_spawn` — spawn sub-agent sessions with different models
- `read` — read files for review (when file paths provided)
- `write` — save the parliament report (optional)

## Tips

- Parliament works best with specific, concrete tasks (not vague "review everything")
- For large files (>500 lines), split into sections and run parliament on each
- Pay special attention to divergence points — that's where the real value is
- If one model consistently disagrees, investigate why — it may have caught something others missed
- Check model availability first (`/status`) if you're unsure which API keys are configured
