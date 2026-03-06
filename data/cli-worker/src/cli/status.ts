import path from "node:path";
import { getConfig } from "../config.js";
import {
  getProviderFromConfig,
  isValidProviderId,
  VALID_PROVIDER_IDS,
} from "../providers/index.js";
import { getWorktreeBasePath } from "../worktree/repo.js";
import { parseReport } from "../parser/report.js";
import { resolveTaskIdPath } from "../safe-task-id.js";

function parseStatusArgs(args: string[]): {
  taskId?: string;
  providerFlag?: string;
} {
  let taskId: string | undefined;
  let providerFlag: string | undefined;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--provider" && args[i + 1]) {
      providerFlag = args[i + 1];
      i++;
    } else if (!args[i].startsWith("--")) {
      taskId = args[i];
    }
  }
  return { taskId, providerFlag };
}

export async function runStatus(args: string[]): Promise<number> {
  const { taskId, providerFlag } = parseStatusArgs(args);
  if (!taskId) {
    console.error(
      "Usage: cli-worker status <taskId> [--provider kimi|claude|opencode]"
    );
    return 1;
  }

  if (providerFlag && !isValidProviderId(providerFlag)) {
    console.error(`✗ Unknown provider: ${providerFlag}`);
    console.error(`\nValid providers: ${VALID_PROVIDER_IDS.join(", ")}`);
    return 1;
  }

  const config = getConfig();
  const provider = getProviderFromConfig(config, providerFlag);

  const basePath = getWorktreeBasePath();
  const worktreeDir = resolveTaskIdPath(basePath, taskId);
  if (!worktreeDir) {
    console.error(
      "Invalid taskId: must be alphanumeric and hyphens only (no path traversal)."
    );
    return 1;
  }
  const reportPath = path.join(
    worktreeDir,
    ".openclaw",
    provider.reportSubdir(),
    `${taskId}.json`
  );

  try {
    const report = parseReport(reportPath);
    console.log("Task ID:", report.task_id ?? taskId);
    console.log("Status:", report.execution?.status ?? "unknown");
    if (report.execution?.duration_seconds != null) {
      console.log("Duration (s):", report.execution.duration_seconds);
    }
    if (report.artifacts?.test_status) {
      console.log("Tests:", report.artifacts.test_status);
    }
    if (report.artifacts?.files_modified?.length) {
      console.log(
        "Files modified:",
        report.artifacts.files_modified.join(", ")
      );
    }
    if (report.cognitive_state?.blockers?.length) {
      console.log("Blockers:", report.cognitive_state.blockers.join("; "));
    }
    return 0;
  } catch (err) {
    console.error("Status failed:", err instanceof Error ? err.message : err);
    return 1;
  }
}
