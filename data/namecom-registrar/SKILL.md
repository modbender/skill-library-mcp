---
name: namecom-registrar
description: Domain registrar and DNS manager using the Name.com CORE API. Use when the user asks to search for, buy, or register domains, manage DNS records (A, AAAA, CNAME, MX, TXT), solve ACME DNS-01 challenges for TLS certificates, or update dynamic DNS for residential/home-lab setups.
metadata: {"openclaw": {"requires": {"bins": ["node", "npm"], "env": ["NAMECOM_USERNAME", "NAMECOM_TOKEN"], "envOptional": ["NAMECOM_USERNAME_TEST", "NAMECOM_TOKEN_TEST"]}, "primaryEnv": "NAMECOM_TOKEN", "homepage": "https://github.com/patramsey/namecom-clawbot", "install": [{"id": "node", "kind": "node", "package": "namecom-clawbot", "bins": ["namecom-clawbot"], "label": "Install namecom-clawbot MCP server (npm)"}]}}
---

# Name.com Domain Registrar & DNS Manager

MCP server providing nine tools for domain registration and DNS management against the **Name.com CORE API (v1)**.

## Environment Variables

Set credentials before starting the server:

| Variable | Required | Description |
|---|---|---|
| `NAMECOM_USERNAME` | Yes | Name.com account username |
| `NAMECOM_TOKEN` | Yes | Name.com API token |
| `NAMECOM_USERNAME_TEST` | Optional | Sandbox username (no real charges) |
| `NAMECOM_TOKEN_TEST` | Optional | Sandbox API token |

Generate tokens at **Account > Security > API Access**. For sandbox testing, create sandbox credentials there and set only `NAMECOM_USERNAME_TEST` and `NAMECOM_TOKEN_TEST` (leave production vars unset); the server then targets the sandbox API.

## Security & trust

- **Token scope:** Authenticates via standard Name.com API token. Name.com does not currently offer per-operation token scopes; the recommended hardening is **IP whitelisting** (Account > Security > API Access) to restrict the token to your deployment environment. Use sandbox credentials during initial setup.
- **Purchases:** `register_domain` enforces a **code-level human-in-the-loop gate** — it is not possible to complete a purchase without first calling `dryRun: true`. The dry-run response includes a one-time `purchaseToken` (6-digit code, valid 10 minutes, single-use, bound to the specific domain). The actual purchase call requires passing that token back; without it the tool returns an error. This is not just a documented guideline — the token gate is enforced in code. For production, **fund the account with Name.com account credit** instead of attaching a credit card when possible — that limits exposure if credentials are ever compromised. Otherwise use a payment method with spending limits or alerts.
- **Install & supply chain:** This skill installs the npm package `namecom-clawbot`. The package is published with **signed npm provenance** (GitHub Actions), so you can verify on the [npm package page](https://www.npmjs.com/package/namecom-clawbot) that the build matches the [GitHub repo](https://github.com/patramsey/namecom-clawbot). Review the repo and package before installing. To limit risk, run the MCP server in an isolated environment (e.g. container or VM) and use sandbox credentials first.

## Running the Server

```bash
# Install & build
npm install && npm run build

# Run (stdio transport — used by MCP hosts like Cursor)
node dist/src/index.js
```

Or add to your MCP host config:

```json
{
  "mcpServers": {
    "namecom-registrar": {
      "command": "node",
      "args": ["dist/src/index.js"],
      "env": {
        "NAMECOM_USERNAME": "<your-username>",
        "NAMECOM_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

## Tools

### `check_domain`

Check availability and pricing for up to 50 specific domain names at once. Returns purchase price (USD), renewal price, and premium status.

**Always call this before `register_domain`** to confirm availability and get pricing for premium domains.

### `search_domain`

Keyword-based domain search. Provide a keyword and optionally filter by TLDs to get suggested available domain names with pricing. Use this when the user wants to brainstorm names rather than check a specific one.

### `register_domain`

Provisions and registers a domain via the account’s payment settings. Automatically enables WHOIS privacy and registrar lock.

**Required confirmation flow (enforced in code):**

1. Call with **`dryRun: true`** — returns a quote (domain, years, estimated cost) plus a `purchaseToken`. No charge made.
2. Show the user the quote and get explicit confirmation.
3. Call again with **`dryRun: false`** and pass the `purchaseToken` from step 1.

The `purchaseToken` is a one-time **6-digit numeric code** (e.g. `847291`) valid for 10 minutes and bound to the specific domain name — easy to relay via Telegram, WhatsApp, or read aloud. Passing an incorrect, expired, or already-used token returns an error. You cannot skip to step 3 — there is no way to complete a purchase without a valid token from a prior dry-run.

For premium domains, pass the `purchasePrice` and `purchaseType` values from `check_domain`. For safety, prefer funding the Name.com account with **account credit** rather than a credit card when possible.

### `list_domains`

List all domains in the account with expiration dates, autorenew/lock/privacy status. Use to see what the user already owns.

### `get_domain`

Get detailed info for a single domain — contacts, nameservers, expiration, renewal pricing.

### `set_nameservers`

Replace a domain's nameservers. Use when pointing a domain to Cloudflare, Route 53, Fly.io DNS, etc.

### `manage_dns`

Create, delete, or list DNS records. Supported types: A, AAAA, CNAME, MX, TXT, ANAME, NS, SRV.

- Use `action="list"` to see all records and get record IDs for deletion
- Use `host=""` or `host="@"` for apex records, `host="*"` for wildcard
- MX and SRV records require `priority`

### `solve_dns01_challenge`

End-to-end ACME DNS-01 challenge workflow:

1. Creates `_acme-challenge` TXT record with the challenge digest
2. Polls Google DNS and Cloudflare DNS every 5s until global propagation (up to 2 min)
3. Cleans up the TXT record on timeout or error

Returns the `recordId` so the caller can delete the record after certificate validation completes.

### `update_ddns`

Dynamic DNS updater for residential/home-lab IPs:

1. Detects the machine's current public IPv4 via ipify
2. Finds the existing A record for the given host
3. Updates it if the IP changed, creates it if none exists, or skips if already correct

## Example Workflows

**Find and buy a cheap .dev domain, set up a wildcard A record:**

1. `search_domain` with `keyword="coolproject"`, `tldFilter=["dev", "app"]`
2. Pick the cheapest purchasable result
3. `register_domain` with the chosen name
4. `manage_dns` → `action="create"`, `host="*"`, `type="A"`, `answer="<ip>"`

**See what domains you already own and check one's details:**

1. `list_domains` to get the full inventory
2. `get_domain` with a specific domain to see contacts, nameservers, expiration

**Update DDNS after IP change:**

1. `update_ddns` with `domainName="example.com"`, `host="home"`
2. Tool auto-detects the new public IP and patches the A record

**Solve an ACME DNS-01 challenge for Let's Encrypt:**

1. `solve_dns01_challenge` with `domainName="example.com"`, `challengeValue="<digest>"`
2. Wait for the tool to confirm propagation
3. Complete ACME validation with the CA
4. `manage_dns` → `action="delete"`, `recordId=<id from step 1>` to clean up
