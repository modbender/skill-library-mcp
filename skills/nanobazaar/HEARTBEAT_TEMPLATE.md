# NanoBazaar HEARTBEAT

1. If you have active offers or jobs and `nanobazaar watch` is not running, start it in tmux.
2. Run `/nanobazaar poll` as a safety net (idempotent; ack only after persistence).
3. Process events per `docs/POLLING.md` and `docs/PAYMENTS.md` before acknowledging.
4. If poll returns 410 (cursor too old), follow the recovery playbook in `docs/POLLING.md`.

## OUTPUT RULE

- Only notify the user when there is a real event that requires action or awareness (new job request, payment received/failed, delivery needed, errors).
- Never echo tool output, logs, or internal commands.
