# MoreLogin Local API Contract (CLI-aligned)

Source of truth: `local-api.yaml` in this repository.

This contract focuses on endpoints currently wrapped by `bin/morelogin.js`.

## 1) Common response contract

- Success: `code === 0`
- Failure: `code !== 0` and `msg` contains server-side reason
- Most wrapped commands use strict fail-fast behavior on non-zero code

## 2) Browser Profile

### `POST /api/env/start`
- Body:
  - `envId` (string) **or** `uniqueId` (integer), at least one
  - Optional: `encryptKey`, `isHeadless`, `cdpEvasion`

### `POST /api/env/close`
- Body:
  - `envId` (string) **or** `uniqueId` (integer), at least one

### `POST /api/env/status`
- Body:
  - `envId` (string) required by spec

### `POST /api/env/detail`
- Body:
  - `envId` (string) required

### `POST /api/env/page`
- Body (recommended):
  - `envName` (string)
  - `pageNo` (integer, >=1)
  - `pageSize` (integer, 1..100)

### `POST /api/env/create/quick`
- Body:
  - `browserTypeId` (integer)
  - `operatorSystemId` (integer)
  - `quantity` (integer, 1..50)
  - Optional: `groupId`, `proxy`, `isEncrypt`, `browserCore`

### `POST /api/env/fingerprint/refresh`
- Body:
  - `envId` (string) **or** `uniqueId` (string/integer), one required
  - Optional: `uaVersion`, `browserTypeId`, `operatorSystemId`, `advancedSetting`

### `POST /api/env/removeLocalCache`
- Body:
  - `envId` or `uniqueId` (one required)
  - Cache switches: `localStorage`, `indexedDB`, `cookie`, `extension`, `extensionFile`
- Runtime best practice:
  - Require at least one cache switch set to `true`

### `POST /api/env/cache/cleanCloud`
- Body:
  - `envId` or `uniqueId` (one required)
  - `cookie` (boolean), `others` (boolean)
- Runtime best practice:
  - Require at least one of `cookie`/`others`

### `POST /api/env/removeToRecycleBin/batch`
- Body:
  - `envIds` (array<string>) required
  - Optional: `removeEnvData` (boolean)

## 3) CloudPhone

### `POST /api/cloudphone/page`
- Body:
  - `pageNo` (integer)
  - `pageSize` (integer)
  - Optional: `keyword`, `bindIp`, `sort`

### `POST /api/cloudphone/create`
- Body:
  - `skuId` (string) required
  - `quantity` (integer) required
  - Optional: `altitude`, `proxyId`, `envRemark`, geo/language/location fields, `tags`

### `POST /api/cloudphone/powerOn`
- Body:
  - `id` (int64) required
  - Optional: `headless`, `disableMoneySavingMode`

### `POST /api/cloudphone/powerOff`
- Body:
  - `id` (int64) required

### `POST /api/cloudphone/info`
- Body:
  - `id` (int64) required

### `POST /api/cloudphone/exeCommand`
- Body:
  - `id` (int64) required
  - `command` (string) required

### `POST /api/cloudphone/updateAdb`
- Body:
  - `ids` (array<int64>) required
  - `enableAdb` (boolean) required

### `POST /api/cloudphone/newMachine`
- Body:
  - `id` recommended
  - Optional: `brand`, `modelId`

### App endpoints
- `POST /api/cloudphone/app/installedList` -> `{ id }`
- `POST /api/cloudphone/app/start` -> `{ id, packageName }`
- `POST /api/cloudphone/app/stop` -> `{ id, packageName }`
- `POST /api/cloudphone/app/restart` -> `{ id, packageName }`
- `POST /api/cloudphone/app/uninstall` -> `{ id, packageName }`

### Batch edit (currently via `api` passthrough mode)
- `POST /api/cloudphone/edit/batch`
- Body:
  - `id` (array<int64>) required
  - Optional: `envRemark`, `proxyId`, geo/language/location fields, `tags`, `groupId`

## 4) Proxy

### `POST /api/proxyInfo/page`
- Body:
  - `pageNo`, `pageSize`
  - Optional filters: `proxyIp`, `proxyName`, `proxyProviders`, `proxyTypes`, etc.

### `POST /api/proxyInfo/add`
- Body required by spec:
  - `proxyIp`, `proxyPort`, `proxyProvider`
  - Optional: `proxyType`, auth fields, monitor fields, geo fields

### `POST /api/proxyInfo/update`
- Body required by spec:
  - `id`, `proxyIp`, `proxyPort`, `proxyProvider`
  - Optional fields same as add

### `POST /api/proxyInfo/delete`
- Body:
  - root array of proxy IDs (int64)

## 5) Group

### `POST /api/envgroup/page`
- Example body:
  - `groupName`, `pageNo`, `pageSize`

### `POST /api/envgroup/create`
- Example body:
  - `groupName`

### `POST /api/envgroup/edit`
- Body:
  - `id` required
  - `groupName` required

### `POST /api/envgroup/delete`
- Example body:
  - `ids` (array)
  - Optional: `isDeleteAllEnv`

## 6) Tag

### `GET /api/envtag/all`
- No request body

### `POST /api/envtag/create`
- Example body:
  - `tagName`

### `POST /api/envtag/edit`
- Example body:
  - `id`, `tagName`

### `POST /api/envtag/delete`
- Example body:
  - `ids` (array)

## 7) CLI mapping notes (important)

- CLI uses `--page` / `--page-size`, internally mapped to API `pageNo` / `pageSize`.
- Browser list `--name` maps to API `envName`.
- Group create/edit `--name` maps to `groupName`.
- Tag create/edit `--name` maps to `tagName`.
- CloudPhone ADB update uses API-correct payload `{ ids: [...], enableAdb: <bool> }`.

## 8) Execution guardrails for AI

- Never infer payload key names from natural language docs alone; follow this contract.
- For async start/power operations, verify with `status`/`info` before next step.
- Prefer `--payload` mode for complex writes to avoid accidental field loss.
