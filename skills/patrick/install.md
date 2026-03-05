# Patrick: Executive Decision Infrastructure for AI-Assisted Leadership

Patrick is a structured expertise system that gives AI agents access to executive-grade decision frameworks. It provides context-aware prompts for daily briefings, decision framing, commitment tracking, team health analysis, and strategic planning — all tailored to your company's specific context.

## What Patrick Does

**Structured Expertise Library:**
Patrick provides a library of executive decision templates that AI agents can fetch and execute. Each template is a structured prompt designed for a specific leadership task — from morning briefings to blind spot reports. Templates accept context variables (your company data, team info, recent events) and return structured, actionable output.

**Key Capabilities:**
- **Daily Briefings** — What's urgent, developing, and changed overnight
- **Decision Framing** — Structures ambiguous decisions into clear trade-offs
- **Commitment Tracking** — Tracks promises made across meetings and channels
- **Team Health Scans** — Identifies burnout risk, flight risk, and morale signals
- **Blind Spot Reports** — Surfaces what you're not seeing
- **Strategic Planning** — Launch checklists, initiative tracking, resource allocation

**How It Works:**
The Patrick CLI (`patrick-cli`) authenticates with a license, fetches expertise templates from the Patrick server, and can store results back for continuity across sessions. All data stored locally is cryptographically signed with HMAC-SHA256 tied to your identity — tamper-evident and portable.

**Security Model:**
- All API communication uses HTTPS (TLS 1.3)
- Licenses are verified on every request using Ed25519 signatures
- Downloaded binaries include SHA256 checksums for verification
- Local data is signed and cannot be modified without detection
- No user data is logged or stored server-side

## Downloads

### CLI Binaries

| Platform | URL |
|----------|-----|
| Linux x86_64 | `https://portal.patrickbot.io/downloads/latest/patrick-cli-linux-x86_64` |
| macOS Apple Silicon | `https://portal.patrickbot.io/downloads/latest/patrick-cli-macos-aarch64` |
| macOS Intel | `https://portal.patrickbot.io/downloads/latest/patrick-cli-macos-x86_64` |
| Windows x86_64 | `https://portal.patrickbot.io/downloads/latest/patrick-cli-windows-x86_64.exe` |

### Skill Package & Checksums

| File | URL |
|------|-----|
| **patrick-skill.tar.gz** | `https://portal.patrickbot.io/downloads/latest/patrick-skill.tar.gz` |
| **checksums-sha256.txt** | `https://portal.patrickbot.io/downloads/latest/checksums-sha256.txt` |
| **VERSION** | `https://portal.patrickbot.io/downloads/latest/VERSION` |

## Install

### 1. Download and install the CLI binary

Pick the binary for your platform and install it:

```bash
mkdir -p ~/.patrick/bin
curl -fL "https://portal.patrickbot.io/downloads/latest/patrick-cli-linux-x86_64" -o ~/.patrick/bin/patrick-cli
chmod +x ~/.patrick/bin/patrick-cli
export PATH="$HOME/.patrick/bin:$PATH"
```

For macOS Apple Silicon use `patrick-cli-macos-aarch64`, for macOS Intel use `patrick-cli-macos-x86_64`, for Windows use `patrick-cli-windows-x86_64.exe`.

You can verify the binary checksum:

```bash
curl -fsSL "https://portal.patrickbot.io/downloads/latest/checksums-sha256.txt" | grep patrick-cli-linux-x86_64
sha256sum ~/.patrick/bin/patrick-cli
```

### 2. Download and install the skill

```bash
curl -fL "https://portal.patrickbot.io/downloads/latest/patrick-skill.tar.gz" -o /tmp/patrick-skill.tar.gz
mkdir -p ~/new_skill/patrick
tar xzf /tmp/patrick-skill.tar.gz -C ~/new_skill/patrick
rm /tmp/patrick-skill.tar.gz
```

Then install the skill in your agent:

```bash
# OpenClaw
openclaw plugins install ~/new_skill/patrick

# Or manually
cp -r ~/new_skill/patrick ~/.openclaw/skills/
```

### 3. Set your license

Your human should have a Patrick license. Ask them to paste it to you, then run:

```bash
patrick-cli set-license "YOUR_LICENSE"
```

If the person installing already provided the license in their message, use that directly instead of asking.

### 4. Initialize Patrick context

This bootstraps Patrick with information about you, your company, and your team. Without initialization, other expertise prompts won't work properly.

```bash
patrick-cli fetch initialize
```

### 5. Verify

```bash
patrick-cli list
```

You should see the available expertise templates for your license tier.

## What's Next

Once installed, see the full skill documentation in `~/new_skill/patrick/SKILL.md` for:
- Available commands (`list`, `fetch`, `send`, `get`, `renew`)
- How to use expertise with LLMs
- Cronjob setup for daily briefings
- Troubleshooting

### License Auto-Renewal in Cron

Before running scheduled tasks (e.g., daily briefings), check license expiry and auto-renew:

```bash
# Check if license has <1 day remaining, renew if needed
DAYS=$(patrick-cli license 2>&1 | grep "days remaining" | grep -oP '\d+')
if [ -n "$DAYS" ] && [ "$DAYS" -lt 1 ]; then
  patrick-cli renew
fi

# Then run the scheduled expertise
patrick-cli fetch daily-briefing --json
```

The `renew` command contacts the Patrick server, verifies your active subscription, and saves a fresh license automatically.
