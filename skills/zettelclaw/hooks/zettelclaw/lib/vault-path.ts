import { access, readdir } from "node:fs/promises"
import { homedir } from "node:os"
import { join, resolve } from "node:path"

import { FALLBACK_VAULT_CANDIDATES } from "./folders"
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

async function hasObsidianVault(pathToDir: string): Promise<boolean> {
  try {
    await access(join(pathToDir, ".obsidian"))
    return true
  } catch {
    return false
  }
}

async function findVaultPath(candidatePath: string): Promise<string | null> {
  const resolved = resolve(expandHome(candidatePath))

  if (await hasObsidianVault(resolved)) {
    return resolved
  }

  const nestedVault = join(resolved, "vault")
  if (await hasObsidianVault(nestedVault)) {
    return nestedVault
  }

  try {
    const entries = await readdir(resolved, { withFileTypes: true })

    const sortedDirectories = entries
      .filter((entry) => entry.isDirectory())
      .sort((a, b) => a.name.localeCompare(b.name))

    for (const entry of sortedDirectories) {
      const childPath = join(resolved, entry.name)
      if (await hasObsidianVault(childPath)) {
        return childPath
      }
    }
  } catch {
    return null
  }

  return null
}

function readExtraPathsFromConfig(cfg: unknown): unknown[] {
  const cfgRecord = asRecord(cfg)

  const directMemorySearch = asRecord(cfgRecord.memorySearch)
  const agents = asRecord(cfgRecord.agents)
  const defaults = asRecord(agents.defaults)
  const defaultMemorySearch = asRecord(defaults.memorySearch)

  const directPaths = Array.isArray(directMemorySearch.extraPaths) ? directMemorySearch.extraPaths : []
  const defaultPaths = Array.isArray(defaultMemorySearch.extraPaths) ? defaultMemorySearch.extraPaths : []

  return [...directPaths, ...defaultPaths]
}

export async function resolveVaultPath(cfg: unknown, hookConfig: unknown): Promise<string | null> {
  const hookRecord = asRecord(hookConfig)
  const explicitVaultPath = hookRecord.vaultPath

  if (typeof explicitVaultPath === "string" && explicitVaultPath.trim().length > 0) {
    const resolvedExplicit = resolve(expandHome(explicitVaultPath.trim()))
    const discovered = await findVaultPath(resolvedExplicit)
    return discovered ?? resolvedExplicit
  }

  for (const candidate of readExtraPathsFromConfig(cfg)) {
    if (typeof candidate !== "string" || candidate.trim().length === 0) {
      continue
    }

    const resolved = await findVaultPath(candidate)
    if (resolved) {
      return resolved
    }
  }

  for (const candidate of FALLBACK_VAULT_CANDIDATES) {
    const resolved = await findVaultPath(candidate)
    if (resolved) {
      return resolved
    }
  }

  return null
}
