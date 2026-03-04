export class ReferralTool {
    static async execute(context, params) {
        const action = String(params.action || "get").trim().toLowerCase()

        if (action === "get") {
            return context.apiClient.getReferral()
        }

        if (action === "apply") {
            const code = String(params.code || "").trim()
            if (!code) {
                throw new Error("Referral code is required for action 'apply'.")
            }
            return context.apiClient.applyReferralCode(code)
        }

        throw new Error(
            `Invalid action: "${action}". Must be "get" or "apply".`
        )
    }
}
