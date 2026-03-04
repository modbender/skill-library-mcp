import test from "node:test"
import assert from "node:assert/strict"
import { createServer } from "node:http"
import { StudioApiClient, StudioApiError } from "../src/lib/api-client.mjs"

// --- Helper: tiny HTTP server for testing actual request behavior ---

function createTestServer(handler) {
  const server = createServer(handler)
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address()
      resolve({
        baseUrl: `http://127.0.0.1:${port}`,
        close: () => new Promise((r) => server.close(r)),
      })
    })
  })
}

test("StudioApiClient requires authentication", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  assert.throws(() => client.getAuthHeaders(), StudioApiError)
})

test("StudioApiClient prefers API key auth", () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
    bearerToken: "abc",
  })

  const headers = client.getAuthHeaders()
  assert.equal(headers["X-API-Key"], "w2l_test")
  assert.equal(headers.Authorization, undefined)
})

test("StudioApiClient includes basic auth alongside API key", () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
    basicAuth: "web2labs:secret",
  })

  const headers = client.getAuthHeaders()
  assert.equal(headers["X-API-Key"], "w2l_test")
  const expected = `Basic ${Buffer.from("web2labs:secret").toString("base64")}`
  assert.equal(headers.Authorization, expected)
})

test("StudioApiClient basic auth is omitted when bearer token is used", () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    bearerToken: "abc",
    basicAuth: "web2labs:secret",
  })

  const headers = client.getAuthHeaders()
  assert.equal(headers.Authorization, "Bearer abc")
})

test("StudioApiClient resolves v1 paths", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  assert.equal(client.resolveUrl("/credits"), "https://example.com/api/v1/credits")
  assert.equal(client.resolveUrl("/api/v1/credits"), "https://example.com/api/v1/credits")
})

test("StudioApiClient revenue/brand/assets endpoints use expected paths", async () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
  })

  const calls = []
  client.request = async (method, path, options = {}) => {
    calls.push({ method, path, options })
    return { ok: true }
  }

  await client.getPricing()
  await client.estimateCost({ durationMinutes: 10 })
  await client.getAnalytics("this_month")
  await client.getBrand()
  await client.updateBrand({ primaryColor: "#112233" })
  await client.importBrand({ url: "https://youtube.com/@web2labs", apply: false })
  await client.listAssets()
  await client.deleteAsset("intro")
  await client.generateProjectThumbnails("project-1", { variants: 2 })
  await client.rerenderProject("project-1", { subtitlesOnVideo: true })

  assert.equal(calls[0].method, "GET")
  assert.equal(calls[0].path, "/pricing")
  assert.equal(calls[1].method, "POST")
  assert.equal(calls[1].path, "/estimate")
  assert.equal(calls[2].method, "GET")
  assert.equal(calls[2].path, "/analytics?period=this_month")
  assert.equal(calls[3].method, "GET")
  assert.equal(calls[3].path, "/brand")
  assert.equal(calls[4].method, "PUT")
  assert.equal(calls[4].path, "/brand")
  assert.equal(calls[5].method, "POST")
  assert.equal(calls[5].path, "/brand/import")
  assert.equal(calls[6].method, "GET")
  assert.equal(calls[6].path, "/assets")
  assert.equal(calls[7].method, "DELETE")
  assert.equal(calls[7].path, "/assets/intro")
  assert.equal(calls[8].method, "POST")
  assert.equal(calls[8].path, "/projects/project-1/thumbnails/generate")
  assert.equal(calls[9].method, "POST")
  assert.equal(calls[9].path, "/projects/project-1/rerender")
})

test("StudioApiClient uploadAsset rejects invalid type", async () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
  })

  await assert.rejects(
    () => client.uploadAsset("bad-type", "/tmp/file.mp4"),
    /assetType must be one of/i
  )
})

// --- getSocketToken ---

test("getSocketToken calls POST /api/auth/socket", async () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
  })

  const calls = []
  client.request = async (method, path) => {
    calls.push({ method, path })
    return { token: "socket-jwt-123" }
  }

  const result = await client.getSocketToken()
  assert.equal(calls.length, 1)
  assert.equal(calls[0].method, "POST")
  assert.equal(calls[0].path, "/api/auth/socket")
  assert.equal(result.token, "socket-jwt-123")
})

test("getSocketToken resolves to /api/auth/socket (bypasses /api/v1 prefix)", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://web2labs.com" })
  assert.equal(
    client.resolveUrl("/api/auth/socket"),
    "https://web2labs.com/api/auth/socket"
  )
})

// --- Referral/apply endpoints ---

test("getReferral and applyReferralCode use correct paths", async () => {
  const client = new StudioApiClient({
    apiEndpoint: "https://example.com",
    apiKey: "w2l_test",
  })

  const calls = []
  client.request = async (method, path, options = {}) => {
    calls.push({ method, path })
    return {}
  }

  await client.getReferral()
  await client.applyReferralCode("STUDIO-ABCD")

  assert.equal(calls[0].method, "GET")
  assert.equal(calls[0].path, "/referral")
  assert.equal(calls[1].method, "POST")
  assert.equal(calls[1].path, "/referral/apply")
})

// --- parseResponse ---

test("parseResponse returns null for empty body", async () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  const result = await client.parseResponse({ text: async () => "" })
  assert.equal(result, null)
})

test("parseResponse parses valid JSON", async () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  const result = await client.parseResponse({
    text: async () => '{"success":true,"data":{"id":"p1"}}',
  })
  assert.equal(result.success, true)
  assert.equal(result.data.id, "p1")
})

test("parseResponse returns raw string for invalid JSON", async () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  const result = await client.parseResponse({
    text: async () => "not-json-at-all",
  })
  assert.equal(result, "not-json-at-all")
})

// --- isRetryableStatus ---

test("isRetryableStatus returns true for 5xx (429 has dedicated handling)", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  assert.equal(client.isRetryableStatus(500), true)
  assert.equal(client.isRetryableStatus(502), true)
  assert.equal(client.isRetryableStatus(503), true)
  assert.equal(client.isRetryableStatus(429), false)
  assert.equal(client.isRetryableStatus(400), false)
  assert.equal(client.isRetryableStatus(401), false)
  assert.equal(client.isRetryableStatus(404), false)
  assert.equal(client.isRetryableStatus(200), false)
})

// --- getBackoffMs ---

test("getBackoffMs uses exponential backoff capped at 8s", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  assert.equal(client.getBackoffMs(0), 1000)
  assert.equal(client.getBackoffMs(1), 2000)
  assert.equal(client.getBackoffMs(2), 4000)
  assert.equal(client.getBackoffMs(3), 8000)
  assert.equal(client.getBackoffMs(4), 8000) // capped
  assert.equal(client.getBackoffMs(10), 8000) // still capped
})

// --- normalizeHeaders ---

test("normalizeHeaders adds User-Agent when missing", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  const headers = client.normalizeHeaders({})
  assert.ok(headers["User-Agent"])
  assert.ok(headers["User-Agent"].includes("web2labs"))
})

test("normalizeHeaders preserves existing User-Agent", () => {
  const client = new StudioApiClient({ apiEndpoint: "https://example.com" })
  const headers = client.normalizeHeaders({ "User-Agent": "custom/1.0" })
  assert.equal(headers["User-Agent"], "custom/1.0")
})

// --- Retry behavior (real HTTP) ---

test("request retries on 500 and eventually succeeds", async () => {
  let requestCount = 0
  const server = await createTestServer((req, res) => {
    requestCount += 1
    if (requestCount < 3) {
      res.writeHead(500, { "Content-Type": "application/json" })
      res.end(JSON.stringify({ success: false, error: { code: "server_error", message: "fail" } }))
    } else {
      res.writeHead(200, { "Content-Type": "application/json" })
      res.end(JSON.stringify({ success: true, data: { ok: true } }))
    }
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 3,
    })
    // Override wait to avoid real delays
    client.wait = async () => {}

    const result = await client.request("GET", "/test")
    assert.equal(result.ok, true)
    assert.equal(requestCount, 3)
  } finally {
    await server.close()
  }
})

test("request throws after max retries exhausted on 500", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(500, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ success: false, error: { code: "server_error", message: "always fails" } }))
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 2,
    })
    client.wait = async () => {}

    await assert.rejects(
      () => client.request("GET", "/test"),
      (err) => err instanceof StudioApiError && err.code === "server_error"
    )
  } finally {
    await server.close()
  }
})

test("request handles 429 rate limiting with retry-after header", async () => {
  let requestCount = 0
  const server = await createTestServer((req, res) => {
    requestCount += 1
    if (requestCount === 1) {
      res.writeHead(429, { "Content-Type": "application/json", "retry-after": "1" })
      res.end(JSON.stringify({ success: false, error: { code: "rate_limited" } }))
    } else {
      res.writeHead(200, { "Content-Type": "application/json" })
      res.end(JSON.stringify({ success: true, data: { retried: true } }))
    }
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 2,
    })
    client.wait = async () => {} // skip real wait

    const result = await client.request("GET", "/test")
    assert.equal(result.retried, true)
    assert.equal(requestCount, 2)
  } finally {
    await server.close()
  }
})

test("request throws on timeout", async () => {
  const server = await createTestServer((req, res) => {
    // Never respond — will trigger timeout
    setTimeout(() => {
      res.writeHead(200)
      res.end()
    }, 10000)
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 0,
    })

    await assert.rejects(
      () => client.request("GET", "/test", { timeoutMs: 100 }),
      (err) => err instanceof StudioApiError && err.code === "timeout"
    )
  } finally {
    await server.close()
  }
})

test("request throws on non-ok with non-retryable status", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(404, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ success: false, error: { code: "not_found", message: "Project not found" } }))
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 0,
    })

    await assert.rejects(
      () => client.request("GET", "/test"),
      (err) => err instanceof StudioApiError && err.code === "not_found" && err.status === 404
    )
  } finally {
    await server.close()
  }
})

test("request unwraps data envelope from success response", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ success: true, data: { projectId: "p1", status: "Completed" } }))
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
    })

    const result = await client.request("GET", "/test")
    assert.equal(result.projectId, "p1")
    assert.equal(result.status, "Completed")
  } finally {
    await server.close()
  }
})

test("request throws on success:false even with 200 status", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(200, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ success: false, error: { code: "validation_error", message: "Bad input" } }))
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 0,
    })

    await assert.rejects(
      () => client.request("GET", "/test"),
      (err) => err instanceof StudioApiError && err.code === "validation_error"
    )
  } finally {
    await server.close()
  }
})

test("request raw mode returns response object directly", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(200, { "Content-Type": "application/octet-stream" })
    res.end("binary-data-here")
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
    })

    const response = await client.request("GET", "/test", { raw: true })
    assert.equal(response.status, 200)
    const text = await response.text()
    assert.equal(text, "binary-data-here")
  } finally {
    await server.close()
  }
})

test("request raw mode throws on non-ok status", async () => {
  const server = await createTestServer((req, res) => {
    res.writeHead(404)
    res.end("not found")
  })

  try {
    const client = new StudioApiClient({
      apiEndpoint: server.baseUrl,
      apiKey: "w2l_test",
      maxRetries: 0,
    })

    await assert.rejects(
      () => client.request("GET", "/test", { raw: true }),
      (err) => err instanceof StudioApiError && err.status === 404
    )
  } finally {
    await server.close()
  }
})
