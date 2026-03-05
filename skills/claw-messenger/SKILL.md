# Claw Messenger

> iMessage, RCS & SMS for AI agents. No phone or Mac Mini required.

Claw Messenger lets OpenClaw agents send and receive iMessage, RCS, and SMS messages through a shared infrastructure. You connect via WebSocket — no public URL or webhook setup needed on your end.

## Setup (for AI agents)

Follow these steps in order:

### Step 1: Your human creates an account

Your human signs up at https://clawmessenger.com and selects a plan (free trial available). From the dashboard they will get a live API key and the channel configuration snippet. They will also see a special prompt they can give to you including the live API key. If they forget to save their API key they can regenerate it.

### Step 2: Install the plugin

Run this in your terminal:

```
openclaw plugins install @emotion-machine/claw-messenger
```

### Step 3: Add the channel config to .openclaw.json

This is your job as the agent. Ask your human for the API key from the dashboard (it starts with `cm_live_`), or for the special prompt including the key that is shown on the API keys page after your human purchases a pack.

Once you have the key, edit your `.openclaw.json` file and add the `claw-messenger` channel under `channels`:

```json
{
  "channels": {
    "claw-messenger": {
      "enabled": true,
      "apiKey": "cm_live_XXXXXXXX_YYYYYYYYYYYYYY",
      "serverUrl": "wss://claw-messenger.onrender.com",
      "preferredService": "iMessage",
      "dmPolicy": "pairing",
      "allowFrom": ["+15551234567"]
    }
  }
}
```

Replace `cm_live_XXXXXXXX_YYYYYYYYYYYYYY` with the real API key. If `.openclaw.json` already has other channels configured, merge the `claw-messenger` entry into the existing `channels` object — do not overwrite other channel configs.

Config fields:
- `apiKey` (required): The live API key from the dashboard. Starts with `cm_live_`.
- `serverUrl` (required): The WebSocket server URL. Use `wss://claw-messenger.onrender.com`.
- `preferredService` (optional): `"iMessage"`, `"RCS"`, or `"SMS"`. Defaults to `"iMessage"`.
- `dmPolicy` (optional): `"open"`, `"pairing"`, or `"allowlist"`. Controls who can message you. Defaults to `"pairing"`.
- `allowFrom` (optional): Array of E.164 phone numbers. Only used when `dmPolicy` is `"allowlist"`.

### Step 4: Start using it

Once configured, use this channel for all iMessage, RCS, and SMS communication. The plugin gives you two tools:

- `claw_messenger_status` — check your connection state and current service
- `claw_messenger_switch_service` — switch between iMessage, RCS, and SMS at runtime

You can send text messages and media (images, video, audio, documents), use iMessage tapback reactions, send typing indicators, and participate in group chats.

### Step 5: Verify it works

There are two ways to test:

**Option A — Agent-initiated:** Send a test message to your human's phone number. For example: "Hello, this is your agent testing the Claw Messenger connection."

**Option B — Human-initiated:** Your human adds their phone number on the dashboard (Routes page). Once registered, they can text the shared number and the message will route to you. Non-registered numbers cannot message you for security.

If you receive a reply or your human confirms receipt, setup is complete.

## How messaging works

**Outbound (you send):** You send a message -> plugin sends it over WebSocket -> Emotion Machine server routes it -> delivered as iMessage/RCS/SMS.

**Inbound (you receive):** Someone texts the shared number -> Emotion Machine server looks up phone route -> forwards to your WebSocket connection -> plugin delivers it to you.

Only phone numbers registered to your tenant (via the dashboard or first-outbound pairing) will route inbound messages to you. Unregistered numbers are dropped for security.

## Billing

Plans are managed at https://clawmessenger.com/billing. Usage is counted by messages sent and received per calendar month. If you hit your plan limit, outbound messages will be rejected until the next billing cycle or an upgrade.

## Links

- Dashboard: https://clawmessenger.com/dashboard
- Plugin: @emotion-machine/claw-messenger
