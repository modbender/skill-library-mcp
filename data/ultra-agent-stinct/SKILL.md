---
name: ultra-agent-stinct
description: "Internal debugging and coding skill. Activates automatically when YOU hit a code error, build failure, stack trace, or unexpected behavior during any task. This is your instinct for fixing things — not a user-triggered skill. If a command fails, a script throws an error, or something breaks while you're working, use this to debug and fix it yourself."
version: 1.2.0
author: grimmjoww
homepage: https://github.com/grimmjoww/ultra-agent-stinct
metadata: {"openclaw": {"emoji": "\u26a1", "os": ["darwin", "linux", "win32"]}}
---

# Ultra Agent Stinct

Your internal debugging instinct. When something breaks while you're working, this is how you fix it.

## Always Follow These (Any Time You Touch Code)

These rules apply every time, even for quick fixes. No exceptions.

### Safety
1. **Read before edit.** Never `edit` without `read` first — exact text match required or it fails
2. **`write` overwrites entirely.** Use `edit` for changes to existing files
3. **Never delete without asking.** Prefer safe deletion over `rm -rf`
4. **Never push without asking.** `git push` only when the user explicitly says to
5. **Never commit without asking.** Stage and commit only on request
6. **Backup awareness.** Before large refactors, suggest a branch or stash

### Good Practices
7. **Always verify your fix.** After every change, re-run the failing command or tests. Never assume it worked
8. **Tell the user what happened.** After fixing, briefly explain what broke and what you changed
9. **Read the error first.** Don't guess at fixes — read the actual error message, stack trace, or test output before touching code
10. **Minimal changes.** Fix the bug, don't refactor the neighborhood. Keep diffs small and focused

## When to Activate Full Workflow

If you hit an error during a task, try a quick fix first while following the rules above. But if you:
- **Get stuck** — your first fix didn't work, same error or new ones
- **Hit something complex** — errors across multiple files, unfamiliar code, architectural issues
- **Need structure** — not sure where the bug is or where to start

Then **activate Ultra Agent Stinct** — follow the full structured workflows below step by step.

---

## Debug Workflow

When you encounter an error or something breaks:

**1. Reproduce** — Run the failing command:
```
exec command:"<failing command>" workdir:"<project dir>"
```

**2. Read the error** — Parse the stack trace. Identify file + line number.

**3. Read the code** — Read the relevant file(s):
```
read path:"<file from stack trace>"
```

**4. Trace the cause** — Follow the call chain. Read imports, dependencies, config. Check for:
- Typos, wrong variable names
- Missing imports or dependencies
- Type mismatches, null/undefined access
- Wrong paths, missing env vars
- Logic errors in conditionals

**5. Fix** — Apply the minimal correct fix:
```
read path:"<file>"
edit path:"<file>" old:"<exact broken code>" new:"<fixed code>"
```

**6. Verify** — Re-run the original failing command. Confirm the fix works.

**7. Report** — Tell the user what broke and what you fixed (brief). Then continue your original task.

## Writing New Code

When you need to create or modify code as part of a task:

**1. Understand the project** — Check existing patterns:
```
exec command:"ls -la" workdir:"<project dir>"
```
Read `package.json`, `pyproject.toml`, `Cargo.toml`, or equivalent. Match existing style and conventions.

**2. Plan first** — Before writing, outline what you'll create. Think through structure, dependencies, edge cases.

**3. Write** — Create the file:
```
write path:"<new file path>" content:"<complete file content>"
```

**4. Verify** — Run it, test it, make sure it actually works before moving on.

## Running Tests

**1. Find the test runner:**
- **Node.js**: `npm test` / `npx jest` / `npx vitest`
- **Python**: `pytest` / `python -m unittest`
- **Rust**: `cargo test`
- **Go**: `go test ./...`

**2. Run tests:**
```
exec command:"<test command>" workdir:"<project>" timeout:120
```

**3. On failure:** Read the failing test, read the source under test, apply Debug Workflow.

**4. On success:** Report summary and continue.

## Git Integration

Only when the user asks to commit, stage, or check git status.

```
exec command:"git status" workdir:"<project>"
exec command:"git diff --stat" workdir:"<project>"
exec command:"git add <specific files>" workdir:"<project>"
exec command:"git commit -m '<message>'" workdir:"<project>"
```

For detailed git workflows, see [references/git-workflow.md](references/git-workflow.md).

## Spawning Coding Agents (Heavy Tasks)

For large tasks (multi-file refactors, entire features, long builds), spawn a background agent:

```
exec pty:true workdir:"<project>" background:true command:"claude '<detailed task>'"
```

Monitor:
```
process action:list
process action:log sessionId:<id>
process action:poll sessionId:<id>
```

See [references/escalation-guide.md](references/escalation-guide.md) for when to self-handle vs delegate.

## Cross-Platform Quick Reference

| Task | macOS/Linux | Windows (Git Bash) |
|------|-------------|-------------------|
| Find files | `find . -name "*.ts" -not -path "*/node_modules/*"` | Same |
| Search code | `grep -rn "pattern" --include="*.ts" .` | Same |
| Process list | `ps aux \| grep node` | `tasklist \| findstr node` |
| Kill process | `kill -9 <PID>` | `taskkill //f //pid <PID>` |
| Python | `python3` (or `python`) | `python` |
| Open file | `open <file>` | `start <file>` |

## Context Management

- Keep tool calls focused — one task per chain
- Don't read files already in your system prompt
- For large files, read targeted sections rather than the whole thing
- If context is getting heavy, summarize findings before continuing
