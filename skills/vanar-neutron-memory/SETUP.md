# Setup Guide

Get persistent memory with semantic search running in under 2 minutes.

## Step 1: Get Your API Key (Free)

1. Go to **https://openclaw.vanarchain.com/signup**
2. Sign up with **Email** or **Google** (free tier, no credit card required)
   - **Email**: Enter your name and email → you'll receive a 6-digit code → enter it to verify
   - **Google**: Click "Continue with Google" → authorize
3. After signup you're automatically redirected to the **Manage** dashboard
4. A modal appears showing your API key — **copy it now, you won't see the full key again**
   - The key starts with `nk_` (e.g. `nk_abc123...`)
   - Click the copy button to copy to clipboard

Your account comes with **$20 of free credits** — enough to store and search thousands of memories.

> If you already have an account, log in at https://openclaw.vanarchain.com/login and go to **Manage** → **API Keys** to create a new key.

That's it — one key is all you need. No agent IDs, no app IDs, no other configuration.

## Step 2: Configure

Pick one of these options:

**Option A — Environment variable** (recommended):
```bash
export API_KEY=nk_your_key_here
```

Add to your `~/.zshrc` or `~/.bashrc` to persist across sessions:
```bash
echo 'export API_KEY=nk_your_key_here' >> ~/.zshrc
source ~/.zshrc
```

**Option B — Credentials file:**
```bash
mkdir -p ~/.config/neutron
echo '{"api_key":"nk_your_key_here"}' > ~/.config/neutron/credentials.json
```

**Option C — OpenClaw project config** (`openclaw.json`):
```json
{
  "skills": {
    "entries": {
      "vanar-neutron-memory": {
        "enabled": true,
        "apiKey": "nk_your_key_here"
      }
    }
  }
}
```

## Step 3: Test

```bash
./scripts/neutron-memory.sh test
```

You should see: `API connection successful`

## Step 4: Try It

Save something:
```bash
./scripts/neutron-memory.sh save "I prefer dark mode and use vim keybindings" "User preferences"
```

Wait ~15 seconds, then search:
```bash
./scripts/neutron-memory.sh search "what editor settings does the user like" 5 0.5
```

You should get back the saved memory matched by meaning — not keywords.

## Auto-Recall & Auto-Capture (Opt-In)

These optional features automate memory management:
- **Auto-Recall**: Queries relevant memories before each AI turn and injects as context
- **Auto-Capture**: Saves conversations after each AI turn to memory

Both are **off by default**. To enable:
```bash
export VANAR_AUTO_RECALL=true
export VANAR_AUTO_CAPTURE=true
```

## Credits

Your free account includes $20 of trial credits. Credits are consumed by save and search operations. You can check your balance anytime at https://openclaw.vanarchain.com/manage.

| Tier | Cost | Details |
|------|------|---------|
| **Free** | $0 | $20 of credits on signup, no credit card |
| **Pay As You Go** | $10 min top-up | Coming soon |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `API_KEY not found` | Set the env var or create credentials file (see Step 2) |
| `API connection failed` | Check your API key is correct at https://openclaw.vanarchain.com/manage |
| Search returns no results | Memories take 10-30s to process after saving — wait and retry |
| `jq: command not found` | Install jq: `brew install jq` (macOS) or `apt install jq` (Linux) |

## Security & Privacy

This skill sends only what you explicitly save (or auto-captured conversations) over HTTPS. No local files, environment variables, or system information are ever sent. The entire source code is three short bash scripts — fully readable in `scripts/` and `hooks/`.

For full details, see the **Security & Privacy** section in [SKILL.md](SKILL.md).

## Need Help?

- Dashboard & API keys: https://openclaw.vanarchain.com/
- Skill page: https://clawhub.ai/naeemmaliki036/vanar-neutron-memory
