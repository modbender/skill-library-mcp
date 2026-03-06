# @elvatis_com/openclaw-rss-feeds

OpenClaw plugin for RSS and Atom security digests with optional NVD CVE enrichment, Ghost CMS draft publishing, and channel notifications.

## Quick Start

```bash
npm install @elvatis_com/openclaw-rss-feeds
```

Minimal config - add to your OpenClaw plugin config:

```json
{
  "plugins": {
    "openclaw-rss-feeds": {
      "feeds": [
        {
          "id": "cert-bund",
          "name": "BSI CERT-Bund",
          "url": "https://wid.cert-bund.de/portal/wid/securityadvisory?rss",
          "keywords": ["critical", "cve"]
        }
      ]
    }
  }
}
```

See [`examples/minimal-config.json`](examples/minimal-config.json) for the minimal setup and [`examples/full-config.json`](examples/full-config.json) for all options.

## Configuration

The plugin schema is defined in `openclaw.plugin.json`.

Full example with all supported options:

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
      "nvdApiKey": "<nvd-api-key-optional>",
      "retry": {
        "maxRetries": 3,
        "initialDelayMs": 1000,
        "backoffMultiplier": 2
      }
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

## Retry / Backoff

Feed fetches use exponential backoff by default. If a feed request fails (network error, timeout, etc.), the plugin retries with increasing delays before giving up.

Default behavior (no config needed):

| Setting | Default | Description |
|---|---|---|
| `maxRetries` | 3 | Maximum retry attempts per feed |
| `initialDelayMs` | 1000 | Delay before the first retry (ms) |
| `backoffMultiplier` | 2 | Multiplier applied to the delay after each retry |

With the defaults, the retry delays are: 1s, 2s, 4s (then fail). Set `maxRetries` to 0 to disable retries entirely.

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

## Community Catalog

This plugin is listed in the [OpenClaw Community Catalog](https://github.com/openclaw/community-catalog). The catalog entry is defined in [`catalog.yaml`](catalog.yaml).

To register via the CLI:

```bash
openclaw catalog submit --from ./catalog.yaml
```

## Development

```bash
npm install
npx tsc --noEmit
npm test
npm run build
```

## License

MIT
