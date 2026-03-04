# 🛡️ MaclawPro Security - OpenClaw Skill

**Comprehensive macOS security monitoring for OpenClaw**

Created by certified cybersecurity experts.

---

## 🎯 **What is this?**

MaclawPro Security brings **52+ professional macOS security tasks** to OpenClaw, enabling you to monitor and protect your Mac through simple commands.

**Use cases:**
- 📹 Monitor camera/microphone access in real-time
- 🔥 Check firewall status and open ports
- 🌐 Verify VPN connection and DNS security
- 📡 Scan WiFi networks for security risks
- 🛑 Block malicious apps instantly
- 🔐 Audit system permissions and encryption

---

## 🚀 **Installation**

```bash
# Via npm
npm install openclaw-macos-security

# Or via OpenClaw CLI (if supported)
openclaw skill install openclaw-macos-security
```

---

## 💬 **Usage**

### **Basic Commands**

```
/camera-status          Check which apps use camera
/microphone-status      Check microphone access
/firewall-status        Verify firewall is enabled
/vpn-checker            Check VPN connection
/open-ports             List open network ports
/wifi-scanner           Scan WiFi security
/block-app <name>       Block malicious app
```

### **Examples**

```
User: /camera-status
MaclawPro: 🔴 CAMERA ACTIVE
           Zoom is using your camera right now
           [Block] [Revoke Permission]

User: /firewall-status
MaclawPro: ✅ FIREWALL ENABLED
           Your Mac is protected!

User: /block-app Malware
MaclawPro: 🚨 BLOCKED
           Malware.app moved to Trash
```

---

## 📋 **Full Command List**

### **Monitoring (Real-Time)**
- `camera-status` - Active camera usage
- `microphone-status` - Microphone access
- `location-status` - GPS tracking apps

### **Network Security**
- `firewall-status` - Firewall configuration
- `vpn-checker` - VPN status (with leak detection)
- `open-ports` - Listening ports
- `wifi-scanner` - WiFi encryption analysis
- `ssh-connections` - Active SSH sessions
- `network-connections` - All network activity

### **System Hardening**
- `gatekeeper-sip-status` - SIP & Gatekeeper
- `screen-lock-status` - Auto-lock settings
- `sharing-status` - File/screen sharing
- `update-checker` - macOS security updates

### **Threat Detection**
- `clipboard-monitor` - Clipboard security
- `dns-leak-test` - DNS privacy check
- `keylogger-detector` - Keylogger scan
- `network-sniff-detector` - Packet capture detection
- `rootkit-scanner` - System integrity check

### **System Audit**
- `permission-audit` - App permissions review
- `launch-daemon-audit` - Startup items
- `bluetooth-audit` - Bluetooth security
- `browser-extensions` - Extension safety

### **App Management**
- `block-app <name>` - Block/remove app
- `installed-apps` - List all apps
- `uninstall <name>` - Remove app

---

## 🔒 **Security & Privacy**

**This skill requires the following permissions:**
- `exec` - Run macOS security commands (lsof, ps, etc.)
- `fs.read` - Read TCC database for permissions
- `network` - Check network connections

**All monitoring data stays on your Mac.** No data is sent to external servers.

---

## 🎓 **About MaclawPro**

MaclawPro is developed by certified cybersecurity experts with:
- 🏅 Professional wireless network security certification
- 💼 Years of Mac security experience
- 🌐 Serving businesses and individuals worldwide

**Learn more:**
- 🌐 [maclawpro.com](https://maclawpro.com) - Full standalone version

---

## ⭐ **Upgrade to MaclawPro Standalone**

This OpenClaw skill provides **basic monitoring**. For advanced features:

**MaclawPro Full Version includes:**
- ✅ Real-time alerts (Telegram, Email, Slack)
- ✅ Web dashboard with analytics
- ✅ Multi-channel notifications
- ✅ Alert history and reports
- ✅ Automated threat blocking
- ✅ 24/7 background monitoring

**Pricing:**
- Free: Basic monitoring
- Pro: $49/year - Full features
- Business: $99/month - Multi-Mac licensing

[Get MaclawPro →](https://maclawpro.com/pricing)

---

## 🤝 **Support**

- 🌐 Website: [maclawpro.com](https://maclawpro.com)
- 🐛 Issues: [GitHub Issues](https://github.com/drg3nz0/maclaw-openclaw-skill/issues)
- 💬 Discord: [OpenClaw Community](https://discord.gg/openclaw)

---

## 📄 **License**

MIT © MaclawPro

---

**Professional macOS security monitoring**
