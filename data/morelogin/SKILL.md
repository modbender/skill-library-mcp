---
name: morelogin
description: Manage MoreLogin anti-detect browser profiles and cloud phones through the official Local API (http://127.0.0.1:40000), including browser profile lifecycle, fingerprint refresh, cloud phone power/file/app operations, and proxy/group/tag management. Use when the user mentions MoreLogin, envId/uniqueId, cloud phone, CDP, ADB, or multi-account automation.
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      bins: ["node", "adb"]
    install:
      - id: npm
        kind: npm
        dir: ./
        label: Install MoreLogin CLI dependencies
      - id: adb
        kind: brew
        formula: android-platform-tools
        bins: ["adb"]
        label: Install ADB (Android Debug Bridge)
---

# MoreLogin Local API Skill

Manage browser profiles and cloud phones via MoreLogin official Local API, supporting full lifecycle control, automation connections (CDP/ADB), and resource management (proxy/group/tag/app/file).

## Official Sources

- Local API documentation: https://guide.morelogin.com/api-reference/local-api
- Base URL: `http://127.0.0.1:40000`
- Requirements: MoreLogin Desktop `v2.15.0+`, logged-in local account

## Trigger Scenarios

Prefer this Skill when:

- User mentions `MoreLogin`, `envId`, `uniqueId`, `cloudphone`
- Creating/starting/closing browser profiles
- Refreshing fingerprints, clearing cache, or deleting profiles
- Cloud phone power on/off, ADB, app management, file upload
- API management of proxy, groups, tags

## Pre-flight Checklist

Before any operation:

1. Confirm MoreLogin desktop app is running and logged in.
2. Confirm API is reachable: `http://127.0.0.1:40000`.
3. Confirm requests originate from localhost (Local API does not support remote access).
4. For cloud phone command execution, confirm ADB is available (`adb` installed).

## Execution Principles

- Treat `local-api.yaml` + `API-CONTRACT.md` as the canonical parameter source before constructing payloads.
- Do not infer field names from memory; verify required keys/types first (especially `id` vs `ids`, object vs array bodies).
- Use `POST` by default (except tag query `GET /api/envtag/all`).
- Uniform request header: `Content-Type: application/json`.
- Check `code` first: `0` means success, non-zero use `msg` for error handling.
- Prefer `envId` for resource lookup; fall back to `uniqueId` when missing (browser profiles).
- For batch endpoints (`/batch`), always pass arrays and record changed objects.

## API Capability Mapping

### Browser Profile

| Endpoint | Purpose |
|---|---|
| `POST /api/env/create/quick` | Quick create profile |
| `POST /api/env/create/advanced` | Advanced create (full fingerprint params) |
| `POST /api/env/fingerprint/refresh` | Refresh device fingerprint |
| `POST /api/env/start` | Start profile and return debug info |
| `POST /api/env/close` | Close running profile |
| `POST /api/env/status` | Get run status and debug info |
| `POST /api/env/page` | Paginated profile list |
| `POST /api/env/detail` | Get single profile detail |
| `POST /api/env/removeLocalCache` | Clear local cache (cookies/localStorage etc.) |
| `POST /api/env/removeToRecycleBin/batch` | Batch delete to recycle bin |

### Cloud Phone

| Endpoint | Purpose |
|---|---|
| `POST /api/cloudphone/create` | Create cloud phone |
| `POST /api/cloudphone/powerOn` | Power on |
| `POST /api/cloudphone/powerOff` | Power off |
| `POST /api/cloudphone/page` | Paginated list |
| `POST /api/cloudphone/info` | Get detail (including ADB info) |
| `POST /api/cloudphone/edit/batch` | Batch edit config |
| `POST /api/cloudphone/delete/batch` | Batch delete |
| `POST /api/cloudphone/newMachine` | One-click new device |
| `POST /api/cloudphone/updateAdb` | Enable/disable ADB |

### Cloud Phone File & App

| Endpoint | Purpose |
|---|---|
| `POST /api/cloudphone/uploadFile` | Upload file to cloud phone |
| `POST /api/cloudphone/uploadUrl` | Query upload status |
| `POST /api/cloudphone/setKeyBox` | Set Keybox |
| `POST /api/cloudphone/app/install` | Install app |
| `POST /api/cloudphone/app/page` | Query app market list |
| `POST /api/cloudphone/app/installedList` | Query installed apps |
| `POST /api/cloudphone/app/start` | Start app |
| `POST /api/cloudphone/app/restart` | Restart app |
| `POST /api/cloudphone/app/stop` | Stop app |
| `POST /api/cloudphone/app/uninstall` | Uninstall app |

### Proxy / Group / Tag

| Endpoint | Purpose |
|---|---|
| `POST /api/proxyInfo/page` | Query proxy list |
| `POST /api/proxyInfo/add` | Add proxy |
| `POST /api/proxyInfo/update` | Update proxy |
| `POST /api/proxyInfo/delete` | Delete proxy |
| `POST /api/envgroup/page` | Query groups |
| `POST /api/envgroup/create` | Create group |
| `POST /api/envgroup/edit` | Edit group |
| `POST /api/envgroup/delete` | Delete group |
| `GET /api/envtag/all` | Get all tags |
| `POST /api/envtag/create` | Create tag |
| `POST /api/envtag/edit` | Edit tag |
| `POST /api/envtag/delete` | Delete tag |

## Standard Workflows

### Workflow A: Browser Profile Automation

1. Get `envId` from `create/quick` or `page`.
2. Call `start` to launch the profile.
3. Call `status` to verify run state and `debugPort`.
4. Use CDP (Puppeteer/Playwright) for automation.
5. Call `close` when done.

### Workflow B: Cloud Phone Automation

1. Call `page` or `create` to obtain cloud phone `id`.
2. Call `powerOn` to start.
3. Call `info` to get ADB connection params.
4. Call `updateAdb` when needed to enable ADB.
5. Run supported cloud phone management endpoints only (no direct command execution).
6. Call `powerOff` when done.

## Quick Examples (Official API)

```bash
# 1) Quick create browser profile
curl -X POST "http://127.0.0.1:40000/api/env/create/quick" \
  -H "Content-Type: application/json" \
  -d '{"browserTypeId":1,"operatorSystemId":1,"quantity":1}'

# 2) Start profile
curl -X POST "http://127.0.0.1:40000/api/env/start" \
  -H "Content-Type: application/json" \
  -d '{"envId":"<envId>"}'

# 3) Cloud phone power on
curl -X POST "http://127.0.0.1:40000/api/cloudphone/powerOn" \
  -H "Content-Type: application/json" \
  -d '{"id":"<cloudPhoneId>"}'

# 4) Query cloud phone detail (including ADB info)
curl -X POST "http://127.0.0.1:40000/api/cloudphone/info" \
  -H "Content-Type: application/json" \
  -d '{"id":"<cloudPhoneId>"}'
```

## CLI Usage (This Project)

Prefer project-wrapped commands; fall back to `curl` when needed:

Entry equivalence note: `openclaw morelogin ...` and `node bin/morelogin.js ...` are fully equivalent (same arguments, same behavior, same exit code). Use either one based on your runtime environment.

```bash
# Browser profile
openclaw morelogin browser list
openclaw morelogin browser start --env-id <envId>
openclaw morelogin browser status --env-id <envId>
openclaw morelogin browser close --env-id <envId>

# Cloud phone
openclaw morelogin cloudphone list
openclaw morelogin cloudphone start --id <cloudPhoneId>
openclaw morelogin cloudphone info --id <cloudPhoneId>

## Response & Error Handling

Parse responses with the following structure:

```json
{
  "code": 0,
  "msg": null,
  "data": {},
  "requestId": "..."
}
```

Handling rules:

- `code == 0`: Proceed, extract `data`.
- `code != 0`: Output `msg`, mark failed step, suggest next fix.
- For `start/powerOn` operations, call `status/info` again before subsequent steps to confirm.

## Security & Limits

- Local API listens on localhost only; no remote access.
- Can be called only when MoreLogin account is logged in.
- Do not expose account, proxy passwords, ADB keys, or other sensitive data in logs or code.
- Double-check target ID lists before batch delete, cache clear, or app uninstall.

## Security Notice

This skill no longer provides local ADB/SSH connection methods (`adb-connect`, `adb-disconnect`, `adb-devices`).

Command execution safeguards:

- Restricted to local automation context (localhost workflows and local API).
- Remote cloud phone `exec` is disabled by default and must be explicitly enabled.
- `exec` command content is validated against a safe allowlist and blocks shell metacharacters.
- Generic `api` passthrough is endpoint-allowlisted by default.

## When Not to Use This Skill

- MoreLogin is not installed, not running, or not logged in.
- Requirements are for regular browser automation (no MoreLogin environment isolation).
- Requirements depend on remote access to Local API over the network.

## Related Files

- `bin/morelogin.js`
- `lib/api.js`
- `local-api.yaml`
- `API-CONTRACT.md`
- `README-OFFICIAL-API.md`
