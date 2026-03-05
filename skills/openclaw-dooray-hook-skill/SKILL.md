---
name: dooray-hook
description: Send automated notifications to Dooray! messenger channels via webhooks.
homepage: https://dooray.com
metadata:
  openclaw:
    emoji: "📨"
    requires:
      bins: ["python3"]
      config: ["skills.entries.dooray-hook.config"]
---

# Dooray! Webhook Skill

A seamless integration to send text notifications and status updates to **Dooray!** chat rooms using Incoming Webhooks.

## Overview

This skill allows OpenClaw to communicate with your team on Dooray!. It supports multiple chat rooms, customizable bot profiles, and configurable SSL verification settings.

## Configuration

To use this skill, you must define your Dooray! webhook URLs in the OpenClaw global config (`~/.openclaw/openclaw.json`).

> **Security Note:** Webhook URLs are stored in your local config file. Ensure this file's permissions are restricted (e.g., `chmod 600`).

```json
{
  "skills": {
    "entries": {
      "dooray-hook": {
        "enabled": true,
        "config": {
          "botName": "N.I.C.K.",
          "botIconImage": "[https://static.dooray.com/static_images/dooray-bot.png](https://static.dooray.com/static_images/dooray-bot.png)",
          "verify_ssl": true,
          "rooms": {
            "General": "[https://hook.dooray.com/services/YOUR_TOKEN_1](https://hook.dooray.com/services/YOUR_TOKEN_1)",
            "Alerts": "[https://hook.dooray.com/services/YOUR_TOKEN_2](https://hook.dooray.com/services/YOUR_TOKEN_2)"
          }
        }
      }
    }
  }
}

```

### Configuration Options

* **`rooms`** (Required): A dictionary mapping room names to webhook URLs.
* **`botName`** (Optional): The name displayed for the bot message (Default: "OpenClaw").
* **`verify_ssl`** (Optional): Set to `false` to disable SSL certificate verification. Useful for corporate proxies or self-signed certificates. (Default: `true`).

## Usage

### 💬 Natural Language

You can ask OpenClaw to send messages directly:

* *"Send 'Server deployment successful' to the Alerts room on Dooray."*
* *"Tell the General channel that I'll be late for the meeting."*

### 💻 CLI Execution

```bash
python scripts/send_dooray.py "RoomName" "Your message content"

```

## Technical Details

* **Zero Dependencies**: Uses Python's built-in `urllib.request` and `json` modules. No `pip install` or `venv` required.
* **Security**:
* Defaults to secure SSL context (`verify_ssl: true`).
* Requires explicit configuration to bypass certificate checks.



## Troubleshooting

* **[SSL: CERTIFICATE_VERIFY_FAILED]**: If you are behind a corporate proxy or using self-signed certificates, add `"verify_ssl": false` to your config.
* **Room Not Found**: Ensure the room name matches the key in your `openclaw.json` exactly (case-sensitive).
* **Invalid URL**: Verify the webhook URL starts with `https://hook.dooray.com/services/`.

```

```