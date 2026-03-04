# Proton Bridge setup

Complete guide for installing Proton Bridge on Ubuntu 24.04, setting up credential storage, and running Bridge as a background service.

## Prerequisites

- Ubuntu 24.04 (or compatible Debian-based distro)
- A Proton account (free or paid)
- `gnupg` and `pass` installed (`sudo apt install gnupg pass`)

## Step 1: Install Proton Bridge

Download the `.deb` package from the official site and install it:

```bash
# Download from https://proton.me/bridge/install (choose the .deb for Ubuntu/Debian)
# Then install:
sudo apt install ./protonmail-bridge_*.deb
```

This installs the `protonmail-bridge` binary and its dependencies.

## Step 2: Set up `pass` for credential storage

Proton Bridge stores its login credentials using `pass`, which requires a GPG key. The GPG key **must have no passphrase** — Bridge runs non-interactively and cannot prompt for one.

### Generate a passphrase-free GPG key

```bash
# Generate key non-interactively with no passphrase
gpg --batch --gen-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Proton Bridge
Name-Email: bridge@localhost
Expire-Date: 0
%commit
EOF
```

Why no passphrase? Bridge needs to read credentials automatically when it starts. A passphrase would cause Bridge to hang waiting for input, especially under systemd where there is no terminal.

### Initialize the password store

```bash
# Get the GPG key ID
gpg --list-keys --keyid-format long bridge@localhost

# Initialize pass with that key ID
pass init <GPG_KEY_ID>
```

`pass` creates an encrypted store at `~/.password-store/`. Bridge writes its credentials here automatically during login.

## Step 3: Log in via Bridge CLI

Bridge has a CLI mode for headless servers (no GUI needed):

```bash
protonmail-bridge --cli
```

Inside the Bridge CLI:

```
>>> login
# Enter your Proton account email and password
# Complete 2FA if enabled

>>> info
# This shows your Bridge credentials:
#   Username: your.email@proton.me
#   Password: abcdefghijklmnop    <-- THIS is the Bridge password
#   IMAP: 127.0.0.1:1143
#   SMTP: 127.0.0.1:1025

>>> exit
```

**Save the Bridge password.** This is the generated credential you need for himalaya (and for the OpenClaw `PROTON_BRIDGE_PASSWORD` secret). It is NOT your Proton account password.

### Why not `--noninteractive`?

The `--noninteractive` flag starts Bridge in daemon mode but **cannot perform login**. You must use `--cli` for the initial login. After that, credentials are stored in `pass` and `--noninteractive` works for background operation.

## Step 4: Create a systemd user service

Create a service file so Bridge starts automatically and runs in the background:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/protonmail-bridge.service <<EOF
[Unit]
Description=Proton Bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/protonmail-bridge --noninteractive
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%U/bus

[Install]
WantedBy=default.target
EOF
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable protonmail-bridge
systemctl --user start protonmail-bridge

# Verify it's running
systemctl --user status protonmail-bridge
```

### D-Bus requirement

`pass` uses `gpg-agent`, which communicates over D-Bus. The `DBUS_SESSION_BUS_ADDRESS` environment variable in the service file ensures `pass` can decrypt credentials when Bridge runs under systemd. Without it, Bridge fails silently with GPG errors.

If your system uses a non-standard D-Bus path, check with:

```bash
echo $DBUS_SESSION_BUS_ADDRESS
```

### Enable lingering (optional but recommended)

By default, systemd user services only run while the user is logged in. Enable lingering to keep Bridge running after logout:

```bash
sudo loginctl enable-linger $USER
```

## Step 5: Verify

After Bridge is running, confirm IMAP and SMTP are accessible:

```bash
# Test IMAP port
nc -z 127.0.0.1 1143 && echo "IMAP OK" || echo "IMAP FAILED"

# Test SMTP port
nc -z 127.0.0.1 1025 && echo "SMTP OK" || echo "SMTP FAILED"
```

## Gotchas

### Bridge password is not your Proton password

The Bridge password is a randomly generated string (e.g., `abcdefghijklmnop`) created by Bridge for local IMAP/SMTP access. You get it from `protonmail-bridge --cli` > `info`. Your actual Proton account password is only used once during the `login` step.

### GPG key must be passphrase-free

If your GPG key has a passphrase, Bridge will fail to start under systemd because there is no terminal to prompt for it. Delete the key and regenerate without a passphrase:

```bash
gpg --delete-secret-and-public-key bridge@localhost
# Then re-run the generation command from Step 2
```

### Self-signed certificate for STARTTLS

Bridge uses a self-signed TLS certificate for localhost IMAP/SMTP. Most mail clients (including himalaya) need certificate verification disabled for this connection. This is safe because all traffic stays on localhost — nothing crosses the network.

In the himalaya config (generated by `setup configure`), the relevant fields are:

```toml
backend.encryption.type = "start-tls"
message.send.backend.encryption.type = "start-tls"
```

The `setup configure` command generates this automatically. If you need to edit manually, the full config is at `config/himalaya.toml`.

### Default ports: IMAP 1143, SMTP 1025

These are non-standard ports (not 993/465) because Bridge runs as a user process, not root. The ports are configurable in Bridge settings but the defaults are fine for local use.

### Mail sync delay on first start

After the initial login, Bridge needs to download and decrypt all your mail. This can take several minutes depending on mailbox size. Emails will not appear in himalaya until sync completes. You can monitor progress in Bridge logs:

```bash
journalctl --user -u protonmail-bridge -f
```

### `--noninteractive` cannot log in

The `--noninteractive` flag is for daemon mode only. It assumes credentials are already stored in `pass`. Always use `--cli` for the first login, then switch to `--noninteractive` for background operation.

### D-Bus under systemd

If `pass` fails with GPG errors when Bridge runs under systemd, the cause is almost always a missing `DBUS_SESSION_BUS_ADDRESS`. Ensure the environment variable is set in the service file (see Step 4).
