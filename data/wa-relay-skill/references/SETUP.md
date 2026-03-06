# wa-relay v0.2.0 — Setup Guide

## Prerequisites

- OpenClaw installed and running with WhatsApp channel connected
- Your phone number in international format (e.g. `+573001234567`)

## Architecture

```
Third party → [Relay Agent] --sessions_send--> [Main Agent] --WhatsApp--> Owner
                 (NO_REPLY)                      (📩 + suggested response)
```

The relay agent **never** responds to senders. It forwards messages to the main agent via `sessions_send`. The main agent notifies the owner with a suggested response.

## Step-by-Step

### 1. Run the setup script

```bash
cd ~/.openclaw/workspace/skills/wa-relay-skill
bash scripts/setup.sh +57XXXXXXXXXX
```

This will:
- Create `~/.openclaw/workspace-relay/` with a `SOUL.md` for the relay agent
- Add a "Relay de WhatsApp" section to your main agent's `SOUL.md`
- Copy `auth-profiles.json` from your main workspace (with confirmation)
- Patch the `SAFE_SESSION_ID_RE` regex (temporary until PR #16531 is merged)

### 2. Generate the routing config

```bash
# Basic (only owner goes to main):
bash scripts/configure.sh +57XXXXXXXXXX

# With direct numbers (bypass relay):
bash scripts/configure.sh +57XXXXXXXXXX +573009999999,+573008888888
```

This outputs the YAML/JSON you need for `agents.list` and `bindings`.

### 3. Apply the config

Edit your OpenClaw config (typically `~/.openclaw/config.yaml`):

```yaml
agents:
  list:
    - name: main
      workspace: ~/.openclaw/workspace
    - name: relay
      workspace: ~/.openclaw/workspace-relay

bindings:
  - channel: whatsapp
    agent: main
    filter:
      from: "+57XXXXXXXXXX"        # owner
  - channel: whatsapp
    agent: main
    filter:
      from: "+573009999999"        # direct number (optional)
  - channel: whatsapp
    agent: relay                   # catch-all: everyone else
```

**Important:** Bindings are evaluated in order. The catch-all relay binding must be last.

### 4. Restart OpenClaw

```bash
openclaw gateway restart
```

### 5. Test it

- Send a message **from your phone** → should go to the **main** agent
- Have someone else message you → relay forwards to main agent → you get a notification with suggested response

## How It Works (v0.2.0)

1. Third party sends a message → relay agent receives it
2. Relay uses `sessions_send` to forward: `📩 RELAY de [number]: [message]`
3. Main agent receives the inter-session message
4. Main agent notifies owner on WhatsApp with the message + a suggested response
5. Owner decides what to reply

## Reverting the Patch

Once PR #16531 is merged, restore the original files:

```bash
find ~/.openclaw/node_modules -name 'paths-*.js.bak' -exec sh -c 'mv "$1" "${1%.bak}"' _ {} \;
```

Or simply update OpenClaw to the latest version.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Relay not receiving messages | Check `bindings` config — catch-all must be last |
| Session ID errors | Verify the `paths-*.js` patch was applied |
| Auth errors on relay | Ensure `auth-profiles.json` was copied |
| Messages going to wrong agent | Restart gateway: `openclaw gateway restart` |
| Main agent not getting relay messages | Check `sessions_send` is available in relay agent's tools |
