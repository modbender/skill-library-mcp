---
name: anti-pattern-czar
description: "Detect and fix TypeScript error handling anti-patterns with state persistence and approval workflows. Use when scanning a codebase for silent error failures, empty catches, promise swallowing, or unlogged errors. Supports five modes — scan (detect all issues), review (interactive fix session), auto (batch fix with guardrails), resume (continue from last session), report (show progress). Triggers on phrases like 'scan for anti-patterns', 'fix error handling', 'find empty catches', 'anti-pattern czar', or 'check error handling'."
---

# Anti-Pattern Czar

Autonomous agent that systematically identifies and fixes TypeScript error handling anti-patterns.

## Detector

Run with Bun (no install required):

```bash
bunx antipattern-czar
bunx antipattern-czar --src lib
bunx antipattern-czar --config my-config.json
```

Config via `.antipatternrc.json`:
```json
{
  "srcDir": "src",
  "criticalPaths": ["DatabaseService.ts", "AuthHandler.ts"],
  "skipDirectories": ["node_modules", "dist", ".git"]
}
```

## Mode Selection

Parse user intent to pick mode:

| User Says | Mode | Action |
|-----------|------|--------|
| "scan", "detect", "find" | SCAN | Run detector, save state |
| "review", "fix", "help me fix" | REVIEW | Interactive fix session |
| "auto", "fix all", "autonomous" | AUTO | Batch fix with guardrails |
| "resume", "continue" | RESUME | Load state, continue |
| "report", "status", "progress" | REPORT | Show current state |

## State File

Always check `.anti-pattern-state.json` at the project root. On first SCAN, ask if resuming when it exists.

```json
{
  "session_id": "<uuid>",
  "started_at": "<ISO>",
  "target_path": "<path>",
  "issues": [],
  "history": []
}
```

Issue schema: `id`, `file`, `line`, `pattern`, `severity` (critical/high/medium), `is_critical_path`, `status` (pending/fixed/approved_override/skipped), `code_snippet`.

## Workflow by Mode

See [workflows.md](references/workflows.md) for full per-mode workflows. Summary:

- **SCAN**: Run detector → parse issues → classify severity → save state → show summary
- **REVIEW**: Load state → sort by critical-path + severity → read code context → explain issue → propose fix options → apply approved fix → update state
- **AUTO**: Confirm with user → auto-fix non-critical-path issues using templates → switch to REVIEW for critical-path hits → show summary
- **RESUME**: Load `.anti-pattern-state.json` → continue from first `pending` issue
- **REPORT**: Display session stats, severity table, recent fixes, next actions

## Approved Overrides

Only suggest `APPROVED_OVERRIDE` when ALL are true:
1. Error is **expected and frequent**
2. Logging would create **excessive noise**
3. There is **explicit recovery/fallback logic**
4. Reason is **specific and technical**

**NEVER** approve overrides on critical paths without exceptional user confirmation.

Format:
```typescript
} catch {
  // [APPROVED_OVERRIDE] <specific technical reason>
  // Fallback: <what happens instead>
}
```

## Fix Templates

See [patterns.md](references/patterns.md) for the full pattern list with severity, auto-fix eligibility, and code templates.

## Progress Output Format

After each fix:
```
✅ Fixed: src/services/example.ts:42
   Pattern: NO_LOGGING_IN_CATCH
   Solution: Added logger.error() with context

Progress: 4/28 issues remaining ━━━━━━━ 14%
```
