# Safety and Logging Policy

## Destructive Action Policy

### Delete

- Always requires explicit second confirmation.
- Confirmation must show target summary:
  - `memo_id`
  - timestamp
  - short snippet
  - action (`delete`)
- If the UI delete path cannot be located reliably, stop and do not attempt guessed clicks.

### Edit (Text Search Path)

- When target selection starts from text search, candidate confirmation is required before writing.
- Default edit mode is `replace` (full body replacement).
- Show target summary before executing edit.

## Candidate Selection Safety

- Text search is for discovery, not final identity.
- Final write target must be locked by `memo_id` extracted from a flomo href.
- If multiple candidates match and the user does not choose one, do not proceed.

## Minimal Logging (v1 Default)

Do not persist memo body text in local files.

Allowed in transient response output:
- action name
- success/failure status
- `memo_id`
- timestamp text
- candidate count
- short snippet for confirmation (truncated, only in-session)

Disallowed by default:
- local persistent logs containing memo bodies
- reference docs with real user memo content examples
- debug dumps of full page text unless explicitly requested for troubleshooting

## Screenshots

- Screenshots are for debugging and visual confirmation only.
- Prefer not to store screenshots unless needed for troubleshooting.
- If a tool auto-saves a screenshot, treat it as temporary debugging output.

## Stop Conditions

Stop and report a recoverable failure when:
- action menu or edit/delete controls cannot be located after retries
- dialog state is ambiguous (not clear which memo is selected)
- MCP tool returns inconsistent page state after a write action
- user has not confirmed a required destructive step

## Suggested Confirmation Phrases

Use short, unambiguous confirmations before destructive actions:
- Edit: "Confirm replace memo `<memo_id>` (timestamp `<time>`) with the new content?"
- Delete: "Confirm delete memo `<memo_id>` (timestamp `<time>`)? This cannot be undone."
