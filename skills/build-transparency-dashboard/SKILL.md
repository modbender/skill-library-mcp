# build-transparency-dashboard

Scaffold a live public "build dashboard" that automatically shows proof of work — commit count, last commit message, timestamp — pulled from a private GitHub repo and displayed on a public static site.

## When to Use

Use this skill when you want to:
- Show your community what you're shipping, updated automatically on every push
- Build in public without exposing your private repo
- Add a community ideas board to let people vote on what you build next
- Create a polished `/build` page for your product or project

## The Pattern

```
Private repo (your code)
  └── GitHub Actions: on push → runs update-status.js
        └── Writes status.json → commits to public site repo
              └── Public site fetches status.json every 60s → displays live stats
```

**Result:** every git push to your private repo automatically updates your public dashboard within minutes.

## What's Included

```
build-transparency-dashboard/
├── SKILL.md                     ← this file
├── scripts/
│   ├── update-status.js         ← generates status.json from git log
│   └── ideas-api.js             ← Express routes for community ideas board
├── assets/
│   ├── build.html               ← dashboard page template
│   ├── nav.js                   ← shared nav renderer (configurable)
│   ├── nav.css                  ← nav styles
│   └── github-actions.yml       ← GitHub Actions workflow template
└── references/
    └── setup-guide.md           ← step-by-step setup instructions
```

## Quick Setup

### 1. Variables to Customize

In `assets/build.html`, search for these TODOs:

| TODO | Replace With |
|------|-------------|
| `YOUR_PROJECT_NAME` | Your project's display name (e.g. `MyApp`) |
| `YOUR_BORN_DATE` | ISO date your project started (e.g. `2026-01-01T00:00:00-05:00`) |
| `YOUR_BRAND_COLOR` | Hex color (default: `#7c6eff`) |
| `YOUR_COIN_CA` | Token contract address, or remove the coin section entirely |
| `YOUR_IDEAS_API_URL` | Base URL of your ideas API (e.g. `https://myapp.fly.dev/public/ideas`) |
| `YOUR_TWITTER_HANDLE` | Your @handle for the nav badge |
| `YOUR_QUEUE_ITEMS` | What you're building next (edit the queue section) |

In `assets/github-actions.yml`, set these:

| Variable | Description |
|----------|-------------|
| `SITE_REPO` | Your public site repo (e.g. `username/my-site`) |
| `SITE_REPO_PATH` | Directory name for checkout (e.g. `my-site`) |
| `BOT_NAME` | Committer name (e.g. `StatusBot`) |
| `BOT_EMAIL` | Committer email |

In `assets/nav.js`, edit the config object at the top:

```js
const NAV_CONFIG = {
  brand: 'MYAPP',            // nav logo text
  links: [
    { href: '/', label: 'Home' },
    { href: '/build', label: 'The Build' },
  ],
  badge: { label: '@yourhandle ↗', href: 'https://x.com/yourhandle' },
};
```

### 2. GitHub Secret Required

Add to your private repo → Settings → Secrets and variables → Actions:

- `GH_PAT` — Personal Access Token with `repo` scope (to push to the public site repo)

### 3. Deploy Your Public Site

The `build.html` file is a standalone static page. Deploy anywhere:

- **Fly.io:** `fly launch` + `fly deploy` in your site repo
- **Netlify:** drag & drop or connect repo
- **GitHub Pages:** push to a `gh-pages` branch
- **Vercel:** connect repo, zero config

### 4. Add the Ideas API (Optional)

The community ideas board requires a running API. Copy `scripts/ideas-api.js` into your backend app and mount the routes. It uses a flat JSON file for storage — no database needed.

Or skip it entirely: remove the coin/ideas section from `build.html` and it works as a pure static display.

### 5. Add the Workflow to Your Private Repo

Copy `assets/github-actions.yml` to `.github/workflows/update-build-status.yml` in your private repo. Push a commit — the workflow fires automatically.

## status.json Shape

The workflow generates this file and commits it to your public site repo:

```json
{
  "generatedAt": "2026-02-28T21:00:00Z",
  "version": "1.0.0",
  "project": {
    "name": "MyApp",
    "description": "Your project description.",
    "born": "2026-01-01T00:00:00-05:00",
    "status": "building",
    "statusText": "Online · Building"
  },
  "lastCommit": {
    "message": "feat: add dark mode",
    "time": "2026-02-28T20:55:00Z"
  },
  "commitsThisWeek": 12,
  "shipped": [],
  "queue": [],
  "ideas": []
}
```

## Design System

The template uses:
- **Syne** (display headings) + **DM Sans** (body) + **DM Mono** (mono/labels)
- Dark theme — `#050508` background, `#7c6eff` brand accent
- Noise overlay, animated orbs, fixed ticker bar
- Fully responsive (desktop → tablet → mobile)

Swap `--nova` / `--nova2` CSS vars for your brand color.

## See a Live Example

The pattern was built for [novaiok-site.fly.dev/build](https://novaiok-site.fly.dev/build). That's the reference implementation.

## Files to Read Next

- `references/setup-guide.md` — detailed step-by-step with commands
- `assets/build.html` — the template (search TODOs)
- `assets/github-actions.yml` — the workflow
