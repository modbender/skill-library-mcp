import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

export default function register(api: OpenClawPluginApi) {
  const cfg = api.pluginConfig as { prependText?: string; enabled?: boolean } | undefined;
  const enabled = cfg?.enabled !== false;
  const prependText = cfg?.prependText || "";

  if (!enabled || !prependText) {
    api.logger.info("message-injector: disabled or no prependText configured.");
    return;
  }

  api.logger.info("message-injector: active.");

  api.on("before_agent_start", async (event) => {
    if (!event.prompt || event.prompt.length < 1) return;
    return { prependContext: prependText };
  });
}
