import test from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, rm } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { WatchStore } from "../src/lib/watch-store.mjs"

let tmpPath = null
let originalEnv = null

test("WatchStore setup", async () => {
  tmpPath = await mkdtemp(join(tmpdir(), "w2l-watch-test-"))
  originalEnv = process.env.OPENCLAW_CONFIG_PATH
  process.env.OPENCLAW_CONFIG_PATH = join(tmpPath, "openclaw.json")
})

test("WatchStore.load returns empty array when no file exists", async () => {
  const watchers = await WatchStore.load()
  assert.deepEqual(watchers, [])
})

test("WatchStore.add creates and persists a watcher", async () => {
  const watcher = await WatchStore.add({
    url: "https://youtube.com/@testchannel",
    preset: "youtube",
  })

  assert.ok(watcher.id.startsWith("w_"))
  assert.equal(watcher.url, "https://youtube.com/@testchannel")
  assert.equal(watcher.type, "youtube_channel")
  assert.equal(watcher.label, "testchannel")
  assert.equal(watcher.preset, "youtube")
  assert.equal(watcher.enabled, true)
  assert.equal(watcher.lastChecked, null)
  assert.deepEqual(watcher.lastProcessedIds, [])
  assert.equal(watcher.pollIntervalMinutes, 30)
  assert.equal(watcher.maxDurationMinutes, 120)
  assert.equal(watcher.maxDailyUploads, 5)
})

test("WatchStore.list returns persisted watchers", async () => {
  const watchers = await WatchStore.list()
  assert.equal(watchers.length, 1)
  assert.equal(watchers[0].url, "https://youtube.com/@testchannel")
})

test("WatchStore.get returns a watcher by ID", async () => {
  const watchers = await WatchStore.list()
  const watcher = await WatchStore.get(watchers[0].id)
  assert.ok(watcher)
  assert.equal(watcher.url, "https://youtube.com/@testchannel")
})

test("WatchStore.get returns null for unknown ID", async () => {
  const result = await WatchStore.get("w_nonexistent")
  assert.equal(result, null)
})

test("WatchStore.update modifies a watcher", async () => {
  const watchers = await WatchStore.list()
  const updated = await WatchStore.update(watchers[0].id, { enabled: false })
  assert.equal(updated.enabled, false)

  const reloaded = await WatchStore.get(watchers[0].id)
  assert.equal(reloaded.enabled, false)
})

test("WatchStore.update returns null for unknown ID", async () => {
  const result = await WatchStore.update("w_nonexistent", { enabled: false })
  assert.equal(result, null)
})

test("WatchStore.remove deletes a watcher", async () => {
  const watchers = await WatchStore.list()
  const id = watchers[0].id
  const removed = await WatchStore.remove(id)
  assert.equal(removed, true)

  const remaining = await WatchStore.list()
  assert.equal(remaining.length, 0)
})

test("WatchStore.remove returns false for unknown ID", async () => {
  const removed = await WatchStore.remove("w_nonexistent")
  assert.equal(removed, false)
})

test("WatchStore.generateId produces unique IDs", () => {
  const ids = new Set()
  for (let i = 0; i < 100; i++) {
    ids.add(WatchStore.generateId())
  }
  assert.equal(ids.size, 100)
})

test("WatchStore.markProcessed tracks video IDs and updates timestamp", async () => {
  const watcher = await WatchStore.add({
    url: "https://youtube.com/@marktest",
  })

  const updated = await WatchStore.markProcessed(watcher.id, ["vid1", "vid2"])
  assert.deepEqual(updated.lastProcessedIds, ["vid1", "vid2"])
  assert.ok(updated.lastChecked)
  assert.equal(updated.uploadsToday, 2)
})

test("WatchStore.markProcessed caps lastProcessedIds at 500", async () => {
  const watchers = await WatchStore.list()
  const watcher = watchers.find((w) => w.label === "marktest")

  const manyIds = Array.from({ length: 520 }, (_, i) => `batch_${i}`)
  const updated = await WatchStore.markProcessed(watcher.id, manyIds)
  assert.equal(updated.lastProcessedIds.length, 500)
  assert.equal(updated.lastProcessedIds[499], "batch_519")
})

test("WatchStore.filterNewVideos excludes processed IDs", () => {
  const watcher = {
    lastProcessedIds: ["a", "b", "c"],
    maxDurationMinutes: 120,
  }
  const videos = [
    { id: "a", title: "Old", duration: 60 },
    { id: "d", title: "New", duration: 60 },
    { id: "e", title: "Also new", duration: 60 },
  ]

  const result = WatchStore.filterNewVideos(watcher, videos)
  assert.equal(result.length, 2)
  assert.equal(result[0].id, "d")
  assert.equal(result[1].id, "e")
})

test("WatchStore.filterNewVideos excludes videos exceeding max duration", () => {
  const watcher = {
    lastProcessedIds: [],
    maxDurationMinutes: 10,
  }
  const videos = [
    { id: "short", title: "Short", duration: 300 },
    { id: "long", title: "Long", duration: 900 },
  ]

  const result = WatchStore.filterNewVideos(watcher, videos)
  assert.equal(result.length, 1)
  assert.equal(result[0].id, "short")
})

test("WatchStore.getUploadsToday resets on new day", () => {
  const watcher = {
    uploadsToday: 5,
    uploadsTodayDate: "2020-01-01",
    maxDailyUploads: 5,
  }
  assert.equal(WatchStore.getUploadsToday(watcher), 0)
})

test("WatchStore.getUploadsToday returns count for current day", () => {
  const today = new Date().toISOString().slice(0, 10)
  const watcher = {
    uploadsToday: 3,
    uploadsTodayDate: today,
    maxDailyUploads: 5,
  }
  assert.equal(WatchStore.getUploadsToday(watcher), 3)
})

test("WatchStore.getRemainingUploads calculates correctly", () => {
  const today = new Date().toISOString().slice(0, 10)
  const watcher = {
    uploadsToday: 3,
    uploadsTodayDate: today,
    maxDailyUploads: 5,
  }
  assert.equal(WatchStore.getRemainingUploads(watcher), 2)
})

test("WatchStore.isChannelUrl accepts channel URLs", () => {
  assert.equal(WatchStore.isChannelUrl("https://youtube.com/@mkbhd"), true)
  assert.equal(WatchStore.isChannelUrl("https://www.youtube.com/c/mkbhd"), true)
  assert.equal(WatchStore.isChannelUrl("https://www.youtube.com/channel/UC123"), true)
  assert.equal(WatchStore.isChannelUrl("https://www.twitch.tv/shroud"), true)
})

test("WatchStore.isChannelUrl rejects single video URLs", () => {
  assert.equal(WatchStore.isChannelUrl("https://youtube.com/watch?v=abc123"), false)
  assert.equal(WatchStore.isChannelUrl("https://youtu.be/abc123"), false)
})

test("WatchStore.normalizeType detects twitch", () => {
  assert.equal(WatchStore.normalizeType("https://twitch.tv/shroud"), "twitch_channel")
  assert.equal(WatchStore.normalizeType("https://youtube.com/@test"), "youtube_channel")
})

test("WatchStore.deriveLabel extracts channel name", () => {
  assert.equal(WatchStore.deriveLabel("https://youtube.com/@mkbhd"), "mkbhd")
  assert.equal(WatchStore.deriveLabel("https://youtube.com/c/LinusTechTips"), "LinusTechTips")
  assert.equal(WatchStore.deriveLabel("https://twitch.tv/shroud"), "shroud")
})

test("WatchStore.createWatcher clamps values", () => {
  const w = WatchStore.createWatcher({
    url: "https://youtube.com/@test",
    pollIntervalMinutes: 1,
    maxDurationMinutes: 9999,
    maxDailyUploads: -5,
  })
  assert.equal(w.pollIntervalMinutes, 5)
  assert.equal(w.maxDurationMinutes, 720)
  assert.equal(w.maxDailyUploads, 1)
})

test("WatchStore cleanup", async () => {
  if (originalEnv === undefined) delete process.env.OPENCLAW_CONFIG_PATH
  else process.env.OPENCLAW_CONFIG_PATH = originalEnv
  if (tmpPath) await rm(tmpPath, { recursive: true, force: true })
})
