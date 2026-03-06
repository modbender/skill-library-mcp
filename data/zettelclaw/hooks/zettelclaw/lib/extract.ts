import { spawn } from "node:child_process"
import { readFile } from "node:fs/promises"
import { resolve } from "node:path"

import { asRecord } from "./json"

const SYSTEM_PROMPT_PATH = resolve(import.meta.dirname, "..", "prompts", "session-summary.md")
const MAX_TRANSCRIPT_CHARS = 24_000
const MAX_JOURNAL_CHARS = 8_000
const EVENT_TIMEOUT_MS = 60_000
const FINAL_TIMEOUT_MS = 180_000

let cachedSystemPrompt: string | null | undefined

export interface VaultUpdateTaskRequest {
  conversation: string
  conversationSource: "command-reset" | "sweep"
  timestampIso: string
  sessionId?: string
  transcriptPath?: string
  vaultPath: string
  notesDirectory: string
  journalFilename: string
  journalPath: string
  journalContent: string
}

export interface VaultUpdateTaskResult {
  success: boolean
  message?: string
}

interface DispatchOptions {
  model?: string | undefined
  expectFinal?: boolean
  logger?: (message: string) => void
}

interface CommandResult {
  status: number | null
  stdout: string
  stderr: string
  timedOut: boolean
  error?: string
}

async function getSystemPrompt(logger: (message: string) => void): Promise<string | null> {
  if (cachedSystemPrompt !== undefined) {
    return cachedSystemPrompt
  }

  try {
    const rawPrompt = await readFile(SYSTEM_PROMPT_PATH, "utf8")
    const prompt = rawPrompt.trim()

    if (prompt.length === 0) {
      cachedSystemPrompt = null
      logger(`System prompt is empty: ${SYSTEM_PROMPT_PATH}`)
      return null
    }

    cachedSystemPrompt = prompt
    return prompt
  } catch (error) {
    cachedSystemPrompt = null
    const message = error instanceof Error ? error.message : String(error)
    logger(`Could not load hook system prompt ${SYSTEM_PROMPT_PATH}: ${message}`)
    return null
  }
}

function truncateForPrompt(value: string, maxChars: number, label: string): string {
  if (value.length <= maxChars) {
    return value
  }

  const omitted = value.length - maxChars
  return `${value.slice(0, maxChars)}\n\n[${label} truncated: omitted ${String(omitted)} chars]`
}

function buildEventText(prompt: string, request: VaultUpdateTaskRequest, model: string | undefined): string {
  const transcript = truncateForPrompt(request.conversation.trim(), MAX_TRANSCRIPT_CHARS, "transcript")
  const journalContent =
    request.journalContent.trim().length > 0
      ? truncateForPrompt(request.journalContent, MAX_JOURNAL_CHARS, "journal")
      : "(journal note does not exist yet)"

  const modelLine = model ? `- Preferred model for subagents: ${model}` : ""
  const transcriptPathLine = request.transcriptPath ? `- Transcript file: ${request.transcriptPath}` : ""

  return [
    prompt.trim(),
    "",
    "## Hook Context (Auto-Injected)",
    "- Trigger: zettelclaw hook",
    `- Source: ${request.conversationSource}`,
    `- Session timestamp: ${request.timestampIso}`,
    `- Session ID: ${request.sessionId ?? "unknown"}`,
    `- Vault path: ${request.vaultPath}`,
    `- Notes directory: ${request.notesDirectory}`,
    modelLine,
    transcriptPathLine,
    "",
    "### Conversation Transcript",
    "```text",
    transcript.length > 0 ? transcript : "(empty transcript)",
    "```",
    "",
    "### Current Journal Entry",
    `Filename: ${request.journalFilename}`,
    `Path: ${request.journalPath}`,
    "",
    "```markdown",
    journalContent,
    "```",
  ]
    .filter((line) => line.length > 0)
    .join("\n")
}

async function runCommand(command: string, args: string[], timeoutMs: number): Promise<CommandResult> {
  return await new Promise((resolvePromise) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] }) as ReturnType<typeof spawn> & {
      stdout: NodeJS.ReadableStream
      stderr: NodeJS.ReadableStream
      on(event: "error", listener: (error: Error) => void): void
      on(event: "close", listener: (status: number | null) => void): void
    }

    let stdout = ""
    let stderr = ""
    let timedOut = false

    const timer = setTimeout(() => {
      timedOut = true
      child.kill("SIGKILL")
    }, timeoutMs)

    child.stdout.on("data", (chunk) => {
      stdout += String(chunk)
    })

    child.stderr.on("data", (chunk) => {
      stderr += String(chunk)
    })

    child.on("error", (error: Error) => {
      clearTimeout(timer)
      resolvePromise({ status: null, stdout, stderr, timedOut, error: error.message })
    })

    child.on("close", (status: number | null) => {
      clearTimeout(timer)
      resolvePromise({ status, stdout, stderr, timedOut })
    })
  })
}

function parseEventResultMessage(stdout: string, expectFinal: boolean): string {
  const trimmed = stdout.trim()
  if (!trimmed) {
    return expectFinal ? "Vault update completed." : "Vault update task dispatched."
  }

  try {
    const parsed = asRecord(JSON.parse(trimmed))
    const status = parsed.status
    if (typeof status === "string" && status.trim().length > 0) {
      return status.trim()
    }

    const message = parsed.message
    if (typeof message === "string" && message.trim().length > 0) {
      return message.trim()
    }

    const id = parsed.id
    if (typeof id === "string" && id.trim().length > 0) {
      return expectFinal ? `Vault update completed (event ${id}).` : `Vault update task dispatched (event ${id}).`
    }
  } catch {
    // Non-JSON output; return concise single line.
  }

  const firstLine = trimmed.split(/\r?\n/u).find((line) => line.trim().length > 0)
  if (firstLine) {
    return firstLine.trim()
  }

  return expectFinal ? "Vault update completed." : "Vault update task dispatched."
}

export async function dispatchVaultUpdateTask(
  request: VaultUpdateTaskRequest,
  options: DispatchOptions,
): Promise<VaultUpdateTaskResult> {
  const log = options.logger ?? (() => undefined)
  const prompt = await getSystemPrompt(log)

  if (!prompt) {
    const message = "Failed to dispatch vault update: missing hook prompt."
    log(message)
    return { success: false, message }
  }

  const expectFinal = options.expectFinal === true
  const eventText = buildEventText(prompt, request, options.model?.trim() || undefined)
  const args = ["system", "event", "--text", eventText, "--mode", "now", "--json", "--timeout", "120000"]

  if (expectFinal) {
    args.push("--expect-final")
  }

  const result = await runCommand("openclaw", args, expectFinal ? FINAL_TIMEOUT_MS : EVENT_TIMEOUT_MS)

  if (result.error) {
    const message = `OpenClaw system event failed: ${result.error}`
    log(message)
    return { success: false, message }
  }

  if (result.timedOut) {
    const message = `OpenClaw system event timed out after ${String(expectFinal ? FINAL_TIMEOUT_MS : EVENT_TIMEOUT_MS)}ms`
    log(message)
    return { success: false, message }
  }

  if (result.status !== 0) {
    const stderr = result.stderr.trim()
    const message = stderr.length > 0 ? stderr : `openclaw exited with code ${String(result.status)}`
    log(`OpenClaw system event failed: ${message}`)
    return { success: false, message: `OpenClaw system event failed: ${message}` }
  }

  return {
    success: true,
    message: parseEventResultMessage(result.stdout, expectFinal),
  }
}
