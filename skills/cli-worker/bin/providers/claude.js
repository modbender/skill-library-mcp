/**
 * Claude Code CLI Provider implementation.
 *
 * Claude CLI docs: https://docs.anthropic.com/en/docs/claude-code/headless
 * - Command: `claude` (or CLAUDE_CLI_PATH env)
 * - Headless: `claude -p "<prompt>" --output-format stream-json`
 * - Auth: ANTHROPIC_API_KEY environment variable
 * - Output: NDJSON with stream_event/text_delta events
 */
import { spawn, spawnSync } from "node:child_process";
import { createInterface } from "node:readline";
import { sanitizePrompt } from "../sanitize.js";
/**
 * Safe CLI executable path for Claude subprocess calls.
 * Same validation as KIMI_CLI_PATH.
 */
// eslint-disable-next-line no-control-regex
const SAFE_CLI_PATH_REGEX = /^[^\s;|&$`"'<>\x00-\x1f]+$/;
const MAX_LEN = 512;
function getSafeClaudeCliPath() {
    const raw = process.env.CLAUDE_CLI_PATH;
    if (raw == null || raw === "")
        return "claude";
    if (raw.length > MAX_LEN)
        return "claude";
    if (!SAFE_CLI_PATH_REGEX.test(raw))
        return "claude";
    return raw;
}
/**
 * Parse Claude stream-json output.
 * Accumulates text_delta events to form finalText.
 */
export function parseClaudeStreamJson(lines) {
    const raw = [];
    let finalTextBuffer = "";
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed)
            continue;
        try {
            const obj = JSON.parse(trimmed);
            raw.push(obj);
            // Handle stream_event with text_delta
            if (obj.type === "stream_event" &&
                obj.event?.delta?.type === "text_delta") {
                if (typeof obj.event.delta.text === "string") {
                    finalTextBuffer += obj.event.delta.text;
                }
            }
        }
        catch {
            // skip non-JSON lines
        }
    }
    return { finalText: finalTextBuffer, raw };
}
export class ClaudeProvider {
    id = "claude";
    displayName = "Claude Code";
    /**
     * Verify Claude CLI is installed and authenticated.
     * Runs `claude -p "Reply OK"` and checks exit code 0.
     */
    verify() {
        const claudeCmd = getSafeClaudeCliPath();
        // Check for API key in environment for better error messages
        if (!process.env.ANTHROPIC_API_KEY) {
            // Still try to run, but Claude might fail - we let the run result speak
        }
        const result = spawnSync(claudeCmd, ["-p", "Reply OK", "--output-format", "stream-json"], {
            encoding: "utf-8",
            timeout: 30_000,
            stdio: ["pipe", "pipe", "pipe"],
            shell: false,
        });
        if (result.status === 0) {
            return { ok: true };
        }
        const msg = result.error?.message ?? result.stderr?.trim() ?? `exit ${result.status}`;
        // Provide helpful error for missing API key
        if (!process.env.ANTHROPIC_API_KEY && msg.toLowerCase().includes("auth")) {
            return {
                ok: false,
                reason: "auth_failed",
                detail: `Claude CLI authentication failed. Set ANTHROPIC_API_KEY environment variable. Error: ${msg}`,
            };
        }
        return {
            ok: false,
            reason: "run_failed",
            detail: `Claude CLI run failed: ${msg}. Ensure 'claude' is on PATH and ANTHROPIC_API_KEY is set.`,
        };
    }
    /**
     * Run Claude CLI with a prompt.
     * Uses spawn() with an argument array (no shell).
     * Prompt is sanitized before passing.
     */
    run(prompt, cwd, options = {}) {
        const safePrompt = sanitizePrompt(prompt);
        return new Promise((resolve, reject) => {
            const claudeCmd = getSafeClaudeCliPath();
            const args = ["-p", safePrompt, "--output-format", "stream-json"];
            const child = spawn(claudeCmd, args, {
                cwd,
                env: process.env, // Uses ANTHROPIC_API_KEY from environment
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
    /**
     * Parse Claude stream-json output.
     * Accumulates text_delta events.
     */
    parseStdout(lines) {
        return parseClaudeStreamJson(lines);
    }
    /**
     * Get the report subdirectory name.
     */
    reportSubdir() {
        return "claude-reports";
    }
    /**
     * Get the AGENTS.md title.
     */
    agentsMdTitle() {
        return "OpenClaw Claude Worker - Task Instructions";
    }
}
/** Singleton instance */
export const claudeProvider = new ClaudeProvider();
//# sourceMappingURL=claude.js.map