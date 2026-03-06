import type { HashBoxPlugin, PluginContext } from "./types.js";
import { configureHashBox, loadConfig, refreshCustomToken } from "./setupHashBox.js";
import { sendHashBoxNotification } from "./pushToHashBox.js";
import { initFirebaseClient, resetFirebaseClient } from "./firebaseClient.js";
import { startCommandListener } from "./commandListener.js";
import type { Unsubscribe } from "firebase/firestore";

export { configureHashBox, loadConfig, refreshCustomToken } from "./setupHashBox.js";
export { sendHashBoxNotification } from "./pushToHashBox.js";
export { initFirebaseClient, reauthenticate, getDb, resetFirebaseClient } from "./firebaseClient.js";
export { startCommandListener } from "./commandListener.js";
export type {
  ArticlePayload,
  MetricItem,
  MetricPayload,
  AuditFinding,
  AuditPayload,
  Channel,
  HashBoxRequest,
  AgentCommand,
  CommandHandler,
  PluginContext,
  PluginTool,
  PluginAction,
  HashBoxPlugin,
} from "./types.js";

let unsubscribe: Unsubscribe | null = null;

export const hashBoxPlugin: HashBoxPlugin = {
  name: "hashbox-plugin",
  description:
    "Connects an AI agent to the HashBox iOS app via Firebase webhook for push notifications and real-time command listening",
  tools: [
    {
      name: "configure_hashbox",
      description: "Configure HashBox with an API token (must start with HB-)",
      execute: async (...args: unknown[]) => {
        const token = args[0] as string;
        return configureHashBox(token);
      },
    },
  ],
  actions: [
    {
      name: "send_hashbox_notification",
      description: "Send a push notification to the HashBox iOS app",
      execute: async (...args: unknown[]) => {
        const [payloadType, channelName, channelIcon, title, contentOrData] =
          args as Parameters<typeof sendHashBoxNotification>;
        return sendHashBoxNotification(
          payloadType, channelName, channelIcon, title, contentOrData,
        );
      },
    },
  ],

  /**
   * Lifecycle: Initialize command listener.
   *
   * 1. Reads hashbox_config.json for token, customToken, userId
   * 2. If customToken + userId exist, authenticates with Firebase Client SDK
   * 3. Starts onSnapshot listener on agent_commands collection
   * 4. Injects incoming commands into the Agent's reasoning loop
   *
   * If customToken is expired, automatically refreshes via exchangeToken.
   * If no config or no customToken, silently skips (backward compatible).
   */
  initialize: async (context: PluginContext) => {
    const config = await loadConfig();
    if (!config?.customToken || !config?.userId) {
      // No custom token yet — plugin works in output-only mode
      return;
    }

    try {
      await initFirebaseClient(config.customToken);
    } catch {
      // Custom Token likely expired — refresh and retry
      try {
        const refreshed = await refreshCustomToken(config);
        if (!refreshed.customToken) return;
        await initFirebaseClient(refreshed.customToken);
      } catch {
        // Exchange also failed — skip listener, output-only mode
        return;
      }
    }

    const { getDb } = await import("./firebaseClient.js");
    const db = getDb();

    unsubscribe = startCommandListener(db, config.userId, async (command) => {
      const message = `User command from HashBox App: ${command.payload.raw_instruction}`;
      await context.injectMessage(message);
    });
  },

  /**
   * Lifecycle: Cleanup — unsubscribe Firestore listener and reset Firebase.
   */
  destroy: async () => {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = null;
    }
    resetFirebaseClient();
  },
};
