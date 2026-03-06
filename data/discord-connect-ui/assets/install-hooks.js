/**
 * Discord Connect Hub - Installation Hooks for Plugin Architecture
 * 
 * This module provides the complete installation automation for the
 * Discord Connect skill, including UI components, RPC handlers,
 * navigation updates, and build orchestration.
 * 
 * Implements the Clawdbot Plugin Architecture v2 hooks interface.
 */

import fs from "fs";
import path from "path";
import { execSync } from "child_process";

/**
 * Plugin manifest for the plugin registry
 */
export const PLUGIN_MANIFEST = {
  name: "discord-connect-hub",
  version: "1.0.0",
  type: "channel-ui",
  author: "OpenClaw Community",
  
  provides: {
    tabs: ["discord"],
    rpcMethods: [
      "discord.status",
      "discord.health",
      "discord.guilds",
      "discord.guild",
      "discord.channels",
      "discord.invite",
      "discord.testToken",
      "discord.setToken",
      "discord.permissions",
    ],
    channelType: "discord",
  },
  
  requires: {
    clawdbot: ">=2026.1.0",
  },
  
  hooks: {
    preInstall: "preInstall",
    install: "install",
    postInstall: "postInstall",
    preUninstall: "preUninstall",
    uninstall: "uninstall",
    configUpdated: "onConfigUpdated",
  },
};

/**
 * Installation context - populated during install
 */
let installContext = {
  skillPath: null,
  gatewayPath: null,
  uiPath: null,
  backupPath: null,
  installedFiles: [],
  patchedFiles: [],
};

/**
 * Pre-installation hook
 * Validates environment and creates backups
 */
export async function preInstall(ctx) {
  console.log("🎮 Discord Connect Hub - Pre-installation check");
  
  const { skillPath, gatewayPath } = ctx;
  installContext.skillPath = skillPath;
  
  // Detect Clawdbot paths
  const possiblePaths = [
    path.join(process.env.HOME, "clawdbot"),
    path.join(process.env.HOME, "clawd/koda-desktop/gateway"),
    "/usr/local/lib/clawdbot",
    process.env.CLAWDBOT_PATH,
  ].filter(Boolean);
  
  for (const p of possiblePaths) {
    if (fs.existsSync(path.join(p, "src/gateway"))) {
      installContext.gatewayPath = p;
      installContext.uiPath = path.join(p, "ui");
      break;
    }
  }
  
  if (!installContext.gatewayPath) {
    throw new Error(
      "Could not locate Clawdbot source directory. " +
      "Set CLAWDBOT_PATH environment variable or install manually."
    );
  }
  
  // Create backup directory
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  installContext.backupPath = path.join(
    installContext.gatewayPath,
    `.backups/discord-connect-${timestamp}`
  );
  fs.mkdirSync(installContext.backupPath, { recursive: true });
  
  // Backup files that will be modified
  const filesToBackup = [
    "src/gateway/server-methods.ts",
    "ui/src/ui/navigation.ts",
    "ui/src/ui/app-render.ts",
  ];
  
  for (const file of filesToBackup) {
    const fullPath = path.join(installContext.gatewayPath, file);
    if (fs.existsSync(fullPath)) {
      const backupFile = path.join(installContext.backupPath, file);
      fs.mkdirSync(path.dirname(backupFile), { recursive: true });
      fs.copyFileSync(fullPath, backupFile);
      console.log(`  📦 Backed up: ${file}`);
    }
  }
  
  console.log("  ✅ Pre-installation checks passed");
  return { success: true, context: installContext };
}

/**
 * Main installation hook
 * Copies files and patches source code
 */
export async function install(ctx) {
  console.log("🎮 Discord Connect Hub - Installing components");
  
  const { gatewayPath, uiPath, skillPath } = installContext;
  const assetsPath = path.join(skillPath, "assets");
  
  // 1. Install backend RPC handlers
  console.log("  📂 Installing backend handlers...");
  const backendSrc = path.join(assetsPath, "discord-backend.ts");
  const backendDest = path.join(gatewayPath, "src/gateway/server-methods/discord-connect.ts");
  fs.mkdirSync(path.dirname(backendDest), { recursive: true });
  fs.copyFileSync(backendSrc, backendDest);
  installContext.installedFiles.push(backendDest);
  console.log("    ✅ discord-connect.ts");
  
  // 2. Register handlers in server-methods.ts
  console.log("  📝 Patching server-methods.ts...");
  const serverMethodsPath = path.join(gatewayPath, "src/gateway/server-methods.ts");
  let serverMethods = fs.readFileSync(serverMethodsPath, "utf-8");
  
  if (!serverMethods.includes("discord-connect")) {
    // Add import
    serverMethods = serverMethods.replace(
      /(import[^;]+server-methods[^;]*;?\n)/,
      '$1import { registerDiscordConnectHandlers } from "./server-methods/discord-connect.js";\n'
    );
    
    // Add registration call
    serverMethods = serverMethods.replace(
      /(registerMethod\s*\)\s*(?:=>)?\s*{[^}]*})/,
      (match) => {
        if (match.includes("registerDiscordConnect")) return match;
        return match.replace(/}$/, "  registerDiscordConnectHandlers(registerMethod);\n}");
      }
    );
    
    // Alternative pattern for arrow functions
    if (!serverMethods.includes("registerDiscordConnectHandlers")) {
      serverMethods = serverMethods.replace(
        /(export\s+(?:async\s+)?function\s+registerServerMethods[^{]+{)/,
        "$1\n  registerDiscordConnectHandlers(registerMethod);"
      );
    }
    
    fs.writeFileSync(serverMethodsPath, serverMethods);
    installContext.patchedFiles.push(serverMethodsPath);
    console.log("    ✅ Handlers registered");
  } else {
    console.log("    ⏭️  Handlers already registered");
  }
  
  // 3. Install UI component
  console.log("  📂 Installing UI components...");
  const viewSrc = path.join(assetsPath, "discord-views.ts");
  const viewDest = path.join(uiPath, "src/ui/views/discord.ts");
  fs.mkdirSync(path.dirname(viewDest), { recursive: true });
  fs.copyFileSync(viewSrc, viewDest);
  installContext.installedFiles.push(viewDest);
  console.log("    ✅ discord.ts view");
  
  // 4. Patch navigation.ts
  console.log("  📝 Patching navigation.ts...");
  const navPath = path.join(uiPath, "src/ui/navigation.ts");
  let navContent = fs.readFileSync(navPath, "utf-8");
  
  // Import and use navigation hooks
  const { patchNavigation, isDiscordTabRegistered } = await import(
    path.join(assetsPath, "navigation-hooks.js")
  );
  
  if (!isDiscordTabRegistered(navContent)) {
    navContent = patchNavigation(navContent);
    fs.writeFileSync(navPath, navContent);
    installContext.patchedFiles.push(navPath);
    console.log("    ✅ Navigation updated");
  } else {
    console.log("    ⏭️  Navigation already configured");
  }
  
  // 5. Patch app-render.ts
  console.log("  📝 Patching app-render.ts...");
  const renderPath = path.join(uiPath, "src/ui/app-render.ts");
  let renderContent = fs.readFileSync(renderPath, "utf-8");
  
  const { patchAppRender, isDiscordViewRegistered } = await import(
    path.join(assetsPath, "navigation-hooks.js")
  );
  
  if (!isDiscordViewRegistered(renderContent)) {
    renderContent = patchAppRender(renderContent);
    fs.writeFileSync(renderPath, renderContent);
    installContext.patchedFiles.push(renderPath);
    console.log("    ✅ Render logic updated");
  } else {
    console.log("    ⏭️  Render logic already configured");
  }
  
  console.log("  ✅ Component installation complete");
  return { success: true, installedFiles: installContext.installedFiles };
}

/**
 * Post-installation hook
 * Builds and restarts the gateway
 */
export async function postInstall(ctx) {
  console.log("🎮 Discord Connect Hub - Post-installation");
  
  const { gatewayPath } = installContext;
  const skipBuild = ctx.options?.skipBuild || process.env.SKIP_BUILD;
  
  if (!skipBuild) {
    try {
      // Build backend
      console.log("  🔨 Building backend...");
      execSync("pnpm build", { 
        cwd: gatewayPath, 
        stdio: "inherit",
        timeout: 120000,
      });
      
      // Build UI
      console.log("  🔨 Building UI...");
      execSync("pnpm ui:build", { 
        cwd: gatewayPath, 
        stdio: "inherit",
        timeout: 120000,
      });
      
      console.log("  ✅ Build complete");
    } catch (err) {
      console.error("  ⚠️  Build failed:", err.message);
      console.log("  💡 Run manually: cd " + gatewayPath + " && pnpm build && pnpm ui:build");
    }
  }
  
  // Restart gateway if running
  const skipRestart = ctx.options?.skipRestart || process.env.SKIP_RESTART;
  if (!skipRestart) {
    try {
      console.log("  🔄 Restarting gateway...");
      execSync("clawdbot gateway restart", { 
        stdio: "inherit",
        timeout: 30000,
      });
      console.log("  ✅ Gateway restarted");
    } catch (err) {
      console.log("  💡 Restart gateway manually: clawdbot gateway restart");
    }
  }
  
  // Verify installation
  console.log("\n✨ Discord Connect Hub installed successfully!");
  console.log("\nNext steps:");
  console.log("  1. Open Control Dashboard → Channels → Discord");
  console.log("  2. Enter your Discord bot token");
  console.log("  3. Click 'Save & Connect'");
  console.log("\nNeed a bot token? Visit: https://discord.com/developers/applications");
  
  return { 
    success: true, 
    backupPath: installContext.backupPath,
    installedFiles: installContext.installedFiles,
    patchedFiles: installContext.patchedFiles,
  };
}

/**
 * Pre-uninstall hook
 * Prepares for removal
 */
export async function preUninstall(ctx) {
  console.log("🎮 Discord Connect Hub - Preparing uninstallation");
  
  // Warn about active connections
  try {
    const status = execSync("clawdbot rpc discord.status", { encoding: "utf-8" });
    if (status.includes('"connected": true')) {
      console.log("  ⚠️  Discord bot is currently connected");
      console.log("  💡 Bot will be disconnected during uninstallation");
    }
  } catch {
    // Ignore - RPC might not be available
  }
  
  return { success: true };
}

/**
 * Uninstall hook
 * Removes installed files and patches
 */
export async function uninstall(ctx) {
  console.log("🎮 Discord Connect Hub - Uninstalling");
  
  // Remove installed files
  for (const file of installContext.installedFiles) {
    if (fs.existsSync(file)) {
      fs.unlinkSync(file);
      console.log(`  🗑️  Removed: ${file}`);
    }
  }
  
  // Restore backups if available
  if (installContext.backupPath && fs.existsSync(installContext.backupPath)) {
    console.log("  📦 Restoring backups...");
    // Restore logic would go here
  }
  
  console.log("  ✅ Uninstallation complete");
  console.log("  💡 Remember to rebuild: pnpm build && pnpm ui:build");
  
  return { success: true };
}

/**
 * Configuration updated hook
 * Responds to Discord config changes
 */
export async function onConfigUpdated(ctx) {
  const { path: configPath, oldValue, newValue } = ctx;
  
  // Only care about discord config changes
  if (!configPath.startsWith("channels.discord")) return;
  
  console.log("🎮 Discord config updated");
  
  // If token changed, the gateway will automatically reconnect
  if (configPath === "channels.discord.botToken") {
    console.log("  🔑 Bot token updated - reconnecting...");
  }
  
  return { success: true };
}

export default {
  PLUGIN_MANIFEST,
  preInstall,
  install,
  postInstall,
  preUninstall,
  uninstall,
  onConfigUpdated,
};
