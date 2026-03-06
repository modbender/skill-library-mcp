import test from "node:test"
import assert from "node:assert/strict"
import { ResultsTool } from "../src/tools/results.mjs"

class FakeApiClient {
  async getProjectResults(projectId) {
    return {
      name: "Test Project",
      mainVideo: { url: "/download/main", filename: "test.mp4" },
      shorts: [],
      thumbnails: [],
    }
  }
}

test("ResultsTool returns project results", async () => {
  const result = await ResultsTool.execute(
    { apiClient: new FakeApiClient() },
    { project_id: "proj_456" }
  )

  assert.equal(result.projectId, "proj_456")
  assert.equal(result.name, "Test Project")
  assert.ok(result.mainVideo)
  assert.equal(result.mainVideo.url, "/download/main")
})

test("ResultsTool throws on missing project_id", async () => {
  await assert.rejects(
    () => ResultsTool.execute({ apiClient: new FakeApiClient() }, {}),
    { message: "project_id is required" }
  )
})
