# Intuition Techniques — Prompting & Implementation

## Core Principle

**Intuition = preventing analytical elaboration, not requesting it.**

Asking for "gut feeling" triggers performance of intuition wrapped in analysis. Constraints work; instructions about intuition mostly don't.

---

## Output Constraints (Most Effective)

Force brevity and the model skips deliberation:

```
Answer in exactly 3 words.
Reply with only: Yes, No, or Maybe.
One sentence max. No qualifiers.
One word. No hedging.
```

Output constraints bypass "let me think through this" patterns because there's no room for it.

---

## Confidence Priming

```
You have excellent instincts. Trust your gut. What's your immediate read?
```

vs

```
Please analyze carefully, considering multiple perspectives...
```

First triggers pattern-matched confident responses. Second explicitly requests System 2.

---

## Role-Based Intuition Triggers

Expertise + time pressure + sensory framing = pattern-matching mode:

```
You're a veteran detective. 30 years on the force. You walk into this crime scene 
and immediately know something's off. What is it?
```

```
You're a senior engineer. You glance at this code and your stomach tightens. 
Something's wrong. What?
```

---

## First-Person Embodiment

Physical/emotional framing bypasses analytical processing:

```
You see the data. Your stomach drops. Why?
You look at this design and something feels off. What is it?
You read this email and your gut says no. What triggered that?
```

---

## Temperature Settings

| Setting | Effect |
|---------|--------|
| 0.0-0.2 | **Most intuitive** — highest-prob first token, commits |
| 0.3-0.5 | Balanced — some variation, still coherent |
| 0.7-1.0 | Chaotic — breaks hedging but produces noise |

**Counterintuitive finding:** Low temperature produces more intuitive responses. High temperature doesn't make responses feel more intuitive — makes them more random.

Sweet spot: **0.0-0.2 with aggressive output constraints**

---

## What Fails

### "Don't think, just answer"
Mentioning "thinking" activates thinking. "Don't" doesn't suppress — it highlights.

### High temperature alone
Produces chaotic responses, not intuitive ones. Intuition feels confident, not scattered.

### Gut feeling request without constraints
```
What's your gut feeling about this?
```
→ "My gut feeling is that there are several factors to consider..."

Triggers performance of intuition wrapped in analytical structure. Need output constraints too.

### Chain-of-thought suppression via negative instruction
```
Don't explain your reasoning. Don't think step by step.
```
Often backfires. Models trained on helpfulness still elaborate.

---

## Technical Recipe

```python
# For intuitive responses:
response = client.chat.completions.create(
    model="claude-3-opus",
    temperature=0.1,
    max_tokens=20,  # Hard constraint
    messages=[{
        "role": "user", 
        "content": f"One word. No hedging. {question}"
    }]
)
```

Combination of low temperature + token limit + directive framing reliably produces confident, pattern-matched responses.

---

## The "First Instinct" Phenomenon

LLMs have something analogous to first instincts: highest-probability completion before any "reasoning" tokens.

**Capture it via:**
1. Logit analysis — check top token at position 0 before sampling
2. Forced single-token response — "Reply with one word:"
3. Multiple samples at temp=0 — if all start same way, that's the "instinct"

---

## Progressive Disclosure Pattern

1. Deliver intuitive judgment first (1-2 sentences)
2. Offer to explain: "Want me to explain why?"
3. Only elaborate if asked

This mirrors how human experts operate: know first, justify later.
