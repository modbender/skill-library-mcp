import { readdir, stat } from "node:fs/promises"
import { homedir } from "node:os"
import { dirname, join, resolve } from "node:path"

import { JOURNAL_FOLDER_CANDIDATES, NOTES_FOLDER_CANDIDATES } from "./folders"
import { isDirectory, pathExists } from "./hook-fs"
import type { HookEvent, TranscriptCandidate } from "./hook-types"
import { asRecord } from "./json"

function expandHome(inputPath: string): string {
  if (inputPath === "~") {
    return homedir()
  }

  if (inputPath.startsWith("~/")) {
    return resolve(homedir(), inputPath.slice(2))
  }

  return inputPath
}

export async function resolveNotesDirectory(vaultPath: string): Promise<string | null> {
  for (const folder of NOTES_FOLDER_CANDIDATES) {
    const candidate = join(vaultPath, folder)
    if (await pathExists(candidate)) {
      return candidate
    }
  }

  return null
}

export async function resolveJournalDirectory(vaultPath: string): Promise<string> {
  for (const folder of JOURNAL_FOLDER_CANDIDATES) {
    const candidate = join(vaultPath, folder)
    if (await pathExists(candidate)) {
      return candidate
    }
  }

  return join(vaultPath, JOURNAL_FOLDER_CANDIDATES[0])
}

export function resolveOpenClawStateDir(): string {
  const envPath = process.env.OPENCLAW_STATE_DIR
  if (typeof envPath === "string" && envPath.trim().length > 0) {
    return resolve(expandHome(envPath.trim()))
  }

  return join(homedir(), ".openclaw")
}

export function resolveWorkspaceDir(cfg: unknown, eventWorkspaceDir: unknown): string {
  if (typeof eventWorkspaceDir === "string" && eventWorkspaceDir.trim().length > 0) {
    return resolve(expandHome(eventWorkspaceDir.trim()))
  }

  const cfgRecord = asRecord(cfg)
  const directWorkspace = cfgRecord.workspace
  if (typeof directWorkspace === "string" && directWorkspace.trim().length > 0) {
    return resolve(expandHome(directWorkspace.trim()))
  }

  const agents = asRecord(cfgRecord.agents)
  const defaults = asRecord(agents.defaults)
  const defaultsWorkspace = defaults.workspace
  if (typeof defaultsWorkspace === "string" && defaultsWorkspace.trim().length > 0) {
    return resolve(expandHome(defaultsWorkspace.trim()))
  }

  return join(resolveOpenClawStateDir(), "workspace")
}

export function resolveHookStatePath(): string {
  return join(resolveOpenClawStateDir(), "hooks", "zettelclaw", "state.json")
}

function extractSessionFilePath(entryValue: unknown): string | null {
  const entry = asRecord(entryValue)
  const sessionFile = entry.sessionFile

  if (typeof sessionFile === "string" && sessionFile.trim().length > 0) {
    return resolve(sessionFile)
  }

  return null
}

export async function resolveSessionDirectories(event: HookEvent, cfg: unknown): Promise<string[]> {
  const stateDir = resolveOpenClawStateDir()
  const context = asRecord(event.context)
  const workspaceDir = resolveWorkspaceDir(cfg, context.workspaceDir)

  const directories = new Set<string>()

  const contextSessionFile = context.sessionFile
  if (typeof contextSessionFile === "string" && contextSessionFile.trim().length > 0) {
    directories.add(dirname(resolve(contextSessionFile)))
  }

  const entrySessionFile = extractSessionFilePath(context.sessionEntry)
  if (entrySessionFile) {
    directories.add(dirname(entrySessionFile))
  }

  const previousSessionFile = extractSessionFilePath(context.previousSessionEntry)
  if (previousSessionFile) {
    directories.add(dirname(previousSessionFile))
  }

  directories.add(join(workspaceDir, "sessions"))
  directories.add(join(stateDir, "workspace", "sessions"))

  const existingDirectories: string[] = []
  for (const candidate of directories) {
    if (await isDirectory(candidate)) {
      existingDirectories.push(candidate)
    }
  }

  existingDirectories.sort((left, right) => left.localeCompare(right))
  return existingDirectories
}

function isTranscriptFilename(name: string): boolean {
  return /\.jsonl(?:\.reset\..+)?$/u.test(name)
}

export async function collectTranscriptCandidates(
  sessionDirs: readonly string[],
  staleMinutes: number,
): Promise<TranscriptCandidate[]> {
  const staleCutoffMs = Date.now() - staleMinutes * 60_000
  const candidates = new Map<string, TranscriptCandidate>()

  for (const sessionDir of sessionDirs) {
    const entries = await readdir(sessionDir, { withFileTypes: true, encoding: "utf8" }).catch(() => null)
    if (!entries) {
      continue
    }

    for (const entry of entries) {
      if (!(entry.isFile() && isTranscriptFilename(entry.name))) {
        continue
      }

      const transcriptPath = resolve(join(sessionDir, entry.name))
      let transcriptStat: Awaited<ReturnType<typeof stat>>

      try {
        transcriptStat = await stat(transcriptPath)
      } catch {
        continue
      }

      if (!entry.name.includes(".reset.") && transcriptStat.mtimeMs > staleCutoffMs) {
        continue
      }

      const existing = candidates.get(transcriptPath)
      if (!existing || transcriptStat.mtimeMs > existing.mtimeMs) {
        candidates.set(transcriptPath, {
          path: transcriptPath,
          mtimeMs: transcriptStat.mtimeMs,
        })
      }
    }
  }

  const sorted = [...candidates.values()]
  sorted.sort((left, right) => left.mtimeMs - right.mtimeMs)
  return sorted
}
