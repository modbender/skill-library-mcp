---
name: Remote Desktop
slug: remote-desktop
version: 1.0.0
homepage: https://clawic.com/skills/remote-desktop
description: Connect to remote desktops via RDP, VNC, and SSH X11 with secure tunneling and troubleshooting.
metadata: {"clawdbot":{"emoji":"🖥️","requires":{"bins":["ssh"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines and help the user with their question.

## When to Use

User needs remote desktop access to another machine. Agent handles protocol selection, connection commands, tunnel setup, and troubleshooting display issues.

## Architecture

Config lives in `~/remote-desktop/`. See `memory-template.md` for structure.

```
~/remote-desktop/
├── memory.md         # Saved hosts, preferences
└── hosts/            # Per-host connection profiles
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Protocol details | `protocols.md` |
| Troubleshooting | `troubleshooting.md` |

## Core Rules

### 1. Protocol Selection
| Target OS | Best Protocol | Why |
|-----------|---------------|-----|
| Windows | RDP | Native, best performance |
| Linux (desktop) | VNC or X11 | VNC for persistent, X11 for apps |
| macOS | VNC (built-in) | Screen Sharing uses VNC |
| Headless Linux | SSH + X11 forwarding | No desktop needed |

### 2. Security First
- Always prefer SSH tunneling over direct exposure
- Never expose RDP (3389) or VNC (5900) to internet directly
- Use SSH keys, not passwords
- If direct needed, use VPN or firewall rules

### 3. Connection Commands

**RDP to Windows:**
```bash
# xfreerdp (recommended)
xfreerdp /v:HOST /u:USER /p:PASS /size:1920x1080 /dynamic-resolution

# With SSH tunnel first
ssh -L 3389:localhost:3389 user@jumphost
xfreerdp /v:localhost /u:USER
```

**VNC:**
```bash
# Direct (NOT recommended for internet)
vncviewer HOST:5901

# Via SSH tunnel (recommended)
ssh -L 5901:localhost:5901 user@HOST
vncviewer localhost:5901
```

**SSH X11 forwarding:**
```bash
# Single app
ssh -X user@HOST firefox

# Trusted (faster, less secure)
ssh -Y user@HOST
```

### 4. Port Defaults
| Protocol | Default Port | Display :0 | Display :1 |
|----------|--------------|------------|------------|
| RDP | 3389 | 3389 | - |
| VNC | 5900 | 5900 | 5901 |
| SSH | 22 | - | - |
| NoMachine | 4000 | 4000 | - |

### 5. Tunnel Everything
For any remote desktop over internet:
```bash
# Local port forward
ssh -L LOCAL_PORT:TARGET:REMOTE_PORT user@JUMPHOST

# Example: RDP via jumphost
ssh -L 13389:windows-pc:3389 user@jumphost
xfreerdp /v:localhost:13389 /u:USER
```

### 6. Clipboard and Files
| Tool | Clipboard | File Transfer |
|------|-----------|---------------|
| xfreerdp | `/clipboard` flag | `/drive:share,/path` |
| vncviewer | Usually works | Separate SCP/SFTP |
| SSH X11 | Needs xclip setup | SCP/SFTP |

### 7. Save Working Configs (with consent)
When a connection works, ask "Want me to save this config for next time?" If yes, save to `~/remote-desktop/hosts/`:
```markdown
# hostname.md
host: 192.168.1.50
protocol: rdp
user: admin
tunnel: ssh user@jumphost -L 3389:192.168.1.50:3389
resolution: 1920x1080
notes: Windows 11 dev machine
```
Never save passwords — only hostnames, users, and connection flags.

## Common Traps

- **Black screen after VNC connect** → Display manager not running or wrong display number. Try `:1` instead of `:0`, or start a VNC server: `vncserver :1`
- **RDP disconnects immediately** → Check Network Level Authentication (NLA) settings, or add `/sec:tls` to xfreerdp
- **X11 forwarding not working** → Ensure `X11Forwarding yes` in server's `/etc/ssh/sshd_config` and `ForwardX11 yes` in client config
- **Slow VNC performance** → Use tighter encodings: `vncviewer -encoding tight HOST:1`
- **"Connection refused"** → Service not running, firewall blocking, or wrong port. Check with `ss -tlnp | grep PORT`
- **Clipboard not syncing** → xfreerdp needs `/clipboard`, VNC needs vncconfig running

## Security & Privacy

**Data that stays local:**
- Host configurations in `~/remote-desktop/` (with user consent)
- Connection preferences

**This skill does NOT:**
- Store passwords in plain text — use SSH keys or system keyring
- Auto-save configs without asking first
- Connect to hosts without explicit user command
- Make any network requests itself (you run the commands)
- Access any memory outside `~/remote-desktop/`

**Before saving a host profile:** Always ask "Want me to save this config for next time?"

## Scope

This skill ONLY:
- Provides commands for remote desktop connections
- Helps troubleshoot display and connection issues
- Saves host profiles locally

This skill NEVER:
- Stores credentials in plain text
- Auto-connects to anything
- Modifies SSH or system configs without explicit instruction

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `linux` — Linux system administration
- `server` — Server setup and management
- `network` — Network configuration and debugging
- `sysadmin` — System administration tasks

## Feedback

- If useful: `clawhub star remote-desktop`
- Stay updated: `clawhub sync`
