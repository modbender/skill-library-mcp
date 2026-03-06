export class AssetsTool {
  static normalizeAction(value) {
    return String(value || "list")
      .trim()
      .toLowerCase()
  }

  static normalizeAssetType(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
  }

  static assertAssetType(assetType) {
    if (!["intro", "outro", "watermark"].includes(assetType)) {
      throw new Error("asset_type must be one of: intro, outro, watermark")
    }
  }

  static async execute(context, params = {}) {
    const action = AssetsTool.normalizeAction(params.action)

    if (action === "list") {
      const result = await context.apiClient.listAssets()
      return {
        action: "list",
        ...result,
      }
    }

    if (action === "upload") {
      const assetType = AssetsTool.normalizeAssetType(
        params.asset_type || params.assetId || params.asset_id
      )
      const filePath = String(params.file_path || "").trim()
      if (!filePath) {
        throw new Error("file_path is required for action=upload")
      }
      AssetsTool.assertAssetType(assetType)

      const uploadResult = await context.apiClient.uploadAsset(assetType, filePath)
      const latest = await context.apiClient.listAssets().catch(() => null)

      return {
        action: "upload",
        assetType,
        filePath,
        result: uploadResult,
        assets: latest?.assets || null,
      }
    }

    if (action === "delete") {
      const assetId = AssetsTool.normalizeAssetType(
        params.asset_type || params.asset_id || params.assetId
      )
      if (!assetId) {
        throw new Error("asset_type is required for action=delete (intro, outro, or watermark)")
      }
      AssetsTool.assertAssetType(assetId)

      const deleteResult = await context.apiClient.deleteAsset(assetId)
      const latest = await context.apiClient.listAssets().catch(() => null)

      return {
        action: "delete",
        assetId,
        result: deleteResult,
        assets: latest?.assets || null,
      }
    }

    throw new Error('action must be one of: "list", "upload", "delete"')
  }
}
