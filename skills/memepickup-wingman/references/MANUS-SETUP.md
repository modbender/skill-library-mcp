# Manus Setup — MemePickup Wingman

Detailed setup guide for running the MemePickup Wingman skill on Manus.

## Installation

### Option 1: GitHub Import

In Manus, import from:
```
github.com/samcraw1/rork-memepickup-app-3
```

Select the `memepickup-wingman` directory. Manus will read the SKILL.md and register the skill.

### Option 2: Upload Zip

1. Download the `memepickup-wingman` directory as a zip
2. Upload to Manus via the file upload interface
3. Manus will detect the SKILL.md and register it

### Option 3: Build from Chat

Tell Manus:
> "Install the MemePickup Wingman skill from github.com/samcraw1/rork-memepickup-app-3"

Manus will clone the repo and set up the skill in its sandbox.

## API Key Setup

### Via Chat

Tell Manus your API key directly:
> "My MemePickup API key is mp_your_key_here"

Manus will export it in the sandbox environment.

### Via Sandbox Terminal

Open the Manus sandbox terminal and run:

```bash
export MEMEPICKUP_API_KEY="mp_your_api_key_here"
```

### Persistent Configuration

To persist across sandbox sessions, add the export to `~/.bashrc` in the sandbox:

```bash
echo 'export MEMEPICKUP_API_KEY="mp_your_api_key_here"' >> ~/.bashrc
```

## Script Execution

Manus runs scripts in an Ubuntu sandbox VM. Both `scripts/api.sh` (Bash) and `scripts/api.py` (Python) are available:

```bash
# Bash version
echo '{"intensity": 0.5}' | scripts/api.sh lines

# Python version (no pip install needed — stdlib only)
echo '{"intensity": 0.5}' | python3 scripts/api.py lines
```

Use whichever Manus prefers for the task. Both produce identical output.

## Browser Automation (Auto-Swipe)

Manus performs auto-swipe using browser automation on web versions of dating apps:

| Platform | Web URL | Supported |
|----------|---------|-----------|
| Hinge | hinge.co | Yes |
| Tinder | tinder.com | Yes |
| Bumble | bumble.com | Yes |
| Instagram | — | No (no web dating UI) |

### Requirements

1. Log into the web version of the dating app in Manus's browser before starting auto-swipe
2. Keep the browser tab open during the session
3. Some platforms may require completing a CAPTCHA on first login

### Login Steps

1. Tell Manus to open the dating app's web version
2. Log in manually (Manus will wait)
3. Confirm you're logged in
4. Tell Manus to start auto-swiping

Manus will screenshot each profile, send it to the API for analysis, and click the appropriate action in the browser.

## Telegram Integration

Manus can act as a persistent Telegram agent, receiving dating app notifications and providing wingman advice directly in chat.

### Setup

1. Connect Manus to your Telegram account via Manus settings
2. The wingman activates when you forward dating app messages/notifications to Manus
3. Manus runs the API call in its sandbox and returns suggestions in the Telegram chat

### Usage

Forward a dating app notification or message to Manus in Telegram:
> "New message from Sarah: What's your most controversial food take?"

The wingman will generate reply suggestions and send them back through Telegram.

### Availability

Manus Telegram agents are a new feature. Availability may vary and some Telegram accounts have reported rate limiting. If Telegram integration is unavailable, use the Manus desktop app or web sandbox as a fallback.

This pattern will also work with WhatsApp, LINE, Slack, and Discord when Manus adds support.

## Troubleshooting

**Skill not recognized:**
- Re-import from GitHub or re-upload the zip
- Verify SKILL.md is in the root of the imported directory

**"MEMEPICKUP_API_KEY not set" in sandbox:**
- Re-export the key: `export MEMEPICKUP_API_KEY="mp_..."`
- Add to `~/.bashrc` for persistence

**curl not available in sandbox:**
- Use the Python version instead: `python3 scripts/api.py <action>`

**Browser automation can't find elements:**
- Make sure you're logged into the web dating app
- Try refreshing the page
- Some platforms update their web UI frequently — report issues to support@memepickup.com

**Telegram not receiving responses:**
- Check that Manus is connected to your Telegram in Manus settings
- Manus Telegram agents may have rate limits — wait and retry
- Fallback: use the Manus desktop app directly
