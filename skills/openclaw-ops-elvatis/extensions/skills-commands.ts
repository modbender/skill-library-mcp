/**
 * openclaw-ops-elvatis Skills & Shortcuts Commands
 *
 * /skills    — all locally installed plugins with their commands
 * /shortcuts — flat cheat-sheet of every command, grouped by plugin
 */

import fs from "node:fs";
import path from "node:path";
import { readJsonSafe } from "../src/utils.js";

interface PluginCommand {
  name: string;
  description: string;
  acceptsArgs?: boolean;
}

interface PluginInfo {
  id: string;
  name: string;
  version: string;
  description: string;
  dirName: string;
  dirPath: string;
  commands: PluginCommand[];
  installed: boolean;
}

/**
 * Scan a plugin directory and extract all commands registered via api.registerCommand().
 * Reads .ts / .js source files and parses name + description fields.
 */
function extractCommandsFromSource(pluginPath: string): PluginCommand[] {
  const commands: PluginCommand[] = [];
  const seen = new Set<string>();

  // Collect all .ts and .js files (excluding node_modules / dist / out)
  function walk(dir: string): string[] {
    const results: string[] = [];
    try {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (["node_modules", "dist", "out", ".git"].includes(entry.name)) continue;
          results.push(...walk(full));
        } else if (entry.isFile() && (entry.name.endsWith(".ts") || entry.name.endsWith(".js")) && !entry.name.endsWith(".test.ts") && !entry.name.endsWith(".test.js")) {
          results.push(full);
        }
      }
    } catch { /* skip unreadable */ }
    return results;
  }

  for (const file of walk(pluginPath)) {
    let src = "";
    try { src = fs.readFileSync(file, "utf-8"); } catch { continue; }

    // Match registerCommand({ ... name: "xxx", ... description: "yyy" ... })
    // Handles multi-line blocks
    const blockRe = /registerCommand\s*\(\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}/g;
    let blockMatch: RegExpExecArray | null;
    while ((blockMatch = blockRe.exec(src)) !== null) {
      const block = blockMatch[1] ?? "";

      const nameMatch = block.match(/name\s*:\s*["'`]([^"'`]+)["'`]/);
      const descMatch = block.match(/description\s*:\s*["'`]([^"'`]+)["'`]/);
      const argsMatch = block.match(/acceptsArgs\s*:\s*(true|false)/);

      const cmdName = nameMatch?.[1]?.trim();
      if (!cmdName || seen.has(cmdName)) continue;
      seen.add(cmdName);

      commands.push({
        name: cmdName,
        description: descMatch?.[1]?.trim() ?? "(no description)",
        acceptsArgs: argsMatch?.[1] === "true",
      });
    }
  }

  return commands;
}

/**
 * Scan workspace for all openclaw-* plugin directories and build a full PluginInfo list.
 */
function scanInstalledPlugins(workspace: string): PluginInfo[] {
  const plugins: PluginInfo[] = [];

  // Also try the dev root (parent of workspace) — plugins may be checked out there
  const roots = [workspace];
  const devRoot = path.resolve(workspace, "..");
  if (devRoot !== workspace) roots.push(devRoot);

  const seen = new Set<string>();

  for (const root of roots) {
    let entries: fs.Dirent[] = [];
    try { entries = fs.readdirSync(root, { withFileTypes: true }); } catch { continue; }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (!entry.name.startsWith("openclaw-")) continue;
      if (seen.has(entry.name)) continue;

      const pluginPath = path.join(root, entry.name);
      const manifestPath = path.join(pluginPath, "openclaw.plugin.json");
      if (!fs.existsSync(manifestPath)) continue;

      seen.add(entry.name);

      const manifest = readJsonSafe<Record<string, any>>(manifestPath, {});

      // Read version from package.json if not in manifest
      let version: string = manifest.version ?? "";
      if (!version) {
        const pkg = readJsonSafe<{ version?: string } | null>(path.join(pluginPath, "package.json"), null);
        version = pkg?.version ?? "?";
      }

      const commands = extractCommandsFromSource(pluginPath);

      plugins.push({
        id: manifest.id ?? entry.name,
        name: manifest.name ?? entry.name,
        version,
        description: manifest.description ?? "",
        dirName: entry.name,
        dirPath: pluginPath,
        commands,
        installed: true, // in workspace = available/installed
      });
    }
  }

  // Sort: openclaw-ops-elvatis first, then alphabetical
  plugins.sort((a, b) => {
    if (a.dirName === "openclaw-ops-elvatis") return -1;
    if (b.dirName === "openclaw-ops-elvatis") return 1;
    return a.dirName.localeCompare(b.dirName);
  });

  return plugins;
}

export function registerSkillsCommands(api: any, workspace: string) {

  // ── /skills ───────────────────────────────────────────────────────────────────
  api.registerCommand({
    name: "skills",
    description: "Show all locally installed OpenClaw plugins (skills) with their commands",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const plugins = scanInstalledPlugins(workspace);
      const lines: string[] = [];

      lines.push(`Skills (${plugins.length} plugin${plugins.length !== 1 ? "s" : ""} found)`);
      lines.push("");

      if (plugins.length === 0) {
        lines.push("No openclaw-* plugins found in workspace.");
        lines.push(`Scanned: ${workspace}`);
        return { text: lines.join("\n") };
      }

      for (const plugin of plugins) {
        lines.push(`${plugin.name} v${plugin.version}`);
        if (plugin.description) lines.push(`  ${plugin.description}`);
        lines.push(`  Path: ${plugin.dirPath}`);

        if (plugin.commands.length > 0) {
          lines.push(`  Commands (${plugin.commands.length}):`);
          for (const cmd of plugin.commands) {
            const argHint = cmd.acceptsArgs ? " [args]" : "";
            lines.push(`    /${cmd.name}${argHint} — ${cmd.description}`);
          }
        } else {
          lines.push(`  Commands: (none detected in source)`);
        }
        lines.push("");
      }

      const totalCmds = plugins.reduce((n, p) => n + p.commands.length, 0);
      lines.push(`Total: ${plugins.length} skills, ${totalCmds} commands`);
      lines.push("Use /shortcuts for a flat command cheat-sheet");

      return { text: lines.join("\n") };
    },
  });

  // ── /shortcuts ────────────────────────────────────────────────────────────────
  api.registerCommand({
    name: "shortcuts",
    description: "Flat cheat-sheet of every command across all installed plugins",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const plugins = scanInstalledPlugins(workspace);
      const lines: string[] = [];

      const totalCmds = plugins.reduce((n, p) => n + p.commands.length, 0);
      lines.push(`Shortcuts — ${totalCmds} commands across ${plugins.length} plugins`);
      lines.push("");

      // Flat alphabetical index first
      const allCmds: Array<{ cmd: PluginCommand; pluginName: string }> = [];
      for (const plugin of plugins) {
        for (const cmd of plugin.commands) {
          allCmds.push({ cmd, pluginName: plugin.id });
        }
      }
      allCmds.sort((a, b) => a.cmd.name.localeCompare(b.cmd.name));

      lines.push("ALL COMMANDS (A-Z)");
      for (const { cmd, pluginName } of allCmds) {
        const argHint = cmd.acceptsArgs ? " [args]" : "";
        lines.push(`/${cmd.name}${argHint.padEnd(12)} ${cmd.description}  [${pluginName}]`);
      }

      // Grouped by plugin
      lines.push("");
      lines.push("BY PLUGIN");
      for (const plugin of plugins) {
        if (plugin.commands.length === 0) continue;
        lines.push(`\n${plugin.name} (${plugin.id})`);
        for (const cmd of plugin.commands) {
          const argHint = cmd.acceptsArgs ? " [args]" : "";
          lines.push(`  /${cmd.name}${argHint} — ${cmd.description}`);
        }
      }

      lines.push("");
      lines.push("Use /skills for full plugin details and paths");

      return { text: lines.join("\n") };
    },
  });
}
