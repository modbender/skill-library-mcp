import { chmod, mkdir, readFile, writeFile } from "node:fs/promises"
import { homedir } from "node:os"
import { dirname, join } from "node:path"
import fetch from "node-fetch"

export class AuthFlowError extends Error {
  constructor(message, code = "auth_flow_error", status = 500, details = null) {
    super(message)
    this.name = "AuthFlowError"
    this.code = code
    this.status = status
    this.details = details
  }
}

export class AuthFlow {
  static DEFAULT_TIMEOUT_MS = 20000

  static normalizeApiEndpoint(apiEndpoint) {
    return String(apiEndpoint || "https://www.web2labs.com").replace(/\/$/, "")
  }

  static async parsePayload(response) {
    const raw = await response.text()
    if (!raw) {
      return null
    }

    try {
      return JSON.parse(raw)
    } catch {
      return {
        raw,
      }
    }
  }

  static createApiError(response, payload, fallbackCode, fallbackMessage) {
    const code = payload?.error?.code || fallbackCode
    const message = payload?.error?.message || fallbackMessage
    return new AuthFlowError(message, code, response.status, payload?.error || null)
  }

  static buildBasicAuthHeader(basicAuth) {
    if (!basicAuth) return {}
    const encoded = Buffer.from(basicAuth).toString("base64")
    return { Authorization: `Basic ${encoded}` }
  }

  static async requestJson(url, options = {}) {
    const timeoutMs = Number(options.timeoutMs || AuthFlow.DEFAULT_TIMEOUT_MS)
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      })
      const payload = await AuthFlow.parsePayload(response)
      return { response, payload }
    } catch (error) {
      if (error?.name === "AbortError") {
        throw new AuthFlowError(
          "Setup request timed out. Please try again.",
          "timeout",
          408
        )
      }
      throw new AuthFlowError(
        error?.message || "Network error during setup.",
        "network_error",
        503
      )
    } finally {
      clearTimeout(timer)
    }
  }

  static getConfigPath() {
    const override = process.env.OPENCLAW_CONFIG_PATH
    if (override && override.trim()) {
      return override.trim()
    }
    return join(homedir(), ".openclaw", "openclaw.json")
  }

  static getConfigDir() {
    return dirname(AuthFlow.getConfigPath())
  }

  static async sendMagicLink(apiEndpoint, email, basicAuth = null) {
    const normalizedEndpoint = AuthFlow.normalizeApiEndpoint(apiEndpoint)
    const { response, payload } = await AuthFlow.requestJson(
      `${normalizedEndpoint}/api/auth/magic/send`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...AuthFlow.buildBasicAuthHeader(basicAuth),
        },
        body: JSON.stringify({ email }),
      }
    )
    if (!response.ok) {
      if (response.status === 429) {
        const retryIn = Number(payload?.error?.details?.retryIn || 60)
        throw new AuthFlowError(
          `Rate limited. Please wait ${retryIn} seconds and retry.`,
          "rate_limited",
          response.status,
          payload?.error?.details || null
        )
      }
      throw AuthFlow.createApiError(
        response,
        payload,
        "magic_send_failed",
        "Failed to send magic link"
      )
    }

    return {
      sent: true,
      email: payload?.data?.email || email,
      retryInSeconds: null,
    }
  }

  static async completeMagicLinkToken(apiEndpoint, email, code, basicAuth = null) {
    const normalizedEndpoint = AuthFlow.normalizeApiEndpoint(apiEndpoint)
    const { response, payload } = await AuthFlow.requestJson(
      `${normalizedEndpoint}/api/auth/magic/token`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...AuthFlow.buildBasicAuthHeader(basicAuth),
        },
        body: JSON.stringify({ state: email, code }),
      }
    )
    if (!response.ok) {
      if (payload?.error?.code === "invalid_code") {
        throw new AuthFlowError(
          "Invalid or expired code. Request a new magic link and retry.",
          "invalid_code",
          response.status,
          payload?.error?.details || null
        )
      }
      throw AuthFlow.createApiError(
        response,
        payload,
        "magic_token_failed",
        "Authentication failed"
      )
    }

    return {
      accessToken: payload?.data?.accessToken,
      userId: payload?.data?.userId,
      tier: payload?.data?.tier,
      expiresIn: payload?.data?.expiresIn,
    }
  }

  static async generateApiKey(apiEndpoint, accessToken, basicAuth = null) {
    // Bearer token goes in Authorization header; Basic Auth is intentionally
    // omitted here — the server endpoint should not require it.
    // regenerateIfExists: if the user already has an API key, revoke it and
    // create a new one instead of returning a key_already_exists error.
    const normalizedEndpoint = AuthFlow.normalizeApiEndpoint(apiEndpoint)
    const { response, payload } = await AuthFlow.requestJson(
      `${normalizedEndpoint}/api/user/api-key/generate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ regenerateIfExists: true }),
      }
    )
    if (!response.ok) {
      if (payload?.error?.code === "key_already_exists") {
        throw new AuthFlowError(
          "API key already exists. Open https://web2labs.com/user/api to view or regenerate your key.",
          "key_already_exists",
          response.status,
          payload?.error?.details || null
        )
      }
      throw AuthFlow.createApiError(
        response,
        payload,
        "api_key_generate_failed",
        "Failed to generate API key"
      )
    }

    return {
      key: payload?.data?.key,
      keyPrefix: payload?.data?.keyPrefix,
      freeCredits: payload?.data?.freeCredits || 0,
      message: payload?.data?.message || "API key generated",
    }
  }

  static async storeApiKey(apiKey) {
    const configPath = AuthFlow.getConfigPath()
    const configDir = AuthFlow.getConfigDir()

    let config = {}
    try {
      const raw = await readFile(configPath, "utf-8")
      config = JSON.parse(raw)
    } catch (err) {
      if (err?.code === "ENOENT") {
        await mkdir(configDir, { recursive: true })
      } else if (err instanceof SyntaxError) {
        throw new AuthFlowError(
          `Config file ${configPath} contains invalid JSON. Please fix or delete it manually.`,
          "config_corrupt",
          500
        )
      } else {
        throw new AuthFlowError(
          `Unable to read config file ${configPath}: ${err?.message || err}`,
          "config_read_error",
          500
        )
      }
    }

    if (!config.skills) {
      config.skills = {}
    }
    if (!config.skills.entries) {
      config.skills.entries = {}
    }
    if (!config.skills.entries["@web2labs/studio"]) {
      config.skills.entries["@web2labs/studio"] = {}
    }

    config.skills.entries["@web2labs/studio"].enabled = true
    config.skills.entries["@web2labs/studio"].apiKey = apiKey

    await writeFile(configPath, JSON.stringify(config, null, 2), "utf-8")

    try {
      await chmod(configPath, 0o600)
    } catch {
      // Best effort; platform may not support chmod semantics.
    }

    return {
      stored: true,
      path: configPath,
    }
  }
}
