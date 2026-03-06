/**
 * openclaw-model-orchestrator
 *
 * Multi-LLM orchestration plugin for OpenClaw.
 * Supports fan-out, pipeline, and consensus patterns with AAHP v3 inspired handoffs.
 */

import { execSync } from "node:child_process";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ModelInfo {
  id: string;
  alias?: string;
  provider: string;
  auth: boolean;
  tags: string[];
}

interface TaskProfile {
  planner: string;
  workers: string[];
  reviewer: string;
}

type OrchestrateMode = "fan-out" | "pipeline" | "consensus";

interface OrchestrateRequest {
  mode: OrchestrateMode;
  task: string;
  planner: string;
  workers: string[];
  reviewer: string;
  profile?: string;
}

// ---------------------------------------------------------------------------
// Model Discovery (parses `openclaw models status`)
// ---------------------------------------------------------------------------

let _cachedModels: ModelInfo[] | null = null;
let _cachedAliases: Map<string, string> | null = null;
let _cacheTime = 0;
const CACHE_TTL_MS = 60_000;

function parseModelsStatus(): { models: ModelInfo[]; aliases: Map<string, string> } {
  const now = Date.now();
  if (_cachedModels && _cachedAliases && now - _cacheTime < CACHE_TTL_MS) {
    return { models: _cachedModels, aliases: _cachedAliases };
  }

  try {
    const raw = execSync("openclaw models status 2>/dev/null", {
      encoding: "utf-8",
      timeout: 15_000,
    });

    const aliases = new Map<string, string>();
    const models: ModelInfo[] = [];

    // Parse "Aliases (N) : alias1 -> model1, alias2 -> model2, ..."
    const aliasMatch = raw.match(/Aliases\s*\(\d+\)\s*:\s*(.+?)(?:\nConfigured)/s);
    if (aliasMatch) {
      const aliasStr = aliasMatch[1].replace(/\n/g, " ").trim();
      for (const pair of aliasStr.split(",")) {
        const m = pair.trim().match(/^(\S+)\s*->\s*(\S+)$/);
        if (m) aliases.set(m[1], m[2]);
      }
    }

    // Parse "Configured models (N): model1, model2, ..."
    const modelsMatch = raw.match(/Configured models\s*\(\d+\)\s*:\s*(.+?)(?:\n\n|\nAuth)/s);
    if (modelsMatch) {
      const modelStr = modelsMatch[1].replace(/\n/g, " ").trim();

      // Parse "Providers w/ OAuth/tokens (N): provider1 (N), provider2 (N), ..."
      const authLine = raw.match(/Providers w\/\s*OAuth\/tokens\s*\(\d+\)\s*:\s*(.+)/);
      const authedStr = authLine ? authLine[1].toLowerCase() : "";

      for (const chunk of modelStr.split(",")) {
        const id = chunk.trim();
        if (!id) continue;

        const provider = id.split("/")[0] || "unknown";

        // Find alias pointing to this model
        let alias: string | undefined;
        for (const [a, mid] of aliases) {
          if (mid === id) { alias = a; break; }
        }

        // Check if provider has auth configured
        const auth = authedStr.includes(provider);
        const isFree = provider === "github-copilot";

        models.push({
          id,
          alias,
          provider,
          auth,
          tags: isFree ? ["free"] : [],
        });
      }
    }

    _cachedModels = models;
    _cachedAliases = aliases;
    _cacheTime = now;
    return { models, aliases };
  } catch {
    return { models: [], aliases: new Map() };
  }
}

function getAvailableModels(): ModelInfo[] {
  return parseModelsStatus().models;
}

function resolveModel(nameOrAlias: string, models: ModelInfo[]): ModelInfo | undefined {
  const { aliases } = parseModelsStatus();
  // Check if it's an alias
  const fullId = aliases.get(nameOrAlias);
  if (fullId) {
    const found = models.find((m) => m.id === fullId);
    if (found) return found;
    // Alias exists but model might not be in filtered list -- still valid
    return { id: fullId, alias: nameOrAlias, provider: fullId.split("/")[0], auth: true, tags: [] };
  }
  // Direct model ID match
  return models.find((m) => m.id === nameOrAlias);
}

// ---------------------------------------------------------------------------
// Task Classification
// ---------------------------------------------------------------------------

const TASK_KEYWORDS: Record<string, string[]> = {
  coding: [
    "build", "implement", "create", "code", "develop", "feature", "api",
    "endpoint", "function", "class", "module", "refactor", "fix", "bug",
    "rest", "graphql", "crud", "database", "migration", "test", "deploy",
  ],
  research: [
    "research", "analyze", "compare", "evaluate", "investigate", "study",
    "benchmark", "survey", "literature", "state of the art", "trend",
    "market", "competitor", "feasibility",
  ],
  security: [
    "security", "vulnerability", "audit", "penetration", "cve", "patch",
    "hardening", "encryption", "auth", "rbac", "cors", "xss", "injection",
    "compliance", "nis-2", "gdpr", "iso27001",
  ],
  review: [
    "review", "check", "verify", "validate", "inspect", "quality",
    "feedback", "improve", "optimize", "refine", "critique",
  ],
  bulk: [
    "batch", "bulk", "mass", "all", "every", "scan", "label", "tag",
    "categorize", "migrate", "convert", "transform", "update all",
  ],
};

function classifyTask(task: string): string {
  const lower = task.toLowerCase();
  let bestProfile = "coding";
  let bestScore = 0;

  for (const [profile, keywords] of Object.entries(TASK_KEYWORDS)) {
    const score = keywords.filter((kw) => lower.includes(kw)).length;
    if (score > bestScore) {
      bestScore = score;
      bestProfile = profile;
    }
  }

  return bestProfile;
}

// ---------------------------------------------------------------------------
// AAHP v3 Handoff Object
// ---------------------------------------------------------------------------

interface AahpHandoff {
  version: "3.0";
  taskId: string;
  phase: string;
  context: {
    task: string;
    subtask?: string;
    constraints: string[];
  };
  routing: {
    sourceModel: string;
    targetModel: string;
    mode: OrchestrateMode;
  };
  state: Record<string, unknown>;
}

function createHandoff(
  task: string,
  subtask: string | undefined,
  sourceModel: string,
  targetModel: string,
  mode: OrchestrateMode,
  state: Record<string, unknown> = {},
): AahpHandoff {
  return {
    version: "3.0",
    taskId: `orch-${Date.now().toString(36)}`,
    phase: subtask ? "execution" : "planning",
    context: {
      task,
      subtask,
      constraints: [
        "Respond with actionable output only",
        "No conversational filler",
        "Structured JSON or code output preferred",
        "Stay within the subtask scope",
      ],
    },
    routing: { sourceModel, targetModel, mode },
    state,
  };
}

// ---------------------------------------------------------------------------
// Help & Formatting
// ---------------------------------------------------------------------------

function formatModelList(models: ModelInfo[]): string {
  const { aliases } = parseModelsStatus();
  const lines: string[] = [`*Available Models (${models.length}):*\n`];

  const byProvider = new Map<string, ModelInfo[]>();
  for (const m of models) {
    const list = byProvider.get(m.provider) || [];
    list.push(m);
    byProvider.set(m.provider, list);
  }

  for (const [provider, pModels] of byProvider) {
    const free = provider === "github-copilot" ? " (FREE)" : "";
    lines.push(`*${provider}*${free} (${pModels.length})`);
    for (const m of pModels) {
      const alias = m.alias ? ` [${m.alias}]` : "";
      const authIcon = m.auth ? "✅" : "❌";
      lines.push(`  ${authIcon} ${m.id}${alias}`);
    }
    lines.push("");
  }

  lines.push(`*Aliases (${aliases.size}):*`);
  for (const [a, fullId] of aliases) {
    const free = fullId.startsWith("github-copilot") ? " FREE" : "";
    lines.push(`  ${a} -> ${fullId}${free}`);
  }

  return lines.join("\n");
}

function formatRecommendation(
  task: string,
  profile: string,
  taskProfile: TaskProfile,
  models: ModelInfo[],
): string {
  const lines: string[] = [];
  lines.push(`*Task Classification:* ${profile}`);
  lines.push(`*Task:* ${task}\n`);

  const resolve = (name: string) => {
    const m = resolveModel(name, models);
    const status = m ? "✅" : "❌";
    const free = name.includes("copilot") || (m?.provider || "").includes("copilot") ? " (FREE)" : "";
    return `${status} \`${name}\`${free}`;
  };

  lines.push(`*Recommended Setup:*`);
  lines.push(`  Planner: ${resolve(taskProfile.planner)}`);
  lines.push(`  Workers: ${taskProfile.workers.map(resolve).join(", ")}`);
  lines.push(`  Reviewer: ${resolve(taskProfile.reviewer)}`);
  lines.push("");
  lines.push(`*Why:*`);

  const reasons: Record<string, string> = {
    coding: "Opus plans the architecture, Codex models execute fast, Sonnet reviews for quality.",
    research: "Gemini 2.5 Pro has 1M context for deep analysis, Flash models for parallel breadth, Opus synthesizes.",
    security: "Opus identifies attack vectors, Sonnet + Gemini cross-validate findings from different perspectives.",
    review: "Opus plans review criteria, dual Sonnet models catch different issues, Opus merges findings.",
    bulk: "Haiku triages cheaply, Flash models process in parallel, Haiku validates results.",
  };
  lines.push(`  ${reasons[profile] || "Balanced model selection for this task type."}`);

  lines.push("");
  lines.push(`*Run it:*`);
  lines.push(
    `/orchestrate --mode fan-out --task "${task}" --planner ${taskProfile.planner} --workers ${taskProfile.workers.join(",")} --reviewer ${taskProfile.reviewer}`,
  );

  return lines.join("\n");
}

function showHelp(models: ModelInfo[], profiles: Record<string, TaskProfile>): string {
  const lines: string[] = [];
  lines.push("*OpenClaw Model Orchestrator*\n");
  lines.push("Dispatch tasks across multiple LLMs with AAHP v3 handoffs.\n");

  lines.push("*Modes:*");
  lines.push("  `fan-out` - Split task into subtasks, run parallel on different models");
  lines.push("  `pipeline` - Chain models sequentially: plan -> code -> review -> cleanup");
  lines.push("  `consensus` - Same task to multiple models, compare & merge results\n");

  lines.push("*Usage:*");
  lines.push("  `/orchestrate help` - This help");
  lines.push("  `/orchestrate models` - List available models");
  lines.push('  `/orchestrate recommend "your task"` - Get model recommendations');
  lines.push("  `/orchestrate --mode fan-out --task \"Build X\" --planner opus --workers copilot52c,grokfast --reviewer copilot-sonnet46`");
  lines.push("  `/orchestrate --mode consensus --task \"Review security of X\" --workers opus,gemini25,sonnet`");
  lines.push("  `/orchestrate --mode pipeline --task \"Build and test feature X\"`\n");

  lines.push("*Shorthand:*");
  lines.push('  `/orchestrate --task "Build X"` - Auto-detects mode + models based on task');
  lines.push('  `/orchestrate --task "Build X" --profile coding` - Use predefined profile');
  lines.push("  Use `help` as value for any flag to get recommendations\n");

  lines.push("*Task Profiles:*");
  for (const [name, p] of Object.entries(profiles)) {
    lines.push(`  *${name}*: planner=${p.planner} workers=${p.workers.join(",")} reviewer=${p.reviewer}`);
  }

  lines.push(`\n*Models:* ${models.length} configured (use \`/orchestrate models\` for full list)`);
  lines.push(`*AAHP v3:* Structured handoffs between models -- 98% token reduction vs raw chat history`);

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Orchestration Execution
// ---------------------------------------------------------------------------

async function executeFanOut(
  req: OrchestrateRequest,
  api: any,
): Promise<string> {
  const lines: string[] = [];
  lines.push(`*Fan-Out Orchestration*`);
  lines.push(`Task: ${req.task}`);
  lines.push(`Planner: \`${req.planner}\` | Workers: \`${req.workers.join(", ")}\` | Reviewer: \`${req.reviewer}\`\n`);

  lines.push("*Phase 1: Planning...*");
  const planHandoff = createHandoff(req.task, undefined, "user", req.planner, "fan-out");

  const planPrompt = `You are a task planner. Break down this task into ${req.workers.length} independent subtasks that can be executed in parallel by different AI models.

Task: ${req.task}

Respond with a JSON array of subtask objects:
[{"id": 1, "title": "...", "description": "...", "expectedOutput": "..."}]

Rules:
- Each subtask must be independently executable
- Be specific and actionable
- No conversational filler
- ${req.workers.length} subtasks exactly`;

  let subtasks: Array<{ id: number; title: string; description: string; expectedOutput: string }>;
  try {
    const planResult = await api.inference({
      model: req.planner,
      messages: [{ role: "user", content: planPrompt }],
      maxTokens: 2000,
    });
    const content = planResult?.content || planResult?.message?.content || "";
    const jsonMatch = content.match(/\[[\s\S]*\]/);
    subtasks = jsonMatch ? JSON.parse(jsonMatch[0]) : [];
    if (!subtasks.length) {
      return lines.join("\n") + "\n\nPlanner returned no subtasks. Aborting.";
    }
    lines.push(`  Planned ${subtasks.length} subtasks`);
    for (const st of subtasks) {
      lines.push(`  ${st.id}. ${st.title}`);
    }
    lines.push("");
  } catch (e: any) {
    return lines.join("\n") + `\n\nPlanner error: ${e.message}`;
  }

  lines.push("*Phase 2: Parallel Execution...*");
  const results: Array<{ worker: string; subtask: string; result: string }> = [];

  const workerPromises = subtasks.map(async (st, i) => {
    const workerModel = req.workers[i % req.workers.length];
    const handoff = createHandoff(req.task, st.description, req.planner, workerModel, "fan-out", {
      subtaskId: st.id,
      parentPlan: subtasks.map((s) => s.title),
    });

    const workerPrompt = `You are executing a subtask as part of a larger project.

AAHP Handoff:
${JSON.stringify(handoff, null, 2)}

Your subtask: ${st.title}
Description: ${st.description}
Expected output: ${st.expectedOutput}

Execute this subtask now. Provide only the deliverable output, no explanation or filler.`;

    try {
      const result = await api.inference({
        model: workerModel,
        messages: [{ role: "user", content: workerPrompt }],
        maxTokens: 4000,
      });
      const content = result?.content || result?.message?.content || "(no output)";
      results.push({ worker: workerModel, subtask: st.title, result: content });
      lines.push(`  [${workerModel}] ${st.title} -- done`);
    } catch (e: any) {
      results.push({ worker: workerModel, subtask: st.title, result: `ERROR: ${e.message}` });
      lines.push(`  [${workerModel}] ${st.title} -- failed: ${e.message}`);
    }
  });

  await Promise.all(workerPromises);
  lines.push("");

  lines.push("*Phase 3: Review & Merge...*");
  const reviewPrompt = `You are a senior reviewer. Multiple AI workers executed subtasks in parallel. Review and merge their outputs into a coherent final result.

Original task: ${req.task}

Worker results:
${results.map((r) => `--- [${r.worker}] ${r.subtask} ---\n${r.result}`).join("\n\n")}

Provide a merged, quality-checked final output. Flag any issues or conflicts between worker outputs. Be concise.`;

  try {
    const reviewResult = await api.inference({
      model: req.reviewer,
      messages: [{ role: "user", content: reviewPrompt }],
      maxTokens: 4000,
    });
    const content = reviewResult?.content || reviewResult?.message?.content || "(no review output)";
    lines.push(`  Review complete by \`${req.reviewer}\`\n`);
    lines.push("*Final Result:*");
    lines.push(content);
  } catch (e: any) {
    lines.push(`  Review failed: ${e.message}`);
    lines.push("\n*Raw Worker Results:*");
    for (const r of results) {
      lines.push(`\n--- [${r.worker}] ${r.subtask} ---`);
      lines.push(r.result);
    }
  }

  return lines.join("\n");
}

async function executePipeline(
  req: OrchestrateRequest,
  api: any,
): Promise<string> {
  const lines: string[] = [];
  const chain = [req.planner, ...req.workers, req.reviewer];
  const phases = ["Planning", ...req.workers.map((_, i) => `Execution ${i + 1}`), "Review"];

  lines.push(`*Pipeline Orchestration*`);
  lines.push(`Task: ${req.task}`);
  lines.push(`Chain: ${chain.map((m) => `\`${m}\``).join(" -> ")}\n`);

  let state: Record<string, unknown> = {};
  let lastOutput = "";

  for (let i = 0; i < chain.length; i++) {
    const model = chain[i];
    const phase = phases[i] || `Step ${i + 1}`;
    lines.push(`*${phase}:* \`${model}\``);

    const handoff = createHandoff(req.task, phase, i > 0 ? chain[i - 1] : "user", model, "pipeline", state);

    const prompt =
      i === 0
        ? `You are the planner in a multi-model pipeline. Plan the approach for this task, then produce an initial output that the next model will refine.

Task: ${req.task}

Provide structured output that can be handed off.`
        : i === chain.length - 1
          ? `You are the final reviewer in a multi-model pipeline. Review and polish the output from the previous model.

Original task: ${req.task}
Previous output:
${lastOutput}

AAHP Handoff: ${JSON.stringify(handoff)}

Provide the final, polished result.`
          : `You are step ${i + 1} in a multi-model pipeline. Take the previous model's output and improve/extend it.

Original task: ${req.task}
Previous output:
${lastOutput}

AAHP Handoff: ${JSON.stringify(handoff)}

Improve and extend this output. Stay focused on the task.`;

    try {
      const result = await api.inference({
        model,
        messages: [{ role: "user", content: prompt }],
        maxTokens: 4000,
      });
      lastOutput = result?.content || result?.message?.content || "(no output)";
      state = { ...state, [`step_${i}`]: { model, phase, outputLength: lastOutput.length } };
      lines.push(`  Done (${lastOutput.length} chars)`);
    } catch (e: any) {
      lines.push(`  Failed: ${e.message}`);
      break;
    }
  }

  lines.push("\n*Final Result:*");
  lines.push(lastOutput);
  return lines.join("\n");
}

async function executeConsensus(
  req: OrchestrateRequest,
  api: any,
): Promise<string> {
  const lines: string[] = [];
  const allWorkers = [req.planner, ...req.workers];

  lines.push(`*Consensus Orchestration*`);
  lines.push(`Task: ${req.task}`);
  lines.push(`Models: ${allWorkers.map((m) => `\`${m}\``).join(", ")}`);
  lines.push(`Synthesizer: \`${req.reviewer}\`\n`);

  lines.push("*Phase 1: Parallel Query...*");
  const responses: Array<{ model: string; response: string }> = [];

  const promises = allWorkers.map(async (model) => {
    const prompt = `${req.task}

Provide a thorough, well-structured response. Be specific and actionable.`;

    try {
      const result = await api.inference({
        model,
        messages: [{ role: "user", content: prompt }],
        maxTokens: 4000,
      });
      const content = result?.content || result?.message?.content || "(no output)";
      responses.push({ model, response: content });
      lines.push(`  [${model}] responded (${content.length} chars)`);
    } catch (e: any) {
      responses.push({ model, response: `ERROR: ${e.message}` });
      lines.push(`  [${model}] failed: ${e.message}`);
    }
  });

  await Promise.all(promises);
  lines.push("");

  lines.push("*Phase 2: Synthesis...*");
  const synthPrompt = `You received responses from ${responses.length} different AI models to the same question. Synthesize the best answer by:
1. Identifying points of agreement (high confidence)
2. Noting disagreements or unique insights
3. Producing a final, merged answer that takes the best from each

Question: ${req.task}

Responses:
${responses.map((r) => `--- [${r.model}] ---\n${r.response}`).join("\n\n")}

Provide:
1. A brief comparison (which models agreed/disagreed on what)
2. The synthesized final answer`;

  try {
    const result = await api.inference({
      model: req.reviewer,
      messages: [{ role: "user", content: synthPrompt }],
      maxTokens: 4000,
    });
    const content = result?.content || result?.message?.content || "(no synthesis)";
    lines.push(`  Synthesized by \`${req.reviewer}\`\n`);
    lines.push("*Consensus Result:*");
    lines.push(content);
  } catch (e: any) {
    lines.push(`  Synthesis failed: ${e.message}`);
    lines.push("\n*Raw Responses:*");
    for (const r of responses) {
      lines.push(`\n--- [${r.model}] ---`);
      lines.push(r.response);
    }
  }

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Argument Parsing
// ---------------------------------------------------------------------------

function parseArgs(argsStr: string): Record<string, string> {
  const result: Record<string, string> = {};
  const regex = /--(\w[\w-]*)\s+(?:"([^"]*)"|'([^']*)'|(\S+))/g;
  let match;
  while ((match = regex.exec(argsStr)) !== null) {
    result[match[1]] = match[2] ?? match[3] ?? match[4];
  }
  const bare = argsStr.trim().split(/\s+/)[0];
  if (bare && !bare.startsWith("--")) {
    result._subcommand = bare;
  }
  return result;
}

// ---------------------------------------------------------------------------
// Plugin Registration
// ---------------------------------------------------------------------------

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    defaultPlanner?: string;
    defaultReviewer?: string;
    defaultWorkers?: string[];
    maxConcurrent?: number;
    taskProfiles?: Record<string, TaskProfile>;
  };

  if (cfg.enabled === false) return;

  const taskProfiles = cfg.taskProfiles || {};

  api.registerCommand({
    name: "orchestrate",
    description: "Multi-LLM orchestration with AAHP v3 handoffs",
    usage: "/orchestrate [help|models|recommend] [--mode fan-out|pipeline|consensus] [--task \"...\"]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const argsStr = String(ctx?.args ?? "").trim();
      const models = getAvailableModels();
      const args = parseArgs(argsStr || "");
      const subcommand = args._subcommand || "";

      const reply = (text: string) => ({ text });

      // /orchestrate help
      if (!argsStr || subcommand === "help") {
        return reply(showHelp(models, taskProfiles));
      }

      // /orchestrate models
      if (subcommand === "models") {
        return reply(formatModelList(models));
      }

      // /orchestrate recommend "task"
      if (subcommand === "recommend") {
        const task = argsStr.replace(/^recommend\s*/, "").replace(/^["']|["']$/g, "").trim();
        if (!task) return reply("Usage: `/orchestrate recommend \"your task description\"`");
        const profile = classifyTask(task);
        const tp = taskProfiles[profile] || {
          planner: cfg.defaultPlanner || "copilot-opus",
          workers: cfg.defaultWorkers || ["copilot52c", "grokfast"],
          reviewer: cfg.defaultReviewer || "copilot-sonnet46",
        };
        return reply(formatRecommendation(task, profile, tp, models));
      }

      // /orchestrate --mode ... --task ...
      const task = args.task;
      if (!task) {
        return reply("Missing `--task`. Usage: `/orchestrate --task \"your task\" [--mode fan-out] [--planner opus] [--workers copilot52c,grokfast] [--reviewer copilot-sonnet46]`");
      }

      const profile = args.profile || classifyTask(task);
      const tp = taskProfiles[profile] || {
        planner: cfg.defaultPlanner || "copilot-opus",
        workers: cfg.defaultWorkers || ["copilot52c", "grokfast"],
        reviewer: cfg.defaultReviewer || "copilot-sonnet46",
      };

      let planner = args.planner || tp.planner;
      if (planner === "help") return reply(formatRecommendation(task, profile, tp, models));

      let workers: string[];
      if (args.workers === "help") return reply(formatRecommendation(task, profile, tp, models));
      workers = args.workers ? args.workers.split(",").map((w: string) => w.trim()) : tp.workers;

      let reviewer = args.reviewer || tp.reviewer;
      if (reviewer === "help") return reply(formatRecommendation(task, profile, tp, models));

      const mode: OrchestrateMode = (args.mode as OrchestrateMode) || "fan-out";
      const req: OrchestrateRequest = { mode, task, planner, workers, reviewer, profile };

      // Validate models
      const allModels = [planner, ...workers, reviewer];
      const missing = allModels.filter((m) => !resolveModel(m, models));
      if (missing.length > 0) {
        return reply(`Unknown models: ${missing.map((m) => `\`${m}\``).join(", ")}. Use \`/orchestrate models\` to see available models.`);
      }

      let result: string;
      switch (mode) {
        case "fan-out":
          result = await executeFanOut(req, api);
          break;
        case "pipeline":
          result = await executePipeline(req, api);
          break;
        case "consensus":
          result = await executeConsensus(req, api);
          break;
        default:
          result = `Unknown mode: \`${mode}\`. Supported: fan-out, pipeline, consensus`;
      }
      return reply(result);
    },
  });
}
