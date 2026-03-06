# ClawHub Publish Error Map

Use this to quickly classify failures before taking action.

## 1) Browser login fails with `spawn xdg-open ENOENT`

**Cause:** GUI opener not available on headless/server environment.

**Fix options:**
- Preferred: `clawhub login --token <clh_token>`
- Optional: install `xdg-utils`

## 2) `Error: Not logged in. Run: clawhub login`

**Cause:** No stored auth token (or logged out).

**Fix:**
- `clawhub login --token <clh_token>`
- Verify: `clawhub whoami`

## 3) `inspect` says hidden/pending scan or not found right after publish

**Cause:** Newly published skills may be temporarily hidden while security scan indexes.

**Fix:**
- Retry inspect with backoff for a few minutes.
- Confirm web route: `https://clawhub.ai/skills/<slug>`

## 4) Profile URL says not found

**Cause:** Route mismatch/quirk.

**Fix:**
- Use canonical skill links: `/skills/<slug>`
- Use owner+slug link: `/<handle>/<slug>`
- Try `/users/<handle>` for profile pages.

## 5) `rg: command not found`

**Cause:** ripgrep missing.

**Fix:**
- Install ripgrep or use `grep` fallback.

## 6) Mixed `clawhub` vs `clawdhub`

**Cause:** Legacy CLI binary conflict/old install.

**Fix:**
- Standardize on `clawhub`.
- If needed, reinstall: `npm i -g clawhub --force`

## 7) Non-transient publish failures (permission/moderation/validation)

**Symptoms:**
- Consistent error after retries
- Explicit auth/permission/validation message

**Fix:**
- Verify account owner with `clawhub whoami`
- Check slug ownership and version bump
- Re-run publish with corrected slug/version
