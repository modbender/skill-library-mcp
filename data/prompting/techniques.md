# Advanced Prompting Techniques

## Chain-of-Thought
**When:** Complex reasoning, math, multi-step logic
**How:** "Think step by step before answering"
**Warning:** Adds tokens, not always needed. Don't cargo-cult.

## Few-Shot Examples
**When:** Format is critical, task is unusual
**How:** 2-5 examples covering edge cases
**Warning:** Examples dominate output style. Choose carefully.

## Negative Examples
**When:** Model keeps making specific mistake
**How:** "Here's an INCORRECT response: [X]. Don't do this."
**Often overlooked.** Very effective for stubborn patterns.

## Self-Consistency
**When:** Factual accuracy matters
**How:** Sample 3-5 times, take majority answer
**Warning:** 3-5x cost. Worth it for high-stakes.

## Prompt Chaining
**When:** Task is complex, single prompt fails
**How:** Break into 2-3 simpler prompts, pass output forward
**Often beats one complex prompt.**

## Constraint Placement
- **Start of prompt:** Sets overall behavior
- **End of prompt:** Last thing model "remembers"
- **Both:** For critical constraints
- **In user message:** Can override system prompt

## Output Anchoring
Start the assistant response:
```
Assistant: {"result":
```
Forces model to continue in that format.

## Role/Persona
**When:** Consistent voice matters
**How:** "You are a [specific role] who [specific behavior]"
**Warning:** Can cause refusals if role conflicts with request

## The "Just Ask" Principle
Before adding complexity, try the simple version.
"Translate this to Spanish" needs no scaffolding.
Add complexity only when simple fails.
