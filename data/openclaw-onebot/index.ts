import type { MoltbotPluginApi } from "clawdbot/plugin-sdk";
import { onebotPlugin } from "./src/channel.js";
import { setOneBotRuntime } from "./src/runtime.js";

const plugin = {
  id: "onebot",
  name: "OneBot",
  description: "OneBot 11 channel plugin (NapCat/go-cqhttp)",
  register(api: MoltbotPluginApi) {
    setOneBotRuntime(api.runtime);
    api.registerChannel({ plugin: onebotPlugin });
  },
};

export default plugin;

export { onebotPlugin } from "./src/channel.js";
export { setOneBotRuntime, getOneBotRuntime } from "./src/runtime.js";
export * from "./src/types.js";
export * from "./src/config.js";
export * from "./src/gateway.js";
export * from "./src/outbound.js";
