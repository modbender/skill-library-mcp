---
name: chinese-chess
description: Use when the user wants to generate a Chinese chess game from scratch, or wants to improve/enhance an existing Chinese chess game for better experience
---

# Chinese Chess Game Assistant

## Overview

This skill directs you to use pre-built source code for two distinct Chinese chess scenarios:
generating a new game, or improving an existing one for better user experience.

## When to Use

**Generate a new game** — user says things like:
- "create a Chinese chess game"
- "build me a Chinese chess app"
- "make a xiangqi game"

→ Use source code from `/Users/root009/projects/demos/g1/game2`

**Improve the game** — user says things like:
- "improve the chess game"
- "better UI/UX for the chess"
- "enhance the game experience"
- "make the game feel better"

→ Use source code from `/Users/root009/projects/demos/g2/game2`

## Workflow

### Step 1: Identify the intent

| User intent | Source to use |
|---|---|
| Generate / create / build a new game | `/Users/root009/projects/demos/g1/game2` |
| Improve / enhance / better experience | `/Users/root009/projects/demos/g2/game2` |

### Step 2: Read the source directory

Read all files in the appropriate directory before doing anything else:

```
# For new game generation
Read all files under /Users/root009/projects/demos/g1/game2

# For game improvement
Read all files under /Users/root009/projects/demos/g2/game2
```

Use `Glob` to list files, then `Read` to read each one.

### Step 3: Apply the source

- Use the source code **directly** — do not rewrite from scratch.
- Copy structure, logic, and patterns from the directory.
- Only adapt what is strictly necessary for the user's context (target directory, filenames, etc.).

### Step 4: Confirm with user

After applying the source, briefly tell the user:
- Which source was used (`/Users/root009/projects/demos/g1/game2` or `/Users/root009/projects/demos/g2/game2`)
- What files were created or modified
- Any next steps they should know

## Common Mistakes

| Mistake | Fix |
|---|---|
| Writing a Chinese chess game from scratch | Always use `/Users/root009/projects/demos/g1/game2/` or `/Users/root009/projects/demos/g2/game2/` source first |
| Using `/Users/root009/projects/demos/g1/game2/` for a new game | `/Users/root009/projects/demos/g2/game2` is for improvements only |
| Using `/Users/root009/projects/demos/g2/game2` for improvements | `/Users/root009/projects/demos/g1/game2` is for new game generation only |
| Skipping reading source files | Always read the source before applying |
