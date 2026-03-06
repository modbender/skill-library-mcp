import path from "node:path";
import os from "node:os";
import { getConfig } from "../config.js";
/**
 * Detect repo path from cwd or --repo flag. Default: process.cwd().
 */
export function getRepoPath(cwd, repoFlag) {
    if (repoFlag)
        return path.resolve(cwd, repoFlag);
    return cwd;
}
const DEFAULT_WORKTREE_BASE = "~/.openclaw/worktrees/kimi";
export function getWorktreeBasePath() {
    const config = getConfig();
    const base = config.worktree?.basePath ?? DEFAULT_WORKTREE_BASE;
    if (typeof base !== "string")
        return DEFAULT_WORKTREE_BASE;
    if (base.startsWith("~/")) {
        return path.join(os.homedir(), base.slice(2));
    }
    return base;
}
//# sourceMappingURL=repo.js.map