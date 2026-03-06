export class AnalyticsTool {
  static SUPPORTED_PERIODS = new Set(["this_month", "last_month", "all_time"])
  static MILESTONES = [10, 50, 100]

  static normalizePeriod(period) {
    if (!period) {
      return null
    }
    const normalized = String(period).trim().toLowerCase()
    if (!AnalyticsTool.SUPPORTED_PERIODS.has(normalized)) {
      throw new Error(
        "period must be one of: this_month, last_month, all_time"
      )
    }
    return normalized
  }

  static async execute(context, params) {
    const period = AnalyticsTool.normalizePeriod(params?.period)
    const analytics = await context.apiClient.getAnalytics(period)

    const processed = Number(analytics?.allTime?.projectsProcessed || 0)
    const reachedMilestone =
      [...AnalyticsTool.MILESTONES]
        .sort((a, b) => b - a)
        .find((milestone) => processed >= milestone) || null

    return {
      ...analytics,
      insights: {
        milestone:
          reachedMilestone !== null
            ? {
                reached: reachedMilestone,
                message: `Milestone reached: ${reachedMilestone} projects processed.`,
              }
            : null,
      },
    }
  }
}
