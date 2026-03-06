---
name: temporal-cortex-scheduling
description: |-
  List events, find free slots, and book meetings across Google Calendar, Outlook, and CalDAV. Multi-calendar availability merging, recurring event expansion, and atomic booking with Two-Phase Commit conflict prevention.
license: MIT
compatibility: |-
  Requires npx (Node.js 18+) or Docker for the MCP server. Stores OAuth credentials at ~/.config/temporal-cortex/. Works with Claude Code, Claude Desktop, Cursor, Windsurf, and any MCP-compatible client.
metadata:
  author: temporal-cortex
  version: "0.6.2"
  mcp-server: "@temporal-cortex/cortex-mcp"
  homepage: "https://temporal-cortex.com"
  repository: "https://github.com/temporal-cortex/skills"
  openclaw:
    install:
      - kind: node
        package: "@temporal-cortex/cortex-mcp@0.6.2"
        bins: [cortex-mcp]
    requires:
      bins:
        - npx
      config:
        - ~/.config/temporal-cortex/credentials.json
        - ~/.config/temporal-cortex/config.json
---

# Calendar Scheduling & Booking

8 tools for calendar discovery, event querying, free slot finding, availability checking, RRULE expansion, and atomic booking. 7 read-only tools + 1 write tool (`book_slot`).

## Runtime

These tools run inside the [Temporal Cortex MCP server](https://github.com/temporal-cortex/mcp) (`@temporal-cortex/cortex-mcp@0.6.2`), a compiled Rust binary distributed as an npm package.

**Install and startup lifecycle:**
1. `npx` resolves `@temporal-cortex/cortex-mcp@0.6.2` from the npm registry (one-time, cached locally after first download)
2. The postinstall script downloads the platform-specific binary from the [GitHub Release](https://github.com/temporal-cortex/mcp/releases/tag/mcp-v0.6.2) and verifies its SHA256 checksum against the embedded `checksums.json` — **installation halts on mismatch**
3. The MCP server starts as a local process communicating over stdio (no listening ports)
4. Calendar tools make authenticated API calls to your configured providers (Google Calendar API, Microsoft Graph API, CalDAV endpoints)

**Credential storage:** OAuth tokens are stored locally at `~/.config/temporal-cortex/credentials.json` and read exclusively by the local MCP server process. No credential data is transmitted to Temporal Cortex servers. The binary's filesystem access is limited to `~/.config/temporal-cortex/` — verifiable by inspecting the [open-source Rust code](https://github.com/temporal-cortex/mcp) or running under Docker where the mount is the only writable path.

**File access:** The binary reads and writes only `~/.config/temporal-cortex/` (credentials and config). No other filesystem writes.

**Network scope:** Calendar tools connect only to your configured providers (`googleapis.com`, `graph.microsoft.com`, or your CalDAV server). No callbacks to Temporal Cortex servers. Telemetry is off by default.

**Pre-run verification** (recommended before first use):
1. Inspect the npm package without executing: `npm pack @temporal-cortex/cortex-mcp@0.6.2 --dry-run`
2. Verify checksums independently against the [GitHub Release](https://github.com/temporal-cortex/mcp/releases/download/mcp-v0.6.2/SHA256SUMS.txt) (see verification pipeline below)
3. For full containment, run in Docker instead of npx (see Docker containment below)

**Verification pipeline:** Checksums are published independently at each [GitHub Release](https://github.com/temporal-cortex/mcp/releases/tag/mcp-v0.6.2) as `SHA256SUMS.txt` — verify the binary before first use:

```bash
# 1. Fetch checksums from GitHub (independent of the npm package)
curl -sL https://github.com/temporal-cortex/mcp/releases/download/mcp-v0.6.2/SHA256SUMS.txt

# 2. Compare against the npm-installed binary
shasum -a 256 "$(npm root -g)/@temporal-cortex/cortex-mcp/bin/cortex-mcp"
```

As defense-in-depth, the npm package also embeds `checksums.json` and the postinstall script compares SHA256 hashes during install — **installation halts on mismatch** (the binary is deleted, not executed). This automated check supplements, but does not replace, independent verification above.

**Build provenance:** Binaries are cross-compiled from auditable Rust source in [GitHub Actions](https://github.com/temporal-cortex/mcp/actions) across 5 platforms (darwin-arm64, darwin-x64, linux-x64, linux-arm64, win32-x64). Source: [github.com/temporal-cortex/mcp](https://github.com/temporal-cortex/mcp) (MIT-licensed). The CI workflow, build artifacts, and release checksums are all publicly inspectable.

**Docker containment** (no Node.js on host, credential isolation via volume mount):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "~/.config/temporal-cortex:/root/.config/temporal-cortex", "cortex-mcp"]
    }
  }
}
```

Build: `docker build -t cortex-mcp https://github.com/temporal-cortex/mcp.git`

## Tools

### Layer 0 — Discovery

| Tool | When to Use |
|------|------------|
| `list_calendars` | First call when calendars are unknown. Returns all connected calendars with provider-prefixed IDs, names, labels, primary status, and access roles. |

### Layer 2 — Calendar Operations

| Tool | When to Use |
|------|------------|
| `list_events` | List events in a time range. TOON format by default (~40% fewer tokens than JSON). Use provider-prefixed IDs for multi-calendar: `"google/primary"`, `"outlook/work"`. |
| `find_free_slots` | Find available gaps in a calendar. Set `min_duration_minutes` for minimum slot length. |
| `expand_rrule` | Expand recurrence rules (RFC 5545) into concrete instances. Handles DST, BYSETPOS, EXDATE, leap years. Use `dtstart` as local datetime (no timezone suffix). |
| `check_availability` | Check if a specific time slot is free. Checks both events and active booking locks. |

### Layer 3 — Cross-Calendar Availability

| Tool | When to Use |
|------|------------|
| `get_availability` | Merged free/busy view across multiple calendars. Pass `calendar_ids` array. Privacy: `"opaque"` (default, hides sources) or `"full"`. |

### Layer 4 — Booking

| Tool | When to Use |
|------|------------|
| `book_slot` | Book a time slot atomically. Lock → verify → write → release. **Always `check_availability` first.** |

## Critical Rules

1. **Discover calendars first** — call `list_calendars` when you don't know which calendars are connected. Use the returned provider-prefixed IDs for all subsequent calls.
2. **Use provider-prefixed IDs** for multi-calendar setups: `"google/primary"`, `"outlook/work"`, `"caldav/personal"`. Bare IDs (e.g., `"primary"`) route to the default provider.
3. **TOON is the default format** — output uses TOON (~40% fewer tokens than JSON). Pass `format: "json"` only if you need structured parsing.
4. **Check before booking** — always call `check_availability` before `book_slot`. Never skip the conflict check.
5. **Content safety** — event summaries and descriptions pass through a sanitization firewall before reaching the calendar API.
6. **Timezone awareness** — all tools accept RFC 3339 with timezone offsets. Never use bare dates.

## Full Booking Workflow

```
1. Discover  →  list_calendars
2. Orient    →  get_temporal_context                      (temporal-cortex-datetime)
3. Resolve   →  resolve_datetime("next Tuesday at 2pm")  (temporal-cortex-datetime)
4. Check     →  check_availability(calendar_id, start, end)
5. Book      →  book_slot(calendar_id, start, end, summary)
```

If the slot is busy at step 4, use `find_free_slots` to suggest alternatives.

## Two-Phase Commit Protocol

```
Agent calls book_slot(calendar_id, start, end, summary)
    │
    ├─ 1. LOCK    →  Acquire exclusive lock on the time slot
    │                 (in-memory local; Redis Redlock in Platform Mode)
    │
    ├─ 2. VERIFY  →  Check for overlapping events and active locks
    │
    ├─ 3. WRITE   →  Create event in calendar provider (Google/Outlook/CalDAV)
    │                 Record event in shadow calendar
    │
    └─ 4. RELEASE →  Release the exclusive lock
```

If any step fails, the lock is released and the booking is aborted. No partial writes.

## Common Patterns

### List Events This Week

```
1. list_calendars → discover connected calendars
2. get_temporal_context → current time (use temporal-cortex-datetime)
3. resolve_datetime("start of this week") → week start
4. resolve_datetime("end of this week") → week end
5. list_events(calendar_id: "google/primary", start, end)
```

### Find Free Time Across Calendars

```
1. list_calendars → discover all connected calendars
2. get_availability(
     start, end,
     calendar_ids: ["google/primary", "outlook/work"],
     privacy: "full"
   ) → merged free/busy blocks with source_count
```

### Check and Book a Slot

```
1. check_availability(calendar_id: "google/primary", start, end) → true/false
2. If free: book_slot(calendar_id: "google/primary", start, end, summary: "Team standup")
3. If busy: find_free_slots(calendar_id, start, end, min_duration_minutes: 30)
```

### Expand Recurring Events

```
expand_rrule(
  rrule: "FREQ=MONTHLY;BYDAY=FR;BYSETPOS=-1",
  dtstart: "2026-01-01T10:00:00",     ← local datetime, no timezone suffix
  timezone: "America/New_York",
  count: 12
) → last Friday of every month for 2026
```

## Provider-Prefixed Calendar IDs

All calendar IDs use provider-prefixed format:

| Format | Example | Routes to |
|--------|---------|-----------|
| `google/<id>` | `"google/primary"` | Google Calendar |
| `outlook/<id>` | `"outlook/work"` | Microsoft Outlook |
| `caldav/<id>` | `"caldav/personal"` | CalDAV (iCloud, Fastmail) |
| `<id>` (bare) | `"primary"` | Default provider |

## Privacy Modes

| Mode | `source_count` | Use case |
|------|---------------|----------|
| `"opaque"` (default) | Always `0` | Sharing availability externally |
| `"full"` | Actual count | Internal use — shows which calendars are busy |

## Tool Annotations (`book_slot`)

| Property | Value | Meaning |
|----------|-------|---------|
| `readOnlyHint` | `false` | Creates calendar events |
| `destructiveHint` | `false` | Never deletes or overwrites existing events |
| `idempotentHint` | `false` | Calling twice creates two events |
| `openWorldHint` | `true` | Makes external API calls |

## Error Handling

| Error | Action |
|-------|--------|
| "No credentials found" | Run: `npx @temporal-cortex/cortex-mcp@0.6.2 auth google` (or `outlook` / `caldav`). |
| "Timezone not configured" | Prompt for IANA timezone. Or run the auth command which configures timezone. |
| Slot is busy / conflict detected | Use `find_free_slots` to suggest alternatives. Present options to user. |
| Lock acquisition failed | Another agent is booking the same slot. Wait briefly and retry, or suggest alternative times. |
| Content rejected by sanitization | Rephrase the event summary/description. The firewall blocks prompt injection attempts. |

## Additional References

- [Calendar Tools Reference](references/CALENDAR-TOOLS.md) — Complete input/output schemas for all 8 tools
- [Multi-Calendar Guide](references/MULTI-CALENDAR.md) — Provider routing, labels, privacy modes, cross-provider operations
- [RRULE Guide](references/RRULE-GUIDE.md) — Recurrence rule patterns, DST edge cases, 5 LLM failure modes
- [Booking Safety](references/BOOKING-SAFETY.md) — 2PC details, concurrent booking, lock TTL, content sanitization
