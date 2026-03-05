import { createServer } from "node:http"
import assert from "node:assert/strict"
import { mkdtemp, readFile, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import test from "node:test"
import { AuthFlow, AuthFlowError } from "../src/lib/auth-flow.mjs"

async function createTestApiServer(handler) {
  const server = createServer(handler)
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve))
  const address = server.address()
  return {
    baseUrl: `http://127.0.0.1:${address.port}`,
    close: () => new Promise((resolve) => server.close(resolve)),
  }
}

test("AuthFlow config path can be overridden for testability", async () => {
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-auth-flow-"))
  const overridePath = join(sandbox, "openclaw.json")
  process.env.OPENCLAW_CONFIG_PATH = overridePath

  try {
    assert.equal(AuthFlow.getConfigPath(), overridePath)
    await AuthFlow.storeApiKey("w2l_test_key")
    const raw = await readFile(overridePath, "utf-8")
    const parsed = JSON.parse(raw)
    assert.equal(parsed.skills.entries["@web2labs/studio"].apiKey, "w2l_test_key")
    assert.equal(parsed.skills.entries["@web2labs/studio"].enabled, true)
  } finally {
    delete process.env.OPENCLAW_CONFIG_PATH
  }
})

test("AuthFlow.sendMagicLink handles success", async () => {
  const api = await createTestApiServer((req, res) => {
    if (req.method === "POST" && req.url === "/api/auth/magic/send") {
      res.statusCode = 200
      res.setHeader("Content-Type", "application/json")
      res.end(JSON.stringify({ success: true, data: { email: "user@example.com" } }))
      return
    }
    res.statusCode = 404
    res.end()
  })

  try {
    const result = await AuthFlow.sendMagicLink(api.baseUrl, "user@example.com")
    assert.equal(result.sent, true)
    assert.equal(result.email, "user@example.com")
  } finally {
    await api.close()
  }
})

test("AuthFlow.completeMagicLinkToken surfaces invalid_code", async () => {
  const api = await createTestApiServer((req, res) => {
    if (req.method === "POST" && req.url === "/api/auth/magic/token") {
      res.statusCode = 401
      res.setHeader("Content-Type", "application/json")
      res.end(
        JSON.stringify({
          success: false,
          error: { code: "invalid_code", message: "Invalid or expired code" },
        })
      )
      return
    }
    res.statusCode = 404
    res.end()
  })

  try {
    await assert.rejects(
      AuthFlow.completeMagicLinkToken(api.baseUrl, "user@example.com", "ABC123"),
      (error) => {
        assert.equal(error instanceof AuthFlowError, true)
        assert.equal(error.code, "invalid_code")
        return true
      }
    )
  } finally {
    await api.close()
  }
})

test("AuthFlow.generateApiKey surfaces key_already_exists", async () => {
  const api = await createTestApiServer((req, res) => {
    if (req.method === "POST" && req.url === "/api/user/api-key/generate") {
      res.statusCode = 409
      res.setHeader("Content-Type", "application/json")
      res.end(
        JSON.stringify({
          success: false,
          error: { code: "key_already_exists", message: "Key already exists" },
        })
      )
      return
    }
    res.statusCode = 404
    res.end()
  })

  try {
    await assert.rejects(AuthFlow.generateApiKey(api.baseUrl, "token"), (error) => {
      assert.equal(error instanceof AuthFlowError, true)
      assert.equal(error.code, "key_already_exists")
      return true
    })
  } finally {
    await api.close()
  }
})

test("AuthFlow.storeApiKey merges existing config", async () => {
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-auth-flow-"))
  const configPath = join(sandbox, "openclaw.json")
  process.env.OPENCLAW_CONFIG_PATH = configPath

  await writeFile(
    configPath,
    JSON.stringify(
      {
        skills: {
          entries: {
            "@other/skill": { enabled: true, apiKey: "other" },
          },
        },
      },
      null,
      2
    ),
    "utf-8"
  )

  try {
    await AuthFlow.storeApiKey("w2l_merged_key")
    const raw = await readFile(configPath, "utf-8")
    const parsed = JSON.parse(raw)
    assert.equal(parsed.skills.entries["@other/skill"].apiKey, "other")
    assert.equal(
      parsed.skills.entries["@web2labs/studio"].apiKey,
      "w2l_merged_key"
    )
  } finally {
    delete process.env.OPENCLAW_CONFIG_PATH
  }
})
