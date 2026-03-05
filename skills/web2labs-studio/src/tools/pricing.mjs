import { PurchaseLinks } from "../lib/purchase-links.mjs"

export class PricingTool {
  static async execute(context) {
    const pricing = await context.apiClient.getPricing()
    const purchaseLinks = PurchaseLinks.buildFromPricing(
      pricing,
      context.apiEndpoint
    )
    const recommended = {
      apiCredits:
        PurchaseLinks.recommendBundle(purchaseLinks.apiCredits, 10) || null,
      creatorCredits:
        PurchaseLinks.recommendBundle(purchaseLinks.creatorCredits, 120) || null,
      subscriptionUpgradeUrl: purchaseLinks.subscriptions.creator,
    }

    return {
      ...pricing,
      purchaseLinks,
      recommended,
    }
  }
}
