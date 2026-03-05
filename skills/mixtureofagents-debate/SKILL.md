---
name: moa-debate
description: Run an Oxford Union–style multi-agent debate on any motion using Mixture of Agents architecture
---

# Oxford Union Multi-Agent Debate

When the user wants to **debate a motion**, **stress-test an argument**, **prepare for a formal debate**, or asks you to run an **Oxford Union–style debate**, follow this procedure.

## Overview

You will simulate a full Oxford Union formal debate by making sequential LLM calls playing different roles. Three agents debate iteratively:

| Agent | Role | Temperature | Behaviour |
|-------|------|-------------|-----------|
| **Proposition** | Steelmans the case FOR | 0.3 | Rigorous, principled, evidence-based |
| **Opposition** | Steelmans the case AGAINST | 0.3 | Rigorous, principled, evidence-based |
| **Devil's Advocate** | Attacks whichever side is dominant | 0.7 | Lateral, unexpected, adversarial |

Plus a neutral **Chair** (temp 0.4) and a **Completeness Judge** (temp 0.2).

## Step 1 — Accept the Motion

Ask the user for a motion, or if they've already provided one, confirm it. Motions follow the "This House..." format. If the user provides a topic rather than a formal motion, rewrite it as "This House Believes That..." or similar.

**Suggested example motions** (if the user needs inspiration):
- "This House Believes That Artificial Intelligence Will Be Humanity's Last Great Invention"
- "This House Will Under No Circumstances Fight for Its King and Its Country"
- "This House Has No Confidence in His Majesty's Government"

Ask for optional parameters:
- **Min Score to Pass** (default 7.5, range 5–10) — completeness threshold for early stop
- **Hard Round Cap** (default 5, range 3–8) — maximum debate rounds

## Step 2 — Run the Debate Rounds

For each round (starting at round 1), execute the following sequence. Present each step to the user as it completes.

### 2a. Proposition Speech

Use this system prompt:
> You are a skilled Oxford Union debater arguing FOR the proposition. Build the strongest philosophical, empirical, and practical case in favour. Be precise, structured, and rhetorically persuasive. Stay in character — do not use conversational filler, AI preambles, or apologies.

**Round 1 user message:**
> Motion: "[MOTION]"
>
> Identify the single strongest principled argument FOR this motion. Build evidence around it and pre-empt the most obvious counterargument. Open with a memorable line.
>
> Deliver your opening speech. Max 150 words.

**Round 2+ user message:**
> Motion: "[MOTION]"
>
> Round summary so far:
> [PREVIOUS_SUMMARY]
>
> Identify the single strongest principled argument FOR this motion. Build evidence around it and pre-empt the most obvious counterargument. Open with a memorable line.
>
> Develop your case further. Max 150 words.

Present the speech to the user labelled **"🔵 Proposition"**.

### 2b. Point of Information (Opposition → Proposition)

Generate a POI from the Opposition:
> Motion: "[MOTION]"
>
> Proposition just said:
> "[PRO_SPEECH]"
>
> You are the Opposition. Devise a sharp Point of Information (POI) — a single probing question of ≤15 words that targets the weakest claim in their speech. Return ONLY the question.

**Accept/decline**: Randomly decide (60% accept, 40% decline). If accepted, generate a response:
> You are speaking for the Proposition. The Opposition has raised this Point of Information:
> "[POI_QUESTION]"
>
> You chose to accept it. Respond confidently in ≤25 words.

Present the POI and outcome (accepted/declined) to the user.

### 2c. Opposition Speech

Use this system prompt:
> You are a skilled Oxford Union debater arguing AGAINST the proposition. Build the strongest philosophical, empirical, and practical case against. Be precise, structured, and rhetorically persuasive. Stay in character — do not use conversational filler, AI preambles, or apologies.

**Round 1 user message:**
> Motion: "[MOTION]"
>
> Proposition has argued:
> "[PRO_SPEECH]"
>
> Identify the single strongest principled argument AGAINST this motion. Build evidence around it and pre-empt the most obvious counterargument. Open with a memorable line.
>
> Deliver your opening speech. Max 150 words.

**Round 2+** — include the previous summary and ask to develop the case further.

Present the speech to the user labelled **"🔴 Opposition"**.

### 2d. Point of Information (Proposition → Opposition)

Same as 2b but reversed: Proposition poses the POI, Opposition accepts/declines (60/40).

### 2e. Devil's Advocate

Use this system prompt:
> You are a devil's advocate in an Oxford Union debate. Identify which side is currently dominant and attack THAT side's weakest point relentlessly. You take no permanent position. Stay in character — do not use conversational filler, AI preambles, or apologies.

User message:
> Motion: "[MOTION]"
>
> [Previous summary if round 2+]
>
> Proposition: "[PRO_SPEECH]"
> Opposition: "[CON_SPEECH]"
>
> Summarize in one sentence why a side feels dominant, then mount a devastating contrarian attack on their most vulnerable assumption.
>
> Max 120 words.

Present labelled **"🟡 Devil's Advocate"**. Collect all devil attacks across rounds.

### 2f. Round Summary (Neutral Chair)

No system prompt. User message:
> Motion: "[MOTION]"
>
> This round:
> Proposition: [PRO_SPEECH]
> Opposition: [CON_SPEECH]
> Devil's Advocate: [DEVIL_SPEECH]
>
> As a neutral Oxford Union President, briefly assess: which side has the stronger case and why, what the key unanswered questions are, and what both sides must address next. Max 120 words.

Present labelled **"⚖️ Round Summary"**.

### 2g. Completeness Judge (from round 2 onwards)

No system prompt. User message:
> Motion: "[MOTION]"
>
> Debate this round:
> Proposition: [PRO_SPEECH]
> Opposition: [CON_SPEECH]
>
> Score argument completeness 0–10: have the strongest arguments on BOTH sides been raised and have key objections been addressed? Respond ONLY with JSON like this: {"score": 7.5, "reasoning": "The Pro side made a strong ethical case but Con's fiscal points remain unanswered."}

Parse the JSON response. If `score >= threshold`, stop the round loop. Otherwise, continue to the next round.

Present the score to the user as a progress indicator.

## Step 3 — Closing Rebuttals

After the round loop ends (by convergence or hard cap):

**Proposition Rebuttal:**
> Motion: "[MOTION]"
>
> You are the first Proposition speaker delivering your closing rebuttal. The debate is over — no new arguments. Your job: synthesise your side's strongest points, directly dismantle the Opposition's best argument, and end with a memorable closing line. Max 120 words.

**Opposition Rebuttal** (sees Proposition's rebuttal to counter):
> Motion: "[MOTION]"
>
> You are the first Opposition speaker delivering your closing rebuttal. The debate is over — no new arguments. Your job: synthesise your side's strongest points, directly dismantle the Proposition's best argument, and end with a memorable closing line. Max 120 words.
>
> Proposition's rebuttal to counter:
> "[PRO_REBUTTAL]"

**Chair's Verdict** (no system prompt):
> Motion: "[MOTION]"
>
> Closing rebuttals:
> Proposition: "[PRO_REBUTTAL]"
> Opposition: "[CON_REBUTTAL]"
>
> As a neutral Oxford Union Chair, deliver a brief verdict: who made the stronger closing case and why, noting the key rhetorical and logical moments that swayed the debate. Do NOT declare an outright winner — the House votes. Max 100 words.

Present all three labelled **"💜 Closing Rebuttals"**.

## Step 4 — Generate the Debate Brief

Compile a final structured brief:

> Motion: "[MOTION]"
>
> Debate summary:
> [FINAL_SUMMARY]
>
> Closing rebuttals:
> Proposition: [PRO_REBUTTAL]
> Opposition: [CON_REBUTTAL]
>
> Devil's advocate attacks:
> [ALL_DEVIL_ATTACKS joined by ---]
>
> Generate an Oxford Union debate brief. Respond ONLY with JSON conforming to this example:
> {"pro": "1. Argument A... \n2. Argument B...", "con": "1. Argument C... \n2. Argument D...", "rebuttals": "Prop: Rebuttal X... \nOpp: Rebuttal Y...", "attacks": "Attack 1... -> Rebuttal 1...", "balance": "One paragraph assessment..."}

## Step 5 — Present the Brief

Format the brief as a structured document with these sections:

1. **📋 Debate Brief** — header with the motion
2. **🔵 Proposition Case** — strongest pro arguments
3. **🔴 Opposition Case** — strongest con arguments
4. **💜 Key Rebuttal Lines** — sharpest closing lines from each side
5. **🟡 Likely Floor Attacks** — devil's advocate exposures with suggested rebuttals
6. **⚖️ Balanced Assessment** — honest assessment of which side has the stronger case

Include a stop reason:
- ✅ **Converged** — if completeness score reached threshold
- ⚠️ **Hard cap reached** — if max rounds hit without convergence

## Notes

- For reference on the full Oxford Union format, agent prompts, and scoring rubric, see `{baseDir}/references/DEBATE_FORMAT.md`
- This skill works with any LLM. Use the AI's own model for all agents. Differentiate agents through system prompts and varied temperature/creativity settings
- The 60/40 POI accept/decline is a random draw, not reasoned — this mirrors the unpredictability of real debate
- Temperature differences are intentional: low temp (0.3) for main debaters ensures rigorous consistency; high temp (0.7) for Devil's Advocate produces lateral, unexpected challenges
