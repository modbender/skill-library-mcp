import { access } from "node:fs/promises"
import { basename, extname } from "node:path"
import { NextSteps } from "../lib/next-steps.mjs"
import { SpendPolicyGuard } from "../lib/spend-policy.mjs"
import { PresetCatalog } from "../lib/presets.mjs"
import { VideoDownloader } from "../lib/downloader.mjs"

export class UploadTool {
  static SUPPORTED_EXTENSIONS = new Set([
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
  ])

  static stripExtension(fileName) {
    const extension = extname(fileName)
    if (!extension) {
      return fileName
    }
    return fileName.slice(0, -extension.length)
  }

  static async assertLocalFile(filePath) {
    await access(filePath)
    const extension = extname(filePath).toLowerCase()
    if (!UploadTool.SUPPORTED_EXTENSIONS.has(extension)) {
      throw new Error(
        `Unsupported file type ${extension}. Supported formats: ${Array.from(
          UploadTool.SUPPORTED_EXTENSIONS
        ).join(", ")}`
      )
    }
  }

  static resolveConfiguration(defaultPreset, presetName, overrideConfiguration) {
    const selectedPreset = presetName || defaultPreset || null

    let configuration = {}
    if (selectedPreset) {
      configuration = PresetCatalog.resolvePreset(selectedPreset)
    }

    if (overrideConfiguration && typeof overrideConfiguration === "object") {
      configuration = PresetCatalog.mergeConfigurations(
        configuration,
        overrideConfiguration
      )
    }

    return {
      preset: selectedPreset,
      configuration,
    }
  }

  static async execute(context, params) {
    const apiClient = context.apiClient
    const defaultPreset = context.defaultPreset || null

    const sourceInput = String(params.file_path || "").trim()
    if (!sourceInput) {
      throw new Error("file_path is required")
    }

    let localFilePath = sourceInput
    let tmpDir = null
    let downloadedFromUrl = false
    let sourceInfo = null

    try {
      if (VideoDownloader.isUrl(sourceInput)) {
        if (!VideoDownloader.isSupportedUrl(sourceInput)) {
          throw new Error(
            "Unsupported URL domain. Supported: YouTube, Twitch, Vimeo, Dailymotion, Streamable, Reddit"
          )
        }

        const ytdlp = await VideoDownloader.checkYtDlp()
        if (!ytdlp.installed) {
          throw new Error(
            "yt-dlp is not installed. Install with: brew install yt-dlp (macOS), pip install yt-dlp (Linux), winget install yt-dlp (Windows)."
          )
        }

        sourceInfo = await VideoDownloader.getVideoInfo(sourceInput)
        let download
        try {
          download = await VideoDownloader.download(sourceInput)
        } catch (dlErr) {
          tmpDir = dlErr.tmpDir || null
          throw dlErr
        }
        localFilePath = download.filePath
        tmpDir = download.tmpDir
        downloadedFromUrl = true
      } else {
        await UploadTool.assertLocalFile(localFilePath)
      }

      const { preset, configuration } = UploadTool.resolveConfiguration(
        defaultPreset,
        params.preset,
        params.configuration
      )

      const projectName =
        params.name ||
        sourceInfo?.title ||
        UploadTool.stripExtension(basename(localFilePath))
      const priority = params.priority || "normal"
      const webhookUrl =
        typeof params?.webhook_url === "string" &&
        params.webhook_url.trim().length > 0
          ? params.webhook_url.trim()
          : null
      const webhookSecret =
        typeof params?.webhook_secret === "string" &&
        params.webhook_secret.trim().length > 0
          ? params.webhook_secret.trim()
          : null

      let estimate = null
      try {
        const estimatePayload = {
          preset,
          priority,
          configuration,
        }

        const durationValue = Number(params?.duration_minutes)
        if (Number.isFinite(durationValue) && durationValue > 0) {
          estimatePayload.durationMinutes = Math.round(durationValue)
        }

        estimate = await apiClient.estimateCost(estimatePayload)
      } catch {
        estimate = {
          apiCredits: priority === "rush" ? 2 : 1,
          creatorCredits: { total: 0 },
          totalCost: {
            apiCredits: priority === "rush" ? 2 : 1,
            creatorCredits: 0,
          },
        }
      }

      const spendAuthorization = await SpendPolicyGuard.authorizeAction(
        context,
        {
          action: "upload",
          actionLabel: "Upload and process video",
          estimatedCost: {
            apiCredits:
              estimate?.totalCost?.apiCredits ??
              estimate?.apiCredits ??
              (priority === "rush" ? 2 : 1),
            creatorCredits:
              estimate?.totalCost?.creatorCredits ??
              estimate?.creatorCredits?.total ??
              0,
          },
          confirmSpend: Boolean(params?.confirm_spend),
        }
      )

      const result = await apiClient.uploadProject(localFilePath, {
        name: projectName,
        configuration,
        priority,
        webhookUrl,
        webhookSecret,
      })

      return {
        projectId: result.projectId || result.id,
        status: result.status || "Uploading",
        pollUrl:
          result.pollUrl || `/api/v1/projects/${result.projectId || result.id}/status`,
        preset,
        projectName,
        priority,
        spendPolicy: spendAuthorization.policy?.mode || "smart",
        estimatedCost: spendAuthorization.estimatedCost,
        webhook: result.webhook || {
          enabled: Boolean(webhookUrl),
          url: webhookUrl,
          event: webhookUrl ? "project.completed" : null,
          signing: Boolean(webhookSecret),
        },
        downloadedFromUrl,
        sourceUrl: downloadedFromUrl ? sourceInput : null,
        next_steps: NextSteps.forUpload(Boolean(webhookUrl)),
      }
    } finally {
      if (tmpDir) {
        await VideoDownloader.cleanup(tmpDir)
      }
    }
  }
}
