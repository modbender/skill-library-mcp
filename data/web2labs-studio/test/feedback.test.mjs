import test from "node:test"
import assert from "node:assert/strict"
import { FeedbackTool } from "../src/tools/feedback.mjs"

class FakeApiClient {
  lastPayload = null
  lastHeaders = null

  async submitFeedback(payload, headers) {
    this.lastPayload = payload
    this.lastHeaders = headers
    return { id: "fb_001", message: "Feedback received" }
  }
}

test("FeedbackTool submits feedback with context", async () => {
  const apiClient = new FakeApiClient()
  const result = await FeedbackTool.execute(
    { apiClient, skillVersion: "1.0.0" },
    {
      type: "bug",
      title: "Something broke",
      description: "Detailed description of the issue",
      severity: "high",
      project_id: "proj_abc",
    }
  )

  assert.equal(result.id, "fb_001")
  assert.equal(apiClient.lastPayload.type, "bug")
  assert.equal(apiClient.lastPayload.title, "Something broke")
  assert.equal(apiClient.lastPayload.severity, "high")
  assert.equal(apiClient.lastPayload.projectId, "proj_abc")
  assert.equal(apiClient.lastPayload.context.skillVersion, "1.0.0")
  assert.equal(apiClient.lastPayload.context.agent, "openclaw")
  assert.equal(apiClient.lastHeaders["X-Agent-Client"], "openclaw")
})

test("FeedbackTool throws on missing required fields", async () => {
  await assert.rejects(
    () =>
      FeedbackTool.execute(
        { apiClient: new FakeApiClient(), skillVersion: "1.0.0" },
        { type: "bug", title: "", description: "" }
      ),
    { message: "type, title, and description are required" }
  )
})
