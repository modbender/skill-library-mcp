import test from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, rm } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { WatchTool } from "../src/tools/watch.mjs"
import { WatchStore } from "../src/lib/watch-store.mjs"
import { VideoDownloader } from "../src/lib/downloader.mjs"

let tmpPath = null
let originalEnv = null

function makeMockContext(overrides = {}) {
  return {
    apiClient: {
      uploadProject: async () => ({ projectId: "p_mock", status: "Uploading" }),
      getCredits: async () => ({ apiCredits: { total: 10 }, creatorCredits: { total: 100 } }),
      getPricing: async () => ({}),
      getAnalytics: async () => ({}),
    },
    apiEndpoint: "https://web2labs.com",
    defaultPreset: "youtube",
    spendPolicy: { mode: "auto" },
    ...overrides,
  }
}

test("WatchTool setup", async () => {
  tmpPath = await mkdtemp(join(tmpdir(), "w2l-watch-tool-test-"))
  originalEnv = process.env.OPENCLAW_CONFIG_PATH
  process.env.OPENCLAW_CONFIG_PATH = join(tmpPath, "openclaw.json")
})

test("WatchTool add requires url", async () => {
  const ctx = makeMockContext()
  await assert.rejects(
    () => WatchTool.execute(ctx, { action: "add" }),
    /url is required/
  )
})

test("WatchTool add rejects unsupported URLs", async () => {
  const ctx = makeMockContext()
  await assert.rejects(
    () => WatchTool.execute(ctx, { action: "add", url: "https://example.com/video" }),
    /Unsupported URL/
  )
})

test("WatchTool add rejects single video URLs", async () => {
  const ctx = makeMockContext()

  const originalCheck = VideoDownloader.checkYtDlp
  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })

  try {
    await assert.rejects(
      () => WatchTool.execute(ctx, { action: "add", url: "https://youtube.com/watch?v=abc123" }),
      /channel or user URL/
    )
  } finally {
    VideoDownloader.checkYtDlp = originalCheck
  }
})

test("WatchTool add succeeds with valid channel URL", async () => {
  const ctx = makeMockContext()

  const originalCheck = VideoDownloader.checkYtDlp
  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })

  try {
    const result = await WatchTool.execute(ctx, {
      action: "add",
      url: "https://youtube.com/@testcreator",
      preset: "youtube",
      max_duration_minutes: 60,
      max_daily_uploads: 3,
    })

    assert.equal(result.action, "add")
    assert.ok(result.watcher.id.startsWith("w_"))
    assert.equal(result.watcher.label, "testcreator")
    assert.equal(result.watcher.maxDurationMinutes, 60)
    assert.equal(result.watcher.maxDailyUploads, 3)
    assert.ok(result.warning)
  } finally {
    VideoDownloader.checkYtDlp = originalCheck
  }
})

test("WatchTool list returns watchers", async () => {
  const ctx = makeMockContext()
  const result = await WatchTool.execute(ctx, { action: "list" })

  assert.equal(result.action, "list")
  assert.ok(result.count >= 1)
  assert.ok(Array.isArray(result.watchers))
})

test("WatchTool status returns watcher details", async () => {
  const watchers = await WatchStore.list()
  const id = watchers[0].id
  const ctx = makeMockContext()

  const result = await WatchTool.execute(ctx, { action: "status", id })
  assert.equal(result.action, "status")
  assert.equal(result.watcher.id, id)
  assert.ok("remainingUploads" in result.watcher)
})

test("WatchTool status requires id", async () => {
  const ctx = makeMockContext()
  await assert.rejects(
    () => WatchTool.execute(ctx, { action: "status" }),
    /id is required/
  )
})

test("WatchTool pause disables a watcher", async () => {
  const watchers = await WatchStore.list()
  const id = watchers[0].id
  const ctx = makeMockContext()

  const result = await WatchTool.execute(ctx, { action: "pause", id })
  assert.equal(result.action, "pause")
  assert.equal(result.enabled, false)
})

test("WatchTool resume enables a watcher", async () => {
  const watchers = await WatchStore.list()
  const id = watchers[0].id
  const ctx = makeMockContext()

  const result = await WatchTool.execute(ctx, { action: "resume", id })
  assert.equal(result.action, "resume")
  assert.equal(result.enabled, true)
})

test("WatchTool check with no enabled watchers returns empty", async () => {
  const ctx = makeMockContext()

  const originalCheck = VideoDownloader.checkYtDlp
  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })

  const watchers = await WatchStore.list()
  for (const w of watchers) {
    await WatchStore.update(w.id, { enabled: false })
  }

  try {
    const result = await WatchTool.execute(ctx, { action: "check" })
    assert.equal(result.action, "check")
    assert.equal(result.processed, 0)
  } finally {
    for (const w of watchers) {
      await WatchStore.update(w.id, { enabled: true })
    }
    VideoDownloader.checkYtDlp = originalCheck
  }
})

test("WatchTool check skips watcher at daily cap", async () => {
  const ctx = makeMockContext()
  const watchers = await WatchStore.list()
  const watcher = watchers[0]

  const originalCheck = VideoDownloader.checkYtDlp
  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })

  const today = new Date().toISOString().slice(0, 10)
  await WatchStore.update(watcher.id, {
    uploadsToday: watcher.maxDailyUploads,
    uploadsTodayDate: today,
  })

  try {
    const result = await WatchTool.execute(ctx, { action: "check", id: watcher.id })
    assert.equal(result.results[0].skipped, true)
    assert.equal(result.results[0].reason, "daily_upload_cap_reached")
  } finally {
    await WatchStore.update(watcher.id, { uploadsToday: 0, uploadsTodayDate: null })
    VideoDownloader.checkYtDlp = originalCheck
  }
})

test("WatchTool check processes new videos", async () => {
  const ctx = makeMockContext()
  const watchers = await WatchStore.list()
  const watcher = watchers[0]

  const originalCheck = VideoDownloader.checkYtDlp
  const originalList = VideoDownloader.listChannelVods
  const originalDownload = VideoDownloader.download
  const originalCleanup = VideoDownloader.cleanup

  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })
  VideoDownloader.listChannelVods = async () => [
    { id: "new_vid_1", title: "New Video 1", date: "20260222", duration: 300 },
    { id: "new_vid_2", title: "New Video 2", date: "20260222", duration: 600 },
  ]
  VideoDownloader.download = async () => ({
    filePath: "/tmp/fake.mp4",
    tmpDir: "/tmp/fake-dir",
    fileSize: 1000,
    fileName: "fake.mp4",
  })
  VideoDownloader.cleanup = async () => {}

  try {
    const result = await WatchTool.execute(ctx, { action: "check", id: watcher.id })
    assert.equal(result.action, "check")
    assert.equal(result.totalUploaded, 2)
    assert.equal(result.results[0].uploaded, 2)
    assert.equal(result.results[0].uploads[0].projectId, "p_mock")

    const updated = await WatchStore.get(watcher.id)
    assert.ok(updated.lastProcessedIds.includes("new_vid_1"))
    assert.ok(updated.lastProcessedIds.includes("new_vid_2"))
  } finally {
    VideoDownloader.checkYtDlp = originalCheck
    VideoDownloader.listChannelVods = originalList
    VideoDownloader.download = originalDownload
    VideoDownloader.cleanup = originalCleanup
  }
})

test("WatchTool check skips already-processed videos", async () => {
  const ctx = makeMockContext()
  const watchers = await WatchStore.list()
  const watcher = watchers[0]

  const originalCheck = VideoDownloader.checkYtDlp
  const originalList = VideoDownloader.listChannelVods

  VideoDownloader.checkYtDlp = async () => ({ installed: true, version: "2024.01.01" })
  VideoDownloader.listChannelVods = async () => [
    { id: "new_vid_1", title: "Already processed", date: "20260222", duration: 300 },
  ]

  try {
    const result = await WatchTool.execute(ctx, { action: "check", id: watcher.id })
    assert.equal(result.results[0].newVideos, 0)
    assert.equal(result.results[0].uploaded, 0)
  } finally {
    VideoDownloader.checkYtDlp = originalCheck
    VideoDownloader.listChannelVods = originalList
  }
})

test("WatchTool remove deletes a watcher", async () => {
  const watchers = await WatchStore.list()
  const id = watchers[0].id
  const ctx = makeMockContext()

  const result = await WatchTool.execute(ctx, { action: "remove", id })
  assert.equal(result.removed, true)

  const remaining = await WatchStore.list()
  assert.equal(remaining.filter((w) => w.id === id).length, 0)
})

test("WatchTool remove requires id", async () => {
  const ctx = makeMockContext()
  await assert.rejects(
    () => WatchTool.execute(ctx, { action: "remove" }),
    /id is required/
  )
})

test("WatchTool invalid action throws", async () => {
  const ctx = makeMockContext()
  await assert.rejects(
    () => WatchTool.execute(ctx, { action: "invalid_action" }),
    /Invalid action/
  )
})

test("WatchTool buildVideoUrl returns correct URLs", () => {
  assert.equal(
    WatchTool.buildVideoUrl("youtube_channel", "abc123"),
    "https://www.youtube.com/watch?v=abc123"
  )
  assert.equal(
    WatchTool.buildVideoUrl("twitch_channel", "12345"),
    "https://www.twitch.tv/videos/12345"
  )
})

test("WatchTool cleanup", async () => {
  if (originalEnv === undefined) delete process.env.OPENCLAW_CONFIG_PATH
  else process.env.OPENCLAW_CONFIG_PATH = originalEnv
  if (tmpPath) await rm(tmpPath, { recursive: true, force: true })
})
