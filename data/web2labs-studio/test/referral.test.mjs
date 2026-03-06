import assert from "node:assert/strict"
import test from "node:test"
import { ReferralTool } from "../src/tools/referral.mjs"

class FakeApiClient {
    constructor() {
        this.lastAppliedCode = null
    }

    async getReferral() {
        return {
            code: "STUDIO-AB7X",
            link: "https://web2labs.com/ref/STUDIO-AB7X",
            stats: {
                totalReferred: 3,
                creditsEarned: 15,
                maxCredits: 50,
                remainingSlots: 7,
            },
        }
    }

    async applyReferralCode(code) {
        this.lastAppliedCode = code
        if (code === "STUDIO-XXXX") {
            return {
                bonusCredits: 5,
                message: "Referral applied! You received 5 bonus API credits.",
            }
        }
        throw new Error("Invalid referral code.")
    }
}

test("ReferralTool 'get' returns referral code and stats", async () => {
    const client = new FakeApiClient()
    const result = await ReferralTool.execute(
        { apiClient: client },
        { action: "get" }
    )

    assert.equal(result.code, "STUDIO-AB7X")
    assert.equal(result.link, "https://web2labs.com/ref/STUDIO-AB7X")
    assert.equal(result.stats.totalReferred, 3)
    assert.equal(result.stats.creditsEarned, 15)
    assert.equal(result.stats.maxCredits, 50)
    assert.equal(result.stats.remainingSlots, 7)
})

test("ReferralTool defaults to 'get' when action is omitted", async () => {
    const client = new FakeApiClient()
    const result = await ReferralTool.execute({ apiClient: client }, {})

    assert.equal(result.code, "STUDIO-AB7X")
})

test("ReferralTool 'apply' calls applyReferralCode with provided code", async () => {
    const client = new FakeApiClient()
    const result = await ReferralTool.execute(
        { apiClient: client },
        { action: "apply", code: "STUDIO-XXXX" }
    )

    assert.equal(client.lastAppliedCode, "STUDIO-XXXX")
    assert.equal(result.bonusCredits, 5)
    assert.ok(result.message.includes("5"))
})

test("ReferralTool 'apply' throws when code is missing", async () => {
    const client = new FakeApiClient()
    await assert.rejects(
        () =>
            ReferralTool.execute(
                { apiClient: client },
                { action: "apply" }
            ),
        { message: /code is required/i }
    )
})

test("ReferralTool 'apply' throws when code is empty string", async () => {
    const client = new FakeApiClient()
    await assert.rejects(
        () =>
            ReferralTool.execute(
                { apiClient: client },
                { action: "apply", code: "   " }
            ),
        { message: /code is required/i }
    )
})

test("ReferralTool rejects invalid action", async () => {
    const client = new FakeApiClient()
    await assert.rejects(
        () =>
            ReferralTool.execute(
                { apiClient: client },
                { action: "invalid" }
            ),
        { message: /invalid action/i }
    )
})

test("ReferralTool 'apply' propagates API errors", async () => {
    const client = new FakeApiClient()
    await assert.rejects(
        () =>
            ReferralTool.execute(
                { apiClient: client },
                { action: "apply", code: "STUDIO-NOPE" }
            ),
        { message: /Invalid referral code/i }
    )
})
