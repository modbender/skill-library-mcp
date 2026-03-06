import { execSync } from "node:child_process";
import path from "node:path";

export interface WorktreeInfo {
  path: string;
  taskId: string | null;
}

/**
 * Parse output of `git worktree list` and return worktrees under basePath.
 */
export function parseWorktreeListOutput(
  output: string,
  basePath: string,
  repoPath: string
): WorktreeInfo[] {
  const lines = output.trim().split("\n");
  const result: WorktreeInfo[] = [];
  const normalizedBase = path.resolve(basePath) + path.sep;

  for (const line of lines) {
    const worktreePath = line.split(/\s+/)[0];
    if (!worktreePath) continue;
    const resolved = path.isAbsolute(worktreePath)
      ? path.resolve(worktreePath)
      : path.resolve(repoPath, worktreePath);
    if (!resolved.startsWith(normalizedBase)) continue;
    const relative = path.relative(basePath, resolved);
    const taskId = relative.split(path.sep)[0] || null;
    result.push({ path: resolved, taskId });
  }

  return result;
}

export async function listWorktrees(
  repoPath: string,
  basePath: string
): Promise<WorktreeInfo[]> {
  const out = execSync("git worktree list", {
    cwd: repoPath,
    encoding: "utf-8",
  });
  return parseWorktreeListOutput(out, basePath, repoPath);
}
