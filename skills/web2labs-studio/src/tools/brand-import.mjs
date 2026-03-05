export class BrandImportTool {
  static normalizeApply(value) {
    if (value === true) return true
    return String(value || "")
      .trim()
      .toLowerCase() === "true"
  }

  static async execute(context, params = {}) {
    const url = String(params.url || "").trim()
    if (!url) {
      throw new Error("url is required")
    }
    if (url.length > 2048) {
      throw new Error("URL is too long (max 2048 characters)")
    }
    if (!/^https?:\/\/.+/i.test(url)) {
      throw new Error("URL must start with http:// or https://")
    }

    const apply = BrandImportTool.normalizeApply(params.apply)
    const result = await context.apiClient.importBrand({
      url,
      apply,
    })

    return {
      action: apply ? "apply" : "preview",
      ...result,
    }
  }
}

