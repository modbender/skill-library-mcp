/**
 * Shared utility functions for openclaw-ops-elvatis.
 *
 * Single source of truth for all cross-cutting helpers used by index.ts
 * and extension modules. Grouped by domain:
 *
 *   - Path helpers
 *   - Shell / process helpers
 *   - Filesystem helpers
 *   - JSON helpers
 *   - Formatting helpers
 *   - Cooldown / model-failover state helpers
 *   - System inspection helpers
 *   - Workspace / plugin scanning helpers
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { execSync, spawnSync } from "node:child_process";

// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

/** Expand a leading `~` or `~/` to the user's home directory. */
export function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return p;
}

// ---------------------------------------------------------------------------
// Shell / process helpers
// ---------------------------------------------------------------------------

/**
 * Run a shell command synchronously, returning trimmed stdout on success
 * or an empty string on failure. Stderr is suppressed.
 */
export function safeExec(cmd: string): string {
  try {
    return execSync(cmd, { stdio: ["ignore", "pipe", "ignore"], encoding: "utf-8" }).trim();
  } catch {
    return "";
  }
}

/**
 * Run a command with arguments via `spawnSync`, returning the exit code and
 * combined stdout+stderr output.
 *
 * @param cmd       - The executable to run.
 * @param args      - Array of arguments.
 * @param timeoutMs - Timeout in milliseconds (default 120 000 - two minutes).
 */
export function runCmd(
  cmd: string,
  args: string[],
  timeoutMs = 120_000,
): { code: number; out: string } {
  try {
    const p = spawnSync(cmd, args, {
      encoding: "utf-8",
      timeout: timeoutMs,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const out = `${p.stdout ?? ""}\n${p.stderr ?? ""}`.trim();
    return { code: p.status ?? (p.error ? 1 : 0), out };
  } catch (e: any) {
    return { code: 1, out: String(e?.message ?? e) };
  }
}

// ---------------------------------------------------------------------------
// Filesystem helpers
// ---------------------------------------------------------------------------

/**
 * Return the filename of the most recently modified file in `dir` whose name
 * starts with `prefix`, or `null` if none is found.
 */
export function latestFile(dir: string, prefix: string): string | null {
  try {
    const files = fs
      .readdirSync(dir)
      .filter((f) => f.startsWith(prefix))
      .map((f) => ({ f, t: fs.statSync(path.join(dir, f)).mtimeMs }))
      .sort((a, b) => b.t - a.t);
    return files[0]?.f ?? null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// JSON helpers
// ---------------------------------------------------------------------------

/**
 * Read a JSON file and return the parsed value, or `fallback` when the file
 * is missing, unreadable, or contains invalid JSON.
 */
export function readJsonSafe<T = any>(filePath: string, fallback: T): T {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
  } catch {
    return fallback;
  }
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

/**
 * Format a Date (or epoch-ms number) into a compact ISO-ish string:
 * `"YYYY-MM-DD HH:MM"` (UTC).
 *
 * Useful for human-readable timestamps in command output. The same pattern
 * was previously inlined in index.ts, formatCooldownLine, and observer-commands.
 */
export function formatIsoCompact(input: Date | number): string {
  const d = typeof input === "number" ? new Date(input) : input;
  return d.toISOString().slice(0, 16).replace("T", " ");
}

/** Format a byte count into a human-readable string (B, KB, MB, GB). */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)}KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)}MB`;
  return `${(bytes / 1024 ** 3).toFixed(2)}GB`;
}

// ---------------------------------------------------------------------------
// Cooldown / model-failover state helpers
// ---------------------------------------------------------------------------

/** A single model cooldown entry from the model-failover state file. */
export interface CooldownEntry {
  model: string;
  lastHitAt: number;
  nextAvailableAt: number;
  reason?: string;
}

/**
 * Load active cooldowns from the model-failover state file.
 *
 * Reads `<workspace>/memory/model-ratelimits.json`, filters for entries whose
 * `nextAvailableAt` is still in the future, and returns them sorted by
 * soonest-to-expire first.
 *
 * Returns an empty array when the file is missing, unreadable, or contains
 * no active cooldowns.
 */
export function loadActiveCooldowns(workspace: string): CooldownEntry[] {
  const statePath = path.join(workspace, "memory", "model-ratelimits.json");
  const now = Math.floor(Date.now() / 1000);

  try {
    if (!fs.existsSync(statePath)) return [];
    const raw = fs.readFileSync(statePath, "utf-8");
    const st = JSON.parse(raw) as any;
    const lim = (st?.limited ?? {}) as Record<
      string,
      { lastHitAt: number; nextAvailableAt: number; reason?: string }
    >;

    return Object.entries(lim)
      .map(([model, v]) => ({ model, ...v }))
      .filter((v) => typeof v.nextAvailableAt === "number" && v.nextAvailableAt > now)
      .sort((a, b) => a.nextAvailableAt - b.nextAvailableAt);
  } catch {
    return [];
  }
}

/**
 * Format a cooldown entry into a human-readable status line.
 *
 * Example output: `openai-codex/gpt-5.3 - 2026-02-27 15:30 UTC (~45m)`
 */
export function formatCooldownLine(entry: CooldownEntry): string {
  const now = Math.floor(Date.now() / 1000);
  const etaSec = entry.nextAvailableAt - now;
  const etaMin = Math.max(1, Math.round(etaSec / 60));

  let eta: string;
  if (etaMin >= 60) {
    const h = Math.floor(etaMin / 60);
    const m = etaMin % 60;
    eta = m > 0 ? `~${h}h${m}m` : `~${h}h`;
  } else {
    eta = `~${etaMin}m`;
  }

  const until = formatIsoCompact(entry.nextAvailableAt * 1000);

  return `${entry.model} - ${until} UTC (${eta})`;
}

// ---------------------------------------------------------------------------
// System inspection helpers
// ---------------------------------------------------------------------------

/**
 * Gather CPU load, memory usage, and disk usage for the current host.
 *
 * @param workspacePath - Optional workspace path used to detect the correct
 *   drive on Windows. When omitted, falls back to `process.cwd()`.
 */
export function getSystemResources(workspacePath?: string): { cpu: string; memory: string; disk: string } {
  const platform = os.platform();

  // CPU load
  const loadavg = os.loadavg();
  const cpu = `${loadavg[0].toFixed(2)}, ${loadavg[1].toFixed(2)}, ${loadavg[2].toFixed(2)}`;

  // Memory
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  const memPercent = ((usedMem / totalMem) * 100).toFixed(1);
  const memory = `${formatBytes(usedMem)} / ${formatBytes(totalMem)} (${memPercent}%)`;

  // Disk (platform-specific)
  let disk = "N/A";
  try {
    if (platform === "linux" || platform === "darwin") {
      const df = safeExec("df -h /");
      const lines = df.split("\n");
      if (lines.length >= 2) {
        const parts = lines[1].split(/\s+/);
        disk = `${parts[4] || "N/A"} used (${parts[2] || "?"} / ${parts[1] || "?"})`;
      }
    } else if (platform === "win32") {
      // Detect the drive letter from the workspace path (or cwd as fallback).
      // This avoids hardcoding C: which may not be the workspace drive.
      const probePath = workspacePath ?? process.cwd();
      const driveRoot = detectWindowsDriveRoot(probePath);
      const stats = fs.statfsSync(driveRoot);
      const total = stats.bsize * stats.blocks;
      const free = stats.bsize * stats.bavail;
      const used = total - free;
      const usedPercent = ((used / total) * 100).toFixed(1);
      disk = `${usedPercent}% used (${formatBytes(used)} / ${formatBytes(total)}) [${driveRoot.replace("\\", "")}]`;
    }
  } catch {
    // Keep N/A
  }

  return { cpu, memory, disk };
}

/**
 * Extract the drive root (e.g. `C:\\`) from a Windows path.
 *
 * Handles standard paths like `E:\\_data\\workspace`, UNC paths, and
 * forward-slash paths. Falls back to `C:\\` when no drive letter is found.
 */
export function detectWindowsDriveRoot(filepath: string): string {
  // Match drive letter at the start: "C:", "C:\", "C:/", "c:\\"
  const match = filepath.match(/^([A-Za-z]):[/\\]/);
  if (match) {
    return `${match[1].toUpperCase()}:\\`;
  }
  // Bare drive letter without trailing separator (e.g. "C:")
  if (/^[A-Za-z]:$/.test(filepath)) {
    return `${filepath[0].toUpperCase()}:\\`;
  }
  return "C:\\";
}

/**
 * Check whether the OpenClaw gateway is running for a given profile.
 * Returns running state, optional PID, and optional uptime string.
 */
export function checkGatewayStatus(
  profile = "default",
): { running: boolean; pid?: number; uptime?: string } {
  const profileArg = profile === "default" ? [] : ["--profile", profile];
  const result = runCmd("openclaw", [...profileArg, "gateway", "status"], 10_000);

  const running = result.code === 0 && result.out.toLowerCase().includes("running");

  let pid: number | undefined;
  let uptime: string | undefined;
  const pidMatch = result.out.match(/PID[:\s]+(\d+)/i);
  if (pidMatch) pid = parseInt(pidMatch[1]);

  const uptimeMatch = result.out.match(/uptime[:\s]+(.+?)(?:\n|$)/i);
  if (uptimeMatch) uptime = uptimeMatch[1].trim();

  return { running, pid, uptime };
}

// ---------------------------------------------------------------------------
// Workspace / plugin scanning helpers
// ---------------------------------------------------------------------------

/**
 * Return the list of `openclaw-*` directory names under `workspace` that
 * contain an `openclaw.plugin.json` manifest, sorted alphabetically.
 *
 * Returns an empty array when the workspace is missing or unreadable.
 */
export function listWorkspacePluginDirs(workspace: string): string[] {
  try {
    return fs
      .readdirSync(workspace)
      .filter(
        (d) =>
          d.startsWith("openclaw-") &&
          fs.existsSync(path.join(workspace, d, "openclaw.plugin.json")),
      )
      .sort();
  } catch {
    return [];
  }
}
