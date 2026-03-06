# Token Counter Classification Rules

## Session Type

- `main`: session key equals `agent:main:main` or first user message looks like `[Tue 2026-... message_id ...]`.
- `cron`: session key contains `:cron:` or first user message starts with `[cron:<job-id> ...]`.
- `subagent`: session key contains `:subagent:`.
- Fallback: `interactive`.

## Category

Explicit cron mappings:

- `d3d76f7a-7090-41c3-bb19-e2324093f9b1` -> `content_generation`
- `736a84a6-162a-4301-9deb-810cefff0628` -> `outreach_management`
- `6c966232-5cc9-4e21-aec7-fb8f143e67f6` -> `monitoring`

Keyword-based classification across session key, label, first user text, and cron payload:

- `job_search`: job hunt, application, resume, linkedin, remote role.
- `outreach_management`: outreach, guest post, lead, reply checker, gmail, email check, prospect, pitch, inbox.
- `content_generation`: content, article, blog, youtube, summarize, writer, research, publish, nano-banana.
- `monitoring`: monitor, heartbeat, health, status, daily summary, check-in, watcher, scan.
- Fallback by type:
  - main -> `interactive`
  - cron -> `monitoring`
  - subagent -> `content_generation`
  - else -> `interactive`

## Client Detection

Client is detected from user/task context, labels, keys, and cron payload text.

- `bonsai` markers:
  - `bonsai`, `bonsaimediagroup.com`, `mike@bonsai`, `/projects/bonsai`, `regulator`, `jayco`, `ocala horse`, `ohp`
- `personal` markers:
  - `mkhaytman@gmail.com`, `aimarketingpicks`, `remoteworkpicks`, `anonark`, `soflotimes`, `quicksummit`, `personal site`
- If both marker sets appear: `mixed`
- If neither appears: `unknown`

## Outcome

- `failure`: has errors and no successful assistant turns.
- `partial`: has errors, or model hit `max_tokens`, but session still made progress.
- `success`: no errors and no truncation indicators.

## Tool Token Attribution

- Tool calls are parsed from assistant message content blocks where `type == "toolCall"`.
- Assistant message `usage.totalTokens` is split evenly across tool calls in that same assistant message.
- This is heuristic attribution, useful for hotspot detection rather than exact billing.
