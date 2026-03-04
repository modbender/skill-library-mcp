import { isIsolatedSession, isResetEvent } from "./lib/hook-config"
import { logWarning } from "./lib/hook-log"
import { resolveHookStatePath, resolveNotesDirectory } from "./lib/hook-paths"
import { processResetEventSession } from "./lib/hook-reset"
import { runTranscriptSweep } from "./lib/hook-sweep"
import { loadSweepState, saveSweepState } from "./lib/hook-sweep-state"
import type { HookHandler } from "./lib/hook-types"
import { asRecord } from "./lib/json"
import { resolveVaultPath } from "./lib/vault-path"

export const handler: HookHandler = async (event) => {
  try {
    if (!isResetEvent(event)) {
      return
    }

    const cfg = event.context?.cfg ?? {}
    const hooks = asRecord(asRecord(asRecord(cfg).hooks).internal)
    const entries = asRecord(hooks.entries)
    const hookConfig = asRecord(entries.zettelclaw)

    const vaultPath = await resolveVaultPath(cfg, hookConfig)
    if (!vaultPath) {
      const message = "No vault path found; skipping vault update dispatch."
      logWarning(message)
      event.messages.push(`🦞 ${message}`)
      return
    }

    const notesDirectory = await resolveNotesDirectory(vaultPath)
    if (!notesDirectory) {
      const message = `No Notes folder found in vault: ${vaultPath}`
      logWarning(message)
      event.messages.push(`🦞 ${message}`)
      return
    }

    const statePath = resolveHookStatePath()
    const state = await loadSweepState(statePath)
    let stateChanged = false

    if (!isIsolatedSession(event.sessionKey)) {
      const resetResult = await processResetEventSession(event, hookConfig, vaultPath, notesDirectory, state)
      if (resetResult.message) {
        event.messages.push(resetResult.message)
      }

      stateChanged = stateChanged || resetResult.stateChanged
    }

    const sweepResult = await runTranscriptSweep(event, cfg, hookConfig, vaultPath, notesDirectory, state)
    stateChanged = stateChanged || sweepResult.stateChanged

    if (sweepResult.ran && sweepResult.processedFiles > 0) {
      const dispatchSuffix =
        sweepResult.dispatchedTasks > 0 ? `, dispatched ${sweepResult.dispatchedTasks} vault update tasks` : ""
      event.messages.push(`🦞 Sweep backfilled ${sweepResult.processedFiles} session files${dispatchSuffix}`)
    }

    if (sweepResult.failedFiles > 0) {
      event.messages.push(`🦞 Sweep skipped ${sweepResult.failedFiles} files due to dispatch errors`)
    }

    if (stateChanged) {
      try {
        await saveSweepState(statePath, state)
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error)
        logWarning(`Could not persist sweep state: ${message}`)
      }
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    logWarning(`Unexpected error: ${message}`)
    event.messages.push(`🦞 Hook failed: ${message}`)
  }
}

export default handler
