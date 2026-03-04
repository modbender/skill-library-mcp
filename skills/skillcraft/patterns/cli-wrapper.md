# CLI Wrapper Pattern

Wrap a CLI tool for use through OpenClaw.

## OpenClaw-Specific Concerns

### Channel-Aware Output
Output goes to surfaces with different capabilities. Some channels lack markdown tables, long output may need summarising, rich formatting varies. Check `/providers/` docs for the target channel.

### Execution
Use `exec` tool. Always set timeouts (hung CLIs block the agent). For long-running commands, use background mode + `process` tool to poll.

### Scheduled Execution
Use OpenClaw's `cron` tool for periodic runs. Document the cron prompt text and expected behaviour in SKILL.md.

### Heavy Work
Use `sessions_spawn` for output-heavy or long-running operations. Include path context if the subagent needs workspace files (sandbox mounts differ).

### Results Delivery
Use `message` tool to push results to specific channels when completing background work.

### User Preferences
Store user-specific defaults in `<workspace>/TOOLS.md` under a section for the tool.

## State

CLI wrappers are usually stateless. Exceptions:
- **Auth tokens** that expire → `{baseDir}/state.json`
- **Incremental sync** → track last-sync timestamp
- **Rate limits** → remember reset time

## Checklist

- [ ] Timeouts set for all exec calls
- [ ] Output formatting considers channel constraints
- [ ] Cron integration documented (if periodic)
- [ ] Heavy operations spawn subagents
- [ ] User preferences location documented
- [ ] State paths use `{baseDir}/` or `<workspace>/`, never `~/`
- [ ] Subagent path context documented if applicable
