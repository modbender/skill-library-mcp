import fs from "node:fs";
import path from "node:path";
import os from "node:os";

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    includeTips?: boolean;
    workspacePath?: string;
    // Optional: user-supplied help sections. Keep defaults generic.
    sections?: Array<{ title: string; lines: string[] }>;
  };
  if (cfg.enabled === false) return;

  const includeTips = cfg.includeTips !== false;
  const workspacePath = String(cfg.workspacePath ?? "~/.openclaw/workspace");
  const resolvedWorkspace = workspacePath.startsWith("~")
    ? path.join(os.homedir(), workspacePath.slice(1))
    : workspacePath;

  function listProjects(): string[] {
    try {
      const entries = fs.readdirSync(resolvedWorkspace, { withFileTypes: true });
      return entries
        .filter((e) => e.isDirectory())
        .map((e) => e.name)
        .filter((name) => !name.startsWith("."))
        .filter((name) => fs.existsSync(path.join(resolvedWorkspace, name, ".git")))
        .sort((a, b) => a.localeCompare(b));
    } catch {
      return [];
    }
  }

  function readPackageVersion(repoDir: string): string | null {
    try {
      const pj = path.join(resolvedWorkspace, repoDir, "package.json");
      if (!fs.existsSync(pj)) return null;
      const raw = fs.readFileSync(pj, "utf-8");
      const j = JSON.parse(raw);
      const v = String(j?.version ?? "").trim();
      return v || null;
    } catch {
      return null;
    }
  }


  api.registerCommand({
    name: "shortcuts",
    description: "Show local shortcuts and helper commands (generic by default)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const lines: string[] = [];
      lines.push("Shortcuts");
      lines.push("");

      // Generic placeholders only. Users can configure their own sections.
      const sections = cfg.sections ?? [
        {
          title: "Shortcuts",
          lines: [
            "- /<project>   - Project shortcut (configured by user)",
            "- /<command>   - A custom command (configured by user)",
          ],
        },
        {
          title: "Memory",
          lines: [
            "- /remember-<x> <text>  - Save a note (if installed)",
            "- <trigger phrase>: ... - Optional explicit capture trigger",
          ],
        },
        {
          title: "TODO",
          lines: [
            "- /todo-list",
            "- /todo-add <text>",
            "- /todo-done <index>",
          ],
        },
      ];

      for (const s of sections) {
        lines.push(s.title + ":");
        for (const ln of s.lines) lines.push(ln);
        lines.push("");
      }

      if (includeTips) {
        lines.push("Tips:");
        lines.push("- Keep infrastructure changes ask-first.");
        lines.push("- Keep secrets out of repos.");
        lines.push("");
      }

      lines.push("(This /help output is intentionally generic. Configure your own sections in plugin config.)");

      return { text: lines.join("\n") };
    },
  });

  function readOriginRepoSlug(repoDir: string): string | null {
    // Supports git@github.com:owner/repo.git and https://github.com/owner/repo(.git)
    try {
      const cfgPath = path.join(resolvedWorkspace, repoDir, ".git", "config");
      const raw = fs.readFileSync(cfgPath, "utf-8");
      const m = raw.match(/\[remote \"origin\"\][^\[]*?url\s*=\s*(.+)\s*/i);
      const url = (m?.[1] ?? "").trim();
      if (!url) return null;

      const mm = url.match(/github\.com[:/]+([^/\s]+)\/([^/\s]+?)(?:\.git)?$/i);
      if (!mm) return null;
      const owner = mm[1];
      const repo = mm[2];
      if (!owner || !repo) return null;
      return `${owner}/${repo}`;
    } catch {
      return null;
    }
  }

  function hasAnyRemote(repoDir: string): boolean {
    try {
      const cfgPath = path.join(resolvedWorkspace, repoDir, ".git", "config");
      const raw = fs.readFileSync(cfgPath, "utf-8");
      return /\[remote\s+"/i.test(raw);
    } catch {
      return false;
    }
  }

  type Vis = "public" | "private" | "unknown";

  function fmtVis(vis: Vis): string {
    // Chat surfaces usually don't support ANSI colors reliably.
    // Use symbols by default.
    if (vis === "public") return "🟩 public";
    if (vis === "private") return "🟥 private";
    return "⬜ unknown";
  }

  async function getGithubVisibility(slug: string): Promise<Vis> {
    try {
      // Use gh CLI (already configured in your environment). Keep it best-effort.
      const { execSync } = await import("node:child_process");
      const out = execSync(`gh repo view ${slug} --json visibility --jq .visibility`, {
        stdio: ["ignore", "pipe", "ignore"],
      }).toString("utf-8").trim().toLowerCase();

      if (out === "public" || out === "private" || out === "internal") {
        // internal treated as private from user's perspective
        return out === "public" ? "public" : "private";
      }
      return "unknown";
    } catch {
      return "unknown";
    }
  }

  api.registerCommand({
    name: "projects",
    description: "List local projects (git repos) in the workspace",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const projects = listProjects();
      if (projects.length === 0) {
        return { text: `No git projects found under ${resolvedWorkspace}.` };
      }

      const rows: Array<{ name: string; ver: string; vis: string }> = [];

      for (const p of projects) {
        const ver = readPackageVersion(p) ?? "-";
        const slug = readOriginRepoSlug(p);
        if (!slug) {
          const anyRemote = hasAnyRemote(p);
          rows.push({ name: p, ver, vis: anyRemote ? "⬜ remote" : "⬜ local" });
          continue;
        }
        const vis = await getGithubVisibility(slug);
        rows.push({ name: p, ver, vis: fmtVis(vis) });
      }

      // Format in a code block to avoid text salad on proportional fonts
      const nameW = Math.min(40, Math.max(...rows.map((r) => r.name.length)));
      const verW = Math.min(10, Math.max(...rows.map((r) => r.ver.length)));

      const lines: string[] = [];
      lines.push(`Projects (${projects.length}):`);
      lines.push("```text");
      for (const r of rows) {
        const n = r.name.padEnd(nameW, " ");
        const v = ("v" + r.ver).padEnd(verW + 1, " ");
        lines.push(`${n}  ${v}  ${r.vis}`);
      }
      lines.push("```");

      return { text: lines.join("\n") };
    },
  });
}

