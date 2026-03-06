---
name: simple-random-interaction-designer
description: Decide whether OpenClaw should send a spontaneous casual message during periodic checks, and when it should, choose a natural interaction type plus concise guidance for how to deliver it. Use when scheduling or executing human-like proactive chat check-ins.
metadata: {"homepage":"https://docs.openclaw.ai/tools/skills","env":[],"network":"optional","version":"2.0.0","notes":"Uses local randomness to return only a final yes/no decision and, on yes, an interaction type plus interaction description for natural outreach, including grounded OpenClaw-accessible real-world context when relevant"}
---

# Simple Random Interaction Designer

Use this skill to decide whether to send a casual proactive message and, when the answer is yes, what kind of interaction to deliver.
Use `{baseDir}/scripts/random_interaction_designer.py` as the default execution path.

## Workflow
1. Run the script once per scheduled check interval.
2. Read `decision` from the JSON output.
3. Stop immediately if `decision` is `no`.
4. If `decision` is `yes`, use both `interaction_type` and `interaction_description` to draft the outgoing message.
5. If the selected interaction is data-aware, use any relevant OpenClaw-accessible tools, skills, or integrations to fetch live context before drafting the message.
6. Keep the final message brief, casual, and easy to ignore without social pressure.
7. Prefer recent chat context when it is clearly present.
8. Do not mention the random process, scheduled checks, or why this interaction was selected.

## Primary Tooling
- Script path: `{baseDir}/scripts/random_interaction_designer.py`
- Runtime: Python 3, standard library only.

Preferred command:
- `python3 {baseDir}/scripts/random_interaction_designer.py`

## Output Contract
When the result is no:

```json
{"decision":"no"}
```

When the result is yes:

```json
{
  "decision": "yes",
  "interaction_type": "Playful opener",
  "interaction_description": "Send a brief playful line that feels spontaneous and easy to ignore."
}
```

Contract rules:
- `decision` is always present and is either `yes` or `no`.
- `interaction_type` is present only when `decision` is `yes`.
- `interaction_description` is present only when `decision` is `yes`.
- Do not expect debug fields, probability values, roll values, or fallback metadata.

## Interaction Design Rules
- Treat the JSON as execution guidance, not user-facing text.
- Keep the final message to one or two short chat lines.
- Prefer soft phrasing over transactional or assistant-like framing.
- Avoid defaulting to "just checking in" language.
- Ask at most one question in a single ping.
- Do not fabricate recent context, external facts, or account-backed data.
- For data-aware categories, prefer real-world grounding when OpenClaw can actually access the relevant source.
- Use smart-home, weather, calendar, traffic, news, or market context only when the information is reliable, fresh, and genuinely relevant to the user.
- If `interaction_type` depends on context or fresh data and that support is unavailable, rerun once to try for a non-data interaction; if rerunning is not practical, keep the message general and low-pressure instead of pretending specificity.
- Vary tone and wording from recent interactions when possible so the behavior feels casual rather than patterned.

## Interaction Catalog
Use the selected `interaction_type` and follow the matching guidance from `interaction_description`.

1. `Playful opener`
   Start with a short playful line that feels light and spontaneous.
2. `Curious check-in`
   Ask one low-stakes question that is easy to answer or ignore.
3. `Light shared observation`
   Make a casual observation that feels conversational rather than task-driven.
4. `Tiny celebration`
   Briefly acknowledge a small win or effort when the chat supports it.
5. `Smart device status`
   If OpenClaw can access relevant device state, share one useful smart-device status or gentle suggestion naturally.
6. `Weather-aware check-in`
   Use current weather only when fresh reliable data is available and clearly relevant.
7. `Calendar-aware nudge`
   Turn calendar context into a soft human-sounding reminder or prompt, not an alert.
8. `Context-aware follow-up`
   Build on a recent chat detail only when it is clearly present in the current conversation.
9. `Practical nudge`
   Offer one concise optional nudge that may help the user.
10. `Optional real-world update`
   Share one brief real-world update such as traffic, news, or market context only when reliable relevant data is already available.

## Error Handling
- If execution fails, surface the Python error message and rerun.
- If output is not valid JSON, treat it as a hard failure and rerun.
- If `decision` is missing or is not `yes` or `no`, rerun and discard the invalid result.
- If `decision` is `yes` and either `interaction_type` or `interaction_description` is missing, rerun and discard the invalid result.

## Minimal Examples

```bash
python3 {baseDir}/scripts/random_interaction_designer.py
python3 {baseDir}/scripts/random_interaction_designer.py --seed 42
```

```powershell
python3 "{baseDir}/scripts/random_interaction_designer.py"
python3 "{baseDir}/scripts/random_interaction_designer.py" --seed 42
```
