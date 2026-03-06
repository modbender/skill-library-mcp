import test from "node:test"
import assert from "node:assert/strict"
import { DeleteTool } from "../src/tools/delete.mjs"

class FakeApiClient {
  async deleteProject(projectId) {
    return { deleted: true }
  }
}

test("DeleteTool deletes project and returns result", async () => {
  const result = await DeleteTool.execute(
    { apiClient: new FakeApiClient() },
    { project_id: "proj_789" }
  )

  assert.equal(result.projectId, "proj_789")
  assert.equal(result.deleted, true)
})

test("DeleteTool throws on missing project_id", async () => {
  await assert.rejects(
    () => DeleteTool.execute({ apiClient: new FakeApiClient() }, {}),
    { message: "project_id is required" }
  )
})
