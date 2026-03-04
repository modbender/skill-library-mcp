export class ProjectsTool {
  static async execute(context, params) {
    const rawLimit =
      typeof params.limit === "undefined" ? 20 : Number(params.limit)
    const rawOffset =
      typeof params.offset === "undefined" ? 0 : Number(params.offset)
    const limit = Math.min(100, Math.max(1, Number.isFinite(rawLimit) ? rawLimit : 20))
    const offset = Math.max(0, Number.isFinite(rawOffset) ? rawOffset : 0)
    return context.apiClient.listProjects(limit, offset)
  }
}
