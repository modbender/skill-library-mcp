import { spawn } from "node:child_process";
import http from "node:http";
import { URL } from "node:url";

import type { VoiceCallConfig } from "./config.js";
import type { CallManager } from "./manager.js";
import type { MediaStreamConfig } from "./media-stream.js";
import { MediaStreamHandler } from "./media-stream.js";
import type { VoiceCallProvider } from "./providers/base.js";
import { OpenAIRealtimeConversationProvider } from "./providers/openai-realtime-conversation.js";
import type { NormalizedEvent, WebhookContext } from "./types.js";

/**
 * HTTP server for receiving voice call webhooks from providers.
 * Supports WebSocket upgrades for media streams when streaming is enabled.
 */
export class VoiceCallWebhookServer {
  private server: http.Server | null = null;
  private config: VoiceCallConfig;
  private manager: CallManager;
  private provider: VoiceCallProvider;
  private selfTestSecret: string | null = null;

  /** Media stream handler for bidirectional audio (when streaming enabled) */
  private mediaStreamHandler: MediaStreamHandler | null = null;

  constructor(
    config: VoiceCallConfig,
    manager: CallManager,
    provider: VoiceCallProvider,
    _coreConfig?: unknown,
    options?: { selfTestSecret?: string },
  ) {
    this.config = config;
    this.manager = manager;
    this.provider = provider;
    this.selfTestSecret = options?.selfTestSecret ?? null;

    // Initialize media stream handler (always needed for supercall)
    this.initializeMediaStreaming();
  }

  /**
   * Get the media stream handler (for wiring to provider).
   */
  getMediaStreamHandler(): MediaStreamHandler | null {
    return this.mediaStreamHandler;
  }

  /**
   * Initialize media streaming with full realtime mode.
   */
  private initializeMediaStreaming(): void {
    const apiKey =
      this.config.streaming?.openaiApiKey || process.env.OPENAI_API_KEY;

    if (!apiKey) {
      console.warn(
        "[supercall] Streaming enabled but no OpenAI API key found",
      );
      return;
    }

    console.log("[supercall] 🎙️ Initializing full realtime mode");

    const defaultInstructions =
      "You are a helpful voice assistant. Be concise and natural. Keep responses short (1-2 sentences).";
    const conversationProvider = new OpenAIRealtimeConversationProvider({
      apiKey,
      voice: "marin",
      silenceDurationMs: this.config.streaming?.silenceDurationMs,
      vadThreshold: this.config.streaming?.vadThreshold,
      instructions: defaultInstructions,
    });

    const streamConfig: MediaStreamConfig = {
      conversationProvider,

      // Get instructions for realtime calls
      getInstructionsForCall: (providerCallId: string) => {
        const call = this.manager.getCallByProviderCallId(providerCallId);
        if (call?.metadata?.personaPrompt) {
          return call.metadata.personaPrompt as string;
        }
        return defaultInstructions;
      },
      
      // Get initial greeting for realtime calls (AI speaks first)
      getInitialGreetingForCall: (providerCallId: string) => {
        const call = this.manager.getCallByProviderCallId(providerCallId);

        let openingLine = (call?.metadata?.initialMessage ?? call?.metadata?.openingLine) as string | undefined;

        if (openingLine) {
          console.log(`[supercall] Initial greeting for ${providerCallId.slice(0,12)}...: "${openingLine.slice(0,60)}..."`);
        } else {
          console.log(`[supercall] No initial greeting found for ${providerCallId.slice(0,12)}... (AI will wait for user)`);
        }
        return openingLine;
      },
      // Realtime mode callbacks
      onUserTranscript: (providerCallId, transcript) => {
        console.log(`[supercall] User said: "${transcript}"`);
        const call = this.manager.getCallByProviderCallId(providerCallId);
        if (call) {
          const event: NormalizedEvent = {
            id: `stream-transcript-${Date.now()}`,
            type: "call.speech",
            callId: call.callId,
            providerCallId,
            timestamp: Date.now(),
            transcript,
            isFinal: true,
          };
          this.manager.processEvent(event);
        }
      },

      onAssistantTranscript: (providerCallId, transcript) => {
        console.log(`[supercall] AI said: "${transcript}"`);
        const call = this.manager.getCallByProviderCallId(providerCallId);
        if (call) {
          this.manager.addTranscriptEntry(call.callId, "bot", transcript);
        }
      },

      // Common callbacks
      onConnect: (callId, streamSid) => {
        console.log(`[supercall] Media stream connected: ${callId} -> ${streamSid}`);
      },

      onDisconnect: (callId) => {
        console.log(`[supercall] Media stream disconnected: ${callId}`);
      },

      onHangupRequested: (providerCallId, reason) => {
        console.log(`[supercall] 📞 AI requested hangup: ${reason}`);
        const call = this.manager.getCallByProviderCallId(providerCallId);
        if (call) {
          console.log(`[supercall] Ending call ${call.callId} (provider: ${providerCallId.slice(0, 12)}...)`);
          this.manager.endCall(call.callId).catch((err) => {
            console.error(`[supercall] Failed to end call: ${err.message}`);
          });
        } else {
          console.warn(`[supercall] Could not find call for provider ID: ${providerCallId}`);
        }
      },
    };

    this.mediaStreamHandler = new MediaStreamHandler(streamConfig);
    console.log("[supercall] Full realtime media streaming initialized");
  }

  /**
   * Start the webhook server.
   */
  async start(): Promise<string> {
    const { port, bind, path: webhookPath } = this.config.serve;
    const streamPath = this.config.streaming?.streamPath || "/voice/stream";

    return new Promise((resolve, reject) => {
      this.server = http.createServer((req, res) => {
        this.handleRequest(req, res, webhookPath).catch((err) => {
          console.error("[supercall] Webhook error:", err);
          res.statusCode = 500;
          res.end("Internal Server Error");
        });
      });

      // Handle WebSocket upgrades for media streams
      if (this.mediaStreamHandler) {
        this.server.on("upgrade", (request, socket, head) => {
          const url = new URL(
            request.url || "/",
            `http://${request.headers.host}`,
          );

          if (url.pathname === streamPath) {
            console.log("[supercall] WebSocket upgrade for media stream");
            this.mediaStreamHandler?.handleUpgrade(request, socket, head);
          } else {
            socket.destroy();
          }
        });
      }

      this.server.on("error", reject);

      this.server.listen(port, bind, () => {
        const url = `http://${bind}:${port}${webhookPath}`;
        console.log(`[supercall] Webhook server listening on ${url}`);
        if (this.mediaStreamHandler) {
          console.log(
            `[supercall] Media stream WebSocket on ws://${bind}:${port}${streamPath}`,
          );
        }
        resolve(url);
      });
    });
  }

  /**
   * Stop the webhook server.
   */
  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          this.server = null;
          resolve();
        });
      } else {
        resolve();
      }
    });
  }

  /**
   * Handle incoming HTTP request.
   */
  private async handleRequest(
    req: http.IncomingMessage,
    res: http.ServerResponse,
    webhookPath: string,
  ): Promise<void> {
    const url = new URL(req.url || "/", `http://${req.headers.host}`);

    // Check path
    if (!url.pathname.startsWith(webhookPath)) {
      res.statusCode = 404;
      res.end("Not Found");
      return;
    }

    // Only accept POST
    if (req.method !== "POST") {
      res.statusCode = 405;
      res.end("Method Not Allowed");
      return;
    }

    // Allow internal self-test to bypass signature verification.
    if (
      this.selfTestSecret &&
      req.headers["x-supercall-self-test"] === this.selfTestSecret
    ) {
      res.statusCode = 200;
      res.end("OK");
      return;
    }

    // Read body
    const body = await this.readBody(req);

    // Build webhook context
    const ctx: WebhookContext = {
      headers: req.headers as Record<string, string | string[] | undefined>,
      rawBody: body,
      url: `http://${req.headers.host}${req.url}`,
      method: "POST",
      query: Object.fromEntries(url.searchParams),
    };

    // Verify signature
    const verification = this.provider.verifyWebhook(ctx);
    if (!verification.ok) {
      console.warn(
        `[supercall] Webhook verification failed: ${verification.reason}`,
      );
      res.statusCode = 401;
      res.end("Unauthorized");
      return;
    }

    // Parse events
    const result = this.provider.parseWebhookEvent(ctx);

    // Process each event
    for (const event of result.events) {
      try {
        this.manager.processEvent(event);
      } catch (err) {
        console.error(
          `[supercall] Error processing event ${event.type}:`,
          err,
        );
      }
    }

    // Send response
    res.statusCode = result.statusCode || 200;

    if (result.providerResponseHeaders) {
      for (const [key, value] of Object.entries(
        result.providerResponseHeaders,
      )) {
        res.setHeader(key, value);
      }
    }

    res.end(result.providerResponseBody || "OK");
  }

  /**
   * Read request body as string.
   */
  private readBody(req: http.IncomingMessage): Promise<string> {
    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      req.on("data", (chunk) => chunks.push(chunk));
      req.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
      req.on("error", reject);
    });
  }

  // Auto-response pipeline removed in full realtime mode.
}

/**
 * Resolve the current machine's Tailscale DNS name.
 */
export type TailscaleSelfInfo = {
  dnsName: string | null;
  nodeId: string | null;
};

/**
 * Run a tailscale command with timeout, collecting stdout.
 */
function runTailscaleCommand(
  args: string[],
  timeoutMs = 2500,
): Promise<{ code: number; stdout: string }> {
  return new Promise((resolve) => {
    const proc = spawn("tailscale", args, {
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    proc.stdout.on("data", (data) => {
      stdout += data;
    });

    const timer = setTimeout(() => {
      proc.kill("SIGKILL");
      resolve({ code: -1, stdout: "" });
    }, timeoutMs);

    proc.on("close", (code) => {
      clearTimeout(timer);
      resolve({ code: code ?? -1, stdout });
    });
  });
}

export async function getTailscaleSelfInfo(): Promise<TailscaleSelfInfo | null> {
  const { code, stdout } = await runTailscaleCommand(["status", "--json"]);
  if (code !== 0) return null;

  try {
    const status = JSON.parse(stdout);
    return {
      dnsName: status.Self?.DNSName?.replace(/\.$/, "") || null,
      nodeId: status.Self?.ID || null,
    };
  } catch {
    return null;
  }
}

export async function getTailscaleDnsName(): Promise<string | null> {
  const info = await getTailscaleSelfInfo();
  return info?.dnsName ?? null;
}

export async function setupTailscaleExposureRoute(opts: {
  mode: "serve" | "funnel";
  path: string;
  localUrl: string;
}): Promise<string | null> {
  const dnsName = await getTailscaleDnsName();
  if (!dnsName) {
    console.warn("[supercall] Could not get Tailscale DNS name");
    return null;
  }

  const { code } = await runTailscaleCommand([
    opts.mode,
    "--bg",
    "--yes",
    "--set-path",
    opts.path,
    opts.localUrl,
  ]);

  if (code === 0) {
    const publicUrl = `https://${dnsName}${opts.path}`;
    console.log(`[supercall] Tailscale ${opts.mode} active: ${publicUrl}`);
    return publicUrl;
  }

  console.warn(`[supercall] Tailscale ${opts.mode} failed`);
  return null;
}

export async function cleanupTailscaleExposureRoute(opts: {
  mode: "serve" | "funnel";
  path: string;
}): Promise<void> {
  await runTailscaleCommand([opts.mode, "off", opts.path]);
}

/**
 * Setup Tailscale serve/funnel for the webhook server.
 */
export async function setupTailscaleExposure(
  config: VoiceCallConfig,
): Promise<string | null> {
  if (config.tailscale.mode === "off") {
    return null;
  }

  const mode = config.tailscale.mode === "funnel" ? "funnel" : "serve";
  const localUrl = `http://127.0.0.1:${config.serve.port}${config.serve.path}`;
  return setupTailscaleExposureRoute({
    mode,
    path: config.tailscale.path,
    localUrl,
  });
}

/**
 * Cleanup Tailscale serve/funnel.
 */
export async function cleanupTailscaleExposure(
  config: VoiceCallConfig,
): Promise<void> {
  if (config.tailscale.mode === "off") {
    return;
  }

  const mode = config.tailscale.mode === "funnel" ? "funnel" : "serve";
  await cleanupTailscaleExposureRoute({ mode, path: config.tailscale.path });
}
