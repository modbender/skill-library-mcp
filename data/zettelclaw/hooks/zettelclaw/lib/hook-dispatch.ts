import { dispatchVaultUpdateTask } from "./extract"
import { readJournalSnapshot } from "./hook-journal"
import { logWarning } from "./hook-log"
import type { ExtractResult } from "./hook-types"
import type { ConversationTurn } from "./session"

function buildConversationTranscript(turns: ConversationTurn[]): string {
  return turns
    .map((turn) => `${turn.role === "user" ? "User" : "Assistant"}: ${turn.content}`)
    .join("\n\n")
    .trim()
}

export async function dispatchVaultUpdateFromTurns(input: {
  turns: ConversationTurn[]
  timestamp: Date
  hookConfig: Record<string, unknown>
  vaultPath: string
  notesDirectory: string
  conversationSource: "command-reset" | "sweep"
  sessionId?: string
  transcriptPath?: string
  expectFinal: boolean
}): Promise<ExtractResult> {
  if (input.turns.length === 0) {
    return { success: true, dispatched: false, message: "No extractable insights from this session" }
  }

  const transcript = buildConversationTranscript(input.turns)
  if (transcript.length === 0) {
    return { success: true, dispatched: false, message: "No extractable insights from this session" }
  }

  const journal = await readJournalSnapshot(input.vaultPath, input.timestamp)
  const request = {
    conversation: transcript,
    conversationSource: input.conversationSource,
    timestampIso: input.timestamp.toISOString(),
    vaultPath: input.vaultPath,
    notesDirectory: input.notesDirectory,
    journalFilename: journal.journalFilename,
    journalPath: journal.journalPath,
    journalContent: journal.content,
    ...(typeof input.sessionId === "string" && input.sessionId.length > 0 ? { sessionId: input.sessionId } : {}),
    ...(typeof input.transcriptPath === "string" && input.transcriptPath.length > 0
      ? { transcriptPath: input.transcriptPath }
      : {}),
  }

  const dispatch = await dispatchVaultUpdateTask(request, {
    expectFinal: input.expectFinal,
    model: typeof input.hookConfig.model === "string" ? input.hookConfig.model : undefined,
    logger: logWarning,
  })

  if (!dispatch.success) {
    return { success: false, dispatched: false, message: dispatch.message ?? "Could not dispatch vault update task" }
  }

  if (typeof dispatch.message === "string" && dispatch.message.length > 0) {
    return {
      success: true,
      dispatched: true,
      message: dispatch.message,
    }
  }

  return { success: true, dispatched: true }
}
