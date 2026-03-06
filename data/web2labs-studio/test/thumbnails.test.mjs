import test from "node:test"
import assert from "node:assert/strict"
import { ThumbnailsTool } from "../src/tools/thumbnails.mjs"

class FakeApiClient {
  constructor() {
    this.lastProjectId = null
    this.lastPayload = null
  }

  async getPricing() {
    return {
      thumbnails: {
        standard: { costPerVariant: 8 },
        premium: { costPerVariant: 32 },
      },
      creatorCreditBundles: [{ id: "topup_s", credits: 120, price: 9.99 }],
      apiCreditBundles: [{ id: "starter", credits: 20, price: 39.99 }],
    }
  }

  async getCredits() {
    return {
      total: 10,
      apiCredits: { total: 10 },
      creatorCredits: { total: 200 },
      subscription: { tier: "creator", monthlyLimit: 100, monthlyUsed: 0 },
    }
  }

  async getAnalytics() {
    return { thisMonth: { apiCreditsUsed: 0, creatorCreditsUsed: 0, projectsProcessed: 0 } }
  }

  async listProjectThumbnails() {
    return { thumbnails: [] }
  }

  async generateProjectThumbnails(projectId, payload) {
    this.lastProjectId = projectId
    this.lastPayload = payload
    return { projectId, thumbnails: [], creditsCost: 0 }
  }
}

test("ThumbnailsTool requires project_id", async () => {
  const apiClient = new FakeApiClient()
  await assert.rejects(
    ThumbnailsTool.execute({ apiClient }, {}),
    /project_id is required/i
  )
})

test("ThumbnailsTool clamps variants and maps flags", async () => {
  const apiClient = new FakeApiClient()
  const result = await ThumbnailsTool.execute(
    { apiClient },
    {
      project_id: "project-1",
      variants: 9,
      premium_quality: true,
      use_brand_colors: true,
      use_brand_faces: false,
      confirm_spend: true,
    }
  )

  assert.equal(apiClient.lastProjectId, "project-1")
  assert.equal(apiClient.lastPayload.variants, 3)
  assert.equal(apiClient.lastPayload.premiumQuality, true)
  assert.equal(apiClient.lastPayload.useBrandColors, true)
  assert.equal(apiClient.lastPayload.useBrandFaces, false)
  assert.equal(result.projectId, "project-1")
})

test("ThumbnailsTool requires confirmation in explicit spend mode", async () => {
  const apiClient = new FakeApiClient()

  await assert.rejects(
    ThumbnailsTool.execute(
      {
        apiClient,
        apiEndpoint: "https://web2labs.com",
        spendPolicy: { mode: "explicit" },
      },
      {
        project_id: "project-1",
        variants: 1,
      }
    ),
    /confirmation required/i
  )
})
