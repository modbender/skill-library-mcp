# Remote Jobs Finder (OpenClaw × Remote Rocketship)

A fully conversational remote job finder for OpenClaw (including WhatsApp), powered by Remote Rocketship.

- Remote Rocketship: https://www.remoterocketship.com  
- ClawHub Skill: https://clawhub.ai/Lior539/remote-jobs-finder  

This skill lets you ask things like:

- “Find 5 UK remote product manager jobs”
- “Send me 20 more”
- “Only senior roles”
- “Check daily for new matches”

…and get real listings directly in chat.

No dashboards. No slash commands. Fully conversational.

---

## How it works

This integration has **two parts**:

1. A ClawHub **skill** (prompt + behavior)  
2. A one-time OpenClaw **gateway extension** that registers the `rr_jobs_search` tool

ClawHub installs the skill.

The gateway extension lives on your server and only needs to be installed once.

After that, updates are usually just:

```bash
clawhub install remote-jobs-finder
openclaw gateway restart
```

---

# Installation

## 1. Install the skill from ClawHub

```bash
clawhub install remote-jobs-finder
```

---

## 2. One-time server setup: deploy the rr_jobs_search gateway extension

```bash
mkdir -p ~/.openclaw/extensions

cp SERVER_EXTENSION_openclaw_extensions_root/openclaw.plugin.json ~/.openclaw/extensions/openclaw.plugin.json
cp SERVER_EXTENSION_openclaw_extensions_root/index.ts ~/.openclaw/extensions/index.ts

ls -la ~/.openclaw/extensions
```

If you’re inside the bundle folder, you can also run:

```bash
./install-server.sh
```

---

## 3. Enable the extension in OpenClaw

```bash
nano ~/.openclaw/openclaw.json
```

Ensure:

```json
"plugins": {
  "entries": {
    "index": { "enabled": true },
    "whatsapp": { "enabled": true }
  }
}
```

---

## 4. Set RR_API_KEY

```bash
sudo systemctl edit openclaw-gateway.service
```

Paste:

```ini
[Service]
Environment="RR_API_KEY=YOUR_REMOTE_ROCKETSHIP_KEY"
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart openclaw-gateway.service
```

Verify:

```bash
sudo systemctl show openclaw-gateway.service --property=Environment | tr ' ' '\n' | grep RR_API_KEY
```

---

## 5. Restart OpenClaw

```bash
openclaw gateway restart
```

---

## 6. Verify

```bash
openclaw agent --to <your_number> --message "What tools do you currently have available?" --json --verbose on
```

You should see:

```
rr_jobs_search
```

---

# Usage

Examples:

```
Find 5 UK remote product manager jobs
Send me 20 more
Only senior roles
Only contract jobs
```

---

## Optional monitoring

```
Check daily
Monitor hourly
```

---

Enjoy 🚀
