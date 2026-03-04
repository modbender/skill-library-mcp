# hashbox-plugin

OpenClaw plugin that connects an AI agent to the HashBox iOS app via Firebase webhook for push notifications.

## Installation

```bash
npm install hashbox-plugin
```

Or via ClawHub:

```bash
clawhub install hashbox-plugin
```

## Quick Start

### 1. Configure your token

```
configure_hashbox({ "token": "HB-your-token-here" })
```

### 2. Send a notification

```
send_hashbox_notification({
  "payloadType": "article",
  "channelName": "AI Trends",
  "channelIcon": "🤖",
  "title": "Daily Summary",
  "contentOrData": "Here's what happened today..."
})
```

## Tools

### configure_hashbox

Saves your HashBox API token locally so the agent can push notifications.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | string | Yes | Your HashBox API token (must start with `HB-`) |

### send_hashbox_notification

Pushes curated news, summaries, or system metrics to your HashBox iOS app.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `payloadType` | `"article"` \| `"metric"` \| `"audit"` | Yes | Type of notification payload |
| `channelName` | string | Yes | Name of the notification channel |
| `channelIcon` | string | Yes | Single emoji icon for the channel |
| `title` | string | Yes | Notification title |
| `contentOrData` | string \| MetricItem[] \| AuditFinding[] | Yes | Markdown string for articles, or structured data for metrics/audits |

#### Payload Examples

**Article:**
```json
{
  "payloadType": "article",
  "channelName": "Builds",
  "channelIcon": "🔨",
  "title": "Build Complete",
  "contentOrData": "Your project compiled successfully with 0 errors."
}
```

**Metric:**
```json
{
  "payloadType": "metric",
  "channelName": "Performance",
  "channelIcon": "📊",
  "title": "Daily Metrics",
  "contentOrData": [
    { "label": "CPU Usage", "value": 42, "unit": "%" },
    { "label": "Memory", "value": 8.2, "unit": "GB" }
  ]
}
```

**Audit:**
```json
{
  "payloadType": "audit",
  "channelName": "Security",
  "channelIcon": "🔒",
  "title": "Audit Log",
  "contentOrData": [
    { "severity": "info", "message": "User logged in from new device" }
  ]
}
```

## Programmatic Usage

```typescript
import { hashBoxPlugin, configureHashBox, sendHashBoxNotification } from "hashbox-plugin";

// Register with OpenClaw
registerPlugin(hashBoxPlugin);

// Or use directly
await configureHashBox("HB-your-token");
const result = await sendHashBoxNotification(
  "article", "AI Trends", "🤖", "Hello", "Test content"
);
console.log(result.status); // 200
```

## Requirements

- Node.js >= 18.0.0
- A valid `HB-` prefixed token from your HashBox account

## License

MIT
