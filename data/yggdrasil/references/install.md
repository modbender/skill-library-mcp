# Yggdrasil Installation Guide

Yggdrasil is a lightweight, end-to-end encrypted IPv6 overlay network.
After install, restart the OpenClaw gateway — the plugin starts the daemon automatically.

---

## macOS

```bash
brew install yggdrasil
```

Verify:
```bash
yggdrasil -version
```

---

## Linux — Debian / Ubuntu / Raspberry Pi OS

```bash
# Add the Yggdrasil apt repo
curl -sL https://www.yggdrasil-network.github.io/apt-key.gpg | sudo apt-key add -
echo "deb http://www.yggdrasil-network.github.io/apt/ debian main" \
  | sudo tee /etc/apt/sources.list.d/yggdrasil.list

sudo apt update
sudo apt install yggdrasil
```

> The plugin manages its own daemon. You do NOT need `systemctl enable yggdrasil` — the gateway controls it.

Verify:
```bash
yggdrasil -version
```

---

## Linux — Arch

```bash
yay -S yggdrasil   # or: paru -S yggdrasil
```

---

## Linux — Manual / other distros

Download the latest release binary from:
https://github.com/yggdrasil-network/yggdrasil-go/releases/latest

Pick the archive for your arch (e.g. `yggdrasil-X.Y.Z-linux-amd64.tar.gz`),
extract, and place the `yggdrasil` binary somewhere on your `$PATH`:

```bash
tar -xzf yggdrasil-*.tar.gz
sudo mv yggdrasil /usr/local/bin/
```

---

## Windows

Download the `.msi` installer from:
https://github.com/yggdrasil-network/yggdrasil-go/releases/latest

Run it. The binary ends up at `C:\Program Files\Yggdrasil\yggdrasil.exe`.
Make sure `C:\Program Files\Yggdrasil` is on your system `PATH`.

---

## After any install

1. Restart the OpenClaw gateway.
2. The plugin detects the binary, generates a config, and starts the daemon.
3. Your `200::/8` address will be shown in the gateway logs.
4. Call `yggdrasil_check()` to confirm and get your routable address to share.
