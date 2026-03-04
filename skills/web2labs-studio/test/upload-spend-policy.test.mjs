import test from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, writeFile } from "node:fs/promises"
import { join } from "node:path"
import { tmpdir } from "node:os"
import { UploadTool } from "../src/tools/upload.mjs"

class FakeApiClient {
  constructor() {
    this.uploadCalls = 0
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

  async uploadProject() {
    this.uploadCalls += 1
    return {
      projectId: "project-1",
      status: "Uploading",
      pollUrl: "/api/v1/projects/project-1/status",
    }
  }
}

async function createVideoFixture() {
  const sandbox = await mkdtemp(join(tmpdir(), "w2l-upload-policy-test-"))
  const filePath = join(sandbox, "input.mp4")
  await writeFile(filePath, "video")
  return filePath
}

test("UploadTool requires confirmation in explicit spend mode", async () => {
  const filePath = await createVideoFixture()
  const apiClient = new FakeApiClient()

  await assert.rejects(
    UploadTool.execute(
      {
        apiClient,
        defaultPreset: "quick",
        apiEndpoint: "https://web2labs.com",
        spendPolicy: { mode: "explicit" },
      },
      {
        file_path: filePath,
      }
    ),
    /confirmation required/i
  )

  assert.equal(apiClient.uploadCalls, 0)
})

test("UploadTool allows standard upload without confirmation in smart mode", async () => {
  const filePath = await createVideoFixture()
  const apiClient = new FakeApiClient()

  const result = await UploadTool.execute(
    {
      apiClient,
      defaultPreset: "quick",
      apiEndpoint: "https://web2labs.com",
      spendPolicy: { mode: "smart" },
    },
    {
      file_path: filePath,
    }
  )

  assert.equal(result.projectId, "project-1")
  assert.equal(apiClient.uploadCalls, 1)
})

test("UploadTool requires confirmation for rush in smart mode", async () => {
  const filePath = await createVideoFixture()
  const apiClient = new FakeApiClient()

  await assert.rejects(
    UploadTool.execute(
      {
        apiClient,
        defaultPreset: "quick",
        apiEndpoint: "https://web2labs.com",
        spendPolicy: { mode: "smart" },
      },
      {
        file_path: filePath,
        priority: "rush",
      }
    ),
    /confirmation required/i
  )

  assert.equal(apiClient.uploadCalls, 0)
})
