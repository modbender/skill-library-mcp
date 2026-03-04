---
name: wp-to-static
description: Convert a WordPress website to a static site and deploy to Cloudflare Pages. Mirrors the rendered HTML via SSH, extracts only referenced assets (shrinks 1.5GB+ to ~25MB), fixes URLs, self-hosts fonts, strips WordPress cruft, and deploys. Use when migrating a WordPress site to static hosting.
disable-model-invocation: true
argument-hint: "[site-url]"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task, WebFetch
metadata: {"openclaw":{"requires":{"bins":["ssh","ssh-agent","rsync","curl","git","gh","wrangler"],"env":["WP_SSH_HOST","WP_SSH_USER","WP_SSH_PORT","WP_SSH_KEY","WP_SITE_URL","WP_SITE_NAME"]},"emoji":"🔄","os":["darwin","linux"]}}
---

# WordPress to Static Site (Cloudflare Pages)

Convert a WordPress website to a pixel-perfect static site and deploy it to Cloudflare Pages. Zero attack surface, zero hosting cost, instant load times.

## Prerequisites

Before running this skill, the user MUST have:

1. **GitHub CLI authenticated:** Run `gh auth status` to verify. If not logged in, run `gh auth login` first.
2. **Cloudflare Wrangler authenticated:** Run `wrangler whoami` to verify. If not logged in, run `wrangler login` first.
3. **SSH key added to ssh-agent:** The recommended way to handle SSH keys. Run:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/your_wp_key
   ```
4. **Server host key verified:** The user should have connected to the server at least once and accepted the host key, so it exists in `~/.ssh/known_hosts`.

## Environment Variables

**Required** (stop and ask if any are missing):
- `WP_SSH_HOST` — SSH hostname (e.g., `ssh.example.com`)
- `WP_SSH_USER` — SSH username
- `WP_SSH_PORT` — SSH port (e.g., `18765`)
- `WP_SSH_KEY` — Path to SSH private key file (e.g., `~/.ssh/wp_key`). Key must have `chmod 600` permissions.
- `WP_SITE_URL` — WordPress site URL (e.g., `https://example.com`)
- `WP_SITE_NAME` — Short project name (e.g., `mysite`)

**Optional:**
- `CF_ACCOUNT_ID` — Cloudflare account ID for Pages deployment
- `GH_REPO_VISIBILITY` — `private` (default) or `public`

## Security Model

- SSH authentication uses `ssh-agent` — keys are loaded into the agent before running, so no passphrase is passed via environment variables or command arguments
- SSH host key verification is ENABLED (no `StrictHostKeyChecking=no`) — the server must already be in `~/.ssh/known_hosts`
- Credentials are NEVER logged, echoed, or displayed
- Credentials are NEVER committed to git
- GitHub repos are created as private by default

## Step 0: Validate

1. Check all required env vars are set. If any are missing, stop and tell the user.
2. Verify required binaries exist: `ssh`, `ssh-agent`, `rsync`, `curl`, `git`, `gh`, `wrangler`.
3. Verify `gh auth status` succeeds. If not, tell user to run `gh auth login`.
4. Verify `wrangler whoami` succeeds (if `CF_ACCOUNT_ID` is set). If not, tell user to run `wrangler login`.
5. Verify SSH key file exists and has correct permissions (`chmod 600`).
6. Stop if anything is missing.

## Step 1: Test SSH Connection

Test the connection using the key from ssh-agent:

```bash
ssh -i $WP_SSH_KEY -p $WP_SSH_PORT $WP_SSH_USER@$WP_SSH_HOST "echo connected"
```

If the key requires a passphrase and ssh-agent is not loaded, tell the user:
```
Please add your SSH key to ssh-agent first:
  eval "$(ssh-agent -s)"
  ssh-add /path/to/your/key
Then re-run /wp-to-static
```

If the host key is not recognized, tell the user to connect manually once first to verify and accept the host key:
```
Please connect to the server once manually to verify the host key:
  ssh -i $WP_SSH_KEY -p $WP_SSH_PORT $WP_SSH_USER@$WP_SSH_HOST
Accept the host key, then re-run /wp-to-static
```

Do NOT use `StrictHostKeyChecking=no`. Do NOT bypass host key verification.

## Step 2: Locate WordPress Installation

SSH in and find the WordPress `public_html` directory. Common locations:
- `~/www/DOMAIN/public_html/`
- `~/public_html/`
- `~/htdocs/`
- `/var/www/html/`

Confirm by finding `wp-config.php`. Store path as `WP_ROOT`.

## Step 3: Mirror with wget (ON THE SERVER)

Run `wget --mirror` **on the server** (not locally):

```bash
cd /tmp && rm -rf static_mirror && mkdir -p static_mirror && cd static_mirror && \
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent \
  --restrict-file-names=windows -e robots=off --timeout=30 --tries=3 --wait=0.5 \
  --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  $WP_SITE_URL/ 2>&1 | tail -30
```

If `wget` is not available on the server, fall back to `curl` locally for rendered HTML.

## Step 4: Rsync to Local

Create `./build/site` (NEVER use the project root as temp dir).

**Exclude server-side code and sensitive files.** Only static assets (images, CSS, JS, fonts) are needed. PHP files, config files, and other server-side code must NEVER be downloaded.

```bash
RSYNC_EXCLUDE="--exclude='*.php' --exclude='wp-config*' --exclude='.htaccess' --exclude='*.sql' --exclude='*.log' --exclude='debug.log' --exclude='error_log' --exclude='.env' --exclude='*.bak' --exclude='*.backup'"

rsync -avz $RSYNC_EXCLUDE server:/tmp/static_mirror/DOMAIN/ ./build/site/
rsync -avz $RSYNC_EXCLUDE server:$WP_ROOT/wp-content/uploads/ ./build/site/wp-content/uploads/
rsync -avz $RSYNC_EXCLUDE server:$WP_ROOT/wp-content/themes/ ./build/site/wp-content/themes/
rsync -avz $RSYNC_EXCLUDE server:$WP_ROOT/wp-content/plugins/ ./build/site/wp-content/plugins/
rsync -avz $RSYNC_EXCLUDE server:$WP_ROOT/wp-includes/ ./build/site/wp-includes/
```

After rsync, verify no PHP or config files were downloaded:
```bash
find ./build/site -name '*.php' -o -name 'wp-config*' -o -name '.htaccess' -o -name '.env' | head -20
```
If any are found, delete them before proceeding.

## Step 5: Extract Only Referenced Assets

**This is the key step.** Parse all HTML and CSS files to find every referenced local file:

**From HTML:** `src=`, `href=`, `data-src=`, `data-srcset=`, `srcset=`, inline `background-image: url()`

**From CSS:** All `url()` references — resolve relative paths from CSS file location to site root.

Write the list to `./build/referenced-files.txt`, then copy only those files to `./public/` preserving directory structure. This typically shrinks 1.5GB+ down to ~25MB.

## Step 6: Fix Absolute URLs

In `index.html` and ALL CSS files:

1. Replace `$WP_SITE_URL/` → empty string (relative paths)
2. Replace any staging/dev domain URLs → local paths
3. Self-host Google Fonts:
   - Download each `.ttf` to `./public/fonts/`
   - Update `@font-face src:` to `fonts/filename.ttf`
4. Remove `<link rel="preconnect">` for Google Fonts domains

**CSS path resolution is critical.** If CSS is at `wp-content/uploads/cache/file.css`:
- `wp-content/uploads/` → `../../`
- `wp-content/themes/` → `../../themes/`
- `wp-includes/` → `../../../wp-includes/`

## Step 7: Strip WordPress Cruft

**Remove:**
- `<meta name="generator" ...>` (WordPress, WPBakery, Slider Revolution)
- `<link rel="EditURI"...>`, `<link rel="alternate"...>` (RSS, oEmbed)
- `<link rel="https://api.w.org/"...>`, `<link rel="shortlink"...>`
- `<link rel="profile" href="gmpg.org/xfn/11">`
- `<link rel="dns-prefetch"...>` for fonts.googleapis.com
- W3 Total Cache HTML comments
- `wp-json` root references in inline JSON

**Keep:** Email addresses, `<link rel="canonical">` (update to `/`)

## Step 8: Cloudflare Pages Config

Create `./public/_headers` with aggressive caching for `/fonts/*`, `/wp-content/*`, `/wp-includes/*`.

Create `./public/_redirects` redirecting `/wp-admin/*`, `/wp-login.php`, `/xmlrpc.php`, `/feed/*` → `/` (302).

## Step 9: Verify Locally

1. Start `python3 -m http.server` from `./public/`
2. Test key assets return HTTP 200 (CSS, JS, logo, fonts, images)
3. Tell user to open the URL and visually verify
4. **Wait for user confirmation before deploying**

## Step 10: Scrub Temporary Files and Deploy

**Before any git operations**, remove the `./build/` directory to ensure no server-side code, PHP files, or sensitive data can accidentally be committed:

```bash
rm -rf ./build
```

Verify only `./public/` remains and contains no PHP or config files:
```bash
find ./public -name '*.php' -o -name 'wp-config*' -o -name '.htaccess' -o -name '.env'
```
This must return empty. If not, delete those files before proceeding.

Then deploy:
1. `git init`, commit ONLY `./public/` and `.gitignore`
2. `git config http.postBuffer 524288000` (for binary assets)
3. `gh repo create $WP_SITE_NAME --private --source=. --push`
4. `CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID wrangler pages project create $WP_SITE_NAME --production-branch main`
5. `CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID wrangler pages deploy ./public --project-name $WP_SITE_NAME`
6. Verify deployment, report live URL, remind about custom domain setup

## Safety Rules

- NEVER display or log credentials (SSH keys, passphrases, tokens)
- NEVER commit credentials to git (.gitignore must exclude .env, *.key, *.pem)
- NEVER use `StrictHostKeyChecking=no` or bypass SSH host verification
- NEVER pass passphrases as command-line arguments or environment variables at runtime
- NEVER delete the current working directory (breaks the shell CWD)
- NEVER force-push or use destructive git commands
- NEVER rsync PHP files, wp-config, .htaccess, .env, or SQL dumps from the server
- Use `./build/` for temp files, `./public/` for output — only `./public/` is committed
- ALWAYS delete `./build/` BEFORE any git operations to prevent accidental commits of server-side files
- Verify `./public/` contains no PHP or config files before committing
- Stop and report on any failure — do NOT retry blindly
