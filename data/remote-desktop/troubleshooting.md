# Troubleshooting — Remote Desktop

## Connection Refused

**Symptom:** "Connection refused" or timeout

**Causes:**
1. Service not running
2. Firewall blocking
3. Wrong port

**Diagnosis:**
```bash
# Check if service is listening (on target)
ss -tlnp | grep 3389   # RDP
ss -tlnp | grep 590    # VNC
ss -tlnp | grep 22     # SSH

# Check firewall (on target)
sudo ufw status
sudo iptables -L -n | grep 3389
```

**Fixes:**
```bash
# Start RDP (Windows)
# Enable via Settings > Remote Desktop

# Start VNC server
vncserver :1

# Open firewall
sudo ufw allow 3389/tcp   # RDP
sudo ufw allow 5901/tcp   # VNC :1
```

## Black Screen After Connect

**Symptom:** VNC connects but shows black/blank screen

**Causes:**
1. No desktop session running
2. Wrong display number
3. Display manager conflict

**Fixes:**
```bash
# Check which displays exist
ls /tmp/.X11-unix/

# Start new VNC session with desktop
vncserver :1 -geometry 1920x1080

# For x11vnc sharing existing display
x11vnc -display :0 -auth guess
```

## RDP Disconnects Immediately

**Symptom:** Brief connection then disconnect

**Causes:**
1. NLA authentication issue
2. Certificate problem
3. Another user logged in (Windows)

**Fixes:**
```bash
# Try different security modes
xfreerdp /v:HOST /u:USER /sec:tls
xfreerdp /v:HOST /u:USER /sec:rdp
xfreerdp /v:HOST /u:USER /sec:nla /cert:ignore

# Check if another session active (Windows)
# Use /admin to take over console
xfreerdp /v:HOST /u:USER /admin
```

## X11 Forwarding Not Working

**Symptom:** "Can't open display" or no window appears

**Check server config:**
```bash
# /etc/ssh/sshd_config must have:
X11Forwarding yes

# Restart SSH after changes
sudo systemctl restart sshd
```

**Check client:**
```bash
# Must have -X or -Y
ssh -X user@HOST xclock

# Check DISPLAY is set
ssh -X user@HOST 'echo $DISPLAY'
# Should show localhost:10.0 or similar

# Verbose to debug
ssh -vvv -X user@HOST xclock 2>&1 | grep -i x11
```

**Check xauth:**
```bash
# On server, verify xauth exists
which xauth

# Install if missing
sudo apt install xauth
```

## Slow Performance

**VNC:**
```bash
# Use tight encoding with low quality
vncviewer -encoding tight -quality 3 HOST:1

# Reduce color depth
vncviewer -depth 8 HOST:1
```

**RDP:**
```bash
xfreerdp /v:HOST /u:USER \
  /bpp:16 \              # Lower color depth
  /network:modem \       # Optimize for slow link
  -themes -wallpaper     # Disable eye candy
```

**SSH X11:**
```bash
# Enable compression
ssh -X -C user@HOST firefox
```

## Clipboard Not Working

**VNC:**
```bash
# Run vncconfig on remote
vncconfig &
# Keep it running in background
```

**RDP:**
```bash
# Enable clipboard explicitly
xfreerdp /v:HOST /u:USER +clipboard

# On Windows, check if rdpclip.exe is running
```

**SSH X11:**
```bash
# Install and use xclip
ssh -X user@HOST
# On remote: echo "text" | xclip -selection clipboard
# On local: xclip -o -selection clipboard
```

## Audio Not Working

**RDP:**
```bash
# ALSA
xfreerdp /v:HOST /u:USER /sound:sys:alsa

# PulseAudio
xfreerdp /v:HOST /u:USER /sound:sys:pulse
```

**VNC:** VNC doesn't support audio natively. Use PulseAudio network streaming:
```bash
# On server
pactl load-module module-native-protocol-tcp auth-anonymous=1

# On client
PULSE_SERVER=tcp:HOST:4713 firefox
```

## Can't Connect Through NAT/Firewall

**Solution: SSH tunnel everything**

```bash
# From client with SSH access to target network
ssh -L 3389:windows-pc:3389 user@jumphost
# Then connect to localhost:3389

# For VNC
ssh -L 5901:linux-pc:5901 user@jumphost
vncviewer localhost:5901
```

**Reverse tunnel (target initiates):**
```bash
# On target machine (behind NAT)
ssh -R 3389:localhost:3389 user@your-server

# Now from your-server
xfreerdp /v:localhost:3389 /u:USER
```
