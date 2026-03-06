# Hooks Integration Complete 🎯

**Completed**: 2025-02-26T17:30:00Z
**Phase**: Phase 3 (Optional Enhancement)

## What Was Created

### Custom Hook Handlers

**Location**: `/Volumes/Transcend/GitHub/openclaw-workflow/hooks/openclaw/`

1. **handler.ts** — TypeScript implementation for Node/Deno
2. **handler.js** — JavaScript fallback implementation
3. **HOOK.md** — Complete documentation

### What the Hook Does

Fires on `agent:bootstrap` event (session start) and injects a virtual file:

```
PI_WORKFLOW_REMINDER.md
├── 📝 When to log lessons (corrections, insights)
├── ⚠️ When to log errors (command failures, API issues)
├── 💡 When to log features (capability gaps)
├── 🔄 How to track recurring patterns (Recurrence-Count ≥ 3)
├── ⬆️ How to promote to AGENTS.md/SOUL.md/TOOLS.md
└── 🔗 Link to detailed guide (references/phase1-phase2-enhanced-lessons.md)
```

**Output**: ~400 tokens (lightweight, non-intrusive)

---

## Customizations vs Self-Improving-Agent

| Feature | Self-Improving-Agent | Pi-Workflow Custom |
|---------|--------------------|--------------------|
| **File Paths** | `.learnings/LEARNINGS.md` | `tasks/lessons.md` ✅ |
| | `.learnings/ERRORS.md` | `tasks/errors.md` ✅ |
| | `.learnings/FEATURE_REQUESTS.md` | `tasks/feature_requests.md` ✅ |
| **ID Format** | Generic | `[LRN/ERR/FEAT-YYYYMMDD-XXX]` ✅ |
| **Metadata** | Basic reminder | Phase 1+2 format ✅ |
| **Recurring Detection** | Mentioned | Explained + Pattern-Key ✅ |
| **Promotion Path** | Generic | AGENTS.md/SOUL.md/TOOLS.md ✅ |

---

## How to Enable

### Option A: If Using ClawHub Skill

```bash
# Install/update pi-workflow from clawhub
clawdhub install pi-workflow

# Enable the hook
openclaw hooks enable pi-workflow

# Verify
openclaw hooks list
```

You should see `pi-workflow` in the hooks list.

### Option B: Manual Installation

```bash
# Copy hook to OpenClaw hooks directory
cp -r hooks/openclaw ~/.openclaw/hooks/pi-workflow

# Enable
openclaw hooks enable pi-workflow

# Verify
openclaw hooks list
```

### Option C: Verify Hook is Ready

```bash
# Check hook status
openclaw hooks list

# Restart gateway if needed
openclaw gateway restart

# Test: start new session
/new
```

You should see the `PI_WORKFLOW_REMINDER.md` in bootstrap context.

---

## Architecture

### Hook Flow

```
Session Start
     ↓
agent:bootstrap event fires
     ↓
handler.ts/handler.js executes
     ↓
Safety checks:
  - Is this agent:bootstrap? ✓
  - Is this not a sub-agent? ✓
  - Do we have context? ✓
     ↓
Inject virtual file:
  path: PI_WORKFLOW_REMINDER.md
  content: Self-improvement guidance
  virtual: true
     ↓
Reminder appears in session
```

### Handler Logic

```typescript
// Safety-first approach
if (!event || event.type !== 'agent' || event.action !== 'bootstrap') return;
if (!event.context || !Array.isArray(event.context.bootstrapFiles)) return;
if (sessionKey.includes(':subagent:')) return;  // Skip sub-agents

// Inject reminder
event.context.bootstrapFiles.push({
  path: 'PI_WORKFLOW_REMINDER.md',
  content: REMINDER_CONTENT,
  virtual: true,  // No file system write
});
```

---

## File Changes

### Skill Repository
```
/Volumes/Transcend/GitHub/openclaw-workflow/
├── hooks/openclaw/
│   ├── handler.ts        ✅ NEW - TypeScript handler
│   ├── handler.js        ✅ NEW - JavaScript handler
│   └── HOOK.md           ✅ NEW - Documentation
└── SKILL.md              ✅ UPDATED - References hooks
```

### Workspace
```
~/.openclaw/workspace/
└── HOOKS-SETUP.md        ✅ NEW - Setup guide
```

### Git Commit
```
806b319 Add custom hooks for Phase 1+2 self-improvement system
```

---

## Customization Guide

### Edit Hook Reminder

1. Open handler file:
```bash
nano ~/.openclaw/hooks/pi-workflow/handler.ts
```

2. Find `REMINDER_CONTENT` variable
3. Edit the markdown content
4. Restart gateway:
```bash
openclaw gateway restart
```

### Example: Add Internal Link

```typescript
const REMINDER_CONTENT = `
## 🧠 Self-Improvement Reminder

... existing content ...

### See Also
- [Company Wiki](https://internal.wiki/lessons)
- [Project Template](https://docs/template)
`;
```

### Example: Reduce Output

Delete non-essential sections from `REMINDER_CONTENT` to reduce token overhead.

---

## Troubleshooting

### Hook doesn't appear at session start

1. Check hook list:
```bash
openclaw hooks list
```

2. If `pi-workflow` not listed or not `enabled`:
```bash
openclaw hooks enable pi-workflow
```

3. Restart gateway:
```bash
openclaw gateway restart
```

4. Start new session:
```bash
/new
```

### Hook shows but has wrong content

- Verify you're using the custom handler files (not original self-improving-agent)
- Check that `REMINDER_CONTENT` references `tasks/` paths (not `.learnings/`)

### Hook interferes with other hooks

Multiple hooks can coexist. They fire in order. If there's output duplication:
- Check all enabled hooks: `openclaw hooks list`
- Look for conflicts
- Disable unneeded hooks: `openclaw hooks disable hook-name`

### Hook shows outdated information

The reminder is injected at session start. If you edit SKILL.md or reference docs:
- Restart gateway: `openclaw gateway restart`
- The reminder references docs files, not hardcoded paths

---

## Important Notes

### Virtual File Injection

- Hook creates a **virtual file** in bootstrap context
- Does **not** write to disk
- Appears as `PI_WORKFLOW_REMINDER.md` in your session context
- Is **not** saved to your workspace

### Safety-First Design

- Handles null/undefined gracefully
- Skips sub-agent sessions (no cascade injection)
- No file modifications
- No environment variable pollution
- Error-safe (won't break session if hook fails)

### Optional, Not Required

- Hooks are **optional enhancement**
- Phase 1+2 works without hooks
- Hooks just add reminders for better adoption
- Can disable anytime

---

## Next Steps

1. **Enable hook**: `openclaw hooks enable pi-workflow` (or `clawdhub install pi-workflow`)
2. **Restart gateway**: `openclaw gateway restart`
3. **Test**: Start new session `/new` and see reminder
4. **Start using** Phase 1+2 format for new lessons/errors/features

---

## References

- **Phase 1+2 Guide**: `references/phase1-phase2-enhanced-lessons.md`
- **Hook Documentation**: `hooks/openclaw/HOOK.md`
- **Setup Guide**: `~/.openclaw/workspace/HOOKS-SETUP.md`
- **Completion Summary**: `~/.openclaw/workspace/PHASE1-PHASE2-COMPLETION.md`
- **SKILL.md**: Updated with hook section

---

## Git Commit

```
806b319 Add custom hooks for Phase 1+2 self-improvement system

- Create handler.ts and handler.js for agent:bootstrap event
- Inject PI_WORKFLOW_REMINDER.md with tailored guidance
- Points to tasks/ files (lessons.md, errors.md, feature_requests.md)
- References Phase 1+2 format and recurring pattern tracking
- Add HOOK.md documentation with setup and configuration
- Update SKILL.md with hook enablement instructions
```

---

## Summary

✅ **Phase 1**: Structured metadata for lessons (Priority, Status, Area, Pattern-Key, Recurrence-Count)
✅ **Phase 2**: File separation (lessons.md, errors.md, feature_requests.md)
✅ **Phase 3**: Custom hooks for reminders (tailored to your workspace structure)

**Status**: Complete and ready to use. Next: enable hooks and start capturing learnings!
