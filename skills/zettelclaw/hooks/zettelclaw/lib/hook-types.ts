export interface HookEvent {
  type: string
  action: string
  sessionKey: string
  timestamp: Date
  messages: string[]
  context: {
    cfg?: unknown
    sessionEntry?: unknown
    previousSessionEntry?: unknown
    sessionId?: string
    sessionFile?: string
    commandSource?: string
    senderId?: string
    workspaceDir?: string
  }
}

export type HookHandler = (event: HookEvent) => Promise<void>

export interface SweepCursor {
  offset: number
  hash: string
  mtimeMs: number
  updatedAt: string
}

export interface SweepState {
  version: number
  lastSweepAt?: string
  files: Record<string, SweepCursor>
}

export interface SweepRunResult {
  ran: boolean
  processedFiles: number
  dispatchedTasks: number
  failedFiles: number
  stateChanged: boolean
}

export interface SweepConfig {
  enabled: boolean
  intervalMinutes: number
  messages: number
  maxFiles: number
  staleMinutes: number
}

export interface ExtractResult {
  success: boolean
  dispatched: boolean
  message?: string
}

export interface TranscriptCandidate {
  path: string
  mtimeMs: number
}

export interface JournalSnapshot {
  journalPath: string
  journalFilename: string
  content: string
}
