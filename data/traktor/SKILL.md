---
name: traktor
description: |
  Extract all assets and content from websites including images, SVGs, fonts,
  videos, and page structure. Parallel agents with thorough scraping coverage.
  Triggers: "extract assets", "scrape website", "download site assets",
  "get all images from", or "/traktor url". Supports multiple URLs.
compatibility: |
  Requires Claude Code with claude-in-chrome MCP server (browser extension).
  Will not work on Claude.ai or API without browser automation capability.
metadata:
  version: 2.0.0
---

# Traktor - web asset extraction skill v2.0

Follow these steps exactly when extracting website assets.

## Trigger

`/traktor <url1> [url2] [url3]...`

---

## Step 1: Parse URLs from arguments

Extract all URLs from the user's command. Store them in a list.

```text
URLS = [all URLs provided after /traktor]
SITE_COUNT = number of URLs
PROJECT_DIR = current working directory
```

---

## Step 2: Create folder structure

### If SITE_COUNT == 1

**RUN THIS BASH COMMAND:**
```bash
mkdir -p assets/{logos,icons,images,videos,fonts,backgrounds} full-site/{pages,assets,styles}
```

### If SITE_COUNT > 1

**For each URL, extract site name (e.g., "stripe.com" -> "stripe-com") and RUN:**
```bash
# Replace {site-name} with actual site name for each URL
mkdir -p assets/{site-name}/{logos,icons,images,videos,fonts,backgrounds}
mkdir -p full-sites/{site-name}/{pages,assets,styles}
```

**Example for 3 sites:**
```bash
mkdir -p assets/{stripe-com,vercel-com,linear-app}/{logos,icons,images,videos,fonts,backgrounds}
mkdir -p full-sites/{stripe-com,vercel-com,linear-app}/{pages,assets,styles}
```

---

## Step 3: Spawn extraction agents

**For EACH URL, call the Task tool with these EXACT parameters:**

```text
Tool: Task
Parameters:
  - subagent_type: "general-purpose"
  - run_in_background: true
  - description: "Extract {site-name} assets"
  - prompt: [USE THE AGENT PROMPT BELOW - replace variables]
```

### Agent prompt (copy this exactly, replace {variables})

> **NOTE:** This agent prompt uses `mcp__claude-in-chrome__*` tools which require the
> claude-in-chrome browser extension MCP server. These tools will not be available
> in environments without the browser extension installed.

```text
Extract ALL assets from {URL} with paranoid-level thoroughness. Miss nothing.

OUTPUT DIRECTORIES
- Assets: {PROJECT_DIR}/assets/{site-name}/ (or {PROJECT_DIR}/assets/ if single site)
- Full site: {PROJECT_DIR}/full-sites/{site-name}/ (or {PROJECT_DIR}/full-site/ if single site)

PHASE 1: Browser setup and navigation

1. Call mcp__claude-in-chrome__tabs_context_mcp to get browser context
2. Call mcp__claude-in-chrome__tabs_create_mcp to create new tab
3. Call mcp__claude-in-chrome__navigate with url="{URL}" and the new tabId
4. Call mcp__claude-in-chrome__computer with action="screenshot" to verify page loaded
5. Scroll full page to trigger lazy loading:
   - mcp__claude-in-chrome__computer action="scroll" scroll_direction="down" scroll_amount=10
   - Repeat 3-5 times with 1 second waits

PHASE 2: Asset discovery (JavaScript extraction)

Call mcp__claude-in-chrome__javascript_tool with this code:
```

```javascript
(() => {
  const assets = {
    images: [...document.querySelectorAll('img')].map(img => ({
      src: img.src,
      srcset: img.srcset,
      dataSrc: img.dataset.src,
      alt: img.alt
    })).filter(i => i.src || i.srcset || i.dataSrc),

    videos: [...document.querySelectorAll('video, video source')].map(v => ({
      src: v.src || v.currentSrc,
      poster: v.poster,
      type: v.type
    })).filter(v => v.src),

    svgsInline: [...document.querySelectorAll('svg')].map((svg, i) => ({
      id: svg.id || 'svg-' + i,
      class: svg.className?.baseVal || '',
      html: svg.outerHTML
    })),

    backgrounds: [...document.querySelectorAll('*')].map(el => {
      const bg = getComputedStyle(el).backgroundImage;
      if (bg && bg !== 'none' && bg.includes('url(')) {
        return bg.match(/url\(['"]?([^'"]+)['"]?\)/)?.[1];
      }
      return null;
    }).filter(Boolean),

    favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({
      href: l.href,
      rel: l.rel,
      sizes: l.sizes?.value
    })),

    ogImages: (() => {
      const og = document.querySelector('meta[property="og:image"]');
      const twitter = document.querySelector('meta[name="twitter:image"]');
      return [og?.content, twitter?.content].filter(Boolean);
    })(),

    fonts: (() => {
      const fonts = [];
      for (const sheet of document.styleSheets) {
        try {
          for (const rule of sheet.cssRules) {
            if (rule.type === 5) { // FONT_FACE_RULE
              const src = rule.style.getPropertyValue('src');
              const urls = src.match(/url\(['"]?([^'"]+)['"]?\)/g);
              if (urls) fonts.push(...urls.map(u => u.match(/url\(['"]?([^'"]+)['"]?\)/)?.[1]));
            }
          }
        } catch (e) {}
      }
      return [...new Set(fonts)];
    })()
  };

  return JSON.stringify(assets, null, 2);
})()
```

```text
Store the result as DISCOVERED_ASSETS.

PHASE 3: Content extraction

Call mcp__claude-in-chrome__javascript_tool with this code:
```

```javascript
(() => {
  const content = {
    url: window.location.href,
    title: document.title,
    extractedAt: new Date().toISOString().split('T')[0],
    meta: {
      description: document.querySelector('meta[name="description"]')?.content,
      ogTitle: document.querySelector('meta[property="og:title"]')?.content,
      ogDescription: document.querySelector('meta[property="og:description"]')?.content,
      ogImage: document.querySelector('meta[property="og:image"]')?.content,
      favicon: document.querySelector('link[rel*="icon"]')?.href
    },
    navigation: {
      header: [...document.querySelectorAll('header a, nav a')].slice(0, 20).map(a => ({
        text: a.textContent?.trim(),
        href: a.href
      })),
      footer: [...document.querySelectorAll('footer a')].slice(0, 20).map(a => ({
        text: a.textContent?.trim(),
        href: a.href
      }))
    },
    headings: [...document.querySelectorAll('h1, h2, h3')].slice(0, 30).map(h => ({
      level: h.tagName,
      text: h.textContent?.trim()
    })),
    buttons: [...document.querySelectorAll('button, a.btn, [class*="button"]')].slice(0, 20).map(b => ({
      text: b.textContent?.trim(),
      href: b.href || null
    }))
  };

  return JSON.stringify(content, null, 2);
})()
```

```text
Store the result as PAGE_CONTENT.

PHASE 4: Download assets

For each asset URL discovered, download using curl with error handling.
If curl fails (non-zero exit), log the URL and continue to the next asset.

# Logos (favicon, og:image, header logos)
curl -sfLo "{output_dir}/logos/{site-name}-favicon.ico" "{favicon_url}" || echo "FAIL: {favicon_url}"
curl -sfLo "{output_dir}/logos/{site-name}-og-image.png" "{og_image_url}" || echo "FAIL: {og_image_url}"

# Images
curl -sfLo "{output_dir}/images/{site-name}-{descriptive-name}.{ext}" "{image_url}" || echo "FAIL: {image_url}"

# SVGs - Write inline SVGs to files using Write tool

# Videos
curl -sfLo "{output_dir}/videos/{site-name}-{name}.mp4" "{video_url}" || echo "FAIL: {video_url}"

# Fonts
curl -sfLo "{output_dir}/fonts/{font-name}.woff2" "{font_url}" || echo "FAIL: {font_url}"

NAMING CONVENTION: {site-prefix}-{descriptive-name}.{ext}
- Use alt text or context for descriptive names
- Example: stripe-hero-illustration.svg, vercel-logo-white.svg

PHASE 5: Save JSON files

1. Save page content:
   Use Write tool to save PAGE_CONTENT to:
   {full-site-dir}/pages/homepage.json

2. Save asset URLs catalog:
   Use Write tool to save DISCOVERED_ASSETS to:
   {full-site-dir}/asset-urls.json

PHASE 6: Report results

When complete, report:
- Total assets downloaded (count by type)
- Total size (estimate from curl outputs)
- Any failed downloads (list URLs)
- Output paths

ERROR HANDLING
- If site unreachable: Report error, skip
- If asset download fails: Retry once with 2s delay, then log URL and continue
- If browser tab crashes: Call tabs_create_mcp again, continue
- If rate limited: Add 2 second delays between requests

CONSTRAINTS
- Skip files > 50MB (log URL for manual download)
- Skip duplicate URLs
- Maximum 100 assets per category
- 5 minute timeout for entire extraction
```

---

## Step 4: Monitor agents

After spawning all agents:

1. **Report to user:**
```text
Traktor v2.0 - Extraction started

Folder structure created
Spawned {N} extraction agents:
   - Agent 1: {site1} [running in background]
   - Agent 2: {site2} [running in background]
   ...

Agents working in background. You'll be notified as they complete.
```

2. **As agents complete**, collect their results.

---

## Step 5: Generate final manifest

After ALL agents complete, create manifest file:

**Use Write tool to create `asset-manifest.json`:**

```json
{
  "generated_at": "{current_datetime}",
  "tool": "traktor v2.0",
  "project_dir": "{PROJECT_DIR}",
  "sites_extracted": ["{site1}", "{site2}"],
  "total_assets": "{total_count}",
  "by_type": {
    "logos": "{count}",
    "icons": "{count}",
    "images": "{count}",
    "videos": "{count}",
    "fonts": "{count}",
    "svgs": "{count}"
  },
  "naming_convention": "{site-prefix}-{descriptive-name}.{ext}",
  "output_structure": {
    "assets": "./assets/",
    "full_sites": "./full-sites/"
  }
}
```

---

## Step 6: Final report

**Display to user:**

```text
Traktor extraction complete!

Summary:
   Sites: {N}
   Total assets: {count} ({size_mb} MB)

   By type:
   - Logos: {n}
   - Images: {n}
   - Videos: {n}
   - SVGs: {n}
   - Fonts: {n}

Output:
   - Assets: ./assets/
   - Full sites: ./full-sites/
   - Manifest: ./asset-manifest.json

Failed downloads: {list or "None"}
```

---

## Quick reference

| Step | Action | Tool |
|------|--------|------|
| 1 | Parse URLs | Internal |
| 2 | Create folders | Bash |
| 3 | Spawn agents | Task (background) |
| 4 | Monitor | Wait for notifications |
| 5 | Create manifest | Write |
| 6 | Report | Output to user |

---

## Example execution

**User:** `/traktor https://0g.ai`

**Claude executes:**
1. Parse: `URLS = ["https://0g.ai"]`, `SITE_COUNT = 1`
2. Bash: `mkdir -p assets/{logos,icons,images,videos,fonts,backgrounds} full-site/{pages,assets,styles}`
3. Task: Spawn 1 agent with exact prompt above
4. Report: "Traktor started, 1 agent running..."
5. Wait for agent completion
6. Write: `asset-manifest.json`
7. Report: Final summary

**User:** `/traktor https://stripe.com https://vercel.com https://linear.app`

**Claude executes:**
1. Parse: 3 URLs
2. Bash: Create 3 site folders in assets/ and full-sites/
3. Task: Spawn 3 parallel background agents
4. Report: "Traktor started, 3 agents running..."
5. Collect results as agents finish
6. Write: Combined manifest
7. Report: Combined summary
