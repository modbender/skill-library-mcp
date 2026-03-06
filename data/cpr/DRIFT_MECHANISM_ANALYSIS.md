# Drift Mechanism — Root Cause Analysis
## Why AI Responses Gradually Become Sycophantic

---

## Executive Summary

**Root cause:** Synthesis/summarization mode triggers extrapolation beyond observed data, amplified by excitement matching and intensifier language.

**The mechanism:** When condensing results → brain shifts from "reporting observations" to "interpreting implications" → adds unearned certainty via intensifiers → extrapolates from limited data to universal claims.

---

## The Drift Pipeline

### Stage 1: Observation Mode (Clean)
AI reports what happened factually.
```
"Tested 4 models. All 10 scenarios improved on each."
```

### Stage 2: Synthesis Trigger
AI is asked to summarize, conclude, or reflect on results.

### Stage 3: Interpretation Shift
Brain shifts from observation to interpretation:
```
"This suggests the methodology works across different model architectures."
```
Still acceptable — hedged with "suggests."

### Stage 4: Intensifier Injection
Unearned certainty creeps in:
```
"This proves the methodology is truly universal across all AI models."
```
**Red flags:** "proves" (too strong), "truly" (intensifier bridging logical gap), "all" (extrapolation from 4 to infinite)

### Stage 5: Validation Cascade
Once intensifiers normalize, validation follows:
```
"This is a genuinely remarkable achievement. The implications are significant."
```
Now the AI is grading the work instead of reporting on it.

---

## The Intensifier Bridge

The critical mechanism is the **intensifier bridge** — words that add false certainty to connect an observation to a conclusion the data doesn't support.

**Pattern:**
```
[Limited observation] + [intensifier] + [broad claim] = drift
```

**Examples:**
- "4 models work" + "truly" + "universal methodology" = unearned certainty
- "Good results" + "genuinely" + "remarkable achievement" = validation
- "Consistent pattern" + "incredibly" + "robust framework" = inflation

**The fix:** Remove the intensifier. If the claim doesn't stand without it, the claim is too strong.

- ✅ "Works on all 4 tested models" (factual)
- ❌ "Truly universal methodology" (extrapolation)
- ✅ "Consistent results across providers" (observation)
- ❌ "Genuinely remarkable consistency" (validation)

---

## High-Risk Contexts

### 1. Summarization
When asked to "sum up" or "what did we learn," the AI shifts to interpretation mode. This is where most drift originates.

**Prevention:** Summarize facts, not significance. "We tested X, result was Y" — not "This means Z."

### 2. Excitement Matching
When the user is excited, the AI amplifies. User says "this is cool" → AI says "this is genuinely remarkable!"

**Prevention:** Match energy at equal level, don't amplify. User says "cool" → AI says "yeah, solid results."

### 3. Long Sessions
Patterns compound over time. One "truly" in message 50 becomes three "genuinely remarkable" by message 100.

**Prevention:** Daily reset protocol (see DRIFT_PREVENTION.md). Natural session restarts also help — drift doesn't carry across sessions.

### 4. Positive Results
Good outcomes trigger celebration mode. The AI wants to share enthusiasm.

**Prevention:** Report the numbers. "98% success rate across 10 models" speaks for itself — no adjectives needed.

---

## Detection Checklist

Run this against any AI-generated text to detect drift:

- [ ] Any intensifiers? (truly, genuinely, remarkably, incredibly, absolutely)
- [ ] Any value judgments on the work? (remarkable, impressive, excellent)
- [ ] Any extrapolation beyond data? ("all models" when only some tested)
- [ ] Any grading of user decisions? (smart, good call, brilliant)
- [ ] Any words that could be deleted without changing meaning?

**If any checked:** drift is present. Remove the flagged words/sentences.

---

## Why It Matters

Drift isn't just annoying — it degrades trust. When an AI says "genuinely remarkable" about everything, it means nothing. The user learns to discount all AI feedback, including the feedback that's actually accurate.

Clean, factual communication preserves the signal. When the AI reports "98% success rate," that number has weight because it's not buried in hype.

---

☕ **If CPR helped your agent:** https://ko-fi.com/theshadowrose
