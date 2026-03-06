/**
 * mindgraph-context hook
 * Fires on agent:bootstrap — pulls context from mindgraph-server
 * and injects it into BOOTSTRAP.md so the agent sees it on session start.
 *
 * Main session:  3 fixed queries — active Goals, active Projects, hard Constraints
 * Sub-agent/cron: task-query context (FTS + semantic) + fixed queries appended
 *
 * Failure mode: always silent — never blocks session start.
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import * as path from "node:path";
import * as fs from "node:fs/promises";

const execFileAsync = promisify(execFile);

const handler = async (event: {
  type: string;
  action: string;
  context: {
    workspaceDir: string;
    sessionKey?: string;
    sessionId?: string;
    bootstrapFiles: Array<{ name: string; path: string; content?: string; missing: boolean }>;
  };
}) => {
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  const ctx = event.context;
  const workspaceDir = ctx.workspaceDir;
  const sessionKey = ctx.sessionKey || "";
  const isSubAgent = sessionKey.includes(":sub:");
  const isCron = sessionKey.includes(":cron:");
  const isMain = !isSubAgent && !isCron;

  const bridgePath = path.join(workspaceDir, "mindgraph-bridge.js");
  const clientPath = path.join(workspaceDir, "mindgraph-client.js");

  // Bail if dependencies missing
  try {
    await fs.access(bridgePath);
    await fs.access(clientPath);
  } catch {
    return;
  }

  // ─── Helper: run a node script inline ────────────────────────────────────
  async function runNode(script: string, timeoutMs = 8000): Promise<string> {
    try {
      const { stdout } = await execFileAsync(
        "node",
        ["-e", script],
        { timeout: timeoutMs, env: { ...process.env }, cwd: workspaceDir }
      );
      return stdout.trim();
    } catch {
      return "";
    }
  }

  // ─── Helper: run mindgraph-bridge.js CLI ─────────────────────────────────
  async function runBridge(args: string[], timeoutMs = 8000): Promise<string> {
    try {
      const { stdout } = await execFileAsync(
        "node",
        [bridgePath, ...args],
        { timeout: timeoutMs, env: { ...process.env }, cwd: workspaceDir }
      );
      return stdout.trim();
    } catch {
      return "";
    }
  }

  // ─── Fixed queries: Goals, Projects, Constraints ─────────────────────────
  async function fetchFixedContext(): Promise<string> {
    const script = `
const mg = require('./mindgraph-client.js');
(async () => {
  const lines = [];

  // Active Goals
  try {
    const goals = await mg.activeGoals();
    if (goals && goals.length) {
      lines.push('### 🎯 Active Goals');
      for (const g of goals) {
        const pri = g.props?.priority ? \` [\${g.props.priority}]\` : '';
        const prog = g.props?.progress != null ? \` (\${Math.round(g.props.progress * 100)}%)\` : '';
        lines.push(\`- **\${g.label}**\${pri}\${prog}: \${g.props?.description || g.summary || ''}\`);
      }
      lines.push('');
    }
  } catch {}

  // Active Projects — typed query /nodes?node_type=Project (server-filtered, no full scan)
  try {
    const res = await mg.getNodes({ nodeType: 'Project', limit: 50 });
    const all = res.items || res;
    const DONE = ['completed', 'archived', 'cancelled'];
    const projects = all.filter(n =>
      !n.props?.status || !DONE.includes(n.props.status.toLowerCase())
    );
    if (projects.length) {
      lines.push('### 📁 Active Projects');
      for (const p of projects.slice(0, 8)) {
        lines.push(\`- **\${p.label}**: \${p.props?.description || p.summary || ''}\`);
      }
      lines.push('');
    }
  } catch {}

  // Hard Constraints — typed query /nodes?node_type=Constraint (server-filtered, no full scan)
  try {
    const res = await mg.getNodes({ nodeType: 'Constraint', limit: 100 });
    const all = res.items || res;
    const hard = all.filter(n => n.props?.hard === true);
    if (hard.length) {
      lines.push('### 🚫 Hard Constraints (' + hard.length + ')');
      for (const c of hard.slice(0, 15)) {
        lines.push(\`- \${c.props?.description || c.label}\`);
      }
      lines.push('');
    }
  } catch {}

  // Decisions — recent 10 decisions
  try {
    const res = await mg.getNodes({ nodeType: 'Decision', limit: 10 });
    const decisions = res.items || res;
    if (decisions && decisions.length) {
      lines.push(\`### ⚠️ Recent Decisions (\${decisions.length})\`);
      for (const d of decisions) {
        const status = d.props?.status ? \` [\${d.props.status}]\` : '';
        lines.push(\`- **\${d.label}**\${status}: \${d.props?.question || d.props?.description || d.summary || ''}\`);
      }
      lines.push('');
    }
  } catch {}

  // Recent Observations — news events, etc.
  try {
    const res = await mg.getNodes({ nodeType: 'Observation', limit: 5 });
    const obs = res.items || res;
    if (obs && obs.length) {
      lines.push(\`### 🗞️ Recent Observations (\${obs.length})\`);
      for (const o of obs) {
        lines.push(\`- **\${o.label}**: \${o.props?.content || o.summary || ''}\`);
      }
      lines.push('');
    }
  } catch {}

  // Open Decisions — actionable, needs resolution
  try {
    const res = await mg.getNodes({ nodeType: 'Decision', limit: 50 });
    const all = res.items || res;
    const open = all.filter(n => !n.tombstone_at && n.props?.status === 'open').slice(0, 5);
    if (open.length) {
      lines.push(\`### 🔓 Open Decisions (\${open.length})\`);
      for (const d of open) {
        lines.push(\`- **\${d.label}**: \${d.props?.question || d.props?.description || d.summary || ''}\`);
      }
      lines.push('');
    }
  } catch {}

  // Pending Tasks
  try {
    const res = await mg.getNodes({ nodeType: 'Task', limit: 100 });
    const all = res.items || res;
    const pending = all.filter(n =>
      !n.tombstone_at &&
      ['pending', 'active'].includes(n.props?.status || '')
    ).slice(0, 8);
    if (pending.length) {
      lines.push(\`### ✅ Pending Tasks (\${pending.length})\`);
      for (const t of pending) {
        const pri = t.props?.priority ? \` [\${t.props.priority}]\` : '';
        lines.push(\`- **\${t.label}**\${pri}\`);
      }
      lines.push('');
    }
  } catch {}

  console.log(lines.join('\\n'));
})().catch(() => {});
`;
    return runNode(script, 10000);
  }

  // ─── Semantic context for main session ───────────────────────────────────
  async function fetchSemanticContext(): Promise<string> {
    // Build query from the previous session's last assistant messages —
    // more focused than daily notes (which reflect completed work, not intent).
    // Fallback: most recent daily notes file.
    let query = "";

    try {
      const sessionsDir = path.join(workspaceDir, "..", "agents", "main", "sessions");

      // Find the current session file from sessions.json
      const sessionsJson = JSON.parse(await fs.readFile(path.join(sessionsDir, "sessions.json"), "utf-8"));
      const currentSessionId: string = sessionsJson["agent:main:main"]?.sessionId || "";

      // Get all JSONL files sorted by modification time (most recent first)
      const { readdir, stat } = fs;
      const allFiles = (await readdir(sessionsDir)).filter((f: string) => f.endsWith(".jsonl"));
      const withStats = await Promise.all(
        allFiles.map(async (f: string) => ({
          f,
          mtime: (await stat(path.join(sessionsDir, f))).mtimeMs,
        }))
      );
      withStats.sort((a: any, b: any) => b.mtime - a.mtime);

      // Skip the current session — use the 2nd and 3rd most recent for prior context
      const candidates = withStats
        .filter((x: any) => !x.f.startsWith(currentSessionId))
        .slice(0, 3)
        .map((x: any) => path.join(sessionsDir, x.f));

      for (const sessionFile of candidates) {
        try {
          const lines = (await fs.readFile(sessionFile, "utf-8")).split("\n").filter(Boolean);
          const msgs: string[] = [];
          for (const line of [...lines].reverse()) {
            if (msgs.length >= 5) break;
            try {
              const d = JSON.parse(line);
              if (d.type === "message" && d.message?.role === "assistant") {
                const content = d.message.content;
                const text = Array.isArray(content)
                  ? content.filter((c: any) => c.type === "text").map((c: any) => c.text).join(" ")
                  : String(content || "");
                if (text.trim().length > 30) msgs.push(text.trim().slice(0, 300));
              }
            } catch {}
          }
          if (msgs.length >= 2) {
            query = msgs.reverse().join(" ").replace(/\n+/g, " ").trim().slice(0, 600);
            break;
          }
        } catch {}
      }
    } catch {}

    // Fallback: daily notes
    if (!query) {
      const now = new Date();
      for (let offset = 0; offset < 2; offset++) {
        const d = new Date(now);
        d.setDate(d.getDate() - offset);
        const notePath = path.join(workspaceDir, "memory", `${d.toISOString().slice(0, 10)}.md`);
        try {
          const raw = await fs.readFile(notePath, "utf-8");
          query += raw.slice(0, 1500);
          if (query.length >= 2000) break;
        } catch {}
      }
      query = query.replace(/#+\s*/g, "").replace(/\n+/g, " ").trim().slice(0, 600);
    }

    if (!query.trim()) return "";

    const script = `
const mg = require('./mindgraph-client.js');
const key = process.env.OPENAI_API_KEY;
if (!key) { process.exit(0); }

(async () => {
  try {
    const results = await mg.retrieve('semantic', { query: ${JSON.stringify(query)}, limit: 20 });
    const items = Array.isArray(results) ? results : (results.items || []);
    if (!items.length) return;

    // Exclude only extraction noise (no semantic value in bootstrap)
    const NOISE_TYPES = new Set(['Source', 'Session']);

    // Deduplicate by uid, filter noise + low scores, take top 6
    const seen = new Set();
    const relevant = items
      .filter(n => {
        if ((n.score || 0) < 0.55) return false;
        if (NOISE_TYPES.has(n.node_type)) return false;
        if (n.tombstone_at) return false;
        if (seen.has(n.uid)) return false;
        seen.add(n.uid);
        return true;
      })
      .slice(0, 6);
    if (!relevant.length) return;

    const lines = ['### 🔍 Relevant Context (semantic)'];
    for (const n of relevant) {
      const score = Math.round((n.score || 0) * 100);
      const desc = n.props?.description || n.props?.content || n.summary || '';
      lines.push(\`- **\${n.label}** [\${n.node_type}] (\${score}%): \${desc.slice(0, 120)}\`);
    }
    lines.push('');
    console.log(lines.join('\\n'));
  } catch {}
})();
`;
    return runNode(script, 12000);
  }

  // ─── Task-specific context for sub-agents/crons ───────────────────────────
  async function fetchTaskContext(): Promise<string> {
    const sessionId = ctx.sessionId || "";
    const parts = sessionKey.split(":");
    const possibleIds = [sessionId, parts[parts.length - 1]].filter(Boolean);

    let taskQuery = "";
    for (const id of possibleIds) {
      const taskFile = path.join(workspaceDir, `.mindgraph-task-${id}.tmp`);
      try {
        const raw = await fs.readFile(taskFile, "utf-8");
        taskQuery = raw.trim().slice(0, 500);
        await fs.unlink(taskFile).catch(() => {});
        break;
      } catch {}
    }

    if (!taskQuery) return "";
    return runBridge(["context", "--query", taskQuery], 8000);
  }

  // ─── Build BOOTSTRAP.md content ──────────────────────────────────────────
  const sections: string[] = [];

  if (isMain) {
    // Main session: fixed context + semantic pass from recent daily notes
    const [fixed, semantic] = await Promise.all([fetchFixedContext(), fetchSemanticContext()]);
    if (fixed || semantic) {
      sections.push("## MindGraph Context\n");
      if (fixed) sections.push(fixed);
      if (semantic) sections.push(semantic);
      sections.push("_Injected by mindgraph-context hook at session start._");
    }
  } else {
    // Sub-agent/cron: task context first, then fixed queries appended
    const [taskCtx, fixed] = await Promise.all([fetchTaskContext(), fetchFixedContext()]);
    if (taskCtx) {
      sections.push(taskCtx);
    }
    if (fixed) {
      sections.push("\n## MindGraph Context\n");
      sections.push(fixed);
      sections.push(`\n_Injected by mindgraph-context hook — ${isSubAgent ? "sub-agent" : "cron"} session._`);
    }
  }

  if (!sections.length) return;

  const bootstrapContent = sections.join("\n") + "\n";

  const existingIdx = ctx.bootstrapFiles.findIndex((f) => f.name === "BOOTSTRAP.md");
  if (existingIdx >= 0) {
    ctx.bootstrapFiles[existingIdx] = {
      ...ctx.bootstrapFiles[existingIdx],
      content: bootstrapContent,
      missing: false,
    };
  } else {
    ctx.bootstrapFiles.push({
      name: "BOOTSTRAP.md",
      path: path.join(workspaceDir, "BOOTSTRAP.md"),
      content: bootstrapContent,
      missing: false,
    });
  }
};

export default handler;
