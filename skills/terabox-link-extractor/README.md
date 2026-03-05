# TeraBox Link Extractor (XAPIverse Edition)

High-performance extraction of direct assets from TeraBox using the browser-less XAPIverse API.

## Features

- **Direct Extraction:** Bypasses browser requirements to fetch direct download and stream links.
- **High-Speed Streams:** Retrieves 360p and 480p fast streaming URLs.
- **Node.js Native:** Built for speed and seamless integration with OpenClaw.
- **Secure Auth:** Uses standard API key injection.

## Installation

1. Copy this folder into your OpenClaw `skills/` directory.
2. Add your XAPIverse API Key to your `openclaw.json` configuration:

```json
"skills": {
  "entries": {
    "terabox-link-extractor": {
      "apiKey": "your_xapiverse_key_here"
    }
  }
}
```

## Usage

Provide any valid TeraBox URL to your agent.

- **Command:** Automatically triggered by the agent or manually via `node scripts/extract.js <url>`.

---\n*Created by Abdul Karim Mia with Jarvis for OpenClaw.*
