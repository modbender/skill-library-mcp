---
name: skill
title: CamoFox MCP for OpenClaw
version: 1.10.0
description: Anti-detection browser automation MCP skill for OpenClaw agents with 41 tools for navigation, interaction, extraction, downloads, profiles, sessions, and stealth web search.
author: redf0x1
tags:
  - mcp
  - openclaw
  - browser-automation
  - anti-detection
  - camofox
  - web-scraping
  - ai-agent
license: MIT
homepage: https://github.com/redf0x1/camofox-mcp#readme
metadata:
  title: CamoFox MCP for OpenClaw
  version: 1.10.0
  author: redf0x1
  tags:
    - mcp
    - openclaw
    - browser-automation
    - anti-detection
    - camofox
    - web-scraping
    - ai-agent
  homepage: https://github.com/redf0x1/camofox-mcp#readme
---

# CamoFox MCP Skill

CamoFox MCP gives OpenClaw agents a production-ready anti-detection browser automation toolkit over MCP HTTP transport. It connects OpenClaw to CamoFox Browser so agents can browse, click, type, extract content, manage cookies/sessions, run stealth search workflows, and download resources without the high block rates common with standard automation stacks.

## Why this skill exists

Most browser automation flows eventually hit CAPTCHAs, fingerprint checks, or bot detection. CamoFox is purpose-built for that reality:

- Anti-detection fingerprinting per tab/session
- Better resilience on sites that aggressively detect automation
- Token-efficient accessibility snapshots for agent reasoning
- Session persistence via cookie/profile tools
- Built-in search macros across 14 engines

## Setup

### 1) Start CamoFox Browser

CamoFox Browser must be running first (default `http://localhost:9377`).

### 2) Start CamoFox MCP in HTTP mode

CAMOFOX_TRANSPORT=http npx camofox-mcp@1.10.0

Optional examples:

CAMOFOX_TRANSPORT=http CAMOFOX_API_KEY=your-key npx camofox-mcp@1.10.0
CAMOFOX_TRANSPORT=http CAMOFOX_HTTP_PORT=8080 npx camofox-mcp@1.10.0

### 3) Configure OpenClaw

Add this MCP server:

{"mcpServers":{"camofox":{"url":"http://localhost:3000/mcp"}}}

Alternative skill-generation flow:

npx @filiksyos/mcptoskill http://localhost:3000/mcp

## Trigger phrases

Use this skill when the user asks for tasks like:

- Browse this site and extract the data
- Automate this login/search/form flow
- Use a stealth or anti-detection browser
- Take a snapshot and click/type through this workflow
- Collect all links/images/PDFs from this page section
- Persist session cookies and restore later
- Run web search in browser and summarize results
- Download files and return metadata/content

## Tool catalog (41 tools)

### Health (1)

- server_status: Check CamoFox server health and browser connection.

### Tabs (3)

- create_tab: Create a new browser tab with anti-detection fingerprinting.
- close_tab: Close a browser tab and release resources.
- list_tabs: List all open browser tabs with URLs and titles.

### Navigation (4)

- navigate: Navigate a tab to a URL.
- go_back: Navigate backward in browser history.
- go_forward: Navigate forward in browser history.
- refresh: Reload the current page.

### Interaction (8)

- click: Click an element by ref or CSS selector.
- type_text: Type text into an input field.
- scroll: Scroll page up or down by pixel amount.
- camofox_scroll_element: Scroll a specific container element.
- camofox_evaluate_js: Execute JavaScript in isolated page context.
- camofox_hover: Hover over an element.
- camofox_wait_for: Wait for page readiness.
- camofox_press_key: Press a keyboard key.

### Observation (4)

- snapshot: Get accessibility tree snapshot (PRIMARY way to read page content).
- screenshot: Take visual screenshot as base64 PNG.
- get_links: Get all hyperlinks on page.
- camofox_wait_for_text: Wait for specific text to appear.

### Downloads (3)

- list_downloads: List downloaded files with optional filtering.
- get_download: Get a downloaded file with optional inline content.
- delete_download: Delete a downloaded file from disk.

### Extraction (3)

- extract_resources: Extract images, links, media, documents from a DOM scope.
- batch_download: Extract and download scoped resources in one call.
- resolve_blobs: Resolve blob URLs to downloadable base64 data.

### Search (1)

- web_search: Search across 14 engines (Google, YouTube, Amazon, Reddit, etc.).

### Session (3)

- import_cookies: Import cookies for authenticated sessions.
- get_stats: Get session usage and performance statistics.
- camofox_close_session: Close all tabs for a user session.

### Batch workflows (6)

- fill_form: Fill multiple form fields in one operation.
- type_and_submit: Type text and press key in one step.
- navigate_and_snapshot: Navigate, wait, and snapshot in a single call.
- scroll_and_snapshot: Scroll then snapshot to reveal below-fold content.
- camofox_scroll_element_and_snapshot: Scroll container element and snapshot.
- batch_click: Click multiple elements sequentially.

### Profiles (4)

- save_profile: Save tab cookies to a named profile.
- load_profile: Load saved profile cookies into a tab.
- list_profiles: List saved profiles and metadata.
- delete_profile: Delete a saved profile.

### Presets (1)

- list_presets: List available geo presets.

## What makes CamoFox unique

- Stealth-first architecture for AI agents that need reliability on hostile sites
- Rich tool surface (41 tools) combining low-level controls + high-level workflows
- Snapshot-first design that reduces token burn while preserving actionable context
- Built-in profile/session controls for long-running authenticated automations
- Native HTTP MCP endpoint for OpenClaw and remote MCP-compatible clients
