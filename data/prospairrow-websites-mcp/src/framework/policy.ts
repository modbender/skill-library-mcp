import fs from "node:fs/promises";
import path from "node:path";
import type { Request, Route } from "playwright";
import { Capability } from "./types.js";

const ALLOWED_PROTOCOLS = new Set(["https:", "data:", "blob:"]);

function envFlagEnabled(value: string | undefined): boolean {
  if (!value) return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes" || normalized === "on";
}

export function resolveEnabledCapabilities(configCapabilities: Capability[]): Capability[] {
  const enabled = new Set<Capability>(configCapabilities.length ? configCapabilities : [Capability.READ_ONLY]);

  if (envFlagEnabled(process.env.WEBSITES_ENABLE_WRITES)) {
    enabled.add(Capability.WRITE);
  }

  // Intentionally never auto-enable destructive capabilities.
  enabled.delete(Capability.DESTRUCTIVE);

  return Array.from(enabled);
}

export function isHostAllowed(hostname: string, allowedHosts: string[]): boolean {
  const host = hostname.toLowerCase();
  return allowedHosts.some((allowed) => {
    const normalized = allowed.toLowerCase();
    return host === normalized || host.endsWith(`.${normalized}`);
  });
}

export function validateUrlAgainstAllowlist(urlRaw: string, allowedHosts: string[]): { ok: boolean; reason?: string } {
  try {
    const url = new URL(urlRaw);

    if (!ALLOWED_PROTOCOLS.has(url.protocol)) {
      return { ok: false, reason: `Blocked protocol: ${url.protocol}` };
    }

    if (url.protocol === "https:" && !isHostAllowed(url.hostname, allowedHosts)) {
      return { ok: false, reason: `Blocked host: ${url.hostname}` };
    }

    return { ok: true };
  } catch {
    return { ok: false, reason: "Invalid URL" };
  }
}

export async function enforceRequestAllowlist(route: Route, request: Request, allowedHosts: string[]): Promise<void> {
  const verdict = validateUrlAgainstAllowlist(request.url(), allowedHosts);
  if (!verdict.ok) {
    await route.abort("blockedbyclient");
    return;
  }
  await route.continue();
}

export function enforceCapability(taskCapability: Capability, enabledCapabilities: Capability[]): void {
  if (!enabledCapabilities.includes(taskCapability)) {
    throw new Error(`CAPABILITY_DISABLED:${taskCapability}`);
  }
}

export async function logTaskInvocation(rootDir: string, payload: Record<string, unknown>): Promise<void> {
  const logDir = path.join(rootDir, "logs");
  const logPath = path.join(logDir, "task-invocations.log");
  await fs.mkdir(logDir, { recursive: true });
  const line = `${JSON.stringify({ timestamp: new Date().toISOString(), ...payload })}\n`;
  await fs.appendFile(logPath, line, "utf-8");
}
