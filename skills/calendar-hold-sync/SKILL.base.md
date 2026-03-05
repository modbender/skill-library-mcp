# Calendar Hold Sync

Implement hold mirroring from source Google calendars into target calendars to prevent double-booking.

## Dependency

- Require `gog` CLI in `PATH`.
- Require user OAuth already configured for each account used in `mappings`.
- Do not hardcode account emails, calendar IDs, or event IDs in code.

If `gog` is not configured, use this setup flow:

1. Run `gog auth credentials /path/to/client_secret.json`.
2. Run `gog auth add you@gmail.com --services calendar`.
3. Verify with `gog auth list`.

Only add additional Google services if you explicitly need them for another workflow.

Official `gog` references:

- Homepage: https://gogcli.sh/
- Source: https://github.com/steipete/gogcli

## Config Contract

Use a user-provided JSON config file with this shape:

- `mappings[]`
- `mappings[].name`
- `mappings[].targetAccount`
- `mappings[].targetCalendarId` (default `primary`)
- `mappings[].sources[]` with `{ account, calendarId }`
- `mappings[].lookaheadDays` (default `30`)
- `mappings[].allDayMode`: `ignore|mirror`
- `mappings[].overlapPolicy`: `skip|allow`
- `hold.summary` (default `Busy`)
- `hold.visibility` (`private`)
- `hold.transparency` (`busy`)
- `hold.notifications` (`none`)
- `hold.reminders` (`none`)
- `metadata.format` (`SYNCV1`)
- `metadata.encoding` (`base64url(json)`)
- `metadata.fields`: `srcAccount,srcCalendar,eventId,start,end,title`
- `scheduling.reconcileCron`
- `scheduling.daytimeCron` (optional)
- `scheduling.driftWindowDays` (optional)
- `scheduling.watchIntervalSeconds` (optional, default `20`)
- `safety.dryRun`
- `safety.maxChangesPerRun`
- `safety.excludeIfSummaryMatches[]`
- `safety.excludeIfDescriptionPrefix[]`
- `gog.listEventsCmd|createEventCmd|updateEventCmd|deleteEventCmd` (optional template overrides)
- `gog.allowCustomCommands` (must be `true` to enable any `gog.*Cmd` override)

## Custom Command Template Safety

When custom commands are enabled:

- Only `gog` command templates are accepted.
- Templates are rendered by replacing placeholders like `{account}` and `{calendarId}`.
- Rendered commands are executed as argv tokens (no shell interpolation).
- Keep `gog.allowCustomCommands=false` unless you fully trust and audit the config file.

## Metadata Encoding

Store source linkage in hold `description` as:

- `SYNCV1:<base64url(JSON)>`

JSON fields:

- `srcAccount`
- `srcCalendar`
- `eventId`
- `start`
- `end`
- `title`

## Behavior

For each mapping:

1. Read source events in the active window.
2. Build desired hold events (`private`, `busy`, no reminders).
3. Detect existing managed holds by `SYNCV1:` prefix.
4. Reconcile idempotently:
- Create missing holds.
- Update drifted holds.
- Delete stale holds.
5. If overlap policy is `skip`, do not create a hold when a non-managed target event overlaps.
6. Enforce `maxChangesPerRun`.
7. Respect `dryRun`.

## Backfill

Backfill mode upgrades legacy hold events (matching expected hold signature but lacking `SYNCV1`) by attaching encoded metadata when a unique source match exists.

## Command Surface

- `hold-sync validate-config`
- `hold-sync reconcile --mapping <name>|--all [--dry-run]`
- `hold-sync backfill --mapping <name>|--all [--dry-run]`
- `hold-sync status --mapping <name>|--all`
- `hold-sync install-cron --mapping <name>|--all`
- `hold-sync watch --mapping <name>|--all [--dry-run] [--interval-seconds <n>]`

## Watch Cadence

Require watch cadence to be configurable from user config:

- `scheduling.watchIntervalSeconds` controls watch poll frequency.
- `mappings[].lookaheadDays` controls rolling watch/reconcile window.

Recommend baseline values:

- `watchIntervalSeconds: 900` (15 minutes)
- `lookaheadDays: 1` (24 hours)

## Working Model

- Use polling-based watch mode (`hold-sync watch`) for fast updates.
- Expect update latency approximately equal to `watchIntervalSeconds`.
- Treat this as self-hosted/operator-run automation.

## Known Limits

- Do not assume webhook/push subscriptions are present; current fast sync path is polling.
- Keep periodic scheduled reconcile as fallback even when watch mode is enabled.

## Required Tests

- metadata encode/decode round-trip
- overlap detection correctness
- idempotent reconcile upsert/delete behavior

Attribution: `gog` setup flow adapted from:
- https://clawhub.ai/steipete/gog
- https://github.com/steipete/gogcli
- https://gogcli.sh/
