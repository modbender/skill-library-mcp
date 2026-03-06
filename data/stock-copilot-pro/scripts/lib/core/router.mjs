import { briefCommand } from "./commands/brief.mjs";
import { radarCommand } from "./commands/radar.mjs";
import { watchCommand } from "./commands/watch.mjs";

export const COMMANDS = {
  brief: { handler: briefCommand, description: "早晚报生成" },
  radar: { handler: radarCommand, description: "行业热点追踪" },
  watch: { handler: watchCommand, description: "自选股管理" },
};

export function hasCommand(command) {
  return Boolean(COMMANDS[String(command || "").toLowerCase()]);
}

export async function dispatchCommand(command, args = {}, context = {}) {
  const key = String(command || "").toLowerCase();
  const cmd = COMMANDS[key];
  if (!cmd) {
    throw new Error(`Unknown routed command: ${command}`);
  }
  return cmd.handler(args, context);
}
