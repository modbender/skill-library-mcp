import fs from "node:fs";
import { listWorktrees } from "../worktree/list.js";
import { removeWorktree } from "../worktree/remove.js";

export interface CleanupResult {
  removed: number;
  failures: string[];
}

/**
 * List worktrees under basePath, remove those older than olderThanHours (by dir mtime).
 * Returns number of worktrees removed and any failure messages.
 */
export async function cleanupWorktrees(
  repoPath: string,
  basePath: string,
  olderThanHours: number
): Promise<CleanupResult> {
  const worktrees = await listWorktrees(repoPath, basePath);
  const cutoff = Date.now() - olderThanHours * 60 * 60 * 1000;
  let removed = 0;
  const failures: string[] = [];

  for (const wt of worktrees) {
    try {
      const stat = fs.statSync(wt.path);
      if (stat.mtimeMs < cutoff) {
        await removeWorktree(wt.path);
        removed++;
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      failures.push(`Failed to remove ${wt.path}: ${msg}`);
    }
  }

  return { removed, failures };
}
