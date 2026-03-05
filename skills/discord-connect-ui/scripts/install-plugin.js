#!/usr/bin/env node
/**
 * Discord Connect Hub - Plugin Installation Script
 * 
 * Installs the Discord Connect UI and RPC handlers into Clawdbot.
 * 
 * Usage:
 *   node install-plugin.js [options]
 * 
 * Options:
 *   --gateway-path <path>   Path to Clawdbot gateway source
 *   --skip-build            Skip build step after installation
 *   --skip-restart          Skip gateway restart
 *   --dry-run               Show what would be done without making changes
 *   --uninstall             Remove the plugin
 *   --help                  Show this help
 */

import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const ASSETS_PATH = path.join(SKILL_ROOT, "assets");

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  gatewayPath: null,
  skipBuild: false,
  skipRestart: false,
  dryRun: false,
  uninstall: false,
  help: false,
};

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--gateway-path":
      options.gatewayPath = args[++i];
      break;
    case "--skip-build":
      options.skipBuild = true;
      break;
    case "--skip-restart":
      options.skipRestart = true;
      break;
    case "--dry-run":
      options.dryRun = true;
      break;
    case "--uninstall":
      options.uninstall = true;
      break;
    case "--help":
    case "-h":
      options.help = true;
      break;
  }
}

if (options.help) {
  console.log(`
Discord Connect Hub - Installation Script

Usage:
  node install-plugin.js [options]

Options:
  --gateway-path <path>   Path to Clawdbot gateway source (auto-detected if not set)
  --skip-build            Skip build step after installation
  --skip-restart          Skip gateway restart
  --dry-run               Show what would be done without making changes
  --uninstall             Remove the plugin
  --help, -h              Show this help

Examples:
  node install-plugin.js
  node install-plugin.js --gateway-path ~/clawdbot
  node install-plugin.js --dry-run
  node install-plugin.js --uninstall
`);
  process.exit(0);
}

// Find gateway path
function findGatewayPath() {
  if (options.gatewayPath) {
    if (fs.existsSync(path.join(options.gatewayPath, "src/gateway"))) {
      return options.gatewayPath;
    }
    throw new Error(`Invalid gateway path: ${options.gatewayPath}`);
  }

  const possiblePaths = [
    process.env.CLAWDBOT_PATH,
    path.join(process.env.HOME, "clawdbot"),
    path.join(process.env.HOME, "clawd/koda-desktop/gateway"),
    "/usr/local/lib/clawdbot",
  ].filter(Boolean);

  for (const p of possiblePaths) {
    if (fs.existsSync(path.join(p, "src/gateway"))) {
      return p;
    }
  }

  throw new Error(
    "Could not locate Clawdbot source directory.\n" +
    "Use --gateway-path or set CLAWDBOT_PATH environment variable."
  );
}

// Logging helpers
function log(msg) {
  console.log(msg);
}

function dryLog(msg) {
  if (options.dryRun) {
    console.log(`[DRY RUN] ${msg}`);
  }
}

// File operations with dry-run support
function copyFile(src, dest) {
  if (options.dryRun) {
    dryLog(`Would copy: ${src} -> ${dest}`);
    return;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
  log(`  ✅ Copied: ${path.basename(dest)}`);
}

function writeFile(filepath, content) {
  if (options.dryRun) {
    dryLog(`Would write: ${filepath}`);
    return;
  }
  fs.writeFileSync(filepath, content);
  log(`  ✅ Updated: ${path.basename(filepath)}`);
}

function removeFile(filepath) {
  if (options.dryRun) {
    dryLog(`Would remove: ${filepath}`);
    return;
  }
  if (fs.existsSync(filepath)) {
    fs.unlinkSync(filepath);
    log(`  🗑️  Removed: ${path.basename(filepath)}`);
  }
}

// Main installation
async function install() {
  log("🎮 Discord Connect Hub - Installation");
  log("");

  const gatewayPath = findGatewayPath();
  const uiPath = path.join(gatewayPath, "ui");

  log(`📁 Gateway path: ${gatewayPath}`);
  log(`📁 UI path: ${uiPath}`);
  log("");

  if (options.dryRun) {
    log("⚡ Dry run mode - no changes will be made");
    log("");
  }

  // 1. Install backend handlers
  log("📦 Installing backend handlers...");
  const backendSrc = path.join(ASSETS_PATH, "discord-backend.ts");
  const backendDest = path.join(gatewayPath, "src/gateway/server-methods/discord-connect.ts");
  copyFile(backendSrc, backendDest);

  // 2. Register handlers in server-methods.ts
  log("📝 Registering RPC handlers...");
  const serverMethodsPath = path.join(gatewayPath, "src/gateway/server-methods.ts");
  let serverMethods = fs.readFileSync(serverMethodsPath, "utf-8");

  if (!serverMethods.includes("discord-connect")) {
    // Add import at the top with other imports
    const importLine = 'import { registerDiscordConnectHandlers } from "./server-methods/discord-connect.js";';
    
    if (!serverMethods.includes(importLine)) {
      serverMethods = serverMethods.replace(
        /(import[^;]+from\s+["'][^"']*server-methods[^"']*["'];?\n)/,
        `$1${importLine}\n`
      );
    }

    // Add registration in the function
    if (!serverMethods.includes("registerDiscordConnectHandlers")) {
      serverMethods = serverMethods.replace(
        /(export\s+(?:async\s+)?function\s+registerServerMethods[^{]+{)/,
        "$1\n  registerDiscordConnectHandlers(registerMethod);"
      );
    }

    writeFile(serverMethodsPath, serverMethods);
  } else {
    log("  ⏭️  Already registered");
  }

  // 3. Install UI view
  log("📦 Installing UI components...");
  const viewSrc = path.join(ASSETS_PATH, "discord-views.ts");
  const viewDest = path.join(uiPath, "src/ui/views/discord.ts");
  copyFile(viewSrc, viewDest);

  // 4. Update navigation.ts
  log("📝 Updating navigation...");
  const navPath = path.join(uiPath, "src/ui/navigation.ts");
  let navContent = fs.readFileSync(navPath, "utf-8");

  if (!navContent.includes('"discord"') || !navContent.includes('"/discord"')) {
    // Add to Tab type
    navContent = navContent.replace(
      /export type Tab\s*=\s*\n([^;]+);/,
      (match, types) => {
        if (types.includes('"discord"')) return match;
        return match.replace(';', '\n  | "discord";');
      }
    );

    // Add to TAB_PATHS
    if (!navContent.includes('discord: "/discord"')) {
      navContent = navContent.replace(
        /(export const TAB_PATHS[^}]+)(};)/,
        '$1  discord: "/discord",\n$2'
      );
    }

    // Add to TAB_ICONS
    if (!navContent.includes('discord:') || !navContent.includes('🎮')) {
      navContent = navContent.replace(
        /(export const TAB_ICONS[^}]+)(};)/,
        '$1  discord: "🎮",\n$2'
      );
    }

    // Add to TAB_TITLES
    navContent = navContent.replace(
      /(export const TAB_TITLES[^}]+)(};)/,
      (match, content, end) => {
        if (content.includes('discord:')) return match;
        return `${content}  discord: "Discord",\n${end}`;
      }
    );

    // Add to TAB_SUBTITLES
    navContent = navContent.replace(
      /(export const TAB_SUBTITLES[^}]+)(};)/,
      (match, content, end) => {
        if (content.includes('discord:')) return match;
        return `${content}  discord: "Bot connection & servers",\n${end}`;
      }
    );

    // Add to channels group
    if (!navContent.includes('"discord"')) {
      navContent = navContent.replace(
        /(channels:\s*{\s*label:\s*"Channels",\s*tabs:\s*\[)([^\]]*)\]/,
        (match, prefix, tabs) => {
          if (tabs.includes('"discord"')) return match;
          const newTabs = tabs ? `"discord", ${tabs}` : '"discord"';
          return `${prefix}${newTabs}]`;
        }
      );
    }

    writeFile(navPath, navContent);
  } else {
    log("  ⏭️  Already configured");
  }

  // 5. Update app-render.ts
  log("📝 Updating render logic...");
  const renderPath = path.join(uiPath, "src/ui/app-render.ts");
  let renderContent = fs.readFileSync(renderPath, "utf-8");

  if (!renderContent.includes("discord-connect-view")) {
    // Add import
    const importLine = 'import "./views/discord.js";';
    if (!renderContent.includes(importLine)) {
      renderContent = renderContent.replace(
        /(import\s+["']\.\/views\/[^"']+["'];?\n)/,
        `$1${importLine}\n`
      );
    }

    // Add case statement
    const caseStatement = `      case "discord":
        return html\`<discord-connect-view></discord-connect-view>\`;`;
    
    if (!renderContent.includes('case "discord"')) {
      renderContent = renderContent.replace(
        /(switch\s*\(\s*(?:this\.)?(?:current)?[Tt]ab\s*\)\s*{)/,
        `$1\n${caseStatement}`
      );
    }

    writeFile(renderPath, renderContent);
  } else {
    log("  ⏭️  Already configured");
  }

  // 6. Build
  if (!options.skipBuild && !options.dryRun) {
    log("");
    log("🔨 Building...");
    try {
      execSync("pnpm build", { cwd: gatewayPath, stdio: "inherit" });
      execSync("pnpm ui:build", { cwd: gatewayPath, stdio: "inherit" });
      log("  ✅ Build complete");
    } catch (err) {
      log("  ⚠️  Build failed - run manually:");
      log(`     cd ${gatewayPath} && pnpm build && pnpm ui:build`);
    }
  }

  // 7. Restart gateway
  if (!options.skipRestart && !options.dryRun) {
    log("");
    log("🔄 Restarting gateway...");
    try {
      execSync("clawdbot gateway restart", { stdio: "inherit" });
      log("  ✅ Gateway restarted");
    } catch {
      log("  💡 Restart manually: clawdbot gateway restart");
    }
  }

  log("");
  log("✨ Installation complete!");
  log("");
  log("Next steps:");
  log("  1. Open Control Dashboard → Channels → Discord");
  log("  2. Enter your Discord bot token");
  log("  3. Click 'Save & Connect'");
}

// Uninstallation
async function uninstall() {
  log("🎮 Discord Connect Hub - Uninstallation");
  log("");

  const gatewayPath = findGatewayPath();
  const uiPath = path.join(gatewayPath, "ui");

  if (options.dryRun) {
    log("⚡ Dry run mode - no changes will be made");
    log("");
  }

  // Remove files
  log("🗑️  Removing files...");
  removeFile(path.join(gatewayPath, "src/gateway/server-methods/discord-connect.ts"));
  removeFile(path.join(uiPath, "src/ui/views/discord.ts"));

  // Note: We don't automatically remove patches from server-methods.ts,
  // navigation.ts, and app-render.ts as it's safer to do manually

  log("");
  log("⚠️  Manual cleanup required:");
  log("  1. Remove Discord import from src/gateway/server-methods.ts");
  log("  2. Remove Discord entries from ui/src/ui/navigation.ts");
  log("  3. Remove Discord case from ui/src/ui/app-render.ts");
  log("  4. Rebuild: pnpm build && pnpm ui:build");
  log("  5. Restart: clawdbot gateway restart");
}

// Run
try {
  if (options.uninstall) {
    await uninstall();
  } else {
    await install();
  }
} catch (err) {
  console.error("❌ Error:", err.message);
  process.exit(1);
}
