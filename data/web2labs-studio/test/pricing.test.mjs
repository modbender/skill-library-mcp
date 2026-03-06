import test from "node:test"
import assert from "node:assert/strict"
import { PricingTool } from "../src/tools/pricing.mjs"

class FakeApiClient {
  async getPricing() {
    return {
      apiProject: { cost: 1, currency: "api_credits" },
      apiCreditBundles: [
        { id: "casual", credits: 10, price: 22.99, currency: "EUR" },
        { id: "starter", credits: 20, price: 39.99, currency: "EUR" },
      ],
      creatorCreditBundles: [
        { id: "topup_s", credits: 120, price: 9.99, currency: "EUR" },
        { id: "topup_m", credits: 330, price: 24.99, currency: "EUR" },
      ],
    }
  }
}

test("PricingTool enriches pricing with purchase links and recommendations", async () => {
  const result = await PricingTool.execute({
    apiClient: new FakeApiClient(),
    apiEndpoint: "https://web2labs.com",
  })

  assert.equal(result.apiProject.cost, 1)
  assert.equal(result.purchaseLinks.ref, "openclaw")
  assert.match(
    result.purchaseLinks.apiCredits[0].checkoutUrl,
    /checkout\/api-credits\/casual\?ref=openclaw/i
  )
  assert.match(
    result.purchaseLinks.creatorCredits[0].checkoutUrl,
    /checkout\/creator-credits\/topup_s\?ref=openclaw/i
  )
  assert.ok(result.recommended.apiCredits)
  assert.ok(result.recommended.creatorCredits)
})
