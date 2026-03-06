import { mkdir } from "node:fs/promises"
import { homedir } from "node:os"
import { basename, join } from "node:path"
import { NextSteps } from "../lib/next-steps.mjs"

export class DownloadTool {
  static expandHome(pathValue) {
    if (pathValue === "~") {
      return homedir()
    }
    if (pathValue.startsWith("~/")) {
      return join(homedir(), pathValue.slice(2))
    }
    return pathValue
  }

  static sanitizeName(value) {
    return String(value || "project")
      .replace(/[<>:\"/\\|?*]+/g, "-")
      .replace(/\s+/g, "-")
      .toLowerCase()
      .slice(0, 120)
  }

  static safeFilename(name, fallback) {
    const base = basename(String(name || ""))
    const cleaned = base.replace(/[<>:"/\\|?*\x00-\x1F]+/g, "-").slice(0, 200)
    if (!cleaned || cleaned === "." || cleaned === "..") return fallback
    return cleaned
  }

  static isTypeEnabled(requested, candidate) {
    if (requested.includes("all")) {
      return true
    }
    return requested.includes(candidate)
  }

  static collectArtifacts(results, requestedTypes) {
    const artifacts = []

    if (results.mainVideo?.url && DownloadTool.isTypeEnabled(requestedTypes, "main")) {
      const fallbackMain = `${results.name || "project"}.mp4`
      artifacts.push({
        kind: "main",
        url: results.mainVideo.url,
        fileName: DownloadTool.safeFilename(results.mainVideo.filename, fallbackMain),
      })
    }

    if (Array.isArray(results.shorts) && DownloadTool.isTypeEnabled(requestedTypes, "shorts")) {
      for (let i = 0; i < results.shorts.length; i++) {
        const short = results.shorts[i]
        const fallbackShort = `${results.name || "project"}-short-${i + 1}.mp4`
        artifacts.push({
          kind: "shorts",
          url: short.url,
          fileName: DownloadTool.safeFilename(short.filename, fallbackShort),
        })
      }
    }

    if (results.subtitles?.url && DownloadTool.isTypeEnabled(requestedTypes, "subtitles")) {
      artifacts.push({
        kind: "subtitles",
        url: results.subtitles.url,
        fileName: "subtitles.srt",
      })
    }

    if (results.transcription?.url && DownloadTool.isTypeEnabled(requestedTypes, "transcription")) {
      artifacts.push({
        kind: "transcription",
        url: results.transcription.url,
        fileName: "transcription.json",
      })
    }

    if (DownloadTool.isTypeEnabled(requestedTypes, "timeline-edl")) {
      const edl = (results.timelineExports || []).find((item) => item.format === "edl")
      if (edl?.url) {
        artifacts.push({
          kind: "timeline-edl",
          url: edl.url,
          fileName: DownloadTool.safeFilename(edl.filename, "timeline.edl"),
        })
      }
    }

    if (DownloadTool.isTypeEnabled(requestedTypes, "timeline-fcpxml")) {
      const fcpxml = (results.timelineExports || []).find((item) => item.format === "fcpxml")
      if (fcpxml?.url) {
        artifacts.push({
          kind: "timeline-fcpxml",
          url: fcpxml.url,
          fileName: DownloadTool.safeFilename(fcpxml.filename, "timeline.fcpxml"),
        })
      }
    }

    if (DownloadTool.isTypeEnabled(requestedTypes, "timeline-xml")) {
      const xml = (results.timelineExports || []).find((item) => item.format === "premiere-xml")
      if (xml?.url) {
        artifacts.push({
          kind: "timeline-xml",
          url: xml.url,
          fileName: DownloadTool.safeFilename(xml.filename, "timeline.xml"),
        })
      }
    }

    if (Array.isArray(results.thumbnails) && DownloadTool.isTypeEnabled(requestedTypes, "thumbnails")) {
      for (const thumbnail of results.thumbnails) {
        if (!thumbnail?.imageUrl) {
          continue
        }
        const variant = String(thumbnail.variant || "x").toLowerCase()
        artifacts.push({
          kind: "thumbnails",
          url: thumbnail.imageUrl,
          fileName: `thumbnails/thumbnail-${variant}.png`,
        })
      }
    }

    return artifacts
  }

  static async execute(context, params) {
    const projectId = String(params.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const results = await context.apiClient.getProjectResults(projectId)

    const requestedTypes = Array.isArray(params.types) && params.types.length > 0
      ? params.types.map((item) => String(item || "").trim())
      : ["all"]

    const projectSlug = DownloadTool.sanitizeName(results.name || projectId)
    const baseOutputDir =
      params.output_dir ||
      `${context.downloadDir || "~/studio-exports"}/${projectSlug}`

    const outputDir = DownloadTool.expandHome(baseOutputDir)
    await mkdir(outputDir, { recursive: true })

    const artifacts = DownloadTool.collectArtifacts(results, requestedTypes)
    const downloaded = []

    for (const artifact of artifacts) {
      const destination = join(outputDir, artifact.fileName)
      await context.apiClient.downloadFile(artifact.url, destination)
      downloaded.push({
        kind: artifact.kind,
        sourceUrl: artifact.url,
        localPath: destination,
      })
    }

    return {
      projectId,
      outputDir,
      downloaded,
      retentionTimeRemaining: results.retentionTimeRemaining || null,
      next_steps: NextSteps.forDownload(results),
    }
  }
}
