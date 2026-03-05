---
name: terabox-link-extractor
description: "Direct link extraction from TeraBox URLs using the XAPIverse protocol. Extracts high-speed download and stream links (All Resolutions) without browser session requirements. Use when the user provides a TeraBox link and wants to download or stream content directly."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"], "env": ["TERABOX_API_KEY"], "config": [] },
        "primaryEnv": "TERABOX_API_KEY"
      }
  }
---

# TeraBox Link Extractor (XAPIverse Edition)

High-performance extraction of direct assets from TeraBox using the browser-less XAPIverse API.

## 📖 Navigation & Data
- **Primary Interaction**: Use the adaptive logic in `handler.js`. See [api-reference.md](references/api-reference.md) for command specs and [changelog.md](references/changelog.md) for version history.
- **Secondary Interaction**: Use CLI via `node scripts/extract.js <url>`.

## 🛠 AI Protocol (Security First)

### 1. Informed Consent Protocol
- **Trigger**: When a user provides a TeraBox link (`terabox.com`, etc.), inform them that you can extract direct links using the XAPIverse service.
- **Permission**: You MUST ask for the user's permission before sending the URL to the extraction service.
- **Execution**: Only trigger the `extract` command AFTER the user confirms.

### 2. Mandatory Response Format
Once permitted, present the extraction results as a text-only report. **DO NOT use interactive buttons.**

**Format per file:**
📦 **Name**: [name]
📁 **Type**: [type] | 📺 **Quality**: [quality]
📏 **Size**: [size_formatted] | ⏱️ **Duration**: [duration]
🔗 **Links**:
 - [▶️ Slow Stream](stream_url)
 - [▶️ Fast {res} Stream](link) *(List all available resolutions)*
 - [⬇️ Fast Download](fast_download_link)
 - [⬇️ Slow Download](download_link)

💳 **Credits Remaining**: [free_credits_remaining]

### 3. Privacy & Security
- **Data Transmission**: Inform the user (if asked) that the full target URL and your API key (TERABOX_API_KEY) are transmitted to `https://xapiverse.com` for processing.
- **No Residual State**: Do not log or store the API key or extracted links beyond the immediate session.

## Setup

### 1. Obtain Credentials
Get your API key from the XAPIverse portal: [https://xapiverse.com/apis/terabox-pro](https://xapiverse.com/apis/terabox-pro)

### 2. Configure Agent
Add the `TERABOX_API_KEY` to the skill's entry in `openclaw.json`:
```json
"terabox-link-extractor": {
  "TERABOX_API_KEY": "sk_..."
}
```

---
Developed for the OpenClaw community by [Abdul Karim Mia](https://github.com/abdul-karim-mia).
