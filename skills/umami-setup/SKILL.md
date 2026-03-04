---
name: umami-setup
description: "Add Umami self-hosted analytics to any website with adblocker-proof proxy. Covers: creating the website in Umami, setting up a same-domain proxy (Next.js, Astro/Vercel, Caddy, Nginx), and verifying tracking works."
homepage: "https://casys.ai"
source: "https://github.com/Casys-AI/casys-pml-cloud"
author: "Erwan Lee Pesle (superWorldSavior)"
always: false
privileged: false
---

# umami-setup — Add analytics to a new website

## Overview

Self-hosted Umami analytics with a same-domain proxy to bypass adblockers. The script is served from the same domain as your site, so blockers see it as first-party.

## Prerequisites

- A running Umami instance (self-hosted, e.g. `analytics.casys.ai`)
- Admin credentials for Umami
- Access to the website's codebase for proxy configuration

## Step 1: Create the website in Umami

```bash
# Login
TOKEN=$(curl -s -X POST "https://<UMAMI_HOST>/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<PASSWORD>"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

# Create website
curl -s -X POST "https://<UMAMI_HOST>/api/websites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"<SITE_NAME>","domain":"<DOMAIN>"}' | python3 -m json.tool
```

Save the `id` from the response — that's your `data-website-id`.

## Step 2: Set up the proxy

The proxy serves the Umami script and send endpoint from your own domain. Adblockers can't distinguish it from your own assets.

Pick the method matching your stack:

### Next.js (rewrites in next.config.ts)

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/u/script.js",
        destination: "https://<UMAMI_HOST>/script.js",
      },
      {
        source: "/u/api/send",
        destination: "https://<UMAMI_HOST>/api/send",
      },
    ];
  },
};
```

Then add to your layout:
```html
<script defer src="/u/script.js" data-website-id="<WEBSITE_ID>"></script>
```

### Astro + Vercel (rewrites in vercel.json)

```json
{
  "rewrites": [
    {
      "source": "/u/script.js",
      "destination": "https://<UMAMI_HOST>/script.js"
    },
    {
      "source": "/u/api/send",
      "destination": "https://<UMAMI_HOST>/api/send"
    }
  ]
}
```

Then add before `</head>` in your layout(s):
```html
<script defer src="/u/script.js" data-website-id="<WEBSITE_ID>"></script>
```

### Caddy (reverse proxy)

```caddyfile
example.com {
    handle /u/script.js {
        rewrite * /script.js
        reverse_proxy https://<UMAMI_HOST> {
            header_up Host <UMAMI_HOST>
        }
    }
    handle /u/api/send {
        rewrite * /api/send
        reverse_proxy https://<UMAMI_HOST> {
            header_up Host <UMAMI_HOST>
        }
    }
}
```

### Nginx

```nginx
location /u/script.js {
    proxy_pass https://<UMAMI_HOST>/script.js;
    proxy_set_header Host <UMAMI_HOST>;
}
location /u/api/send {
    proxy_pass https://<UMAMI_HOST>/api/send;
    proxy_set_header Host <UMAMI_HOST>;
}
```

## Step 3: Verify

1. **Deploy** the proxy config
2. **Visit your site** in a browser
3. **Check Umami dashboard** — you should see a pageview within seconds
4. **Test with adblocker enabled** — visit again with uBlock Origin on; the pageview should still appear
5. **Verify the proxy** works: `curl -sI https://<YOUR_DOMAIN>/u/script.js` should return 200

## Proxy path convention

Use `/u/` as the proxy prefix. It's short, non-obvious to blockers, and consistent across projects:

| Project | Proxy path | Umami host |
|---------|-----------|------------|
| thenocodeguy.com | `/umami/script.js` | analytics.casys.ai |
| casys.ai | `/u/script.js` | analytics.casys.ai |

## Umami API — quick reference

```bash
# Get all websites
curl -s -H "Authorization: Bearer $TOKEN" "https://<UMAMI_HOST>/api/websites"

# Get stats for a website (last 24h)
START=$(($(date +%s) * 1000 - 86400000))
END=$(($(date +%s) * 1000))
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<UMAMI_HOST>/api/websites/<WEBSITE_ID>/stats?startAt=$START&endAt=$END"

# Get pageviews
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<UMAMI_HOST>/api/websites/<WEBSITE_ID>/pageviews?startAt=$START&endAt=$END&unit=day"
```

## Notes

- The Umami instance should be behind a reverse proxy with HTTPS (e.g. Cloudflare → Caddy → localhost:3002)
- Docker bind on `127.0.0.1` only — never expose Umami directly to the internet
- The `/u/` prefix can be anything — `/stats/`, `/t/`, etc. — as long as it doesn't conflict with existing routes
