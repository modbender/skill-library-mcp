import test from "node:test"
import assert from "node:assert/strict"
import { EstimateTool } from "../src/tools/estimate.mjs"

class FakeApiClient {
  constructor() {
    this.lastPayload = null
  }

  async estimateCost(payload) {
    this.lastPayload = payload
    return { ok: true, payload }
  }
}

test("EstimateTool normalizes duration and passes configuration", async () => {
  const apiClient = new FakeApiClient()
  const result = await EstimateTool.execute(
    { apiClient },
    {
      duration_minutes: 31.7,
      preset: "youtube",
      priority: "rush",
      configuration: { thumbnailVariantsRequested: 2 },
    }
  )

  assert.equal(apiClient.lastPayload.durationMinutes, 32)
  assert.equal(apiClient.lastPayload.preset, "youtube")
  assert.equal(apiClient.lastPayload.priority, "rush")
  assert.equal(apiClient.lastPayload.configuration.thumbnailVariantsRequested, 2)
  assert.equal(result.ok, true)
})

test("EstimateTool rejects non-object configuration", async () => {
  const apiClient = new FakeApiClient()

  await assert.rejects(
    EstimateTool.execute(
      { apiClient },
      {
        configuration: "bad",
      }
    ),
    /configuration must be an object/i
  )
})

test("EstimateTool rejects invalid priority", async () => {
  const apiClient = new FakeApiClient()

  await assert.rejects(
    EstimateTool.execute(
      { apiClient },
      {
        priority: "urgent",
      }
    ),
    /priority must be \"normal\" or \"rush\"/i
  )
})
