/**
 * 1Password UI - Plugin Registration
 * 
 * Registers the 1Password UI tab using the plugin architecture.
 * 
 * Add this to your plugin's register() function, or create a new plugin.
 * 
 * Example: src/plugins/builtin/1password-ui.ts
 */

import type { ClawdbotPluginApi } from "../../plugins/types.js";

export function register1PasswordUI(api: ClawdbotPluginApi): void {
  // Only register if the API supports UI views
  if (typeof api.registerView !== "function") {
    console.warn("[1password-ui] Plugin architecture not installed - UI view not registered");
    return;
  }

  // Register the 1Password tab under Tools group
  api.registerView({
    id: "1password",
    label: "1Password",
    subtitle: "Manage secrets and credential mappings",
    icon: "key", // or use a custom icon
    group: "Tools",
    position: 10, // After other tool tabs
  });

  console.log("[1password-ui] Registered 1Password UI view");
}

/**
 * Standalone plugin definition (if not adding to existing plugin)
 */
export const onePasswordUIPlugin = {
  id: "1password-ui",
  name: "1Password UI",
  version: "1.0.0",
  description: "1Password integration for OpenClaw Control UI",
  
  register(api: ClawdbotPluginApi): void {
    register1PasswordUI(api);
  },
};
