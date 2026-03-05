/**
 * openclaw-ops-elvatis Phase 1 Extensions
 * Operational Command Board - High Priority Commands
 *
 * Commands: /health, /services, /logs, /plugins
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  expandHome,
  safeExec,
  runCmd,
  getSystemResources,
  checkGatewayStatus,
  loadActiveCooldowns,
  formatCooldownLine,
  readJsonSafe,
  listWorkspacePluginDirs,
} from "../src/utils.js";

export function registerPhase1Commands(api: any, workspace: string) {
  
  // ========================================
  // /health - System Health Overview
  // ========================================
  api.registerCommand({
    name: "health",
    description: "Quick system health check (gateway, resources, plugins)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const lines: string[] = [];
      lines.push("System Health");
      lines.push("");
      
      // Gateway Status
      lines.push("GATEWAY");
      const defaultStatus = checkGatewayStatus("default");
      const statusIcon = defaultStatus.running ? "✓" : "✗";
      lines.push(`- Default: ${statusIcon} ${defaultStatus.running ? "Running" : "Stopped"}`);
      if (defaultStatus.pid) lines.push(`  PID ${defaultStatus.pid}`);
      if (defaultStatus.uptime) lines.push(`  Uptime: ${defaultStatus.uptime}`);
      
      const stagingStatus = checkGatewayStatus("staging");
      const stageIcon = stagingStatus.running ? "✓" : "○";
      lines.push(`- Staging: ${stageIcon} ${stagingStatus.running ? "Running" : "Stopped"}`);
      
      // System Resources
      lines.push("");
      lines.push("RESOURCES");
      const resources = getSystemResources(workspace);
      lines.push(`- CPU load: ${resources.cpu}`);
      lines.push(`- Memory: ${resources.memory}`);
      lines.push(`- Disk: ${resources.disk}`);
      
      // Plugin Count
      lines.push("");
      lines.push("PLUGINS");
      const pluginList = runCmd("openclaw", ["plugins", "list"], 10000);
      if (pluginList.code === 0) {
        const count = pluginList.out.split("\n").filter(l => l.trim() && !l.startsWith("Installed")).length;
        lines.push(`- Installed: ${count}`);
      } else {
        lines.push("- Unable to count plugins");
      }
      
      // Cooldown Detection (model-failover state)
      lines.push("");
      lines.push("COOLDOWNS");
      const cooldowns = loadActiveCooldowns(workspace);
      if (cooldowns.length === 0) {
        lines.push("✓ None active");
      } else {
        lines.push(`⚠ ${cooldowns.length} model${cooldowns.length > 1 ? "s" : ""} in cooldown`);
        for (const cd of cooldowns.slice(0, 5)) {
          lines.push(`  ${formatCooldownLine(cd)}`);
          if (cd.reason) lines.push(`  Reason: ${cd.reason}`);
        }
        if (cooldowns.length > 5) {
          lines.push(`  ... and ${cooldowns.length - 5} more (use /limits for full list)`);
        }
      }

      // Last Error Check
      lines.push("");
      lines.push("ERRORS");
      const logDir = path.join(expandHome("~/.openclaw"), "logs");
      let lastError = "None detected";
      try {
        if (fs.existsSync(logDir)) {
          const logFiles = fs.readdirSync(logDir)
            .filter((f: string) => f.endsWith(".log"))
            .map((f: string) => path.join(logDir, f));
          
          for (const logFile of logFiles.slice(-3)) {
            const content = fs.readFileSync(logFile, "utf-8");
            const errorLines = content.split("\n").filter((l: string) => 
              l.toLowerCase().includes("error") || l.toLowerCase().includes("fatal")
            );
            if (errorLines.length > 0) {
              const lastLine = errorLines[errorLines.length - 1];
              lastError = `${path.basename(logFile)}: ${lastLine.slice(0, 60)}...`;
              break;
            }
          }
        }
      } catch {
        lastError = "Error reading logs";
      }
      lines.push(`- Last error: ${lastError}`);
      
      return { text: lines.join("\n") };
    },
  });

  // ========================================
  // /services - Comprehensive Service Status
  // ========================================
  api.registerCommand({
    name: "services",
    description: "Show all OpenClaw profiles and service status",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const lines: string[] = [];
      lines.push("Services Status");
      lines.push("");
      
      // Detect available profiles
      const openclawDir = expandHome("~/.openclaw");
      const profiles: string[] = ["default"];
      
      try {
        const entries = fs.readdirSync(path.dirname(openclawDir));
        for (const entry of entries) {
          if (entry.startsWith(".openclaw-") && entry !== ".openclaw-staging") {
            const profileName = entry.replace(".openclaw-", "");
            profiles.push(profileName);
          }
        }
        if (fs.existsSync(expandHome("~/.openclaw-staging"))) {
          profiles.push("staging");
        }
      } catch {
        // Continue with default only
      }
      
      lines.push(`PROFILES (${profiles.length})`);
      
      for (const profile of profiles) {
        const status = checkGatewayStatus(profile);
        const icon = status.running ? "▶" : "■";
        const state = status.running ? "Running" : "Stopped";
        lines.push(`${icon} ${profile}: ${state}`);
        if (status.running) {
          if (status.pid) lines.push(`  PID: ${status.pid}`);
          if (status.uptime) lines.push(`  Uptime: ${status.uptime}`);
          
          // Try to get port binding
          const configPath = profile === "default" 
            ? expandHome("~/.openclaw/config.json")
            : expandHome(`~/.openclaw-${profile}/config.json`);
          
          const config = readJsonSafe<{ gateway?: { port?: string }; port?: string } | null>(configPath, null);
          if (config) {
            const port = config.gateway?.port || config.port || "default";
            lines.push(`  Port: ${port}`);
          }
        }
      }
      
      // Check for systemd services (Linux only)
      if (os.platform() === "linux") {
        lines.push("");
        lines.push("SYSTEMD SERVICES");
        const systemdOut = safeExec("systemctl --user list-units 'openclaw*' --no-pager");
        if (systemdOut) {
          const services = systemdOut.split("\n")
            .filter(l => l.includes("openclaw"))
            .slice(0, 5);
          if (services.length > 0) {
            for (const svc of services) {
              lines.push(`- ${svc.trim()}`);
            }
          } else {
            lines.push("- (none)");
          }
        } else {
          lines.push("- (unable to check)");
        }
      }
      
      return { text: lines.join("\n") };
    },
  });

  // ========================================
  // /logs [service] [lines] - Unified Log Viewer
  // ========================================
  api.registerCommand({
    name: "logs",
    description: "View gateway or plugin logs (usage: /logs [service] [lines])",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (args: string) => {
      const parts = args.trim().split(/\s+/);
      const service = parts[0] || "gateway";
      const numLines = parseInt(parts[1] || "50");
      
      const lines: string[] = [];
      lines.push(`Logs: ${service} (last ${numLines} lines)`);
      lines.push("");
      
      const logDir = expandHome("~/.openclaw/logs");
      
      try {
        let targetLog: string | null = null;
        
        if (service === "gateway") {
          // Find latest gateway log
          const files = fs.readdirSync(logDir).filter((f: string) => f.startsWith("gateway")).sort();
          if (files.length > 0) {
            targetLog = path.join(logDir, files[files.length - 1]);
          }
        } else {
          // Find plugin log
          const files = fs.readdirSync(logDir).filter((f: string) => f.includes(service)).sort();
          if (files.length > 0) {
            targetLog = path.join(logDir, files[files.length - 1]);
          }
        }
        
        if (!targetLog || !fs.existsSync(targetLog)) {
          lines.push(`No log file found for: ${service}`);
          lines.push("");
          lines.push("Available logs:");
          const allLogs = fs.readdirSync(logDir);
          for (const log of allLogs.slice(-10)) {
            lines.push(`- ${log}`);
          }
        } else {
          const content = fs.readFileSync(targetLog, "utf-8");
          const logLines = content.split("\n").filter((l: string) => l.trim());
          const tail = logLines.slice(-numLines);
          
          lines.push(`File: ${path.basename(targetLog)}`);
          lines.push("```text");
          for (const line of tail) {
            lines.push(line);
          }
          lines.push("```");
        }
      } catch (e: any) {
        lines.push(`Error reading logs: ${e.message}`);
      }
      
      return { text: lines.join("\n") };
    },
  });

  // ========================================
  // /plugins - Enhanced Plugin Dashboard
  // ========================================
  api.registerCommand({
    name: "plugins",
    description: "Show detailed plugin dashboard (installed, status, versions)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const lines: string[] = [];
      lines.push("Plugins Dashboard");
      lines.push("");
      
      // Get plugin list
      const result = runCmd("openclaw", ["plugins", "list"], 15000);
      
      if (result.code !== 0) {
        lines.push("Failed to list plugins");
        lines.push("```text");
        lines.push(result.out);
        lines.push("```");
        return { text: lines.join("\n") };
      }
      
      // Parse plugin list
      const pluginLines = result.out.split("\n").filter(l => l.trim() && !l.startsWith("Installed"));
      
      lines.push(`INSTALLED (${pluginLines.length})`);
      
      // Try to get more details by checking workspace
      const pluginDetails: Array<{ name: string; version?: string; path?: string }> = [];
      
      for (const line of pluginLines) {
        const match = line.match(/^[\s-]*(.+?)(?:\s+\((.+?)\))?$/);
        if (match) {
          const name = match[1].trim();
          const info = match[2];
          pluginDetails.push({ name, version: info });
        }
      }
      
      // Enhanced details from workspace
      const dirs = listWorkspacePluginDirs(workspace);

      for (const plugin of pluginDetails) {
        const pluginDir = dirs.find((d: string) => d === plugin.name || d.endsWith(plugin.name));
        if (pluginDir) {
          const pkg = readJsonSafe<{ version?: string } | null>(path.join(workspace, pluginDir, "package.json"), null);
          if (pkg?.version) plugin.version = pkg.version;
          plugin.path = pluginDir;
        }
      }
      
      // Display formatted
      for (const plugin of pluginDetails) {
        let display = `- ${plugin.name}`;
        if (plugin.version) display += ` (v${plugin.version})`;
        lines.push(display);
        if (plugin.path) {
          lines.push(`  Path: ~/.openclaw/workspace/${plugin.path}`);
        }
      }
      
      if (pluginDetails.length === 0) {
        lines.push("- (none installed)");
      }
      
      // Check for available but not installed
      lines.push("");
      lines.push("AVAILABLE IN WORKSPACE");
      const installedNames = new Set(pluginDetails.map((p: any) => p.name));
      const available = dirs.filter((wp: string) => !installedNames.has(wp));

      if (available.length > 0) {
        for (const avail of available) {
          lines.push(`- ${avail} (not installed)`);
        }
      } else {
        lines.push("- (all workspace plugins installed)");
      }
      
      return { text: lines.join("\n") };
    },
  });
}
