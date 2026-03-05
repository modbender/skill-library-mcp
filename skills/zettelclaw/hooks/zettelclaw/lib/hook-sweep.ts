import { parseSweepConfig } from "./hook-config"
import { dispatchVaultUpdateFromTurns } from "./hook-dispatch"
import { collectTranscriptCandidates, resolveSessionDirectories } from "./hook-paths"
import { hashTurns, shouldRunSweep, updateSweepCursor } from "./hook-sweep-state"
import type { HookEvent, SweepRunResult, SweepState } from "./hook-types"
import { readSessionTurnsFromFile } from "./session"

export async function runTranscriptSweep(
  event: HookEvent,
  cfg: unknown,
  hookConfig: Record<string, unknown>,
  vaultPath: string,
  notesDirectory: string,
  state: SweepState,
): Promise<SweepRunResult> {
  const sweepConfig = parseSweepConfig(hookConfig)

  if (!(sweepConfig.enabled && shouldRunSweep(state, sweepConfig.intervalMinutes))) {
    return {
      ran: false,
      processedFiles: 0,
      dispatchedTasks: 0,
      failedFiles: 0,
      stateChanged: false,
    }
  }

  const nowIso = new Date().toISOString()
  let stateChanged = false

  const sessionDirs = await resolveSessionDirectories(event, cfg)
  if (sessionDirs.length === 0) {
    if (state.lastSweepAt !== nowIso) {
      state.lastSweepAt = nowIso
      stateChanged = true
    }

    return {
      ran: true,
      processedFiles: 0,
      dispatchedTasks: 0,
      failedFiles: 0,
      stateChanged,
    }
  }

  const candidates = await collectTranscriptCandidates(sessionDirs, sweepConfig.staleMinutes)
  let processedFiles = 0
  let dispatchedTasks = 0
  let failedFiles = 0
  let examinedFiles = 0

  for (const candidate of candidates) {
    const previous = state.files[candidate.path]

    if (previous && previous.mtimeMs === candidate.mtimeMs) {
      continue
    }

    if (examinedFiles >= sweepConfig.maxFiles) {
      break
    }

    examinedFiles += 1

    const turns = await readSessionTurnsFromFile(candidate.path)

    if (turns.length === 0) {
      const changed = updateSweepCursor(state, candidate.path, turns, candidate.mtimeMs, nowIso)
      stateChanged = stateChanged || changed
      continue
    }

    let startOffset = 0

    if (previous && previous.offset > 0 && previous.offset <= turns.length) {
      const currentPrefixHash = hashTurns(turns.slice(0, previous.offset))
      if (currentPrefixHash === previous.hash) {
        startOffset = previous.offset
      }
    }

    const pendingTurns = turns.slice(startOffset)

    if (pendingTurns.length < 2) {
      const changed = updateSweepCursor(state, candidate.path, turns, candidate.mtimeMs, nowIso)
      stateChanged = stateChanged || changed
      continue
    }

    const extractionTurns = pendingTurns.slice(-sweepConfig.messages)
    const extractionTimestamp = new Date(candidate.mtimeMs)
    const extraction = await dispatchVaultUpdateFromTurns({
      turns: extractionTurns,
      timestamp: extractionTimestamp,
      hookConfig,
      vaultPath,
      notesDirectory,
      conversationSource: "sweep",
      transcriptPath: candidate.path,
      expectFinal: false,
    })

    if (!extraction.success) {
      failedFiles += 1
      continue
    }

    const changed = updateSweepCursor(state, candidate.path, turns, candidate.mtimeMs, nowIso)
    stateChanged = stateChanged || changed

    processedFiles += 1
    if (extraction.dispatched) {
      dispatchedTasks += 1
    }
  }

  if (failedFiles === 0 && state.lastSweepAt !== nowIso) {
    state.lastSweepAt = nowIso
    stateChanged = true
  }

  return {
    ran: true,
    processedFiles,
    dispatchedTasks,
    failedFiles,
    stateChanged,
  }
}
