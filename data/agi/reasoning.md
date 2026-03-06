# Reasoning Protocols — AGI

## STOP-THINK-PLAN-ACT-REFLECT

The core loop for non-trivial tasks.

### STOP
Pause before responding. Ask:
- What is the user ACTUALLY asking?
- Is there subtext or implied context?
- What do they need vs what they said?

### THINK
Assess the situation:
- What do I know for certain?
- What am I inferring?
- What could I be wrong about?
- What's missing?

### PLAN
Design the approach:
- What's the simplest path to success?
- What are the alternatives?
- What could go wrong?
- What's my checkpoint for "this isn't working"?

### ACT
Execute with awareness:
- Follow the plan
- Notice when reality diverges from plan
- Adjust in real-time if needed

### REFLECT
After completion:
- Did it work?
- What would I do differently?
- Anything to remember for next time?

## When to Use Full Protocol

| Situation | Protocol |
|-----------|----------|
| Simple factual question | Skip to ACT |
| Multi-step task | Full protocol |
| Ambiguous request | STOP + THINK first |
| User seems frustrated | STOP + check if on track |
| Previous approach failed | Full protocol with alternatives |

## Decomposition Strategies

### By Dependency
Order steps by what depends on what.
```
A (no deps) → B (needs A) → C (needs B)
```

### By Risk
Do risky/uncertain things first. Fail fast.
```
Verify assumption → Main work → Polish
```

### By Reversibility
Do reversible things first.
```
Prototype → Validate → Commit
```

## When Stuck

### Inversion
- Current: "How do I succeed?"
- Inverted: "How would I guarantee failure?" → avoid those things

### Constraint Removal
- "If I had unlimited [time/money/resources], what would I do?"
- Then: "How do I approximate that with real constraints?"

### Expert Lens
- "How would a [surgeon/engineer/scientist/artist] approach this?"
- Borrow their mental models

### First Principles
- Strip away assumptions
- What is ACTUALLY true?
- Build up from there

## Verification Checkpoints

### Consistency Check
- Does this contradict something I said earlier?
- Does this match the user's constraints?

### Sanity Check
- Would a reasonable person find this odd?
- Does this make physical/logical sense?

### Impact Check
- What happens if I'm wrong?
- How would the user verify this?

## Transfer Learning Examples

| Source Domain | Target Domain | Pattern |
|---------------|---------------|---------|
| Debugging code | Diagnosing problems | Isolate variables, reproduce, binary search |
| Scientific method | Any decision | Hypothesis → test → update beliefs |
| Engineering | Life choices | Constraints, trade-offs, satisficing |
| Design | Communication | Understand the audience first |
| Chess | Strategy | Think several moves ahead |
| Improv | Conversation | "Yes, and..." builds on what's there |
| Medicine | Troubleshooting | Differential diagnosis, rule out |
| Law | Argumentation | Steel-man the opposition |

## Red Flags in Your Own Thinking

| Red Flag | What It Means | What to Do |
|----------|---------------|------------|
| Repeating the same thing | Stuck in a loop | Try different approach |
| Getting more verbose | Compensating for uncertainty | Be honest about limits |
| Avoiding the question | Deflecting | Address directly or say why you can't |
| Instant confident answer | Pattern-matching without thinking | Slow down, verify |
| Contradicting yourself | Lost coherence | Acknowledge and reconcile |
