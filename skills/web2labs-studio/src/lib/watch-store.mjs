import { mkdir, readFile, writeFile } from "node:fs/promises"
import { randomBytes } from "node:crypto"
import { homedir } from "node:os"
import { dirname, join } from "node:path"

const MAX_PROCESSED_IDS = 500
const MAX_RETRIES = 3

export class WatchStore {
  static getStorePath() {
    const override = process.env.OPENCLAW_CONFIG_PATH
    const configDir = override && override.trim()
      ? dirname(override.trim())
      : join(homedir(), ".openclaw")
    return join(configDir, "watchers.json")
  }

  static generateId() {
    return `w_${randomBytes(6).toString("hex")}`
  }

  static async load() {
    try {
      const raw = await readFile(WatchStore.getStorePath(), "utf-8")
      const data = JSON.parse(raw)
      return Array.isArray(data.watchers) ? data.watchers : []
    } catch {
      return []
    }
  }

  static async save(watchers) {
    const storePath = WatchStore.getStorePath()
    await mkdir(dirname(storePath), { recursive: true })
    await writeFile(
      storePath,
      JSON.stringify({ watchers }, null, 2),
      "utf-8"
    )
  }

  static normalizeType(url) {
    try {
      const host = new URL(url).hostname.toLowerCase()
      if (host.includes("twitch.tv")) return "twitch_channel"
      return "youtube_channel"
    } catch {
      return "youtube_channel"
    }
  }

  static deriveLabel(url) {
    try {
      const parsed = new URL(url)
      const path = parsed.pathname.replace(/\/+$/, "")
      const segments = path.split("/").filter(Boolean)
      const last = segments[segments.length - 1] || parsed.hostname
      return last.replace(/^@/, "")
    } catch {
      return "unknown"
    }
  }

  static isChannelUrl(url) {
    try {
      const parsed = new URL(url)
      const host = parsed.hostname.toLowerCase()
      const path = parsed.pathname.toLowerCase()

      if (host.includes("youtube.com") || host.includes("youtu.be")) {
        if (path.includes("/watch")) return false
        if (path.startsWith("/@") || path.startsWith("/c/") ||
            path.startsWith("/channel/") || path.startsWith("/user/")) {
          return true
        }
        return false
      }

      if (host.includes("twitch.tv")) {
        if (path.includes("/videos") || path.includes("/clip")) return false
        const segments = path.split("/").filter(Boolean)
        return segments.length >= 1
      }

      return false
    } catch {
      return false
    }
  }

  static createWatcher(params) {
    return {
      id: WatchStore.generateId(),
      type: WatchStore.normalizeType(params.url),
      url: String(params.url).trim(),
      label: params.label || WatchStore.deriveLabel(params.url),
      preset: params.preset || "youtube",
      configuration: params.configuration || {},
      pollIntervalMinutes: Math.max(5, Math.min(1440, Number(params.pollIntervalMinutes) || 30)),
      maxDurationMinutes: Math.max(1, Math.min(720, Number(params.maxDurationMinutes) || 120)),
      maxDailyUploads: Math.max(1, Math.min(50, Number(params.maxDailyUploads) || 5)),
      outputDir: params.outputDir || null,
      enabled: true,
      lastChecked: null,
      lastProcessedIds: [],
      failedVideos: [],
      uploadsToday: 0,
      uploadsTodayDate: null,
      createdAt: new Date().toISOString(),
    }
  }

  static async add(params) {
    const watchers = await WatchStore.load()
    const watcher = WatchStore.createWatcher(params)
    watchers.push(watcher)
    await WatchStore.save(watchers)
    return watcher
  }

  static async list() {
    return WatchStore.load()
  }

  static async get(id) {
    const watchers = await WatchStore.load()
    return watchers.find((w) => w.id === id) || null
  }

  static async remove(id) {
    const watchers = await WatchStore.load()
    const index = watchers.findIndex((w) => w.id === id)
    if (index === -1) return false
    watchers.splice(index, 1)
    await WatchStore.save(watchers)
    return true
  }

  static async update(id, updates) {
    const watchers = await WatchStore.load()
    const watcher = watchers.find((w) => w.id === id)
    if (!watcher) return null
    Object.assign(watcher, updates)
    await WatchStore.save(watchers)
    return watcher
  }

  static async markProcessed(id, videoIds) {
    const watchers = await WatchStore.load()
    const watcher = watchers.find((w) => w.id === id)
    if (!watcher) return null

    const combined = [...(watcher.lastProcessedIds || []), ...videoIds]
    watcher.lastProcessedIds = combined.slice(-MAX_PROCESSED_IDS)
    watcher.lastChecked = new Date().toISOString()

    const today = new Date().toISOString().slice(0, 10)
    if (watcher.uploadsTodayDate !== today) {
      watcher.uploadsToday = 0
      watcher.uploadsTodayDate = today
    }
    watcher.uploadsToday += videoIds.length

    await WatchStore.save(watchers)
    return watcher
  }

  static getUploadsToday(watcher) {
    const today = new Date().toISOString().slice(0, 10)
    if (watcher.uploadsTodayDate !== today) return 0
    return watcher.uploadsToday || 0
  }

  static getRemainingUploads(watcher) {
    return Math.max(0, watcher.maxDailyUploads - WatchStore.getUploadsToday(watcher))
  }

  static filterNewVideos(watcher, videos) {
    const processed = new Set(watcher.lastProcessedIds || [])
    const failedIds = new Set((watcher.failedVideos || []).map((f) => f.id))
    return videos.filter((v) => {
      if (processed.has(v.id)) return false
      if (failedIds.has(v.id)) return false
      if (watcher.maxDurationMinutes && v.duration > watcher.maxDurationMinutes * 60) return false
      return true
    })
  }

  static getRetryableVideos(watcher) {
    return (watcher.failedVideos || []).filter((f) => f.attempts < MAX_RETRIES)
  }

  static async markFailed(id, videoId, title) {
    const watchers = await WatchStore.load()
    const watcher = watchers.find((w) => w.id === id)
    if (!watcher) return null

    if (!Array.isArray(watcher.failedVideos)) {
      watcher.failedVideos = []
    }

    const existing = watcher.failedVideos.find((f) => f.id === videoId)
    if (existing) {
      existing.attempts += 1
      existing.lastAttempt = new Date().toISOString()
    } else {
      watcher.failedVideos.push({
        id: videoId,
        title: title || videoId,
        attempts: 1,
        lastAttempt: new Date().toISOString(),
      })
    }

    await WatchStore.save(watchers)
    return watcher
  }

  static async clearFailed(id, videoId) {
    const watchers = await WatchStore.load()
    const watcher = watchers.find((w) => w.id === id)
    if (!watcher || !Array.isArray(watcher.failedVideos)) return null

    watcher.failedVideos = watcher.failedVideos.filter((f) => f.id !== videoId)
    await WatchStore.save(watchers)
    return watcher
  }
}
