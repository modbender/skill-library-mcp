# Setup Guide — X (Twitter) Personal Analytics Skill

Step-by-step walkthrough from zero to working skill.

## Prerequisites

- [uv](https://astral.sh/uv) — Python package runner (handles dependencies automatically)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- An X (Twitter) account
- $5 minimum to load API credits (see Step 4)

## Step 1: Create an X Developer Account

1. Go to [developer.x.com](https://developer.x.com)
2. Click **Sign Up** (or **Developer Portal** if you already have an account)
3. Sign in with your X account
4. Fill out the required info:
   - What's your use case? Select **"Making a bot"** or **"Exploring the API"**
   - Describe your project (e.g., "Personal analytics dashboard for monitoring my own posts and engagement")
5. Accept the developer agreement
6. You'll land on the Developer Dashboard

## Step 2: Create a Project and App

1. In the Developer Dashboard, click **Projects & Apps** in the sidebar
2. Click **+ Create Project**
3. Fill in:
   - **Project name**: anything (e.g., "Personal Analytics")
   - **Use case**: select what fits (e.g., "Exploring the API")
   - **Description**: brief description
4. Click **Next** — this creates both a Project and an App inside it
5. You'll see your **App** listed under the project

## Step 3: Generate All 5 Keys

From your App settings page:

### API Key & Secret (Consumer Keys)

1. Go to your App → **Keys and tokens** tab
2. Under **Consumer Keys**, click **Regenerate** (or they may already be shown on first creation)
3. Copy both values:
   - **API Key** (also called Consumer Key) — looks like: `7UmWI5z...`
   - **API Key Secret** (also called Consumer Secret) — looks like: `g9NNNTOi...`
4. Save these somewhere safe — you can't see them again

### Access Token & Secret (User Auth)

1. On the same **Keys and tokens** page, scroll to **Authentication Tokens**
2. Under **Access Token and Secret**, click **Generate**
3. Make sure the permissions say **Read** (that's all this skill needs)
4. Copy both values:
   - **Access Token** — looks like: `963201358...-WUoW5r...`
   - **Access Token Secret** — looks like: `CoI5VNuU...`
5. Save these too

### Bearer Token

1. Still on the **Keys and tokens** page, scroll to **Bearer Token**
2. Click **Generate** (or **Regenerate**)
3. Copy the value — looks like: `AAAAAAAAAAAAA...`
4. This one is optional but recommended for some endpoints

**You should now have 5 values saved:**
| Key | Example format |
|-----|---------------|
| API Key | `7UmWI5zKM1M0pK2...` |
| API Key Secret | `g9NNNTOikCuG5iLS...` |
| Access Token | `963201358...-WUoW5r...` |
| Access Token Secret | `CoI5VNuUV5SqRiJK...` |
| Bearer Token | `AAAAAAAAAAAAAAAAAA...` |

## Step 4: Load API Credits

The X API v2 is pay-per-use. You need credits loaded to make any API calls.

1. Go to [developer.x.com](https://developer.x.com) → **Dashboard**
2. Click on your **Project** → look for **API Credits** or **Billing**
3. Click **Add Credits** or **Top Up**
4. Add at least **$5** (minimum purchase)
   - This skill uses ~$0.60-1.50/month for daily briefings
   - $5 will last you 3-8 months of normal use
5. Your credit balance appears on the dashboard

**Cost reference:**
- Tweet read: ~$0.005 per request
- User read: ~$0.01 per request
- A typical morning briefing costs ~$0.02

## Step 5: Install the Skill

```bash
# Clone into your skills directory
cd ~/.openclaw/workspace/skills  # or wherever you keep skills
git clone https://github.com/aaronnev/x-smart-read.git x-smart-read
```

## Step 6: Run Setup

```bash
cd x-smart-read
uv run scripts/x_setup.py
```

The setup wizard will:

1. **Look for credentials** in `~/.openclaw/.env` first. If found, it imports them automatically. If not, it prompts you to paste each key.

2. **Ask for your X handle** (without the @)

3. **Validate credentials** by calling the X API — you'll see your profile info if it works

4. **Choose a budget tier:**

   | Tier | Daily limit | Monthly cost | Best for |
   |------|------------|-------------|----------|
   | **lite** | $0.03/day | ~$0.50/mo | Morning brief only |
   | **standard** | $0.10/day | ~$1.50/mo | Brief + a few checks (recommended) |
   | **intense** | $0.25/day | ~$5/mo | Frequent monitoring |

5. **Save config** to `~/.openclaw/skills-config/x-twitter/config.json` (permissions set to 0600)

### Alternative: Import from .env

If you prefer, create `~/.openclaw/.env` with your keys before running setup:

```env
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

Then `x_setup.py` will pick them up automatically.

## Step 7: Test It

```bash
# Check your profile (costs ~$0.01)
uv run scripts/x_user.py me

# You should see:
# Profile: Your Name (@yourhandle)
# ========================================
# Followers: 1,234
# Following: 567
# Posts: 890
# ...
```

If that works, try:

```bash
# Pull recent posts (costs ~$0.005)
uv run scripts/x_timeline.py recent --max 5

# Preview cost without making the call
uv run scripts/x_timeline.py --dry-run recent

# Check spend so far
uv run scripts/x_setup.py --spend-report
```

## How Costs Scale

Cost scales with **check frequency**, not content volume. Whether you have 100 or 100K followers, each API call costs the same.

| Usage Pattern | Daily Cost | Monthly Cost |
|--------------|-----------|-------------|
| Morning briefing only | $0.02 | $0.60 |
| Briefing + a few checks | $0.04 | $1.20 |
| Heavy monitoring | $0.10 | $3.00 |

The biggest cost driver is curiosity — reading threads, checking mentions, looking up other users. Posting is free.

## Troubleshooting

### "401 Unauthorized"
- Double-check all 5 keys are correct — one wrong character breaks auth
- Regenerate your Access Token & Secret if unsure
- Make sure your App has at least **Read** permissions

### "402 Payment Required"
- You need API credits loaded. Go to developer.x.com → Billing → Add Credits ($5 min)

### "403 Forbidden"
- Your App may not have the right permissions. Go to App Settings → User authentication settings → make sure Read access is enabled
- You may need to regenerate your Access Token after changing permissions

### "Daily budget exceeded"
- This is the skill protecting your wallet. Wait until tomorrow, or:
  - Use `--force` to override for one command
  - Use `--no-budget` to skip all budget checks/warnings for one command
  - Switch to relaxed mode (warns but never blocks): `uv run scripts/x_setup.py --budget-mode relaxed`
  - Reconfigure with a higher tier: `uv run scripts/x_setup.py --reconfig --tier intense`

### "No config found"
- Run `uv run scripts/x_setup.py` first

### "uv: command not found"
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Then restart your shell or run `source ~/.bashrc`
