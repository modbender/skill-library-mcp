# Evolution WhatsApp Skill

Control WhatsApp via Evolution API v2.

## Configuration

Before using, configure your credentials:

```bash
export EVO_BASE_URL="https://your-evo-instance.com"
export EVO_INSTANCE_TOKEN="your-instance-token"
export EVO_INSTANCE_NAME="YourInstanceName"
```

### Getting Credentials

1. **Deploy Evolution API** — Use [Evolution API](https://github.com/Atelier23/evolution-api-v2) or their hosted service
2. **Create an instance** — Get your instance name and token
3. **Set environment variables** — Add to your shell or OpenClaw config

## Capabilities

- Send text messages
- Send media (images, videos, documents)
- Send audio / voice notes
- Send stickers
- Send location
- Send contacts
- Send buttons / interactive messages
- Send lists
- Send polls
- Create / manage groups
- Fetch chats, messages, contacts
- Summarize group conversations

## Usage Examples

```
Send a message to +201234567890: Hello!
Send an image to [number]: https://example.com/image.jpg with caption "Check this out"
Get my recent chats
List my groups
Summarize group [group name]
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EVO_BASE_URL` | Your Evolution API base URL |
| `EVO_INSTANCE_TOKEN` | Your instance API token |
| `EVO_INSTANCE_NAME` | Your instance name (URL encoded if needed) |

## Notes

- Ensure your Evolution API instance is running and accessible
- The instance must be connected to WhatsApp
- Check API documentation for rate limits and restrictions
