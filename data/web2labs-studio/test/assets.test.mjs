import test from "node:test"
import assert from "node:assert/strict"
import { AssetsTool } from "../src/tools/assets.mjs"

test("AssetsTool list action returns assets payload", async () => {
  const context = {
    apiClient: {
      async listAssets() {
        return {
          assets: [{ id: "intro" }],
          total: 1,
        }
      },
    },
  }

  const result = await AssetsTool.execute(context, { action: "list" })
  assert.equal(result.action, "list")
  assert.equal(result.total, 1)
  assert.equal(result.assets[0].id, "intro")
})

test("AssetsTool upload action requires file_path", async () => {
  const context = {
    apiClient: {
      async uploadAsset() {
        return {}
      },
      async listAssets() {
        return { assets: [] }
      },
    },
  }

  await assert.rejects(
    () => AssetsTool.execute(context, { action: "upload", asset_type: "intro" }),
    /file_path is required/i
  )
})

test("AssetsTool upload/delete actions call API client", async () => {
  const calls = []
  const context = {
    apiClient: {
      async uploadAsset(assetType, filePath) {
        calls.push(["upload", assetType, filePath])
        return { ok: true }
      },
      async deleteAsset(assetId) {
        calls.push(["delete", assetId])
        return { deleted: true }
      },
      async listAssets() {
        return { assets: [{ id: "intro" }] }
      },
    },
  }

  const uploadResult = await AssetsTool.execute(context, {
    action: "upload",
    asset_type: "intro",
    file_path: "C:/tmp/intro.mp4",
  })
  assert.equal(uploadResult.action, "upload")
  assert.equal(calls[0][0], "upload")
  assert.equal(calls[0][1], "intro")

  const deleteResult = await AssetsTool.execute(context, {
    action: "delete",
    asset_id: "intro",
  })
  assert.equal(deleteResult.action, "delete")
  assert.equal(calls[1][0], "delete")
  assert.equal(calls[1][1], "intro")
})
