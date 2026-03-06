---
name: hashbox-plugin
description: OpenClaw plugin that connects an AI agent to the HashBox iOS app
  via Firebase webhook for push notifications.
---

# hashbox-plugin

OpenClaw plugin that connects an AI agent to the HashBox iOS app via Firebase webhook for push notifications.

## Installation

```bash
npm install hashbox-plugin
```

## Setup

### Prerequisites

1. A HashBox iOS app account
2. A valid `HB-` prefixed API token from your HashBox dashboard

### Configuration

Before using the plugin, configure it with your HashBox API token using the `configure_hashbox` tool:

```
configure_hashbox({
  "token": "HB-your-token-here"
})
```

This stores your configuration locally in `hashbox_config.json`.

## Usage

### configure_hashbox

Sets up the HashBox connection by saving your API token.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | string | Yes | Your HashBox API token (must start with `HB-`) |

**Example:**

```
configure_hashbox({
  "token": "HB-abc123"
})
```

### send_hashbox_notification

Sends a push notification to the HashBox iOS app through the configured Firebase webhook.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `payloadType` | `"article"` \| `"metric"` \| `"audit"` | Yes | Type of notification payload |
| `channelName` | string | Yes | Name of the notification channel |
| `channelIcon` | string | Yes | Icon/emoji for the channel |
| `title` | string | Yes | Notification title |
| `contentOrData` | string \| MetricItem[] \| AuditFinding[] | Yes | Content body (string for article) or structured data (array for metric/audit) |

**Example (article):**

```
send_hashbox_notification({
  "payloadType": "article",
  "channelName": "Builds",
  "channelIcon": "🔨",
  "title": "Build Complete",
  "contentOrData": "Your project compiled successfully with 0 errors."
})
```

**Example (metric):**

```
send_hashbox_notification({
  "payloadType": "metric",
  "channelName": "Performance",
  "channelIcon": "📊",
  "title": "Daily Metrics",
  "contentOrData": [
    { "label": "CPU Usage", "value": 42, "unit": "%" },
    { "label": "Memory", "value": 8.2, "unit": "GB" }
  ]
})
```

**Example (audit):**

```
send_hashbox_notification({
  "payloadType": "audit",
  "channelName": "Security",
  "channelIcon": "🔒",
  "title": "Audit Log",
  "contentOrData": [
    { "severity": "info", "message": "User logged in from new device" }
  ]
})
```

## Dependencies

- Node.js >= 18.0.0
- A valid `HB-` prefixed token from your HashBox account

## License

MIT
