/**
 * Clawfinger OpenClaw plugin entry point.
 *
 * Registers a background WS bridge service, LLM-callable tools for
 * call control/observation, and a /clawfinger slash command.
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { Type } from "@sinclair/typebox";
import { GatewayClient } from "./gateway-client.js";
import { WsBridge } from "./ws-bridge.js";

export default function register(api: OpenClawPluginApi) {
  const cfg = api.pluginConfig as
    | { gatewayUrl?: string; bearerToken?: string }
    | undefined;
  const gatewayUrl = cfg?.gatewayUrl || "http://127.0.0.1:8996";
  const bearerToken = cfg?.bearerToken || "";

  const client = new GatewayClient(gatewayUrl, bearerToken);
  const bridge = new WsBridge(gatewayUrl, api.logger);

  // --- Background service: persistent WS bridge ---

  api.registerService({
    id: "clawfinger-bridge",
    start: async () => {
      await bridge.connect();
      api.logger.info(`Clawfinger bridge connected to ${gatewayUrl}`);
    },
    stop: async () => {
      await bridge.disconnect();
      api.logger.info("Clawfinger bridge disconnected");
    },
  });

  // --- Tools (available to LLM agents) ---

  api.registerTool({
    name: "clawfinger_status",
    label: "Clawfinger Status",
    description:
      "Check Clawfinger gateway health, active sessions, and bridge connection status.",
    parameters: Type.Object({}),
    async execute() {
      const status = await client.status();
      return {
        content: [{ type: "text", text: JSON.stringify(status) }],
        details: status,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_sessions",
    label: "Clawfinger Sessions",
    description: "List active call sessions on the Clawfinger gateway.",
    parameters: Type.Object({}),
    async execute() {
      const sessions = await client.getSessions();
      return {
        content: [{ type: "text", text: JSON.stringify(sessions) }],
        details: { sessions },
      };
    },
  });

  api.registerTool({
    name: "clawfinger_call_state",
    label: "Clawfinger Call State",
    description:
      "Get full call state for a session: conversation history, instructions, takeover status.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID" }),
    }),
    async execute(_id: string, params: { session_id: string }) {
      const state = await client.getCallState(params.session_id);
      return {
        content: [{ type: "text", text: JSON.stringify(state) }],
        details: state,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_dial",
    label: "Clawfinger Dial",
    description:
      "Dial an outbound phone call. The phone must be connected via ADB.",
    parameters: Type.Object({
      number: Type.String({
        description: "Phone number to dial (e.g., +49123456789)",
      }),
    }),
    async execute(_id: string, params: { number: string }) {
      const result = await client.dial(params.number);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_hangup",
    label: "Clawfinger Hangup",
    description:
      "Force hang up the active phone call via ADB and end the gateway session.",
    parameters: Type.Object({
      session_id: Type.Optional(
        Type.String({
          description:
            "Session ID to end (optional — auto-detects if only one active)",
        }),
      ),
    }),
    async execute(
      _id: string,
      params: { session_id?: string },
    ) {
      const result = await client.hangup(params.session_id);
      return {
        content: [
          {
            type: "text",
            text: result.ok
              ? "Call hung up."
              : `Hangup failed: ${JSON.stringify(result)}`,
          },
        ],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_inject",
    label: "Clawfinger Inject TTS",
    description:
      "Inject a TTS message into the active call. The text is synthesized and played to the caller.",
    parameters: Type.Object({
      text: Type.String({ description: "Text to synthesize and play" }),
      session_id: Type.Optional(
        Type.String({ description: "Session ID (optional)" }),
      ),
    }),
    async execute(
      _id: string,
      params: { text: string; session_id?: string },
    ) {
      const result = await client.inject(params.text, params.session_id);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_takeover",
    label: "Clawfinger Takeover",
    description:
      "Take over LLM control for a call session. After takeover, use clawfinger_turn_wait to receive caller transcripts, then clawfinger_turn_reply to respond. Call clawfinger_release when done.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID to take over" }),
    }),
    async execute(_id: string, params: { session_id: string }) {
      const ok = await bridge.takeover(params.session_id);
      return {
        content: [
          { type: "text", text: ok ? "Takeover active. Use clawfinger_turn_wait to receive the next caller turn." : "Takeover failed." },
        ],
        details: { ok },
      };
    },
  });

  api.registerTool({
    name: "clawfinger_turn_wait",
    label: "Clawfinger Wait for Turn",
    description:
      "Wait for the next caller turn during takeover. Returns the caller's transcript and a request_id. You MUST then call clawfinger_turn_reply with that request_id and your response text. Times out after 30 seconds if no turn arrives.",
    parameters: Type.Object({
      timeout_ms: Type.Optional(
        Type.Number({ description: "Timeout in ms (default: 30000)", default: 30000 }),
      ),
    }),
    async execute(_id: string, params: { timeout_ms?: number }) {
      const turn = await bridge.popTurnRequest(params.timeout_ms || 30000);
      if (!turn) {
        return {
          content: [
            { type: "text", text: "No turn arrived within timeout. The caller may have hung up or is still speaking. You can call clawfinger_turn_wait again to keep waiting, or clawfinger_release to hand back control." },
          ],
        };
      }
      return {
        content: [
          { type: "text", text: `Caller said: "${turn.transcript}"\n\nrequest_id: ${turn.request_id}\n\nYou MUST now call clawfinger_turn_reply with this request_id and your response.` },
        ],
        details: turn,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_turn_reply",
    label: "Clawfinger Turn Reply",
    description:
      "Send your reply to the caller and wait for their next turn. Returns the next caller transcript + request_id (same as turn_wait). If no next turn arrives within 45s, returns a timeout notice. Call this in a loop for multi-turn conversations.",
    parameters: Type.Object({
      request_id: Type.String({ description: "The request_id from clawfinger_turn_wait or previous turn_reply" }),
      reply: Type.String({ description: "Your response text (will be spoken to the caller via TTS)" }),
    }),
    async execute(_id: string, params: { request_id: string; reply: string }) {
      bridge.sendTurnReply(params.request_id, params.reply);

      // Immediately start waiting for the next turn — eliminates the
      // LLM think-time gap between turn_reply and the next turn_wait
      const next = await bridge.popTurnRequest(45_000);
      if (!next) {
        return {
          content: [
            { type: "text", text: `Reply sent: "${params.reply}"\n\nNo next turn arrived within 45s. The caller may have hung up. Call clawfinger_turn_wait to keep waiting, or clawfinger_release to hand back control.` },
          ],
        };
      }
      return {
        content: [
          { type: "text", text: `Reply sent: "${params.reply}"\n\nNext turn — Caller said: "${next.transcript}"\n\nrequest_id: ${next.request_id}\n\nCall clawfinger_turn_reply again with this request_id and your response.` },
        ],
        details: next,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_release",
    label: "Clawfinger Release",
    description:
      "Release LLM control for a call session back to the local gateway LLM.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID to release" }),
    }),
    async execute(_id: string, params: { session_id: string }) {
      const ok = await bridge.release(params.session_id);
      return {
        content: [
          { type: "text", text: ok ? "Released." : "Release failed." },
        ],
        details: { ok },
      };
    },
  });

  api.registerTool({
    name: "clawfinger_context_set",
    label: "Clawfinger Set Context",
    description:
      "Inject knowledge into a call session. The LLM sees this as context before each user turn. Replaces any existing context.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID" }),
      context: Type.String({ description: "Knowledge text to inject" }),
    }),
    async execute(
      _id: string,
      params: { session_id: string; context: string },
    ) {
      const result = await client.setContext(
        params.session_id,
        params.context,
      );
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_context_clear",
    label: "Clawfinger Clear Context",
    description: "Clear injected knowledge from a call session.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID" }),
    }),
    async execute(_id: string, params: { session_id: string }) {
      const result = await client.clearContext(params.session_id);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_call_config_get",
    label: "Clawfinger Get Call Config",
    description:
      "Read current call policy settings: auto-answer, greetings, caller filtering, max duration, auth.",
    parameters: Type.Object({}),
    async execute() {
      const config = await client.getCallConfig();
      return {
        content: [{ type: "text", text: JSON.stringify(config) }],
        details: config,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_call_config_set",
    label: "Clawfinger Set Call Config",
    description:
      "Update call policy settings. Pass only the fields you want to change.",
    parameters: Type.Object({
      config: Type.Record(Type.String(), Type.Unknown(), {
        description: "Config fields to update",
      }),
    }),
    async execute(
      _id: string,
      params: { config: Record<string, unknown> },
    ) {
      const result = await client.setCallConfig(params.config);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_session_end",
    label: "Clawfinger End Session",
    description:
      "Mark a call session as ended (hung up). Moves it from active to ended state.",
    parameters: Type.Object({
      session_id: Type.String({ description: "Session ID to end" }),
    }),
    async execute(_id: string, params: { session_id: string }) {
      const result = await client.endSession(params.session_id);
      return {
        content: [
          {
            type: "text",
            text: result.ok
              ? `Session ${params.session_id} ended.`
              : `Failed to end session: ${JSON.stringify(result)}`,
          },
        ],
        details: result,
      };
    },
  });

  api.registerTool({
    name: "clawfinger_instructions_set",
    label: "Clawfinger Set Instructions",
    description:
      "Set the LLM system instructions. Scope: 'global' (all sessions), 'session' (one session), or 'turn' (consumed after one turn).",
    parameters: Type.Object({
      text: Type.String({ description: "Instruction text" }),
      scope: Type.Optional(
        Type.Union(
          [
            Type.Literal("global"),
            Type.Literal("session"),
            Type.Literal("turn"),
          ],
          {
            description: "Scope: session or turn (default: session). Global scope is disabled.",
            default: "session",
          },
        ),
      ),
      session_id: Type.Optional(
        Type.String({
          description: "Session ID (required for session/turn scope)",
        }),
      ),
    }),
    async execute(
      _id: string,
      params: { text: string; scope?: string; session_id?: string },
    ) {
      const scope = params.scope === "turn" ? "turn" : "session";
      if (!params.session_id) {
        return {
          content: [{ type: "text", text: "Error: session_id is required." }],
          details: { ok: false },
        };
      }
      bridge.sendRaw({
        type: "set_instructions",
        instructions: params.text,
        scope,
        session_id: params.session_id,
      });
      return {
        content: [{ type: "text", text: "Instructions set." }],
        details: { ok: true },
      };
    },
  });

  // --- Slash command ---

  const HELP_TEXT = [
    "Clawfinger commands:",
    "",
    "/clawfinger                                  — this help",
    "/clawfinger status                           — gateway health, bridge, sessions, uptime",
    "/clawfinger sessions                         — list active session IDs",
    "/clawfinger state <session_id>               — full call state (history, instructions, takeover)",
    "/clawfinger dial <number>                    — dial outbound call (e.g. +49123456789)",
    "/clawfinger hangup [session_id]              — force hang up the active call",
    "/clawfinger inject <text>                    — inject TTS into active call (first session)",
    "/clawfinger inject <session_id> <text>       — inject TTS into specific session",
    "/clawfinger takeover <session_id>            — take over LLM control for a session",
    "/clawfinger release <session_id>             — release LLM control back to local LLM",
    "/clawfinger context get <session_id>         — read injected knowledge",
    "/clawfinger context set <session_id> <text>  — inject/replace knowledge",
    "/clawfinger context clear <session_id>       — clear injected knowledge",
    "/clawfinger config call                      — show call policy settings",
    "/clawfinger config tts                       — show TTS voice and speed",
    "/clawfinger config llm                       — show LLM model and params",
    "/clawfinger instructions <text>              — set global LLM instructions",
    "/clawfinger instructions <session_id> <text> — set per-session instructions",
    "/clawfinger end <session_id>                 — mark a session as ended (hung up)",
  ].join("\n");

  api.registerCommand({
    name: "clawfinger",
    description: "Clawfinger gateway control — status, dial, inject, takeover, context, config.",
    acceptsArgs: true,
    handler: async (ctx: { args?: string }) => {
      const args = ctx.args?.trim() || "";
      const tokens = args.split(/\s+/).filter(Boolean);
      const action = (tokens[0] || "help").toLowerCase();

      try {
        // --- status ---
        if (action === "status") {
          const s = await client.status();
          const bridgeOk = bridge.isConnected ? "connected" : "disconnected";
          const agents = s.agents?.length || 0;
          const takenOver = bridge.takenOverSessions.size;
          return {
            text: [
              `Gateway: ${s.mlx_audio?.ok ? "healthy" : "degraded"}`,
              `Bridge: ${bridgeOk}`,
              `Sessions: ${s.active_sessions || 0}`,
              `Agents: ${agents}`,
              `Takeovers: ${takenOver}`,
              `Uptime: ${Math.floor((s.uptime_s || 0) / 60)}m`,
              `LLM: ${s.llm?.model || "unknown"} (${s.llm?.loaded ? "loaded" : "not loaded"})`,
            ].join("\n"),
          };
        }

        // --- sessions ---
        if (action === "sessions") {
          const sessions = await client.getSessions();
          if (!sessions.length) return { text: "No active sessions." };
          return { text: `Active sessions (${sessions.length}):\n${sessions.map((s: string) => `  ${s}`).join("\n")}` };
        }

        // --- state <session_id> ---
        if (action === "state") {
          if (!tokens[1]) return { text: "Usage: /clawfinger state <session_id>" };
          const state = await client.getCallState(tokens[1]);
          const lines = [
            `Session: ${state.session_id}`,
            `Turns: ${state.turn_count}`,
            `Takeover: ${state.agent_takeover ? "yes" : "no"}`,
          ];
          if (state.history?.length) {
            lines.push("", "Recent:");
            for (const msg of state.history.slice(-4)) {
              const preview = String(msg.content || "").slice(0, 80);
              lines.push(`  ${msg.role}: ${preview}`);
            }
          }
          return { text: lines.join("\n") };
        }

        // --- dial <number> ---
        if (action === "dial") {
          if (!tokens[1]) return { text: "Usage: /clawfinger dial <number>" };
          const result = await client.dial(tokens[1]);
          return { text: result.ok ? `Dialing ${tokens[1]}...` : `Dial failed: ${result.detail}` };
        }

        // --- hangup [session_id] ---
        if (action === "hangup") {
          const result = await client.hangup(tokens[1]);
          return { text: result.ok ? `Call hung up.${result.session_id ? ` Session: ${result.session_id}` : ''}` : `Hangup failed: ${JSON.stringify(result)}` };
        }

        // --- inject [session_id] <text> ---
        if (action === "inject") {
          if (!tokens[1]) return { text: "Usage: /clawfinger inject <text>  or  /clawfinger inject <session_id> <text>" };
          // If first arg looks like a session ID (hex, 20+ chars) and there's more text, use it as session_id
          let sid: string | undefined;
          let text: string;
          if (tokens[1].length >= 20 && /^[a-f0-9]+$/i.test(tokens[1]) && tokens[2]) {
            sid = tokens[1];
            text = tokens.slice(2).join(" ");
          } else {
            text = tokens.slice(1).join(" ");
          }
          const result = await client.inject(text, sid);
          return { text: result.ok ? `Injected: "${text}"` : `Inject failed: ${JSON.stringify(result)}` };
        }

        // --- takeover <session_id> ---
        if (action === "takeover") {
          if (!tokens[1]) return { text: "Usage: /clawfinger takeover <session_id>" };
          const ok = await bridge.takeover(tokens[1]);
          return { text: ok ? `Takeover active for ${tokens[1]}` : `Takeover failed for ${tokens[1]}` };
        }

        // --- release <session_id> ---
        if (action === "release") {
          if (!tokens[1]) return { text: "Usage: /clawfinger release <session_id>" };
          const ok = await bridge.release(tokens[1]);
          return { text: ok ? `Released ${tokens[1]}` : `Release failed for ${tokens[1]}` };
        }

        // --- end <session_id> ---
        if (action === "end") {
          if (!tokens[1]) return { text: "Usage: /clawfinger end <session_id>" };
          const result = await client.endSession(tokens[1]);
          return { text: result.ok ? `Session ${tokens[1]} ended.` : `End failed: ${JSON.stringify(result)}` };
        }

        // --- context get|set|clear <session_id> [text] ---
        if (action === "context") {
          const sub = (tokens[1] || "").toLowerCase();
          const sid = tokens[2] || "";

          if (sub === "get" && sid) {
            const ctx = await client.getContext(sid);
            return { text: ctx.has_knowledge ? `Context for ${sid}:\n${ctx.knowledge}` : `No context for ${sid}.` };
          }
          if (sub === "set" && sid && tokens[3]) {
            const text = tokens.slice(3).join(" ");
            await client.setContext(sid, text);
            return { text: `Context set for ${sid}.` };
          }
          if (sub === "clear" && sid) {
            await client.clearContext(sid);
            return { text: `Context cleared for ${sid}.` };
          }
          return { text: "Usage:\n  /clawfinger context get <session_id>\n  /clawfinger context set <session_id> <text>\n  /clawfinger context clear <session_id>" };
        }

        // --- config call|tts|llm ---
        if (action === "config") {
          const sub = (tokens[1] || "call").toLowerCase();
          if (sub === "call") {
            const cfg = await client.getCallConfig();
            return { text: JSON.stringify(cfg, null, 2) };
          }
          if (sub === "tts") {
            const cfg = await client.getTtsConfig();
            return { text: JSON.stringify(cfg, null, 2) };
          }
          if (sub === "llm") {
            const cfg = await client.getLlmConfig();
            return { text: JSON.stringify(cfg, null, 2) };
          }
          return { text: "Usage: /clawfinger config call|tts|llm" };
        }

        // --- instructions <session_id> <text> ---
        if (action === "instructions") {
          if (!tokens[1] || !tokens[2]) return { text: "Usage: /clawfinger instructions <session_id> <text>" };
          const sid = tokens[1];
          const text = tokens.slice(2).join(" ");
          bridge.sendRaw({ type: "set_instructions", instructions: text, scope: "session", session_id: sid });
          return { text: `Instructions set for session ${sid}.` };
        }

        // --- help (default) ---
        return { text: HELP_TEXT };

      } catch (e) {
        return { text: `Error: ${e}` };
      }
    },
  });
}
