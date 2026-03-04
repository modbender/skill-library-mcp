import type { PluginRuntime } from "clawdbot/plugin-sdk";

let runtime: PluginRuntime | null = null;

export function setOneBotRuntime(next: PluginRuntime) {
  runtime = next;
}

export function getOneBotRuntime(): PluginRuntime {
  if (!runtime) {
    throw new Error("OneBot runtime not initialized");
  }
  return runtime;
}
