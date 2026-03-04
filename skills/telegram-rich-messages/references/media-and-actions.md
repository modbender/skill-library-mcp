# Telegram Media & Message Actions

## Direct File Transfers
Telegram supports sending files directly from the agent's filesystem.

### Sending a File
Use the `message` tool with the `media` parameter pointing to a local path or URL.
```json
{
  "action": "send",
  "channel": "telegram",
  "target": "telegram:2136878064",
  "message": "Here is the PDF report.",
  "media": "/tmp/report.pdf"
}
```

### Voice Notes and Video Notes
- **Voice Note**: Set `asVoice: true` in the `send` action. This sends audio as a native Telegram voice message.
- **Video Note**: Set `asVideoNote: true` in the `send` action. This sends video as a native "Round Video".

## Reactions
Reactions are a low-noise way to acknowledge messages.

### Adding a Reaction
Use the `message` tool with `action: "react"`.
```json
{
  "action": "react",
  "channel": "telegram",
  "target": "telegram:2136878064",
  "messageId": "12345",
  "emoji": "👍"
}
```

## Stickers
If enabled in config, you can send and search for stickers.

- **Send**: `action: "sticker"` with `fileId`.
- **Search**: `action: "sticker-search"` with `query`.

## Message Management
- **Edit**: Use `action: "edit"` to update a message you previously sent. Great for showing progress or changing state (e.g., "Starting..." -> "Done!").
- **Delete**: Use `action: "delete"` to remove sensitive or temporary messages.

## Best Practices for Media
- **Captions**: Always include a descriptive message when sending media.
- **Audio as Voice**: Include `[[audio_as_voice]]` in your response to force an audio file to be sent as a voice note.
- **Video Notes**: Use `asVideoNote: true` in the tool call for round "video messages".
