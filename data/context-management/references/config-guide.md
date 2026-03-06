# OpenClaw Context Configuration Guide

All settings live in the OpenClaw config file. Run `gateway config.get` to find its path and current values.

## Compaction Settings

```json5
// config path: agents.defaults.compaction
{
  mode: "safeguard",           // Chunked summarisation — recommended
  reserveTokensFloor: 20000,   // Compact when this many tokens remain free
  memoryFlush: {
    enabled: true,              // Save state to disk before compaction
    softThresholdTokens: 10000  // Start flush this far from limit
  }
}
```

**`reserveTokensFloor`** is the most impactful setting.
Example for a 200k context window:
- `20000` (OpenClaw default): compaction at 90% — late, big summaries, death spiral risk
- `50000` (recommended): compaction at 75% — earlier, smaller summaries
- `60000` (aggressive): compaction at 70% — maximum headroom

Scale these values relative to your model's context window. The principle: higher floor = earlier compaction = smaller summaries = more headroom after.

## Pruning Settings

```json5
// config path: agents.defaults.contextPruning
{
  mode: "cache-ttl",           // Prune when cache TTL expires
  ttl: "5m",                   // Time since last API call before pruning
  keepLastAssistants: 2,       // Protect this many recent exchanges
  minPrunableToolChars: 50000, // Only trim results larger than this
  softTrim: {
    maxChars: 4000,            // Max trimmed output size
    headChars: 1500,           // Keep from start
    tailChars: 1500            // Keep from end
  },
  hardClear: {
    enabled: true,
    placeholder: "[Old tool result content cleared]"
  },
  tools: {
    deny: ["browser", "canvas"]  // Never prune these tools' results
  }
}
```

**Key tuning points:**
- `keepLastAssistants: 1` — most aggressive, only last exchange is safe
- `minPrunableToolChars: 10000` — catches medium results (default 50000 only catches huge ones)
- `ttl: "2m"` — prunes after shorter pauses (default 5m rarely fires during active work)

## Recommended Profiles

### Conservative (OpenClaw defaults, minimal intervention)
```json5
{ reserveTokensFloor: 20000, ttl: "5m", keepLastAssistants: 2 }
```
Late compaction, large summaries. Risk: death spiral after 3+ compactions.

### Balanced (recommended for most users)
```json5
{ reserveTokensFloor: 50000, ttl: "2m", keepLastAssistants: 1, minPrunableToolChars: 10000 }
```
Earlier compaction, more aggressive pruning. Good for mixed workloads.

### Aggressive (heavy tool users)
```json5
{ reserveTokensFloor: 60000, ttl: "1m", keepLastAssistants: 1, minPrunableToolChars: 5000 }
```
Maximum headroom. May need to re-read files after pruning clears them.

## Applying Changes

From within a session, use the `gateway` tool:
```
gateway config.patch with the JSON values to merge
```

From the command line:
```bash
# Edit the config file directly, then restart
nano <config_path>    # path from: gateway config.get
openclaw gateway restart
```

Always follow the full backup → rollback doc → explain → apply → confirm procedure in SKILL.md.
