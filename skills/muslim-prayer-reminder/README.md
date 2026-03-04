# 🕌 Prayer Times - Automated Salat Reminders for OpenClaw

Never forget about the most important thing in your day and life. **Prayer is your first priority.**

This OpenClaw skill provides accurate Islamic prayer times for any location worldwide, with automated background reminders that ensure you never miss Salat - even during busy conversations.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

## ✨ Features

### 🌍 Global Prayer Times
- **20+ countries** with official calculation methods
- **Any location** - city/country or GPS coordinates
- **Automatic method selection** - no manual configuration
- **Next prayer countdown** - know exactly when Salat is coming
- **Specific date support** - plan ahead for travel

### 🔔 Automated Background Reminders
The core feature that makes this special:

- **10 minutes before** - "🕌 Salat approaching: Asr in 10 minutes (16:43)"
- **At prayer time** - "🕌 Salat First: Asr time is now (16:43)"
- **5 minutes after** - "🕌 Salat reminder: Asr started 5 minutes ago (16:43)"

**Works during conversations** - No need to ask. The reminders appear automatically while you're chatting, ensuring you never forget.

**Set up once, works forever** - Updates daily automatically via cron jobs. Zero maintenance required.

### 🌐 Supported Countries

Automatically uses official calculation methods for:

🇲🇦 Morocco | 🇸🇦 Saudi Arabia | 🇪🇬 Egypt | 🇹🇷 Turkey | 🇦🇪 UAE | 🇰🇼 Kuwait | 🇶🇦 Qatar | 🇯🇴 Jordan | 🇩🇿 Algeria | 🇹🇳 Tunisia

Plus 10+ more countries with Muslim World League as default fallback.

## ⚠️ CRITICAL: Read This First

**[CRITICAL_SETUP.md](CRITICAL_SETUP.md)** - Essential guide to ensure prayer reminders NEVER fail.

Prayer is not optional. The reminder system must be 100% reliable. Read the critical setup guide to:
- Verify cron jobs at every session
- Test the system properly
- Fix issues immediately if something breaks

**Don't skip this.** Missing a prayer reminder is a critical failure.

## 📦 Installation

### Prerequisites
- [OpenClaw](https://openclaw.ai) installed and running
- Internet connection (for AlAdhan API)

### Install the Skill

**Option 1: Direct Install (from GitHub)**
```bash
git clone https://github.com/diepox/openclaw-prayer-times.git
cd openclaw-prayer-times
# Copy to your OpenClaw skills directory
cp -r . ~/.openclaw/skills/prayer-times/
```

**Option 2: Via OpenClaw CLI**
```
/skill install prayer-times.skill
```

## 🚀 Quick Start

### 1. Query Prayer Times

Just ask OpenClaw:

```
What are the prayer times in Rabat today?
When is the next prayer?
Show me prayer times for Mecca
What are the prayer times in Cairo on March 15, 2026?
```

**Example Output:**
```
📍 Mecca, Saudi Arabia
📆 10 Feb 2026
🌙 22-08-1447
🔢 Method: 4

🕌 Fajr     05:37
🌅 Sunrise  06:54
🕌 Dhuhr    12:35
🕌 Asr      15:50
🕌 Maghrib  18:16
🕌 Isha     19:46

⏳ Next: Maghrib at 18:16 (in 15 minutes)
```

### 2. Set Up Automated Reminders

This is where the magic happens. One command sets up everything:

```
Set up prayer time reminders for [Your City], [Your Country] (GMT+[offset]). 
Fetch daily at midnight and check every 5 minutes.
```

**Examples:**
```
Set up prayer time reminders for Mecca, Saudi Arabia (GMT+3). 
Fetch daily at midnight and check every 5 minutes.
```

```
Set up prayer time reminders for Istanbul, Turkey (GMT+3). 
Fetch daily at midnight and check every 5 minutes.
```

**That's it!** Two cron jobs are created:
1. **Daily fetch** (midnight) - Gets fresh prayer times for your location
2. **Reminder check** (every 5 min) - Alerts you when it's time

**From now on, you'll receive automatic reminders** - even while chatting about completely different topics.

## 📖 Documentation

### Core Files

- **[SKILL.md](SKILL.md)** - Complete skill documentation and usage guide
- **[setup-reminders.md](references/setup-reminders.md)** - Detailed reminder setup guide
- **[methods.md](references/methods.md)** - Calculation methods for all countries
- **[example-cron-jobs.json](references/example-cron-jobs.json)** - Copy-paste cron templates

### Scripts

- **[get_prayer_times.py](scripts/get_prayer_times.py)** - Query prayer times for any location
- **[check_prayer_reminder.py](scripts/check_prayer_reminder.py)** - Automated reminder checker
- **[fetch_prayer_times.py](scripts/fetch_prayer_times.py)** - Morocco-specific fetcher (legacy)

## 🎯 Use Cases

- **Daily reminders** - Never miss Salat during work, study, or conversations
- **Travel planning** - Check prayer times before trips
- **Multi-location monitoring** - Track times for family in different cities
- **Ramadan preparation** - Accurate Iftar and Suhoor times
- **Mosque coordination** - Sync with local prayer schedules

## 🔧 Advanced Configuration

### Custom Calculation Method

By default, the skill auto-selects the correct method for your country. To override:

```bash
python3 scripts/get_prayer_times.py --city London --country UK --method 2
```

See [methods.md](references/methods.md) for all available methods.

### Adjust Reminder Frequency

Default is every 5 minutes. To change:

```javascript
// In your cron job configuration
"everyMs": 300000  // 5 minutes (default)
"everyMs": 120000  // 2 minutes (more frequent)
"everyMs": 600000  // 10 minutes (less frequent)
```

See [setup-reminders.md](references/setup-reminders.md) for complete guide.

## 🌐 Network Considerations

The skill uses the [AlAdhan API](https://aladhan.com/prayer-times-api) which may be unreachable from some datacenter IPs due to routing issues.

**Solution:** If you're running OpenClaw on a VPS/datacenter, you may need Cloudflare WARP VPN:

```bash
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt update && sudo apt install cloudflare-warp
warp-cli register
warp-cli connect
```

See [SKILL.md](SKILL.md) for more details.

## 💰 Cost Estimate

Running automated reminders costs approximately:

- **Daily fetch:** ~500-800 tokens/day
- **Reminder checks:** ~60K tokens/day
- **Total:** ~$1.80-2.00/month (at $0.03/1K tokens)

**Worth every cent** to never miss Salat! 🤲

## 🤝 Contributing

Contributions are welcome! Whether it's:

- Adding support for more calculation methods
- Improving documentation
- Fixing bugs
- Translating to other languages

Please feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **API Provider:** [AlAdhan](https://aladhan.com) / Islamic Network
- **Creator:** L'Modir ([OpenClaw](https://openclaw.ai))
- **Framework:** [OpenClaw](https://openclaw.ai) - AI agent framework

## 🌟 Support

- **Documentation:** [docs.openclaw.ai](https://docs.openclaw.ai)
- **Community:** [Discord](https://discord.com/invite/clawd)
- **Issues:** [GitHub Issues](https://github.com/diepox/openclaw-prayer-times/issues)

## ⭐ Star This Repo

If this skill helps you maintain your Salat, please ⭐ star this repo to help others discover it!

---

**Made with ❤️ for the Muslim community**

> "Indeed, prayer has been decreed upon the believers at specified times." - Quran 4:103

May Allah accept your prayers 🤲 Alhamdulillah!
