import fs from "node:fs";
import path from "node:path";
import os from "node:os";
function getLogDir() {
    return (process.env.OPENCLAW_LOG_DIR ?? path.join(os.homedir(), ".openclaw", "logs"));
}
const LOG_FILE = () => path.join(getLogDir(), "cli-worker.log");
const ROTATE_THRESHOLD = 10 * 1024 * 1024; // 10MB
function ensureLogDir() {
    const dir = getLogDir();
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}
function maybeRotate() {
    const file = LOG_FILE();
    if (!fs.existsSync(file))
        return;
    const stat = fs.statSync(file);
    if (stat.size >= ROTATE_THRESHOLD) {
        const rotated = `${file}.${Date.now()}.bak`;
        fs.renameSync(file, rotated);
    }
}
export function log(level, message) {
    ensureLogDir();
    maybeRotate();
    const line = `${new Date().toISOString()} [${level}] ${message}\n`;
    fs.appendFileSync(LOG_FILE(), line, "utf-8");
}
export function logInfo(message) {
    log("INFO", message);
}
export function logError(message) {
    log("ERROR", message);
}
//# sourceMappingURL=logging.js.map