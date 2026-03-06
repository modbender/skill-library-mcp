import { mkdir, readFile, writeFile } from "node:fs/promises"
import { dirname, join } from "node:path"

import { resolveJournalDirectory } from "./hook-paths"
import type { JournalSnapshot } from "./hook-types"

const DEFAULT_JOURNAL_TEMPLATE = `---
type: journal
tags: [journals]
created: {{DATE}}
updated: {{DATE}}
---
`

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

function getErrorCode(error: unknown): string | undefined {
  if (typeof error !== "object" || !error) {
    return undefined
  }

  const maybeCode = (error as { code?: unknown }).code
  return typeof maybeCode === "string" ? maybeCode : undefined
}

function renderJournalTemplate(template: string, dateStamp: string): string {
  const rendered = template
    .replaceAll("{{DATE}}", dateStamp)
    .replaceAll("{{CREATED_DATE}}", dateStamp)
    .replaceAll("{{UPDATED_DATE}}", dateStamp)
    .replaceAll('<% tp.date.now("YYYY-MM-DD") %>', dateStamp)

  return rendered.endsWith("\n") ? rendered : `${rendered}\n`
}

function resolveJournalTemplatePaths(vaultPath: string): string[] {
  return [join(vaultPath, "04 Templates", "journal.md"), join(vaultPath, "Templates", "journal.md")]
}

async function loadJournalTemplate(vaultPath: string, dateStamp: string): Promise<string> {
  for (const templatePath of resolveJournalTemplatePaths(vaultPath)) {
    try {
      const template = await readFile(templatePath, "utf8")
      if (template.trim().length === 0) {
        continue
      }

      return renderJournalTemplate(template, dateStamp)
    } catch {
      // Try the next template candidate path.
    }
  }

  return renderJournalTemplate(DEFAULT_JOURNAL_TEMPLATE, dateStamp)
}

async function ensureJournalExists(vaultPath: string, journalPath: string, dateStamp: string): Promise<string> {
  try {
    return await readFile(journalPath, "utf8")
  } catch (error) {
    if (getErrorCode(error) !== "ENOENT") {
      throw error
    }
  }

  const template = await loadJournalTemplate(vaultPath, dateStamp)
  await mkdir(dirname(journalPath), { recursive: true })

  try {
    await writeFile(journalPath, template, { encoding: "utf8", flag: "wx" })
    return template
  } catch (error) {
    if (getErrorCode(error) !== "EEXIST") {
      throw error
    }
  }

  return await readFile(journalPath, "utf8")
}

export async function readJournalSnapshot(vaultPath: string, timestamp: Date): Promise<JournalSnapshot> {
  const journalDir = await resolveJournalDirectory(vaultPath)
  const dateStamp = formatDate(timestamp)
  const journalFilename = `${dateStamp}.md`
  const journalPath = join(journalDir, journalFilename)

  let content = ""
  try {
    content = await ensureJournalExists(vaultPath, journalPath, dateStamp)
  } catch {
    // If journal read/create fails, continue with an empty journal snapshot.
  }

  return {
    journalPath,
    journalFilename,
    content,
  }
}
