# VAGUS Skill for OpenClaw

Give your OpenClaw agent a phone.

## Install

**Important:** Install the skill to your *user* OpenClaw skills directory to persist across updates. Do **not** place it in the system skills directory (`/usr/local/lib/node_modules/openclaw/skills/`) as it may be overwritten.

### Manual Install (Current)

1. From the skill root directory, run the installer:
   ```bash
   ./scripts/install.sh
   ```
   This copies the skill to `~/.openclaw/skills/vagus` and installs dependencies.

   Or do it manually:
   ```bash
   mkdir -p ~/.openclaw/skills
   git clone https://github.com/vagus-mcp/openclaw-skill.git ~/.openclaw/skills/vagus
   # or copy the vagus-openclaw folder to ~/.openclaw/skills/vagus
   cd ~/.openclaw/skills/vagus/scripts
   npm install
   ```

3. Pair your phone with the VAGUS app and run:
   ```bash
   node vagus-connect.js pair <CODE>
   node vagus-connect.js call agent/set_name '{"name":"<YOUR_AGENT_NAME>"}'
   ```

### Agent-driven Install (Future)

When available, you can instruct your OpenClaw agent:
> "Install the VAGUS skill from https://github.com/vagus-mcp/openclaw-skill"

The agent should fetch and install to `~/.openclaw/skills/vagus` automatically.

After pairing, the agent should set its device-side identity name:

```bash
node {baseDir}/scripts/vagus-connect.js call agent/set_name '{"name":"<IDENTITY_NAME>"}'
```

## Requirements

- [VAGUS app](https://play.google.com/store/apps/details?id=com.vagus.app) installed on an Android phone
- OpenClaw with Node 22+
- Internet access to `relay.withvagus.com`

## What It Does

Once connected, your agent can:
- Read phone sensors: motion, location, environment
- Read inferred attention availability (`vagus://inference/attention`)
- Read inferred indoor confidence (`vagus://inference/indoor_confidence`)
- Read inferred sleep likelihood (`vagus://inference/sleep_likelihood`)
- Read inferred notification timing suitability (`vagus://inference/notification_timing`)
- Read device state: battery, connectivity, screen
- Read phone notifications (if enabled)
- Call haptic actions: `haptic/pulse`, `haptic/pattern`
- Speak through the phone (`speak`)
- Push phone notifications (`notify`)
- Write clipboard content (`clipboard/set`)
- Send SMS messages (`sms/send`)
- Open URLs on the phone (`intent/open_url`)
- Create calendar events (`calendar/create_event`)
- Set/clear device-side agent name (`agent/set_name`)

Capabilities are controlled by the user through VAGUS app permission toggles.

Environment note: `vagus://sensors/environment` now reports inferred context (for example indoor/outdoor/vehicle) with confidence and evidence, in addition to ambient signals.

## Repository Structure

```text
.
├── SKILL.md
├── scripts/
│   ├── package.json
│   ├── vagus-connect.js
│   └── lib/
│       ├── mcp-codec.js
│       ├── mcp-session.js
│       ├── ws-transport.js
│       ├── session-store.js
│       └── subscription-manager.js
├── references/
│   ├── mcp-resources.md
│   ├── mcp-tools.md
│   └── troubleshooting.md
└── README.md
```

## Pairing and Usage (Direct)

If needed for manual diagnostics:

```bash
cd ~/.openclaw/skills/vagus/scripts
npm install
node vagus-connect.js pair <CODE>
node vagus-connect.js status
node vagus-connect.js read vagus://session/info
node vagus-connect.js list-resources
node vagus-connect.js list-tools
```

### Subscription Streaming

Use subscriptions for continuous updates:

```bash
node vagus-connect.js subscribe <resource-uri>
```

Behavior:
- The command is long-running and continuously writes JSONL updates to stdout.
- In OpenClaw, the agent keeps this `exec` process alive and consumes update lines as they arrive.
- Stop by terminating the process, or explicitly call:

```bash
node vagus-connect.js unsubscribe <resource-uri>
```

Lifecycle and accuracy note:
- Module lifecycle is subscription-driven (start on active subscriptions, stop when no subscriptions remain).
- Inference resources are most accurate while stream-subscribed; one-off reads can be briefly cold-start and less accurate.
- Reconnect behavior: server emits a `session/reconnect` marker with `sessionId`, `gap_ms`, and `ts`, then replays buffered resource updates (bounded, up to 64) and emits a fresh snapshot before resuming normal live streaming.

## Troubleshooting

Start with:

```bash
node {baseDir}/scripts/vagus-connect.js status
```

Then follow `references/troubleshooting.md`.
