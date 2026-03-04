import { getRepoPath, getWorktreeBasePath } from "../worktree/repo.js";
import { listWorktrees } from "../worktree/list.js";
import { removeWorktree } from "../worktree/remove.js";
import { resolveTaskIdPath } from "../safe-task-id.js";
export async function runWorktree(args) {
    const sub = args[0];
    if (sub === "list") {
        const cwd = process.cwd();
        const rest = args.slice(1);
        let repoFlag;
        for (let i = 0; i < rest.length; i++) {
            if (rest[i] === "--repo" && rest[i + 1]) {
                repoFlag = rest[i + 1];
                break;
            }
        }
        const repoPath = getRepoPath(cwd, repoFlag);
        const basePath = getWorktreeBasePath();
        try {
            const worktrees = await listWorktrees(repoPath, basePath);
            if (worktrees.length === 0) {
                console.log("No worktrees found.");
                return 0;
            }
            for (const wt of worktrees) {
                console.log(`${wt.taskId ?? "?"}\t${wt.path}`);
            }
            return 0;
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : String(err);
            if (msg.includes("not a git repository") || msg.includes("git")) {
                console.error("Not a git repository. Run from repo root or use --repo <path>.");
            }
            else {
                console.error("Failed to list worktrees:", msg);
            }
            return 1;
        }
    }
    if (sub === "remove") {
        const taskId = args[1];
        if (!taskId) {
            console.error("Usage: cli-worker worktree remove <taskId>");
            return 1;
        }
        const basePath = getWorktreeBasePath();
        const worktreePath = resolveTaskIdPath(basePath, taskId);
        if (!worktreePath) {
            console.error("Invalid taskId: must be alphanumeric and hyphens only (no path traversal).");
            return 1;
        }
        try {
            await removeWorktree(worktreePath);
            console.log(`Removed worktree: ${worktreePath}`);
            return 0;
        }
        catch (err) {
            console.error("Remove failed:", err instanceof Error ? err.message : err);
            return 1;
        }
    }
    console.error("Usage: cli-worker worktree list | remove <taskId>");
    return 1;
}
//# sourceMappingURL=worktree.js.map