import { NextSteps } from "../lib/next-steps.mjs"
import { PurchaseLinks } from "../lib/purchase-links.mjs"

export class CreditsTool {
  static toNumber(value, fallback = 0) {
    const n = Number(value)
    if (!Number.isFinite(n)) {
      return fallback
    }
    return n
  }

  static buildAlerts({ credits, purchaseLinks, analytics }) {
    const alerts = []
    const apiCredits = CreditsTool.toNumber(
      credits?.apiCredits?.total ?? credits?.total,
      0
    )
    const creatorCredits = CreditsTool.toNumber(credits?.creatorCredits?.total, 0)

    if (apiCredits <= 2) {
      alerts.push({
        type: "low_api_credits",
        severity: "high",
        message:
          "Heads up: API credits are low. Consider topping up to avoid interrupted uploads.",
        recommendation:
          purchaseLinks?.apiCredits?.find((bundle) => bundle.id === "starter") ||
          purchaseLinks?.apiCredits?.[0] ||
          null,
      })
    }

    const monthlyLimit = CreditsTool.toNumber(credits?.subscription?.monthlyLimit, 0)
    const monthlyUsed = CreditsTool.toNumber(credits?.subscription?.monthlyUsed, 0)
    const usageRatio = monthlyLimit > 0 ? monthlyUsed / monthlyLimit : 0
    if (usageRatio >= 0.8) {
      alerts.push({
        type: "subscription_near_limit",
        severity: "medium",
        message:
          "Subscription usage is above 80% of the monthly limit. API credit bundles can extend capacity.",
        recommendation:
          purchaseLinks?.apiCredits?.find((bundle) => bundle.id === "casual") ||
          purchaseLinks?.apiCredits?.[0] ||
          null,
      })
    }

    const thisMonthProjects = CreditsTool.toNumber(
      analytics?.thisMonth?.projectsProcessed,
      0
    )
    if (thisMonthProjects >= 1 && thisMonthProjects < 2) {
      alerts.push({
        type: "first_success_expansion",
        severity: "info",
        message:
          "First project done. Next-step upgrades: thumbnails, cinematic preset, and brand consistency.",
        recommendation:
          purchaseLinks?.creatorCredits?.find((bundle) => bundle.id === "topup_s") ||
          purchaseLinks?.creatorCredits?.[0] ||
          null,
      })
    }

    if (creatorCredits <= 20 && creatorCredits > 0) {
      alerts.push({
        type: "low_creator_credits",
        severity: "medium",
        message:
          "Creator Credits are getting low. Premium thumbnails and B-roll may fail without a top-up.",
        recommendation:
          purchaseLinks?.creatorCredits?.find((bundle) => bundle.id === "topup_m") ||
          purchaseLinks?.creatorCredits?.[0] ||
          null,
      })
    }

    return alerts
  }

  static async execute(context) {
    const [credits, pricing, analytics] = await Promise.all([
      context.apiClient.getCredits(),
      context.apiClient.getPricing().catch(() => null),
      context.apiClient.getAnalytics("this_month").catch(() => null),
    ])

    const purchaseLinks = pricing
      ? PurchaseLinks.buildFromPricing(pricing, context.apiEndpoint)
      : null
    const alerts = CreditsTool.buildAlerts({
      credits,
      purchaseLinks,
      analytics,
    })

    return {
      ...credits,
      upsell: {
        alerts,
        purchaseLinks,
      },
      next_steps: NextSteps.forCredits(credits),
    }
  }
}
