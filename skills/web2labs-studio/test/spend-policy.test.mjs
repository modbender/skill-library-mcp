import test from "node:test"
import assert from "node:assert/strict"
import { SpendPolicy, SpendPolicyGuard } from "../src/lib/spend-policy.mjs"

// ===================== SpendPolicy =====================

// --- normalizeMode ---

test("SpendPolicy.normalizeMode returns valid modes", () => {
  assert.equal(SpendPolicy.normalizeMode("explicit"), "explicit")
  assert.equal(SpendPolicy.normalizeMode("smart"), "smart")
  assert.equal(SpendPolicy.normalizeMode("auto"), "auto")
})

test("SpendPolicy.normalizeMode is case-insensitive", () => {
  assert.equal(SpendPolicy.normalizeMode("EXPLICIT"), "explicit")
  assert.equal(SpendPolicy.normalizeMode("Smart"), "smart")
})

test("SpendPolicy.normalizeMode defaults to auto for invalid values", () => {
  assert.equal(SpendPolicy.normalizeMode("invalid"), "auto")
  assert.equal(SpendPolicy.normalizeMode(""), "auto")
  assert.equal(SpendPolicy.normalizeMode(null), "auto")
  assert.equal(SpendPolicy.normalizeMode(undefined), "auto")
})

// --- toNumber ---

test("SpendPolicy.toNumber returns number for valid input with explicit bounds", () => {
  assert.equal(SpendPolicy.toNumber(42, 0, 1, 100), 42)
  assert.equal(SpendPolicy.toNumber("10", 0, 1, 1000), 10)
  assert.equal(SpendPolicy.toNumber(0, 5, 0, 100), 0)
})

test("SpendPolicy.toNumber returns fallback for invalid input", () => {
  assert.equal(SpendPolicy.toNumber("abc", 7, 1, 20), 7)
  assert.equal(SpendPolicy.toNumber(undefined, 3, 1, 100), 3)
  assert.equal(SpendPolicy.toNumber(NaN, 99, 1, 1000), 99)
  assert.equal(SpendPolicy.toNumber(Infinity, 1, 0, 100), 1)
})

test("SpendPolicy.toNumber clamps to min", () => {
  assert.equal(SpendPolicy.toNumber(-5, 0, 0, 100), 0)
  assert.equal(SpendPolicy.toNumber(3, 0, 5, 100), 5)
})

test("SpendPolicy.toNumber clamps to max", () => {
  assert.equal(SpendPolicy.toNumber(100, 0, null, 50), 50)
  assert.equal(SpendPolicy.toNumber(999, 0, 1, 20), 20)
})

test("SpendPolicy.toNumber clamps to both min and max", () => {
  assert.equal(SpendPolicy.toNumber(0, 5, 1, 100), 1)
  assert.equal(SpendPolicy.toNumber(200, 5, 1, 100), 100)
  assert.equal(SpendPolicy.toNumber(50, 5, 1, 100), 50)
})

// --- fromEnvironment ---

test("SpendPolicy.fromEnvironment reads all env vars", () => {
  const env = {
    WEB2LABS_SPEND_POLICY: "explicit",
    WEB2LABS_SMART_CONFIRM_API_THRESHOLD: "5",
    WEB2LABS_SMART_CONFIRM_CREATOR_THRESHOLD: "20",
    WEB2LABS_SMART_CONFIRM_LOW_API_BALANCE: "3",
    WEB2LABS_SMART_CONFIRM_LOW_CREATOR_BALANCE: "50",
    WEB2LABS_AUTO_SPEND_MAX_API_PER_ACTION: "4",
    WEB2LABS_AUTO_SPEND_MAX_CREATOR_PER_ACTION: "80",
    WEB2LABS_AUTO_SPEND_MAX_API_PER_MONTH: "100",
    WEB2LABS_AUTO_SPEND_MAX_CREATOR_PER_MONTH: "500",
  }

  const policy = SpendPolicy.fromEnvironment(env)
  assert.equal(policy.mode, "explicit")
  assert.equal(policy.smartApiConfirmThreshold, 5)
  assert.equal(policy.smartCreatorConfirmThreshold, 20)
  assert.equal(policy.lowApiBalanceThreshold, 3)
  assert.equal(policy.lowCreatorBalanceThreshold, 50)
  assert.equal(policy.autoMaxApiPerAction, 4)
  assert.equal(policy.autoMaxCreatorPerAction, 80)
  assert.equal(policy.autoMaxApiPerMonth, 100)
  assert.equal(policy.autoMaxCreatorPerMonth, 500)
})

test("SpendPolicy.fromEnvironment uses defaults for empty env", () => {
  const policy = SpendPolicy.fromEnvironment({})
  assert.equal(policy.mode, "auto")
  assert.equal(policy.smartApiConfirmThreshold, 2)
  assert.equal(policy.smartCreatorConfirmThreshold, 8)
  assert.equal(policy.lowApiBalanceThreshold, 2)
  assert.equal(policy.lowCreatorBalanceThreshold, 20)
  assert.equal(policy.autoMaxApiPerAction, 2)
  assert.equal(policy.autoMaxCreatorPerAction, 40)
  assert.equal(policy.autoMaxApiPerMonth, 80)
  assert.equal(policy.autoMaxCreatorPerMonth, 400)
})

// --- fromContext ---

test("SpendPolicy.fromContext reads from context object", () => {
  const ctx = {
    spendPolicy: { mode: "auto", autoMaxApiPerAction: 10 },
  }
  const policy = SpendPolicy.fromContext(ctx)
  assert.equal(policy.mode, "auto")
  assert.equal(policy.autoMaxApiPerAction, 10)
})

test("SpendPolicy.fromContext falls back to env when context has no spendPolicy", () => {
  const policy = SpendPolicy.fromContext({})
  assert.equal(policy.mode, "auto") // default
})

// ===================== SpendPolicyGuard =====================

// --- normalizeCost ---

test("SpendPolicyGuard.normalizeCost normalizes cost from various shapes", () => {
  assert.deepEqual(
    SpendPolicyGuard.normalizeCost({ apiCredits: 2, creatorCredits: 10 }),
    { apiCredits: 2, creatorCredits: 10 }
  )

  assert.deepEqual(
    SpendPolicyGuard.normalizeCost({ totalCost: { apiCredits: 3, creatorCredits: 5 } }),
    { apiCredits: 3, creatorCredits: 5 }
  )

  assert.deepEqual(
    SpendPolicyGuard.normalizeCost(null),
    { apiCredits: 0, creatorCredits: 0 }
  )
})

test("SpendPolicyGuard.normalizeCost clamps negatives to 0", () => {
  const result = SpendPolicyGuard.normalizeCost({ apiCredits: -5, creatorCredits: -10 })
  assert.equal(result.apiCredits, 0)
  assert.equal(result.creatorCredits, 0)
})

test("SpendPolicyGuard.normalizeCost rounds to integers", () => {
  const result = SpendPolicyGuard.normalizeCost({ apiCredits: 1.7, creatorCredits: 3.3 })
  assert.equal(result.apiCredits, 2)
  assert.equal(result.creatorCredits, 3)
})

// --- normalizeBalance ---

test("SpendPolicyGuard.normalizeBalance extracts all balance fields", () => {
  const credits = {
    apiCredits: { total: 10 },
    creatorCredits: { total: 50 },
    subscription: {
      tier: "creator",
      monthlyLimit: 100,
      monthlyUsed: 20,
      monthlyRemaining: 80,
    },
  }
  const balance = SpendPolicyGuard.normalizeBalance(credits)
  assert.equal(balance.apiCredits, 10)
  assert.equal(balance.creatorCredits, 50)
  assert.equal(balance.subscriptionTier, "creator")
  assert.equal(balance.subscriptionMonthlyLimit, 100)
  assert.equal(balance.subscriptionMonthlyUsed, 20)
  assert.equal(balance.subscriptionMonthlyRemaining, 80)
})

test("SpendPolicyGuard.normalizeBalance defaults to 0 for missing data", () => {
  const balance = SpendPolicyGuard.normalizeBalance({})
  assert.equal(balance.apiCredits, 0)
  assert.equal(balance.creatorCredits, 0)
  assert.equal(balance.subscriptionTier, "unknown")
  assert.equal(balance.subscriptionMonthlyLimit, 0)
})

// --- isPaidAction ---

test("SpendPolicyGuard.isPaidAction returns true when credits are needed", () => {
  assert.equal(SpendPolicyGuard.isPaidAction({ apiCredits: 1, creatorCredits: 0 }), true)
  assert.equal(SpendPolicyGuard.isPaidAction({ apiCredits: 0, creatorCredits: 5 }), true)
  assert.equal(SpendPolicyGuard.isPaidAction({ apiCredits: 2, creatorCredits: 8 }), true)
})

test("SpendPolicyGuard.isPaidAction returns false for free actions", () => {
  assert.equal(SpendPolicyGuard.isPaidAction({ apiCredits: 0, creatorCredits: 0 }), false)
  assert.equal(SpendPolicyGuard.isPaidAction(null), false)
  assert.equal(SpendPolicyGuard.isPaidAction({}), false)
})

// --- normalizeMonthlyUsage ---

test("SpendPolicyGuard.normalizeMonthlyUsage extracts usage fields", () => {
  const analytics = {
    thisMonth: {
      apiCreditsUsed: 10,
      creatorCreditsUsed: 30,
      projectsProcessed: 5,
    },
  }
  const usage = SpendPolicyGuard.normalizeMonthlyUsage(analytics)
  assert.equal(usage.apiCreditsUsed, 10)
  assert.equal(usage.creatorCreditsUsed, 30)
  assert.equal(usage.projectsProcessed, 5)
})

test("SpendPolicyGuard.normalizeMonthlyUsage defaults missing fields", () => {
  const usage = SpendPolicyGuard.normalizeMonthlyUsage({})
  assert.equal(usage.apiCreditsUsed, 0)
  assert.equal(usage.creatorCreditsUsed, 0)
  assert.equal(usage.projectsProcessed, 0)
})

// --- getNeededCredits ---

test("SpendPolicyGuard.getNeededCredits calculates deficit", () => {
  const needed = SpendPolicyGuard.getNeededCredits(
    { apiCredits: 5, creatorCredits: 30 },
    { apiCredits: 3, creatorCredits: 50 }
  )
  assert.equal(needed.apiCreditsNeeded, 2)
  assert.equal(needed.creatorCreditsNeeded, 0)
})

test("SpendPolicyGuard.getNeededCredits returns 0 when balance covers cost", () => {
  const needed = SpendPolicyGuard.getNeededCredits(
    { apiCredits: 1, creatorCredits: 10 },
    { apiCredits: 10, creatorCredits: 100 }
  )
  assert.equal(needed.apiCreditsNeeded, 0)
  assert.equal(needed.creatorCreditsNeeded, 0)
})

// --- evaluateSmartPolicy ---

test("evaluateSmartPolicy triggers on high API cost", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateSmartPolicy(
    policy,
    { apiCredits: 3, creatorCredits: 0 },
    { apiCredits: 10, creatorCredits: 100 }
  )
  assert.ok(triggers.includes("api_cost_threshold"))
})

test("evaluateSmartPolicy triggers on high creator cost", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateSmartPolicy(
    policy,
    { apiCredits: 0, creatorCredits: 10 },
    { apiCredits: 10, creatorCredits: 100 }
  )
  assert.ok(triggers.includes("creator_cost_threshold"))
})

test("evaluateSmartPolicy triggers on low API balance", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateSmartPolicy(
    policy,
    { apiCredits: 1, creatorCredits: 0 },
    { apiCredits: 1, creatorCredits: 100 }
  )
  assert.ok(triggers.includes("low_api_balance"))
})

test("evaluateSmartPolicy triggers on low creator balance", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateSmartPolicy(
    policy,
    { apiCredits: 0, creatorCredits: 1 },
    { apiCredits: 10, creatorCredits: 10 }
  )
  assert.ok(triggers.includes("low_creator_balance"))
})

test("evaluateSmartPolicy returns no triggers for small cost and healthy balance", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateSmartPolicy(
    policy,
    { apiCredits: 1, creatorCredits: 0 },
    { apiCredits: 10, creatorCredits: 100 }
  )
  assert.equal(triggers.length, 0)
})

// --- evaluateAutoCaps ---

test("evaluateAutoCaps triggers on API per-action cap", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateAutoCaps(
    policy,
    { apiCredits: 5, creatorCredits: 0 },
    { apiCreditsUsed: 0, creatorCreditsUsed: 0 }
  )
  assert.ok(triggers.includes("auto_api_action_cap"))
})

test("evaluateAutoCaps triggers on creator per-action cap", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateAutoCaps(
    policy,
    { apiCredits: 0, creatorCredits: 100 },
    { apiCreditsUsed: 0, creatorCreditsUsed: 0 }
  )
  assert.ok(triggers.includes("auto_creator_action_cap"))
})

test("evaluateAutoCaps triggers on API monthly cap", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateAutoCaps(
    policy,
    { apiCredits: 1, creatorCredits: 0 },
    { apiCreditsUsed: 80, creatorCreditsUsed: 0 }
  )
  assert.ok(triggers.includes("auto_api_month_cap"))
})

test("evaluateAutoCaps triggers on creator monthly cap", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateAutoCaps(
    policy,
    { apiCredits: 0, creatorCredits: 10 },
    { apiCreditsUsed: 0, creatorCreditsUsed: 395 }
  )
  assert.ok(triggers.includes("auto_creator_month_cap"))
})

test("evaluateAutoCaps returns no triggers within all caps", () => {
  const policy = SpendPolicy.fromEnvironment({})
  const triggers = SpendPolicyGuard.evaluateAutoCaps(
    policy,
    { apiCredits: 1, creatorCredits: 5 },
    { apiCreditsUsed: 2, creatorCreditsUsed: 10 }
  )
  assert.equal(triggers.length, 0)
})

// --- buildTriggerMessages ---

test("buildTriggerMessages maps all known trigger codes", () => {
  const allCodes = [
    "explicit_policy",
    "api_cost_threshold",
    "creator_cost_threshold",
    "low_api_balance",
    "low_creator_balance",
    "auto_api_action_cap",
    "auto_creator_action_cap",
    "auto_api_month_cap",
    "auto_creator_month_cap",
  ]
  const messages = SpendPolicyGuard.buildTriggerMessages(allCodes)
  assert.equal(messages.length, allCodes.length)
  for (const msg of messages) {
    assert.ok(typeof msg === "string" && msg.length > 0)
  }
})

test("buildTriggerMessages returns empty array for no triggers", () => {
  assert.deepEqual(SpendPolicyGuard.buildTriggerMessages([]), [])
  assert.deepEqual(SpendPolicyGuard.buildTriggerMessages(null), [])
})

// --- authorizeAction (integration of above) ---

function makeMockContext(policyMode = "smart") {
  return {
    apiClient: {
      getCredits: async () => ({
        total: 10,
        apiCredits: { total: 10 },
        creatorCredits: { total: 200 },
        subscription: { tier: "creator", monthlyLimit: 100, monthlyUsed: 10 },
      }),
      getPricing: async () => ({
        apiCreditBundles: [{ id: "starter", credits: 20, price: 39.99 }],
        creatorCreditBundles: [{ id: "topup_s", credits: 120, price: 9.99 }],
      }),
      getAnalytics: async () => ({
        thisMonth: { apiCreditsUsed: 4, creatorCreditsUsed: 24, projectsProcessed: 4 },
      }),
    },
    apiEndpoint: "https://web2labs.com",
    spendPolicy: { mode: policyMode },
  }
}

test("authorizeAction passes free actions without checks", async () => {
  const ctx = makeMockContext("explicit")
  const result = await SpendPolicyGuard.authorizeAction(ctx, {
    action: "free_thing",
    estimatedCost: { apiCredits: 0, creatorCredits: 0 },
  })
  assert.equal(result.confirmationRequired, false)
})

test("authorizeAction explicit mode requires confirmation for paid actions", async () => {
  const ctx = makeMockContext("explicit")
  await assert.rejects(
    () =>
      SpendPolicyGuard.authorizeAction(ctx, {
        action: "upload",
        estimatedCost: { apiCredits: 1 },
      }),
    /confirmation required/i
  )
})

test("authorizeAction explicit mode allows with confirmSpend=true", async () => {
  const ctx = makeMockContext("explicit")
  const result = await SpendPolicyGuard.authorizeAction(ctx, {
    action: "upload",
    estimatedCost: { apiCredits: 1 },
    confirmSpend: true,
  })
  assert.equal(result.confirmationRequired, false)
  assert.equal(result.confirmed, true)
})

test("authorizeAction smart mode passes low-cost actions", async () => {
  const ctx = makeMockContext("smart")
  const result = await SpendPolicyGuard.authorizeAction(ctx, {
    action: "upload",
    estimatedCost: { apiCredits: 1, creatorCredits: 0 },
  })
  assert.equal(result.confirmationRequired, false)
})

test("authorizeAction smart mode requires confirmation for rush", async () => {
  const ctx = makeMockContext("smart")
  await assert.rejects(
    () =>
      SpendPolicyGuard.authorizeAction(ctx, {
        action: "upload",
        estimatedCost: { apiCredits: 2, creatorCredits: 0 },
      }),
    /confirmation required/i
  )
})

test("authorizeAction auto mode passes within caps", async () => {
  const ctx = makeMockContext("auto")
  const result = await SpendPolicyGuard.authorizeAction(ctx, {
    action: "upload",
    estimatedCost: { apiCredits: 1, creatorCredits: 5 },
  })
  assert.equal(result.confirmationRequired, false)
})

test("authorizeAction auto mode requires confirmation when per-action cap exceeded", async () => {
  const ctx = makeMockContext("auto")
  await assert.rejects(
    () =>
      SpendPolicyGuard.authorizeAction(ctx, {
        action: "upload",
        estimatedCost: { apiCredits: 5, creatorCredits: 0 },
      }),
    /confirmation required/i
  )
})

test("authorizeAction throws insufficient credits when balance too low", async () => {
  const ctx = makeMockContext("smart")
  ctx.apiClient.getCredits = async () => ({
    total: 0,
    apiCredits: { total: 0 },
    creatorCredits: { total: 0 },
    subscription: { tier: "free" },
  })
  await assert.rejects(
    () =>
      SpendPolicyGuard.authorizeAction(ctx, {
        action: "upload",
        estimatedCost: { apiCredits: 1, creatorCredits: 0 },
      }),
    /insufficient credits/i
  )
})
