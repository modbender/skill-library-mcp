export class DeleteTool {
  static async execute(context, params) {
    const projectId = String(params.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const result = await context.apiClient.deleteProject(projectId)
    return {
      projectId,
      ...result,
    }
  }
}
