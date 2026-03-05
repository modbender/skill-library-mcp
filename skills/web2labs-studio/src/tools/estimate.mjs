export class EstimateTool {
  static normalizeDurationMinutes(value) {
    if (!Number.isFinite(Number(value))) {
      return null
    }
    const normalized = Math.round(Number(value))
    return Math.min(24 * 60, Math.max(0, normalized))
  }

  static async execute(context, params) {
    const payload = {}

    if (typeof params?.preset !== "undefined" && params?.preset !== null) {
      payload.preset = String(params.preset).trim()
    }

    const durationMinutes = EstimateTool.normalizeDurationMinutes(
      params?.duration_minutes
    )
    if (durationMinutes !== null) {
      payload.durationMinutes = durationMinutes
    }

    if (typeof params?.priority !== "undefined" && params?.priority !== null) {
      const priority = String(params.priority).trim().toLowerCase()
      if (priority !== "normal" && priority !== "rush") {
        throw new Error('priority must be "normal" or "rush"')
      }
      payload.priority = priority
    }

    if (typeof params?.configuration !== "undefined") {
      if (!params.configuration || typeof params.configuration !== "object") {
        throw new Error("configuration must be an object")
      }
      payload.configuration = params.configuration
    }

    return context.apiClient.estimateCost(payload)
  }
}
