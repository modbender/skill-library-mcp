# pidgesms

An [OpenClaw](https://openclaw.ai/) skill for sending and reading SMS messages via [pidge](https://github.com/typhonius/pidge), a CLI and webhook server for [Android SMS Gateway](https://github.com/capcom6/android-sms-gateway).

## What it does

- Send SMS messages from your Android phone
- Read your SMS inbox
- Check message delivery status
- Mark messages as processed/unprocessed
- Health check the gateway

## Requirements

- [`pidge`](https://github.com/typhonius/pidge) installed (`go install github.com/typhonius/pidge@latest`)
- An Android device running [Android SMS Gateway](https://github.com/capcom6/android-sms-gateway), reachable over your network
- pidge config at `~/.config/pidge/config.toml`

## Installation

Copy or symlink the `pidgesms` folder into your OpenClaw skills directory:

```bash
# Local install
cp -r pidgesms ~/.openclaw/skills/pidgesms

# Or via ClawHub
clawhub install pidgesms
```

## Configuration

pidge reads its gateway connection details from `~/.config/pidge/config.toml`. See the [pidge docs](https://github.com/typhonius/pidge) for setup.

## Safety

- Messages go to real phone numbers — the skill confirms recipient and content before sending
- Private SMS content is never leaked into group chats
- Unknown numbers require explicit owner approval
- Sensitive information (passwords, tokens, etc.) is never sent via SMS

## License

MIT
