# quick-reminders (OpenClaw Skill)

Zero-LLM one-shot reminders delivered via `openclaw message send`. The agent composes the reminder text **at creation time**; at fire time a background process sends it with no LLM invocation — zero tokens consumed on delivery.

Uses `nohup sleep` under the hood, so it's lightweight and doesn't require external schedulers.

Recommended for short-horizon reminders (typically under 48 hours).

---

## Requirements

* `jq` — install via `brew install jq` (macOS) or your package manager
* `openclaw` CLI in PATH (ships with any OpenClaw install)

---

## How it works

1. User asks: "Remind me to X in Y minutes."
2. Agent composes a natural-language reminder message and calls the CLI script.
3. The script spawns a detached `nohup sleep <seconds> && openclaw message send ...` process.
4. When the timer fires, the message is delivered and the reminder auto-cleans from the tracking file.

All state is stored in `./reminders.json` (workspace root) — one JSON array of active reminders with IDs, PIDs, text, and fire times.

---

## Setup

Add your preferred delivery channel and target to `TOOLS.md` so the agent knows where to send reminders without asking:

```markdown
## Reminders
- Delivery target (Telegram): 268203409
```

Replace the channel name and ID with your own (e.g. WhatsApp E.164 number, Discord channel ID). The agent reads this at reminder creation time and passes it to `--target` and `--channel` automatically.

---

## CLI usage

```bash
# Set a reminder (relative time)
bash ./skills/quick-reminders/scripts/nohup-reminder.sh add "Call John back!" --target <chat_id> -t 2h

# Set a reminder (absolute time with timezone)
bash ./skills/quick-reminders/scripts/nohup-reminder.sh add "Pick up the package" --target <chat_id> -t "2026-02-07T18:00:00" -z "America/New_York"

# Set a reminder via WhatsApp
bash ./skills/quick-reminders/scripts/nohup-reminder.sh add "Check the oven!" --target +15551234567 -t 30m --channel whatsapp

# List active reminders
bash ./skills/quick-reminders/scripts/nohup-reminder.sh list

# Cancel by ID
bash ./skills/quick-reminders/scripts/nohup-reminder.sh remove 3

# Cancel multiple
bash ./skills/quick-reminders/scripts/nohup-reminder.sh remove 1 4

# Cancel all
bash ./skills/quick-reminders/scripts/nohup-reminder.sh remove --all

# Help
bash ./skills/quick-reminders/scripts/nohup-reminder.sh help
```

### Flags

| Flag | Used with | Description |
|------|-----------|-------------|
| `--target ID` | `add` | Delivery target (e.g. Telegram chat ID, WhatsApp E.164, Discord channel). Required. |
| `-t TIME` | `add` | When to fire. Relative (`30s`, `20m`, `2h`, `1d`, `1h30m`) or absolute ISO-8601. Required. |
| `--channel CH` | `add` | Delivery channel (default: `telegram`). E.g. `whatsapp`, `discord`, `signal`. Optional. |
| `-z TZ` | `add` | IANA timezone for naive absolute times (default: system local). Optional. |
| `--all` | `remove` | Cancel all active reminders. |

---

## Security & data access

### What the skill needs and why

| Data | Purpose | Source |
|------|---------|--------|
| **Delivery target** (e.g. Telegram chat ID) | Passed to `openclaw message send --target` so the reminder reaches the right chat. | Read from `TOOLS.md` (§ Reminders) at creation time; if missing, the agent falls back to `session_status` tool's `deliveryContext.to` and saves it to `TOOLS.md` for future use. |
| **Delivery channel** (e.g. `telegram`) | Passed to `openclaw message send --channel` to route through the correct messaging channel. | Defaults to `telegram`; overridden via `--channel` flag when the user requests a different channel. |
| **Reminder text** | The exact message delivered to the user at fire time. | Composed by the agent at creation time; stored in a temp file (`/tmp/oclaw-rem-<key>-<id>.msg`, mode 0600) until delivery, then deleted. |

### What it reads and writes

| Path | Access | Why |
|------|--------|-----|
| `TOOLS.md` | Read (always), write (once, if delivery target missing) | Reads the delivery target. Writes it once if discovered from session context — so it doesn't need to be looked up again. |
| `./reminders.json` | Read/write | Tracks active reminders (ID, PID, text, fire time). Auto-pruned on every operation. |
| `/tmp/oclaw-rem-<key>-<id>.msg` | Write (create), read (at fire), delete (after fire or cancel) | Holds reminder text as a plain file to avoid shell quoting issues in the background process. |

### Credentials

The skill itself declares **no API keys or tokens**. Message delivery is handled entirely by the `openclaw` CLI, which uses whatever authentication and channel credentials are already configured in your OpenClaw instance. The skill does not read, store, or transmit any credentials directly.

### Background processes

Each reminder spawns **one detached `nohup` process** that sleeps for the specified duration, then calls `openclaw message send` and self-removes from `reminders.json`. These processes:
- Run under the same user as the OpenClaw gateway.
- Are visible via standard process tools (`ps`, Activity Monitor).
- Are killed and cleaned up when cancelled via `remove`.
- Do **not** survive machine reboots.

### Model invocation

`disable-model-invocation` is **not set** — the agent can create reminders autonomously from natural conversation (e.g. "remind me in 20 min"). This is intentional for a personal assistant workflow. If you prefer explicit-only invocation, add `disable-model-invocation: true` to the SKILL.md frontmatter; the skill will then only respond to the `/quick-reminders` slash command.

---

## Limitations

* **Does not survive machine reboot.** The reminder is a background `sleep` process — if the machine restarts, pending reminders are lost.
* **Best for < 48 hours.** For longer-horizon reminders, use a calendar event with a notification or openclaw cron instead.
* **Gateway must be running** at fire time for `openclaw message send` to deliver.
* **Best-effort delivery** — no delivery receipt or retry on failure.
* **Auto-cleanup after fire attempt** — reminder metadata is removed after scheduled execution even if delivery fails.

---

## Notes

* **Channel-agnostic** — defaults to Telegram but works with any channel supported by `openclaw message send` (WhatsApp, Discord, Slack, Signal, iMessage, etc.). Pass `--channel <name>` to override.
* The script is BSD/GNU portable — handles both macOS (`date -j`) and Linux (`date -d`) date parsing.
* Fired reminders self-clean: the runner script calls `remove <id>` after delivery, so the tracking file stays tidy.
* Temp files (`/tmp/oclaw-rem-<workspace-key>-<id>.msg` - holds the reminder text as a plain file to avoid quoting nightmares) are cleaned up on both fire and manual removal.
