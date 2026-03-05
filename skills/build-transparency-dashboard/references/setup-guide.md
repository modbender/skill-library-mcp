# Setup Guide — Build Transparency Dashboard

This guide walks you through setting up a live public build dashboard that auto-updates on every git push.

**Time to set up:** ~30 minutes  
**What you need:** Two GitHub repos, a Fly.io or Netlify account, Node.js

---

## Overview

```
YOUR PRIVATE REPO (your code)
  └── .github/workflows/update-build-status.yml  ← runs on push
        ├── Checks out your private repo (git log)
        ├── Checks out your PUBLIC SITE repo
        ├── Runs scripts/update-status.js → writes status.json
        └── Commits + pushes status.json to public site

YOUR PUBLIC SITE REPO
  ├── build.html    ← fetches /status.json every 60s
  └── status.json   ← updated automatically on every push
```

---

## Step 1: Set Up Your Two Repos

You need:

1. **Private repo** — your actual product code  
   (already exists, just needs the workflow added)

2. **Public site repo** — a minimal static site  
   Create a new public repo on GitHub, e.g. `username/my-site`

**Minimal public site structure:**

```
my-site/
├── build.html      ← from assets/build.html
├── nav.js          ← from assets/nav.js
├── nav.css         ← from assets/nav.css
├── status.json     ← auto-generated (start with an empty {})
└── index.html      ← your homepage (optional)
```

Copy the files from the `assets/` directory into your public site repo. Start `status.json` with `{}`.

---

## Step 2: Set Up GitHub Actions Secrets

In your **private repo**: GitHub → Settings → Secrets and variables → Actions → New repository secret

| Secret | Value |
|--------|-------|
| `GH_PAT` | A Personal Access Token (classic) with **`repo`** scope. Create at: github.com/settings/tokens |
| `FLY_API_TOKEN` | (optional) Fly.io API token — only if you deploy via Fly |

**Create a PAT:**
1. github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → select `repo` scope → copy the value
3. Add as `GH_PAT` secret in your private repo

---

## Step 3: Customize build.html

Open `assets/build.html` and search for `TODO`. Replace each one:

```
TODO: Replace YOUR_PROJECT_NAME     → "MyApp"
TODO: Replace YOUR_BORN_DATE        → "Jan 1, 2026" (human readable, in the panel)
TODO: Replace YOUR_BORN_DATE_ISO    → "2026-01-01T00:00:00-05:00" (in the JS CONFIG block)
TODO: Replace YOUR_BRAND_COLOR      → "#ff6b6b" (or keep default #7c6eff)
TODO: Replace YOUR_COIN_CA          → Your token CA, or remove the coin section entirely
TODO: Replace YOUR_IDEAS_API_URL    → "https://myapp.fly.dev/public/ideas"
TODO: Replace YOUR_TWITTER_HANDLE   → "@myhandle"
```

Also update:
- The feature list tags (`.tag.done`, `.tag.active`, `.tag`)
- The static shipped log and queue items (these will be overridden by status.json once the workflow runs)

**To remove the coin section:**
Delete the `<div class="coin-panel">` block and change `ideas-layout` grid to `grid-template-columns: 1fr`.

---

## Step 4: Customize nav.js

Open `assets/nav.js` and update the `NAV_CONFIG` object at the top:

```js
const NAV_CONFIG = {
  brand: { prefix: 'MY', accent: 'APP' },  // logo text
  links: [
    { href: '/',      label: 'Home' },
    { href: '/build', label: 'The Build' },
  ],
  badge: {
    label: '@yourhandle ↗',
    href:  'https://x.com/yourhandle',
  },
};
```

---

## Step 5: Configure the GitHub Actions Workflow

Copy `assets/github-actions.yml` to your **private repo** at:

```
.github/workflows/update-build-status.yml
```

Edit the `env` block at the top:

```yaml
env:
  SITE_REPO:      username/my-site        # your public site repo
  SITE_REPO_PATH: my-site                 # checkout directory name
  BOT_NAME:       StatusBot               # git committer name
  BOT_EMAIL:      bot@example.com         # git committer email
  PROJECT_NAME:   MyApp
  PROJECT_DESC:   "A project built in public."
  PROJECT_BORN:   "2026-01-01T00:00:00-05:00"
```

---

## Step 6: Customize update-status.js

Copy `scripts/update-status.js` into your **private repo** at `scripts/update-status.js`.

The script uses the `PROJECT_NAME`, `PROJECT_DESC`, and `PROJECT_BORN` environment variables (set in the workflow). You can also hard-code them if you prefer.

**To update the shipped log and queue:**
Edit the `shipped` and `queue` arrays inside `update-status.js`. They're preserved across runs from the existing `status.json` once it exists — after first run, you can manage them directly in `status.json` in your public site repo.

Or: add a separate script that appends to `status.json`'s shipped array on demand.

---

## Step 7: Add the Ideas API (Optional)

If you want the community ideas board to work:

1. Copy `scripts/ideas-api.js` into your backend app
2. Mount it:
   ```js
   const ideasRouter = require('./ideas-api');
   app.use('/public/ideas', ideasRouter);
   ```
3. Set `IDEAS_API` in `build.html`'s JS config block to your API URL
4. Make sure your server sets `IDEAS_FILE` env var or uses the default `./data/build-ideas.json`

**No backend?** Skip the ideas board — just remove the idea form from `build.html` and keep the rest.

---

## Step 8: Deploy Your Public Site

### Option A: Fly.io

```bash
cd my-site/
fly launch --no-deploy     # creates fly.toml
fly deploy --remote-only --depot=false
```

Fly needs a `Dockerfile` or a static file server. Simplest: add a tiny `Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

Then deploy: `fly deploy --remote-only --depot=false`

To also auto-deploy via GitHub Actions, uncomment the Fly deploy step in the workflow and add `FLY_API_TOKEN` to secrets.

### Option B: Netlify

1. Push your public site repo to GitHub
2. Go to netlify.com → Add new site → Import from Git
3. Select your public site repo → Deploy
4. Done — Netlify auto-deploys on every push (including when the bot commits `status.json`)

### Option C: GitHub Pages

1. In your public site repo: Settings → Pages → Source: Deploy from branch → main
2. Your site will be at `username.github.io/my-site`
3. Use `index.html` as your entry point, or configure root to `build.html`

---

## Step 9: Test It

1. Push a commit to your **private repo**
2. Go to GitHub → Actions → "Update Build Status" — watch it run
3. Check your **public site repo** — you should see a new `status.json` commit from the bot
4. Open your site at `/build` — the status panel should update within 60 seconds

**Manual trigger:** GitHub → Actions → "Update Build Status" → Run workflow

---

## Troubleshooting

**Workflow fails with "Permission denied"**
→ Check `GH_PAT` has `repo` scope and is set as a secret in the private repo

**status.json commits but site doesn't update**
→ The page fetches `/status.json?t=<timestamp>` every 60s. Hard refresh (Ctrl+Shift+R) to see changes immediately.

**Ideas not loading**
→ Check `IDEAS_API` in `build.html` matches your deployed API URL. Check CORS — the API must allow `*` or your site's origin.

**Coin price not loading**
→ Check `COIN_CA` in `build.html`. DexScreener must have a listed pair for this token. If the token isn't on DexScreener, remove the coin section.

**"Days alive" shows NaN**
→ `BORN_DATE_ISO` must be a valid ISO date string: `2026-01-01T00:00:00-05:00`

---

## File Reference

| File | Purpose | Where it lives |
|------|---------|---------------|
| `assets/build.html` | Dashboard page | Public site repo root |
| `assets/nav.js` | Nav renderer | Public site repo root |
| `assets/nav.css` | Nav styles | Public site repo root |
| `assets/github-actions.yml` | CI workflow | Private repo `.github/workflows/` |
| `scripts/update-status.js` | Generates status.json | Private repo `scripts/` |
| `scripts/ideas-api.js` | Ideas board API | Your backend server |

---

## What's in status.json

```json
{
  "generatedAt": "2026-03-01T12:00:00Z",
  "version": "1.2.0",
  "project": {
    "name": "MyApp",
    "description": "A project built in public.",
    "born": "2026-01-01T00:00:00-05:00",
    "status": "building",
    "statusText": "Online · Building"
  },
  "lastCommit": {
    "message": "feat: add dark mode",
    "time": "2026-03-01T11:55:00Z"
  },
  "commitsThisWeek": 12,
  "shipped": [
    { "date": "Mar 01", "text": "Dark mode", "type": "feature" }
  ],
  "queue": [
    { "num": "01", "title": "Next Feature", "desc": "What it does." }
  ],
  "ideas": [],
  "projects": []
}
```

Fields you manage manually: `shipped`, `queue`  
Fields auto-generated: `generatedAt`, `version`, `lastCommit`, `commitsThisWeek`  
Fields persisted from previous run: `ideas`, `projects`
