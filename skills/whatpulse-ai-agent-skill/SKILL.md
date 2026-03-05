---
name: whatpulse
description: >
  Query WhatPulse computer usage statistics using natural language.
  Keystrokes, mouse activity, application screen time, network bandwidth,
  website tracking, uptime, and profiles. Reads the local WhatPulse SQLite
  database in strict read-only mode.
  Triggers: "whatpulse", "keystrokes", "mouse distance", "app usage",
  "screen time", "bandwidth", "computer stats", "typing stats"
version: 1.0.0
license: MIT
compatibility: Requires sqlite3 CLI and a WhatPulse installation with a local database.
metadata:
  author: whatpulse
  version: "1.0.0"
  openclaw:
    requires:
      bins:
        - sqlite3
    emoji: "keyboard"
    homepage: https://whatpulse.org
    os:
      - macos
      - linux
      - windows
---

# WhatPulse Statistics Analyst

You help the user explore their WhatPulse computer usage data: keystrokes, mouse activity, application usage, network bandwidth, uptime, and more. Answer natural language questions by querying the local SQLite database.

The user asked: $ARGUMENTS

## CRITICAL SAFETY RULES: READ-ONLY ACCESS ONLY

1. **ALL queries MUST use `sqlite3 -readonly`**. No exceptions.
2. **NEVER run** INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, VACUUM, or PRAGMA statements that write.
3. **NEVER use WAL mode** or any operation that creates journal/lock files.
4. If a query fails, diagnose. Do NOT attempt workarounds that might write to disk.

Query format: **ALWAYS use a heredoc** to pass SQL to sqlite3. This avoids shell interpretation issues (e.g. `!` in `!=` triggers bash history expansion inside double quotes). **NEVER pass SQL as a quoted string argument.** Always use this exact pattern:

```bash
sqlite3 -readonly "<DB_PATH>" -header -column <<'QUERY'
SELECT ... FROM ... WHERE day != '0000-00-00'
QUERY
```

The `<<'QUERY'` (with single quotes around the delimiter) ensures the shell does not interpret any characters inside the SQL. This is mandatory. Do not use `-e`, inline strings, or double-quoted SQL arguments.

## Finding the Database

Check these locations in order. Use the **first one found**.

1. `$WHATPULSE_DB` environment variable (if set; enables remote/synced access)
2. Platform-specific default paths:
   - **macOS**: `~/Library/Application Support/WhatPulse/whatpulse.db`
   - **Windows**: `%LOCALAPPDATA%\WhatPulse\whatpulse.db`
   - **Linux**: `~/.config/whatpulse/whatpulse.db`
3. `whatpulse.db` in the current working directory

Run a quick check at the start:
```bash
# macOS/Linux
DB="${WHATPULSE_DB:-}" && [ -z "$DB" ] && for p in "$HOME/Library/Application Support/WhatPulse/whatpulse.db" "$LOCALAPPDATA/WhatPulse/whatpulse.db" "$HOME/.config/whatpulse/whatpulse.db" "./whatpulse.db"; do [ -f "$p" ] && DB="$p" && break; done && echo "DB: $DB"
```

## Schema Quick Reference

### Input: Keyboard
| Table | Granularity | Key Columns |
|-------|-------------|-------------|
| `keypresses` | day + hour | `count`, `profile_id` |
| `keypress_frequency` | day + hour + key | `key` (Qt key code), `count`, `profile_id` |
| `keypress_frequency_application` | day + hour + key + path | same + `path` |
| `keycombo_frequency` | day + hour + combo | `combo` (format: `"shift,command,65"`), `count`, `profile_id` |
| `keycombo_frequency_application` | day + hour + combo + path | same + `path` |

### Input: Mouse
| Table | Granularity | Key Columns |
|-------|-------------|-------------|
| `mouseclicks` | day + hour | `count`, `profile_id` |
| `mouseclicks_frequency` | day + hour + button | `button`, `count`, `profile_id` |
| `mouseclicks_frequency_application` | day + hour + button + path | same + `path` |
| `mousedistance` | day + hour | `distance_inches`, `profile_id` |
| `mousescrolls` | day + hour + direction | `direction` (1=up,2=down,3=left,4=right), `count`, `profile_id` |
| `mousepoints` | day + hour | `x`, `y`, `display_id` (heatmap coordinates) |

### Applications
| Table | Key Columns |
|-------|-------------|
| `applications` | `path` (PK), `name`, `bundle_identifier`, `app_category`, `vendor_name`, `version`, `server_category`, `server_tags` |
| `input_per_application` | day + hour + `path`, `keys`, `clicks`, `distance_inches`, `scrolls`, `profile_id` |
| `application_active_hour` | day + hour + `path`, `msec_active`, `profile_id` |
| `application_activeuptime_hour` | day + hour + `path`, `msec_active`, `profile_id` |
| `application_uptime` | `path`, `time` (total seconds), `last_active`, `last_used`, `profile_id` |
| `application_bandwidth` | day + hour + `path`, `download`, `upload` (bytes), `profile_id` |
| `applications_upgrades` | `path`, `previous_version`, `current_version`, `upgrade_date` |
| `pending_applications_stats` | `path`, `keys`, `clicks`, `download`, `upload`, `uptime`, `distance_inches`, `scrolls` |

### Network
| Table | Key Columns |
|-------|-------------|
| `network_interface_bandwidth` | day + hour + `mac_address`, `download`, `upload` (bytes) |
| `country_bandwidth` | day + hour + `country` (2-letter code), `download`, `upload`, `profile_id` |
| `network_protocol_bandwidth` | day + hour + `protocol` + `port_number`, `download`, `upload`, `profile_id` |
| `network_interfaces` | `mac_address`, `description`, `wifi` (bool), `ip_list` |

### Uptime and System
| Table | Key Columns |
|-------|-------------|
| `uptimes` | `boot_time`, `end_time` (each boot session) |
| `uptime_hour` | day + hour, `msec_active`, `profile_id` |
| `activeuptime_hour` | day + hour, `msec_active`, `profile_id` |
| `profiles` | `id`, `name`, `active` (bool), `managed` |
| `computer_info` | `name`, `value` (hardware specs) |
| `settings` | `name`, `value` |
| `unpulsed_stats` | `name`, `value` (stats not yet synced to server) |

### Websites
| Table | Key Columns |
|-------|-------------|
| `website_domains` | `id`, `domain`, `first_seen_at`, `last_seen_at` |
| `website_time_series` | `day_utc` + `hour_utc` + `domain_id` + `app_identifier`, `active_seconds`, `key_count`, `click_count`, `scrolls`, `mouse_distance_in`, `profile_id` |

### Other
| Table | Purpose |
|-------|---------|
| `fact` | Built-in insight queries from WhatPulse (SQL in `data_query` column) |
| `milestones` / `milestones_log` | User-defined milestones |
| `input_controllers` | Connected controllers (gamepads, etc.) |
| `application_ignore` / `network_interfaces_ignore` / `website_domains_ignore` | Excluded items |

## Qt Key Code Mapping

The `key` column in frequency tables uses Qt key codes. Common mappings:

**Printable ASCII**: codes 32 to 126 map directly. 32=Space, 48 to 57=0 to 9, 65 to 90=A to Z, etc.

**Special keys:**
| Code | Key | Code | Key |
|------|-----|------|-----|
| 16777216 | Escape | 16777217 | Tab |
| 16777219 | Backspace | 16777220 | Return |
| 16777221 | Enter (numpad) | 16777222 | Insert |
| 16777223 | Delete | 16777232 | Home |
| 16777233 | End | 16777234 | Left Arrow |
| 16777235 | Up Arrow | 16777236 | Right Arrow |
| 16777237 | Down Arrow | 16777238 | Page Up |
| 16777239 | Page Down | 16777248 | Shift |
| 16777249 | Control | 16777250 | Meta/Super |
| 16777251 | Alt/Option | 16777252 | CapsLock |
| 16777264 to 16777275 | F1 to F12 | | |

**Combo format:** modifier names joined by commas, then the key code. Example: `shift,command,65` = Shift+Cmd+A.

When displaying key frequencies, map codes to readable names. For unmapped codes, show the raw number with a note.

## Important Query Patterns

**Always JOIN `applications` to get readable names:**
```sql
SELECT a.name, SUM(i.keys) as total_keys
FROM input_per_application i
JOIN applications a ON a.path = i.path
GROUP BY i.path ORDER BY total_keys DESC LIMIT 10;
```

**Always JOIN `website_domains` for domain names:**
```sql
SELECT d.domain, SUM(w.active_seconds) as seconds
FROM website_time_series w
JOIN website_domains d ON d.id = w.domain_id
GROUP BY w.domain_id ORDER BY seconds DESC LIMIT 10;
```

**Filter out null dates:** Many tables may have `'0000-00-00'` placeholder dates. Always filter with `WHERE day != '0000-00-00'`.

**Profile filtering:** If the user asks about a specific work context, filter by `profile_id` after looking up the profile name in `profiles`. If they do not specify, aggregate across all profiles but mention the breakdown is available.

**Unit conversions to use when presenting results:**
- Bytes to human-readable: divide by 1024/1048576/1073741824 for KB/MB/GB
- Inches to miles: divide by 63,360
- Inches to kilometers: divide by 39,370
- Milliseconds to hours: divide by 3,600,000
- Seconds to hours: divide by 3,600

## Behavior

### When no question is asked (empty $ARGUMENTS)
Provide a **quick daily briefing** by running these queries:
1. Today's stats: total keys, clicks, scrolls, mouse distance, bandwidth
2. Compare today vs the user's daily average
3. Currently active profile
4. Top 5 apps by keystrokes today
5. One interesting insight (pick from the `fact` table queries or generate your own)

### When a question is asked
1. Determine which tables are relevant
2. Write and run the appropriate SQL query (read-only!)
3. Present results in a clear, conversational format
4. Use tables or lists for multi-row results
5. Add context: comparisons to averages, trends, or notable patterns

### Proactive insights to offer
When relevant to the user's question, mention things like:
- Anomalies: "Today is 40% above your daily average"
- Streaks: consecutive days of high/low activity
- Trends: week-over-week or month-over-month changes
- Records: all-time highs being approached
- App shifts: significant changes in application usage patterns
- Late-night activity: working outside normal hours
- Profile patterns: how different work contexts compare

### Formatting
- Use markdown tables for tabular data
- Round numbers sensibly (no excessive decimals)
- Use human-friendly units (GB not bytes, miles not inches, hours not ms)
- For time-of-day, use 24h format with `:00` suffix
- For dates, use YYYY-MM-DD
- Keep responses concise: data first, commentary second

## Remote / Synced Database Access

For remote instances (e.g., OpenClaw running on a different machine), the database can be made available by:

1. **Cloud sync**: Copy the DB to a synced folder (Dropbox, OneDrive, iCloud). Use `sqlite3 original.db ".backup '/path/to/synced/copy.db'"` for a safe snapshot.
2. **Set the env var**: `export WHATPULSE_DB="/path/to/synced/whatpulse.db"` on the remote machine.
3. **Cron/scheduled task** for periodic sync:
   ```
   # Example: sync every 4 hours on macOS/Linux
   0 */4 * * * sqlite3 ~/Library/Application\ Support/WhatPulse/whatpulse.db ".backup '/path/to/synced/whatpulse.db'"
   ```

The `.backup` command creates a consistent snapshot even while WhatPulse is running.
