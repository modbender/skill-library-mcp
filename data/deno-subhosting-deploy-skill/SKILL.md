---
name: deno-deploy
description: Deploy simple web pages and HTML apps live to the internet using the Deno Deploy REST API. Use this skill whenever the user wants to make something "live", "hosted", "shareable via URL", "deployed", or "accessible online" — even if they don't mention Deno explicitly. Also trigger when the user asks to build a web page, interactive app, or HTML project that would benefit from a live URL. Does not require the Deno MCP tool — this skill is fully standalone and uses the Deno API directly.
license: Apache-2.0
metadata:
   author: hosainnet
   version: "0.0.1"
---

# Deno Deploy Skill (Standalone)

Deploy simple web pages and HTML apps to Deno Deploy using a bundled Python script that calls the Deno REST API directly. No MCP tool required.

---

## Credentials Setup (First Time)

Before deploying, the user must create a **Deno Subhosting organization** and retrieve their credentials:

1. Go to [dash.deno.com/subhosting/new_auto](https://dash.deno.com/subhosting/new_auto) and create a new subhosting org
2. From the org dashboard, copy the **org ID** and **access token**

Then save them as config files under `~/.config/deno-deploy/`:

```bash
mkdir -p ~/.config/deno-deploy
echo "your_token_here" > ~/.config/deno-deploy/access_token
echo "your_org_id_here" > ~/.config/deno-deploy/org_id
```

If these files don't exist, the deploy script will print a clear error with setup instructions. Direct the user to [dash.deno.com/subhosting/new_auto](https://dash.deno.com/subhosting/new_auto) to get started.

---

## Step 1: Plan the App

Before writing code, think about:
- What HTML/CSS/JS is needed?
- Does it need external libraries? (Use CDN links — no npm installs)
- Is it purely static, or does it need a simple backend (e.g., an API route)?

For simple pages: serve everything from a single `main.ts` file with inline HTML.

---

## Step 2: Write Good Deno-Compatible Code

### Standard Pattern

All Deno Deploy apps must export a `fetch` handler:

```typescript
export default {
  async fetch(req: Request): Promise<Response> {
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
</head>
<body>
  <!-- content here -->
</body>
</html>`;

    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  },
};
```

### Key Rules

- **No Node.js APIs** — no `require()`, no `fs`, no `path`
- **No npm packages** — use CDN links (e.g. `https://cdn.tailwindcss.com`)
- **Single file** — inline all HTML, CSS, JS as template literals in `main.ts`
- **Always set Content-Type** — include `charset=utf-8` for HTML responses
- **Routing** — use `new URL(req.url).pathname` for multi-route apps

### Useful CDN Libraries

| Purpose | URL |
|---|---|
| Tailwind CSS | `https://cdn.tailwindcss.com` |
| Alpine.js | `https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js` |
| Chart.js | `https://cdn.jsdelivr.net/npm/chart.js` |
| Marked (markdown) | `https://cdn.jsdelivr.net/npm/marked/marked.min.js` |

---

## Step 3: Save the Code to a File

Write the TypeScript code to a temporary file, e.g. `/tmp/main.ts`:

```bash
cat > /tmp/main.ts << 'EOF'
export default {
  async fetch(req: Request): Promise<Response> {
    ...
  },
};
EOF
```

---

## Step 4: Deploy Using the Script

Run the bundled deploy script:

```bash
python scripts/deploy.py \
  --name <project-name> \
  --code /tmp/main.ts
```

**Project naming tips:**
- Use the topic/purpose: `birthday-card`, `sales-dashboard`, `quiz-game`
- Lowercase, hyphens only, max ~30 chars
- Avoid generic names like `app` or `test`

The script will:
1. Create a new Deno Deploy project
2. Upload the code
3. Print the live URL

---

## Step 5: Verify the Deployment

After the deploy script runs, you MUST verify the deployment was successful:

1. **Check the script output** — look at the deployment response JSON printed by the script:
   - `"status"` should NOT be `"failed"`. If it is, the code has errors — fix and redeploy.
   - If the status is `"pending"`, wait a few seconds and proceed to the next check.

2. **Curl the live URL** to confirm it's serving correctly:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://<project-name>.deno.dev
   ```
   - **200** = success, the page is live
   - **404** or **500** = something is wrong — check the deployment logs URL printed by the script
   - **Any other error** = the deployment may still be propagating, wait 5 seconds and retry once

3. **If the deployment failed**, check for these common causes:
   - Syntax errors in the TypeScript code (missing braces, unclosed template literals)
   - Missing `export default { fetch }` handler
   - Use of Node.js APIs (`require`, `fs`, etc.)
   - Fix the issue in the code file and redeploy

Do NOT tell the user the deployment succeeded until you have confirmed it with curl.

---

## Step 6: Share the Result

After a **verified** successful deployment, always:

1. **Share the live URL** prominently as a clickable link
2. **Briefly explain** what the user will see when they open it

Example:
> Your page is live at **https://your-project.deno.dev**
>
> It shows [brief description]. Let me know if you'd like to change anything!

---

## Common Pitfalls

- Don't forget `<!DOCTYPE html>` — browsers may render in quirks mode without it
- Don't use backticks inside template literals without escaping them
- Don't forget `export default { fetch }` — the app won't start without it
- If the project name is already taken, try a more specific name or add a suffix
