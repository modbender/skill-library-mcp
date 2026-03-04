import test, { after } from "node:test"
import assert from "node:assert/strict"
import { StudioSkillServer } from "../src/server.mjs"

// McpServer keeps event loop handles open; force clean exit after tests.
after(() => setTimeout(() => process.exit(0), 50))

// --- readConfig ---

test("readConfig reads environment variables", () => {
  const original = { ...process.env }
  try {
    process.env.WEB2LABS_API_ENDPOINT = "https://custom.api.com"
    process.env.WEB2LABS_API_KEY = "w2l_testkey123"
    process.env.WEB2LABS_BEARER_TOKEN = "bearer-abc"
    process.env.WEB2LABS_DEFAULT_PRESET = "podcast"
    process.env.WEB2LABS_DOWNLOAD_DIR = "/tmp/exports"
    process.env.WEB2LABS_SPEND_POLICY = "explicit"
    delete process.env.WEB2LABS_TEST_MODE
    delete process.env.WEB2LABS_BASIC_AUTH

    const server = new StudioSkillServer()
    const config = server.config

    assert.equal(config.apiEndpoint, "https://custom.api.com")
    assert.equal(config.apiKey, "w2l_testkey123")
    assert.equal(config.bearerToken, "bearer-abc")
    assert.equal(config.defaultPreset, "podcast")
    assert.equal(config.downloadDir, "/tmp/exports")
    assert.equal(config.spendPolicy.mode, "explicit")
    assert.equal(config.testMode, false)
    assert.equal(config.basicAuth, null)
  } finally {
    for (const key of [
      "WEB2LABS_API_ENDPOINT",
      "WEB2LABS_API_KEY",
      "WEB2LABS_BEARER_TOKEN",
      "WEB2LABS_DEFAULT_PRESET",
      "WEB2LABS_DOWNLOAD_DIR",
      "WEB2LABS_SPEND_POLICY",
      "WEB2LABS_TEST_MODE",
      "WEB2LABS_BASIC_AUTH",
    ]) {
      if (original[key] === undefined) delete process.env[key]
      else process.env[key] = original[key]
    }
  }
})

test("readConfig uses defaults when env vars are absent", () => {
  const original = { ...process.env }
  try {
    delete process.env.WEB2LABS_API_ENDPOINT
    delete process.env.WEB2LABS_API_KEY
    delete process.env.WEB2LABS_BEARER_TOKEN
    delete process.env.WEB2LABS_DEFAULT_PRESET
    delete process.env.WEB2LABS_DOWNLOAD_DIR
    delete process.env.WEB2LABS_SPEND_POLICY
    delete process.env.WEB2LABS_TEST_MODE
    delete process.env.WEB2LABS_BASIC_AUTH

    const server = new StudioSkillServer()
    const config = server.config

    assert.equal(config.apiEndpoint, "https://www.web2labs.com")
    assert.equal(config.apiKey, null)
    assert.equal(config.bearerToken, null)
    assert.equal(config.basicAuth, null)
    assert.equal(config.testMode, false)
    assert.equal(config.defaultPreset, "youtube")
    assert.equal(config.downloadDir, "~/studio-exports")
    assert.equal(config.spendPolicy.mode, "auto")
  } finally {
    for (const key of Object.keys(original)) {
      process.env[key] = original[key]
    }
  }
})

test("readConfig enables test mode with WEB2LABS_TEST_MODE=true", () => {
  const original = { ...process.env }
  try {
    delete process.env.WEB2LABS_API_ENDPOINT
    process.env.WEB2LABS_TEST_MODE = "true"
    process.env.WEB2LABS_BASIC_AUTH = "web2labs:secret"

    const server = new StudioSkillServer()
    const config = server.config

    assert.equal(config.testMode, true)
    assert.equal(config.apiEndpoint, "https://test.web2labs.com")
    assert.equal(config.basicAuth, "web2labs:secret")
  } finally {
    for (const key of [
      "WEB2LABS_API_ENDPOINT",
      "WEB2LABS_TEST_MODE",
      "WEB2LABS_BASIC_AUTH",
    ]) {
      if (original[key] === undefined) delete process.env[key]
      else process.env[key] = original[key]
    }
  }
})

test("readConfig test mode can be overridden with explicit endpoint", () => {
  const original = { ...process.env }
  try {
    process.env.WEB2LABS_TEST_MODE = "true"
    process.env.WEB2LABS_API_ENDPOINT = "https://custom-test.example.com"

    const server = new StudioSkillServer()
    const config = server.config

    assert.equal(config.testMode, true)
    assert.equal(config.apiEndpoint, "https://custom-test.example.com")
  } finally {
    for (const key of ["WEB2LABS_TEST_MODE", "WEB2LABS_API_ENDPOINT"]) {
      if (original[key] === undefined) delete process.env[key]
      else process.env[key] = original[key]
    }
  }
})

// --- createToolContext ---

test("createToolContext returns expected shape", () => {
  const server = new StudioSkillServer()
  const ctx = server.createToolContext()

  assert.ok(ctx.apiClient, "should have apiClient")
  assert.ok(ctx.apiEndpoint, "should have apiEndpoint")
  assert.ok(ctx.defaultPreset, "should have defaultPreset")
  assert.ok(ctx.downloadDir, "should have downloadDir")
  assert.ok(ctx.skillVersion, "should have skillVersion")
  assert.ok(ctx.spendPolicy, "should have spendPolicy")
  assert.equal(typeof ctx.testMode, "boolean", "should have testMode")
  assert.ok("basicAuth" in ctx, "should have basicAuth key")
})

test("createToolContext apiClient has correct baseUrl", () => {
  const original = process.env.WEB2LABS_API_ENDPOINT
  try {
    process.env.WEB2LABS_API_ENDPOINT = "https://test.web2labs.com"
    const server = new StudioSkillServer()
    const ctx = server.createToolContext()
    assert.equal(ctx.apiClient.baseUrl, "https://test.web2labs.com")
  } finally {
    if (original === undefined) delete process.env.WEB2LABS_API_ENDPOINT
    else process.env.WEB2LABS_API_ENDPOINT = original
  }
})

// --- wrapResult ---

test("wrapResult returns MCP-formatted content", () => {
  const server = new StudioSkillServer()
  const result = server.wrapResult({ projectId: "p1", status: "Completed" })

  assert.equal(result.content.length, 1)
  assert.equal(result.content[0].type, "text")
  const parsed = JSON.parse(result.content[0].text)
  assert.equal(parsed.projectId, "p1")
  assert.equal(parsed.status, "Completed")
})

test("wrapResult pretty-prints JSON", () => {
  const server = new StudioSkillServer()
  const result = server.wrapResult({ a: 1 })
  assert.ok(result.content[0].text.includes("\n"), "should be pretty-printed")
})

test("wrapResult does not set isError", () => {
  const server = new StudioSkillServer()
  const result = server.wrapResult({ ok: true })
  assert.equal(result.isError, undefined)
})

// --- wrapError ---

test("wrapError returns error-formatted MCP content", () => {
  const server = new StudioSkillServer()
  const result = server.wrapError(new Error("Something failed"))

  assert.equal(result.isError, true)
  assert.equal(result.content.length, 1)
  const parsed = JSON.parse(result.content[0].text)
  assert.equal(parsed.error, true)
  assert.equal(parsed.message, "Something failed")
  assert.equal(parsed.code, "tool_error")
  assert.equal(parsed.status, 500)
})

test("wrapError preserves StudioApiError fields", () => {
  const server = new StudioSkillServer()
  const err = {
    message: "Not found",
    code: "project_not_found",
    status: 404,
    details: { projectId: "p1" },
  }
  const result = server.wrapError(err)
  const parsed = JSON.parse(result.content[0].text)

  assert.equal(parsed.code, "project_not_found")
  assert.equal(parsed.status, 404)
  assert.deepEqual(parsed.details, { projectId: "p1" })
})

test("wrapError handles null error", () => {
  const server = new StudioSkillServer()
  const result = server.wrapError(null)
  const parsed = JSON.parse(result.content[0].text)

  assert.equal(parsed.error, true)
  assert.equal(parsed.code, "tool_error")
  assert.equal(parsed.message, "Tool execution failed")
})

// --- registerTools ---

test("registerTools registers all expected tools", () => {
  const server = new StudioSkillServer()
  const registeredNames = []
  const originalTool = server.server.tool.bind(server.server)

  server.server.tool = function (name, ...rest) {
    registeredNames.push(name)
    return originalTool(name, ...rest)
  }

  server.registerTools()

  const expectedTools = [
    "studio_upload",
    "studio_status",
    "studio_poll",
    "studio_results",
    "studio_download",
    "studio_setup",
    "studio_credits",
    "studio_pricing",
    "studio_estimate",
    "studio_thumbnails",
    "studio_analytics",
    "studio_brand",
    "studio_brand_import",
    "studio_assets",
    "studio_rerender",
    "studio_projects",
    "studio_delete",
    "studio_feedback",
    "studio_referral",
    "studio_watch",
  ]

  for (const name of expectedTools) {
    assert.ok(registeredNames.includes(name), `Missing tool registration: ${name}`)
  }

  assert.equal(registeredNames.length, expectedTools.length, "Unexpected extra tools registered")
})

// --- Constructor ---

test("constructor sets skillVersion", () => {
  const server = new StudioSkillServer()
  assert.equal(server.skillVersion, "1.0.1")
})

test("constructor creates apiClient", () => {
  const server = new StudioSkillServer()
  assert.ok(server.apiClient)
  assert.ok(typeof server.apiClient.request === "function")
})

test("constructor creates MCP server", () => {
  const server = new StudioSkillServer()
  assert.ok(server.server)
})
