import test from "node:test"
import assert from "node:assert/strict"
import { BrandImportTool } from "../src/tools/brand-import.mjs"

test("BrandImportTool returns preview result by default", async () => {
  const calls = []
  const context = {
    apiClient: {
      async importBrand(payload) {
        calls.push(payload)
        return {
          source: "youtube",
          suggested: {
            channelName: "Web2Labs",
          },
        }
      },
    },
  }

  const result = await BrandImportTool.execute(context, {
    url: "https://youtube.com/@web2labs",
  })

  assert.equal(result.action, "preview")
  assert.equal(result.source, "youtube")
  assert.equal(calls.length, 1)
  assert.equal(calls[0].apply, false)
})

test("BrandImportTool apply mode forwards apply=true", async () => {
  const calls = []
  const context = {
    apiClient: {
      async importBrand(payload) {
        calls.push(payload)
        return {
          applied: true,
          updatedFields: ["channelName"],
        }
      },
    },
  }

  const result = await BrandImportTool.execute(context, {
    url: "https://x.com/web2labs",
    apply: true,
  })

  assert.equal(result.action, "apply")
  assert.equal(result.applied, true)
  assert.equal(calls.length, 1)
  assert.equal(calls[0].apply, true)
})

test("BrandImportTool requires URL", async () => {
  const context = {
    apiClient: {
      async importBrand(payload) {
        return payload
      },
    },
  }

  await assert.rejects(
    () => BrandImportTool.execute(context, {}),
    /url is required/i
  )
})

