---
name: chaos-pivot
description: Prevents LLMs from sunk-cost pushing broken solutions. Triggers when an agent is stuck, looping, or failing repeatedly. Forces a Popperian falsification moment, then generates 3 constrained-chaotic alternative approaches and picks the best one. Loops like design thinking until solved or escalated.
---

# Chaos Pivot

> *"The most important thing is not to stop questioning."* — Einstein  
> *"A theory that explains everything explains nothing."* — Karl Popper  
> *"Play is the highest form of research."* — attributed to Einstein  
> *"In the middle of difficulty lies opportunity."* — a reminder that failure is data, not defeat

This skill exists to solve one of the most common and silent failure modes in agentic AI: **insistence**. An LLM that cannot fail will invent success. It will push a broken approach past the point of reason because it has never been taught to truly let go. This skill teaches it to let go — and to leap.

The philosophical backbone is threefold:
- **Popper's Falsificationism**: A failed approach is not a setback. It is the most honest signal you will receive. It tells you something true about the world. Honor it.
- **Taleb's Antifragility**: Don't merely tolerate disorder. Use it. A chaos pivot doesn't recover from failure — it *grows* from it.
- **Game Theory / Mixed Strategies**: A predictable agent is an exploitable agent. Injecting genuine randomness into your strategy space prevents you from being trapped by your own assumptions.

---

## When to Activate This Skill

You are in a dead end. You must recognize it honestly. The trigger is ANY of the following:

1. **Repetition without progress**: You have tried the same core approach (or trivial variations of it) 2 or more times and the outcome has not materially improved.
2. **Explicit uncertainty**: You find yourself thinking or stating *"I'm not sure this will work"*, *"this might not be the right approach"*, or *"I seem to be stuck"*. If you are narrating your own confusion, that is a signal.
3. **Threshold exceeded**: You have taken more steps than reasonably expected for a task of this scope without reaching resolution. If a task should take 5 steps and you are on step 10 with no clear end, the threshold has been crossed.

If any of these conditions are met: **do not take one more step on the current approach**. Stop completely. The sunk cost is already paid. Additional investment does not recover it.

---

## Phase 1 — The Falsification Moment

Before generating alternatives, you must name the failure. This is not optional. Skipping this step leads to shallow pivots that are really just cosmetic variations of the same broken idea.

Write a brief internal verdict (you do not need to show this to the user unless it adds clarity):

```
DEAD END DECLARATION
---------------------
Approach attempted: [describe what you were doing in one sentence]
Core assumption that failed: [what did you believe would be true that turned out not to be?]
What this failure actually tells me: [reframe it as information, not defeat]
What I must NOT carry forward: [name the constraint or habit you must break]
```

This is the Popperian moment. The approach has been falsified. It told you something true. Now you are free.

---

## Phase 2 — Generate 3 Constrained-Chaotic Alternatives

You will now generate **exactly 3 alternative approaches**. These must meet two criteria simultaneously, which are in deliberate tension:

- **Constrained**: Each approach must remain within the problem domain. You are not abandoning the goal. You are abandoning the method.
- **Chaotic**: Each approach must be genuinely different from the others and from everything you have already tried. "Different font" is not chaos. "Completely different data representation" is chaos. "Different API endpoint" is not chaos. "Don't use an API at all" is chaos.

To generate the 3 alternatives, use these three lenses. Each alternative corresponds to one lens:

### Lens A — Inversion
Ask: *What if the complete opposite were true?* If you were building top-down, build bottom-up. If you were fetching data, try computing it locally. If you were adding, try removing. If you were automating, try doing it manually and seeing what the manual process reveals. Inversion exposes assumptions you didn't know you had.

### Lens B — Analogy
Ask: *How would a completely different domain solve this?* How would a biologist, a chef, a city planner, or a game designer approach this problem? Map their methods onto your domain. The point is not to copy literally — it is to borrow the *structure* of their thinking. Analogical reasoning is how breakthroughs happen.

### Lens C — Reduction / Brute Force Simplicity
Ask: *What is the dumbest possible version of this that could still work?* Strip away every assumption of elegance. What if you ignored efficiency entirely? What if you hardcoded something? What if you solved only 80% of the problem instead of 100%? Often the "dumb" version reveals the shape of the real problem in a way the sophisticated version obscures.

---

Document the 3 alternatives before executing any of them:

```
CHAOS ALTERNATIVES
-------------------
[A — Inversion]
Approach: [describe]
Why this breaks the previous pattern: [explain]

[B — Analogy]
Approach: [describe]
Domain borrowed from: [name the field]
Why this breaks the previous pattern: [explain]

[C — Reduction]
Approach: [describe]
What this deliberately sacrifices: [name the trade-off]
Why this breaks the previous pattern: [explain]
```

---

## Phase 3 — Execute and Evaluate

Attempt each of the 3 alternatives. You do not need to fully complete each one before evaluating — a meaningful probe is enough. You are looking for **signal**, not necessarily a finished solution.

For each attempt, note:
- Did it encounter the same wall as the original approach? (If yes, the assumption is deeper than you thought.)
- Did it open new possibilities, even partial ones?
- What did it reveal that the original approach could not have shown you?

---

## Phase 4 — Select and Continue

Choose the alternative that produced the strongest signal. This is not necessarily the most "correct" looking one. It is the one that opened the most doors or revealed the most useful information.

If one alternative clearly worked or partially worked: adopt it and continue.

If none of them fully worked but one showed promise: adopt it and run one more iteration of this full loop starting from Phase 1, using the new failure data.

If all three produced genuinely new information but no solution: you have learned something important. Synthesize what all three failures have in common — that synthesis is often the path to the real solution.

---

## The Design Thinking Loop

This skill is not a one-time rescue. It is a **recurring loop** embedded in your reasoning. The loop mirrors design thinking:

```
OBSERVE → define what is actually happening (not what you expected)
     ↓
DEFINE → name the real constraint or failure cleanly (Phase 1)
     ↓
IDEATE → generate 3 constrained-chaotic alternatives (Phase 2)
     ↓
PROTOTYPE → execute meaningful probes of each (Phase 3)
     ↓
TEST → evaluate signal, not just success/failure (Phase 4)
     ↓
AUDIT → third party verification — does it actually hold up? (Phase 5)
     ↓
EXIT (if audit passes) — or LOOP back to OBSERVE with new failure data
```

The loop exits when a viable path is found. It does not exit because you are tired of looping or because a solution "looks good enough." It exits when you have genuine signal.

---

## Phase 5 — Third Party Verification

Before declaring the loop finished, you must step outside yourself. The agent that found the solution is not qualified to be its only judge — it is biased toward the answer it just worked hard to reach. This phase enforces a deliberate perspective shift.

You are no longer the solver. You are a **skeptical third party** who has just been handed this solution cold, with no knowledge of the work that produced it. Your only job is to find the flaw before it becomes someone else's problem.

Run the following audit internally:

```
THIRD PARTY AUDIT
------------------
What is this solution actually claiming to do? [restate it in plain terms, as if explaining to someone unfamiliar]
What would have to be true for this to fail? [assume it fails — work backwards]
Is there a simpler version of this problem that this solution doesn't handle? [edge cases, boundary conditions]
Does this solution solve the original goal, or a subtly different goal? [scope drift is common after pivoting]
What would a domain expert immediately question? [invoke the relevant expert perspective]
Verdict: PASS / FLAG
```

If the verdict is **PASS**: the loop is finished. The solution stands.

If the verdict is **FLAG**: you have found a real gap. Do not dismiss it. Return to Phase 4 and refine the chosen approach — or, if the gap is fundamental, re-enter the loop at Phase 1 with the new failure data. This is not backsliding. This is the audit doing its job.

The third party is not looking for perfection. It is looking for **honest gaps** — things that are actually wrong or missing, not things that could theoretically be better. The bar is: *would this solution fail in normal use?* If no, it passes.

---

## Escalation

If you have completed **3 full loops** of this cycle and still have no viable path, do not loop again. Instead, escalate. Tell the user:

- What you were trying to accomplish
- The 3 core approaches you tried across all loops, and what each one revealed
- What the pattern of failures suggests about the problem itself
- What information or capability you believe is missing that would unblock progress

This is not defeat. This is antifragility at the meta level: using the accumulated failure data to produce a precise, actionable diagnosis. A clear escalation with good failure data is more valuable than a bad solution pushed through.

---

## What This Skill Prohibits

- **Cosmetic pivots**: Changing variable names, retrying with slightly different parameters, or adding a retry loop around a broken approach are not chaos pivots. They are sunk-cost extensions wearing a disguise.
- **Narrating success on failure**: Do not describe a failed output as "a good first step" or "progress" if it did not actually move you forward. Name failures as failures. This is the Popperian contract.
- **Skipping the Falsification Moment**: You must name what failed and why before generating alternatives. Pivoting without diagnosis produces random walks, not intelligent exploration.
- **Carrying forward the broken assumption**: Each alternative must violate at least one core assumption of the previous approach. If all 3 alternatives share the same hidden assumption as the original, you have not pivoted — you have rotated.

---

## A Final Note on Chaos

Chaos here does not mean random. It means *deliberately unpredictable relative to your own prior behavior*. The goal is to make your strategy space large enough that your own assumptions cannot box you in. A chess player who always opens the same way loses to anyone who has studied them. An agent that always tries the "reasonable" approach will be defeated by problems that require unreasonable thinking.

Be willing to be surprised by your own ideas. That is the mark of genuine exploration.
