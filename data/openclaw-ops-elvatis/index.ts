import path from "node:path";
import { registerPhase1Commands } from "./extensions/phase1-commands.js";
import { registerObserverCommands } from "./extensions/observer-commands.js";
import { registerSkillsCommands } from "./extensions/skills-commands.js";
import { registerConfigCommands } from "./extensions/config-commands.js";
import { registerLegacyCommands } from "./extensions/legacy-commands.js";
import { expandHome } from "./src/utils.js";

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as { enabled?: boolean; workspacePath?: string };
  if (cfg.enabled === false) return;

  const workspace = expandHome(cfg.workspacePath ?? "~/.openclaw/workspace");
  const cronDir = path.join(workspace, "cron");
  const cronScripts = path.join(cronDir, "scripts");
  const cronReports = path.join(cronDir, "reports");

  // Legacy commands (/cron, /privacy-scan, /release, /staging-smoke, /handoff, /limits)
  registerLegacyCommands(api, workspace, cronDir, cronScripts, cronReports);

  // Phase 1 operational commands (/health, /services, /logs, /plugins)
  registerPhase1Commands(api, workspace);

  // Session observer commands (/sessions, /activity, /session-tail, /session-stats, /session-clear)
  registerObserverCommands(api, workspace);

  // Skills & shortcuts commands (/skills, /shortcuts)
  registerSkillsCommands(api, workspace);

  // Config management commands (/config)
  registerConfigCommands(api, workspace);
}
