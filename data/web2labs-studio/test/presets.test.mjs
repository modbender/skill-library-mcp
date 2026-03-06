import test from "node:test"
import assert from "node:assert/strict"
import { PresetCatalog } from "../src/lib/presets.mjs"

test("PresetCatalog resolves known presets", () => {
  const config = PresetCatalog.resolvePreset("youtube")
  assert.equal(config.subtitle, true)
  assert.equal(config.shorts, true)
})

test("PresetCatalog throws for unknown preset", () => {
  assert.throws(() => PresetCatalog.resolvePreset("unknown"))
})

test("PresetCatalog merges nested overrides", () => {
  const base = PresetCatalog.resolvePreset("youtube")
  const merged = PresetCatalog.mergeConfigurations(base, {
    shortsConfig: { amount: 5 },
    musicEnabled: false,
  })

  assert.equal(merged.shortsConfig.amount, 5)
  assert.equal(merged.musicEnabled, false)
  assert.equal(merged.subtitle, true)
})
