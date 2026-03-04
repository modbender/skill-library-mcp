---
name: truetime
description: Ensure real-time accurate scheduling and planning across UTC, server time, NTP-sourced time, user local time, and arbitrary time zones. Use for timers, reminders, cron planning, in X minutes or months or years calculations, absolute timestamp conversion, Chinese lunar date awareness, and cross-timezone coordination. Enforce exact duration fidelity so user values are never replaced by example values, compute target times in UTC first, and verify deltas before execution.
---

# TrueTime

Use this skill to avoid time mistakes caused by stale examples, wrong units, timezone drift, or DST confusion.

## Non-Negotiable Rules

- Treat user-provided duration values as authoritative.
- Never copy numeric values from examples into real execution.
- Read current time from the runtime clock before calculating.
- Compute canonical target time in UTC first.
- Convert for display second (server timezone, user timezone, other timezone).
- Ask for clarification when timezone context is missing and outcome can change.

## Required Workflow

1. Extract timing intent exactly.
   - Capture literal phrase, value, unit, timezone hint, and target date/time.
   - Keep the original requested value unchanged (for example `1 minute` stays `1 minute`).
2. Read current real time.
   - Use the bundled script for deterministic calculations:
     - Relative: `node {baseDir}/scripts/true_time.mjs --plus 1m --user-tz Asia/Shanghai`
     - Relative (calendar units): `node {baseDir}/scripts/true_time.mjs --plus 1month2weeks --user-tz America/New_York --calendar-tz America/New_York`
     - Absolute: `node {baseDir}/scripts/true_time.mjs --target 2026-02-17T09:30:00 --target-tz Asia/Shanghai --user-tz America/Los_Angeles`
     - NTP time source: `node {baseDir}/scripts/true_time.mjs --plus 1h --time-source ntp`
3. Parse the expression into one precise delta or one precise absolute timestamp.
4. Compute UTC target first.
5. Convert UTC target to server/user/other requested timezone for presentation.
6. Verify the result before execution.
   - Confirm `target_utc - now_utc` equals requested delta.
   - Confirm timezone offset conversion is consistent.
7. Execute schedules using UTC unless the target scheduler explicitly needs local timezone.
8. Report both absolute and relative interpretation in the final response.

## Relative Time Guardrails

- Accept explicit units only:
  - milliseconds: `ms`, `msec`, `msecs`, `millisecond`, `milliseconds`
  - seconds: `s`, `sec`, `second`, `seconds`
  - minutes: `m`, `min`, `minute`, `minutes`
  - hours: `h`, `hr`, `hour`, `hours`
  - days: `d`, `day`, `days`
  - weeks: `w`, `week`, `weeks`
  - months: `mo`, `mon`, `month`, `months`
  - years: `y`, `yr`, `year`, `years`
  - decades: `decade`, `decades`
  - centuries: `century`, `centuries`
- Reject ambiguous units instead of guessing.
- All units support decimal values, including calendar units.
  - Examples: `1.5m`, `0.25h`, `2.5day`, `250.5ms`, `1.5month`, `0.1year`, `0.5decade`, `0.01century`.
  - Decimal separator `.` is preferred; `,` is accepted as input and normalized.
- Fixed-unit decimals are computed to millisecond precision.
- Calendar-unit policy:
  - `month/year/decade/century` are calendar-aware, not fixed seconds.
  - Calendar arithmetic uses `--calendar-tz` (fallback: user timezone -> server timezone).
  - Decimal calendar values are split into integer and fractional parts.
  - Integer months use calendar shift; fractional months use the shifted month length to compute milliseconds.
  - End-of-month handling clamps to the last valid day (for example Jan 31 + 1 month -> Feb 28/29).
- Keep verification examples explicit:
  - `1.5m = 90s`
  - `250ms = 0.25s`
  - `1m = 60s`
  - `1h30m = 5400s`
  - `2d = 172800s`
  - `1.5year = 18 months`
  - `1decade = 10 years`
  - `0.5decade = 5 years`
  - `1century = 100 years`
  - `0.01century = 1 year`

## Absolute Time Guardrails

- Prefer IANA timezone names (`Asia/Shanghai`, `America/Los_Angeles`, `UTC`).
- Avoid ambiguous abbreviations (`CST`, `IST`) unless user confirms meaning.
- If user gives a naive datetime with no timezone, ask once or apply an explicit assumption.
- For DST transition windows, state that the chosen timezone rules were applied.

## Timezone Catalog and Customization

- List all available runtime timezones:
  - `node {baseDir}/scripts/true_time.mjs --list-timezones`
- Filter common choices quickly:
  - `node {baseDir}/scripts/true_time.mjs --list-timezones | rg -i '^(UTC|Asia/(Shanghai|Tokyo|Kolkata)|America/(Los_Angeles|New_York)|Europe/(London|Paris|Berlin))$'`
- User custom timezone:
  - Accept any valid IANA timezone from `--list-timezones`.
  - Pass user timezone via `--user-tz <IANA>`.
  - If user timezone is unknown, ask before executing time-sensitive actions.

Common timezones to use in examples and user-facing confirmations:

- `UTC` (no DST)
- `Asia/Shanghai` (Beijing time, UTC+08:00, no DST)
- `Asia/Tokyo` (Tokyo time, UTC+09:00, no DST)
- `Asia/Kolkata` (India time, UTC+05:30, no DST)
- `America/Los_Angeles` (US West: PST UTC-08:00 / PDT UTC-07:00, DST applies)
- `America/New_York` (US East: EST UTC-05:00 / EDT UTC-04:00, DST applies)
- `America/Chicago` (US Central: CST UTC-06:00 / CDT UTC-05:00, DST applies)
- `America/Denver` (US Mountain: MST UTC-07:00 / MDT UTC-06:00, DST applies)
- `America/Phoenix` (Arizona: MST UTC-07:00, typically no DST)
- `America/Anchorage` (Alaska: AKST UTC-09:00 / AKDT UTC-08:00, DST applies)
- `Pacific/Honolulu` (Hawaii: HST UTC-10:00, no DST)
- `Europe/London` (UK: GMT UTC+00:00 / BST UTC+01:00, DST applies)
- `Europe/Paris` (CET UTC+01:00 / CEST UTC+02:00, DST applies)
- `Europe/Berlin` (CET UTC+01:00 / CEST UTC+02:00, DST applies)
- `Europe/Amsterdam` (CET UTC+01:00 / CEST UTC+02:00, DST applies)

## DST and Standard-Time Rules

- Never assume fixed offsets for DST regions (`America/*`, many `Europe/*`).
- Always compute with the actual target date, not "current offset."
- For DST fall-back overlaps (ambiguous local time), require explicit offset:
  - `2026-11-01T01:30:00` in `America/Los_Angeles` is ambiguous.
  - Ask user to choose `-07:00` (before fallback) or `-08:00` (after fallback), or provide explicit offset in `--target`.
- For DST spring-forward gaps (invalid local time), require correction:
  - `2026-03-08T02:30:00` in `America/Los_Angeles` does not exist.
  - Ask user to use a valid local time (for example `01:30` or `03:30`).
- Prefer explicit-offset absolute targets when DST risk is high:
  - `--target 2026-11-01T01:30:00-07:00`
  - `--target 2026-11-01T01:30:00-08:00`

## Chinese Lunar Calendar

- This tool outputs Chinese lunar datetime fields by default:
  - `lunar_timezone` (default `Asia/Shanghai`, configurable via `--lunar-tz`)
  - `now_lunar`
  - `target_lunar`
- Use these fields when the user asks for Chinese lunar context.
- For execution/scheduling, still use Gregorian UTC fields as canonical.
- If a user gives only lunar date text and no Gregorian equivalent, ask for confirmation or a Gregorian target before execution.

## Time Source Policy (Server vs NTP)

- Default time source is server clock (`--time-source server`).
- If user explicitly requests "do not use server time", switch to public NTP:
  - `--time-source ntp`
- Optional NTP controls:
  - `--ntp-server <host>` (repeatable or comma-separated)
  - `--ntp-timeout-ms <ms>`
- NTP mode example:
  - `node {baseDir}/scripts/true_time.mjs --plus 30m --time-source ntp --ntp-server time.google.com`
- If all NTP servers fail, stop and report failure instead of silently falling back to server time.

## Mandatory Integration Points

Use TrueTime calculations before any of the following:

- Cron operations (`cron add`, `cron update`, `cron wake`, `cron run`) when time or schedule is involved.
- Calendar operations (create/update events, convert invite times, multi-timezone meeting planning).
- Reminder operations (in X minutes/hours, tomorrow at HH:mm, next weekday, repeating reminders).
- Planning tasks that include ETA, deadline conversion, or cross-timezone commitments.

## Server Execution Policy

- Persist canonical time as UTC (`target_utc_iso` and optionally epoch seconds).
- Include human-facing fields for user timezone and server timezone.
- If the scheduler supports timezone-aware execution, pass timezone explicitly.
- If the scheduler only accepts UTC, keep execution in UTC and show converted local preview.
- Runtime note: this skill's helper script uses Node (`node .../true_time.mjs`).
- Sandbox note: default `openclaw-sandbox:bookworm-slim` may not include Node; use `openclaw-sandbox-common:bookworm-slim` or install Node in `agents.defaults.sandbox.docker.setupCommand`.

## High-Frequency Examples

Relative calculations:

- Beijing time, 1 minute later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1m --user-tz Asia/Shanghai`
- Beijing time, 1.5 minutes later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1.5m --user-tz Asia/Shanghai`
- Tokyo time, 250.5 milliseconds later:
  - `node {baseDir}/scripts/true_time.mjs --plus 250.5ms --user-tz Asia/Tokyo`
- Tokyo time, 90 minutes later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1h30m --user-tz Asia/Tokyo`
- US West time, 2 hours later:
  - `node {baseDir}/scripts/true_time.mjs --plus 2h --user-tz America/Los_Angeles`
- US East time, 45 minutes later:
  - `node {baseDir}/scripts/true_time.mjs --plus 45m --user-tz America/New_York`
- India time, 1 day later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1d --user-tz Asia/Kolkata`
- US Central, 1 month later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1month --user-tz America/Chicago --calendar-tz America/Chicago`
- US Central, 1.5 months later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1.5month --user-tz America/Chicago --calendar-tz America/Chicago`
- US Mountain, 1 year later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1year --user-tz America/Denver --calendar-tz America/Denver`
- US Mountain, 0.1 years later:
  - `node {baseDir}/scripts/true_time.mjs --plus 0.1year --user-tz America/Denver --calendar-tz America/Denver`
- Hawaii, 1 decade later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1decade --user-tz Pacific/Honolulu --calendar-tz Pacific/Honolulu`
- Hawaii, 0.5 decades later:
  - `node {baseDir}/scripts/true_time.mjs --plus 0.5decade --user-tz Pacific/Honolulu --calendar-tz Pacific/Honolulu`
- UTC, 1 century later:
  - `node {baseDir}/scripts/true_time.mjs --plus 1century --user-tz UTC --calendar-tz UTC`
- UTC, 0.01 centuries later:
  - `node {baseDir}/scripts/true_time.mjs --plus 0.01century --user-tz UTC --calendar-tz UTC`

Absolute and cross-timezone calculations:

- Beijing local absolute time:
  - `node {baseDir}/scripts/true_time.mjs --target 2026-02-18T09:00:00 --target-tz Asia/Shanghai --user-tz Asia/Shanghai`
- London meeting shown to US East:
  - `node {baseDir}/scripts/true_time.mjs --target 2026-05-20T14:00:00 --target-tz Europe/London --user-tz America/New_York`
- UTC target shown to Europe/Berlin:
  - `node {baseDir}/scripts/true_time.mjs --target 2026-04-15T16:00:00Z --user-tz Europe/Berlin`
- DST ambiguity resolved by explicit offset:
  - `node {baseDir}/scripts/true_time.mjs --target 2026-11-01T01:30:00-07:00 --user-tz America/Los_Angeles`
  - `node {baseDir}/scripts/true_time.mjs --target 2026-11-01T01:30:00-08:00 --user-tz America/Los_Angeles`
- NTP-based reminder time:
  - `node {baseDir}/scripts/true_time.mjs --plus 15m --time-source ntp --user-tz Asia/Shanghai`

## Output Contract

When sending or scheduling time-sensitive actions, always include:

- `now_utc`
- `target_utc`
- `target_user_tz` (if known)
- `target_server_tz`
- `delta_milliseconds`
- `delta_seconds`
- `time_source` (server | ntp | override)
- `ntp_server` (when `time_source=ntp`)
- `now_lunar`
- `target_lunar`
- assumptions (if any)

Do not continue with execution when any required field is unknown and may change the target time materially.
