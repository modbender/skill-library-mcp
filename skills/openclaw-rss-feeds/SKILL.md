---
name: openclaw-rss-feeds
description: "RSS/Atom feed digest with optional CVE enrichment, Ghost CMS drafts, and channel notifications"
---

# @elvatis_com/openclaw-rss-feeds

OpenClaw plugin for RSS and Atom security digests with optional NVD CVE enrichment, Ghost CMS draft publishing, and channel notifications.

## Installation

```bash
npm install @elvatis_com/openclaw-rss-feeds
```

Then enable the plugin in your OpenClaw plugin config.

## Configuration

The plugin schema is defined in `openclaw.plugin.json`.

Example with all supported options:

```json
{
  "plugins": {
    "openclaw-rss-feeds": {
      "feeds": [
        {
          "id": "fortinet",
          "name": "Fortinet PSIRT",
          "url": "https://www.fortiguard.com/rss/ir.xml",
          "keywords": ["fortinet", "fortigate", "fortios"],
          "enrichCve": true,
          "cvssThreshold": 7,
          "tags": ["fortinet", "security", "digest"],
          "docsUrlTemplate": "https://docs.fortinet.com/product/{product}/{version}/release-notes",
          "productHighlightPattern": "Forti(?:Gate|OS|Analyzer|Manager|Client|Proxy)"
        },
        {
          "id": "m365",
          "name": "Microsoft 365 Message Center",
          "url": "https://www.microsoft.com/en-us/microsoft-365/roadmap?filters=&searchterms=&rss=1",
          "keywords": ["security", "vulnerability", "defender"],
          "enrichCve": true,
          "cvssThreshold": 6.5,
          "tags": ["microsoft-365", "security"]
        },
        {
          "id": "bsi",
          "name": "BSI CERT-Bund",
          "url": "https://wid.cert-bund.de/portal/wid/securityadvisory?rss",
          "keywords": ["kritisch", "critical", "cve"],
          "enrichCve": false,
          "tags": ["bsi", "cert-bund"]
        },
        {
          "id": "heise-security",
          "name": "Heise Security",
          "url": "https://www.heise.de/security/rss/news-atom.xml",
          "keywords": ["cve", "security", "ransomware"],
          "enrichCve": false,
          "tags": ["heise", "security-news"]
        }
      ],
      "schedule": "0 9 1 * *",
      "lookbackDays": 31,
      "ghost": {
        "url": "https://blog.example.com",
        "adminKey": "<ghost-admin-key-id>:<ghost-admin-key-secret-hex>"
      },
      "notify": [
        "whatsapp:<phone>",
        "telegram:123456789"
      ],
      "nvdApiKey": "<nvd-api-key-optional>"
    }
  }
}
```

## Usage

### Automatic run via cron schedule

If `schedule` is set, the plugin registers a scheduler and runs automatically.

Example:

- `0 9 1 * *` runs at 09:00 on day 1 of every month
- `0 8 * * 1` runs every Monday at 08:00

### Manual run via tool

You can trigger digest generation manually with the registered tool:

- Tool name: `rss_run_digest`
- Optional parameter: `dryRun: true`

`dryRun` fetches and formats the digest but skips Ghost publishing and notifications.

## CVE Enrichment

If a feed has `enrichCve: true`, the plugin calls the NVD CVE API and enriches the digest with:

- CVE ID
- CVSS score (filtered by `cvssThreshold`)
- CVE description
- Link to NVD details

Notes:

- CVE enrichment is keyword-driven via each feed's `keywords`
- Requests are rate-limited between keyword lookups
- NVD failures are handled as non-fatal, feed processing continues

## Ghost CMS Integration

If `ghost` is configured, the digest is published as a draft post through the Ghost Admin API.

Implementation details:

- HS256 JWT is generated from `adminKey` (`id:secret` format)
- API endpoint: `/ghost/api/admin/posts/?source=html`
- Digest is sent as HTML body
- Tags are merged from all configured feed `tags`

If Ghost fails, digest generation still succeeds and the error is reported in result metadata and optional notifications.

## Notifications

If `notify` contains targets (format `channel:target`), a summary notification is sent after the run.

Example targets:

- `whatsapp:<phone>`
- `telegram:123456789`
- `discord:#security`

## Development

```bash
npm install
npx tsc --noEmit
npm test
npm run build
```

## License

MIT
