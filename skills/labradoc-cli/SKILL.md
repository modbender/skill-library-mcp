---
name: labradoc-cli
description: Use the Labradoc CLI to authenticate and call Labradoc API endpoints (tasks, files, users, API keys, email, Google/Microsoft integrations, billing) from OpenClaw. Trigger when the user wants to perform Labradoc operations, manage documents/tasks, or interact with the Labradoc API via command line.
---

# Labradoc CLI

Labradoc is an AI document intelligence platform that unifies emails, documents, and photos into one searchable system. It provides natural-language search and contextual answers over your own data, supports Gmail and Google Drive integrations, email forwarding, and manual uploads, and emphasizes GDPR-aligned hosting in Germany with strong privacy controls.

Use this skill to operate the `labradoc-cli` CLI with API token authentication. It covers configuration and every available command.

## Install

Get the latest prebuilt binary from the GitHub Releases page, then place it on your PATH:

https://github.com/zamedic/labradoc-cli/releases

## Configuration

The CLI sends the API token as the `X-API-Key` header.

**Preferred authentication method:** API Token from your Labradoc profile at https://labradoc.eu/profile

Set the token using one of the following (highest wins):

```text
--api-token flag
API_TOKEN env var
labrador.yaml (api_token)
```

Optional base URL override:

```text
--api-url flag
API_URL env var
labrador.yaml (api_url)
```

Config file precedence:

```text
labrador.yaml
labrador.<ENVIRONMENT>.yaml
ENV vars (dots become underscores)
```

## Global Flags

```text
--api-url     API base URL (default https://labradoc.eu)
--api-token   API token (X-API-Key)
--timeout     HTTP timeout (default 30s)
```

## Authentication (OAuth)

API token auth is preferred, but OAuth is available:

```bash
# Login via browser
eval labradoc-cli auth login --api-url https://api.labradoc.eu

# Check auth status
labradoc-cli auth status --api-url https://labradoc.eu

# Get current token
labradoc-cli auth token

# Refresh token
labradoc-cli auth refresh

# Logout
labradoc-cli auth logout
```

When using OAuth, pass `--use-auth-token` to API commands instead of `--api-token`.

## Raw Request

```bash
labradoc-cli api request /api/tasks --method GET
labradoc-cli api request /api/tasks --method POST --body '{"name":"Example"}'
labradoc-cli api request /api/tasks --method POST --body-file ./payload.json
```

## Tasks

```bash
labradoc-cli api tasks list
labradoc-cli api tasks close --id <task-id>
labradoc-cli api tasks close --ids <task-id> --ids <task-id>
```

## Files

```bash
labradoc-cli api files list --status New --status completed --page-size 50
labradoc-cli api files upload --file ./document.pdf
labradoc-cli api files get --id <file-id>
labradoc-cli api files content --id <file-id> --out content.txt
labradoc-cli api files ocr --id <file-id> --out ocr.txt
labradoc-cli api files download --id <file-id> --out original.pdf
labradoc-cli api files fields --id <file-id>
labradoc-cli api files related --id <file-id>
labradoc-cli api files reprocess --id <file-id>
labradoc-cli api files tasks --id <file-id>
labradoc-cli api files image --id <file-id> --page 1 --out page-1.png
labradoc-cli api files preview --id <file-id> --page 1 --out page-1-preview.png
labradoc-cli api files archive --id <file-id>
labradoc-cli api files archive --ids <file-id> --ids <file-id>
labradoc-cli api files question --id <file-id> --body '{"question":"What is the due date?"}'
labradoc-cli api files search --body '{"question":"Find all invoices from Acme"}'
```

Valid `--status` values: `New`, `multipart`, `googleDocument`, `Check_Duplicate`, `detectFileType`, `htmlToPdf`, `preview`, `ocr`, `process_image`, `embedding`, `name_predictor`, `document_type`, `extraction`, `task`, `completed`, `ignored`, `error`, `not_supported`, `on_hold`, `duplicated`.

Note: `files search` returns a Server-Sent Events (SSE) stream.

## API Keys

```bash
labradoc-cli api apikeys list
labradoc-cli api apikeys create --name "CI token" --expires-at 2026-06-01T00:00:00Z
labradoc-cli api apikeys revoke --id <key-id>
```

## User

```bash
labradoc-cli api user credits
labradoc-cli api user stats
labradoc-cli api user language get
labradoc-cli api user language set --language en
```

## Email

```bash
labradoc-cli api email addresses
labradoc-cli api email request --description "Inbound invoices"
labradoc-cli api email list
labradoc-cli api email body --id <email-id> --index 1 --out body.eml
```

## Integrations

See [references/integrations.md](references/integrations.md) for Google Drive, Gmail, and Microsoft Outlook commands.

## Billing (Stripe)

```bash
labradoc-cli api stripe checkout
labradoc-cli api stripe pages-checkout
labradoc-cli api stripe webhook --body-file ./stripe-event.json
```

## Wrapper Script

A convenience wrapper is provided at `scripts/run-labradoc.sh`. It checks that the `labradoc-cli` binary is on PATH and forwards all arguments:

```bash
./scripts/run-labradoc.sh api tasks list
```

## Troubleshooting

```text
Missing token: provide --api-token, API_TOKEN, or api_token in labrador.yaml
401/403: confirm API token and --api-url
```
