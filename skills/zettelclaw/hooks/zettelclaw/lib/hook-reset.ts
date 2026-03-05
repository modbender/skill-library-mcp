import { stat } from "node:fs/promises"

import { parseExpectFinal, parseMessageCount, toDate } from "./hook-config"
import { dispatchVaultUpdateFromTurns } from "./hook-dispatch"
import { updateSweepCursor } from "./hook-sweep-state"
import type { HookEvent, SweepState } from "./hook-types"
import { readRecentSessionMessagesWithSource, readSessionTurnsFromFile } from "./session"

export async function processResetEventSession(
  event: HookEvent,
  hookConfig: Record<string, unknown>,
  vaultPath: string,
  notesDirectory: string,
  state: SweepState,
): Promise<{ message?: string; stateChanged: boolean }> {
  const messageLimit = parseMessageCount(hookConfig.messages)
  const expectFinal = parseExpectFinal(hookConfig.expectFinal)
  const session = await readRecentSessionMessagesWithSource(event, messageLimit)

  if (session.turns.length === 0) {
    return { message: "🦞 No extractable insights from this session", stateChanged: false }
  }

  const eventDate = toDate(event.timestamp)
  const extraction = await dispatchVaultUpdateFromTurns({
    turns: session.turns,
    timestamp: eventDate,
    hookConfig,
    vaultPath,
    notesDirectory,
    conversationSource: "command-reset",
    expectFinal,
    ...(typeof event.context?.sessionId === "string" && event.context.sessionId.length > 0
      ? { sessionId: event.context.sessionId }
      : {}),
    ...(typeof session.sourceFile === "string" && session.sourceFile.length > 0
      ? { transcriptPath: session.sourceFile }
      : {}),
  })

  if (!extraction.success) {
    return {
      message: `🦞 ${extraction.message ?? "Could not dispatch vault update task"}`,
      stateChanged: false,
    }
  }

  let stateChanged = false

  if (session.sourceFile) {
    try {
      const allTurns = await readSessionTurnsFromFile(session.sourceFile)
      const transcriptStat = await stat(session.sourceFile)
      stateChanged = updateSweepCursor(
        state,
        session.sourceFile,
        allTurns,
        transcriptStat.mtimeMs,
        new Date().toISOString(),
      )
    } catch {
      // If cursor update fails, sweep will catch up on next pass.
    }
  }

  return {
    message: `🦞 ${extraction.message ?? (expectFinal ? "Vault update completed" : "Vault update task dispatched")}`,
    stateChanged,
  }
}
