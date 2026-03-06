# Labradoc CLI

Command-line client for Labradoc authentication and API operations (tasks, files, user settings, API keys, email, integrations, and billing).

## Requirements

- Go 1.26+

## Install

Build locally:

```bash
go build -o labradoc .
```

Or install:

```bash
go install ./...
```

## Configuration

The CLI reads configuration from the current working directory using Viper:

- Base config: `labrador.yaml`
- Environment override: `labrador.<env>.yaml` where `<env>` comes from `ENVIRONMENT` (default: `prod`)
- Environment variables override everything (dots become underscores)

Example `labrador.yaml` (only set values you want to override):

```yaml
api_url: https://labradoc.eu
api_token: your-api-key
keycloak:
  url: https://auth.labradoc.eu
  realm: labradoc
log:
  debug: false
```

Common environment variables (override config defaults only when needed):

- `API_URL`
- `API_TOKEN`
- `KEYCLOAK_URL`
- `KEYCLOAK_REALM`
- `LOG_DEBUG`
- `ENVIRONMENT`

Tokens and PKCE state are stored under the user config directory:

- `~/.config/labradoc/cli/token.json`
- `~/.config/labradoc/cli/pkce.json`

## Authentication

**Preferred method:** API Token authentication via https://labradoc.eu/profile

Generate an API token from your Labradoc profile page and set it via `--api-token`, `API_TOKEN` env var, or `api_token` in `labrador.yaml`.

OAuth is available as an alternative if you prefer browser-based authentication:

Default auth settings (only override when required):

- Auth URL: `https://auth.labradoc.eu`
- Realm: `labradoc`
- Client ID: `labradoc-openclaw`
- Scope: `openid profile email offline_access`

Login using a local callback:

```bash
labradoc auth login --api-url https://api.labradoc.eu
```

Generate a PKCE authorization URL (for manual flow):

```bash
labradoc auth url --redirect-uri http://127.0.0.1:18080/callback
```

Exchange a code for a token (uses saved PKCE state if present):

```bash
labradoc auth exchange --code <authorization-code>
```

Other auth commands:

```bash
labradoc auth token
labradoc auth refresh
labradoc auth status --api-url https://labradoc.eu
labradoc auth logout
```

API commands use API tokens by default. API token auth is the preferred method. OAuth is available if you prefer it — use `labradoc auth login` and pass `--use-auth-token` (or provide a bearer token explicitly).

## API Usage

The API commands accept either (defaults apply unless you override them):

- `--api-token` (sent as `X-API-Key`; default from `api_token`), or
- `--token` (Bearer token), or
- `--use-auth-token` to use the stored OAuth token from `labradoc auth login`

Raw request:

```bash
labradoc api request /api/tasks --method GET
labradoc api request /api/tasks --method POST --body '{"name":"Example"}'
```

Tasks:

```bash
labradoc api tasks list
labradoc api tasks close --id <task-id>
labradoc api tasks close --ids <task-id> --ids <task-id>
```

Files:

```bash
labradoc api files list --status New --status completed --page-size 50
labradoc api files upload --file ./document.pdf
labradoc api files get --id <file-id>
labradoc api files content --id <file-id> --out content.txt
labradoc api files ocr --id <file-id>
labradoc api files download --id <file-id> --out original.pdf
labradoc api files fields --id <file-id>
labradoc api files related --id <file-id>
labradoc api files reprocess --id <file-id>
labradoc api files tasks --id <file-id>
labradoc api files image --id <file-id> --page 1 --out page-1.png
labradoc api files preview --id <file-id> --page 1 --out page-1-preview.png
labradoc api files archive --id <file-id>
labradoc api files question --id <file-id> --body '{"question":"What is the due date?"}'
labradoc api files search --body '{"question":"Find all invoices from Acme"}'
```

Valid `--status` values: `New`, `multipart`, `googleDocument`, `Check_Duplicate`, `detectFileType`, `htmlToPdf`, `preview`, `ocr`, `process_image`, `embedding`, `name_predictor`, `document_type`, `extraction`, `task`, `completed`, `ignored`, `error`, `not_supported`, `on_hold`, `duplicated`.

Note: `files search` returns a Server-Sent Events (SSE) stream.

User:

```bash
labradoc api user credits
labradoc api user stats
labradoc api user language get
labradoc api user language set --language en
```

API keys:

```bash
labradoc api apikeys list
labradoc api apikeys create --name "CI token" --expires-at 2026-06-01T00:00:00Z
labradoc api apikeys revoke --id <key-id>
```

Email:

```bash
labradoc api email addresses
labradoc api email request --description "Inbound invoices"
labradoc api email list
labradoc api email body --id <email-id> --index 1 --out body.eml
```

Google integrations:

```bash
labradoc api google drive status
labradoc api google drive token --scope "https://www.googleapis.com/auth/drive.readonly"
labradoc api google drive code --code <oauth-code>
labradoc api google drive refresh
labradoc api google drive revoke
labradoc api google gmail status
labradoc api google gmail token
labradoc api google gmail code --code <oauth-code>
labradoc api google gmail revoke
```

Microsoft integrations:

```bash
labradoc api microsoft outlook token
labradoc api microsoft outlook code --code <oauth-code>
```

Billing:

```bash
labradoc api stripe checkout
labradoc api stripe pages-checkout
```

## Notes

- The binary name is `labradoc` (see `cmd/root.go`).
- `ENVIRONMENT=dev` loads `labrador.dev.yaml` in addition to `labrador.yaml`.
