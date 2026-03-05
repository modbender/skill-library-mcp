import test from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, writeFile } from "node:fs/promises"
import { join } from "node:path"
import { tmpdir } from "node:os"
import { UploadTool } from "../src/tools/upload.mjs"

// --- Helpers ---

class FakeApiClient {
  constructor() {
    this.uploadCalls = []
  }

  async estimateCost(payload) {
    const priority = String(payload?.priority || "normal").toLowerCase()
    return {
      apiCredits: priority === "rush" ? 2 : 1,
      creatorCredits: { total: 0 },
      totalCost: {
        apiCredits: priority === "rush" ? 2 : 1,
        creatorCredits: 0,
      },
    }
  }

  async getCredits() {
    return {
      total: 10,
      apiCredits: { total: 10 },
      creatorCredits: { total: 200 },
      subscription: { tier: "creator", monthlyLimit: 100, monthlyUsed: 10 },
    }
  }

  async getPricing() {
    return {
      apiCreditBundles: [{ id: "starter", credits: 20, price: 39.99 }],
      creatorCreditBundles: [{ id: "topup_s", credits: 120, price: 9.99 }],
    }
  }

  async getAnalytics() {
    return {
      thisMonth: { apiCreditsUsed: 2, creatorCreditsUsed: 10, projectsProcessed: 2 },
    }
  }

  async uploadProject(filePath, options) {
    this.uploadCalls.push({ filePath, options })
    return {
      projectId: "project-upload-1",
      status: "Uploading",
      pollUrl: "/api/v1/projects/project-upload-1/status",
    }
  }
}

function makeContext(overrides = {}) {
  return {
    apiClient: new FakeApiClient(),
    defaultPreset: "youtube",
    apiEndpoint: "https://web2labs.com",
    spendPolicy: { mode: "smart" },
    ...overrides,
  }
}

async function createVideoFixture(ext = ".mp4") {
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-upload-test-"))
  const filePath = join(sandbox, `input${ext}`)
  await writeFile(filePath, "video-data")
  return filePath
}

// --- SUPPORTED_EXTENSIONS ---

test("SUPPORTED_EXTENSIONS includes common video formats", () => {
  const expected = [".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v"]
  for (const ext of expected) {
    assert.ok(UploadTool.SUPPORTED_EXTENSIONS.has(ext), `Missing: ${ext}`)
  }
})

test("SUPPORTED_EXTENSIONS does not include non-video formats", () => {
  const notExpected = [".jpg", ".png", ".pdf", ".txt", ".mp3", ".zip"]
  for (const ext of notExpected) {
    assert.ok(!UploadTool.SUPPORTED_EXTENSIONS.has(ext), `Should not have: ${ext}`)
  }
})

// --- stripExtension ---

test("stripExtension removes file extension", () => {
  assert.equal(UploadTool.stripExtension("video.mp4"), "video")
  assert.equal(UploadTool.stripExtension("my-video.mkv"), "my-video")
})

test("stripExtension handles files with multiple dots", () => {
  assert.equal(UploadTool.stripExtension("my.cool.video.mp4"), "my.cool.video")
})

test("stripExtension returns original if no extension", () => {
  assert.equal(UploadTool.stripExtension("noext"), "noext")
})

// --- assertLocalFile ---

test("assertLocalFile accepts supported extensions", async () => {
  const filePath = await createVideoFixture(".mp4")
  await UploadTool.assertLocalFile(filePath) // should not throw
})

test("assertLocalFile rejects unsupported extension", async () => {
  const filePath = await createVideoFixture(".txt")
  await assert.rejects(
    () => UploadTool.assertLocalFile(filePath),
    /Unsupported file type/
  )
})

test("assertLocalFile rejects non-existent file", async () => {
  await assert.rejects(
    () => UploadTool.assertLocalFile("/non/existent/file.mp4"),
    (err) => err.code === "ENOENT"
  )
})

// --- resolveConfiguration ---

test("resolveConfiguration uses preset when provided", () => {
  const result = UploadTool.resolveConfiguration(null, "youtube", null)
  assert.equal(result.preset, "youtube")
  assert.ok(typeof result.configuration === "object")
})

test("resolveConfiguration uses default preset as fallback", () => {
  const result = UploadTool.resolveConfiguration("podcast", null, null)
  assert.equal(result.preset, "podcast")
})

test("resolveConfiguration prefers explicit preset over default", () => {
  const result = UploadTool.resolveConfiguration("podcast", "gaming", null)
  assert.equal(result.preset, "gaming")
})

test("resolveConfiguration merges override configuration", () => {
  const result = UploadTool.resolveConfiguration(null, "quick", {
    subtitle: true,
  })
  assert.equal(result.preset, "quick")
  assert.equal(result.configuration.subtitle, true)
})

test("resolveConfiguration returns empty config when no preset", () => {
  const result = UploadTool.resolveConfiguration(null, null, null)
  assert.equal(result.preset, null)
  assert.deepEqual(result.configuration, {})
})

// --- execute ---

test("execute requires file_path", async () => {
  const context = makeContext()
  await assert.rejects(
    () => UploadTool.execute(context, {}),
    /file_path is required/
  )
})

test("execute requires non-empty file_path", async () => {
  const context = makeContext()
  await assert.rejects(
    () => UploadTool.execute(context, { file_path: "   " }),
    /file_path is required/
  )
})

test("execute uploads local file and returns project info", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, { file_path: filePath })

  assert.equal(result.projectId, "project-upload-1")
  assert.equal(result.status, "Uploading")
  assert.equal(result.priority, "normal")
  assert.equal(result.downloadedFromUrl, false)
  assert.equal(result.sourceUrl, null)
  assert.equal(context.apiClient.uploadCalls.length, 1)
})

test("execute uses project name from params", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, {
    file_path: filePath,
    name: "My Custom Name",
  })

  assert.equal(result.projectName, "My Custom Name")
})

test("execute derives project name from filename when not provided", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, { file_path: filePath })

  assert.equal(result.projectName, "input")
})

test("execute passes priority to upload", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext({ spendPolicy: { mode: "auto" } })
  const result = await UploadTool.execute(context, {
    file_path: filePath,
    priority: "rush",
  })

  assert.equal(result.priority, "rush")
  assert.equal(context.apiClient.uploadCalls[0].options.priority, "rush")
})

test("execute passes webhook params to upload", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, {
    file_path: filePath,
    webhook_url: "https://example.com/hook",
    webhook_secret: "s3cret",
  })

  const uploadOptions = context.apiClient.uploadCalls[0].options
  assert.equal(uploadOptions.webhookUrl, "https://example.com/hook")
  assert.equal(uploadOptions.webhookSecret, "s3cret")
})

test("execute ignores empty webhook params", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  await UploadTool.execute(context, {
    file_path: filePath,
    webhook_url: "  ",
    webhook_secret: "",
  })

  const uploadOptions = context.apiClient.uploadCalls[0].options
  assert.equal(uploadOptions.webhookUrl, null)
  assert.equal(uploadOptions.webhookSecret, null)
})

test("execute applies preset from params", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, {
    file_path: filePath,
    preset: "cinematic",
  })

  assert.equal(result.preset, "cinematic")
})

test("execute applies default preset from context", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext({ defaultPreset: "podcast" })
  const result = await UploadTool.execute(context, { file_path: filePath })

  assert.equal(result.preset, "podcast")
})

test("execute returns estimated cost", async () => {
  const filePath = await createVideoFixture()
  const context = makeContext()
  const result = await UploadTool.execute(context, { file_path: filePath })

  assert.ok(result.estimatedCost !== undefined)
  assert.equal(result.estimatedCost.apiCredits, 1)
})

test("execute handles estimateCost failure gracefully", async () => {
  const filePath = await createVideoFixture()
  const apiClient = new FakeApiClient()
  apiClient.estimateCost = async () => { throw new Error("estimate broken") }
  const context = makeContext({ apiClient })
  const result = await UploadTool.execute(context, { file_path: filePath })

  // Should still succeed — estimate failure is non-fatal
  assert.equal(result.projectId, "project-upload-1")
})

test("execute rejects unsupported URL domains", async () => {
  const context = makeContext()
  await assert.rejects(
    () => UploadTool.execute(context, { file_path: "https://randomsite.com/video" }),
    /Unsupported URL domain/
  )
})
