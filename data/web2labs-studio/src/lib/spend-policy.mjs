import { PurchaseLinks } from "./purchase-links.mjs"
import { StudioApiError } from "./api-client.mjs"

export class SpendPolicy {
  static MODES = new Set(["explicit", "smart", "auto"])

  static toNumber(value, fallback, min = null, max = null) {
    const n = Number(value)
    if (!Number.isFinite(n)) {
      return fallback
    }
    let normalized = n
    if (Number.isFinite(Number(min))) {
      normalized = Math.max(Number(min), normalized)
    }
    if (Number.isFinite(Number(max))) {
      normalized = Math.min(Number(max), normalized)
    }
    return normalized
  }

  static normalizeMode(mode) {
    const normalized = String(mode || "auto").trim().toLowerCase()
    if (SpendPolicy.MODES.has(normalized)) {
      return normalized
    }
    return "auto"
  }

  static fromEnvironment(env = process.env) {
    return {
      mode: SpendPolicy.normalizeMode(env.WEB2LABS_SPEND_POLICY),
      smartApiConfirmThreshold: SpendPolicy.toNumber(
        env.WEB2LABS_SMART_CONFIRM_API_THRESHOLD,
        2,
        1,
        20
      ),
      smartCreatorConfirmThreshold: SpendPolicy.toNumber(
        env.WEB2LABS_SMART_CONFIRM_CREATOR_THRESHOLD,
        8,
        1,
        10000
      ),
      lowApiBalanceThreshold: SpendPolicy.toNumber(
        env.WEB2LABS_SMART_CONFIRM_LOW_API_BALANCE,
        2,
        0,
        1000
      ),
      lowCreatorBalanceThreshold: SpendPolicy.toNumber(
        env.WEB2LABS_SMART_CONFIRM_LOW_CREATOR_BALANCE,
        20,
        0,
        100000
      ),
      autoMaxApiPerAction: SpendPolicy.toNumber(
        env.WEB2LABS_AUTO_SPEND_MAX_API_PER_ACTION,
        2,
        1,
        1000
      ),
      autoMaxCreatorPerAction: SpendPolicy.toNumber(
        env.WEB2LABS_AUTO_SPEND_MAX_CREATOR_PER_ACTION,
        40,
        1,
        100000
      ),
      autoMaxApiPerMonth: SpendPolicy.toNumber(
        env.WEB2LABS_AUTO_SPEND_MAX_API_PER_MONTH,
        80,
        1,
        100000
      ),
      autoMaxCreatorPerMonth: SpendPolicy.toNumber(
        env.WEB2LABS_AUTO_SPEND_MAX_CREATOR_PER_MONTH,
        400,
        1,
        1000000
      ),
    }
  }

  static fromContext(context) {
    if (context?.spendPolicy && typeof context.spendPolicy === "object") {
      return {
        ...SpendPolicy.fromEnvironment({}),
        ...context.spendPolicy,
        mode: SpendPolicy.normalizeMode(context.spendPolicy.mode),
      }
    }
    return SpendPolicy.fromEnvironment(process.env)
  }
}

export class SpendPolicyGuard {
  static toNumber(value, fallback = 0) {
    const n = Number(value)
    if (!Number.isFinite(n)) {
      return fallback
    }
    return n
  }

  static normalizeCost(estimatedCost) {
    return {
      apiCredits: Math.max(
        0,
        Math.round(
          SpendPolicyGuard.toNumber(
            estimatedCost?.apiCredits ??
              estimatedCost?.totalCost?.apiCredits ??
              estimatedCost?.api,
            0
          )
        )
      ),
      creatorCredits: Math.max(
        0,
        Math.round(
          SpendPolicyGuard.toNumber(
            estimatedCost?.creatorCredits ??
              estimatedCost?.totalCost?.creatorCredits ??
              estimatedCost?.creator?.total,
            0
          )
        )
      ),
    }
  }

  static normalizeBalance(credits) {
    return {
      apiCredits: Math.max(
        0,
        SpendPolicyGuard.toNumber(
          credits?.apiCredits?.total ?? credits?.total,
          0
        )
      ),
      creatorCredits: Math.max(
        0,
        SpendPolicyGuard.toNumber(credits?.creatorCredits?.total, 0)
      ),
      subscriptionTier:
        credits?.subscription?.tier || credits?.membership || "unknown",
      subscriptionMonthlyLimit: Math.max(
        0,
        SpendPolicyGuard.toNumber(credits?.subscription?.monthlyLimit, 0)
      ),
      subscriptionMonthlyUsed: Math.max(
        0,
        SpendPolicyGuard.toNumber(credits?.subscription?.monthlyUsed, 0)
      ),
      subscriptionMonthlyRemaining: Math.max(
        0,
        SpendPolicyGuard.toNumber(credits?.subscription?.monthlyRemaining, 0)
      ),
    }
  }

  static normalizeMonthlyUsage(analytics) {
    return {
      apiCreditsUsed: Math.max(
        0,
        SpendPolicyGuard.toNumber(analytics?.thisMonth?.apiCreditsUsed, 0)
      ),
      creatorCreditsUsed: Math.max(
        0,
        SpendPolicyGuard.toNumber(analytics?.thisMonth?.creatorCreditsUsed, 0)
      ),
      projectsProcessed: Math.max(
        0,
        SpendPolicyGuard.toNumber(analytics?.thisMonth?.projectsProcessed, 0)
      ),
    }
  }

  static isPaidAction(cost) {
    return (Number(cost?.apiCredits) || 0) > 0 || (Number(cost?.creatorCredits) || 0) > 0
  }

  static buildTriggerMessages(triggerCodes) {
    const messages = []
    for (const code of triggerCodes || []) {
      if (code === "explicit_policy") {
        messages.push("Spend policy requires explicit confirmation.")
      } else if (code === "api_cost_threshold") {
        messages.push("API credit cost exceeds smart confirmation threshold.")
      } else if (code === "creator_cost_threshold") {
        messages.push("Creator Credit cost exceeds smart confirmation threshold.")
      } else if (code === "low_api_balance") {
        messages.push("API balance is low for this spend.")
      } else if (code === "low_creator_balance") {
        messages.push("Creator Credit balance is low for this spend.")
      } else if (code === "auto_api_action_cap") {
        messages.push("Auto-spend API per-action cap exceeded.")
      } else if (code === "auto_creator_action_cap") {
        messages.push("Auto-spend Creator per-action cap exceeded.")
      } else if (code === "auto_api_month_cap") {
        messages.push("Auto-spend API monthly cap would be exceeded.")
      } else if (code === "auto_creator_month_cap") {
        messages.push("Auto-spend Creator monthly cap would be exceeded.")
      }
    }
    return messages
  }

  static buildCostSummary(cost) {
    return {
      apiCredits: Number(cost?.apiCredits) || 0,
      creatorCredits: Number(cost?.creatorCredits) || 0,
    }
  }

  static getNeededCredits(cost, balance) {
    return {
      apiCreditsNeeded: Math.max(
        0,
        (Number(cost?.apiCredits) || 0) - (Number(balance?.apiCredits) || 0)
      ),
      creatorCreditsNeeded: Math.max(
        0,
        (Number(cost?.creatorCredits) || 0) -
          (Number(balance?.creatorCredits) || 0)
      ),
    }
  }

  static buildPurchaseHints(pricing, apiEndpoint, neededCredits = {}) {
    if (!pricing || typeof pricing !== "object") {
      return null
    }

    const links = PurchaseLinks.buildFromPricing(pricing, apiEndpoint)
    const apiRecommended = PurchaseLinks.recommendBundle(
      links.apiCredits,
      neededCredits.apiCreditsNeeded || 1
    )
    const creatorRecommended = PurchaseLinks.recommendBundle(
      links.creatorCredits,
      neededCredits.creatorCreditsNeeded || 1
    )

    return {
      ...links,
      recommended: {
        apiCredits: apiRecommended,
        creatorCredits: creatorRecommended,
      },
    }
  }

  static throwConfirmationRequired(details) {
    throw new StudioApiError(
      "Confirmation required before spending credits. Re-run with confirm_spend: true after user approval.",
      "spend_confirmation_required",
      409,
      details
    )
  }

  static throwInsufficientCredits(details) {
    throw new StudioApiError(
      "Insufficient credits for this action.",
      "insufficient_credits_precheck",
      402,
      details
    )
  }

  static evaluateSmartPolicy(policy, cost, balance) {
    const triggers = []
    if ((Number(cost.apiCredits) || 0) >= Number(policy.smartApiConfirmThreshold)) {
      triggers.push("api_cost_threshold")
    }
    if (
      (Number(cost.creatorCredits) || 0) >=
      Number(policy.smartCreatorConfirmThreshold)
    ) {
      triggers.push("creator_cost_threshold")
    }
    if (
      (Number(cost.apiCredits) || 0) > 0 &&
      (Number(balance.apiCredits) || 0) <= Number(policy.lowApiBalanceThreshold)
    ) {
      triggers.push("low_api_balance")
    }
    if (
      (Number(cost.creatorCredits) || 0) > 0 &&
      (Number(balance.creatorCredits) || 0) <=
        Number(policy.lowCreatorBalanceThreshold)
    ) {
      triggers.push("low_creator_balance")
    }
    return triggers
  }

  static evaluateAutoCaps(policy, cost, monthlyUsage) {
    const triggers = []
    if (
      (Number(cost.apiCredits) || 0) > Number(policy.autoMaxApiPerAction)
    ) {
      triggers.push("auto_api_action_cap")
    }
    if (
      (Number(cost.creatorCredits) || 0) > Number(policy.autoMaxCreatorPerAction)
    ) {
      triggers.push("auto_creator_action_cap")
    }

    if (
      monthlyUsage &&
      (Number(monthlyUsage.apiCreditsUsed) || 0) + (Number(cost.apiCredits) || 0) >
        Number(policy.autoMaxApiPerMonth)
    ) {
      triggers.push("auto_api_month_cap")
    }
    if (
      monthlyUsage &&
      (Number(monthlyUsage.creatorCreditsUsed) || 0) +
        (Number(cost.creatorCredits) || 0) >
        Number(policy.autoMaxCreatorPerMonth)
    ) {
      triggers.push("auto_creator_month_cap")
    }

    return triggers
  }

  static async authorizeAction(context, options) {
    const policy = SpendPolicy.fromContext(context)
    const action = String(options?.action || "paid_action")
    const actionLabel = String(options?.actionLabel || action)
    const confirmSpend = Boolean(options?.confirmSpend)
    const estimatedCost = SpendPolicyGuard.normalizeCost(options?.estimatedCost)

    if (!SpendPolicyGuard.isPaidAction(estimatedCost)) {
      return {
        action,
        actionLabel,
        policy,
        estimatedCost,
        confirmationRequired: false,
        triggers: [],
      }
    }

    const [credits, pricing] = await Promise.all([
      options?.credits || context.apiClient.getCredits(),
      options?.pricing || context.apiClient.getPricing().catch(() => null),
    ])
    const balance = SpendPolicyGuard.normalizeBalance(credits)
    const neededCredits = SpendPolicyGuard.getNeededCredits(estimatedCost, balance)
    const purchaseHints = SpendPolicyGuard.buildPurchaseHints(
      pricing,
      context.apiEndpoint,
      neededCredits
    )

    if (neededCredits.apiCreditsNeeded > 0 || neededCredits.creatorCreditsNeeded > 0) {
      SpendPolicyGuard.throwInsufficientCredits({
        action,
        actionLabel,
        policy: policy.mode,
        estimatedCost: SpendPolicyGuard.buildCostSummary(estimatedCost),
        balance,
        neededCredits,
        purchaseLinks: purchaseHints,
      })
    }

    let monthlyUsage = null
    if (policy.mode === "auto") {
      const analytics =
        options?.analytics ||
        (await context.apiClient.getAnalytics("this_month").catch(() => null))
      monthlyUsage = SpendPolicyGuard.normalizeMonthlyUsage(analytics || {})
    }

    if (confirmSpend) {
      return {
        action,
        actionLabel,
        policy,
        estimatedCost,
        balance,
        monthlyUsage,
        confirmationRequired: false,
        confirmed: true,
        triggers: [],
      }
    }

    const triggers = []
    if (policy.mode === "explicit") {
      triggers.push("explicit_policy")
    } else if (policy.mode === "smart") {
      triggers.push(
        ...SpendPolicyGuard.evaluateSmartPolicy(policy, estimatedCost, balance)
      )
    } else if (policy.mode === "auto") {
      triggers.push(
        ...SpendPolicyGuard.evaluateAutoCaps(policy, estimatedCost, monthlyUsage)
      )
    }

    if (triggers.length > 0) {
      SpendPolicyGuard.throwConfirmationRequired({
        action,
        actionLabel,
        policy: policy.mode,
        estimatedCost: SpendPolicyGuard.buildCostSummary(estimatedCost),
        balance,
        monthlyUsage,
        triggers,
        triggerMessages: SpendPolicyGuard.buildTriggerMessages(triggers),
        purchaseLinks: purchaseHints,
        nextStep:
          "Ask the user for approval and re-run with confirm_spend: true if they agree.",
      })
    }

    return {
      action,
      actionLabel,
      policy,
      estimatedCost,
      balance,
      monthlyUsage,
      confirmationRequired: false,
      confirmed: false,
      triggers,
    }
  }
}
