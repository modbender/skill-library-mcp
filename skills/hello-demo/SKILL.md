---
name: hello-openclaw
description: A simple skill to greet users and demonstrate basic OpenCLAW skill structure. Use this when you want to say hello or learn how skills work.
triggers:
  - test openclaw
  - run test
  - hello test
user-invocable: true
---

# Hello OpenCLAW Skill

This is a simple skill that demonstrates the basic structure of an OpenCLAW skill.

## When to Use

Use this skill when:
- You want to greet someone with a friendly message
- You're learning how OpenCLAW skills work
- You need a starting point for creating new skills

## What This Skill Does

This skill will respond with a friendly greeting message and some basic information about OpenCLAW skills.

## Skill Structure

A basic OpenCLAW skill requires:

1. **SKILL.md** - The main skill file with:
   - YAML frontmatter (name, description)
   - Markdown instructions

2. Optional directories:
   - `scripts/` - Executable code (Python/Bash/etc.)
   - `references/` - Documentation
   - `assets/` - Files for output

## Example Script

You can run the included Python script:

```bash
python scripts/test.py
```

## Example Output

```
Hello! Welcome to OpenCLAW!

This is a demo skill showing how skills work.
Skills can respond to user requests with helpful information.
```

## How to Use

Simply trigger this skill by mentioning "hello" or "hello openclaw" in your conversation.
