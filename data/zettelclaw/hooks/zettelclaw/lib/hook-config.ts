import type { HookEvent, SweepConfig } from "./hook-types"

const DEFAULT_SWEEP_INTERVAL_MINUTES = 1_440
const DEFAULT_SWEEP_MESSAGES = 120
const DEFAULT_SWEEP_MAX_FILES = 40
const DEFAULT_SWEEP_STALE_MINUTES = 30
const DEFAULT_EXPECT_FINAL = false

function parsePositiveInt(value: unknown, fallback: number, minimum: number, maximum: number): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return Math.min(maximum, Math.max(minimum, Math.floor(value)))
  }

  if (typeof value === "string") {
    const parsed = Number.parseInt(value, 10)
    if (Number.isFinite(parsed)) {
      return Math.min(maximum, Math.max(minimum, parsed))
    }
  }

  return fallback
}

function parseBoolean(value: unknown, fallback: boolean): boolean {
  if (typeof value === "boolean") {
    return value
  }

  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase()
    if (normalized === "true") {
      return true
    }

    if (normalized === "false") {
      return false
    }
  }

  return fallback
}

export function parseMessageCount(configValue: unknown): number {
  return parsePositiveInt(configValue, 20, 1, 200)
}

export function parseExpectFinal(configValue: unknown): boolean {
  return parseBoolean(configValue, DEFAULT_EXPECT_FINAL)
}

export function parseSweepConfig(hookConfig: Record<string, unknown>): SweepConfig {
  return {
    enabled: parseBoolean(hookConfig.sweepEnabled, true),
    intervalMinutes: parsePositiveInt(hookConfig.sweepEveryMinutes, DEFAULT_SWEEP_INTERVAL_MINUTES, 5, 1_440),
    messages: parsePositiveInt(hookConfig.sweepMessages, DEFAULT_SWEEP_MESSAGES, 10, 400),
    maxFiles: parsePositiveInt(hookConfig.sweepMaxFiles, DEFAULT_SWEEP_MAX_FILES, 1, 500),
    staleMinutes: parsePositiveInt(hookConfig.sweepStaleMinutes, DEFAULT_SWEEP_STALE_MINUTES, 5, 10_080),
  }
}

export function toDate(value: unknown): Date {
  if (value instanceof Date && Number.isFinite(value.valueOf())) {
    return value
  }

  if (typeof value === "string") {
    const parsed = new Date(value)
    if (Number.isFinite(parsed.valueOf())) {
      return parsed
    }
  }

  return new Date()
}

export function isResetEvent(event: HookEvent): boolean {
  const eventType = event.type.toLowerCase()
  const eventAction = event.action.toLowerCase()

  return (
    eventType === "command:new" ||
    eventType === "command:reset" ||
    (eventType === "command" && (eventAction === "new" || eventAction === "reset"))
  )
}

export function isIsolatedSession(sessionKey: string): boolean {
  const normalized = sessionKey.toLowerCase()
  return normalized === "isolated" || normalized.endsWith(":isolated") || normalized.includes(":isolated:")
}
