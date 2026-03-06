# Step-by-step: Publish clawd-migrate to npm

Follow these in order to publish this package to npm so anyone can run `npx clawd-migrate`.

---

## Step 1: Create an npm account (if you don’t have one)

1. Go to [npmjs.com/signup](https://www.npmjs.com/signup).
2. Sign up with email (or GitHub).
3. Confirm your email if prompted.

---

## Step 2: Log in to npm from the terminal

From any directory:

```bash
npm login
```

- **Username:** your npm username  
- **Password:** your npm password  
- **Email:** (your email, or one already on the account)  
- **OTP:** if you have 2FA, enter the code from your app or email  

You should see: `Logged in as YOUR_USERNAME on https://registry.npmjs.org/`.

---

## Step 3: (Optional) Set repository URL in package.json

If this repo is on GitHub, add the URL so the npm page links to it. In `package.json`, set:

```json
"repository": {
  "type": "git",
  "url": "https://github.com/YOUR_USERNAME/clawd-migrate.git"
}
```

Replace `YOUR_USERNAME` with your GitHub username. You can also set `"author": "Your Name <you@example.com>"` if you want.

---

## Step 4: Check the package name

Open `package.json` and confirm:

- **name:** `clawd-migrate` (must be unique on npm; if taken, use a scoped name like `@yourusername/clawd-migrate`).
- **version:** e.g. `0.1.0` (you can leave as-is for first publish).

If you use a scoped name (e.g. `@yourusername/clawd-migrate`), you’ll need `npm publish --access public` in Step 6.

---

## Step 5: Dry run (see what will be published)

From the **clawd_migrate** folder (repo root):

```bash
cd c:\Users\Douglas\clawd\clawd_migrate
npm pack --dry-run
```

This lists the files that would go in the tarball. You should see `bin/` and `lib/` (and package.json); no Python source at root (it’s copied into `lib/clawd_migrate/` by the prepublish script).

Optional: create a real tarball and inspect it:

```bash
npm pack
```

That creates `clawd-migrate-0.1.0.tgz`. You can delete it after; it’s not needed for publish.

---

## Step 6: Publish

From the **clawd_migrate** folder:

```bash
npm publish
```

- If the **name** is unscoped (`clawd-migrate`): that’s it.
- If the **name** is scoped (e.g. `@yourusername/clawd-migrate`): run:

  ```bash
  npm publish --access public
  ```

You should see something like: `+ clawd-migrate@0.1.0` (or your scoped name).

---

## Step 7: Verify

1. Open [npmjs.com/package/clawd-migrate](https://www.npmjs.com/package/clawd-migrate) (or your scoped package URL).
2. Install and run:

   ```bash
   npx clawd-migrate discover
   ```

If that runs and shows JSON (or the interactive menu with no args), you’re done.

---

## Later: bump version and publish again

1. Edit `package.json`: bump **version** (e.g. `0.1.0` → `0.1.1` or `0.2.0`). Optionally bump `__init__.py` `__version__` to match.
2. From repo root:

   ```bash
   npm publish
   ```

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `You must verify your email` | Verify the email in the link npm sent. |
| `Package name already taken` | Change **name** in package.json (e.g. `clawd-migrate-tools`) or use a scoped name: `@yourusername/clawd-migrate` and `npm publish --access public`. |
| `403 Forbidden` | You’re not logged in or don’t have permission; run `npm login` again. |
| `prepublishOnly` fails | Run `node scripts/copy-py.js` from repo root; fix any errors (e.g. missing files). |
| Users get “Python not found” | The package requires Python 3 on PATH; say so in README (already there). |
