# OpenClaw Menubar Skill

**Quick access to OpenClaw from your macOS menu bar!**

## What is this?

This skill adds OpenClaw as a native macOS menu bar app. Click the icon in your menu bar to instantly chat with your AI assistant - no need to open a browser tab.

**✅ macOS only** (requires macOS with menu bar support)

---

## Installation

### 1. Extract the package
```bash
cd ~/Downloads
tar -xzf menubar-skill.tar.gz
```

### 2. Copy to your OpenClaw workspace
```bash
cp -r menubar ~/.openclaw/workspace/skills/
```

### 3. Install the menubar app
```bash
cd ~/.openclaw/workspace/skills/menubar/assets/openclaw-menubar
npm install
```

### 4. Ask OpenClaw to enable it
In any OpenClaw session (web dashboard, WhatsApp, Telegram, etc.), send:
```
enable menubar
```

or

```
add openclaw to my menu bar
```

OpenClaw will launch the menubar app for you!

---

## Usage

- **Click the menu bar icon** → popup chat window opens
- **Type and chat** → just like the web dashboard
- **Always accessible** → no browser tab needed
- **Auto-reconnects** → stays connected to your gateway

---

## Requirements

- macOS (10.14+)
- OpenClaw gateway running
- Node.js installed (for npm install step)

---

## Troubleshooting

**App won't start?**
```bash
cd ~/.openclaw/workspace/skills/menubar/assets/openclaw-menubar
npm start
```

**Can't find gateway?**
Make sure your OpenClaw gateway is running:
```bash
openclaw gateway status
```

---

## Questions?

Ask your OpenClaw assistant for help!
