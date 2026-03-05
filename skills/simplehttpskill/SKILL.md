---
name: simple-http
description: Make HTTP requests (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS) with custom headers, automatic retries, and graceful error handling. Use when the user needs to call an API, fetch a URL, send webhooks, or make any HTTP request without external dependencies.
---

# Simple HTTP Skill

Make HTTP requests using only Node.js built-in modules. Supports all standard
methods, arbitrary headers, automatic retries with exponential backoff, and
never throws on failure — always resolves with an inspectable response object.

## Required Inputs

- **url** (string): Fully qualified URL to request.
- **method** (string, optional): HTTP method. Default `GET`.
- **headers** (object, optional): Request headers.
- **body** (string | Buffer | object, optional): Request body. Objects are auto-serialized to JSON.
- **maxRetries** (number, optional): Retry attempts for transient failures. Default `3`.
- **timeout** (number, optional): Socket timeout in ms. Default `30000`.

## Step-by-Step Workflow

1. Import the client from `src/http-client.js`:

```js
const { HttpClient } = require("./src/http-client");
```

2. Create a client instance (optionally set default headers shared across calls):

```js
const client = new HttpClient({
  defaultHeaders: { Authorization: "Bearer <token>" },
  maxRetries: 3,
});
```

3. Make requests using convenience methods or the generic `request()`:

```js
// GET
const resp = await client.get("https://api.example.com/items");

// POST with JSON body
const resp = await client.post("https://api.example.com/items", {
  body: { name: "widget" },
});

// PUT with custom headers
const resp = await client.put("https://api.example.com/items/1", {
  headers: { "X-Request-Id": "abc123" },
  body: { name: "updated" },
});

// DELETE
const resp = await client.delete("https://api.example.com/items/1");

// Generic form — any method
const resp = await client.request("PATCH", "https://api.example.com/items/1", {
  body: { qty: 5 },
});
```

4. Inspect the response:

```js
if (resp.ok) {
  console.log(resp.body);      // parsed JSON or raw string
  console.log(resp.status);    // e.g. 200
  console.log(resp.headers);   // response headers object
} else {
  console.log(resp.error);     // human-readable error (null if HTTP error with status)
  console.log(resp.status);    // HTTP status code or null for network errors
}
```

## Output Format

Every call resolves with an object containing:

| Key       | Type              | Description                                        |
|-----------|-------------------|----------------------------------------------------|
| `ok`      | `boolean`         | `true` if status is 2xx                            |
| `status`  | `number \| null`  | HTTP status code; `null` for network-level errors  |
| `headers` | `object`          | Response headers                                   |
| `body`    | `any`             | Parsed JSON (if content-type is JSON), else string |
| `error`   | `string \| null`  | Error description on failure; `null` on success    |

## Error Handling & Retry Behavior

- **Retried automatically:** Connection errors, timeouts, and HTTP 429 / 5xx responses.
- **Not retried:** 4xx errors (except 429) — returned immediately.
- **Backoff:** Exponential with jitter (base 500ms, capped at 30s).
- **Graceful failure:** The client never throws. After exhausting retries, it resolves with the last error response so the caller can always inspect `resp.ok` and `resp.error`.

## Configuration Options

All options can be set at the client level (constructor) and overridden per-request:

| Option           | Default  | Description                          |
|------------------|----------|--------------------------------------|
| `defaultHeaders` | `{}`     | Headers applied to every request     |
| `maxRetries`     | `3`      | Max retry attempts                   |
| `timeout`        | `30000`  | Socket timeout in ms                 |
| `backoffBase`    | `500`    | Base delay (ms) for exponential backoff |
| `backoffMax`     | `30000`  | Maximum backoff delay cap (ms)       |

## Dependencies

None — uses only Node.js built-in modules (`http`, `https`, `url`).
