# acpx v4.0 Quick Reference

## Main CLI Commands

```bash
acpx discover              # List installed agents
acpx health                # Health check all agents
acpx run <agent> "task"    # Run single agent
acpx parallel tasks.txt    # Run parallel from file
acpx batch tasks.txt       # Run sequential from file
acpx watch <agent>         # Watch agent status
acpx kill <agent>          # Kill agent sessions
acpx workflow <name>       # Run preset workflow
acpx json <agent> "task"   # Run with JSON output
```

## Workflows

```bash
acpx workflow review       # Code review
acpx workflow refactor     # Safe refactor
acpx workflow test         # Generate tests
acpx workflow debug        # Deep debugging
```

## Batch File Format

```
opencode exec 'Fix bug'
pi exec 'Create tests'
kimi --print --yolo --prompt 'Review'
```

## Spawn via OpenClaw

```javascript
// Health check
sessions_spawn(
  task="acpx health",
  label="health",
  runtime="subagent",
  mode="run"
)

// Workflow
sessions_spawn(
  task="acpx workflow review",
  label="review",
  runtime="subagent",
  mode="run"
)

// Parallel
sessions_spawn(
  task="acpx parallel tasks.txt",
  label="jobs",
  runtime="subagent",
  mode="run"
)
```

## Agents

- ACP: opencode, pi
- CLI: kimi, kilo, gemini
- PTY: codex, claude, cline
