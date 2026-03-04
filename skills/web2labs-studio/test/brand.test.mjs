import test from "node:test"
import assert from "node:assert/strict"
import { BrandTool } from "../src/tools/brand.mjs"

test("BrandTool get action returns current brand", async () => {
  const context = {
    apiClient: {
      async getBrand() {
        return { primaryColor: "#112233" }
      },
    },
  }

  const result = await BrandTool.execute(context, { action: "get" })
  assert.equal(result.action, "get")
  assert.equal(result.brand.primaryColor, "#112233")
})

test("BrandTool update action normalizes snake_case fields", async () => {
  const calls = []
  const context = {
    apiClient: {
      async updateBrand(payload) {
        calls.push(payload)
        return payload
      },
    },
  }

  const result = await BrandTool.execute(context, {
    action: "update",
    primary_color: "#1a73e8",
    secondary_color: "#ff6f00",
    channel_name: "Web2Labs",
  })

  assert.equal(result.action, "update")
  assert.equal(calls.length, 1)
  assert.equal(calls[0].primaryColor, "#1a73e8")
  assert.equal(calls[0].secondaryColor, "#ff6f00")
  assert.equal(calls[0].channelName, "Web2Labs")
  assert.ok(result.updatedFields.includes("primaryColor"))
})

test("BrandTool update requires at least one field", async () => {
  const context = {
    apiClient: {
      async updateBrand(payload) {
        return payload
      },
    },
  }

  await assert.rejects(
    () => BrandTool.execute(context, { action: "update", updates: {} }),
    /No brand fields were provided/i
  )
})

// --- All 15 snake_case → camelCase field mappings ---

test("normalizeUpdatePayload maps all snake_case aliases to camelCase", () => {
  const input = {
    channel_name: "Test Channel",
    primary_color: "#111111",
    secondary_color: "#222222",
    brand_identity: "Tech reviewer",
    channel_pitch: "Honest reviews",
    posting_plan: [{ platform: "youtube", cadenceUnit: "week", cadenceCount: 2 }],
    scripts_content_category: "tech",
    scripts_channel_about: "Reviews",
    scripts_speaking_style: "casual",
    scripts_viewers_should_feel: "informed",
    scripts_viewers_should_be: "developers",
    subtitle_font_id: "font-1",
    thumbnail_font_id: "font-2",
    default_intro_enabled: true,
    default_outro_enabled: false,
  }

  const result = BrandTool.normalizeUpdatePayload(input)

  assert.equal(result.channelName, "Test Channel")
  assert.equal(result.primaryColor, "#111111")
  assert.equal(result.secondaryColor, "#222222")
  assert.equal(result.brandIdentity, "Tech reviewer")
  assert.equal(result.channelPitch, "Honest reviews")
  assert.deepEqual(result.postingPlan, [{ platform: "youtube", cadenceUnit: "week", cadenceCount: 2 }])
  assert.equal(result.scriptsContentCategory, "tech")
  assert.equal(result.scriptsChannelAbout, "Reviews")
  assert.equal(result.scriptsSpeakingStyle, "casual")
  assert.equal(result.scriptsViewersShouldFeel, "informed")
  assert.equal(result.scriptsViewersShouldBe, "developers")
  assert.equal(result.subtitleFontId, "font-1")
  assert.equal(result.thumbnailFontId, "font-2")
  assert.equal(result.defaultIntroEnabled, true)
  assert.equal(result.defaultOutroEnabled, false)
})

test("normalizeUpdatePayload passes through camelCase keys unchanged", () => {
  const result = BrandTool.normalizeUpdatePayload({
    channelName: "Already Camel",
    primaryColor: "#aabbcc",
  })
  assert.equal(result.channelName, "Already Camel")
  assert.equal(result.primaryColor, "#aabbcc")
})

test("normalizeUpdatePayload skips action and updates keys", () => {
  const result = BrandTool.normalizeUpdatePayload({
    action: "update",
    updates: { foo: "bar" },
    channel_name: "Kept",
  })
  assert.equal(result.action, undefined)
  assert.equal(result.updates, undefined)
  assert.equal(result.channelName, "Kept")
})

// --- resolveRawUpdates ---

test("resolveRawUpdates uses updates object when provided", () => {
  const result = BrandTool.resolveRawUpdates({
    action: "update",
    updates: { primaryColor: "#ff0000" },
    channel_name: "Ignored",
  })
  assert.equal(result.primaryColor, "#ff0000")
  assert.equal(result.channel_name, undefined)
})

test("resolveRawUpdates falls back to params when updates is absent", () => {
  const result = BrandTool.resolveRawUpdates({
    action: "update",
    primary_color: "#00ff00",
    brand_identity: "Creator",
  })
  assert.equal(result.primary_color, "#00ff00")
  assert.equal(result.brand_identity, "Creator")
  assert.equal(result.action, undefined)
})

test("resolveRawUpdates rejects array updates", () => {
  const result = BrandTool.resolveRawUpdates({
    updates: [1, 2, 3],
    primary_color: "#fallback",
  })
  // When updates is an array, it falls back to extracting from params
  assert.equal(result.primary_color, "#fallback")
})

// --- execute edge cases ---

test("BrandTool defaults to get action", async () => {
  const context = {
    apiClient: {
      async getBrand() {
        return { channelName: "Default" }
      },
    },
  }
  const result = await BrandTool.execute(context, {})
  assert.equal(result.action, "get")
})

test("BrandTool rejects invalid action", async () => {
  const context = { apiClient: {} }
  await assert.rejects(
    () => BrandTool.execute(context, { action: "delete" }),
    /action must be "get" or "update"/
  )
})

test("BrandTool update via snake_case params (without updates object)", async () => {
  const calls = []
  const context = {
    apiClient: {
      async updateBrand(payload) {
        calls.push(payload)
        return payload
      },
    },
  }

  const result = await BrandTool.execute(context, {
    action: "update",
    brand_identity: "Gaming channel",
    default_intro_enabled: true,
    subtitle_font_id: "roboto",
  })

  assert.equal(calls[0].brandIdentity, "Gaming channel")
  assert.equal(calls[0].defaultIntroEnabled, true)
  assert.equal(calls[0].subtitleFontId, "roboto")
  assert.ok(result.updatedFields.includes("brandIdentity"))
  assert.ok(result.updatedFields.includes("defaultIntroEnabled"))
  assert.ok(result.updatedFields.includes("subtitleFontId"))
})
