import { SpendPolicyGuard } from "../lib/spend-policy.mjs"

const RERENDER_CREATOR_CREDIT_COST = 15

export class RerenderTool {
  static async execute(context, params) {
    const projectId = String(params?.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const configuration = params?.configuration
    if (
      !configuration ||
      typeof configuration !== "object" ||
      Array.isArray(configuration)
    ) {
      throw new Error("configuration must be an object")
    }

    const status = await context.apiClient.getProjectStatus(projectId)
    const isFirstRerender = !status.rerenderCount || Number(status.rerenderCount) === 0
    const estimatedCreatorCredits = isFirstRerender ? 0 : RERENDER_CREATOR_CREDIT_COST

    const spendAuthorization = await SpendPolicyGuard.authorizeAction(
      context,
      {
        action: "rerender",
        actionLabel: isFirstRerender
          ? "Re-render project (first re-render is free)"
          : `Re-render project (${RERENDER_CREATOR_CREDIT_COST} Creator Credits)`,
        estimatedCost: {
          apiCredits: 0,
          creatorCredits: estimatedCreatorCredits,
        },
        confirmSpend: Boolean(params?.confirm_spend),
      }
    )

    const result = await context.apiClient.rerenderProject(
      projectId,
      configuration
    )

    return {
      projectId,
      spendPolicy: spendAuthorization.policy?.mode || "smart",
      estimatedCost: spendAuthorization.estimatedCost,
      firstRerender: isFirstRerender,
      ...result,
    }
  }
}
