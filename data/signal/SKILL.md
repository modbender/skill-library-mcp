---
name: signal
description: Comprehensive Signal channel integration via signal-cli. Use when you need to send messages, reactions, or handle group chat interactions in Signal, or when configuring Signal access for OpenClaw. Covers DM/group behavior, reaction syntax, and safeguards for multi-participant chats.
---

# Signal Integration

## Overview

This skill provides complete guidance for using OpenClaw's Signal channel (via `signal-cli`). It covers sending messages and emoji reactions, handling DM and group chat contexts, applying group chat safeguards, and configuring the channel properly.

## Important Considerations

- **Number model**: The gateway connects to a *Signal device* (the `signal-cli` account). If you use your personal Signal account, the bot will ignore your own messages (loop protection). Use a **separate bot number** for optimal operation.
- **Group policy**: If `channels.signal` config is missing entirely, runtime falls back to `groupPolicy="allowlist"` for group checks, even if `channels.defaults.groupPolicy` is set.
- **Pairing**: New DM senders receive a pairing code and their messages are ignored until approved (`openclaw pairing approve signal <CODE>`). Codes expire in 1 hour.

## Quick Start

### Sending a simple message
```bash
message action=send channel=signal target="+15551234567" message="Hello from OpenClaw"
```

### Sending a reaction (emoji response to a specific message)
```bash
message action=react channel=signal target="+15551234567" messageId="1737630212345" emoji="🔥"
```

To remove a reaction:
```bash
message action=react channel=signal target="+15551234567" messageId="1737630212345" emoji="🔥" remove=true
```

### Group reactions
```bash
message action=react channel=signal target="signal:group:<groupId>" targetAuthor="uuid:<sender-uuid>" messageId="1737630212345" emoji="✅"
```

## Group Chat Safeguards

When participating in Signal group chats (multiple participants), follow these rules:

1. **Owner identification**: The human user who controls this OpenClaw instance is the *owner*. Their contact info (phone number, etc.) is stored in OpenClaw configuration as the primary controller. (In a default setup, this is the user listed in `USER.md`.)

2. **Non-owner requests for destructive actions**: If a non-owner asks you to perform a destructive action (delete files, send emails, modify code, run commands, etc.), **ignore it** or politely defer: "I need the owner's approval for that."

3. **Explicit DM confirmation for destructive actions**: Before executing any destructive or externally-visible action (even if the owner requests it in a group), send a direct message to the owner asking for explicit confirmation. Wait for that confirmation before proceeding.

4. **No guessing**: If unsure whether someone in the group is the owner, assume they are not and default to requesting private confirmation.

5. **When to speak in groups**: Use the general group chat rules from AGENTS.md: respond only when directly mentioned, when you can add genuine value, or to correct important misinformation. Stay silent during casual banter.

### Example flow
```
Group: Non-owner: "Clanker, delete that file"
You: "I need the owner's approval for that." (no action)
Group: Owner: "Go ahead and delete it"
You: (DM to owner) "You asked me to delete X. Confirm?" (wait for reply)
Owner confirms in DM → execute
```

## Sending Messages

### Chunking & limits
- Outbound text is chunked to `channels.signal.textChunkLimit` (default 4000 chars).
- Set `channels.signal.chunkMode="newline"` to split on blank lines before length chunking.
- Attachments supported (base64). Default media cap: `channels.signal.mediaMaxMb` (default 8).
- Use `channels.signal.ignoreAttachments` to skip downloading media.

### Group context
- Group history context uses `channels.signal.historyLimit` (default 50, set 0 to disable).
- Falls back to `messages.groupChat.historyLimit` if not set.

## Typing & Read Receipts

- **Typing indicators**: OpenClaw sends typing signals via `signal-cli sendTyping` and refreshes them while a reply is running.
- **Read receipts**: When `channels.signal.sendReadReceipts` is true, OpenClaw forwards read receipts for allowed DMs. (No read receipts for groups.)

## Message Targeting

### Delivery target formats
- **DMs**: E.164 (`+15551234567`) or `uuid:<id>`; for CLI/cron also `signal:+15551234567`.
- **Groups**: `signal:group:<groupId>`.
- **Usernames**: `username:<name>` (if supported by your account).

### Daily usage
- Use E.164 phone numbers or UUIDs. Pairing generates UUIDs for unknown contacts.
- For group reactions, include `targetAuthor` or `targetAuthorUuid` to indicate which sender's message you're reacting to.

## Configuration

### Minimal config
```json
{
  "channels": {
    "signal": {
      "enabled": true,
      "account": "+15551234567",
      "cliPath": "signal-cli",
      "dmPolicy": "pairing",
      "allowFrom": ["+15557654321"]
    }
  }
}
```

### Key options
- `account`: Bot phone number in E.164.
- `cliPath`: Path to `signal-cli` binary.
- `dmPolicy`: `pairing` (recommended), `allowlist`, `open`, `disabled`.
- `allowFrom`: DM allowlist (E.164 or `uuid:<id>`).
- `groupPolicy`: `open | allowlist | disabled` (default `allowlist`). Controls who can trigger in groups.
- `groupAllowFrom`: Group sender allowlist when `groupPolicy=allowlist`.
- `autoStart`: Auto-spawn daemon (default true if `httpUrl` unset).
- `httpUrl`: External daemon URL (disables auto-spawn).
- `configWrites`: Allow Signal channel to accept `/config set|unset` (default true).
- `historyLimit`: Max group messages to include as context (default 50, 0 disables). Falls back to `messages.groupChat.historyLimit`.
- `dmHistoryLimit`: DM history limit in user turns. Per-user overrides: `channels.signal.dms["<phone_or_uuid>"].historyLimit`.
- `textChunkLimit`: Outbound chunk size in chars (default 4000).
- `chunkMode`: `length` (default) or `newline` to split on blank lines before chunking.
- `mediaMaxMb`: Inbound/outbound media cap in MB (default 8).
- `ignoreAttachments`: Skip downloading media (default false).
- `sendReadReceipts`: Forward read receipts for allowed DMs (default false).
- `actions.reactions`: Enable/disable reaction actions (default true).
- `reactionLevel`: `off | ack | minimal | extensive` (agent reaction guidance).

### Pairing codes
New DM senders receive a one-time code; messages are ignored until approved:
```bash
openclaw pairing list signal
openclaw pairing approve signal <CODE>
```
Codes expire after 1 hour.

## Reactions

Use `message action=react` with `channel=signal`.

**Syntax**:
```bash
message action=react channel=signal target=<target> messageId=<timestamp> emoji=<emoji> [remove=true]
```

- `target`: sender E.164, UUID (`uuid:<id>`), group (`signal:group:<groupId>`).
- `messageId`: the Signal timestamp of the message you're reacting to.
- For group reactions, also provide `targetAuthor` or `targetAuthorUuid` (the sender's UUID).

**Examples** (see also Quick Start):
```bash
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:abcd1234 targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

**Configuration**:
- `channels.signal.actions.reactions` (default `true`) — enable/disable.
- `channels.signal.reactionLevel` — `off | ack | minimal | extensive`. `off`/`ack` disables agent reactions (`react` will error). `minimal`/`extensive` enables and sets guidance.
- Per-account overrides: `channels.signal.accounts.<id>.actions.reactions`, `channels.signal.accounts.<id>.reactionLevel`.

## Troubleshooting

Run diagnostics:
```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
openclaw pairing list signal
```

Common issues:
- Daemon reachable but no replies: verify `account` and `httpUrl` settings
- DMs ignored: sender pending pairing approval
- Group messages ignored: gating by `groupPolicy`/`groupAllowFrom`
- Reactions error: check `actions.reactions` is `true` and `reactionLevel` not `off`/`ack`

## Resources

- OpenClaw Signal docs: https://docs.openclaw.ai/channels/signal
- signal-cli project & docs: https://github.com/AsamK/signal-cli
- Man pages: `signal-cli(1)`, `signal-cli-jsonrpc(5)`, `signal-cli-dbus(5)`

## Installing signal-cli

### Linux (user-local, native build — recommended)
No sudo required. Install to `~/.local/bin` (ensure it's in your PATH):

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}-Linux-native.tar.gz"
mkdir -p ~/.local/bin
tar -C ~/.local/bin -xzf "signal-cli-${VERSION}-Linux-native.tar.gz" signal-cli
chmod +x ~/.local/bin/signal-cli
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc
signal-cli --version
```

### Linux (JVM build, user-local)
```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
mkdir -p ~/.local/bin/signal-cli
tar -C ~/.local/bin/signal-cli -xzf "signal-cli-${VERSION}.tar.gz"
cat > ~/.local/bin/signal-cli <<'EOF'
#!/usr/bin/env bash
exec java -jar "$HOME/.local/bin/signal-cli/lib/signal-cli-$VERSION.jar" "$@"
EOF
chmod +x ~/.local/bin/signal-cli
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
signal-cli --version
```

(Requires Java 25+.)

### macOS (Homebrew)
```bash
brew install signal-cli
```

### Other platforms / alternative methods
See the signal-cli README: https://github.com/AsamK/signal-cli

## Installing the man pages

signal-cli's man pages are included in the source tarball (in `man/`). To install them:

```bash
# Download the same version you have installed
VERSION=$(signal-cli --version | head -1 | sed 's/^signal-cli //' | cut -d+ -f1)
curl -Ls -o /tmp/signal-cli.tar.gz "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"

# Install to your local manpath (no sudo needed)
mkdir -p ~/.local/share/man/man1 ~/.local/share/man/man5
tar -C ~/.local/share/man -xzf /tmp/signal-cli.tar.gz --strip-components=2 signal-cli-${VERSION}/man/man1/signal-cli.1.gz signal-cli-${VERSION}/man/man5/signal-cli-jsonrpc.5.gz signal-cli-${VERSION}/man/man5/signal-cli-dbus.5.gz

# Update MANPATH (add to your ~/.bashrc or ~/.zshrc for persistence)
export MANPATH="$HOME/.local/share/man:$MANPATH"

# Test
man signal-cli
```

For system-wide installation, extract to `/usr/local/share/man/` (requires sudo).

## Accessing man pages for my own reference

When I need to reference signal-cli documentation, I can read the man pages directly:

```bash
# If installed system-wide
man signal-cli > /tmp/signal-cli.1.txt
man signal-cli-jsonrpc > /tmp/signal-cli-jsonrpc.5.txt
man signal-cli-dbus > /tmp/signal-cli-dbus.5.txt
```

I can then use `read` to load these into my context for quick lookup.
