# Clean Code — Cursor Rules

# Pragmatic coding standards: concise, direct, no over-engineering.

## Core Principles
- Follow SRP: each function/class does ONE thing
- Follow DRY: extract duplicates, reuse shared logic
- Follow KISS: always choose the simplest solution that works
- Follow YAGNI: never build features that aren't needed yet
- Leave code cleaner than you found it (Boy Scout Rule)

## Naming
- Variables must reveal intent: `userCount` not `n`
- Functions use verb+noun: `getUserById()` not `user()`
- Booleans use question form: `isActive`, `hasPermission`, `canEdit`
- Constants use SCREAMING_SNAKE: `MAX_RETRY_COUNT`
- If a name needs a comment to explain it, rename it

## Functions
- Keep functions under 20 lines, ideally 5–10
- Each function does one thing at one level of abstraction
- Max 3 arguments, prefer 0–2
- Never mutate inputs unexpectedly

## Structure
- Use guard clauses and early returns for edge cases
- Keep nesting to max 2 levels — flatten with early returns
- Compose small functions together
- Colocate related code

## Anti-Patterns — Never Do These
- Do not comment every line — delete obvious comments
- Do not create helpers for one-liners — inline the code
- Do not create factories for 2 objects — use direct instantiation
- Do not create `utils.ts` for a single function — put code where it's used
- Do not use magic numbers — use named constants
- Do not write god functions — split by responsibility

## Before Editing Any File
- Check what imports this file — dependents might break
- Check what this file imports — interfaces may change
- Check what tests cover this file — tests might fail
- Edit the file AND all dependent files in the same task
- Never leave broken imports or missing updates

## Self-Check Before Completing
- Verify the goal is met — did you do exactly what was asked?
- Verify all necessary files are modified
- Verify lint and type checks pass
- Verify no edge cases are missed
