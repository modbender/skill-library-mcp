# ⏱️ Hour Meter (TARDIS on ClawHub)

[![ClawHub](https://img.shields.io/badge/ClawHub-TARDIS-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQyIDAtOC0zLjU4LTgtOHMzLjU4LTggOC04IDggMy41OCA4IDgtMy41OCA4LTggOHoiLz48L3N2Zz4=)](https://clawhub.ai/skills/tardis)
[![GitHub](https://img.shields.io/github/stars/rm289/hour-meter?style=social)](https://github.com/rm289/hour-meter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Note:** This skill was originally published to ClawHub as `hour-meter`. Due to a repository issue that caused the original listing to be deleted, it has been republished under the name **TARDIS**. Same great functionality, cooler name! 🕐

```
╔═══════════════════════════════════════════════════════════════════╗
║   ██╗  ██╗ ██████╗ ██╗   ██╗██████╗                               ║
║   ██║  ██║██╔═══██╗██║   ██║██╔══██╗                              ║
║   ███████║██║   ██║██║   ██║██████╔╝                              ║
║   ██╔══██║██║   ██║██║   ██║██╔══██╗                              ║
║   ██║  ██║╚██████╔╝╚██████╔╝██║  ██║                              ║
║   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝                              ║
║   ███╗   ███╗███████╗████████╗███████╗██████╗                     ║
║   ████╗ ████║██╔════╝╚══██╔══╝██╔════╝██╔══██╗                    ║
║   ██╔████╔██║█████╗     ██║   █████╗  ██████╔╝                    ║
║   ██║╚██╔╝██║██╔══╝     ██║   ██╔══╝  ██╔══██╗                    ║
║   ██║ ╚═╝ ██║███████╗   ██║   ███████╗██║  ██║                    ║
║   ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

**The moments that matter, measured and verified.**

---

**Concept & Design:** Ross ([@rm289](https://github.com/rm289))  
**Implementation:** Claude (OpenClaw Agent)

---

## What is Hour Meter?

Hour Meter is a tamper-evident time tracking skill for OpenClaw. Inspired by the analog Hobbs meters bolted to aircraft engines and industrial equipment, it brings that same reliability to the digital world—with cryptographic proof that your timestamps haven't been altered.

---

## 📸 Screenshots

### Check a meter's status
```
⏱️  Meter: my-career (BETWEEN)
   Career: College graduation → Retirement

   📍 Start:     2024-05-15 14:00:00 UTC
   🎯 End:       2064-05-15 14:00:00 UTC

   [░░░░░░░░░░░░░░░░░░░░] 4.3%

   ✅ Elapsed:   628d 1h 52m (15,074 hrs)
   ⏳ Remaining: 13,981d 22h (335,566 hrs)

   Milestones:
   ○ 25.0%: 📊 25% - Establishing expertise
   ○ 50.0%: 📊 HALFTIME - Peak earning years

   🔒 LOCKED ✓ (integrity verified)
   📋 Paper code: F99B-C7C1-7F3B-2EDF-F
```

### Lock a meter and get your verification code
```
🔒 LOCKED: smoke-free

╔══════════════════════════════════════════════════════════════╗
║  PAPER CODE (write this down):                               ║
║                                                              ║
║     A7F3-B92C-1D4E-8F6A-7                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📋 FOUR WAYS TO SAVE THIS:

   1️⃣  PAPER: Write the code on paper/sticky note
   2️⃣  PHOTO: Screenshot this screen  
   3️⃣  WITNESS FILE: Auto-saved to ~/.openclaw/meter-witness.txt
   4️⃣  EMAIL TO SELF: Click the mailto: link
```

### Career earnings projection
```
📊 Career Inventory Projection
   Based on: my-career
   Started:  2010-05-15

   ⏱️  Hours worked:     55,442 hrs (27.7 yrs)
   ⏳ Hours remaining:  24,558 hrs (12.3 yrs)
   📦 Total inventory:  80,000 hrs (40 yrs)

   [█████████████░░░░░░░] 69.3%

   💰 Current rate:     $85.00/hr
   📈 Annual raise:     2.5%

   🎯 REMAINING EARNING POTENTIAL: $2,409,035
```

---

## ✨ Key Features

### Three Ways to Count

| Mode | Use Case | Example |
|------|----------|---------|
| **Count Up** | Time since an event | Quit smoking: *"142 days clean"* |
| **Count Down** | Time until a deadline | Baby due: *"47 days remaining"* |
| **Count Between** | Journey progress | Career: *"69% complete, 12 years to retirement"* |

### 🔒 Tamper-Evident Locking

Lock any meter to generate a cryptographic integrity hash. If anyone changes the start date later, verification fails. Trust, but verify.

### 📋 Human-Friendly Paper Codes

Forget copying 64-character hex strings. Get a short, checksummed code you can actually write on paper:

```
PAPER CODE: A7F3-B92C-1D4E-8F6A-7
```

The checksum catches typos when you verify. Write it on a sticky note, email it to yourself, or let the witness file sync to your cloud storage.

### 🔔 Milestone Notifications

Set triggers at specific hours or percentages:

- *"Notify me at 1,000 hours smoke-free"*
- *"Alert at 75% of pregnancy complete"*
- *"Ping when career hits 90%"*

Notifications route through any OpenClaw channel—Discord, Telegram, Signal, Slack, and more.

### 📧 Email Milestone Notifications (v1.3.0)

Get milestone alerts sent directly to your inbox:

```bash
meter.py create my-meter \
  --notify-email you@example.com \
  -d "Important milestone tracker"

meter.py milestone my-meter -t hours -v 100 -m "🎉 100 hours reached!"
```

When milestones fire, you get a beautifully formatted email notification!

### 💰 Career Projection Calculator

Visualize your career as **80,000 hours of inventory** (40 years × 2,000 hours/year). See your remaining earning potential with compound annual raises.

---

## 🚀 Quick Start

```bash
# Create a meter
meter.py create smoke-free --start "2025-06-15" -d "Last cigarette"

# Add milestones
meter.py milestone smoke-free -t hours -v 720 -m "🎉 30 days smoke-free!"

# Lock it (get your paper code)
meter.py lock smoke-free

# Check status anytime
meter.py check smoke-free

# Verify with your paper code
meter.py verify smoke-free "A7F3-B92C-1D4E-8F6A-7"
```

---

## 📦 Five Ways to Save Your Verification Code

1. **Paper** — Write the code on a sticky note or in a notebook
2. **Photo** — Screenshot or photograph the lock screen
3. **Witness File** — Auto-saved to `~/.openclaw/meter-witness.txt` (sync to Dropbox/iCloud)
4. **Email (mailto)** — Click the mailto: link or copy the one-liner to send to yourself
5. **Email (SendGrid)** — Auto-send on lock with `--email`:
   ```bash
   export SENDGRID_API_KEY=SG.xxxxx
   meter.py lock my-meter --email you@example.com
   ```

---

## 📡 SendGrid Webhook Server (New in v1.2.0!)

Get real-time notifications when recipients interact with your meter verification emails:

```bash
# Start webhook server with Discord webhook
python sendgrid_webhook.py --port 8089 \
  --discord-webhook https://discord.com/api/webhooks/xxx/yyy

# Events supported:
# ✅ delivered - Email reached recipient
# 👀 open      - Recipient opened email  
# 🔗 click     - Recipient clicked a link
# ⚠️ bounce    - Email bounced
# 🔕 unsubscribe - Recipient unsubscribed
# 🚨 spamreport  - Marked as spam
```

Or process events manually for agent integration:
```bash
python sendgrid_webhook.py --process-events --json
```

### SendGrid Configuration

![SendGrid Webhook Setup](docs/sendgrid-webhook-setup.png)

1. Go to **SendGrid > Settings > Mail Settings > Event Webhook**
2. Enter your webhook URL: `https://your-server.com/webhooks/sendgrid`
3. Select all event types you want to receive
4. Click **"Test Integration"** to verify all events fire correctly
5. **Don't forget to click Save!**

### Exposing Your Webhook (Tunnels)

Since SendGrid needs to reach your webhook server, you'll need a public URL. Here are your options:

**Option 1: Cloudflare Tunnel (Recommended for production)**
```bash
# One-time setup (free Cloudflare account required)
cloudflared tunnel login
cloudflared tunnel create tardis-webhook

# Run the tunnel (permanent URL)
cloudflared tunnel run --url http://localhost:8089 tardis-webhook
```

**Option 2: Temporary Cloudflare Tunnel (No account needed)**
```bash
# Quick & free, but URL changes each restart
cloudflared tunnel --url http://localhost:8089
# Gives you: https://random-words.trycloudflare.com
```

**Option 3: ngrok (Free tier available)**
```bash
# Sign up at ngrok.com for a free auth token
ngrok http 8089
```

After starting your tunnel, update the webhook URL in SendGrid settings.

> **Note:** The unsubscribe functionality works regardless of whether you run the webhook server—SendGrid handles unsubscribes server-side. The webhook just lets you *see* the events for logging and analytics.

### Discord Webhook Setup (Recommended)

For reliable Discord notifications, use a Discord webhook URL directly:

```bash
python sendgrid_webhook.py --port 8089 \
  --discord-webhook "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
```

To create a Discord webhook:
1. **Server Settings** → **Integrations** → **Webhooks**
2. Click **New Webhook**
3. Select your channel and copy the URL

> **Troubleshooting:** If you get HTTP 403 errors, ensure your code includes a `User-Agent` header—Discord/Cloudflare blocks requests without one.

---

## 🎯 Use Cases

- **Quit Tracking** — Smoking, drinking, or any habit you're breaking
- **Career Planning** — Visualize your finite work hours and earning potential
- **Pregnancy Countdown** — Milestones for each trimester
- **Project Hours** — Tamper-evident billing records
- **Equipment Runtime** — Service interval tracking
- **Warranty Dates** — Locked start dates for disputes
- **"Days Since" Displays** — Last incident, last deploy, last vacation

---

## 💡 Why Tamper-Evidence Matters

Anyone can edit a text file with a date. Hour Meter creates a cryptographic proof:

1. When you **lock** a meter, it computes `SHA256(name + timestamp + salt)`
2. You save the resulting code externally (paper, email, cloud)
3. Later, **verify** recomputes the hash and compares

If the timestamp was changed, the hashes won't match. Simple, offline-capable, and human-verifiable.

---

## 📚 Documentation

- [SKILL.md](./SKILL.md) — OpenClaw skill reference
- [WHITEPAPER.md](./WHITEPAPER.md) — Technical deep-dive

---

## 🔒 Security Considerations

**Environment Variables:** `meter.py` will auto-load variables from `~/.env` if `SENDGRID_API_KEY` is not already in the environment. This is opt-in behavior — if you don't use SendGrid email features, no `.env` file is accessed.

**Webhook Server:** `sendgrid_webhook.py` can forward events to a Discord webhook URL or OpenClaw gateway. These are user-configured destinations — the server never sends data anywhere without explicit configuration.

**ACTION: Triggers (Advanced):** Milestone messages can optionally be prefixed with `ACTION:` to signal your agent to execute them as instructions rather than just posting them. This is **not enabled by default** — it requires explicit configuration in your `HEARTBEAT.md`. If you use this feature, ensure your `meters.json` file is protected from unauthorized modification.

**Meter Storage:** Meter data is stored in `~/.openclaw/meters.json`. The tamper-evident locking feature detects unauthorized changes to locked meters, but unlocked meters can be freely modified.

---

## 📄 License

MIT — Use it, modify it, ship it.

---

**TARDIS** — Because some moments are worth proving. ⏱️
