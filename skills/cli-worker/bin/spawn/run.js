import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { getSafeKimiCliPath } from "../safe-cli-path.js";
import { sanitizePrompt } from "../sanitize.js";
// Re-export sanitizePrompt for backward compatibility with existing tests
export { sanitizePrompt };
/**
 * Run Kimi CLI with prompt, capture stdout line-by-line.
 * Uses spawn() with an argument array (no shell) so the prompt is passed as
 * a single argv; prompt is sanitized to remove null bytes and control chars.
 */
export function runKimi(prompt, cwd, options = {}) {
    const safePrompt = sanitizePrompt(prompt);
    return new Promise((resolve, reject) => {
        const kimiCmd = getSafeKimiCliPath();
        const args = ["--print", "-p", safePrompt, "--output-format=stream-json"];
        const child = spawn(kimiCmd, args, {
            cwd,
            env: { ...process.env, KIMI_NO_BROWSER: "1" },
            stdio: ["pipe", "pipe", "pipe"],
        });
        const stdoutLines = [];
        const rl = createInterface({ input: child.stdout, crlfDelay: Infinity });
        rl.on("line", (line) => stdoutLines.push(line));
        let stderr = "";
        child.stderr?.on("data", (chunk) => {
            stderr += chunk.toString();
        });
        let timeoutId;
        if (options.timeoutMs && options.timeoutMs > 0) {
            timeoutId = setTimeout(() => {
                child.kill("SIGTERM");
                timeoutId = setTimeout(() => child.kill("SIGKILL"), 2000);
            }, options.timeoutMs);
        }
        child.on("error", (err) => {
            if (timeoutId)
                clearTimeout(timeoutId);
            reject(err);
        });
        child.on("close", (code, signal) => {
            if (timeoutId)
                clearTimeout(timeoutId);
            resolve({
                exitCode: code,
                signal: signal,
                stdoutLines,
                stderr,
            });
        });
    });
}
//# sourceMappingURL=run.js.map