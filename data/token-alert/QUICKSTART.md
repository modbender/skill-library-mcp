# Token Alert - Quick Start Guide

**Status:** ✅ Production Ready (v1.2.0)  
**Date:** 2026-01-27

---

## Installation

### Via ClawdHub
```bash
clawdhub install token-alert
```

### Manual
```bash
cd ~/clawd/skills
git clone https://github.com/r00tid/clawdbot-token-alert token-alert
```

---

## Usage

### 1. CLI Check (Terminal)

**Basic check:**
```bash
python3 ~/clawd/skills/token-alert/scripts/check.py
```

**Output:**
```
🟢 Token Status

🟢 ▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱ 9.0%
94,000 / 1,000,000 Tokens verwendet

📊 Status: Alles im grünen Bereich!
💡 Verbleibend: ~906k Tokens
⏰ Geschätzte Sessions: ~18 weitere
```

---

### 2. Ask Clawdbot

**In Chat:**
- "Check token status"
- "Wie viele Tokens habe ich noch?"
- "Token usage?"

Grym führt automatisch `check.py` aus und zeigt den Status.

---

### 3. Dashboard (HTML)

**Launch:**
```bash
python3 ~/clawd/skills/token-alert/scripts/show_dashboard.py
```

Opens interactive dashboard in browser with:
- Real-time token usage
- Visual progress bars
- Session estimates
- Light/Dark theme

---

### 4. macOS Notifications (Optional)

**Setup:**
```bash
bash ~/clawd/skills/token-alert/scripts/setup-notifications.sh
```

**Requirements:**
- macOS 12+ (Monterey)
- Terminal notification permissions enabled

**What it does:**
- Installs `terminal-notifier`
- Checks tokens every 5 minutes
- Sends native macOS popup when thresholds reached (25%, 50%, 75%, 90%, 95%)

**Note:** If notifications don't appear, enable in:  
`System Preferences → Notifications → Terminal → Allow Notifications`

---

## Alert Thresholds

| Level | % Range | Exit Code | Emoji | Action |
|-------|---------|-----------|-------|--------|
| **OK** | 0-24% | 0 | 🟢 | Continue normally |
| **LOW** | 25-49% | 1 | 🟡 | Keep monitoring |
| **MEDIUM** | 50-74% | 2 | 🟠 | Work token-efficiently |
| **HIGH** | 75-89% | 3 | 🔶 | Prepare new session |
| **CRITICAL** | 90-94% | 4 | 🔴 | Save memory NOW |
| **EMERGENCY** | 95-100% | 5 | 🚨 | Start new session! |

---

## Integration with Clawdbot

### Heartbeat (Automatic)

Add to `~/clawd/HEARTBEAT.md`:

```markdown
### Token Usage Check
- [ ] `python3 ~/clawd/skills/token-alert/scripts/check.py`
- **Warning ab 70%:** Token-sparend arbeiten
```

Grym will check automatically during heartbeats.

---

## How It Works

1. **Reads Clawdbot Status:**  
   Runs `clawdbot status` → parses session token usage

2. **Calculates Percentage:**  
   `used / limit * 100`

3. **Checks Thresholds:**  
   Compares against 6 levels (25%, 50%, 75%, 90%, 95%, 100%)

4. **Formats Output:**  
   Material Design progress bar + recommendations

5. **Returns Exit Code:**  
   0-5 based on severity (for scripting)

---

## Files

```
skills/token-alert/
├── QUICKSTART.md              # This file
├── README.md                  # Full documentation
├── SKILL.md                   # Clawdbot skill definition
├── LICENSE                    # MIT License
├── scripts/
│   ├── check.py               # CLI checker (main)
│   ├── notify.sh              # macOS notification wrapper
│   ├── setup-notifications.sh # Auto-setup script
│   ├── dashboard.html         # HTML dashboard
│   └── show_dashboard.py      # Dashboard launcher
└── com.clawdbot.token-alert.plist  # LaunchAgent config
```

---

## Troubleshooting

### No notifications on macOS

**Fix:**
1. System Preferences → Notifications
2. Find "Terminal" in list
3. Enable "Allow Notifications"
4. Test: `terminal-notifier -title Test -message Hi`

### CLI shows 0%

**Cause:** Not in active Clawdbot session

**Fix:** Run from within Clawdbot chat (ask Grym to check)

### Dashboard doesn't load

**Fix:**
```bash
# Check if Python 3 installed
python3 --version

# Re-run launcher
python3 ~/clawd/skills/token-alert/scripts/show_dashboard.py
```

---

## Next Steps

- ✅ **Test CLI:** Run `check.py` to see current usage
- ✅ **Ask Grym:** "Check token status" in chat
- ✅ **Setup Heartbeat:** Add to HEARTBEAT.md for auto-checks
- ⏳ **Enable Notifications:** Run `setup-notifications.sh` (optional)

---

## Support

- **Issues:** https://github.com/r00tid/clawdbot-token-alert/issues
- **Docs:** https://docs.clawd.bot
- **ClawdHub:** https://clawdhub.com/skills/token-alert

---

Built with ❤️ by Grym 🥜  
**Version:** 1.2.0 | **Status:** Production Ready ✅
