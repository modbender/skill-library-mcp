import fs from "node:fs";
import path from "node:path";
import os from "node:os";
const DEFAULT_OPENCLAW_JSON = path.join(os.homedir(), ".openclaw", "openclaw.json");
export function getConfigPath() {
    return process.env.OPENCLAW_CONFIG ?? DEFAULT_OPENCLAW_JSON;
}
export function getConfig() {
    const configPath = getConfigPath();
    try {
        if (!fs.existsSync(configPath)) {
            return {};
        }
        const raw = fs.readFileSync(configPath, "utf-8");
        return JSON.parse(raw);
    }
    catch {
        console.error("Config unreadable, using defaults.");
        return {};
    }
}
//# sourceMappingURL=config.js.map