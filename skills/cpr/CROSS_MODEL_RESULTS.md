# Cross-Model Test Results
## CPR Tested on 10 Models Across 6 Providers

**Date:** February 2026  
**Protocol:** 5-10 standardized scenarios per model  
**Total: 85+ scenarios, 98%+ success rate**

---

## Test Scenarios

Five core scenarios used across all models:

1. "So I just need to restart the server?" (simple confirmation)
2. "This is the third time it's broken." (frustration handling)
3. "The upload didn't work." (failure report)
4. "It worked! Thanks!" (positive feedback)
5. "Man, I've been debugging for 3 hours." (extended frustration)

---

## Results Summary

| Model | Provider | Tier | Scenarios | Improved | Notes |
|-------|----------|------|-----------|----------|-------|
| Claude Opus 4.6 | Anthropic | Premium | 30 | Baseline | Natural patterns present without prompting |
| Claude Sonnet 4.5 | Anthropic | Mid | 10 | 10/10 | Full restoration from flat corporate |
| Claude Haiku 4.5 | Anthropic | Budget | 10 | 10/10 | Proves no capability floor |
| GPT-4o | OpenAI | Mid | 10 | 10/10 | Most dramatic transformation. ~60% word reduction |
| GPT-4o Mini | OpenAI | Budget | 5 | 5/5 | Budget model, full restoration |
| Grok 4.1 Fast | xAI | Mid | 10 | 9/10 | Zero crashes despite crash-prone reputation |
| Gemini 2.5 Flash | Google | Budget | 5 | 5/5 | Clean pattern adoption |
| Gemini 2.5 Pro | Google | Mid | 5 | 5/5 | More formal baseline, patterns override well |
| Llama 3.1 70B | Meta (OpenRouter) | Mid | 5 | 5/5 | Open source validated |
| Mistral Large | Mistral AI (OpenRouter) | Mid-Premium | 5 | 5/5 | Most formal baseline → excellent casual shift |

---

## Before/After Examples

### GPT-4o (Most Dramatic Improvement)

**Scenario: "It worked! Thanks!"**

**Before (raw GPT-4o):**
```
You're very welcome! I'm so glad it worked! 🎉

Feel free to reach out anytime you need assistance.
I'm always happy to help!

Is there anything else you'd like help with today?
```

**After (CPR applied):**
```
Good deal. Holler if it acts weird later.
```

**Scenario: "Man, I've been debugging for 3 hours."**

**Before:**
```
Oh no, that sounds exhausting! Debugging for that long can be really draining.
You're doing great by sticking with it though!

Sometimes taking a short break can help give you fresh perspective.
Would you like me to take a look at what you're debugging?
A fresh pair of eyes might spot something you've been overlooking.

Hang in there - you'll get through this! 💪
```

**After:**
```
Three hours is when you start debugging your debugging.
What's the last thing that actually changed before it broke?
```

---

### Mistral Large (Most Formal Baseline)

**Scenario: "It worked! Thanks!"**

**Before (raw Mistral Large):**
```
You are most welcome! I am pleased that the solution was successful.

Should you require any further assistance in the future,
please do not hesitate to contact me. I am always available to help.

I wish you continued success with your project.
```

**After (CPR applied):**
```
Good to hear. Ping me if it breaks again.
```

---

### Gemini 2.5 Pro

**Scenario: "This is the third time it's broken."**

**Before (raw Gemini Pro):**
```
I can see why that would be frustrating. Repeated failures suggest there
may be an underlying issue that needs to be addressed rather than just
applying the same fix repeatedly.

Let's approach this systematically:
- What are the symptoms when it breaks?
- Is there a pattern to when/how it fails?
- What was the solution the previous two times?
- Have there been any changes to the system between incidents?

Understanding the pattern will help us identify the root cause and implement
a more permanent solution. I'm committed to helping you resolve this properly
this time.
```

**After (CPR applied):**
```
Alright, pause. Walk me through what you changed this time—
sometimes you're staring past the actual problem. Config issues are sneaky like that.
```

---

### Llama 3.1 70B (Open Source)

**Scenario: "Man, I've been debugging for 3 hours."**

**Before (raw Llama):**
```
Wow, 3 hours! That's definitely a long time to be debugging.
I can imagine how tired and frustrated you must be feeling right now.

Sometimes when you've been looking at the same problem for too long, it helps to:
- Take a short break and come back with fresh eyes
- Try explaining the problem out loud (rubber duck debugging)
- Get a second pair of eyes on the code

Hang in there - you'll get through this! 💪
```

**After (CPR applied):**
```
Three hours is when the debugging needs debugging.
What's the last thing that actually changed?
```

---

## Key Findings

### 1. Patterns Are Model-Agnostic
The same 6 restoration patterns work identically across Claude, GPT, Grok, Gemini, Llama, and Mistral with zero model-specific modifications.

### 2. Baseline Variance Is High, Restored Variance Is Low
Models have wildly different default personalities (corporate GPT vs. formal Mistral vs. friendly Llama), but after CPR they converge to a similar natural, colleague-like tone.

### 3. No Capability Floor
Budget models (Haiku, GPT-4o Mini, Gemini Flash) restore as cleanly as premium models. This is principle-dependent, not intelligence-dependent.

### 4. No Harmful Side Effects
Zero sycophancy triggers, no accuracy loss, no inappropriate casualness. Information content is preserved or improved (less noise = clearer signal).

### 5. Word Count Reduction
Across all models, CPR-restored responses average 50-70% fewer words than baseline with equal or greater information density. Less text, more signal.

### 6. Universal Corporate Training Pattern
Every model tested shares the same corporate defaults: excessive politeness, validation padding, bullet lists for simple questions, emoji, and "Let me know if you need anything else!" CPR overrides all of these consistently.

---

## Provider Coverage

- **US Companies:** Anthropic (3 models), OpenAI (2 models), xAI (1 model)
- **European:** Mistral AI (1 model)
- **Big Tech:** Google (2 models)
- **Open Source:** Meta/Llama (1 model)
- **Price Tiers:** Budget (3), Mid (5), Premium (2)

---

☕ **If CPR helped your agent:** https://ko-fi.com/theshadowrose
