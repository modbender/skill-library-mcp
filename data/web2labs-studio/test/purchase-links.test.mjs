import test from "node:test"
import assert from "node:assert/strict"
import { PurchaseLinks } from "../src/lib/purchase-links.mjs"

// --- normalizeBaseUrl ---

test("normalizeBaseUrl returns protocol://host from full URL", () => {
  assert.equal(
    PurchaseLinks.normalizeBaseUrl("https://web2labs.com/some/path"),
    "https://web2labs.com"
  )
})

test("normalizeBaseUrl strips trailing slash", () => {
  assert.equal(
    PurchaseLinks.normalizeBaseUrl("https://web2labs.com/"),
    "https://web2labs.com"
  )
})

test("normalizeBaseUrl preserves port", () => {
  assert.equal(
    PurchaseLinks.normalizeBaseUrl("http://localhost:3000/api"),
    "http://localhost:3000"
  )
})

test("normalizeBaseUrl falls back for empty string", () => {
  assert.equal(PurchaseLinks.normalizeBaseUrl(""), "https://www.web2labs.com")
})

test("normalizeBaseUrl falls back for null", () => {
  assert.equal(PurchaseLinks.normalizeBaseUrl(null), "https://www.web2labs.com")
})

test("normalizeBaseUrl falls back for undefined", () => {
  assert.equal(PurchaseLinks.normalizeBaseUrl(undefined), "https://www.web2labs.com")
})

test("normalizeBaseUrl falls back for invalid URL", () => {
  assert.equal(PurchaseLinks.normalizeBaseUrl("not-a-url"), "https://www.web2labs.com")
})

// --- withTracking ---

test("withTracking appends ref param", () => {
  assert.equal(
    PurchaseLinks.withTracking("https://web2labs.com", "/checkout/credits"),
    "https://web2labs.com/checkout/credits?ref=openclaw"
  )
})

test("withTracking adds leading slash if missing", () => {
  assert.equal(
    PurchaseLinks.withTracking("https://web2labs.com", "checkout/credits"),
    "https://web2labs.com/checkout/credits?ref=openclaw"
  )
})

// --- toNumeric ---

test("toNumeric returns number for valid input", () => {
  assert.equal(PurchaseLinks.toNumeric(42), 42)
  assert.equal(PurchaseLinks.toNumeric("99"), 99)
  assert.equal(PurchaseLinks.toNumeric(0), 0)
})

test("toNumeric returns fallback for NaN", () => {
  assert.equal(PurchaseLinks.toNumeric("abc", 5), 5)
  assert.equal(PurchaseLinks.toNumeric(undefined, 10), 10)
})

test("toNumeric treats null as 0 (Number(null) === 0)", () => {
  assert.equal(PurchaseLinks.toNumeric(null, 7), 0)
})

test("toNumeric returns fallback for Infinity", () => {
  assert.equal(PurchaseLinks.toNumeric(Infinity, 0), 0)
  assert.equal(PurchaseLinks.toNumeric(-Infinity, 0), 0)
})

// --- buildFromPricing ---

test("buildFromPricing maps API and creator bundles with checkout URLs", () => {
  const pricing = {
    apiCreditBundles: [
      { id: "starter", credits: 20, price: 39.99, currency: "EUR" },
    ],
    creatorCreditBundles: [
      { id: "topup_s", credits: 120, price: 9.99, currency: "EUR" },
      { id: "topup_m", credits: 330, price: 24.99, currency: "EUR" },
    ],
  }

  const result = PurchaseLinks.buildFromPricing(pricing, "https://web2labs.com")

  assert.equal(result.ref, "openclaw")
  assert.equal(result.baseUrl, "https://web2labs.com")
  assert.equal(result.apiCredits.length, 1)
  assert.equal(result.apiCredits[0].id, "starter")
  assert.equal(result.apiCredits[0].credits, 20)
  assert.equal(result.apiCredits[0].price, 39.99)
  assert.ok(result.apiCredits[0].checkoutUrl.includes("/checkout/api-credits/starter"))
  assert.ok(result.apiCredits[0].checkoutUrl.includes("ref=openclaw"))

  assert.equal(result.creatorCredits.length, 2)
  assert.equal(result.creatorCredits[0].id, "topup_s")
  assert.ok(result.creatorCredits[0].checkoutUrl.includes("/checkout/creator-credits/topup_s"))

  assert.ok(result.subscriptions.creator.includes("/checkout/subscribe/creator"))
})

test("buildFromPricing handles missing bundles gracefully", () => {
  const result = PurchaseLinks.buildFromPricing({}, "https://web2labs.com")
  assert.equal(result.apiCredits.length, 0)
  assert.equal(result.creatorCredits.length, 0)
})

test("buildFromPricing handles null pricing", () => {
  const result = PurchaseLinks.buildFromPricing(null, "https://web2labs.com")
  assert.equal(result.apiCredits.length, 0)
  assert.equal(result.creatorCredits.length, 0)
})

test("buildFromPricing defaults currency to EUR", () => {
  const pricing = {
    apiCreditBundles: [{ id: "x", credits: 10, price: 5 }],
    creatorCreditBundles: [],
  }
  const result = PurchaseLinks.buildFromPricing(pricing, "https://web2labs.com")
  assert.equal(result.apiCredits[0].currency, "EUR")
})

// --- recommendBundle ---

test("recommendBundle returns smallest bundle that covers needed credits", () => {
  const bundles = [
    { id: "small", credits: 10 },
    { id: "medium", credits: 50 },
    { id: "large", credits: 200 },
  ]
  const rec = PurchaseLinks.recommendBundle(bundles, 30)
  assert.equal(rec.id, "medium")
})

test("recommendBundle returns exact match", () => {
  const bundles = [
    { id: "small", credits: 10 },
    { id: "large", credits: 50 },
  ]
  const rec = PurchaseLinks.recommendBundle(bundles, 10)
  assert.equal(rec.id, "small")
})

test("recommendBundle returns largest when none are big enough", () => {
  const bundles = [
    { id: "small", credits: 5 },
    { id: "medium", credits: 20 },
  ]
  const rec = PurchaseLinks.recommendBundle(bundles, 100)
  assert.equal(rec.id, "medium")
})

test("recommendBundle returns null for empty bundles", () => {
  assert.equal(PurchaseLinks.recommendBundle([], 10), null)
  assert.equal(PurchaseLinks.recommendBundle(null, 10), null)
})

test("recommendBundle clamps needed credits to minimum 1", () => {
  const bundles = [{ id: "tiny", credits: 1 }]
  const rec = PurchaseLinks.recommendBundle(bundles, 0)
  assert.equal(rec.id, "tiny")
})

test("recommendBundle sorts unsorted bundles correctly", () => {
  const bundles = [
    { id: "large", credits: 100 },
    { id: "small", credits: 5 },
    { id: "medium", credits: 30 },
  ]
  const rec = PurchaseLinks.recommendBundle(bundles, 20)
  assert.equal(rec.id, "medium")
})
