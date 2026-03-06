import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { getConfig } from "../config.js";
import {
  getProviderFromConfig,
  isValidProviderId,
  VALID_PROVIDER_IDS,
} from "../providers/index.js";
import type { CLIProvider } from "../providers/types.js";
import { generateAgentsMd } from "../templates/agents-md.js";
import { writeManifest } from "../manifest/write.js";
import { getRepoPath } from "../worktree/repo.js";
import { createWorktree } from "../worktree/create.js";
import type { TaskInput } from "../types.js";

function isGitRepo(dir: string): boolean {
  const gitDir = path.join(dir, ".git");
  return fs.existsSync(gitDir) && fs.statSync(gitDir).isDirectory();
}

interface ParsedArgs {
  prompt: string;
  outputFormat: "text" | "json";
  cwd: string;
  repoFlag?: string;
  timeoutMinutes?: number;
  constraints: string[];
  successCriteria: string[];
  relevantFiles: string[];
  providerFlag?: string;
}

function parseArgs(args: string[]): ParsedArgs {
  let prompt = "";
  let outputFormat: "text" | "json" = "json";
  const cwd = process.cwd();
  let repoFlag: string | undefined;
  let timeoutMinutes: number | undefined;
  const constraints: string[] = [];
  const successCriteria: string[] = [];
  let relevantFiles: string[] = [];
  let providerFlag: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--repo" && args[i + 1]) {
      repoFlag = args[i + 1];
      i++;
      continue;
    }
    if (args[i] === "--timeout" && args[i + 1]) {
      timeoutMinutes = parseInt(args[i + 1], 10);
      if (!Number.isFinite(timeoutMinutes) || timeoutMinutes < 1)
        timeoutMinutes = undefined;
      i++;
      continue;
    }
    if (args[i] === "--output-format" && args[i + 1]) {
      const fmt = args[i + 1];
      outputFormat = fmt === "text" ? "text" : "json";
      i++;
      continue;
    }
    if (args[i] === "--constraint" && args[i + 1]) {
      constraints.push(args[i + 1]);
      i++;
      continue;
    }
    if (args[i] === "--success" && args[i + 1]) {
      successCriteria.push(args[i + 1]);
      i++;
      continue;
    }
    if (args[i] === "--files" && args[i + 1]) {
      relevantFiles = args[i + 1]
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      i++;
      continue;
    }
    if (args[i] === "--provider" && args[i + 1]) {
      providerFlag = args[i + 1];
      i++;
      continue;
    }
    if (!args[i].startsWith("--")) {
      prompt = args[i];
      break;
    }
  }

  return {
    prompt,
    outputFormat,
    cwd,
    repoFlag,
    timeoutMinutes,
    constraints,
    successCriteria,
    relevantFiles,
    providerFlag,
  };
}

const AGENTS_MD = "AGENTS.md";

export async function runExecute(args: string[]): Promise<number> {
  const parsed = parseArgs(args);
  const { prompt, outputFormat, cwd, providerFlag } = parsed;

  if (!prompt) {
    console.error(
      'Usage: cli-worker execute "<prompt>" [--output-format text|json] [--constraint "X"] [--success "Y"] [--files "path1,path2"] [--provider kimi|claude|opencode]'
    );
    return 1;
  }

  // Validate provider flag if provided
  if (providerFlag && !isValidProviderId(providerFlag)) {
    console.error(`✗ Unknown provider: ${providerFlag}`);
    console.error(`\nValid providers: ${VALID_PROVIDER_IDS.join(", ")}`);
    return 1;
  }

  // Get config and resolve provider
  const config = getConfig();
  const provider: CLIProvider = getProviderFromConfig(config, providerFlag);

  // Verify provider is authenticated
  const auth = await Promise.resolve(provider.verify());
  if (!auth.ok) {
    console.error("✗", auth.detail ?? auth.reason);
    return 1;
  }

  const taskId = randomUUID();
  const repoPath = getRepoPath(cwd, parsed.repoFlag);
  let worktreePath: string;
  if (isGitRepo(repoPath)) {
    try {
      worktreePath = await createWorktree(repoPath, taskId);
    } catch (err) {
      console.error(
        "Failed to create worktree:",
        err instanceof Error ? err.message : err
      );
      return 1;
    }
  } else {
    worktreePath = cwd;
  }

  // Use provider-specific report subdir
  const reportPath = path.join(
    worktreePath,
    ".openclaw",
    provider.reportSubdir(),
    `${taskId}.json`
  );

  const task: TaskInput = {
    prompt,
    worktreePath,
    taskId,
    reportPath,
    relevantFiles:
      parsed.relevantFiles.length > 0 ? parsed.relevantFiles : undefined,
    constraints: parsed.constraints.length > 0 ? parsed.constraints : undefined,
    successCriteria:
      parsed.successCriteria.length > 0 ? parsed.successCriteria : undefined,
  };

  try {
    writeManifest(taskId, task, worktreePath, reportPath);
    // Use provider-specific AGENTS.md title
    const agentsMd = generateAgentsMd(task, provider.agentsMdTitle());
    fs.writeFileSync(path.join(worktreePath, AGENTS_MD), agentsMd, "utf-8");
  } catch (err) {
    console.error(
      "Could not write task files:",
      err instanceof Error ? err.message : err
    );
    return 1;
  }

  const timeoutMs =
    parsed.timeoutMinutes != null
      ? parsed.timeoutMinutes * 60 * 1000
      : undefined;

  // Run using the provider
  const result = await provider.run(prompt, worktreePath, { timeoutMs });

  if (result.exitCode !== 0) {
    const exitCode = result.exitCode ?? 1;
    const stderrMsg = result.stderr ? `: ${result.stderr.trim()}` : "";
    console.error(
      `${provider.displayName} failed (exit ${exitCode})${stderrMsg}`
    );
    return exitCode;
  }

  if (outputFormat === "text") {
    result.stdoutLines.forEach((line) => console.log(line));
    return 0;
  }

  // Parse using the provider's parser
  const { finalText } = provider.parseStdout(result.stdoutLines);
  if (finalText) console.log(finalText);
  return 0;
}
