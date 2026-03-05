export class FeedbackTool {
  static async execute(context, params) {
    const type = String(params.type || "").trim().toLowerCase()
    const title = String(params.title || "").trim()
    const description = String(params.description || "").trim()

    if (!type || !title || !description) {
      throw new Error("type, title, and description are required")
    }

    const payload = {
      type,
      title,
      description,
      severity: params.severity || "medium",
      projectId: params.project_id || null,
      context: {
        skillVersion: context.skillVersion,
        agent: "openclaw",
        os: process.platform,
        nodeVersion: process.version,
        timestamp: new Date().toISOString(),
      },
    }

    return context.apiClient.submitFeedback(payload, {
      "X-Agent-Client": "openclaw",
      "X-Skill-Version": context.skillVersion,
      "Content-Type": "application/json",
    })
  }
}
