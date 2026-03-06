import { AuthFlow, AuthFlowError } from "../lib/auth-flow.mjs"
import { VideoDownloader } from "../lib/downloader.mjs"

export class SetupTool {
  static TRUST_INFO = {
    data_retention: "Uploads deleted after processing (free: 2h, paid: per plan)",
    training: "Your content is never used for AI training",
    api_key_storage: "Stored locally in ~/.openclaw/openclaw.json (chmod 600)",
    communication: "All API calls use HTTPS",
    url_downloads: "Downloaded locally via yt-dlp, never routed through third parties",
  }

  static normalizeAction(value) {
    return String(value || "send_magic_link")
      .trim()
      .toLowerCase()
  }

  static normalizeEmail(value) {
    return String(value || "").trim().toLowerCase()
  }

  static maskApiKey(apiKey) {
    const key = String(apiKey || "")
    if (!key) {
      return ""
    }
    if (key.length <= 8) {
      return `${key.slice(0, 2)}***`
    }
    return `${key.slice(0, 8)}...${key.slice(-4)}`
  }

  static async checkDependencies() {
    const nodeVersion = process.version
    const nodeMajor = Number((nodeVersion.match(/^v(\d+)/) || [])[1] || 0)

    const ytdlp = await VideoDownloader.checkYtDlp().catch(() => ({
      installed: false,
      version: null,
    }))

    const issues = []
    if (nodeMajor < 18) {
      issues.push(`Node.js ${nodeVersion} detected — version 18+ is required.`)
    }
    if (!ytdlp.installed) {
      issues.push(
        "yt-dlp is not installed. URL-based workflows and watch mode require it. Install with: brew install yt-dlp (macOS), pip install yt-dlp (Linux), winget install yt-dlp (Windows)."
      )
    }

    return {
      node: { version: nodeVersion, supported: nodeMajor >= 18 },
      ytdlp: { installed: ytdlp.installed, version: ytdlp.version },
      ready: issues.length === 0,
      issues,
    }
  }

  static async fetchCreditSummary(apiClient) {
    try {
      const credits = await apiClient.getCredits()
      return {
        apiCredits: credits?.apiCredits?.total ?? credits?.total ?? null,
        creatorCredits: credits?.creatorCredits?.total ?? null,
        subscription: credits?.subscription?.tier ?? null,
      }
    } catch {
      return null
    }
  }

  static assertEmail(email) {
    if (!email || !email.includes("@") || !email.includes(".")) {
      throw new AuthFlowError(
        "A valid email is required for setup.",
        "invalid_email",
        400
      )
    }
  }

  static async runSendMagicLink(context, email) {
    SetupTool.assertEmail(email)
    const result = await AuthFlow.sendMagicLink(
      context.apiEndpoint,
      email,
      context.basicAuth || null
    )
    return {
      action: "send_magic_link",
      sent: true,
      email: result.email,
      nextStep:
        "Check your inbox for the Web2Labs magic link, then call studio_setup with action 'complete_setup', your email, and the 6-character code.",
    }
  }

  static async runCompleteSetup(context, email, code) {
    SetupTool.assertEmail(email)
    const normalizedCode = String(code || "").trim()
    if (!normalizedCode || normalizedCode.length < 4) {
      throw new AuthFlowError(
        "A valid code is required. Provide the 6-character code from the magic link email.",
        "missing_code",
        400
      )
    }

    const tokenResult = await AuthFlow.completeMagicLinkToken(
      context.apiEndpoint,
      email,
      normalizedCode,
      context.basicAuth || null
    )
    const keyResult = await AuthFlow.generateApiKey(
      context.apiEndpoint,
      tokenResult.accessToken,
      context.basicAuth || null
    )
    const storeResult = await AuthFlow.storeApiKey(keyResult.key)

    context.apiClient.setApiKey(keyResult.key)
    context.apiClient.setBearerToken(null)

    const [dependencies, creditSummary] = await Promise.all([
      SetupTool.checkDependencies(),
      SetupTool.fetchCreditSummary(context.apiClient),
    ])

    return {
      action: "complete_setup",
      configured: true,
      userId: tokenResult.userId,
      tier: tokenResult.tier || null,
      apiKeyPrefix: keyResult.keyPrefix || SetupTool.maskApiKey(keyResult.key),
      freeCredits: Number(keyResult.freeCredits || 0),
      configPath: storeResult.path,
      message:
        "Setup complete. Your API key was generated and saved to your OpenClaw config.",
      dependencies,
      credits: creditSummary,
      trust: SetupTool.TRUST_INFO,
      next_steps: [
        {
          tool: "studio_estimate",
          message:
            "Run studio_estimate before your first upload to preview costs.",
        },
        {
          tool: "studio_upload",
          message:
            "Upload your first video with studio_upload — 2 free credits included, no credit card needed.",
        },
      ],
    }
  }

  static async runSaveApiKey(context, apiKey) {
    const normalized = String(apiKey || "").trim()
    if (!normalized) {
      throw new AuthFlowError(
        "api_key is required when action is 'save_api_key'.",
        "missing_api_key",
        400
      )
    }

    const storeResult = await AuthFlow.storeApiKey(normalized)
    context.apiClient.setApiKey(normalized)
    context.apiClient.setBearerToken(null)

    const [dependencies, creditSummary] = await Promise.all([
      SetupTool.checkDependencies(),
      SetupTool.fetchCreditSummary(context.apiClient),
    ])

    return {
      action: "save_api_key",
      configured: true,
      apiKeyPrefix: SetupTool.maskApiKey(normalized),
      configPath: storeResult.path,
      message: "API key saved to OpenClaw config.",
      dependencies,
      credits: creditSummary,
      trust: SetupTool.TRUST_INFO,
      next_steps: [
        {
          tool: "studio_estimate",
          message:
            "Run studio_estimate before your first upload to preview costs.",
        },
        {
          tool: "studio_upload",
          message:
            "Upload a video with studio_upload to get started.",
        },
      ],
    }
  }

  static async execute(context, params) {
    const action = SetupTool.normalizeAction(params.action)
    const email = SetupTool.normalizeEmail(params.email)

    if (action === "send_magic_link") {
      return SetupTool.runSendMagicLink(context, email)
    }

    if (action === "complete_setup") {
      return SetupTool.runCompleteSetup(context, email, params.code)
    }

    if (action === "save_api_key") {
      return SetupTool.runSaveApiKey(context, params.api_key)
    }

    throw new AuthFlowError(
      "Invalid action. Use one of: send_magic_link, complete_setup, save_api_key.",
      "invalid_action",
      400
    )
  }
}
