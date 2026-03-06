# OpenClaw macOS Always-On

**Keep OpenClaw running 24/7 on macOS - even when your screen is locked for hours!**

[![macOS](https://img.shields.io/badge/macOS-10.15+-blue.svg)](https://www.apple.com/macos/)
[![Tested](https://img.shields.io/badge/tested-macOS%2014.4-success.svg)](https://github.com/happydog-intj/openclaw-macos-always-on)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

English | [简体中文](README.zh-CN.md)

## 🎯 Problem Solved

By default, macOS suspends user processes when you lock your screen, causing your OpenClaw bot to stop responding to messages. This project provides a **tested and verified** solution using LaunchDaemon + caffeinate.

**Verified Working:**
- ✅ Screen locked for 30+ minutes
- ✅ macOS 14.4 (and earlier versions)
- ✅ Both Intel and Apple Silicon Macs

## 🚀 Quick Install

One-line installation:

```bash
curl -fsSL https://raw.githubusercontent.com/happydog-intj/openclaw-macos-always-on/master/install.sh | bash
```

Or manual installation - see [SKILL.md](./SKILL.md) for detailed instructions.

## ✨ What This Does

Converts OpenClaw from a user-level LaunchAgent to a system-level LaunchDaemon with these enhancements:

| Feature | Before (LaunchAgent) | After (LaunchDaemon + caffeinate) |
|---------|---------------------|----------------------------------|
| **Screen locked** | ❌ Suspends after ~10min | ✅ Runs indefinitely |
| **User logged out** | ❌ Stops | ✅ Continues running |
| **Boot startup** | At login | At system boot |
| **Priority** | User-level | System-level |
| **Sleep prevention** | None | `caffeinate -s` |

## 🔧 How It Works

The solution uses three key components:

1. **LaunchDaemon** - System-level service (runs as your user but managed by system launchd)
2. **caffeinate** - macOS utility that prevents system sleep while keeping display sleep enabled
3. **Enhanced KeepAlive** - Network-aware restart with crash recovery

```xml
<!-- Key configuration -->
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/caffeinate</string>
  <string>-s</string>  <!-- Prevent system sleep -->
  <string>/opt/homebrew/bin/node</string>
  <string>.../openclaw/dist/index.js</string>
  <string>gateway</string>
</array>
```

## 📋 Requirements

- **macOS 10.15+** (tested on 14.4)
- **Admin access** (sudo required for installation)
- **OpenClaw already installed** (`npm install -g openclaw`)

## 📖 Documentation

- [SKILL.md](./SKILL.md) - Complete documentation with troubleshooting
- [install.sh](./install.sh) - Automated installation script

## 🧪 Testing

After installation, test with different lock durations:

```bash
# Test 1: Lock screen immediately
pmset displaysleepnow
# Send "ping" from your phone - should get instant reply

# Test 2: Lock for 30+ minutes
# Bot should still respond
```

## 📊 Verification

Check if caffeinate is working:

```bash
# See caffeinate process
ps aux | grep caffeinate | grep -v grep

# Check power assertions
pmset -g assertions | grep caffeinate
```

You should see:
```
pid XXXXX(caffeinate): PreventSystemSleep named: "caffeinate command-line tool"
  Details: caffeinate asserting on behalf of '/opt/homebrew/bin/node' (pid XXXXX)
```

## 🔄 Management Commands

```bash
# Restart service
sudo launchctl kickstart -k system/ai.openclaw.gateway

# Stop service
sudo launchctl bootout system/ai.openclaw.gateway

# View logs
tail -f ~/.openclaw/logs/gateway.log

# Check status
sudo launchctl print system/ai.openclaw.gateway
```

## 🔓 Uninstall

```bash
# Stop and remove
sudo launchctl bootout system/ai.openclaw.gateway
sudo rm /Library/LaunchDaemons/ai.openclaw.gateway.plist

# Optional: Restore LaunchAgent
mv ~/Library/LaunchAgents/ai.openclaw.gateway.plist.disabled \
   ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

## ⚡ Performance Impact

- **Idle**: ~50MB RAM, <1% CPU
- **Active**: ~100MB RAM, varies by task
- **Battery**: Prevents system sleep (OK for desktops, may impact laptop battery when unplugged)

## 🐛 Troubleshooting

**Service won't start?**
```bash
tail -50 ~/.openclaw/logs/gateway.err.log
```

**Still suspends after lock?**
- Verify caffeinate is running: `ps aux | grep caffeinate`
- Check power assertions: `pmset -g assertions`
- Ensure you used the latest install script

**Port conflict?**
```bash
lsof -i :18789
kill -9 <PID>
```

See [SKILL.md](./SKILL.md#troubleshooting) for more solutions.

## 🤝 Contributing

Found an issue or improvement? Pull requests welcome!

1. Fork the repository
2. Create your feature branch
3. Test on your Mac
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built for [OpenClaw](https://github.com/openclaw/openclaw)
- Tested and verified by the community
- Special thanks to contributors who tested on different macOS versions

## 🔗 Related Projects

- [OpenClaw](https://github.com/openclaw/openclaw) - The AI assistant this skill enables
- [Clawhub](https://clawhub.com) - OpenClaw skills marketplace

---

**Made with ❤️ for OpenClaw users who want 24/7 bot availability on macOS**
