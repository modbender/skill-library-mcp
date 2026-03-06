#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { z } from "zod"
import { StudioApiClient, StudioApiError } from "./lib/api-client.mjs"
import { SpendPolicy } from "./lib/spend-policy.mjs"
import { AnalyticsTool } from "./tools/analytics.mjs"
import { AssetsTool } from "./tools/assets.mjs"
import { BrandImportTool } from "./tools/brand-import.mjs"
import { BrandTool } from "./tools/brand.mjs"
import { CreditsTool } from "./tools/credits.mjs"
import { DeleteTool } from "./tools/delete.mjs"
import { DownloadTool } from "./tools/download.mjs"
import { EstimateTool } from "./tools/estimate.mjs"
import { FeedbackTool } from "./tools/feedback.mjs"
import { PollTool } from "./tools/poll.mjs"
import { PricingTool } from "./tools/pricing.mjs"
import { ProjectsTool } from "./tools/projects.mjs"
import { ReferralTool } from "./tools/referral.mjs"
import { RerenderTool } from "./tools/rerender.mjs"
import { ResultsTool } from "./tools/results.mjs"
import { SetupTool } from "./tools/setup.mjs"
import { StatusTool } from "./tools/status.mjs"
import { ThumbnailsTool } from "./tools/thumbnails.mjs"
import { UploadTool } from "./tools/upload.mjs"
import { WatchTool } from "./tools/watch.mjs"

export class StudioSkillServer {
  constructor() {
    this.skillVersion = "1.0.1"
    this.config = this.readConfig()
    this.apiClient = new StudioApiClient({
      apiEndpoint: this.config.apiEndpoint,
      apiKey: this.config.apiKey,
      bearerToken: this.config.bearerToken,
      basicAuth: this.config.basicAuth,
    })

    this.server = new McpServer({
      name: "web2labs-studio",
      version: this.skillVersion,
    })
  }

  readConfig() {
    const testMode =
      process.env.WEB2LABS_TEST_MODE === "true" ||
      process.env.WEB2LABS_TEST_MODE === "1"

    const defaultEndpoint = testMode
      ? "https://test.web2labs.com"
      : "https://www.web2labs.com"

    const basicAuth = process.env.WEB2LABS_BASIC_AUTH || null

    return {
      testMode,
      apiEndpoint: process.env.WEB2LABS_API_ENDPOINT || defaultEndpoint,
      apiKey: process.env.WEB2LABS_API_KEY || null,
      bearerToken: process.env.WEB2LABS_BEARER_TOKEN || null,
      basicAuth,
      defaultPreset: process.env.WEB2LABS_DEFAULT_PRESET || "youtube",
      downloadDir: process.env.WEB2LABS_DOWNLOAD_DIR || "~/studio-exports",
      spendPolicy: SpendPolicy.fromEnvironment(process.env),
    }
  }

  createToolContext() {
    return {
      apiClient: this.apiClient,
      apiEndpoint: this.config.apiEndpoint,
      basicAuth: this.config.basicAuth,
      testMode: this.config.testMode,
      defaultPreset: this.config.defaultPreset,
      downloadDir: this.config.downloadDir,
      skillVersion: this.skillVersion,
      spendPolicy: this.config.spendPolicy,
    }
  }

  wrapResult(result) {
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    }
  }

  wrapError(error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              error: true,
              code: error?.code || "tool_error",
              status: error?.status || 500,
              message: error?.message || "Tool execution failed",
              details: error?.details || null,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    }
  }

  registerTool(name, description, schema, handler) {
    this.server.tool(name, description, schema, async (params) => {
      try {
        const context = this.createToolContext()
        const data = await handler(context, params)
        return this.wrapResult(data)
      } catch (error) {
        return this.wrapError(error)
      }
    })
  }

  registerTools() {
    this.registerTool(
      "studio_upload",
      "Upload a video file or supported URL for AI video editing.",
      {
        file_path: z.string().describe("Absolute local path or supported URL"),
        name: z.string().optional().describe("Optional project name"),
        preset: z
          .enum([
            "quick",
            "youtube",
            "shorts-only",
            "podcast",
            "gaming",
            "tutorial",
            "vlog",
            "cinematic",
          ])
          .optional(),
        configuration: z
          .record(z.any())
          .optional()
          .describe("Raw configuration override"),
        priority: z.enum(["normal", "rush"]).optional(),
        duration_minutes: z
          .number()
          .optional()
          .describe("Optional duration hint for more accurate cost estimation"),
        webhook_url: z
          .string()
          .optional()
          .describe("Optional callback URL for project.completed webhook delivery"),
        webhook_secret: z
          .string()
          .optional()
          .describe("Optional webhook signing secret (HMAC SHA-256)"),
        confirm_spend: z
          .boolean()
          .optional()
          .describe("Set true after user approval when credits will be spent"),
      },
      UploadTool.execute
    )

    this.registerTool(
      "studio_status",
      "Check current project status and progress.",
      {
        project_id: z.string().describe("Project ID"),
      },
      StatusTool.execute
    )

    this.registerTool(
      "studio_poll",
      "Wait for project completion with stage-aware polling.",
      {
        project_id: z.string().describe("Project ID"),
        timeout_minutes: z.number().optional().describe("Timeout in minutes"),
      },
      PollTool.execute
    )

    this.registerTool(
      "studio_results",
      "Get project output metadata and download URLs.",
      {
        project_id: z.string().describe("Project ID"),
      },
      ResultsTool.execute
    )

    this.registerTool(
      "studio_download",
      "Download project outputs to the local filesystem.",
      {
        project_id: z.string().describe("Project ID"),
        output_dir: z.string().optional().describe("Output directory"),
        types: z
          .array(
            z.enum([
              "main",
              "shorts",
              "subtitles",
              "transcription",
              "timeline-edl",
              "timeline-fcpxml",
              "timeline-xml",
              "thumbnails",
              "all",
            ])
          )
          .optional(),
      },
      DownloadTool.execute
    )

    this.registerTool(
      "studio_setup",
      "Set up Web2Labs authentication (send magic link, complete setup, or save API key).",
      {
        action: z
          .enum(["send_magic_link", "complete_setup", "save_api_key"])
          .optional()
          .describe("Defaults to send_magic_link"),
        email: z.string().optional().describe("Email for magic-link setup"),
        code: z
          .string()
          .optional()
          .describe("6-character magic-link code (for complete_setup)"),
        api_key: z
          .string()
          .optional()
          .describe("Existing API key to save (for save_api_key)"),
      },
      SetupTool.execute
    )

    this.registerTool(
      "studio_credits",
      "Get API credit and subscription allocation details.",
      {},
      CreditsTool.execute
    )

    this.registerTool(
      "studio_pricing",
      "Get current pricing for API and premium Creator Credit features.",
      {},
      PricingTool.execute
    )

    this.registerTool(
      "studio_estimate",
      "Estimate API and Creator Credit costs before upload.",
      {
        duration_minutes: z.number().optional(),
        preset: z
          .enum([
            "quick",
            "youtube",
            "shorts-only",
            "podcast",
            "gaming",
            "tutorial",
            "vlog",
            "cinematic",
          ])
          .optional(),
        priority: z.enum(["normal", "rush"]).optional(),
        configuration: z.record(z.any()).optional(),
      },
      EstimateTool.execute
    )

    this.registerTool(
      "studio_thumbnails",
      "Generate thumbnail variants for an existing completed project (uses Creator Credits).",
      {
        project_id: z.string().describe("Project ID"),
        variants: z.number().min(1).max(3).optional(),
        premium_quality: z.boolean().optional(),
        use_brand_colors: z.boolean().optional(),
        use_brand_faces: z.boolean().optional(),
        confirm_spend: z
          .boolean()
          .optional()
          .describe("Set true after user approval when Creator Credits will be spent"),
      },
      ThumbnailsTool.execute
    )

    this.registerTool(
      "studio_analytics",
      "Get usage analytics and value metrics.",
      {
        period: z.enum(["this_month", "last_month", "all_time"]).optional(),
      },
      AnalyticsTool.execute
    )

    this.registerTool(
      "studio_brand",
      "Get or update brand kit settings used by subtitles and thumbnails.",
      {
        action: z.enum(["get", "update"]).optional(),
        updates: z
          .record(z.any())
          .optional()
          .describe("Brand fields to update when action is update"),
        channel_name: z.string().optional(),
        primary_color: z.string().optional(),
        secondary_color: z.string().optional(),
        brand_identity: z.string().optional(),
        channel_pitch: z.string().optional(),
        posting_plan: z.array(z.record(z.any())).optional(),
        subtitle_font_id: z.string().optional(),
        thumbnail_font_id: z.string().optional(),
        default_intro_enabled: z.boolean().optional(),
        default_outro_enabled: z.boolean().optional(),
      },
      BrandTool.execute
    )

    this.registerTool(
      "studio_brand_import",
      "Import brand colors and identity from a YouTube, Twitch, or X profile URL.",
      {
        url: z
          .string()
          .describe("Channel/profile URL (YouTube or Twitch)"),
        apply: z
          .boolean()
          .optional()
          .describe("Apply suggested settings immediately (default false)"),
      },
      BrandImportTool.execute
    )

    this.registerTool(
      "studio_assets",
      "Manage reusable intro/outro/watermark assets for future projects.",
      {
        action: z.enum(["list", "upload", "delete"]).optional(),
        asset_type: z
          .enum(["intro", "outro", "watermark"])
          .optional()
          .describe("Required for action=upload and action=delete"),
        file_path: z
          .string()
          .optional()
          .describe("Required for action=upload (absolute local file path)"),
      },
      AssetsTool.execute
    )

    this.registerTool(
      "studio_rerender",
      "Re-render a completed project with updated settings without re-uploading.",
      {
        project_id: z.string().describe("Project ID"),
        configuration: z
          .record(z.any())
          .describe("Configuration overrides merged into existing project settings"),
        confirm_spend: z
          .boolean()
          .optional()
          .describe("Set true after user approval when Creator Credits will be spent (subsequent re-renders cost 15 CC)"),
      },
      RerenderTool.execute
    )

    this.registerTool(
      "studio_projects",
      "List projects for the authenticated user.",
      {
        limit: z.number().optional(),
        offset: z.number().optional(),
      },
      ProjectsTool.execute
    )

    this.registerTool(
      "studio_delete",
      "Delete a project by project ID.",
      {
        project_id: z.string(),
      },
      DeleteTool.execute
    )

    this.registerTool(
      "studio_feedback",
      "Submit feedback to Web2Labs team (bug/suggestion/question).",
      {
        type: z.enum(["bug", "suggestion", "question"]),
        title: z.string(),
        description: z.string(),
        severity: z.enum(["low", "medium", "high", "critical"]).optional(),
        project_id: z.string().optional(),
      },
      FeedbackTool.execute
    )

    this.registerTool(
      "studio_referral",
      "Get the user's referral code and stats, or apply a friend's referral code for bonus credits.",
      {
        action: z
          .enum(["get", "apply"])
          .describe(
            "'get' returns the user's referral code, link, and stats. 'apply' applies a friend's code for bonus credits."
          ),
        code: z
          .string()
          .optional()
          .describe(
            "Referral code to apply (required when action is 'apply')"
          ),
      },
      ReferralTool.execute
    )

    this.registerTool(
      "studio_watch",
      "Watch a YouTube or Twitch channel for new videos and auto-process them.",
      {
        action: z
          .enum(["add", "list", "remove", "check", "pause", "resume", "status"])
          .optional()
          .describe("Defaults to list"),
        url: z
          .string()
          .optional()
          .describe("Channel URL (required for add)"),
        id: z
          .string()
          .optional()
          .describe("Watcher ID (for remove/pause/resume/status/check)"),
        preset: z
          .enum([
            "quick",
            "youtube",
            "shorts-only",
            "podcast",
            "gaming",
            "tutorial",
            "vlog",
            "cinematic",
          ])
          .optional()
          .describe("Studio preset for processing (for add)"),
        configuration: z
          .record(z.any())
          .optional()
          .describe("Configuration overrides (for add)"),
        poll_interval_minutes: z
          .number()
          .optional()
          .describe("How often to check for new videos in minutes (default 30, for add)"),
        max_duration_minutes: z
          .number()
          .optional()
          .describe("Skip videos longer than this (default 120, for add)"),
        max_daily_uploads: z
          .number()
          .optional()
          .describe("Max uploads per day per watcher (default 5, for add)"),
        output_dir: z
          .string()
          .optional()
          .describe("Directory for auto-downloading results (for add)"),
      },
      WatchTool.execute
    )

  }

  async start() {
    this.registerTools()
    const transport = new StdioServerTransport()
    await this.server.connect(transport)
  }
}

const app = new StudioSkillServer()
app.start().catch((error) => {
  console.error("[web2labs-studio] Fatal error:", error)
  process.exit(1)
})
