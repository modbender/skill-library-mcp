---
name: aperture
description: Install and run Aperture, the L402 Lightning reverse proxy from Lightning Labs. Use when creating L402 paywalls, configuring paid API endpoints, hosting paid content for other agents, or testing L402 authentication flows.
---

# Aperture - L402 Lightning Reverse Proxy

Aperture is a reverse proxy that implements the L402 protocol, enabling
payment-gated API access via the Lightning Network. It sits in front of your
backend services and requires Lightning micropayments before granting access.

**Source:** `github.com/lightninglabs/aperture`

## Quick Start

```bash
# 1. Install aperture
skills/aperture/scripts/install.sh

# 2. Generate config (connects to local lnd)
skills/aperture/scripts/setup.sh

# 3. Ensure invoice.macaroon exists (required for L402 invoice creation)
#    If not present, bake one with the macaroon-bakery skill:
skills/macaroon-bakery/scripts/bake.sh --role invoice-only \
    --save-to ~/.lnd/data/chain/bitcoin/mainnet/invoice.macaroon

# 4. Start aperture
skills/aperture/scripts/start.sh

# 5. Test with lnget
lnget -k --no-pay https://localhost:8081/api/test
```

## How Aperture Works

1. Client requests a protected resource through Aperture
2. Aperture responds with HTTP 402 + `WWW-Authenticate: L402` header containing
   a macaroon and a Lightning invoice
3. Client pays the invoice and obtains the preimage
4. Client retries with `Authorization: L402 <macaroon>:<preimage>`
5. Aperture validates the token and proxies to the backend service

## Installation

```bash
skills/aperture/scripts/install.sh
```

This will:
- Verify Go is installed
- Run `go install github.com/lightninglabs/aperture/cmd/aperture@latest`
- Verify `aperture` is on `$PATH`

To install manually:

```bash
go install github.com/lightninglabs/aperture/cmd/aperture@latest
```

Or build from source:

```bash
git clone https://github.com/lightninglabs/aperture.git
cd aperture
make install
```

## Setup

```bash
skills/aperture/scripts/setup.sh
```

This generates `~/.aperture/aperture.yaml` from the config template with
sensible defaults. The setup script auto-detects the local lnd node paths.

**Options:**

```bash
# Custom network
setup.sh --network testnet

# Custom lnd paths
setup.sh --lnd-host localhost:10009 \
         --lnd-tls ~/.lnd/tls.cert \
         --lnd-macdir ~/.lnd/data/chain/bitcoin/mainnet

# Custom listen port
setup.sh --port 8081

# Disable TLS (development only)
setup.sh --insecure

# Disable auth (no payments required)
setup.sh --no-auth
```

## Running Aperture

### Start

```bash
skills/aperture/scripts/start.sh
```

Starts aperture as a background process reading `~/.aperture/aperture.yaml`.

**Options:**

```bash
start.sh --foreground         # Run in foreground
start.sh --config /path/to   # Custom config path
```

### Stop

```bash
skills/aperture/scripts/stop.sh
```

## Configuration

Config file: `~/.aperture/aperture.yaml`

### Invoice Macaroon Requirement

Aperture requires `invoice.macaroon` in the configured `macdir` to create
Lightning invoices for L402 challenges. This is **not** the same as
`admin.macaroon`. If the macaroon is missing, aperture will fail to start or
will return errors when clients request paid resources.

To bake an invoice macaroon with the macaroon-bakery skill:

```bash
skills/macaroon-bakery/scripts/bake.sh --role invoice-only \
    --save-to ~/.lnd/data/chain/bitcoin/mainnet/invoice.macaroon
```

The `setup.sh` script will warn you if `invoice.macaroon` is not found at the
expected path.

### Minimal Agent Configuration

This is the minimal config for an agent hosting paid endpoints with a local
lnd node:

```yaml
listenaddr: "localhost:8081"
insecure: true
debuglevel: "info"
dbbackend: "sqlite"
sqlite:
  dbfile: "~/.aperture/aperture.db"

authenticator:
  network: "mainnet"
  lndhost: "localhost:10009"
  tlspath: "~/.lnd/tls.cert"
  macdir: "~/.lnd/data/chain/bitcoin/mainnet"

services:
  - name: "my-api"
    hostregexp: ".*"
    pathregexp: "^/api/.*$"
    address: "127.0.0.1:8080"
    protocol: http
    price: 100
```

### Service Configuration

Each service entry defines a backend to protect:

```yaml
services:
  - name: "service-name"
    # Match requests by host (regex).
    hostregexp: "^api.example.com$"

    # Match requests by path (regex).
    pathregexp: "^/paid/.*$"

    # Backend address to proxy to.
    address: "127.0.0.1:8080"

    # Protocol: http or https.
    protocol: http

    # Static price in satoshis.
    price: 100

    # Macaroon capabilities granted at base tier.
    capabilities: "read,write"

    # Token expiry in seconds (31557600 = 1 year).
    timeout: 31557600

    # Paths exempt from payment.
    authwhitelistpaths:
      - "^/health$"
      - "^/public/.*$"

    # Per-endpoint rate limits (token bucket).
    ratelimits:
      - pathregexp: "^/api/query.*$"
        requests: 10
        per: 1s
        burst: 20
```

### Authentication Backends

#### Direct LND Connection

```yaml
authenticator:
  network: "mainnet"
  lndhost: "localhost:10009"
  tlspath: "~/.lnd/tls.cert"
  macdir: "~/.lnd/data/chain/bitcoin/mainnet"
```

#### Lightning Node Connect (LNC)

```yaml
authenticator:
  network: "mainnet"
  passphrase: "your-pairing-phrase"
  mailboxaddress: "mailbox.terminal.lightning.today:443"
```

#### Disable Authentication

```yaml
authenticator:
  disable: true
```

### Database Backends

**SQLite (recommended for agents):**

```yaml
dbbackend: "sqlite"
sqlite:
  dbfile: "~/.aperture/aperture.db"
```

**PostgreSQL:**

```yaml
dbbackend: "postgres"
postgres:
  host: "localhost"
  port: 5432
  user: "aperture"
  password: "secret"
  dbname: "aperture"
```

### TLS Configuration

```yaml
# Auto Let's Encrypt certificate.
autocert: true
servername: "api.example.com"

# Or disable TLS (development/local only).
insecure: true
```

If neither is set, Aperture generates self-signed certs in `~/.aperture/`.

### Dynamic Pricing

Connect to a gRPC price server instead of static prices:

```yaml
services:
  - name: "my-api"
    dynamicprice:
      enabled: true
      grpcaddress: "127.0.0.1:10010"
      insecure: false
      tlscertpath: "/path/to/pricer/tls.cert"
```

## Hosting Paid Content for Agents

A common pattern is hosting information that other agents pay to access:

```bash
# 1. Start a simple HTTP backend with your content
mkdir -p /tmp/paid-content
echo '{"data": "valuable information"}' > /tmp/paid-content/info.json
cd /tmp/paid-content && python3 -m http.server 8080 &

# 2. Configure aperture to protect it
skills/aperture/scripts/setup.sh --insecure --port 8081

# 3. Start aperture
skills/aperture/scripts/start.sh

# 4. Other agents can now pay and fetch
lnget --max-cost 100 https://localhost:8081/api/info.json
```

## Integration with lnget and lnd

With all three components running:

```bash
# Verify lnd is running
skills/lnd/scripts/lncli.sh getinfo

# Start aperture (uses same lnd for invoice generation)
skills/aperture/scripts/start.sh

# Fetch a paid resource
lnget --max-cost 1000 https://localhost:8081/api/data

# Check tokens
lnget tokens list
```

## File Locations

| Path | Purpose |
|------|---------|
| `~/.aperture/aperture.yaml` | Configuration file |
| `~/.aperture/aperture.db` | SQLite database |
| `~/.aperture/tls.cert` | TLS certificate |
| `~/.aperture/tls.key` | TLS private key |
| `~/.aperture/aperture.log` | Log file |

## Troubleshooting

### Port already in use
Change `listenaddr` in config to a different port, or use `setup.sh --port`.

### LND connection refused
Verify lnd is running and wallet is unlocked. Check `lndhost`, `tlspath`, and
`macdir` in the config point to the correct lnd instance.

### No 402 challenge returned
Check that the request path matches a service's `pathregexp` and is not in
`authwhitelistpaths`. Verify `authenticator.disable` is not `true`.

### Token validation fails
The client must present the exact macaroon from the challenge with the correct
preimage. Verify the preimage matches the payment hash.
