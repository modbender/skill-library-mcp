---
name: structsd-install
description: Installs the structsd binary from source. Covers Go, Ignite CLI, and building structsd for Linux and macOS. Use when structsd is not found, when setting up a new machine, or when the agent needs to install or update the Structs chain binary.
---

# Install structsd

Builds the `structsd` binary from source using Ignite CLI. After this procedure, `structsd` will be available on your PATH.

## Prerequisites

Two dependencies are required: **Go 1.24.1+** and **Ignite CLI**.

---

### 1. Install Go

#### Linux (amd64)

```bash
wget https://go.dev/dl/go1.24.1.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.24.1.linux-amd64.tar.gz
rm go1.24.1.linux-amd64.tar.gz
```

If an older Go was installed via apt, remove it first: `sudo apt remove -y golang-go`

#### macOS (Apple Silicon)

```bash
curl -OL https://go.dev/dl/go1.24.1.darwin-arm64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.24.1.darwin-arm64.tar.gz
rm go1.24.1.darwin-arm64.tar.gz
```

#### macOS (Intel)

```bash
curl -OL https://go.dev/dl/go1.24.1.darwin-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.24.1.darwin-amd64.tar.gz
rm go1.24.1.darwin-amd64.tar.gz
```

Alternatively on macOS: `brew install go@1.24`

#### Configure PATH

Add to `~/.profile` (or `~/.zshrc` on macOS):

```bash
export PATH=$PATH:/usr/local/go/bin:~/go/bin
```

Reload: `source ~/.profile` (or `source ~/.zshrc`)

#### Verify

```bash
go version
```

Expected: `go version go1.24.1 linux/amd64` (or `darwin/arm64`, etc.)

---

### 2. Install Ignite CLI

```bash
curl https://get.ignite.com/cli! | bash
```

#### Verify

```bash
ignite version
```

---

### 3. Build structsd

Clone the repository and build:

```bash
git clone https://github.com/playstructs/structsd.git
cd structsd
ignite chain build
```

The binary is installed to `~/go/bin/structsd`. Since `~/go/bin` is on your PATH (from step 1), it's immediately available.

#### Verify

```bash
structsd version
```

---

### 4. Update structsd

To update to the latest version:

```bash
cd structsd
git pull origin main
ignite chain build
```

---

## Quick Check

Run all verifications in sequence:

```bash
go version && ignite version && structsd version
```

If any command fails, revisit the corresponding step above.

## Troubleshooting

- **`structsd: command not found`** — Ensure `~/go/bin` is on your PATH. Run `ls ~/go/bin/structsd` to confirm the binary exists.
- **`ignite: command not found`** — Re-run the Ignite CLI install. The curl command installs to `/usr/local/bin/ignite`.
- **`go: command not found`** — Ensure `/usr/local/go/bin` is on your PATH. Reload your shell profile.
- **Build fails with Go version error** — Verify `go version` shows 1.24.1+. Older Go versions are not compatible.
- **Permission denied on `/usr/local`** — Use `sudo` for the tar extraction. On shared systems, ask your administrator.

## See Also

- [TOOLS](https://structs.ai/TOOLS) — Environment configuration (servers, account, after structsd is installed)
- [structs-onboarding skill](https://structs.ai/skills/structs-onboarding/SKILL) — Player creation and first builds (requires structsd)
