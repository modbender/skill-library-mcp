import fs from "node:fs";
import { execSync } from "node:child_process";
/**
 * Remove a worktree. Run from inside the worktree: git worktree remove --force .
 */
export async function removeWorktree(worktreePath) {
    if (!fs.existsSync(worktreePath)) {
        throw new Error("Worktree path does not exist or already removed");
    }
    try {
        execSync("git worktree remove --force .", {
            cwd: worktreePath,
            encoding: "utf-8",
        });
    }
    catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        throw new Error(`Could not remove worktree: ${msg}`);
    }
}
//# sourceMappingURL=remove.js.map