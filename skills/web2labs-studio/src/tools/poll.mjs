import { ProjectPoller } from "../lib/poller.mjs"

export class PollTool {
  static normalizeTimeoutMinutes(value) {
    const parsed = Number(value)
    if (!Number.isFinite(parsed)) {
      return 30
    }
    return Math.min(180, Math.max(1, parsed))
  }

  static async execute(context, params) {
    const projectId = String(params.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const timeoutMinutes = PollTool.normalizeTimeoutMinutes(
      params.timeout_minutes || 30
    )
    const updates = []

    const finalStatus = await ProjectPoller.poll(context.apiClient, projectId, {
      timeoutMinutes,
      onProgress: async (update) => {
        updates.push({
          status: update.status,
          progress: update.progress,
          retentionTimeRemaining: update.retentionTimeRemaining,
        })
      },
    })

    return {
      projectId,
      timeoutMinutes,
      updates,
      final: finalStatus,
      completed: String(finalStatus.status || "").toLowerCase() === "completed",
      failed: String(finalStatus.status || "").toLowerCase() === "failed",
    }
  }
}
