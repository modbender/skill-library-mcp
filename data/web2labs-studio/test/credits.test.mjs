import test from "node:test"
import assert from "node:assert/strict"
import { CreditsTool } from "../src/tools/credits.mjs"

class FakeApiClient {
  async getCredits() {
    return {
      total: 2,
      hasCredits: true,
      apiCredits: { total: 2 },
      creatorCredits: { total: 18 },
      subscription: {
        tier: "creator",
        monthlyLimit: 100,
        monthlyUsed: 84,
        monthlyRemaining: 16,
      },
    }
  }

  async getPricing() {
    return {
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

  async getAnalytics() {
    return {
      thisMonth: { projectsProcessed: 1, apiCreditsUsed: 12, creatorCreditsUsed: 40 },
    }
  }
}

test("CreditsTool adds upsell alerts and purchase links", async () => {
  const result = await CreditsTool.execute({
    apiClient: new FakeApiClient(),
    apiEndpoint: "https://web2labs.com",
  })

  assert.equal(result.total, 2)
  assert.ok(Array.isArray(result.upsell.alerts))
  assert.ok(result.upsell.alerts.length >= 2)
  assert.equal(result.upsell.purchaseLinks.ref, "openclaw")
  assert.match(
    result.upsell.purchaseLinks.subscriptions.creator,
    /checkout\/subscribe\/creator\?ref=openclaw/i
  )
})

// --- buildAlerts: all 4 alert conditions ---

const mockPurchaseLinks = {
  apiCredits: [
    { id: "casual", credits: 10 },
    { id: "starter", credits: 20 },
  ],
  creatorCredits: [
    { id: "topup_s", credits: 120 },
    { id: "topup_m", credits: 330 },
  ],
}

test("buildAlerts triggers low_api_credits when apiCredits <= 2", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 2 }, creatorCredits: { total: 100 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: { thisMonth: { projectsProcessed: 5 } },
  })
  const match = alerts.find((a) => a.type === "low_api_credits")
  assert.ok(match, "should have low_api_credits alert")
  assert.equal(match.severity, "high")
})

test("buildAlerts does NOT trigger low_api_credits when apiCredits > 2", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 5 }, creatorCredits: { total: 100 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: {},
  })
  assert.ok(!alerts.find((a) => a.type === "low_api_credits"))
})

test("buildAlerts triggers subscription_near_limit when usage >= 80%", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: {
      apiCredits: { total: 10 },
      creatorCredits: { total: 100 },
      subscription: { monthlyLimit: 100, monthlyUsed: 80 },
    },
    purchaseLinks: mockPurchaseLinks,
    analytics: {},
  })
  const match = alerts.find((a) => a.type === "subscription_near_limit")
  assert.ok(match, "should have subscription_near_limit alert")
  assert.equal(match.severity, "medium")
})

test("buildAlerts does NOT trigger subscription_near_limit when usage < 80%", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: {
      apiCredits: { total: 10 },
      creatorCredits: { total: 100 },
      subscription: { monthlyLimit: 100, monthlyUsed: 70 },
    },
    purchaseLinks: mockPurchaseLinks,
    analytics: {},
  })
  assert.ok(!alerts.find((a) => a.type === "subscription_near_limit"))
})

test("buildAlerts triggers first_success_expansion after exactly 1 project", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 10 }, creatorCredits: { total: 100 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: { thisMonth: { projectsProcessed: 1 } },
  })
  const match = alerts.find((a) => a.type === "first_success_expansion")
  assert.ok(match, "should have first_success_expansion alert")
  assert.equal(match.severity, "info")
  assert.ok(match.recommendation, "should recommend a creator credit bundle")
})

test("buildAlerts does NOT trigger first_success_expansion at 0 or 2+ projects", () => {
  for (const count of [0, 2, 5, 10]) {
    const alerts = CreditsTool.buildAlerts({
      credits: { apiCredits: { total: 10 }, creatorCredits: { total: 100 }, subscription: {} },
      purchaseLinks: mockPurchaseLinks,
      analytics: { thisMonth: { projectsProcessed: count } },
    })
    assert.ok(
      !alerts.find((a) => a.type === "first_success_expansion"),
      `should not trigger for ${count} projects`
    )
  }
})

test("buildAlerts triggers low_creator_credits when 0 < creatorCredits <= 20", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 10 }, creatorCredits: { total: 15 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: { thisMonth: { projectsProcessed: 5 } },
  })
  const match = alerts.find((a) => a.type === "low_creator_credits")
  assert.ok(match, "should have low_creator_credits alert")
  assert.equal(match.severity, "medium")
})

test("buildAlerts does NOT trigger low_creator_credits when creatorCredits > 20", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 10 }, creatorCredits: { total: 50 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: {},
  })
  assert.ok(!alerts.find((a) => a.type === "low_creator_credits"))
})

test("buildAlerts does NOT trigger low_creator_credits when creatorCredits is 0", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 10 }, creatorCredits: { total: 0 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: {},
  })
  assert.ok(!alerts.find((a) => a.type === "low_creator_credits"))
})

test("buildAlerts returns empty array when no conditions met", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: {
      apiCredits: { total: 10 },
      creatorCredits: { total: 100 },
      subscription: { monthlyLimit: 100, monthlyUsed: 10 },
    },
    purchaseLinks: mockPurchaseLinks,
    analytics: { thisMonth: { projectsProcessed: 5 } },
  })
  assert.equal(alerts.length, 0)
})

test("buildAlerts handles missing analytics gracefully", () => {
  const alerts = CreditsTool.buildAlerts({
    credits: { apiCredits: { total: 10 }, creatorCredits: { total: 100 }, subscription: {} },
    purchaseLinks: mockPurchaseLinks,
    analytics: null,
  })
  // Should not throw, no first_success alert
  assert.ok(!alerts.find((a) => a.type === "first_success_expansion"))
})

test("CreditsTool.toNumber returns number for valid input", () => {
  assert.equal(CreditsTool.toNumber(42), 42)
  assert.equal(CreditsTool.toNumber("10"), 10)
  assert.equal(CreditsTool.toNumber(0), 0)
})

test("CreditsTool.toNumber returns fallback for invalid input", () => {
  assert.equal(CreditsTool.toNumber("abc", 5), 5)
  assert.equal(CreditsTool.toNumber(undefined, 3), 3)
  assert.equal(CreditsTool.toNumber(Infinity, 0), 0)
})
