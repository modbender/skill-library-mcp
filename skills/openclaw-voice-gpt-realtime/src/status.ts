import type { PluginConfig } from "./config.ts";
import { TwilioClient } from "./twilio-client.ts";
import { assertPublicUrlResolvesToPublicIp } from "./public-url.ts";

export interface StatusCheck {
  name: string;
  ok: boolean;
  details: Record<string, unknown>;
  error?: string;
}

export interface StatusResult {
  ready: boolean;
  checks: {
    twilio: StatusCheck;
    openai: StatusCheck;
    publicUrl: StatusCheck;
    server: StatusCheck;
  };
  issues: string[];
}

export async function checkStatus(config: PluginConfig, serverListening: boolean): Promise<StatusResult> {
  const issues: string[] = [];

  // Run checks in parallel
  const [twilioCheck, openaiCheck, publicUrlCheck] = await Promise.all([
    checkTwilio(config),
    checkOpenAI(config),
    checkPublicUrl(config),
  ]);

  const serverCheck: StatusCheck = {
    name: "server",
    ok: serverListening,
    details: {
      port: config.server.port,
      bind: config.server.bind,
      listening: serverListening,
    },
  };
  if (!serverListening) {
    serverCheck.error = `Server is not listening on port ${config.server.port}`;
    issues.push(`Server is not listening on ${config.server.bind}:${config.server.port}. Start the plugin service.`);
  }

  if (!twilioCheck.ok) issues.push(twilioCheck.error || "Twilio check failed");
  if (!openaiCheck.ok) issues.push(openaiCheck.error || "OpenAI check failed");
  if (!publicUrlCheck.ok) issues.push(publicUrlCheck.error || "Public URL check failed");

  return {
    ready: twilioCheck.ok && openaiCheck.ok && publicUrlCheck.ok && serverCheck.ok,
    checks: {
      twilio: twilioCheck,
      openai: openaiCheck,
      publicUrl: publicUrlCheck,
      server: serverCheck,
    },
    issues,
  };
}

async function checkTwilio(config: PluginConfig): Promise<StatusCheck> {
  const client = new TwilioClient(config);

  const [accountResult, numberResult] = await Promise.all([
    client.verifyAccount(),
    client.verifyPhoneNumber(),
  ]);

  const ok = accountResult.ok && numberResult.ok;

  return {
    name: "twilio",
    ok,
    details: {
      accountSid: accountResult.accountSid,
      accountName: accountResult.friendlyName,
      fromNumber: config.fromNumber,
      numberCapabilities: numberResult.capabilities,
    },
    error: ok
      ? undefined
      : [accountResult.error, numberResult.error].filter(Boolean).join("; "),
  };
}

async function checkOpenAI(config: PluginConfig): Promise<StatusCheck> {
  try {
    // Test OpenAI API key with a simple models list request
    const res = await fetch("https://api.openai.com/v1/models", {
      headers: { Authorization: `Bearer ${config.openai.apiKey}` },
    });

    if (!res.ok) {
      const body = await res.text();
      return {
        name: "openai",
        ok: false,
        details: { model: config.openai.model, apiKeyValid: false },
        error: `OpenAI API key invalid: ${res.status} ${body.slice(0, 200)}`,
      };
    }

    return {
      name: "openai",
      ok: true,
      details: {
        model: config.openai.model,
        apiKeyValid: true,
        voice: config.openai.voice,
      },
    };
  } catch (err) {
    return {
      name: "openai",
      ok: false,
      details: { model: config.openai.model },
      error: `Failed to reach OpenAI API: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}

async function checkPublicUrl(config: PluginConfig): Promise<StatusCheck> {
  const webhookUrl = `${config.publicUrl}/voice/answer`;

  try {
    await assertPublicUrlResolvesToPublicIp(config.publicUrl);

    const res = await fetch(webhookUrl, { method: "GET" });

    const body = await res.text();
    const hasTwiml = body.includes("<Response>") || body.includes("<Connect>");

    return {
      name: "publicUrl",
      ok: res.ok && hasTwiml,
      details: {
        url: config.publicUrl,
        reachable: res.ok,
        webhookPath: "/voice/answer",
        returnsTwiml: hasTwiml,
      },
      error: !res.ok
        ? `Public URL returned ${res.status}`
        : !hasTwiml
          ? "Public URL did not return valid TwiML"
          : undefined,
    };
  } catch (err) {
    return {
      name: "publicUrl",
      ok: false,
      details: {
        url: config.publicUrl,
        reachable: false,
        webhookPath: "/voice/answer",
      },
      error: `Cannot reach public URL: ${err instanceof Error ? err.message : String(err)}. Check your tunnel/reverse proxy.`,
    };
  }
}
