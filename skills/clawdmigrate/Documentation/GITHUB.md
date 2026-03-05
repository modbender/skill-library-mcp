# This repository: clawd-migrate only

**This folder (`clawd_migrate`) is the full repository.** There is one Git repo here; everything you need to publish lives in this directory.

---

## First-time: push to a new GitHub repo

### 1. Create an empty repo on GitHub

1. Go to [github.com](https://github.com) and sign in.
2. Click **New repository** (or **+** → **New repository**).
3. **Repository name:** e.g. `clawd-migrate`
4. **Public**
5. Do **not** add a README, .gitignore, or license (you already have them in this folder).
6. Click **Create repository**.

### 2. Add, commit, and push from this folder

From **this folder** (the `clawd_migrate` directory):

```bash
git add .
git status   # confirm .gitignore is excluding lib/, __pycache__, node_modules/
git commit -m "Initial commit: clawd-migrate for moltbot/clawdbot to openclaw"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name (e.g. `clawd-migrate`).

**Using SSH instead of HTTPS:**

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## After the first push

### Link package.json to the repo (optional)

In `package.json`, set:

```json
"repository": {
  "type": "git",
  "url": "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
}
```

Then:

```bash
git add package.json
git commit -m "Add repository URL to package.json"
git push
```

### Publish to npm (optional)

1. [npmjs.com](https://www.npmjs.com) account and `npm login`.
2. From this folder: `npm publish` (or `npm publish --access public` for a scoped package).

---

## What’s in this repo

- **Tracked:** All source (`.py`, `bin/`, `scripts/`, `tests/`, `Documentation/`), `package.json`, `README.md`, `HOW_TO_RUN.md`, `.gitignore`.
- **Ignored:** `lib/` (generated on npm publish), `__pycache__/`, `node_modules/`.

Clone this repo and run `npm test` to run tests, or install via npm once published.
