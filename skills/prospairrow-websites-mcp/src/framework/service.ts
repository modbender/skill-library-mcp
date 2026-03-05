import { randomUUID } from "node:crypto";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { stdin as input, stdout as output } from "node:process";
import readline from "node:readline/promises";
import { enforceCapability, logTaskInvocation } from "./policy.js";
import { loadRegistry, loadSiteAndTask } from "./registry.js";
import { createRunnerSession } from "./runner.js";
import { loadStorageStatePath, saveStorageState } from "./storage.js";
import { Capability, type BootstrapLoginInput, type RegistrySummary, type RunTaskInput, type TaskRunResponse } from "./types.js";

function nowIso(): string {
  return new Date().toISOString();
}

function cleanSecret(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
}

function envFlagEnabled(value: string | undefined): boolean {
  if (!value) return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes" || normalized === "on";
}

function allowOpenClawConfigApiKey(): boolean {
  return envFlagEnabled(process.env.WEBSITES_ALLOW_OPENCLAW_CONFIG_API_KEY);
}

function shouldLogInvocations(): boolean {
  return envFlagEnabled(process.env.WEBSITES_LOG_INVOCATIONS);
}

async function readConfigApiKey(): Promise<string | undefined> {
  if (!allowOpenClawConfigApiKey()) return undefined;
  try {
    const openclawConfigPath = path.join(os.homedir(), ".openclaw", "openclaw.json");
    const raw = await fs.readFile(openclawConfigPath, "utf-8");
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const skills = (parsed.skills as Record<string, unknown> | undefined)?.entries as Record<string, unknown> | undefined;
    const prospSkill = skills?.["prospairrow-websites-mcp"] as Record<string, unknown> | undefined;

    const keyFromApiKey = cleanSecret(prospSkill?.apiKey);
    if (keyFromApiKey) return keyFromApiKey;

    const envBag = prospSkill?.env as Record<string, unknown> | undefined;
    return cleanSecret(envBag?.PROSPAIRROW_API_KEY);
  } catch {
    return undefined;
  }
}

async function resolveProspairrowApiKey(inputData: RunTaskInput): Promise<string | undefined> {
  const fromRequest = cleanSecret(inputData.apiKey);
  if (fromRequest) return fromRequest;

  const fromEnv = cleanSecret(process.env.PROSPAIRROW_API_KEY);
  if (fromEnv) return fromEnv;

  return readConfigApiKey();
}

function buildTaskErrorResponse(inputData: RunTaskInput, runId: string, errors: string[]): TaskRunResponse {
  return {
    run_id: runId,
    timestamp: nowIso(),
    site: inputData.siteId,
    task: inputData.taskId,
    result: {
      errors
    }
  };
}

export async function listSites(rootDir: string): Promise<RegistrySummary> {
  return loadRegistry(rootDir);
}

export async function bootstrapLogin(rootDir: string, inputData: BootstrapLoginInput): Promise<Record<string, unknown>> {
  const registry = await loadRegistry(rootDir);
  const site = registry.sites.find((s) => s.siteId === inputData.siteId);
  if (!site) {
    return {
      run_id: randomUUID(),
      timestamp: nowIso(),
      site: inputData.siteId,
      message: "Site not found.",
      errors: [`Unknown siteId: ${inputData.siteId}`]
    };
  }

  const runId = randomUUID();
  if (shouldLogInvocations()) {
    await logTaskInvocation(rootDir, {
      event: "bootstrap_login.start",
      run_id: runId,
      site: site.siteId
    });
  }

  const runner = await createRunnerSession({
    allowedHosts: site.allowedHosts,
    headed: true
  });

  try {
    await runner.safeGoto(site.baseUrl);
    const rl = readline.createInterface({ input, output });
    await rl.question(`Login manually for '${site.siteId}' and press ENTER to save storageState: `);
    rl.close();

    const storageState = await runner.context.storageState();
    let filePath: string;
    try {
      filePath = await saveStorageState(rootDir, site.siteId, storageState);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        run_id: runId,
        timestamp: nowIso(),
        site: site.siteId,
        message: "Login captured, but storage state write is disabled.",
        errors: [message]
      };
    }

    if (shouldLogInvocations()) {
      await logTaskInvocation(rootDir, {
        event: "bootstrap_login.success",
        run_id: runId,
        site: site.siteId,
        storage_file: filePath
      });
    }

    return {
      run_id: runId,
      timestamp: nowIso(),
      site: site.siteId,
      message: "Login state captured successfully.",
      storage_file: filePath,
      errors: []
    };
  } finally {
    await runner.close();
  }
}

export async function runTask(rootDir: string, inputData: RunTaskInput): Promise<TaskRunResponse> {
  const runId = randomUUID();

  let registry: RegistrySummary;
  let site;
  let task;

  try {
    ({ registry, site, task } = await loadSiteAndTask(rootDir, inputData.siteId, inputData.taskId));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return buildTaskErrorResponse(inputData, runId, [message]);
  }

  try {
    enforceCapability(task.capability, registry.policy.enabledCapabilities);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return buildTaskErrorResponse(inputData, runId, [
      `Capability gate blocked task '${task.taskId}': ${message}`,
      "Set WEBSITES_ENABLE_WRITES=1 before starting the server to enable WRITE tasks."
    ]);
  }

  if (!site.capabilities.includes(task.capability)) {
    return buildTaskErrorResponse(inputData, runId, [
      `Site '${site.siteId}' does not allow capability '${task.capability}'.`
    ]);
  }

  const resolvedProspairrowApiKey = inputData.siteId === "prospairrow"
    ? await resolveProspairrowApiKey(inputData)
    : undefined;

  let storageStatePath: string | undefined;
  try {
    storageStatePath = await loadStorageStatePath(rootDir, site.siteId);
  } catch {
    const apiKeyAvailable = Boolean(resolvedProspairrowApiKey);
    const allowApiOnlyMode = site.siteId === "prospairrow" && apiKeyAvailable;
    if (!allowApiOnlyMode) {
      return buildTaskErrorResponse(inputData, runId, [
        `AUTH_REQUIRED: storage state not found for site '${site.siteId}'. Run websites.bootstrap_login first.`
      ]);
    }
  }

  if (shouldLogInvocations()) {
    await logTaskInvocation(rootDir, {
      event: "run_task.start",
      run_id: runId,
      site: site.siteId,
      task: task.taskId,
      capability: task.capability
    });
  }

  const runner = await createRunnerSession({
    allowedHosts: site.allowedHosts,
    storageStatePath,
    headed: false
  });

  try {
    const result = await task.run(
      {
        site,
        task,
        context: runner.context,
        page: runner.page,
        safeGoto: runner.safeGoto,
        runId,
        apiKeys: {
          prospairrow: resolvedProspairrowApiKey
        }
      },
      inputData.params
    );

    if (shouldLogInvocations()) {
      await logTaskInvocation(rootDir, {
        event: "run_task.success",
        run_id: runId,
        site: site.siteId,
        task: task.taskId
      });
    }

    return {
      run_id: runId,
      timestamp: nowIso(),
      site: site.siteId,
      task: task.taskId,
      result
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (shouldLogInvocations()) {
      await logTaskInvocation(rootDir, {
        event: "run_task.error",
        run_id: runId,
        site: site.siteId,
        task: task.taskId,
        error: message
      });
    }

    return buildTaskErrorResponse(inputData, runId, [`Task failed: ${message}`]);
  } finally {
    await runner.close();
  }
}

export function defaultPolicyCapabilities(): Capability[] {
  return [Capability.READ_ONLY];
}
