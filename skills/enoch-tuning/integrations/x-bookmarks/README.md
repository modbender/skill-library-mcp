# Integration: X Bookmarks Sync

Pull your X bookmarks automatically, detect new ones since last sync, and run a research pipeline that verdicts each one — so you never let a good find die in your bookmarks tab.

---

## What It Does

- Pulls all your X bookmarks via the official X API (OAuth 2.0)
- Detects which ones are new since last sync
- Saves a trigger file your agent can analyze
- Auto-refreshes your OAuth token — set it once, runs indefinitely
- Research protocol gives each bookmark a verdict: ARCHIVE / READ_DEEPER / ACT_ON / SHARE / BUILD

---

## What You Need

- X Developer account at developer.x.com (free tier works)
- A Project + App with OAuth 2.0 enabled
- User authentication configured with these scopes: `bookmark.read tweet.read users.read offline.access`
- Callback URL: `http://127.0.0.1:1455/auth/callback`

---

## Setup

### Step 1 — Create your X Developer App

1. Go to developer.x.com → Projects & Apps → New App
2. Enable OAuth 2.0 with User authentication
3. Set callback URL to `http://127.0.0.1:1455/auth/callback`
4. Copy your Client ID and Client Secret

### Step 2 — Save credentials

```bash
mkdir -p ~/.openclaw/credentials
cat > ~/.openclaw/credentials/x-oauth-creds.json << 'EOF'
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
EOF
chmod 600 ~/.openclaw/credentials/x-oauth-creds.json
```

### Step 3 — Run the auth flow (one time only)

```bash
export X_OAUTH_CLIENT_ID="YOUR_CLIENT_ID"
export X_OAUTH_CLIENT_SECRET="YOUR_CLIENT_SECRET"
bash integrations/x-bookmarks/scripts/x-bookmarks-auth.sh
```

Browser opens → authorize → token saves automatically to `~/.openclaw/credentials/x-oauth-token.json`

### Step 4 — Copy scripts to your workspace

```bash
cp integrations/x-bookmarks/scripts/x-bookmarks-sync.py scripts/
cp integrations/x-bookmarks/scripts/x-bookmarks-auth.sh scripts/
cp integrations/x-bookmarks/research-prompt.md scripts/x-bookmark-research-prompt.md
```

### Step 5 — Test it

```bash
python3 scripts/x-bookmarks-sync.py --detect-new
```

Check `research/x-bookmarks-raw.json` — your bookmarks should be there.

### Step 6 — Wire the cron (optional)

Tell your agent: "Set up a daily cron at 10 AM to run `python3 scripts/x-bookmarks-sync.py --detect-new` and analyze new bookmarks."

---

## Files

```
integrations/x-bookmarks/
├── README.md                  ← this file
├── research-prompt.md         ← protocol your agent follows when analyzing bookmarks
└── scripts/
    ├── x-bookmarks-sync.py    ← pulls bookmarks, detects new, writes trigger file
    └── x-bookmarks-auth.sh    ← one-time OAuth flow to generate your token
```

Output files (created in your workspace):
- `research/x-bookmarks-raw.json` — full bookmark archive
- `research/x-bookmarks_latest.md` — human-readable markdown view
- `research/x-bookmarks-new.json` — trigger file (new since last sync)
- `research/vetted/` — verdicted briefs, one file per analyzed bookmark

---

## Notes

- Token refreshes automatically — you won't need to re-auth unless you revoke access
- X API free tier: 1 app, limited reads per month. Bookmark sync is low-volume, fits comfortably.
- Don't try to web_fetch x.com URLs — X blocks scrapers. The sync script uses the official API.
