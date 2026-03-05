# Protocols — Remote Desktop

## RDP (Remote Desktop Protocol)

**Best for:** Windows targets, enterprise environments

### Clients

| Tool | Platform | Install |
|------|----------|---------|
| xfreerdp | Linux | `apt install freerdp2-x11` |
| rdesktop | Linux (legacy) | `apt install rdesktop` |
| Remmina | Linux (GUI) | `apt install remmina` |
| Microsoft Remote Desktop | macOS | App Store |
| mstsc | Windows | Built-in |

### xfreerdp Common Flags

```bash
xfreerdp /v:HOST /u:USER /p:PASS \
  /size:1920x1080 \        # Resolution
  /dynamic-resolution \     # Auto-resize
  /clipboard \              # Enable clipboard
  /sound:sys:alsa \         # Audio
  /drive:share,/home/user \ # Share folder
  /sec:tls \                # Force TLS
  /cert:ignore              # Skip cert validation (use carefully)
```

### NLA (Network Level Authentication)

Modern Windows requires NLA. If connection fails immediately:
```bash
xfreerdp /v:HOST /u:USER /sec:nla  # Force NLA
xfreerdp /v:HOST /u:USER /sec:tls  # Try TLS instead
```

## VNC (Virtual Network Computing)

**Best for:** Linux desktops, macOS, persistent sessions

### Servers

| Server | Platform | Notes |
|--------|----------|-------|
| TigerVNC | Linux | Most common |
| x11vnc | Linux | Shares existing display |
| vino | GNOME | Built into GNOME |
| wayvnc | Wayland | For Wayland compositors |
| Screen Sharing | macOS | Built-in VNC |

### Starting a VNC Server

```bash
# TigerVNC - new display
vncserver :1 -geometry 1920x1080
# Connect to: HOST:5901

# x11vnc - share existing display
x11vnc -display :0 -forever -shared
# Connect to: HOST:5900

# Kill VNC server
vncserver -kill :1
```

### VNC Clients

```bash
# TigerVNC viewer
vncviewer HOST:5901

# With compression
vncviewer -encoding tight -quality 5 HOST:5901

# Full screen
vncviewer -fullscreen HOST:5901
```

### VNC Security

VNC has weak native encryption. Always tunnel:
```bash
# On client
ssh -L 5901:localhost:5901 user@HOST
vncviewer localhost:5901
```

## SSH X11 Forwarding

**Best for:** Running single GUI apps remotely

### Setup

**Server side** (`/etc/ssh/sshd_config`):
```
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes
```

**Client side:**
```bash
# Untrusted (more secure)
ssh -X user@HOST firefox

# Trusted (faster, full access)
ssh -Y user@HOST firefox
```

### Compression

For slow connections:
```bash
ssh -X -C user@HOST firefox  # Enable compression
```

### Wayland Note

X11 forwarding doesn't work with Wayland natively. Options:
1. Start Xwayland app: `GDK_BACKEND=x11 firefox`
2. Use VNC instead
3. Use waypipe (experimental): `waypipe ssh user@HOST firefox`

## Modern Solutions

| Tool | Protocol | Best For |
|------|----------|----------|
| NoMachine | NX | High performance, LAN |
| Parsec | Proprietary | Gaming, low latency |
| AnyDesk | Proprietary | Cross-platform ease |
| RustDesk | Open source | Self-hosted, privacy |
| Chrome Remote Desktop | WebRTC | Quick setup, browser |

### RustDesk (Self-Hosted)

```bash
# Server setup
docker run -d --name rustdesk-server \
  -p 21115:21115 -p 21116:21116 -p 21117:21117 \
  -p 21118:21118 -p 21119:21119 \
  rustdesk/rustdesk-server

# Client connects via ID
```
