import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
import { getSafeKimiCliPath } from "../safe-cli-path.js";
function getKimiHome() {
    return process.env.KIMI_HOME ?? path.join(os.homedir(), ".kimi");
}
function getConfigPath() {
    return path.join(getKimiHome(), "config.toml");
}
function getCredentialsDir() {
    return path.join(getKimiHome(), "credentials");
}
/**
 * Check that ~/.kimi/config.toml exists.
 */
export function verifyConfigExists() {
    const configPath = getConfigPath();
    if (!fs.existsSync(configPath)) {
        return {
            ok: false,
            reason: "config_missing",
            detail: `Kimi config not found at ${configPath}. Run 'kimi' then '/login' to authenticate.`,
        };
    }
    return { ok: true };
}
/**
 * Check that credentials exist: ~/.kimi/credentials/ (or OAuth key path from config).
 * For simplicity we check credentials dir exists; config may point to a different path later.
 */
export function verifyCredentials() {
    const configOk = verifyConfigExists();
    if (!configOk.ok)
        return configOk;
    const credentialsDir = getCredentialsDir();
    if (fs.existsSync(credentialsDir)) {
        const entries = fs.readdirSync(credentialsDir, { withFileTypes: true });
        const hasFile = entries.some((e) => e.isFile());
        if (hasFile)
            return { ok: true };
    }
    const kimiHome = getKimiHome();
    const keyPaths = [
        path.join(kimiHome, "credentials", "kimi-code.json"),
        path.join(kimiHome, "token"),
    ];
    for (const p of keyPaths) {
        if (fs.existsSync(p))
            return { ok: true };
    }
    return {
        ok: false,
        reason: "credentials_missing",
        detail: `No credentials found in ${credentialsDir}. Run 'kimi' then '/login' to authenticate.`,
    };
}
/**
 * Run `kimi --print -p "Reply OK"` and check exit code 0.
 * Uses spawnSync with an argument array (no shell) so KIMI_CLI_PATH cannot be abused.
 */
export function verifyKimiRun() {
    const credsOk = verifyCredentials();
    if (!credsOk.ok)
        return credsOk;
    const kimiCmd = getSafeKimiCliPath();
    const result = spawnSync(kimiCmd, ["--print", "-p", "Reply OK"], {
        encoding: "utf-8",
        timeout: 30_000,
        stdio: ["pipe", "pipe", "pipe"],
        shell: false,
    });
    if (result.status === 0)
        return { ok: true };
    const msg = result.error?.message ?? result.stderr?.trim() ?? `exit ${result.status}`;
    return {
        ok: false,
        reason: "run_failed",
        detail: `Kimi CLI run failed: ${msg}. Ensure 'kimi' is on PATH and authenticated.`,
    };
}
export function verifyAll() {
    const config = verifyConfigExists();
    if (!config.ok)
        return config;
    const creds = verifyCredentials();
    if (!creds.ok)
        return creds;
    return verifyKimiRun();
}
//# sourceMappingURL=verify.js.map