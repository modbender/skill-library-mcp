import { createHash } from "node:crypto"
import { mkdir, readFile, writeFile } from "node:fs/promises"
import { dirname } from "node:path"
import type { SweepCursor, SweepState } from "./hook-types"
import { asRecord } from "./json"
import type { ConversationTurn } from "./session"

const HOOK_STATE_VERSION = 1
const MAX_SWEEP_STATE_ENTRIES = 4_000

export function createEmptySweepState(): SweepState {
  return {
    version: HOOK_STATE_VERSION,
    files: {},
  }
}

export async function loadSweepState(statePath: string): Promise<SweepState> {
  try {
    const raw = await readFile(statePath, "utf8")
    const parsed = asRecord(JSON.parse(raw))
    const filesRecord = asRecord(parsed.files)

    const files: Record<string, SweepCursor> = {}

    for (const [filePath, rawCursor] of Object.entries(filesRecord)) {
      const cursor = asRecord(rawCursor)
      const offset =
        typeof cursor.offset === "number" && Number.isFinite(cursor.offset) ? Math.max(0, cursor.offset) : 0
      const hash = typeof cursor.hash === "string" ? cursor.hash : ""
      const mtimeMs = typeof cursor.mtimeMs === "number" && Number.isFinite(cursor.mtimeMs) ? cursor.mtimeMs : 0
      const updatedAt = typeof cursor.updatedAt === "string" ? cursor.updatedAt : new Date(0).toISOString()

      if (hash.length === 0) {
        continue
      }

      files[filePath] = {
        offset,
        hash,
        mtimeMs,
        updatedAt,
      }
    }

    const state: SweepState = {
      version: HOOK_STATE_VERSION,
      files,
    }

    if (typeof parsed.lastSweepAt === "string") {
      state.lastSweepAt = parsed.lastSweepAt
    }

    return state
  } catch {
    return createEmptySweepState()
  }
}

export async function saveSweepState(statePath: string, state: SweepState): Promise<void> {
  const trimmedEntries = Object.entries(state.files)

  if (trimmedEntries.length > MAX_SWEEP_STATE_ENTRIES) {
    trimmedEntries.sort((a, b) => {
      const left = Date.parse(a[1].updatedAt)
      const right = Date.parse(b[1].updatedAt)
      return right - left
    })

    state.files = Object.fromEntries(trimmedEntries.slice(0, MAX_SWEEP_STATE_ENTRIES))
  }

  await mkdir(dirname(statePath), { recursive: true })
  await writeFile(statePath, `${JSON.stringify(state, null, 2)}\n`, "utf8")
}

export function hashTurns(turns: ConversationTurn[]): string {
  const hash = createHash("sha256")

  for (const turn of turns) {
    hash.update(turn.role)
    hash.update("\u0000")
    hash.update(turn.content)
    hash.update("\u0000")
  }

  return hash.digest("hex")
}

export function updateSweepCursor(
  state: SweepState,
  transcriptPath: string,
  turns: ConversationTurn[],
  mtimeMs: number,
  timestamp: string,
): boolean {
  const cursor: SweepCursor = {
    offset: turns.length,
    hash: hashTurns(turns),
    mtimeMs,
    updatedAt: timestamp,
  }

  const previous = state.files[transcriptPath]
  if (
    previous &&
    previous.offset === cursor.offset &&
    previous.hash === cursor.hash &&
    previous.mtimeMs === cursor.mtimeMs &&
    previous.updatedAt === cursor.updatedAt
  ) {
    return false
  }

  state.files[transcriptPath] = cursor
  return true
}

export function shouldRunSweep(state: SweepState, intervalMinutes: number): boolean {
  if (!state.lastSweepAt) {
    return true
  }

  const lastSweepMs = Date.parse(state.lastSweepAt)
  if (!Number.isFinite(lastSweepMs)) {
    return true
  }

  return Date.now() - lastSweepMs >= intervalMinutes * 60_000
}
