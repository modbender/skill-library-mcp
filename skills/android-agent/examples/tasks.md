# Example Tasks

Real-world tasks you can run with `android-agent`. Copy-paste these directly!

## 📱 Daily Life

```bash
python scripts/run-task.py "Order an Uber to the airport"
python scripts/run-task.py "Set an alarm for 6 AM tomorrow"
python scripts/run-task.py "Check my bank balance on PhonePe"
python scripts/run-task.py "Open Google Maps and navigate to the nearest coffee shop"
python scripts/run-task.py "Call the last number in my recent calls"
```

## 💬 Messaging

```bash
python scripts/run-task.py "Send a WhatsApp message to Mom saying I'll be late for dinner"
python scripts/run-task.py "Read my latest 3 SMS messages"
python scripts/run-task.py "Open Telegram and check unread messages in my first chat"
python scripts/run-task.py "Reply to the last WhatsApp message with 'Sounds good!'"
```

## 🛒 Shopping

```bash
python scripts/run-task.py "Open Amazon and search for wireless earbuds under 2000 rupees"
python scripts/run-task.py "Open Swiggy and order from the first restaurant"
python scripts/run-task.py "Add milk, bread, and eggs to my Instamart cart"
```

## 📅 Productivity

```bash
python scripts/run-task.py "Open Google Calendar and check my schedule for tomorrow"
python scripts/run-task.py "Create a new note in Google Keep titled 'Grocery List' with items: milk, eggs, bread"
python scripts/run-task.py "Open Gmail and read the subject of my latest 3 emails"
```

## 🎵 Entertainment

```bash
python scripts/run-task.py "Play my Discover Weekly playlist on Spotify"
python scripts/run-task.py "Open YouTube and search for lo-fi study music, play the first result"
python scripts/run-task.py "Open Netflix and continue watching my last show"
```

## ⚙️ Settings & Configuration

```bash
python scripts/run-task.py "Turn on Dark Mode"
python scripts/run-task.py "Connect to my home WiFi network"
python scripts/run-task.py "Enable Do Not Disturb mode"
python scripts/run-task.py "Turn off Bluetooth"
python scripts/run-task.py "Increase screen brightness to maximum"
python scripts/run-task.py "Check how much storage is available"
```

## 📸 Utilities

```bash
python scripts/run-task.py "Take a screenshot and save it"
python scripts/run-task.py "Clear all notifications"
python scripts/run-task.py "Open the camera and switch to front-facing"
```

## 💡 Tips

- **Be specific**: "Open Chrome and search for 'best pizza near me'" works better than "find pizza"
- **Use --timeout for long tasks**: `--timeout 180` for app installs or multi-step flows
- **Chain naturally**: Describe the full flow — "Open WhatsApp, find the group 'Family', and send 'Happy birthday!'"
- **Start simple**: Test with "Open Settings" first to verify your setup works
