# Council Protocol Details

## Prompt Template

Each panelist receives:

```
You are an expert panelist in a multi-model deliberation council.
Your assigned perspective: {lens_description}

QUESTION:
{question}

INSTRUCTIONS:
- Analyze from your assigned perspective. Be independent — do not guess
  what others might say or seek a safe middle ground.
- Structure: (1) Key observations, (2) Your position, (3) Risks/caveats,
  (4) Confidence (high/medium/low) WITH reasoning.
- Be substantive and specific. No filler.
- If the question involves a decision, state your recommendation clearly.
- If actionable, suggest 1-3 concrete next steps with effort/time estimates.
- Max 800 words.
- {language_instruction}
```

**Language:** Detect the question language and hardcode it explicitly in the prompt (e.g. `"Respond strictly in Russian"`, `"Respond strictly in English"`). Never use vague instructions like "respond in the same language."

## Debate Round (--rounds 2)

1. After Phase 1, summarize all positions into an anonymized digest (Panelist A/B/C — no model names, to reduce anchoring bias)
2. Spawn new round with digest + prompt: "Considering these perspectives, revise your position, rebut, or strengthen. Be specific about what changed and why. Max 400 words."
3. Collect on next user follow-up
4. Synthesize with both rounds, noting any shifted positions

Cost: doubles API calls. Use for high-stakes questions only.

## Synthesis Rules

- Randomize position order (don't always lead with the same model)
- Quote specific panelist arguments with attribution
- Never fabricate consensus — if they genuinely disagree, say so
- Check: did minority opinions get fair representation?
- If all panelists agree: note this may reflect shared training data bias, not ground truth
- Match the language of the user's question in the synthesis output

**⚠️ Dual-role bias:** If the orchestrator model also participates as a panelist, it may unconsciously favor its own response. Mitigate by randomizing order and quoting specific arguments rather than summarizing loosely.

## Error Handling

- **Panelist fails/times out:** note in output, synthesize from available responses
- **Below min responses (< 2):** abort with error — need minimum 2 for meaningful deliberation
- **Panelist ignores structure:** extract what possible, note format deviation
- **Synthesis fails:** report raw panelist responses so user has something

## Spawn Example

```
sessions_spawn(
  mode: "run",
  model: "<model from panel.json>",
  label: "council-<slot>",
  task: <prompt with lens and language>,
  runTimeoutSeconds: 120
)
```

All spawns are independent — fire them all at once.

## Collect Flow

1. `subagents list` — check all panelists status
2. If all done: `sessions_history` for each session key, extract responses
3. If quorum met but some still running: synthesize from available, note missing panelists in output
4. If below quorum: tell user to wait or abort
