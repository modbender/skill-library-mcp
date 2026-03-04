import { createServer } from "node:http"
import assert from "node:assert/strict"
import { mkdtemp } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import test from "node:test"
import { SetupTool } from "../src/tools/setup.mjs"

class FakeApiClient {
  constructor() {
    this.apiKey = null
    this.bearerToken = "bearer-token"
  }

  setApiKey(value) {
    this.apiKey = value
  }

  setBearerToken(value) {
    this.bearerToken = value
  }
}

async function createSetupApiServer() {
  const server = createServer((req, res) => {
    if (req.method === "POST" && req.url === "/api/auth/magic/send") {
      res.statusCode = 200
      res.setHeader("Content-Type", "application/json")
      res.end(JSON.stringify({ success: true, data: { email: "setup@example.com" } }))
      return
    }

    if (req.method === "POST" && req.url === "/api/auth/magic/token") {
      res.statusCode = 200
      res.setHeader("Content-Type", "application/json")
      res.end(
        JSON.stringify({
          success: true,
          data: {
            accessToken: "access-token",
            userId: "user-123",
            tier: "free",
            expiresIn: 3600,
          },
        })
      )
      return
    }

    if (req.method === "POST" && req.url === "/api/user/api-key/generate") {
      res.statusCode = 200
      res.setHeader("Content-Type", "application/json")
      res.end(
        JSON.stringify({
          success: true,
          data: {
            key: "w2l_generated_key",
            keyPrefix: "w2l_gene",
            freeCredits: 2,
          },
        })
      )
      return
    }

    res.statusCode = 404
    res.end()
  })

  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve))
  const address = server.address()
  return {
    baseUrl: `http://127.0.0.1:${address.port}`,
    close: () => new Promise((resolve) => server.close(resolve)),
  }
}

test("SetupTool send_magic_link validates email", async () => {
  const context = {
    apiEndpoint: "https://example.com",
    apiClient: new FakeApiClient(),
  }

  await assert.rejects(
    SetupTool.execute(context, {
      action: "send_magic_link",
      email: "invalid",
    }),
    /valid email/i
  )
})

test("SetupTool complete_setup stores key and updates api client", async () => {
  const api = await createSetupApiServer()
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-setup-tool-"))
  process.env.OPENCLAW_CONFIG_PATH = join(sandbox, "openclaw.json")

  const context = {
    apiEndpoint: api.baseUrl,
    apiClient: new FakeApiClient(),
  }

  try {
    const result = await SetupTool.execute(context, {
      action: "complete_setup",
      email: "setup@example.com",
      code: "ABC123",
    })

    assert.equal(result.configured, true)
    assert.equal(result.userId, "user-123")
    assert.equal(result.freeCredits, 2)
    assert.equal(context.apiClient.apiKey, "w2l_generated_key")
    assert.equal(context.apiClient.bearerToken, null)
  } finally {
    delete process.env.OPENCLAW_CONFIG_PATH
    await api.close()
  }
})

test("SetupTool save_api_key persists existing key", async () => {
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-setup-tool-"))
  process.env.OPENCLAW_CONFIG_PATH = join(sandbox, "openclaw.json")

  const context = {
    apiEndpoint: "https://example.com",
    apiClient: new FakeApiClient(),
  }

  try {
    const result = await SetupTool.execute(context, {
      action: "save_api_key",
      api_key: "w2l_manual_key",
    })

    assert.equal(result.configured, true)
    assert.equal(context.apiClient.apiKey, "w2l_manual_key")
    assert.equal(context.apiClient.bearerToken, null)
  } finally {
    delete process.env.OPENCLAW_CONFIG_PATH
  }
})
