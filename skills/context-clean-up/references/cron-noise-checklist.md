# Cron noise checklist

Use this checklist to decide whether a cron job should write text back into the interactive session.

## Good candidates for `NO_REPLY`

- Heartbeat / liveness checks where the success case is boring
- Harvesters / ledger updaters / sync jobs
- File initializers
- Cache warmers

## Bad candidates for `NO_REPLY` (unless you do out-of-band delivery)

- Reports the user explicitly wants to read
- Anything that needs a human decision

## Heuristics

- If a job runs more often than every 30 minutes, be extremely strict about output size.
- If a job is `sessionTarget="isolated"`, treat its output as a **side effect** that should not pollute the main chat.
- Prefer a 3-layer output:
  1) short message (user)
  2) detailed artifact saved to file
  3) optional follow-up only on anomalies

## Safe patching rule

Always preserve behavior:
- create backups before editing files
- for cron jobs, modify only the final output instructions first
- verify the next run before making deeper changes
