export class BrandTool {
  static normalizeUpdatePayload(rawUpdates = {}) {
    const aliases = {
      channel_name: "channelName",
      primary_color: "primaryColor",
      secondary_color: "secondaryColor",
      brand_identity: "brandIdentity",
      channel_pitch: "channelPitch",
      posting_plan: "postingPlan",
      scripts_content_category: "scriptsContentCategory",
      scripts_channel_about: "scriptsChannelAbout",
      scripts_speaking_style: "scriptsSpeakingStyle",
      scripts_viewers_should_feel: "scriptsViewersShouldFeel",
      scripts_viewers_should_be: "scriptsViewersShouldBe",
      subtitle_font_id: "subtitleFontId",
      thumbnail_font_id: "thumbnailFontId",
      default_intro_enabled: "defaultIntroEnabled",
      default_outro_enabled: "defaultOutroEnabled",
    }

    const normalized = {}
    for (const [key, value] of Object.entries(rawUpdates || {})) {
      if (key === "action" || key === "updates") {
        continue
      }
      const mappedKey = aliases[key] || key
      normalized[mappedKey] = value
    }

    return normalized
  }

  static resolveRawUpdates(params = {}) {
    if (
      params.updates &&
      typeof params.updates === "object" &&
      !Array.isArray(params.updates)
    ) {
      return params.updates
    }

    const fallback = {}
    for (const [key, value] of Object.entries(params || {})) {
      if (key === "action" || key === "updates") continue
      fallback[key] = value
    }
    return fallback
  }

  static async execute(context, params = {}) {
    const action = String(params?.action || "get")
      .trim()
      .toLowerCase()

    if (action === "get") {
      const brand = await context.apiClient.getBrand()
      return {
        action: "get",
        brand,
      }
    }

    if (action !== "update") {
      throw new Error('action must be "get" or "update"')
    }

    const rawUpdates = BrandTool.resolveRawUpdates(params)
    if (
      !rawUpdates ||
      typeof rawUpdates !== "object" ||
      Array.isArray(rawUpdates)
    ) {
      throw new Error("updates must be an object")
    }

    const payload = BrandTool.normalizeUpdatePayload(rawUpdates)
    const updatedFields = Object.keys(payload)
    if (updatedFields.length === 0) {
      throw new Error("No brand fields were provided to update")
    }

    const brand = await context.apiClient.updateBrand(payload)
    return {
      action: "update",
      updatedFields,
      brand,
    }
  }
}
