# Mobilerun Platform API

Base URL: `https://api.mobilerun.ai/v1`
Auth: `Authorization: Bearer dr_sk_...`

This document covers platform-level APIs: device provisioning, AI agent tasks, webhooks, and the app library.
For direct phone control (tap, swipe, screenshot, etc.), see [phone-api.md](./phone-api.md).

---

## Device Management

### List Devices

```
GET /devices
```

Query params:
- `state` -- filter by state (array, e.g. `state=ready&state=assigned`)
  - Values: `creating`, `assigned`, `ready`, `disconnected`, `terminated`, `unknown`
- `provider` -- `personal`, `limrun`, `remote`, `roidrun`
- `type` -- `device_slot`, `dedicated_emulated_device`, `dedicated_physical_device`
- `page` (default: 1), `pageSize` (default: 20)
- `orderBy` -- `id`, `createdAt`, `updatedAt`, `assignedAt` (default: `createdAt`)
- `orderByDirection` -- `asc`, `desc` (default: `desc`)

Response: `{ items: DeviceInfo[], pagination: Meta }`

### Get Device Info

```
GET /devices/{deviceId}
```

Returns a `DeviceInfo` object:
```json
{
  "id": "uuid",
  "name": "string",
  "state": "ready",
  "stateMessage": "device ready",
  "streamUrl": "wss://...",
  "streamToken": "string",
  "deviceType": "device_slot",
  "provider": "limrun",
  "apps": ["com.example.app"],
  "files": [],
  "country": "US",
  "createdAt": "ISO datetime",
  "updatedAt": "ISO datetime",
  "assignedAt": "ISO datetime | null",
  "terminatesAt": "ISO datetime | null",
  "taskCount": 0
}
```

### Get Device Count

```
GET /devices/count
```

Returns a map of device states to counts.

### Provision a Cloud Device

Cloud devices require an active subscription. If the user's plan doesn't support it,
the API will return `403` with `"detail": "device_slot limit reached"` -- inform the user they need to terminate an existing device or upgrade at https://cloud.mobilerun.ai/billing.
See [subscription.md](./subscription.md) for plan details.

```
POST /devices
Content-Type: application/json

{
  "name": "my-device",
  "apps": ["com.example.app"],
  "files": [],
  "country": "US"
}
```

Query params:
- `provider` -- `limrun`, `physical`, `premium`, `roidrun`
- `deviceType` -- `device_slot`, `dedicated_emulated_device`, `dedicated_physical_device`, `dedicated_premium_device`

After provisioning, wait for it to become ready:

```
GET /devices/{deviceId}/wait
```

This blocks until the device state transitions to `ready`.

### Terminate a Cloud Device

```
DELETE /devices/{deviceId}
Content-Type: application/json

{}
```

Optional body fields:
- `terminateAt` -- ISO datetime for scheduled termination
- `previousDeviceId` -- for device replacement workflows

> Personal devices cannot be terminated via the API. They disconnect when the Portal app is closed.

### List Tasks for a Device

```
GET /devices/{deviceId}/tasks
```

Query params: `page`, `pageSize`, `orderBy`, `orderByDirection`

---

## Tasks (AI Agent)

Instead of controlling a phone step-by-step, you can submit a natural language goal
and let Mobilerun's AI agent execute it autonomously on the device.

Tasks require a paid subscription with credits.
If the user doesn't have an active plan, the API will return an error --
let the user know they need a subscription at https://cloud.mobilerun.ai/billing.
See [subscription.md](./subscription.md) for plan and credit details.

### Run a Task

```
POST /tasks
Content-Type: application/json

{
  "task": "Open Chrome and search for weather",
  "llmModel": "google/gemini-2.5-flash",
  "deviceId": "uuid-of-device",
  "apps": [],
  "credentials": [],
  "files": [],
  "maxSteps": 100,
  "reasoning": true,
  "vision": false,
  "stealth": false,
  "temperature": 0.5,
  "executionTimeout": 1000,
  "outputSchema": null,
  "vpnCountry": "US"
}
```

**Required fields:**
- `task` -- natural language description of what to do (min 1 char)
- `llmModel` -- which model to use (see available models below)

**Optional fields:**
- `deviceId` -- UUID of the device to run on. If omitted, a device will be provisioned automatically (requires subscription), Must set this unless explicitly told that user wants cloud device
- `apps` -- list of app package names to pre-install
- `credentials` -- list of `{ packageName, credentialNames[] }` for app logins
- `files` -- list of file identifiers to make available
- `maxSteps` -- max agent steps (default: 100)
- `reasoning` -- enable reasoning/thinking (default: true). **Always set to `false`** regardless of task complexity, unless the user explicitly requests it.
- `vision` -- enable vision/screenshot analysis (default: false)
- `stealth` -- enable stealth mode (default: false, requires Starter+ plan). **Always set to `false`** unless the user explicitly requests it.
- `temperature` -- LLM temperature (default: 0.5)
- `executionTimeout` -- timeout in seconds (default: 1000)
- `outputSchema` -- JSON schema for structured output (nullable)
- `vpnCountry` -- route through VPN in a specific country: `US`, `BR`, `FR`, `DE`, `IN`, `JP`, `KR`, `ZA`. Only use if the task specifically requires a certain region (e.g. geo-restricted content). VPN adds latency and can cause issues -- avoid unless needed.

Returns:
```json
{
  "id": "uuid",
  "streamUrl": "string",
  "token": "string"
}
```

### Run a Streamed Task (Preferred)

```
POST /tasks/stream
```

Same request body as above. Returns a `text/event-stream` SSE stream of trajectory events in real-time.

**Prefer this over `POST /tasks`.** Run the request in the background and read the SSE events to follow what the agent is doing in real-time -- what actions it's taking, what it sees on screen, why it succeeded or failed, and the final result. Report progress and outcomes to the user based on the stream events. Use `GET /tasks/{task_id}/status` to check completion if the stream disconnects.

### List Tasks

```
GET /tasks
```

Query params:
- `status` -- `created`, `running`, `paused`, `completed`, `failed`, `cancelled`
- `orderBy` -- `id`, `createdAt`, `finishedAt`, `status` (default: `createdAt`)
- `orderByDirection` -- `asc`, `desc` (default: `desc`)
- `query` -- search in task description (max 128 chars)
- `page` (default: 1), `pageSize` (default: 20, max: 100)

### Get Task

```
GET /tasks/{task_id}
```

### Get Task Status

```
GET /tasks/{task_id}/status
```

Returns `{ status: "created" | "running" | "paused" | "completed" | "failed" | "cancelled" }`.

### Cancel Task

```
POST /tasks/{task_id}/cancel
```

### Attach to Running Task

```
GET /tasks/{task_id}/attach
```

Returns an SSE `text/event-stream` of real-time trajectory events. Use this to follow along with a running task.

### Get Task Trajectory

```
GET /tasks/{task_id}/trajectory
```

Returns the full history of events from the task execution.

### Task Screenshots & UI States

```
GET /tasks/{task_id}/screenshots         -- list all screenshot URLs
GET /tasks/{task_id}/screenshots/{index}  -- get screenshot at index
GET /tasks/{task_id}/ui_states            -- list all UI state URLs
GET /tasks/{task_id}/ui_states/{index}    -- get UI state at index
```

### Available LLM Models

```
GET /models
```

Returns the list of models that can be used when creating tasks. Use this to check which models are currently available.

**Default model:** Prefer `google/gemini-3-flash` unless the user requests a specific model.

---

## App Library

### List Available Apps

```
GET /apps
```

Query params:
- `page` (default: 1), `pageSize` (default: 10)
- `source` -- `all`, `uploaded`, `store`, `queued` (default: `all`)
- `query` -- search by name
- `sortBy` -- `createdAt`, `name` (default: `createdAt`)
- `order` -- `asc`, `desc` (default: `desc`)

---

## Webhooks

Subscribe to task lifecycle events to get notified when tasks change state.

### Subscribe

```
POST /hooks/subscribe
Content-Type: application/json

{
  "targetUrl": "https://your-server.com/webhook",
  "events": ["completed", "failed"],
  "service": "other"
}
```

Events: `created`, `running`, `completed`, `failed`, `cancelled`, `paused`
Services: `zapier`, `n8n`, `make`, `internal`, `other`

### List Hooks

```
GET /hooks
```

### Get Hook

```
GET /hooks/{hook_id}
```

### Edit Hook

```
POST /hooks/{hook_id}/edit
Content-Type: application/json

{ "events": ["completed"], "state": "active" }
```

### Unsubscribe

```
POST /hooks/{hook_id}/unsubscribe
```
