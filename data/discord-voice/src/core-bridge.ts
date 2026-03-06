/**
 * Core bridge – loads OpenClaw extension API for agent invocation.
 * Uses the same pattern as the official voice-call plugin:
 * resolves openclaw package root and imports from dist/extensionAPI.js.
 *
 * Requires OpenClaw to be installed (e.g. openclaw gateway). Set OPENCLAW_ROOT
 * if auto-detection fails.
 */

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

import type { VoiceCallTtsConfig } from "./config.js";

export type CoreConfig = {
  session?: {
    store?: string;
  };
  messages?: {
    tts?: VoiceCallTtsConfig;
  };
  [key: string]: unknown;
};

type CoreAgentDeps = {
  resolveAgentDir: (cfg: CoreConfig, agentId: string) => string;
  resolveAgentWorkspaceDir: (cfg: CoreConfig, agentId: string) => string;
  resolveAgentIdentity: (cfg: CoreConfig, agentId: string) => { name?: string | null } | null | undefined;
  resolveThinkingDefault: (params: { cfg: CoreConfig; provider?: string; model?: string }) => string;
  runEmbeddedPiAgent: (params: {
    sessionId: string;
    sessionKey?: string;
    messageProvider?: string;
    sessionFile: string;
    workspaceDir: string;
    config?: CoreConfig;
    prompt: string;
    provider?: string;
    model?: string;
    thinkLevel?: string;
    verboseLevel?: string;
    timeoutMs: number;
    runId: string;
    lane?: string;
    extraSystemPrompt?: string;
    agentDir?: string;
  }) => Promise<{
    payloads?: Array<{ text?: string; isError?: boolean }>;
    meta?: { aborted?: boolean };
  }>;
  resolveAgentTimeoutMs: (opts: { cfg: CoreConfig }) => number;
  ensureAgentWorkspace: (params?: { dir: string }) => Promise<void>;
  resolveStorePath: (store?: string, opts?: { agentId?: string }) => string;
  loadSessionStore: (storePath: string) => Record<string, unknown>;
  saveSessionStore: (storePath: string, store: Record<string, unknown>) => Promise<void>;
  resolveSessionFilePath: (sessionId: string, entry: unknown, opts?: { agentId?: string }) => string;
  DEFAULT_MODEL: string;
  DEFAULT_PROVIDER: string;
};

let coreRootCache: string | null = null;
let coreDepsPromise: Promise<CoreAgentDeps> | null = null;

function findPackageRoot(startDir: string, name: string): string | null {
  let dir = startDir;
  for (;;) {
    const pkgPath = path.join(dir, "package.json");
    try {
      if (fs.existsSync(pkgPath)) {
        const raw = fs.readFileSync(pkgPath, "utf8");
        const pkg = JSON.parse(raw) as { name?: string };
        if (pkg.name === name) return dir;
      }
    } catch {
      // ignore parse errors and keep walking
    }
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

function resolveOpenClawRoot(overrideRoot?: string): string {
  if (coreRootCache) return coreRootCache;

  const override = overrideRoot?.trim() || process.env["OPENCLAW_ROOT"]?.trim();
  if (override) {
    // Normalize and resolve the override to prevent path traversal via ../ sequences
    const resolved = path.resolve(override);
    coreRootCache = resolved;
    return resolved;
  }

  const candidates = new Set<string>();
  if (process.argv[1]) {
    let d = path.dirname(process.argv[1]);
    for (let i = 0; i < 5 && d; i++) {
      candidates.add(d);
      d = path.dirname(d);
    }
  }
  candidates.add(process.cwd());
  try {
    const urlPath = fileURLToPath(import.meta.url);
    let d = path.dirname(urlPath);
    for (let i = 0; i < 6 && d; i++) {
      candidates.add(d);
      d = path.dirname(d);
    }
    // Plugin layout: discord-voice/node_modules/openclaw (e.g. extensions/discord-voice/node_modules/openclaw)
    const pluginRoot = path.join(path.dirname(urlPath), "..");
    candidates.add(path.join(pluginRoot, "node_modules", "openclaw"));
  } catch {
    // ignore
  }
  const stateDir = process.env["OPENCLAW_STATE_DIR"] || process.env["OPENCLAW_HOME"];
  if (stateDir) {
    candidates.add(stateDir);
    candidates.add(path.dirname(stateDir));
  }

  for (const start of candidates) {
    const found = findPackageRoot(start, "openclaw");
    if (found) {
      coreRootCache = found;
      return found;
    }
  }

  // Fallback: resolve via require (plugin runs inside OpenClaw gateway process)
  const resolvePaths: string[] = [process.cwd(), path.dirname(fileURLToPath(import.meta.url))];
  if (process.argv[1]) {
    const scriptDir = path.dirname(process.argv[1]);
    resolvePaths.push(scriptDir);
    resolvePaths.push(path.dirname(scriptDir)); // parent (e.g. dist -> pkg root)
  }
  if (stateDir) resolvePaths.push(stateDir);

  const require = createRequire(import.meta.url);
  for (const dir of resolvePaths) {
    if (!dir) continue;
    try {
      const pkgPath = require.resolve("openclaw/package.json", { paths: [dir] });
      const found = path.dirname(pkgPath);
      if (fs.existsSync(path.join(found, "dist", "extensionAPI.js"))) {
        coreRootCache = found;
        return found;
      }
    } catch {
      // ignore
    }
  }

  throw new Error(
    "Unable to resolve OpenClaw root. Set OPENCLAW_ROOT to the package root, or ensure openclaw is installed and the gateway runs from its context.",
  );
}

async function importCoreExtensionAPI(overrideRoot?: string): Promise<CoreAgentDeps> {
  const root = resolveOpenClawRoot(overrideRoot);
  const distPath = path.join(root, "dist", "extensionAPI.js");
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Missing extension API at ${distPath}. Run \`pnpm build\` in OpenClaw or install the official openclaw package.`,
    );
  }
  // Verify the resolved path belongs to an actual openclaw package (prevents loading arbitrary code)
  const pkgJsonPath = path.join(root, "package.json");
  if (!fs.existsSync(pkgJsonPath)) {
    throw new Error(`No package.json found at ${root} — cannot verify openclaw package integrity.`);
  }
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, "utf8")) as { name?: string };
    if (pkg.name !== "openclaw") {
      throw new Error(`Package at ${root} is "${pkg.name}", expected "openclaw".`);
    }
  } catch (err) {
    if (err instanceof SyntaxError) {
      throw new Error(`Malformed package.json at ${pkgJsonPath}`);
    }
    throw err;
  }

  return (await import(pathToFileURL(distPath).href)) as CoreAgentDeps;
}

export async function loadCoreAgentDeps(overrideRoot?: string): Promise<CoreAgentDeps> {
  if (coreDepsPromise) return coreDepsPromise;

  coreDepsPromise = importCoreExtensionAPI(overrideRoot);
  return coreDepsPromise;
}
