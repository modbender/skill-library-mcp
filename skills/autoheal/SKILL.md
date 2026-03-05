---
name: autoheal
version: 1.0.0
description: Add AI-powered error monitoring and auto-fix generation to any project
requires:
  env:
    - AUTOHEAL_API_KEY
---

# AutoHeal AI Skill

AutoHeal captures production JavaScript/TypeScript errors, analyzes them with AI, and generates platform-specific fix prompts you can paste directly into your AI coding tool.

## 1. Setup AutoHeal in a Project

### Browser Project (React, Next.js, Vue, Svelte, etc.)

Add this snippet to your app's entry point (e.g., `main.tsx`, `layout.tsx`, `App.vue`):

```html
<script>
window.onerror = function(msg, source, line, col, err) {
  fetch("https://autohealai.com/api/errors/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      key: process.env.AUTOHEAL_API_KEY || "YOUR_API_KEY",
      message: msg,
      stack: err?.stack || "",
      source_url: source,
      browser: navigator.userAgent
    })
  }).catch(() => {});
};

window.onunhandledrejection = function(e) {
  const err = e.reason;
  fetch("https://autohealai.com/api/errors/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      key: process.env.AUTOHEAL_API_KEY || "YOUR_API_KEY",
      message: err?.message || String(err),
      stack: err?.stack || "",
      source_url: window.location.href,
      browser: navigator.userAgent
    })
  }).catch(() => {});
};
</script>
```

### Node.js / Server Project

Add this to your server entry point:

```javascript
process.on('uncaughtException', (err) => {
  fetch("https://autohealai.com/api/errors/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      key: process.env.AUTOHEAL_API_KEY,
      message: err.message,
      stack: err.stack || ""
    })
  }).catch(() => {});
});

process.on('unhandledRejection', (reason) => {
  const err = reason instanceof Error ? reason : new Error(String(reason));
  fetch("https://autohealai.com/api/errors/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      key: process.env.AUTOHEAL_API_KEY,
      message: err.message,
      stack: err.stack || ""
    })
  }).catch(() => {});
});
```

## 2. Check Error Status

After an error is ingested, check its analysis status:

```bash
curl -s "https://autohealai.com/api/errors/{ERROR_ID}/status" \
  -H "Authorization: Bearer $AUTOHEAL_API_KEY"
```

Response:
```json
{
  "status": "analyzed",
  "message": "Cannot read properties of undefined",
  "has_fix": true,
  "fix_id": "uuid-here",
  "dashboard_url": "https://autohealai.com/dashboard/errors/{ERROR_ID}"
}
```

Possible statuses: `new`, `analyzing`, `analyzed`, `fix_applied`, `ignored`

View the full fix with AI-generated fix prompt at the `dashboard_url`.

## 3. Report an Error Manually

Send any error directly to AutoHeal:

```bash
curl -X POST "https://autohealai.com/api/errors/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "'$AUTOHEAL_API_KEY'",
    "message": "TypeError: Cannot read properties of undefined (reading '\''map'\'')",
    "stack": "TypeError: Cannot read properties of undefined\n    at renderList (src/components/List.tsx:15:23)"
  }'
```

Response:
```json
{
  "status": "queued",
  "error_id": "uuid-here"
}
```

The error will be analyzed by AI within seconds. Check status using the error_id from the response.
