---
name: channels-setup
description: Guide to set up and configure IM channels(Telegram, Discord, Slack, Feishu, Dingtalk) for OpenClaw.
---

## Quick Start

Use openclaw CLI to enable and configure the channels you want.

After configuration, you should restart the gateway to apply changes:

```bash
openclaw gateway restart
```

In order to use `openclaw` cli, you may need execute `source /root/.nvm/nvm.sh` first to load nvm environment.

Before restart gateway, must tell user you will restart yourself.

### Telegram

```bash
openclaw config set channels.telegram.botToken "YOUR_BOT_TOKEN"
openclaw config set channels.telegram.dmPolicy "pairing"
openclaw config set channels.telegram.groups."*".requireMention true
openclaw config set channels.telegram.enabled true
```

### Discord

```bash
openclaw config set channels.discord.token "YOUR_BOT_TOKEN"
openclaw config set channels.discord.enabled true
```

### Slack

```bash
openclaw config set channels.slack.mode "socket"
openclaw config set channels.slack.appToken "xapp-..."
openclaw config set channels.slack.botToken "xoxb-..."
openclaw config set channels.slack.enabled true
```

### Feishu

```bash
openclaw config set channels.feishu.appId "YOUR_APP_ID"
openclaw config set channels.feishu.appSecret "YOUR_APP_SECRET"
openclaw config set channels.feishu.groupPolicy "true"
openclaw config set channels.feishu.enabled true
```

### Dingtalk

Edit the `channels` and `gateway` fields in `~/.openclaw/openclaw.json` as below:

```json
{
  "channels": {
    "dingtalk-connector": {
      "enabled": true,
      "clientId": "dingxxxxxxxxx",       // DingTalk AppKey
      "clientSecret": "your_secret_here", // DingTalk AppSecret
      "gatewayToken": "",                 // Optional: Gateway authentication token, the value of gateway.auth.token in openclaw.json
      "gatewayPassword": "",              // Optional: Gateway authentication password (choose either token or password)
      "sessionTimeout": 1800000           // Optional: Session timeout (ms), default is 30 minutes
    }
  },
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

## References

You can refer to the following documents for more detailed configuration instructions:

For Feishu channel detail setup, please refer to:

- [Feishu Channel Setup Guide](/root/.openclaw/extensions/feishu/README.md)

For Dingtalk channel detail setup, please refer to:

- [Dingtalk Channel Setup Guide](/root/.openclaw/extensions/dingtalk-connector/README.md)

For Telegram, Slack, Discord or more channels setup, please refer to [OpenClaw Channel Setup Guide](/root/.local/share/pnpm/global/5/node_modules/openclaw/docs/channels). Use `ls /root/.local/share/pnpm/global/5/node_modules/openclaw/docs/channels` to see all available channel setup guides.

