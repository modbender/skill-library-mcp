import test from "node:test"
import assert from "node:assert/strict"
import { ProjectsTool } from "../src/tools/projects.mjs"

test("ProjectsTool clamps limit and offset", async () => {
  const calls = []
  const context = {
    apiClient: {
      async listProjects(limit, offset) {
        calls.push({ limit, offset })
        return { projects: [], total: 0, limit, offset }
      },
    },
  }

  await ProjectsTool.execute(context, { limit: 1000, offset: -5 })
  await ProjectsTool.execute(context, { limit: 0, offset: "bad" })

  assert.deepEqual(calls[0], { limit: 100, offset: 0 })
  assert.deepEqual(calls[1], { limit: 1, offset: 0 })
})
