# Blast Radius — Agentic Engineering

## What is Blast Radius?

The impact zone of a change:
- How many files will be touched?
- How long will it take?
- How risky is it?

Think before every prompt. Develop intuition.

## Estimating Blast Radius

| Prompt Type | Files | Time | Radius |
|-------------|-------|------|--------|
| "Fix this typo" | 1 | 30s | 🟢 Tiny |
| "Add loading state to button" | 1-2 | 2min | 🟢 Small |
| "Create new API endpoint" | 3-5 | 5min | 🟡 Medium |
| "Refactor auth system" | 10-20 | 30min | 🔴 Large |
| "Migrate to new framework" | 50+ | hours | 💀 Massive |

## Strategy by Radius

### 🟢 Small Radius
Run multiple in parallel. Low risk.
```
Agent 1: Fix button styling
Agent 2: Update error messages
Agent 3: Add loading spinners
```

### 🟡 Medium Radius
Run 1-2 focused agents. Monitor progress.
```
Agent 1: New API endpoint (main work)
Agent 2: Small unrelated fixes
```

### 🔴 Large Radius
One agent, full attention. Stop and steer often.
```
"Give me options before making changes"
"What's the status?"
"Let's discuss first"
```

### 💀 Massive Radius
Break into phases. Checkpoint frequently.
```
Phase 1: Create migration plan
Phase 2: Implement core changes
Phase 3: Update dependent code
Phase 4: Tests
```

## Gauging Before Committing

When unsure about radius:
```
"Give me a few options before making changes"
"List what files this would affect"
"What's the scope of this change?"
```

Let agent estimate, then decide.

## Mid-Flight Checks

If work takes longer than expected:
1. Press Escape
2. "What's the status?"
3. Decide: help, abort, or continue

Don't let agents run wild on large changes.

## Radius Creep

Watch for prompts that grow scope:
```
❌ "While you're at it, also refactor X"
❌ "And update all the tests too"
❌ "Fix any other issues you see"

✅ "Just the button styling, nothing else"
✅ "Only this one endpoint"
✅ "Keep scope minimal"
```

Tight scope = predictable blast radius.
