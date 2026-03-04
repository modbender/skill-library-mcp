###### WIP Computer
# wip-file-guard ... Reference

Manual install instructions, CLI usage, and customization.

## Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node \"/path/to/wip-file-guard/guard.mjs\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Replace `/path/to/wip-file-guard/` with where you cloned the repo.

## OpenClaw

Add to your OpenClaw installation's `extensions/` directory:

```bash
cp -r wip-file-guard ~/.openclaw/extensions/wip-file-guard
```

The `openclaw.plugin.json` registers a `before_tool_use` lifecycle hook that applies the same rules.

## CLI

```bash
# List protected files
node guard.mjs --list

# Test the guard with a simulated input
echo '{"tool_name":"Write","tool_input":{"file_path":"/foo/CLAUDE.md"}}' | node guard.mjs

# Run the test suite
bash test.sh
```

## Customization

### Adding Protected Files

Edit the `PROTECTED` set in `guard.mjs`:

```javascript
const PROTECTED = new Set([
  'CLAUDE.md',
  'SHARED-CONTEXT.md',
  'SOUL.md',
  'IDENTITY.md',
  'CONTEXT.md',
  'TOOLS.md',
  'MEMORY.md',
  'YOUR-FILE-HERE.md',   // add yours
]);
```

### Changing the Line Threshold

The default blocks edits that remove more than 2 net lines. Change the threshold in the Edit handler:

```javascript
if (removed > 2) {   // change 2 to your threshold
```
