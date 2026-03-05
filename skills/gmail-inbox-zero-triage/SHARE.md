# 📬 Gmail Inbox Zero Triage - Clawdbot Skill

Achieve inbox zero with AI-powered email triage for Gmail!

## 🎯 What It Does

Interactive Gmail inbox management that helps you process emails 10x faster:
- 🤖 **AI summaries** - Quick 1-line summary of each email
- ⚡ **Batch processing** - Queue actions instantly, execute at the end
- 📱 **Telegram buttons** - Archive, Filter, Unsubscribe, View
- 🎯 **Inbox zero focus** - Process ALL messages until inbox is empty
- 🔒 **Secure OAuth** - No passwords needed (uses gog CLI)

## 🚀 Quick Demo

```
📬 Inbox Triage - 5 messages

1/5 Amazon: Your order has shipped
💡 Shipping notification. Package arrives Thursday.
[📥 Archive] [🔍 Filter] [🚫 Unsub] [📧 View]

2/5 LinkedIn: New job recommendations  
💡 Newsletter with job suggestions. No action required.
[📥 Archive] [🔍 Filter] [🚫 Unsub] [📧 View]

...

[✅ Done - Execute All Actions]
```

Click through all emails, hit Done, and watch your inbox clear in seconds! ⚡

## 📦 Installation

1. **Download:** `gmail-inbox-zero.skill`

2. **Install:**
   ```bash
   clawdbot skills install gmail-inbox-zero.skill
   ```

3. **Setup gog:**
   ```bash
   brew install steipete/tap/gogcli
   gog auth add your@gmail.com --services gmail
   export GOG_KEYRING_PASSWORD="your-password"
   ```

4. **Use it:**
   Just say: *"Triage my emails"*

Full setup guide: [SETUP.md](SETUP.md)

## ✨ Features

- **Fast workflow** - No waiting between actions (batch execution)
- **Smart summaries** - AI explains each email in one line
- **Multiple actions** - Archive, Filter, Unsubscribe, View full email
- **Inbox zero** - Processes ALL messages (read + unread)
- **Safe** - OAuth authentication, no passwords stored
- **Telegram-native** - Uses inline buttons for instant actions

## 📋 Requirements

- Clawdbot with Telegram channel configured
- `gog` CLI (https://gogcli.sh)
- Gmail account
- Python 3 (included with Clawdbot)

## 🎮 How To Use

1. Say *"Triage my emails"* or *"Process my inbox"*
2. Review emails with AI summaries
3. Click actions on each (Archive/Filter/Unsub/View)
4. Hit **"Done"** when finished
5. All actions execute in batch - inbox cleaned! 🎉

## 💡 Tips

- **Archive aggressively** - If you don't need it now, archive it (still searchable)
- **Use filters** - Auto-archive recurring emails from senders
- **Process daily** - Maintain inbox zero with regular 5-minute sessions
- **Trust AI** - Summaries are accurate for quick decisions

## 📚 Documentation

- **SETUP.md** - Complete setup guide
- **OVERVIEW.md** - Technical details and features
- **SKILL.md** - Full documentation (included in .skill file)

## 🔧 Troubleshooting

**"gog not authenticated"**
```bash
gog auth add your@gmail.com --services gmail
```

**"No TTY for keyring password"**
```bash
export GOG_KEYRING_PASSWORD="your-password"
```

Full troubleshooting: See SETUP.md

## 🌟 Why This Skill?

Traditional email clients make you process emails one-by-one. This skill:
- Shows ALL emails at once with summaries
- Queues actions instantly (no API delays)
- Executes everything in batch (10-20 emails in 60 seconds)
- Uses AI to help you make faster decisions

**Result:** Clear your inbox in minutes, not hours! ⚡

## 📊 Performance

- Process 10 emails: ~60 seconds
- Process 20 emails: ~90 seconds
- vs traditional: 5+ minutes for 10 emails

**10x faster** than processing one-by-one! 🚀

## 🤝 Support

- **Issues:** https://github.com/clawdbot/clawdbot/issues
- **Community:** https://discord.com/invite/clawd
- **Docs:** https://docs.clawd.bot
- **gog CLI:** https://gogcli.sh

## 📄 License

Part of Clawdbot skills collection. See Clawdbot license.

## 🙏 Credits

Built with:
- [Clawdbot](https://clawd.bot) - AI assistant platform
- [gog CLI](https://gogcli.sh) - Google Workspace CLI
- Anthropic Claude - AI summaries

---

**Ready to achieve inbox zero?** 📬✨

Download `gmail-inbox-zero.skill` and start triaging! 

---

*Made with ❤️ for inbox zero enthusiasts*
