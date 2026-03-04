/**
 * ClawWall Auto-Start Hook
 *
 * Runs on gateway:startup to ensure the ClawWall DLP service is running
 * before any agent tool calls are processed.
 */

import { execSync, spawn } from "child_process";
import { existsSync, mkdirSync, writeFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
import { createConnection } from "net";

const PORT = 8642;
const HEALTH_URL = `http://127.0.0.1:${PORT}/api/v1/health`;
const CONFIG_DIR = join(homedir(), ".config", "clawwall");
const PID_FILE = join(CONFIG_DIR, "clawwall.pid");

function log(msg: string): void {
  console.log(`[clawwall-hook] ${msg}`);
}

function isPortInUse(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = createConnection({ port, host: "127.0.0.1" });
    socket.setTimeout(1000);
    socket.on("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.on("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.on("error", () => {
      resolve(false);
    });
  });
}

function findBinary(): string | null {
  try {
    return execSync("which clawwall", { encoding: "utf-8" }).trim();
  } catch {
    return null;
  }
}

async function waitForHealth(maxAttempts: number = 15): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const resp = await fetch(HEALTH_URL);
      if (resp.ok) return true;
    } catch {
      // service not ready yet
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

export async function onStartup(): Promise<void> {
  // 1. Check if binary exists
  const bin = findBinary();
  if (!bin) {
    log("clawwall binary not found on PATH — skipping auto-start");
    log("Install with: pip install clawwall");
    return;
  }

  // 2. Check if already running
  const alreadyRunning = await isPortInUse(PORT);
  if (alreadyRunning) {
    log(`Port ${PORT} already in use — ClawWall service appears to be running`);
    return;
  }

  // 3. Ensure config directory exists
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true });
  }

  // 4. Spawn as detached background process
  log("Starting ClawWall DLP service...");
  const child = spawn(bin, [], {
    detached: true,
    stdio: "ignore",
    env: { ...process.env },
  });

  child.unref();

  if (child.pid) {
    writeFileSync(PID_FILE, String(child.pid), "utf-8");
    log(`ClawWall started (PID: ${child.pid})`);
  }

  // 5. Wait for health endpoint
  const healthy = await waitForHealth();
  if (healthy) {
    log(`ClawWall ready on http://127.0.0.1:${PORT}`);
    log(`Dashboard: http://127.0.0.1:${PORT}/dashboard`);
  } else {
    log("Warning: ClawWall started but health check did not respond in time");
    log("The service may still be initializing — check manually");
  }
}
