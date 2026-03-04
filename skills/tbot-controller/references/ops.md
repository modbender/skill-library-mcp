# TBOT Controller references

This folder is optional. It exists to give humans (and agents) a place to look up details without cluttering `SKILL.md`.

## Reference runtime implementation

This skill controls an **external TBOT runtime stack**. One reference implementation (Docker Compose-based) is:

- https://github.com/PlusGenie/openclaw-on-tradingboat

This link is provided as a **reference implementation**, not a hard requirement. Any compatible runtime stack that satisfies the expectations below is acceptable.

## Runtime expectations (summary)

- A TBOT runtime stack must already be running *or* startable by the user (e.g., Docker Compose or systemd).
- This skill **does not** install TBOT, start Docker, or create/migrate databases automatically.
- The preferred “source of truth” is the TBOT SQLite database (read-only by default).

## Safety expectations

- Any state-changing operation requires `--run-it` (or `RUN_IT=1`).
- If paper vs live is unclear, the agent must refuse to execute control or trading actions until the user confirms.

## Database note

The SQLite DB location varies by deployment. This skill supports:
- explicit `--db-path`
- `TBOT_DB_PATH`
- `TBOT_DB_OFFICE`

Bind-mounting the DB to the host is recommended so that DB inspection does not require shell access inside containers.
