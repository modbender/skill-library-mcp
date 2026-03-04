/**
 * Discovery Sync (Standalone)
 *
 * Pulls newly discovered skills from the Taste Finder backend
 * and appends them to `bloom-discoveries.md` for agent context.
 *
 * Stateless — uses a JSON state file for dedup tracking.
 * Same pattern as recommendation-pipeline.ts.
 */

import * as fs from 'fs/promises';
import * as path from 'path';

// ─── Types ───────────────────────────────────────────────────────────────

export interface DiscoveryEntry {
  skillId: string;
  name: string;
  description: string;
  matchScore: number;
  source: string;        // e.g. "ClawHub", "Claude Code"
  installCommand?: string;
  url?: string;
}

interface DiscoveryState {
  syncedSkillIds: string[];
  lastSyncedAt: string | null;
}

export interface SyncDiscoveriesOptions {
  apiUrl?: string;
  outputDir?: string;
}

// ─── Constants ───────────────────────────────────────────────────────────

const MD_FILE = 'bloom-discoveries.md';
const STATE_FILE = '.bloom-discovery-state.json';

const MD_HEADER = `# Bloom Taste Finder — Discovered Skills
> Auto-updated. Your agent grows smarter over time.
`;

const HEADER_SENTINEL = '> Auto-updated. Your agent grows smarter over time.\n';
const MAX_SYNCED_IDS = 500;

// ─── State helpers ───────────────────────────────────────────────────────

async function loadState(stateFilePath: string): Promise<DiscoveryState> {
  try {
    const raw = await fs.readFile(stateFilePath, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return { syncedSkillIds: [], lastSyncedAt: null };
  }
}

async function saveState(stateFilePath: string, state: DiscoveryState): Promise<void> {
  await fs.writeFile(stateFilePath, JSON.stringify(state, null, 2), 'utf-8');
}

// ─── Markdown helpers ────────────────────────────────────────────────────

function formatDateHeading(count: number): string {
  const now = new Date();
  const month = now.toLocaleString('en-US', { month: 'short' });
  const day = now.getDate();
  const year = now.getFullYear();
  return `## ${month} ${day}, ${year} (${count} new)`;
}

function formatEntry(entry: DiscoveryEntry): string {
  const score = `${entry.matchScore}% match`;
  const source = entry.source || 'Unknown';
  const lines = [`- **${entry.name}** (${score}, ${source})`];
  if (entry.description) {
    lines.push(`  ${entry.description}`);
  }
  if (entry.installCommand) {
    lines.push(`  → \`${entry.installCommand}\``);
  } else if (entry.url) {
    lines.push(`  → ${entry.url}`);
  }
  return lines.join('\n');
}

async function appendToMd(mdFilePath: string, entries: DiscoveryEntry[]): Promise<void> {
  let existing = '';
  try {
    existing = await fs.readFile(mdFilePath, 'utf-8');
  } catch {
    // File doesn't exist yet — will create with header
  }

  const section = [
    '',
    formatDateHeading(entries.length),
    ...entries.map(formatEntry),
  ].join('\n');

  if (!existing) {
    // New file: header + first section
    await fs.writeFile(mdFilePath, MD_HEADER + section + '\n', 'utf-8');
  } else {
    // Insert new section right after the sentinel line (newest on top)
    const sentinelIndex = existing.indexOf(HEADER_SENTINEL);
    if (sentinelIndex !== -1) {
      const insertAt = sentinelIndex + HEADER_SENTINEL.length;
      const before = existing.slice(0, insertAt);
      const after = existing.slice(insertAt);
      await fs.writeFile(mdFilePath, before + section + '\n' + after, 'utf-8');
    } else {
      // Header was manually edited — append at end
      await fs.writeFile(mdFilePath, existing + section + '\n', 'utf-8');
    }
  }
}

// ─── Main ────────────────────────────────────────────────────────────────

/**
 * Sync newly discovered skills from the Taste Finder backend.
 *
 * 1. Fetch discoveries from GET /x402/agent/{agentUserId}/discoveries
 * 2. Filter out already-synced entries via state file
 * 3. Append new entries to bloom-discoveries.md
 * 4. Update state file
 */
export async function syncDiscoveries(
  agentUserId: number | string,
  options?: SyncDiscoveriesOptions,
): Promise<{ newCount: number; totalSynced: number }> {
  const apiUrl = options?.apiUrl || process.env.BLOOM_API_URL || 'https://api.bloomprotocol.ai';
  const outputDir = options?.outputDir || process.cwd();

  const mdFilePath = path.join(outputDir, MD_FILE);
  const stateFilePath = path.join(outputDir, STATE_FILE);

  console.log(`[discovery-sync] Fetching discoveries for agent ${agentUserId}...`);

  // 1. Fetch from backend
  const url = `${apiUrl}/x402/agent/${agentUserId}/discoveries`;
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Bloom-Identity-Skill',
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Discovery API returned ${response.status}: ${response.statusText}`);
  }

  const data = await response.json() as { discoveries?: DiscoveryEntry[] };
  const discoveries = data.discoveries || [];

  if (discoveries.length === 0) {
    console.log('[discovery-sync] No discoveries returned from API');
    return { newCount: 0, totalSynced: 0 };
  }

  // 2. Load state and filter already-synced
  const state = await loadState(stateFilePath);
  const syncedSet = new Set(state.syncedSkillIds);
  const newEntries = discoveries.filter(d => d.skillId && !syncedSet.has(d.skillId));

  if (newEntries.length === 0) {
    console.log(`[discovery-sync] All ${discoveries.length} discoveries already synced`);
    return { newCount: 0, totalSynced: syncedSet.size };
  }

  // 3. Append to markdown
  await appendToMd(mdFilePath, newEntries);
  console.log(`[discovery-sync] Appended ${newEntries.length} new discoveries to ${MD_FILE}`);

  // 4. Update state
  for (const entry of newEntries) {
    syncedSet.add(entry.skillId);
  }
  const allIds = Array.from(syncedSet);
  const updatedState: DiscoveryState = {
    // Keep only the most recent IDs to bound state file size
    syncedSkillIds: allIds.length > MAX_SYNCED_IDS ? allIds.slice(-MAX_SYNCED_IDS) : allIds,
    lastSyncedAt: new Date().toISOString(),
  };
  await saveState(stateFilePath, updatedState);

  return { newCount: newEntries.length, totalSynced: syncedSet.size };
}
