# AgentMail API notes used by this skill

- SDK object: `AgentMail(api_key=...)`
- List messages: `client.inboxes.messages.list(inbox_id=..., limit=..., labels=..., ascending=...)`
- Get message: `client.inboxes.messages.get(inbox_id=..., message_id=...)`
- Reply: `client.inboxes.messages.reply(inbox_id=..., message_id=..., text=..., reply_all=False)`
- Update labels (used for read/unread + dedupe): `client.inboxes.messages.update(add_labels=[...], remove_labels=[...])`
- Attachment metadata/download URL: `client.inboxes.messages.get_attachment(...)`

Observed labels in this inbox include `received` and `unread`.

The scripts model read/unread as label toggles:
- read => add `read`, remove `unread`
- unread => add `unread`, remove `read`

Default reply behavior in `reply_messages.py`:
- reply to matching unread emails
- add dedupe label (`AUTO_REPLIED` by default)
- mark as read (unless `--keep-unread` is used)

If your workspace uses different label semantics, adjust `scripts/set_read_state.py`.
