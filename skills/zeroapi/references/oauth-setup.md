# OAuth & Provider Auth Setup

## Provider Auth Summary

| Provider | Auth Method | Setup Command | Maintenance |
|----------|-----------|---------------|-------------|
| Anthropic | Setup-token (OAuth) | `openclaw onboard --auth-choice setup-token` | Low — auto-refresh works |
| Google Gemini | OAuth (CLI plugin) | `openclaw plugins enable google-gemini-cli-auth && openclaw models auth login --provider google-gemini-cli` | Very low — long-lived refresh tokens |
| OpenAI Codex | OAuth (ChatGPT PKCE) | `openclaw onboard --auth-choice openai-codex` | Low — auto-refresh works |
| Kimi | Static API key | `openclaw onboard --auth-choice kimi-code-api-key` | None — never expires |

**Auth reliability ranking**: Kimi API key (static, never expires) ≈ Gemini OAuth (auto-refresh, stable) > Anthropic setup-token (auto-refresh, ~8hr access token) > Codex OAuth (auto-refresh works, see notes below).

## Codex OAuth — Multi-Device Safety (Tested Feb 2026)

A common concern: "Will logging into ChatGPT on my phone/browser invalidate my agent's Codex token on the VPS?"

**No.** We tested all four scenarios with a fresh Codex JWT active on a VPS:

| Action | VPS Token Affected? |
|--------|-------------------|
| Log into ChatGPT web UI (browser) | No — token survived |
| Log into ChatGPT mobile app + chat | No — token survived |
| Use Codex desktop app + new session | No — token survived |
| Use Codex CLI in terminal + chat | No — token survived |

All four passed. OpenClaw's auto-refresh mechanism handles token renewal automatically. Users can freely use ChatGPT and Codex on all their devices without disrupting their agent's authentication.

**Technical note**: Codex CLI and OpenClaw share the same OAuth `client_id` (`app_EMoamEE...`). Despite this, concurrent sessions on different devices do not invalidate each other. A dedicated OpenAI account for the VPS is NOT necessary.

## OAuth Setup for Agents (Headless / No Browser)

The `openclaw onboard` command uses an interactive TUI wizard. On a headless VPS (no browser), OpenClaw detects this and switches to a "paste-the-redirect-URL" flow. The agent needs to:

1. Run the wizard in a virtual terminal
2. Navigate the TUI menus
3. Extract the OAuth URL
4. Send it to the user (via WhatsApp, Telegram, Discord, etc.)
5. Receive the redirect URL back from the user
6. Paste it into the wizard

### If you are an OpenClaw agent (running directly on the VPS)

You have direct Bash access. Use `tmux` to manage the interactive TUI:

```bash
# Step 1: Start the wizard in a tmux session
tmux new-session -d -s oauth 'openclaw onboard --auth-choice openai-codex --accept-risk'

# Step 2: Read the screen and navigate menus
tmux capture-pane -t oauth -p        # read current screen
tmux send-keys -t oauth Enter        # select highlighted option
# Repeat capture-pane + send-keys until you reach the OAuth URL screen

# Step 3: Extract the OAuth URL from the screen output
# Look for a line starting with https://auth.openai.com/oauth/authorize?...
# Send this URL to the user via your channel (WhatsApp, Telegram, etc.)

# Step 4: Tell the user:
#   "Open this link in your browser, log in to ChatGPT.
#    After login, your browser will try to load a localhost URL that won't work.
#    Copy that FULL URL from the browser address bar and send it back to me."

# Step 5: When the user sends back the redirect URL, paste it:
tmux send-keys -t oauth 'THE_REDIRECT_URL_FROM_USER' Enter

# Step 6: Auth is saved. Cancel remaining wizard steps:
tmux send-keys -t oauth C-c

# Step 7: Verify
openclaw models status | grep openai-codex
```

The same approach works for other OAuth providers (Gemini, Anthropic). Change `--auth-choice` accordingly.

### If you are Claude Code (SSH from local machine)

Run the same tmux commands over SSH:

```bash
ssh YOUR_VPS 'tmux new-session -d -s oauth "openclaw onboard --auth-choice openai-codex --accept-risk"'
ssh YOUR_VPS 'tmux capture-pane -t oauth -p'           # read screen
ssh YOUR_VPS 'tmux send-keys -t oauth Enter'           # navigate menus
# ... extract URL, user clicks, paste redirect URL back ...
ssh YOUR_VPS "tmux send-keys -t oauth 'REDIRECT_URL' Enter"
ssh YOUR_VPS 'tmux send-keys -t oauth C-c'
```

### If you are Codex CLI or any other agent

Same principle — use `tmux` (or `screen`) to wrap the interactive wizard, extract the URL, and relay it to the user through whatever channel you communicate on.

Key steps are always:
1. Wrap `openclaw onboard` in a virtual terminal (`tmux`/`screen`)
2. Navigate menus by sending keystrokes
3. Extract the OAuth URL and send to user
4. Receive redirect URL from user and paste back
5. Verify with `openclaw models status`

## Auth Status Monitoring

Any agent can check provider health at any time:

```bash
# Quick check — exit code 0=ok, 1=expired, 2=expiring soon
openclaw models status --check

# Detailed view — shows expiry times and usage quotas
openclaw models status

# Full health check with repair suggestions
openclaw doctor
```

If Codex shows `auth_expired`, guide the user through the OAuth flow above. For Anthropic, run `openclaw onboard --auth-choice setup-token`. For Gemini, run `openclaw models auth login --provider google-gemini-cli`. Kimi API keys do not expire — if Kimi fails, check that the subscription is active.

## Token Storage Architecture (CRITICAL)

OAuth tokens are stored in **3 separate locations** that do **NOT auto-sync**:

| Location | Purpose | Auto-Updated? |
|----------|---------|--------------|
| `credentials/oauth.json` | Raw OAuth output from initial `openclaw onboard` | Only on first onboard |
| `models.providers.<name>.apiKey` in `openclaw.json` | Runtime API calls | By auto-refresh |
| `agents/<id>/agent/auth-profiles.json` | Per-agent active tokens | By auto-refresh |

**Why this matters**: When you manually renew a token (via tmux OAuth flow), the new token is written ONLY to `auth-profiles.json`. The other 2 locations retain the old (possibly expired) token.

OpenClaw's auto-refresh mechanism updates `auth-profiles.json` and `openclaw.json` — but `credentials/oauth.json` is never auto-updated after initial onboard.

**After manual renewal**, sync the new token to all locations. Example for Codex:

```bash
# Extract the new access token from auth-profiles
NEW_TOKEN=$(python3 -c "
import json, glob
for f in glob.glob('$HOME/.openclaw/agents/*/agent/auth-profiles.json'):
    profiles = json.load(open(f))
    for p in profiles:
        if 'openai' in p.get('provider','').lower():
            print(p['access']); break
    else: continue
    break
")

# Update openclaw.json
python3 -c "
import json
c = json.load(open('$HOME/.openclaw/openclaw.json'))
c['models']['providers']['openai-codex']['apiKey'] = '$NEW_TOKEN'
json.dump(c, open('$HOME/.openclaw/openclaw.json','w'), indent=2)
"

# Restart to pick up changes
systemctl --user restart openclaw-gateway.service
```

**Best practice**: Let auto-refresh handle token renewal whenever possible. Only use the manual tmux flow when auto-refresh fails (e.g., refresh token itself has expired).
