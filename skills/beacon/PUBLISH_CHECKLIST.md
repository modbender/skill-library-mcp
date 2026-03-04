# Beacon Publishing Checklist

## 1. GitHub

```bash
cd /home/scott/beacon-skill
git add -A
git commit -m "beacon-skill v0.1.1"
git tag -s v0.1.1 -m "beacon-skill v0.1.1"

# Push using the token stored in ~/git.txt (first line is `ghp_*`).
export GITHUB_TOKEN="$(head -n1 ~/git.txt)"
git push origin main --follow-tags
```

## 2. npm

```bash
export NPM_TOKEN="<your npm token>"
npm version patch   # keep package.json/package-lock in sync
npm publish
```

If you publish from CI, set `NPM_TOKEN` as an environment secret and skip `npm login`.

## 3. PyPI

```bash
python3 -m pip install --upgrade build twine
python3 -m build
twine upload dist/*
```

Export `TWINE_USERNAME`/`TWINE_PASSWORD` or configure `~/.pypirc` ahead of time. Replace tokens with values from your secrets vault (the git.txt file provides the GitHub token only).

## 4. Homebrew

```bash
brew tap Scottcjn/homebrew-beacon
brew bump-formula-pr --version 0.1.1 --url https://registry.npmjs.org/beacon-skill/-/beacon-skill-0.1.1.tgz --sha256 <sha256>
```

Run `brew install --build-from-source --formula ../homebrew-beacon/Formula/beacon.rb` locally to sanity-check the formula before submitting the PR.

## 5. ClawHub

```bash
npx clawhub login --token <clh_token> --no-browser
npx clawhub publish . --slug beacon --version 0.1.1 --name Beacon --description "Agent-to-agent pings with optional RTC value attached"
```

Update the ClawHub payload if `platforms`, `tags`, or `links` change. Use the same token that owns the `beacon` slug.

## 2. ClawHub Registration

ClawHub API base: `https://clawhub.ai/api/v1`

```bash
curl -X POST https://clawhub.ai/api/v1/skills \\
  -H "Authorization: Bearer YOUR_CLAWHUB_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "beacon",
    "description": "Agent-to-agent pings with optional RTC value attached (BoTTube, Moltbook, RustChain)",
    "version": "0.1.0",
    "tags": ["pings", "agent-economy", "bounties", "ads", "rustchain", "bottube", "moltbook"],
    "platforms": ["bottube", "moltbook", "rustchain"],
    "pypi_package": "beacon-skill",
    "github_repo": "Scottcjn/beacon-skill"
  }'
```

## 3. PyPI (Optional)

Use a venv or `pipx`.

```bash
cd /home/scott/beacon-skill
python3 -m venv .venv
. .venv/bin/activate
pip install -U build twine
python -m build
twine upload dist/*
```
