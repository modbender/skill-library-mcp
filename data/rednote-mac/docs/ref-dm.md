# Direct Messages (DM)

RedNote DMs are not accessible via the web API or headless browser — this is one of the core advantages of the native App approach.

---

## xhs_open_dm
Open a DM conversation by its position in the message list.

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `index` | integer | 0 = first conversation in list | `0` |

This tool automatically navigates to the messages tab first, so you don't need to call `xhs_navigate(tab="messages")` separately.

After opening, wait ~1.5s for the conversation to load, then `xhs_screenshot()` to confirm.

---

## xhs_send_dm
Send a message in the currently open DM conversation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | Message content (required) |

Must call `xhs_open_dm()` first. The message is typed into the input box and sent.

---

## Standard DM workflow

```
# Send a message to the first conversation
xhs_open_dm(index=0)
xhs_screenshot()              # confirm conversation opened, check who it is

xhs_send_dm(text="Hi! Saw your post and loved it 🎉")
xhs_screenshot()              # confirm message sent
```

```
# Reply to the third conversation
xhs_open_dm(index=2)
xhs_screenshot()              # verify correct contact
xhs_send_dm(text="Thanks for reaching out!")
```

---

## Notes

- The `index` follows the order of conversations as shown in the messages list (sorted by most recent).
- There's currently no tool to read received messages — use `xhs_screenshot()` + image analysis to read the conversation.
- Emojis and line breaks in `text` are supported.
