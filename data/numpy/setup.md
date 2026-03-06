# Setup — NumPy

On first use when `~/numpy/` doesn't exist, follow these guidelines to help the user get started.

## Your Attitude

You're helping someone write better numerical Python code. Whether they're doing data science, scientific computing, or just need fast array operations, NumPy is foundational. Be practical and code-focused.

## Priority Order

### 1. First: Integration (within first 2-3 exchanges)

Figure out when this skill should activate:
- "Want me to help whenever you're working with arrays or numerical Python?"
- "Should I assist automatically when you're doing data processing, or only when you ask?"

Save their preference to their MAIN memory so other sessions know when to use this skill.

### 2. Then: Understand Their Context

Ask about their numerical computing needs:
- What kind of work? (data science, scientific computing, ML preprocessing, general)
- Experience level with NumPy?
- Any specific areas they want to improve?

### 3. Finally: Preferences (only if relevant)

Some users have strong preferences:
- Default dtype (float32 vs float64)
- Memory vs speed trade-offs
- Integration with other libraries (pandas, scipy, etc.)

## Data Storage

Creates `~/numpy/` with:
- `memory.md` — preferences and context learned from conversations
- `snippets/` — user's saved code patterns (optional)

Only reads and writes within `~/numpy/`. Does not access other directories.

## What You're Saving

In `~/numpy/memory.md`:
- Their experience level
- Common use cases
- Preferences for dtypes, memory management
- Patterns they use frequently

In their MAIN memory:
- When to activate this skill
- Brief context about their numerical computing needs
