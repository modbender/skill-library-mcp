/**
 * 企业微信 Channel 插件入口
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";
import { wecomPlugin } from "./src/channel.js";
import { setWecomRuntime } from "./src/runtime.js";

export { monitorWecomProvider } from "./src/monitor.js";
export { sendMessageWecom } from "./src/send.js";
export { wecomPlugin } from "./src/channel.js";
export { getAccessToken, clearTokenCache, clearAllTokenCache } from "./src/token.js";

const plugin = {
  id: "wecom",
  name: "WeCom",
  description: "企业微信 (WeCom/WxWork) channel plugin",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    setWecomRuntime(api.runtime);
    api.registerChannel({ plugin: wecomPlugin });
  },
};

export default plugin;
