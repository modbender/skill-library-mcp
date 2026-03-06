import { getRepoPath, getWorktreeBasePath } from "../worktree/repo.js";
import { cleanupWorktrees } from "../cleanup/run.js";
import { logInfo } from "../logging.js";
const DEFAULT_OLDER_THAN_HOURS = 24;
export async function runCleanup(args) {
    let olderThanHours = DEFAULT_OLDER_THAN_HOURS;
    const cwd = process.cwd();
    let repoPath = cwd;
    let repoFlag;
    for (let i = 0; i < args.length; i++) {
        if (args[i] === "--older-than" && args[i + 1]) {
            const n = parseInt(args[i + 1], 10);
            if (Number.isFinite(n) && n > 0)
                olderThanHours = n;
            i++;
        }
        if (args[i] === "--repo" && args[i + 1]) {
            repoFlag = args[i + 1];
            i++;
        }
    }
    repoPath = getRepoPath(cwd, repoFlag);
    const basePath = getWorktreeBasePath();
    try {
        const { removed, failures } = await cleanupWorktrees(repoPath, basePath, olderThanHours);
        logInfo(`cleanup: removed ${removed} worktree(s) older than ${olderThanHours}h`);
        if (removed > 0)
            console.log(`Removed ${removed} worktree(s).`);
        for (const failure of failures) {
            console.error(failure);
        }
        return failures.length > 0 ? 1 : 0;
    }
    catch (err) {
        console.error("Cleanup failed:", err instanceof Error ? err.message : err);
        return 1;
    }
}
//# sourceMappingURL=cleanup.js.map