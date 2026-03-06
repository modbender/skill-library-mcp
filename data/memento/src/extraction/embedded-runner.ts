/**
 * OpenClaw Embedded Runner Integration
 *
 * Delegates LLM calls to OpenClaw's internal model routing system
 * (runEmbeddedPiAgent) instead of making direct HTTP calls.
 *
 * This means Memento automatically inherits:
 *   - The agent's configured model (primary + fallbacks)
 *   - OpenClaw's auth profile handling
 *   - Provider routing and failover
 *
 * Used by ExtractionTrigger when running inside the OpenClaw plugin context.
 * Falls back to direct API calls when running as a standalone CLI tool.
 */

import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

type RunEmbeddedPiAgentFn = (params: Record<string, unknown>) => Promise<unknown>;

/**
 * Dynamically load runEmbeddedPiAgent from OpenClaw internals.
 * Returns null if not available (e.g. running standalone CLI).
 */
async function loadRunEmbeddedPiAgent(): Promise<RunEmbeddedPiAgentFn | null> {
  // Try source checkout path first (dev/test)
  const candidates = [
    "openclaw/src/agents/pi-embedded-runner.js",
    "openclaw/dist/agents/pi-embedded-runner.js",
  ];

  for (const candidate of candidates) {
    try {
      const mod = await import(candidate) as any;
      if (typeof mod.runEmbeddedPiAgent === "function") {
        return mod.runEmbeddedPiAgent as RunEmbeddedPiAgentFn;
      }
    } catch {
      // not found — try next
    }
  }

  return null;
}

function collectText(payloads: Array<{ text?: string; isError?: boolean }> | undefined): string {
  return (payloads ?? [])
    .filter((p) => !p.isError && typeof p.text === "string")
    .map((p) => p.text ?? "")
    .join("\n")
    .trim();
}

function stripCodeFences(s: string): string {
  const trimmed = s.trim();
  const m = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  return m ? (m[1] ?? "").trim() : trimmed;
}

export type OpenClawConfig = Record<string, unknown>;

export type EmbeddedRunnerResult = {
  text: string;
  provider: string;
  model: string;
};

/**
 * Run a one-shot LLM prompt via OpenClaw's model routing.
 *
 * Resolves provider/model from api.config (agent defaults),
 * with optional override via the extractionModel config.
 */
export async function runViaOpenClaw(
  prompt: string,
  config: OpenClawConfig,
  extractionModel?: string,
): Promise<EmbeddedRunnerResult | null> {
  const runEmbeddedPiAgent = await loadRunEmbeddedPiAgent();
  if (!runEmbeddedPiAgent) {
    return null; // Not inside OpenClaw — caller falls back to direct API
  }

  // Resolve provider/model from config (same logic as llm-task plugin)
  const defaultsModel = (config as any)?.agents?.defaults?.model;
  const primary =
    typeof defaultsModel === "string"
      ? defaultsModel.trim()
      : (defaultsModel?.primary?.trim() ?? undefined);

  // Allow extractionModel config to override the agent default
  const modelOverride = extractionModel?.trim();
  const resolved = modelOverride ?? primary;

  if (!resolved) {
    return null; // Can't resolve model — fall back to direct API
  }

  const slashIdx = resolved.indexOf("/");
  const provider = slashIdx !== -1 ? resolved.slice(0, slashIdx) : resolved;
  const model = slashIdx !== -1 ? resolved.slice(slashIdx + 1) : resolved;

  const workspaceDir = (config as any)?.agents?.defaults?.workspace ?? process.cwd();

  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "memento-extract-"));
  try {
    const sessionId = `memento-extract-${Date.now()}`;
    const sessionFile = path.join(tmpDir, "session.json");

    const result = await runEmbeddedPiAgent({
      sessionId,
      sessionFile,
      workspaceDir,
      config,
      prompt,
      timeoutMs: 60_000,
      runId: `memento-extract-${Date.now()}`,
      provider,
      model,
      authProfileIdSource: "auto",
      disableTools: true,
    }) as any;

    const text = collectText(result?.payloads);
    if (!text) return null;

    return { text: stripCodeFences(text), provider, model };
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {});
  }
}
