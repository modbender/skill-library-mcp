export class StatusTool {
  static async execute(context, params) {
    const projectId = String(params.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const status = await context.apiClient.getProjectStatus(projectId)
    return {
      projectId,
      status: status.status,
      progress: status.progress,
      resultsUrl: status.resultsUrl || null,
      retentionTimeRemaining: status.retentionTimeRemaining || null,
      error: status.error || null,
    }
  }
}
