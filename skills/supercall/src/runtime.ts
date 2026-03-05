import crypto from "node:crypto";

import type { VoiceCallConfig } from "./config.js";
import type { CoreConfig } from "./types.js";
import { validateProviderConfig } from "./config.js";
import { CallManager } from "./manager.js";
import type { VoiceCallProvider } from "./providers/base.js";
import { MockProvider } from "./providers/mock.js";
import { TwilioProvider } from "./providers/twilio.js";
import { startTunnel, type TunnelResult } from "./tunnel.js";
import {
  cleanupTailscaleExposure,
  setupTailscaleExposure,
  VoiceCallWebhookServer,
} from "./webhook.js";

export type VoiceCallRuntime = {
  config: VoiceCallConfig;
  provider: VoiceCallProvider;
  manager: CallManager;
  webhookServer: VoiceCallWebhookServer;
  webhookUrl: string;
  publicUrl: string | null;
  stop: () => Promise<void>;
};

type Logger = {
  info: (message: string) => void;
  warn: (message: string) => void;
  error: (message: string) => void;
  debug: (message: string) => void;
};

function resolveProvider(config: VoiceCallConfig): VoiceCallProvider {
  switch (config.provider) {
    case "twilio":
      return new TwilioProvider(
        {
          accountSid:
            config.twilio?.accountSid ?? process.env.TWILIO_ACCOUNT_SID,
          authToken: config.twilio?.authToken ?? process.env.TWILIO_AUTH_TOKEN,
        },
        {
          publicUrl: config.publicUrl,
          streamPath: config.streaming?.streamPath,
        },
      );
    case "mock":
      return new MockProvider();
    default:
      throw new Error(
        `Unsupported supercall provider: ${String(config.provider)}`,
      );
  }
}

export async function createVoiceCallRuntime(params: {
  config: VoiceCallConfig;
  coreConfig: CoreConfig;
  logger?: Logger;
}): Promise<VoiceCallRuntime> {
  const { config, coreConfig, logger } = params;
  const log = logger ?? {
    info: console.log,
    warn: console.warn,
    error: console.error,
    debug: console.debug,
  };

  if (!config.enabled) {
    throw new Error(
      "SuperCall disabled. Enable the plugin entry in config.",
    );
  }

  const validation = validateProviderConfig(config);
  if (!validation.valid) {
    throw new Error(`Invalid supercall config: ${validation.errors.join("; ")}`);
  }

  const realtimeApiKey =
    config.streaming?.openaiApiKey ?? process.env.OPENAI_API_KEY;
  if (!realtimeApiKey) {
    throw new Error(
      "Full realtime mode requires an OpenAI API key (streaming.openaiApiKey or OPENAI_API_KEY).",
    );
  }

  if (config.provider !== "twilio" && config.provider !== "mock") {
    throw new Error(
      "Full realtime mode currently supports Twilio (or mock) providers only.",
    );
  }

  const provider = resolveProvider(config);
  const selfTestSecret = crypto.randomBytes(24).toString("hex");
  const manager = new CallManager(config, undefined, { selfTestSecret });
  const webhookServer = new VoiceCallWebhookServer(
    config,
    manager,
    provider,
    coreConfig,
    { selfTestSecret },
  );

  const localUrl = await webhookServer.start();

  // Determine public URL - priority: config.publicUrl > tunnel > legacy tailscale
  let publicUrl: string | null = config.publicUrl ?? null;
  let tunnelResult: TunnelResult | null = null;

  if (!publicUrl && config.tunnel?.provider && config.tunnel.provider !== "none") {
    try {
      tunnelResult = await startTunnel({
        provider: config.tunnel.provider,
        port: config.serve.port,
        path: config.serve.path,
        ngrokAuthToken:
          config.tunnel.ngrokAuthToken ?? process.env.NGROK_AUTHTOKEN,
        ngrokDomain: config.tunnel.ngrokDomain ?? process.env.NGROK_DOMAIN,
      });
      publicUrl = tunnelResult?.publicUrl ?? null;
    } catch (err) {
      log.error(
        `[supercall] Tunnel setup failed: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }

  if (!publicUrl && config.tailscale?.mode !== "off") {
    publicUrl = await setupTailscaleExposure(config);
  }

  const webhookUrl = publicUrl ?? localUrl;

  if (publicUrl && provider.name === "twilio") {
    (provider as TwilioProvider).setPublicUrl(publicUrl);
  }

  if (provider.name === "twilio") {
    // Twilio media streams are handled in the webhook server.
  }

  manager.initialize(provider, webhookUrl);

  const stop = async () => {
    if (tunnelResult) {
      await tunnelResult.stop();
    }
    await cleanupTailscaleExposure(config);
    await webhookServer.stop();
  };

  log.info("[supercall] Runtime initialized");
  log.info(`[supercall] Webhook URL: ${webhookUrl}`);
  if (publicUrl) {
    log.info(`[supercall] Public URL: ${publicUrl}`);
  }

  return {
    config,
    provider,
    manager,
    webhookServer,
    webhookUrl,
    publicUrl,
    stop,
  };
}
