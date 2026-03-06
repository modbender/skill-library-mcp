import test from "node:test"
import assert from "node:assert/strict"
import { RerenderTool } from "../src/tools/rerender.mjs"

class FakeApiClient {
  constructor(options = {}) {
    this.lastProjectId = null
    this.lastConfiguration = null
    this.rerenderCount = options.rerenderCount || 0
  }

  async getProjectStatus(projectId) {
    return { projectId, status: "Completed", rerenderCount: this.rerenderCount }
  }

  async getCredits() {
    return { apiCredits: { total: 10 }, creatorCredits: { total: 100 } }
  }

  async getPricing() {
    return { apiCreditBundles: [], creatorCreditBundles: [] }
  }

  async getAnalytics() {
    return { thisMonth: { apiCreditsUsed: 0, creatorCreditsUsed: 0, projectsProcessed: 0 } }
  }

  async rerenderProject(projectId, configuration) {
    this.lastProjectId = projectId
    this.lastConfiguration = configuration
    return {
      projectId,
      status: "Rendering",
      creditsConsumed: { apiCredits: 0, creatorCredits: 0 },
    }
  }
}

function makeContext(apiClient) {
  return {
    apiClient,
    apiEndpoint: "https://www.web2labs.com",
    spendPolicy: { mode: "auto" },
  }
}

test("RerenderTool requires project_id", async () => {
  const apiClient = new FakeApiClient()
  await assert.rejects(
    RerenderTool.execute(makeContext(apiClient), { configuration: {} }),
    /project_id is required/i
  )
})

test("RerenderTool requires configuration object", async () => {
  const apiClient = new FakeApiClient()
  await assert.rejects(
    RerenderTool.execute(
      makeContext(apiClient),
      { project_id: "project-1", configuration: "invalid" }
    ),
    /configuration must be an object/i
  )
})

test("RerenderTool forwards project_id and configuration", async () => {
  const apiClient = new FakeApiClient()
  const result = await RerenderTool.execute(
    makeContext(apiClient),
    {
      project_id: "project-1",
      configuration: {
        subtitlesOnVideo: true,
        musicEnabled: false,
      },
    }
  )

  assert.equal(apiClient.lastProjectId, "project-1")
  assert.deepEqual(apiClient.lastConfiguration, {
    subtitlesOnVideo: true,
    musicEnabled: false,
  })
  assert.equal(result.projectId, "project-1")
  assert.equal(result.status, "Rendering")
  assert.equal(result.firstRerender, true)
  assert.equal(result.estimatedCost.creatorCredits, 0)
})

test("RerenderTool estimates 15 CC for subsequent rerenders", async () => {
  const apiClient = new FakeApiClient({ rerenderCount: 1 })
  const result = await RerenderTool.execute(
    makeContext(apiClient),
    {
      project_id: "project-2",
      configuration: { subtitle: true },
    }
  )

  assert.equal(result.firstRerender, false)
  assert.equal(result.estimatedCost.creatorCredits, 15)
})
