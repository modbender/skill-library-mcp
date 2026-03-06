# Labradoc CLI (AI Skill Reference)

Purpose: describe the Labradoc CLI in a format suitable for an AI Skill that needs to run auth and API operations.

## Binary

- Command: `labradoc`
- Top-level groups: `auth`, `api`

## Configuration And Precedence

Config is loaded from the current working directory:

1. Base config: `labrador.yaml` (optional)
2. Environment override: `labrador.<env>.yaml` where `<env>` is `ENVIRONMENT` (default `prod`)
3. Environment variables override everything (dots become underscores)

Common config keys and env vars:

- `api_url` -> `API_URL`
- `api_token` -> `API_TOKEN`
- `keycloak.url` -> `KEYCLOAK_URL`
- `keycloak.realm` -> `KEYCLOAK_REALM`
- `log.debug` -> `LOG_DEBUG`
- `ENVIRONMENT` selects the env-specific config file

Auth state files are stored under the OS user config directory in `labradoc/cli`:

- `token.json` (OAuth token)
- `pkce.json` (PKCE state)

Linux example path: `~/.config/labradoc/cli/`.

## Auth Model

API commands require one of:

- API token (preferred): sent as `X-API-Key` via `--api-token` or `api_token` config
- Bearer token: `--token`
- Stored OAuth access token: `--use-auth-token` (requires `labradoc auth login`)

`--api-token` overrides `--token` when both are set.

The `auth` commands implement OAuth PKCE via Keycloak. Defaults:

- Auth URL: `https://auth.labradoc.eu`
- Realm: `labradoc`
- Client ID: `labradoc-openclaw`
- Scope: `openid profile email offline_access`
- API URL default: `https://labradoc.eu`

## Command Reference

### `auth` (OAuth PKCE)

Persistent flags:

- `--auth-url` (default `https://auth.labradoc.eu`)
- `--realm` (default `labradoc`)
- `--client-id` (default `labradoc-openclaw`)
- `--api-url` (default `https://labradoc.eu`)
- `--scope` (default `openid profile email offline_access`)

Commands:

- `labradoc auth login`
  - Starts a local callback listener on `127.0.0.1` and prints an auth URL.
  - Saves the resulting token to `token.json`.
  - Flags: `--timeout` (default `2m`), `--json` (prints JSON to stdout; auth URL goes to stderr).
- `labradoc auth url`
  - Generates a PKCE authorization URL and saves PKCE state to `pkce.json`.
  - Flags: `--redirect-uri` (default `http://127.0.0.1:18080/callback`), `--json`.
- `labradoc auth exchange`
  - Exchanges an auth code for a token and saves it.
  - Required: `--code`.
  - Optional: `--code-verifier`, `--redirect-uri`, `--state` (uses saved `pkce.json` if missing).
  - Flag: `--json`.
- `labradoc auth token`
  - Prints the stored access token. Flag: `--json`.
- `labradoc auth refresh`
  - Refreshes the stored token. Flag: `--json`.
- `labradoc auth status`
  - Validates the stored token against `GET /api/validate`.
- `labradoc auth logout`
  - Deletes `token.json`.

### `api` (Labradoc API)

Persistent flags:

- `--api-url` (default `https://labradoc.eu`)
- `--api-token` (API key; `X-API-Key`)
- `--token` (Bearer token, ignored if `--api-token` is set)
- `--use-auth-token` (use stored OAuth token)
- `--timeout` (default `30s`)

Commands:

- `labradoc api request [path]`
  - Makes a raw API request.
  - Flags: `--method`, `--body`, `--body-file` (`-` for stdin), `--content-type`, `--accept`, `--out`, `--no-auth`.
  - If body is provided and method is not GET, Content-Type defaults to `application/json`.
  - Requires auth unless `--no-auth` is set.

- `labradoc api tasks list`
  - GET `/api/tasks`.

- `labradoc api tasks close`
  - Close tasks by ID.
  - Flags: `--id` (single), `--ids` (repeatable), `--out`.
  - If `--id` is set: POST `/api/tasks/<id>/close`.
  - Else: POST `/api/tasks/close` with `{"id":[...]}`.

- `labradoc api files list`
  - GET `/api/user/files` with optional query params.
  - Flags: `--status` (repeatable), `--page-size`, `--page-number`.
  - Valid `--status` values: `New`, `multipart`, `googleDocument`, `Check_Duplicate`, `detectFileType`, `htmlToPdf`, `preview`, `ocr`, `process_image`, `embedding`, `name_predictor`, `document_type`, `extraction`, `task`, `completed`, `ignored`, `error`, `not_supported`, `on_hold`, `duplicated`.

- `labradoc api files upload`
  - PUT `/api/user/files` with multipart form.
  - Flag: `--file`.

- `labradoc api files get`
  - GET `/api/user/files/<id>`.
  - Flag: `--id`.

- `labradoc api files content`
  - GET `/api/user/files/<id>/content`.
  - Flags: `--id`, `--out`.

- `labradoc api files ocr`
  - GET `/api/user/files/<id>/ocr`.
  - Flags: `--id`, `--out`.

- `labradoc api files download`
  - GET `/api/user/files/<id>/download`.
  - Flags: `--id`, `--out` (default output is `<id>.pdf`).

- `labradoc api files question`
  - POST `/api/user/files/<id>/question` with `application/json` body.
  - Flags: `--id`, `--question` (sets JSON field `question`), `--body`, `--body-file` (`-` for stdin), `--out`.

- `labradoc api files search`
  - POST `/api/user/files` with `application/json` body (SSE streaming response).
  - Flags: `--question` (sets JSON field `question`), `--body`, `--body-file` (`-` for stdin), `--out`.

- `labradoc api files fields`
  - GET `/api/user/files/<id>/fields`.
  - Flags: `--id`, `--out`.

- `labradoc api files related`
  - GET `/api/user/files/<id>/related`.
  - Flags: `--id`, `--out`.

- `labradoc api files reprocess`
  - GET `/api/user/files/<id>/reprocess`.
  - Flags: `--id`, `--out`.

- `labradoc api files tasks`
  - GET `/api/user/files/<id>/tasks`.
  - Flags: `--id`, `--out`.

- `labradoc api files image`
  - GET `/api/user/files/<id>/image/<pageNumber>`.
  - Flags: `--id`, `--page`, `--out`.

- `labradoc api files preview`
  - GET `/api/user/files/<id>/image/preview/<pageNumber>`.
  - Flags: `--id`, `--page`, `--out`.

- `labradoc api files archive`
  - POST `/api/user/files/archive` with JSON body.
  - Flags: `--id` (single), `--ids` (repeatable), `--out`.

- `labradoc api apikeys list`
  - GET `/api/user/apikeys`.

- `labradoc api apikeys create`
  - POST `/api/user/apikeys` with JSON body.
  - Flags: `--name` (required), `--expires-at` (RFC 3339).

- `labradoc api apikeys revoke`
  - DELETE `/api/user/apikeys/<keyId>`.
  - Flags: `--id`.

- `labradoc api user credits`
  - GET `/api/user/ai/credits`.

- `labradoc api user stats`
  - GET `/api/user/stats`.

- `labradoc api user language get`
  - GET `/api/user/preference/language`.

- `labradoc api user language set`
  - POST `/api/user/preference/language` with JSON body.
  - Flags: `--language`.

- `labradoc api email addresses`
  - GET `/api/emailAddresses`.

- `labradoc api email request`
  - POST `/api/emailAddress` with JSON body.
  - Flags: `--description`.

- `labradoc api email list`
  - GET `/api/emails`.

- `labradoc api email body`
  - GET `/api/email/<id>/<index>`.
  - Flags: `--id`, `--index`, `--out`.

- `labradoc api google drive status`
  - GET `/api/google/drive`.

- `labradoc api google drive token`
  - GET `/api/google/drive/token?scope=...`.
  - Flags: `--scope`.

- `labradoc api google drive code`
  - GET `/api/google/drive/code?code=...`.
  - Flags: `--code`.

- `labradoc api google drive refresh`
  - GET `/api/google/drive/refresh`.

- `labradoc api google drive revoke`
  - DELETE `/api/google/drive/token`.

- `labradoc api google gmail status`
  - GET `/api/google/gmail`.

- `labradoc api google gmail token`
  - GET `/api/google/gmail/token`.

- `labradoc api google gmail code`
  - GET `/api/google/gmail/code?code=...`.
  - Flags: `--code`.

- `labradoc api google gmail revoke`
  - GET `/api/google/gmail/revoke`.

- `labradoc api microsoft outlook token`
  - GET `/api/microsoft/outlook/token`.

- `labradoc api microsoft outlook code`
  - GET `/api/microsoft/outlook/code?code=...`.
  - Flags: `--code`.

- `labradoc api stripe checkout`
  - POST `/api/stripe/checkout`.

- `labradoc api stripe pages-checkout`
  - POST `/api/stripe/pages/checkout`.

- `labradoc api stripe webhook`
  - POST `/api/stripe/webhook`.
  - Flags: `--body`, `--body-file` (`-` for stdin).

## Examples

API token usage:

```bash
labradoc api tasks list --api-token "$API_TOKEN"
```

OAuth flow (local callback):

```bash
labradoc auth login --api-url https://labradoc.eu
labradoc api files list --use-auth-token
```

Manual PKCE flow:

```bash
labradoc auth url --redirect-uri http://127.0.0.1:18080/callback
labradoc auth exchange --code <authorization-code>
```

Raw request with JSON body:

```bash
labradoc api request /api/tasks --method POST --body '{"name":"Example"}'
```

Ask a question from stdin:

```bash
printf '{"question":"What is the due date?"}' | labradoc api files question --id <file-id> --body-file -
```
