---
name: secure-autofill
description: 1Password-backed credential filling via vault_suggest/vault_fill (plugin tools).
homepage: https://github.com/openclaw/openclaw
metadata:
  openclaw:
    emoji: "🔐"
---

# secure-autofill 🔐

This skill documents how to use the **secure-autofill** plugin tools:

- `vault_suggest` — find likely 1Password items
- `vault_fill` — fill browser DOM fields with secrets (agent never sees credentials)

## Architecture

**Agent orchestrates; plugin handles secrets.** The agent provides element refs from `browser.snapshot`; the plugin types secrets into the page.

## Prerequisites

- Tools available (if tool allowlists are in use): `vault_suggest`, `vault_fill`
- A working non-headless Chrome on WSL (many sites block headless)
- Gateway environment has required env vars

Concrete checks:

```bash
command -v google-chrome || command -v google-chrome-stable
```

## Configuration (portable)

Machine-specific environment should NOT be hardcoded in this document.

- Example (do not edit): `~/.openclaw/skills/secure-autofill/config.env.example`
- Real (machine-specific): `~/.openclaw/skills/secure-autofill/config.env`
- Gateway env file (recommended destination): `~/.config/openclaw/env`

Typical keys:

- `DISPLAY`
- `WAYLAND_DISPLAY`
- `OP_SERVICE_ACCOUNT_TOKEN` (do not commit; do not paste into chat)

## Initialization / installation / onboarding (WSL)

### Preferred (chat-first)

Because the primary interface is chat (Telegram), the preferred onboarding flow is:

1. Ask Boss which values to set (DISPLAY, WAYLAND_DISPLAY, whether to set OP_SERVICE_ACCOUNT_TOKEN).
2. Write/update the real skill-local env file: `config.env`.
3. Optionally update the gateway env file (`~/.config/openclaw/env`) with per-key confirmation.
4. If applicable, detect whether `openclaw-gateway` is managed by `systemctl --user` and offer to restart.

### Optional (terminal)

If you are running in a real terminal, you can use the interactive onboarding script:

```bash
~/.openclaw/skills/secure-autofill/scripts/onboard.sh
```

### 1) Install Google Chrome (.deb)

Ubuntu 22.04 moved Chromium to snap which doesn't work well in WSL. Install Chrome directly:

```bash
# Add Google apt source
wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
  | sudo gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
  | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Install
sudo apt update && sudo apt install -y google-chrome-stable
```

### 2) Configure gateway environment (non-headless + 1Password token)

1. Create/update `~/.config/openclaw/env`.
2. Run onboarding to generate the real env file (skill-local):

```bash
~/.openclaw/skills/secure-autofill/scripts/onboard.sh
```

3. Copy the needed variables from the skill-local `config.env` into the gateway env file (`~/.config/openclaw/env`).
4. Ensure the gateway service loads the env file:

```bash
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d
cat > ~/.config/systemd/user/openclaw-gateway.service.d/override.conf << 'EOF'
[Service]
EnvironmentFile=%h/.config/openclaw/env
EOF

systemctl --user daemon-reload
systemctl --user restart openclaw-gateway
```

### 3) Tool allowlist (if configured)

In `~/.openclaw/openclaw.json`, add:

```json
"tools": {
  "alsoAllow": ["vault_fill", "vault_suggest"]
}
```

## Tools

- `vault_suggest` — list 1Password items (to find available credentials)
- `vault_fill` — fill DOM fields with secrets (agent provides refs, plugin types secrets)

## `vault_fill` API

```ts
vault_fill({
  item_title: "X",              // 1Password item title
  fields: {
    username: { ref: "e3" },    // field type → DOM ref
    password: { ref: "e5" },
    otp: { ref: "e7" }          // optional
  },
  retry_mode: "simple",         // "simple" | "next_candidate" | "reset"
  targetId: "..."               // from browser snapshot
})

// Returns:
{
  ok: true,
  filled: ["username", "password"],
  item_title: "X",
  has_more_candidates: false
}
```

## Field types

- `username` → 1Password "username" field
- `password` → 1Password "password" field
- `email` → 1Password "email" field (falls back to username)
- `otp` → 1Password TOTP (fresh code)

## Retry modes

- `simple` — same credentials, same refs (use after dismissing a blocker)
- `next_candidate` — try next matching 1Password item (wrong credentials)
- `reset` — clear retry state and start fresh

## Timing note

**Always wait ~1 second after `vault_fill` before clicking submit.**

The plugin uses async CLI calls which take a moment to complete typing.

```text
vault_fill(...)  // returns immediately
wait 1000ms      // let typing complete
click submit
```

## Login workflow (agent-driven)

```text
1. Navigate to login page
2. Loop until logged in or max retries:
   a. snapshot → identify page state
   b. If obstacle (cookie banner, popup, passkey error):
      - Dismiss it
      - Continue loop
   c. If credential field found:
      - Build field mapping from snapshot refs
      - Call vault_fill with mapping
      - Click submit button
      - Continue loop
   d. If logged in:
      - Done!
   e. If error:
      - Decide: retry_mode="simple" or "next_candidate"
      - Continue loop
```

## X.com example

```text
Agent: navigate to x.com/i/flow/login
Agent: snapshot
       → textbox "Phone, email, or username" [ref=e3]
       → button "Next" [ref=e4]
Agent: vault_fill({ item_title: "X", fields: { username: { ref: "e3" } }, targetId })
Agent: click e4 (Next button)
Agent: wait, snapshot
       → button "Next" [ref=e1]  (passkey error dialog)
Agent: click e1 (dismiss)
Agent: wait, snapshot
       → textbox "Password" [ref=e3]
       → button "Log in" [ref=e6]
Agent: vault_fill({ item_title: "X", fields: { password: { ref: "e3" } }, targetId })
Agent: click e6 (Log in)
Agent: wait, snapshot
       → textbox "Enter code" [ref=e4]
       → button "Next" [ref=e7]
Agent: vault_fill({ item_title: "X", fields: { otp: { ref: "e4" } }, targetId })
Agent: click e7 (Next)
Agent: wait, snapshot → home feed visible → Done!
```

## MFA handling

- TOTP: use `vault_fill(otp)`
- SMS/Email: ask user for the code; type it; click Next
- Push: tell user to approve; wait; continue

## Executables / bin placement

This skill is documentation for plugin tools; it does not ship a standalone executable.
Helper scripts (like onboarding) live inside the skill folder under `scripts/`.
