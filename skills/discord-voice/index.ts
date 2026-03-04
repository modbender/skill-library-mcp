/**
 * Discord Voice Plugin for OpenClaw
 *
 * Enables real-time voice conversations in Discord voice channels.
 *
 * Features:
 * - Join/leave voice channels via slash commands (/discord_voice join, /discord_voice leave)
 * - Listen to user speech with VAD (Voice Activity Detection)
 * - Speech-to-text via Whisper API or Deepgram
 * - Routes transcribed text through OpenClaw agent
 * - Text-to-speech via OpenAI or ElevenLabs
 * - Plays audio responses back to the voice channel
 */

import crypto from "node:crypto";
import { Type } from "@sinclair/typebox";
import { Client, GatewayIntentBits, type VoiceBasedChannel } from "discord.js";

import { parseConfig, getAvailableModels, DEFAULT_NO_EMOJI_HINT, sanitizeNoEmojiHint, type DiscordVoiceConfig } from "./src/config.js";
import { VoiceConnectionManager } from "./src/voice-connection.js";
import { loadCoreAgentDeps, type CoreConfig } from "./src/core-bridge.js";

interface PluginApi {
  pluginConfig: unknown;
  config: unknown;
  logger: {
    info(msg: string): void;
    warn(msg: string): void;
    error(msg: string): void;
    debug?(msg: string): void;
  };
  runtime: {
    discord?: {
      getClient(accountId?: string): Client | null;
    };
    agent?: {
      chat(params: {
        sessionKey: string;
        message: string;
        channel?: string;
        senderId?: string;
      }): Promise<{ text: string }>;
    };
  };
  registerGatewayMethod(
    name: string,
    handler: (ctx: { params: unknown; respond: (ok: boolean, payload?: unknown) => void }) => void | Promise<void>,
  ): void;
  registerTool(tool: {
    name: string;
    label: string;
    description: string;
    parameters: unknown;
    execute: (
      toolCallId: string,
      params: unknown,
    ) => Promise<{
      content: Array<{ type: string; text: string }>;
      details?: unknown;
    }>;
  }): void;
  registerService(service: { id: string; start: () => Promise<void> | void; stop: () => Promise<void> | void }): void;
  registerCli(register: (ctx: { program: unknown }) => void, opts?: { commands: string[] }): void;
}

/** Maximum characters for TTS input to prevent abuse and runaway API costs */
const MAX_TTS_TEXT_LENGTH = 4000;

/** Discord snowflake IDs are numeric strings (17–20 digits) */
const DISCORD_SNOWFLAKE_RE = /^\d{17,20}$/;

const VoiceToolSchema = Type.Union([
  Type.Object({
    action: Type.Literal("join"),
    channelId: Type.String({ description: "Voice channel ID to join" }),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional if in guild context)" })),
  }),
  Type.Object({
    action: Type.Literal("leave"),
    guildId: Type.Optional(Type.String({ description: "Guild ID to leave voice in (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("speak"),
    text: Type.String({ description: "Text to speak in the voice channel" }),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("status"),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("reset-fallback"),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("set-stt"),
    provider: Type.String({
      description:
        "STT provider: whisper, gpt4o-mini, gpt4o-transcribe, gpt4o-transcribe-diarize, deepgram, local-whisper, wyoming-whisper",
    }),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("set-tts"),
    provider: Type.String({ description: "TTS provider: openai, elevenlabs, deepgram, polly, kokoro, edge" }),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("set-model"),
    model: Type.String({
      description: "LLM model e.g. google-gemini-cli/gemini-3-fast-preview or xai/grok-4-1-fast-non-reasoning",
    }),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
  Type.Object({
    action: Type.Literal("set-think"),
    level: Type.Union([Type.Literal("off"), Type.Literal("low"), Type.Literal("medium"), Type.Literal("high")]),
    guildId: Type.Optional(Type.String({ description: "Guild ID (optional)" })),
  }),
]);

/** Singleton: prevent duplicate init when plugin is loaded via both openclaw.extensions and clawdbot.extensions */
let discordVoiceRegistered = false;

const discordVoicePlugin = {
  id: "discord-voice",
  name: "Discord Voice",
  description: "Real-time voice conversations in Discord voice channels",

  configSchema: {
    parse(value: unknown): DiscordVoiceConfig {
      return parseConfig(value);
    },
  },

  register(api: PluginApi) {
    if (discordVoiceRegistered) {
      api.logger.warn(
        "[discord-voice] Plugin already registered (likely loaded via both openclaw and clawdbot extensions). Skipping duplicate init to prevent double processing.",
      );
      return;
    }
    discordVoiceRegistered = true;

    const cfg = parseConfig(api.pluginConfig, api.config as Record<string, unknown>);
    let voiceManager: VoiceConnectionManager | null = null;
    let discordClient: Client | null = null;
    let clientReady = false;

    if (!cfg.enabled) {
      discordVoiceRegistered = false;
      api.logger.info("[discord-voice] Plugin disabled");
      return;
    }

    if (process.env["NODE_TLS_REJECT_UNAUTHORIZED"] === "0") {
      api.logger.warn(
        "[discord-voice] NODE_TLS_REJECT_UNAUTHORIZED=0 is set — TLS certificate verification is DISABLED. API keys may be exposed to MITM attacks.",
      );
    }

    if (cfg.allowedUsers.length === 0) {
      api.logger.warn(
        "[discord-voice] No allowedUsers configured — all users in joined channels can interact with the bot and trigger API calls. Set allowedUsers to restrict access.",
      );
    }

    // Get Discord token from main config
    const mainConfig = api.config as { discord?: { token?: string }; channels?: { discord?: { token?: string } } };
    const discordToken = mainConfig?.channels?.discord?.token || mainConfig?.discord?.token;

    if (!discordToken) {
      discordVoiceRegistered = false;
      api.logger.error(
        "[discord-voice] No Discord token found in config. Plugin requires discord.token to be configured.",
      );
      return;
    }

    // Create our own Discord client with voice intents
    discordClient = new Client({
      intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates, GatewayIntentBits.GuildMessages],
    });

    discordClient.once("ready", async () => {
      clientReady = true;
      api.logger.info(`[discord-voice] Discord client ready as ${discordClient?.user?.tag}`);

      // Auto-join channel if configured
      if (cfg.autoJoinChannel) {
        try {
          api.logger.info(`[discord-voice] Auto-joining channel ${cfg.autoJoinChannel}`);
          // Wait a moment for everything to initialize
          await new Promise((resolve) => setTimeout(resolve, 2000));

          const channel = await discordClient!.channels.fetch(cfg.autoJoinChannel);
          if (channel && channel.isVoiceBased()) {
            const vm = ensureVoiceManager();
            await vm.join(channel as VoiceBasedChannel);
            api.logger.info(`[discord-voice] Auto-joined voice channel: ${channel.name}`);
          } else {
            api.logger.warn(`[discord-voice] Auto-join channel ${cfg.autoJoinChannel} is not a voice channel`);
          }
        } catch (error) {
          api.logger.error(
            `[discord-voice] Failed to auto-join: ${error instanceof Error ? error.message : String(error)}`,
          );
        }
      }
    });

    discordClient.login(discordToken).catch((err) => {
      api.logger.error(`[discord-voice] Failed to login: ${err instanceof Error ? err.message : String(err)}`);
    });

    /**
     * Handle transcribed speech - route to agent and get response
     */
    async function handleTranscript(userId: string, guildId: string, channelId: string, text: string): Promise<string> {
      api.logger.debug?.(`[discord-voice] Processing transcript from user (${text.length} chars)`);

      try {
        const deps = await loadCoreAgentDeps(cfg.openclawRoot);
        if (!deps) {
          api.logger.error("[discord-voice] Could not load core dependencies");
          return "I'm having trouble connecting to my brain right now.";
        }

        const coreConfig = api.config as CoreConfig;
        const agentId = "main";

        // Build session key based on guild
        const sessionKey = `discord:voice:${guildId}`;

        // Resolve paths
        const storePath = deps.resolveStorePath(coreConfig.session?.store, { agentId });
        const agentDir = deps.resolveAgentDir(coreConfig, agentId);
        const workspaceDir = deps.resolveAgentWorkspaceDir(coreConfig, agentId);

        // Ensure workspace exists
        await deps.ensureAgentWorkspace({ dir: workspaceDir });

        // Load or create session entry
        const sessionStore = deps.loadSessionStore(storePath);
        const now = Date.now();
        type SessionEntry = { sessionId: string; updatedAt: number };
        let sessionEntry = sessionStore[sessionKey] as SessionEntry | undefined;

        if (!sessionEntry) {
          sessionEntry = {
            sessionId: crypto.randomUUID(),
            updatedAt: now,
          };
          sessionStore[sessionKey] = sessionEntry;
          await deps.saveSessionStore(storePath, sessionStore);
        }

        const sessionId = sessionEntry.sessionId;
        const sessionFile = deps.resolveSessionFilePath(sessionId, sessionEntry, { agentId });

        // Session overrides (from /discord_voice set-model, set-think) take precedence over config
        const session = ensureVoiceManager().getSession(guildId);
        const modelRef = session?.modelOverride ?? cfg.model ?? `${deps.DEFAULT_PROVIDER}/${deps.DEFAULT_MODEL}`;
        const slashIndex = modelRef.indexOf("/");
        const provider = slashIndex === -1 ? deps.DEFAULT_PROVIDER : modelRef.slice(0, slashIndex);
        const model = slashIndex === -1 ? modelRef : modelRef.slice(slashIndex + 1);

        const thinkLevel = (session?.thinkLevelOverride ?? cfg.thinkLevel ?? "off") as
          | "off"
          | "low"
          | "medium"
          | "high";

        // Resolve agent identity — sanitize name to prevent prompt injection via config
        const identity = deps.resolveAgentIdentity(coreConfig, agentId);
        const rawName = identity?.name?.trim() || "assistant";
        // eslint-disable-next-line no-control-regex
        const agentName = rawName.replace(/[\u0000-\u001F\u007F]/g, "").slice(0, 100) || "assistant";

        const noEmojiPart =
          cfg.noEmojiHint === false
            ? ""
            : typeof cfg.noEmojiHint === "string"
              ? ` ${sanitizeNoEmojiHint(cfg.noEmojiHint)}`
              : ` ${DEFAULT_NO_EMOJI_HINT}`;
        // Sanitize userId to prevent prompt injection (must be a Discord snowflake)
        const safeUserId = DISCORD_SNOWFLAKE_RE.test(userId) ? userId : "unknown";
        const extraSystemPrompt = `You are ${agentName}, speaking in a Discord voice channel. Keep responses brief and conversational (1-2 sentences max). Be natural and friendly.${noEmojiPart} You have access to all your normal tools and skills. The user's Discord ID is ${safeUserId}. Your reply will be read aloud automatically—do not use the discord_voice speak tool to respond; just return your reply as text.`;

        const timeoutMs = deps.resolveAgentTimeoutMs({ cfg: coreConfig });
        const runId = `discord-voice:${guildId}:${Date.now()}`;

        const result = await deps.runEmbeddedPiAgent({
          sessionId,
          sessionKey,
          messageProvider: "discord",
          sessionFile,
          workspaceDir,
          config: coreConfig,
          prompt: text,
          provider,
          model,
          thinkLevel,
          verboseLevel: "off",
          timeoutMs,
          runId,
          lane: "discord-voice",
          extraSystemPrompt,
          agentDir,
        });

        // Extract text from payloads
        const texts = (result.payloads ?? [])
          .filter((p) => p.text && !p.isError)
          .map((p) => p.text?.trim())
          .filter(Boolean);

        return texts.join(" ") || "";
      } catch (error) {
        api.logger.error(`[discord-voice] Agent chat error: ${error instanceof Error ? error.message : String(error)}`);
        return "I'm sorry, I encountered an error processing your request.";
      }
    }

    /**
     * Ensure voice manager is initialized
     */
    function ensureVoiceManager(): VoiceConnectionManager {
      if (!voiceManager) {
        voiceManager = new VoiceConnectionManager(cfg, api.logger, handleTranscript);
      }
      return voiceManager;
    }

    /**
     * Get Discord client
     */
    function getDiscordClient(): Client | null {
      if (!clientReady) {
        api.logger.warn("[discord-voice] Discord client not ready yet");
        return null;
      }
      return discordClient;
    }

    // Register Gateway RPC methods
    api.registerGatewayMethod("discord_voice.join", async ({ params, respond }) => {
      try {
        const p = params as { channelId?: string } | null;
        const channelId = p?.channelId;

        if (!channelId) {
          respond(false, { error: "channelId required" });
          return;
        }

        const client = getDiscordClient();
        if (!client) {
          respond(false, { error: "Discord client not available" });
          return;
        }

        const channel = await client.channels.fetch(channelId);
        if (!channel || !("guild" in channel) || !channel.isVoiceBased()) {
          respond(false, { error: "Invalid voice channel" });
          return;
        }

        const vm = ensureVoiceManager();
        const session = await vm.join(channel as VoiceBasedChannel);

        respond(true, {
          joined: true,
          guildId: session.guildId,
          channelId: session.channelId,
        });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.leave", async ({ params, respond }) => {
      try {
        const p = params as { guildId?: string } | null;
        let guildId = p?.guildId;

        const vm = ensureVoiceManager();

        // If no guildId provided, leave all
        if (!guildId) {
          const sessions = vm.getAllSessions();
          const firstSession = sessions[0];
          if (!firstSession) {
            respond(true, { left: false, reason: "Not in any voice channel" });
            return;
          }
          guildId = firstSession.guildId;
        }

        const left = await vm.leave(guildId);
        respond(true, { left, guildId });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.speak", async ({ params, respond }) => {
      try {
        const p = params as { text?: string; guildId?: string } | null;
        const text = p?.text?.slice(0, MAX_TTS_TEXT_LENGTH);
        let guildId = p?.guildId;

        if (!text) {
          respond(false, { error: "text required" });
          return;
        }

        const vm = ensureVoiceManager();

        if (!guildId) {
          const sessions = vm.getAllSessions();
          const firstSession = sessions[0];
          if (!firstSession) {
            respond(false, { error: "Not in any voice channel" });
            return;
          }
          guildId = firstSession.guildId;
        }

        await vm.speak(guildId, text);
        respond(true, { spoken: true });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.status", async ({ params, respond }) => {
      try {
        const vm = ensureVoiceManager();
        const p = params as { guildId?: string } | null;
        let guildId = p?.guildId;
        const allSessions = vm.getAllSessions();
        if (!guildId && allSessions.length > 0) guildId = allSessions[0]!.guildId;
        const sessions = allSessions
          .filter((s) => !guildId || s.guildId === guildId)
          .map((s) => {
            const stt = vm.getSttProviderInfo(s);
            const tts = vm.getTtsProviderInfo(s);
            const effectiveModel = s.modelOverride ?? cfg.model ?? "default";
            const effectiveThink = s.thinkLevelOverride ?? cfg.thinkLevel ?? "off";
            return {
              guildId: s.guildId,
              channelId: s.channelId,
              channelName: s.channelName,
              speaking: s.speaking,
              usersListening: s.userAudioStates.size,
              sttProvider: stt.provider,
              sttModel: stt.model,
              ttsProvider: tts.provider,
              ttsModel: tts.model,
              model: effectiveModel,
              thinkLevel: effectiveThink,
            };
          });
        const availableModels = getAvailableModels(api.config as Record<string, unknown>);
        respond(true, {
          sessions,
          config: {
            model: cfg.model,
            thinkLevel: cfg.thinkLevel,
            sttProvider: cfg.sttProvider,
            ttsProvider: cfg.ttsProvider,
          },
          availableModels,
        });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.set-stt", async ({ params, respond }) => {
      try {
        const p = params as { guildId?: string; provider?: string } | null;
        const provider = p?.provider;
        if (!provider) {
          respond(false, { error: "provider required" });
          return;
        }
        const valid = [
          "whisper",
          "gpt4o-mini",
          "gpt4o-transcribe",
          "gpt4o-transcribe-diarize",
          "deepgram",
          "local-whisper",
          "wyoming-whisper",
        ];
        if (!valid.includes(provider)) {
          respond(false, { error: `Invalid provider. Valid: ${valid.join(", ")}` });
          return;
        }
        const vm = ensureVoiceManager();
        let guildId = p?.guildId;
        if (!guildId) {
          const sessions = vm.getAllSessions();
          if (sessions.length === 0) {
            respond(false, { error: "Not in any voice channel" });
            return;
          }
          guildId = sessions[0]!.guildId;
        }
        const ok = vm.setVoiceConfig(guildId!, {
          sttProvider: provider as DiscordVoiceConfig["sttProvider"],
        });
        respond(ok, ok ? { sttProvider: provider, guildId } : { error: "Session not found" });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.set-tts", async ({ params, respond }) => {
      try {
        const p = params as { guildId?: string; provider?: string } | null;
        const provider = p?.provider;
        if (!provider) {
          respond(false, { error: "provider required" });
          return;
        }
        const valid = ["openai", "elevenlabs", "deepgram", "polly", "kokoro", "edge"];
        if (!valid.includes(provider)) {
          respond(false, { error: `Invalid provider. Valid: ${valid.join(", ")}` });
          return;
        }
        const vm = ensureVoiceManager();
        let guildId = p?.guildId;
        if (!guildId) {
          const sessions = vm.getAllSessions();
          if (sessions.length === 0) {
            respond(false, { error: "Not in any voice channel" });
            return;
          }
          guildId = sessions[0]!.guildId;
        }
        const ok = vm.setVoiceConfig(guildId!, {
          ttsProvider: provider as DiscordVoiceConfig["ttsProvider"],
        });
        respond(ok, ok ? { ttsProvider: provider, guildId } : { error: "Session not found" });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.set-model", async ({ params, respond }) => {
      try {
        const p = params as { guildId?: string; model?: string } | null;
        const model = p?.model;
        if (!model || typeof model !== "string" || !model.trim()) {
          respond(false, { error: "model required (e.g. google-gemini-cli/gemini-3-fast-preview)" });
          return;
        }
        const vm = ensureVoiceManager();
        let guildId = p?.guildId;
        if (!guildId) {
          const sessions = vm.getAllSessions();
          if (sessions.length === 0) {
            respond(false, { error: "Not in any voice channel" });
            return;
          }
          guildId = sessions[0]!.guildId;
        }
        const ok = vm.setVoiceConfig(guildId!, { model: model.trim() });
        const available = getAvailableModels(api.config as Record<string, unknown>);
        respond(ok, ok ? { model: model.trim(), guildId, availableModels: available } : { error: "Session not found" });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.set-think", async ({ params, respond }) => {
      try {
        const p = params as { guildId?: string; level?: string } | null;
        const level = p?.level;
        if (!level) {
          respond(false, { error: "level required: off, low, medium, high" });
          return;
        }
        const valid = ["off", "low", "medium", "high"] as const;
        if (!valid.includes(level as (typeof valid)[number])) {
          respond(false, { error: `Invalid level. Valid: ${valid.join(", ")}` });
          return;
        }
        const vm = ensureVoiceManager();
        let guildId = p?.guildId;
        if (!guildId) {
          const sessions = vm.getAllSessions();
          if (sessions.length === 0) {
            respond(false, { error: "Not in any voice channel" });
            return;
          }
          guildId = sessions[0]!.guildId;
        }
        const ok = vm.setVoiceConfig(guildId!, { thinkLevel: level as (typeof valid)[number] });
        respond(ok, ok ? { thinkLevel: level, guildId } : { error: "Session not found" });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.models", async ({ respond }) => {
      try {
        const models = getAvailableModels(api.config as Record<string, unknown>);
        respond(true, { availableModels: models });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    api.registerGatewayMethod("discord_voice.reset-fallback", async ({ params, respond }) => {
      try {
        const vm = ensureVoiceManager();
        const p = params as { guildId?: string } | null;
        let guildId = p?.guildId;
        if (!guildId) {
          const sessions = vm.getAllSessions();
          if (sessions.length === 0) {
            respond(true, { reset: false, reason: "Not in any voice channel" });
            return;
          }
          guildId = sessions[0]!.guildId;
        }
        const reset = vm.resetFallbacks(guildId!);
        respond(true, { reset, guildId });
      } catch (error) {
        respond(false, { error: error instanceof Error ? error.message : String(error) });
      }
    });

    // Register agent tool
    api.registerTool({
      name: "discord_voice",
      label: "Discord Voice",
      description: "Control Discord voice channel - join, leave, speak, or get status",
      parameters: VoiceToolSchema,
      async execute(_toolCallId, params) {
        const json = (payload: unknown) => ({
          content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
          details: payload,
        });

        try {
          const p = params as { action: string; channelId?: string; guildId?: string; text?: string };
          const vm = ensureVoiceManager();
          const client = getDiscordClient();

          switch (p.action) {
            case "join": {
              if (!p.channelId) throw new Error("channelId required");
              if (!client) throw new Error("Discord client not available");

              const channel = await client.channels.fetch(p.channelId);
              if (!channel || !("guild" in channel) || !channel.isVoiceBased()) {
                throw new Error("Invalid voice channel");
              }

              const session = await vm.join(channel as VoiceBasedChannel);
              return json({ joined: true, guildId: session.guildId, channelId: session.channelId });
            }

            case "leave": {
              let guildId = p.guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                const firstSession = sessions[0];
                if (!firstSession) {
                  return json({ left: false, reason: "Not in any voice channel" });
                }
                guildId = firstSession.guildId;
              }
              const left = await vm.leave(guildId);
              return json({ left, guildId });
            }

            case "speak": {
              if (!p.text) throw new Error("text required");
              p.text = p.text.slice(0, MAX_TTS_TEXT_LENGTH);
              let guildId = p.guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                const firstSession = sessions[0];
                if (!firstSession) {
                  throw new Error("Not in any voice channel");
                }
                guildId = firstSession.guildId;
              }
              vm.markSpokeViaTool(guildId);
              await vm.speak(guildId, p.text);
              return json({ spoken: true });
            }

            case "status": {
              const sessions = vm.getAllSessions().map((s) => {
                const stt = vm.getSttProviderInfo(s);
                const tts = vm.getTtsProviderInfo(s);
                return {
                  guildId: s.guildId,
                  channelId: s.channelId,
                  channelName: s.channelName,
                  speaking: s.speaking,
                  usersListening: s.userAudioStates.size,
                  sttProvider: stt.provider,
                  sttModel: stt.model,
                  ttsProvider: tts.provider,
                  ttsModel: tts.model,
                  model: s.modelOverride ?? cfg.model ?? "default",
                  thinkLevel: s.thinkLevelOverride ?? cfg.thinkLevel ?? "off",
                };
              });
              const availableModels = getAvailableModels(api.config as Record<string, unknown>);
              return json({ sessions, availableModels });
            }

            case "set-stt": {
              const provider = (p as { provider?: string }).provider;
              if (!provider) throw new Error("provider required");
              const valid = [
                "whisper",
                "gpt4o-mini",
                "gpt4o-transcribe",
                "gpt4o-transcribe-diarize",
                "deepgram",
                "local-whisper",
                "wyoming-whisper",
              ];
              if (!valid.includes(provider)) throw new Error(`Invalid provider. Valid: ${valid.join(", ")}`);
              let guildId = (p as { guildId?: string }).guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                if (sessions.length === 0) throw new Error("Not in any voice channel");
                guildId = sessions[0]!.guildId;
              }
              const ok = vm.setVoiceConfig(guildId!, {
                sttProvider: provider as DiscordVoiceConfig["sttProvider"],
              });
              return json(ok ? { sttProvider: provider, guildId } : { error: "Session not found" });
            }

            case "set-tts": {
              const provider = (p as { provider?: string }).provider;
              if (!provider) throw new Error("provider required");
              const valid = ["openai", "elevenlabs", "deepgram", "polly", "kokoro", "edge"];
              if (!valid.includes(provider)) throw new Error(`Invalid provider. Valid: ${valid.join(", ")}`);
              let guildId = (p as { guildId?: string }).guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                if (sessions.length === 0) throw new Error("Not in any voice channel");
                guildId = sessions[0]!.guildId;
              }
              const ok = vm.setVoiceConfig(guildId!, {
                ttsProvider: provider as DiscordVoiceConfig["ttsProvider"],
              });
              return json(ok ? { ttsProvider: provider, guildId } : { error: "Session not found" });
            }

            case "set-model": {
              const model = (p as { model?: string }).model;
              if (!model || typeof model !== "string" || !model.trim()) throw new Error("model required");
              let guildId = (p as { guildId?: string }).guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                if (sessions.length === 0) throw new Error("Not in any voice channel");
                guildId = sessions[0]!.guildId;
              }
              const ok = vm.setVoiceConfig(guildId!, { model: model.trim() });
              const available = getAvailableModels(api.config as Record<string, unknown>);
              return json(
                ok ? { model: model.trim(), guildId, availableModels: available } : { error: "Session not found" },
              );
            }

            case "set-think": {
              const level = (p as { level?: string }).level;
              if (!level) throw new Error("level required: off, low, medium, high");
              const valid = ["off", "low", "medium", "high"];
              if (!valid.includes(level)) throw new Error(`Invalid level. Valid: ${valid.join(", ")}`);
              let guildId = (p as { guildId?: string }).guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                if (sessions.length === 0) throw new Error("Not in any voice channel");
                guildId = sessions[0]!.guildId;
              }
              const ok = vm.setVoiceConfig(guildId!, { thinkLevel: level as "off" | "low" | "medium" | "high" });
              return json(ok ? { thinkLevel: level, guildId } : { error: "Session not found" });
            }

            case "reset-fallback": {
              let guildId = p.guildId;
              if (!guildId) {
                const sessions = vm.getAllSessions();
                if (sessions.length === 0) return json({ reset: false, reason: "Not in any voice channel" });
                guildId = sessions[0]!.guildId;
              }
              const reset = vm.resetFallbacks(guildId!);
              return json({ reset, guildId });
            }

            default:
              throw new Error(`Unknown action: ${p.action}`);
          }
        } catch (error) {
          return json({ error: error instanceof Error ? error.message : String(error) });
        }
      },
    });

    // Register CLI commands
    api.registerCli(
      ({ program }) => {
        interface CliCommand {
          command(name: string): CliCommand;
          description(desc: string): CliCommand;
          argument(name: string, desc: string): CliCommand;
          option(flags: string, desc: string): CliCommand;
          action(fn: (...args: never[]) => void | Promise<void>): CliCommand;
        }
        const prog = program as CliCommand;

        const voiceCmd = prog.command("discord_voice").description("Discord voice channel commands");

        voiceCmd
          .command("join")
          .description("Join a Discord voice channel")
          .argument("<channelId>", "Voice channel ID")
          .action(async (channelId: string) => {
            const client = getDiscordClient();
            if (!client) {
              console.error("Discord client not available");
              return;
            }

            try {
              const channel = await client.channels.fetch(channelId);
              if (!channel || !("guild" in channel) || !channel.isVoiceBased()) {
                console.error("Invalid voice channel");
                return;
              }

              const vm = ensureVoiceManager();
              const session = await vm.join(channel as VoiceBasedChannel);
              console.log(`Joined voice channel in guild ${session.guildId}`);
            } catch (error) {
              console.error(`Failed to join: ${error instanceof Error ? error.message : String(error)}`);
            }
          });

        voiceCmd
          .command("leave")
          .description("Leave the current voice channel")
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;

            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }

            const left = await vm.leave(guildId);
            console.log(left ? `Left voice channel in guild ${guildId}` : "Failed to leave");
          });

        voiceCmd
          .command("status")
          .description("Show voice connection status and providers")
          .action(() => {
            const vm = ensureVoiceManager();
            const sessions = vm.getAllSessions();

            if (sessions.length === 0) {
              console.log("Not connected to any voice channels");
              return;
            }

            const models = getAvailableModels(api.config as Record<string, unknown>);
            if (models.length > 0) {
              console.log("Available models:", models.join(", "));
            }

            for (const s of sessions) {
              const stt = vm.getSttProviderInfo(s);
              const tts = vm.getTtsProviderInfo(s);
              const model = s.modelOverride ?? cfg.model ?? "default";
              const think = s.thinkLevelOverride ?? cfg.thinkLevel ?? "off";
              console.log(`Guild: ${s.guildId}`);
              console.log(`  Channel: ${s.channelId} ${s.channelName ? `(${s.channelName})` : ""}`);
              console.log(`  Speaking: ${s.speaking}`);
              console.log(`  Users listening: ${s.userAudioStates.size}`);
              console.log(`  STT: ${stt.provider} / ${stt.model}`);
              console.log(`  TTS: ${tts.provider} / ${tts.model}`);
              console.log(`  Model: ${model}, Think: ${think}`);
            }
          });

        voiceCmd
          .command("set-stt")
          .description("Set STT provider for current session")
          .argument(
            "<provider>",
            "whisper | gpt4o-mini | gpt4o-transcribe | gpt4o-transcribe-diarize | deepgram | local-whisper | wyoming-whisper",
          )
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (provider: string, opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;
            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }
            const valid = [
              "whisper",
              "gpt4o-mini",
              "gpt4o-transcribe",
              "gpt4o-transcribe-diarize",
              "deepgram",
              "local-whisper",
              "wyoming-whisper",
            ];
            if (!valid.includes(provider)) {
              console.error(`Invalid provider. Valid: ${valid.join(", ")}`);
              return;
            }
            const ok = vm.setVoiceConfig(guildId, {
              sttProvider: provider as DiscordVoiceConfig["sttProvider"],
            });
            console.log(ok ? `STT provider set to ${provider}` : "Session not found");
          });

        voiceCmd
          .command("set-tts")
          .description("Set TTS provider for current session")
          .argument("<provider>", "openai | elevenlabs | deepgram | polly | kokoro | edge")
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (provider: string, opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;
            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }
            const valid = ["openai", "elevenlabs", "deepgram", "polly", "kokoro", "edge"];
            if (!valid.includes(provider)) {
              console.error(`Invalid provider. Valid: ${valid.join(", ")}`);
              return;
            }
            const ok = vm.setVoiceConfig(guildId, {
              ttsProvider: provider as DiscordVoiceConfig["ttsProvider"],
            });
            console.log(ok ? `TTS provider set to ${provider}` : "Session not found");
          });

        voiceCmd
          .command("set-model")
          .description("Set LLM model for voice responses (e.g. google-gemini-cli/gemini-3-fast-preview)")
          .argument("<model>", "Model ID: provider/model-name")
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (model: string, opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;
            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }
            const ok = vm.setVoiceConfig(guildId, { model: model.trim() });
            if (ok) {
              const available = getAvailableModels(api.config as Record<string, unknown>);
              console.log(`Model set to ${model}`);
              if (available.length > 0 && !available.includes(model)) {
                console.log("Note: Available models in config:", available.join(", "));
              }
            } else {
              console.log("Session not found");
            }
          });

        voiceCmd
          .command("set-think")
          .description("Set thinking level (off | low | medium | high)")
          .argument("<level>", "off | low | medium | high")
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (level: string, opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;
            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }
            const valid = ["off", "low", "medium", "high"];
            if (!valid.includes(level)) {
              console.error(`Invalid level. Valid: ${valid.join(", ")}`);
              return;
            }
            const ok = vm.setVoiceConfig(guildId, { thinkLevel: level as "off" | "low" | "medium" | "high" });
            console.log(ok ? `Think level set to ${level}` : "Session not found");
          });

        voiceCmd
          .command("reset-fallback")
          .description("Reset STT/TTS fallbacks – next request will try primary providers")
          .option("-g, --guild <guildId>", "Guild ID")
          .action(async (opts: { guild?: string }) => {
            const vm = ensureVoiceManager();
            const guildId = opts.guild || vm.getAllSessions()[0]?.guildId;

            if (!guildId) {
              console.log("Not in any voice channel");
              return;
            }

            const reset = vm.resetFallbacks(guildId);
            console.log(reset ? `Reset fallbacks for guild ${guildId}` : `No active fallbacks for guild ${guildId}`);
          });
      },
      { commands: ["discord_voice"] },
    );

    // Register background service
    api.registerService({
      id: "discord-voice",
      start: async () => {
        api.logger.info("[discord-voice] Service started");
      },
      stop: async () => {
        if (voiceManager) {
          await voiceManager.destroy();
          voiceManager = null;
        }
        discordVoiceRegistered = false;
        api.logger.info("[discord-voice] Service stopped");
      },
    });
  },
};

export default discordVoicePlugin;
