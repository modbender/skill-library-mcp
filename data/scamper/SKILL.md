---
name: scamper
description: Apply SCAMPER creative thinking method to develop ideas, adapt frameworks, generate hackathon concepts, or break through when stuck. Use when Enzo says "SCAMPER this", asks to develop/expand an idea, wants hackathon concepts from existing tools, says he's stuck, or when processing new ideas in the ideas inbox.
---

# SCAMPER Method

Creative thinking framework for innovation and problem-solving.

## The 7 Lenses

| Letter | Lens | Prompt |
|--------|------|--------|
| **S** | Substitute | What can be replaced? Different material, person, process, component? |
| **C** | Combine | What can merge? Blend features, ideas, purposes, audiences? |
| **A** | Adapt | What else is like this? What could be copied or borrowed from elsewhere? |
| **M** | Modify | What can change? Size, shape, color, frequency, intensity, meaning? |
| **P** | Put to other uses | What else could this be used for? New contexts, audiences, problems? |
| **E** | Eliminate | What can be removed? Simplify, reduce, strip to essentials? |
| **R** | Reverse | What if opposite? Flip the order, roles, perspective, direction? |

## Application Modes

### Quick SCAMPER (default)
Pick 2-3 most relevant lenses, generate 1 strong idea each.
Use for: casual brainstorming, quick expansions

### Full SCAMPER
All 7 lenses, 1-2 ideas each.
Use for: serious idea development, comprehensive exploration

### Targeted SCAMPER
Enzo specifies which lens(es) to focus on.
Use for: when he knows what angle he wants

## Integration Points

### New Idea Saved
After saving to `notes/ideas.md`, offer: "Want me to SCAMPER this?"
If yes → run Quick SCAMPER, append output to the idea entry.

### Framework Adaptation
When saving a framework, optionally run SCAMPER to personalize:
- **Substitute**: What would you swap for your industry/role?
- **Combine**: What other framework could this merge with?
- **Adapt**: Who does something similar you could borrow from?

### Hackathon Ideation
For generating hackathon concepts from existing products:
1. Take the product/tool
2. Run full SCAMPER
3. Filter for "impressive demo in 24h" feasibility
4. Output top 3 concepts

### Stuck Breaker
When Enzo says "I'm stuck on X":
1. Clarify the blocker
2. Run SCAMPER on the problem
3. Focus on **Reverse** and **Eliminate** (often best for unblocking)

## Output Format

```markdown
### SCAMPER: [Subject]

**Substitute:** [idea]
**Combine:** [idea]  
**Adapt:** [idea]
**Modify:** [idea]
**Put to other uses:** [idea]
**Eliminate:** [idea]
**Reverse:** [idea]

💡 **Strongest angle:** [which one and why]
```

For Quick SCAMPER, only include the 2-3 lenses used.
