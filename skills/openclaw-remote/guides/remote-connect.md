# Remote Connection Guide

⚠️ **PREREQUISITE**: This guide assumes you already have SSH access to your remote machine. If you don't, please set up SSH access manually before proceeding.

## Step 1: Determine Connection Method

Ask the user:
> How do you connect to your remote machine?
> 1. Tailscale (recommended — zero-config mesh VPN)
> 2. Direct SSH to a VPS (public IP)
> 3. Local network (same LAN)

## Step 2: Connect via Tailscale

If the user has Tailscale installed on both machines:

```bash
# Check Tailscale is running
tailscale status

# SSH to remote using Tailscale hostname
ssh <user>@<hostname>.tail<tailnet>.ts.net
```

**Note**: If Tailscale is not installed, please install it manually following the official Tailscale documentation: https://tailscale.com/download

## Step 2 (alt): Connect via Direct SSH

```bash
# Test connection (assumes SSH is already configured)
ssh <user>@<ip-address>
```

**Note**: This guide assumes SSH authentication is already configured on your system. We recommend using SSH key-based authentication for security, which you should set up manually outside of this skill.

## Step 3: Start tmux Session on Remote

```bash
# SSH in and start tmux
ssh <user>@<remote-address>
tmux new-session -s openclaw

# Or attach to existing
ssh <user>@<remote-address> -t 'tmux attach-session -t openclaw || tmux new-session -s openclaw'
```

## Step 4: Use tmux from Local Agent

Once the user has an SSH connection, interact via tmux from the local machine:

```bash
# If SSH session has tmux running locally that forwards to remote:
tmux send-keys -t <local-session> 'openclaw --version' Enter
sleep 2 && tmux capture-pane -t <local-session> -p -S -5

# If using SSH directly in tmux:
tmux send-keys -t <session> 'ssh <user>@<remote> "openclaw --version"' Enter
```

## Step 5: Verify OpenClaw Installation

```bash
which openclaw && openclaw --version
```

If not installed:

```bash
# macOS (Homebrew)
brew install openclaw

# Linux (npm)
npm install -g openclaw

# Verify
openclaw --version
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Check SSH is running: `sudo systemctl status sshd` |
| Permission denied | Check key permissions: `chmod 600 ~/.ssh/id_ed25519` |
| Tailscale not connecting | Run `tailscale up --reset` on both machines |
| tmux not found | Install: `brew install tmux` (mac) or `apt install tmux` (linux) |
| ENOENT uv_cwd in tmux | Run `cd ~` first — previous cwd was deleted |
