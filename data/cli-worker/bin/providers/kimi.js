/**
 * Kimi CLI Provider implementation.
 * Delegates to existing auth, spawn, and parser modules.
 */
import { verifyAll } from "../auth/verify.js";
import { runKimi } from "../spawn/run.js";
import { parseStreamJson } from "../parser/stream-json.js";
export class KimiProvider {
    id = "kimi";
    displayName = "Kimi CLI";
    /**
     * Verify Kimi CLI is installed and authenticated.
     * Delegates to verifyAll() from auth/verify module.
     */
    verify() {
        return verifyAll();
    }
    /**
     * Run Kimi CLI with a prompt.
     * Delegates to runKimi() from spawn/run module.
     * Sanitization is handled internally by runKimi.
     */
    run(prompt, cwd, options) {
        return runKimi(prompt, cwd, options);
    }
    /**
     * Parse Kimi stream-json output.
     * Delegates to parseStreamJson() from parser/stream-json module.
     */
    parseStdout(lines) {
        return parseStreamJson(lines);
    }
    /**
     * Get the report subdirectory name.
     */
    reportSubdir() {
        return "kimi-reports";
    }
    /**
     * Get the AGENTS.md title.
     */
    agentsMdTitle() {
        return "OpenClaw Kimi Worker - Task Instructions";
    }
}
/** Singleton instance */
export const kimiProvider = new KimiProvider();
//# sourceMappingURL=kimi.js.map