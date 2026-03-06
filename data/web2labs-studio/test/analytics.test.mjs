import test from "node:test"
import assert from "node:assert/strict"
import { AnalyticsTool } from "../src/tools/analytics.mjs"

class FakeApiClient {
  constructor() {
    this.lastPeriod = null
  }

  async getAnalytics(period) {
    this.lastPeriod = period
    return { period }
  }
}

test("AnalyticsTool validates period", async () => {
  const apiClient = new FakeApiClient()

  await assert.rejects(
    AnalyticsTool.execute({ apiClient }, { period: "weekly" }),
    /period must be one of/i
  )
})

test("AnalyticsTool passes supported period", async () => {
  const apiClient = new FakeApiClient()
  const result = await AnalyticsTool.execute(
    { apiClient },
    { period: "this_month" }
  )

  assert.equal(apiClient.lastPeriod, "this_month")
  assert.equal(result.period, "this_month")
})
