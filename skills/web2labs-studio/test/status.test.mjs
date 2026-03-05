import test from "node:test"
import assert from "node:assert/strict"
import { StatusTool } from "../src/tools/status.mjs"

class FakeApiClient {
  async getProjectStatus(projectId) {
    return {
      status: "editing",
      progress: { percentage: 45, stage: "AI cuts" },
      resultsUrl: null,
      retentionTimeRemaining: null,
      error: null,
    }
  }
}

test("StatusTool returns project status", async () => {
  const result = await StatusTool.execute(
    { apiClient: new FakeApiClient() },
    { project_id: "proj_123" }
  )

  assert.equal(result.projectId, "proj_123")
  assert.equal(result.status, "editing")
  assert.equal(result.progress.percentage, 45)
  assert.equal(result.resultsUrl, null)
  assert.equal(result.error, null)
})

test("StatusTool throws on missing project_id", async () => {
  await assert.rejects(
    () => StatusTool.execute({ apiClient: new FakeApiClient() }, {}),
    { message: "project_id is required" }
  )
})
