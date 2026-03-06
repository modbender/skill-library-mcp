/**
 * OpenClaw plugin entry point.
 *
 * OpenClaw expects a default export with `register(api)` where tools are
 * registered via `api.registerTool({ name, description, parameters, execute })`.
 * Parameters must use TypeBox schemas (@sinclair/typebox), not Zod.
 *
 * This file wraps the core library functions into the OpenClaw plugin interface.
 */
import { Type, type TSchema } from "@sinclair/typebox";
import { configureHashBox, loadConfig, refreshCustomToken } from "./setupHashBox.js";
import { sendHashBoxNotification } from "./pushToHashBox.js";
import { initFirebaseClient, resetFirebaseClient } from "./firebaseClient.js";
import { startCommandListener } from "./commandListener.js";
import type { Unsubscribe } from "firebase/firestore";

let unsubscribe: Unsubscribe | null = null;

interface OpenClawApi {
  registerTool(tool: {
    name: string;
    description: string;
    parameters: TSchema;
    execute: (toolCallId: string, params: Record<string, unknown>) => Promise<unknown>;
  }): void;
}

const plugin = {
  id: "hashbox-plugin",
  name: "HashBox",
  description:
    "Connects an AI agent to the HashBox iOS app via Firebase webhook for push notifications",

  register(api: OpenClawApi) {
    api.registerTool({
      name: "configure_hashbox",
      description: "Configure HashBox with an API token (must start with HB-)",
      parameters: Type.Object({
        token: Type.String({ description: "HashBox API token (must start with HB-)" }),
      }),
      async execute(_toolCallId: string, params: Record<string, unknown>) {
        const result = await configureHashBox(params.token as string);
        return {
          content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result, null, 2) }],
          details: result,
        };
      },
    });

    api.registerTool({
      name: "send_hashbox_notification",
      description: "Send a push notification to the HashBox iOS app",
      parameters: Type.Object({
        payloadType: Type.Unsafe<"article" | "metric" | "audit">({
          type: "string",
          enum: ["article", "metric", "audit"],
          description: "Type of notification payload",
        }),
        channelName: Type.String({ description: "Name of the notification channel" }),
        channelIcon: Type.String({ description: "Icon/emoji for the channel" }),
        title: Type.String({ description: "Notification title" }),
        contentOrData: Type.Unsafe<string | unknown[]>({
          anyOf: [
            { type: "string" },
            { type: "array", items: {} },
          ],
          description:
            "Content body (string for article) or structured data (array for metric/audit)",
        }),
      }),
      async execute(_toolCallId: string, params: Record<string, unknown>) {
        const contentOrData = params.contentOrData as
          | string
          | import("./types.js").MetricItem[]
          | import("./types.js").AuditFinding[];
        const result = await sendHashBoxNotification(
          params.payloadType as "article" | "metric" | "audit",
          params.channelName as string,
          params.channelIcon as string,
          params.title as string,
          contentOrData,
        );
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          details: result,
        };
      },
    });

    // Start the command listener if already configured
    initializeListener().catch(() => {
      // Silently fail — plugin works in output-only mode if not configured
    });
  },
};

async function initializeListener(): Promise<void> {
  const config = await loadConfig();
  if (!config?.customToken || !config?.userId) return;

  try {
    await initFirebaseClient(config.customToken);
  } catch {
    try {
      const refreshed = await refreshCustomToken(config);
      if (!refreshed.customToken) return;
      await initFirebaseClient(refreshed.customToken);
    } catch {
      return;
    }
  }

  const { getDb } = await import("./firebaseClient.js");
  const db = getDb();

  unsubscribe = startCommandListener(db, config.userId, async (command) => {
    // The command listener will log; actual injection depends on OpenClaw's
    // runtime API which we'll map when integrated
    console.log(
      `[HashBox] Received command: ${command.commandType} — ${command.payload.raw_instruction}`,
    );
  });
}

// Cleanup on process exit
process.on("beforeExit", () => {
  if (unsubscribe) {
    unsubscribe();
    unsubscribe = null;
  }
  resetFirebaseClient();
});

export default plugin;
