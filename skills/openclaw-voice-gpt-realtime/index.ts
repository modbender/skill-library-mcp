/**
 * openclaw-voice-gpt-realtime
 *
 * Ultra-low-latency AI phone calls powered by OpenAI's Realtime API.
 * Replaces the multi-step STT → LLM → TTS pipeline with a single
 * speech-to-speech model for ~200-300ms response latency.
 */

import { Type, type Static } from "@sinclair/typebox";
import { spawn } from "node:child_process";
import { parseConfig, type PluginConfig } from "./src/config.ts";
import { CallManager } from "./src/call-manager.ts";
import { TwilioClient, type TwilioCallDetails, type TwilioCallEvent } from "./src/twilio-client.ts";
import { VoiceServer } from "./src/server.ts";
import { checkStatus, type StatusResult } from "./src/status.ts";
import {
  MAX_SYSTEM_PROMPT_LENGTH,
  sanitizeSystemPrompt,
  type CallContext,
} from "./src/prompts.ts";
import { assertPublicUrlResolvesToPublicIp } from "./src/public-url.ts";

const MakePhoneCallParams = Type.Object({
  to: Type.String({
    description: "Phone number to call in E.164 format (e.g. +14155551234)",
  }),
  task: Type.String({
    description:
      "Brief one-line summary of the call objective for logging (e.g. 'Dinner reservation at Tony's', " +
      "'Check if they have iPhone 16 in stock'). The real instructions go in systemPrompt.",
  }),
  systemPrompt: Type.String({
    description:
      "Instructions for the AI voice agent that will speak on this phone call. " +
      "You are writing a prompt for a SEPARATE AI — it will read these instructions, then have a real " +
      "phone conversation with a human. The voice agent has no other context, so include everything it needs.\n\n" +
      "IMPORTANT — keep instructions truthful, concise, and useful. " +
      "What to include:\n" +
      "- Who they are and what they want (written in second person)\n" +
      "- All relevant details: names, dates, times, quantities, preferences, budget, etc.\n" +
      "- What to ask about or what info to gather\n" +
      "- Fallback preferences (e.g. 'if Friday doesn't work, try Saturday')\n" +
      "- Only the minimum personal info needed for this call\n" +
      "- Tone guidance — natural and polite, but never deceptive\n\n" +
      "GOOD example:\n" +
      "\"You're calling Tony's Pizza to make a reservation. You want a table for 4 on Friday around 7pm, " +
      "name is Connor. If 7 doesn't work, anytime between 6 and 8 is fine. Ask if they have outdoor " +
      'seating. Keep responses short and friendly."\n\n' +
      "GOOD example:\n" +
      "\"You're calling to ask if they have the iPhone 16 Pro in stock, and if so what colors and how much. " +
      "If they don't have it, ask when they expect it back in stock. You don't need to buy it right now, " +
      'just getting info."\n\n' +
      "GOOD example:\n" +
      "\"You're calling a barbershop to book a haircut for Saturday morning. You're flexible on the exact " +
      "time — anytime before noon works. Just a regular men's cut. If Saturday is booked, check Sunday. " +
      'Name is Connor, phone number is 707-555-1234 if they need it."\n\n' +
      "BAD — too stiff/robotic:\n" +
      '"You are an AI assistant tasked with making a restaurant reservation. Please inquire about ' +
      'availability for a party of four on Friday evening. Request a time slot at 7:00 PM."\n\n' +
      "BAD — too vague:\n" +
      '"Call the restaurant and make a reservation."',
    maxLength: MAX_SYSTEM_PROMPT_LENGTH,
  }),
});

type MakePhoneCallParamsType = Static<typeof MakePhoneCallParams>;

const voiceRealtimeConfigSchema = {
  parse(value: unknown) {
    const raw =
      value && typeof value === "object" && !Array.isArray(value)
        ? (value as Record<string, unknown>)
        : {};
    return parseConfig(raw);
  },
  uiHints: {
    "twilio.accountSid": { label: "Twilio Account SID" },
    "twilio.authToken": { label: "Twilio Auth Token", sensitive: true },
    fromNumber: { label: "From Phone Number", placeholder: "+17077024785" },
    "openai.apiKey": { label: "OpenAI API Key", sensitive: true },
    "openai.model": { label: "Realtime Model" },
    "openai.voice": { label: "AI Voice" },
    "vad.type": { label: "VAD Type", advanced: true },
    "vad.eagerness": { label: "VAD Eagerness", advanced: true },
    publicUrl: {
      label: "Public Webhook URL",
      placeholder: "https://your-domain.com",
    },
    "server.port": { label: "Server Port", advanced: true },
    "server.bind": { label: "Server Bind Address", advanced: true },
    "calls.maxDurationSeconds": {
      label: "Max Call Duration (sec)",
      advanced: true,
    },
    "calls.timeoutSeconds": { label: "Ring Timeout (sec)", advanced: true },
    "calls.enableAmd": { label: "Answering Machine Detection", advanced: true },
    "calls.maxConcurrent": { label: "Max Concurrent Calls", advanced: true },
    "inbound.enabled": { label: "Enable Inbound Calls" },
    "inbound.policy": { label: "Inbound Policy" },
    "inbound.allowFrom": { label: "Allowed Callers (E.164)", advanced: true },
    "inbound.greeting": { label: "Inbound Greeting" },
    "inbound.systemPrompt": { label: "Inbound System Prompt", advanced: true },
    debug: { label: "Debug Mode" },
  },
};

let config: PluginConfig;
let callManager: CallManager;
let twilioClient: TwilioClient;
let server: VoiceServer;
let agentName: string;

interface InitiateCallResult {
  success: boolean;
  callId: string;
  message: string;
  error?: string;
}

interface ActiveCallsResult {
  calls: Array<{
    callId: string;
    to: string;
    status: string;
    task: string;
  }>;
}

interface InspectCallResult {
  success: boolean;
  callSid: string;
  message: string;
  details?: TwilioCallDetails;
  events?: TwilioCallEvent[];
  error?: string;
}

const voiceRealtimePlugin = {
  id: "openclaw-voice-gpt-realtime",
  name: "Voice Calls (OpenAI Realtime)",
  description:
    "Ultra-low-latency AI phone calls powered by OpenAI's Realtime API. " +
    "Single-model speech-to-speech with ~200-300ms latency.",
  configSchema: voiceRealtimeConfigSchema,

  register(api: any) {
    config = voiceRealtimeConfigSchema.parse(api.pluginConfig);
    callManager = new CallManager();
    twilioClient = new TwilioClient(config);
    server = new VoiceServer(config, callManager, twilioClient);

    // Resolve the agent's display name from OpenClaw config
    const agents = api.config?.agents?.list as
      | Array<{ id: string; identity?: { name?: string } }>
      | undefined;
    const defaultAgent = agents?.find((a) => a.id === "main") || agents?.[0];
    agentName = defaultAgent?.identity?.name?.trim() || "";
    server.setAgentName(agentName);

    const logger = api.logger as {
      info: (m: string) => void;
      warn: (m: string) => void;
      error: (m: string) => void;
    };

    callManager.setOnComplete((callId, record) => {
      logger.info(
        `[voice-rt] Call ${callId} completed: ${
          record.outcome?.summary || record.status
        }`
      );
    });

    // Register the make_phone_call tool
    api.registerTool({
      name: "make_phone_call",
      label: "Make Phone Call",
      description:
        "Make an outbound phone call to a real phone number. A voice AI will dial the number and have " +
        "a natural conversation to accomplish whatever you describe. It can handle any " +
        "phone task: reservations, appointments, checking hours/prices/availability, asking questions, etc. " +
        "You MUST write a systemPrompt that tells the voice AI who it is, what it wants, and all the " +
        "details it needs. Keep prompts truthful and policy-compliant (no impersonation or deception). " +
        "The voice AI will call, handle the conversation, " +
        "and report back with the outcome.",
      parameters: MakePhoneCallParams,
      async execute(_toolCallId: string, params: MakePhoneCallParamsType) {
        const result = await initiateCall(params, logger);
        return {
          content: [
            { type: "text" as const, text: JSON.stringify(result, null, 2) },
          ],
          details: result,
        };
      },
    });

    // Gateway method
    api.registerGatewayMethod(
      "voicecall-rt.call",
      async ({
        params,
        respond,
      }: {
        params: Record<string, unknown>;
        respond: (ok: boolean, payload?: unknown) => void;
      }) => {
        try {
          const result = await initiateCall(params as any, logger);
          respond(result.success, result);
        } catch (err) {
          respond(false, {
            error: err instanceof Error ? err.message : String(err),
          });
        }
      }
    );

    api.registerGatewayMethod(
      "voicecall-rt.status",
      async ({
        respond,
      }: {
        respond: (ok: boolean, payload?: unknown) => void;
      }) => {
        try {
          const result = await checkStatus(config, server.isListening());
          respond(true, result);
        } catch (err) {
          respond(false, {
            error: err instanceof Error ? err.message : String(err),
          });
        }
      }
    );

    api.registerGatewayMethod(
      "voicecall-rt.active",
      async ({
        respond,
      }: {
        respond: (ok: boolean, payload?: unknown) => void;
      }) => {
        const active = callManager.getActiveCalls();
        respond(true, {
          calls: active.map((c) => ({
            callId: c.callId,
            to: c.to,
            status: c.status,
            task: c.task,
          })),
        });
      }
    );

    api.registerGatewayMethod(
      "voicecall-rt.inspect",
      async ({
        params,
        respond,
      }: {
        params: Record<string, unknown>;
        respond: (ok: boolean, payload?: unknown) => void;
      }) => {
        const callSid = typeof params.callSid === "string" ? params.callSid : "";
        const result = await inspectCall({ callSid }, logger);
        respond(result.success, result);
      }
    );

    // CLI
    api.registerCli(
      ({ program }: { program: any }) => {
        const root = program
          .command("voicecall-rt")
          .description("Voice call commands (OpenAI Realtime)");

        root
          .command("call")
          .description("Make an outbound phone call")
          .requiredOption(
            "-n, --number <phone>",
            "Phone number to call (E.164)"
          )
          .requiredOption(
            "-t, --task <description>",
            "What to accomplish on the call"
          )
          .action(async (opts: { number: string; task: string }) => {
            try {
              const result = await callGatewayMethodFromCli<InitiateCallResult>(
                "voicecall-rt.call",
                { to: opts.number, task: opts.task },
                45_000
              );
              console.log(JSON.stringify(result, null, 2));
              if (!result.success) process.exitCode = 1;
            } catch (err) {
              process.exitCode = 1;
              console.error(
                `[voice-rt] Failed to initiate call via gateway: ${err instanceof Error ? err.message : String(err)}`
              );
              console.error("[voice-rt] Ensure the gateway is running and reachable (`openclaw gateway --force`).");
            }
          });

        root
          .command("status")
          .description("Check setup status")
          .action(async () => {
            try {
              const result = await callGatewayMethodFromCli<StatusResult>("voicecall-rt.status", {}, 20_000);
              console.log(JSON.stringify(result, null, 2));
              if (result.ready) {
                console.log("\n✓ All checks passed. Ready to make calls.");
              } else {
                console.log("\n✗ Issues found:");
                for (const issue of result.issues) {
                  console.log(`  - ${issue}`);
                }
              }
            } catch (err) {
              process.exitCode = 1;
              console.error(
                `[voice-rt] Failed to fetch status via gateway: ${err instanceof Error ? err.message : String(err)}`
              );
              console.error("[voice-rt] Ensure the gateway is running and reachable (`openclaw gateway --force`).");
            }
          });

        root
          .command("active")
          .description("List active calls")
          .action(async () => {
            try {
              const result = await callGatewayMethodFromCli<ActiveCallsResult>("voicecall-rt.active", {}, 20_000);
              if (result.calls.length === 0) {
                console.log("No active calls.");
              } else {
                for (const call of result.calls) {
                  console.log(`  ${call.callId}: ${call.to} (${call.status})`);
                }
              }
            } catch (err) {
              process.exitCode = 1;
              console.error(
                `[voice-rt] Failed to fetch active calls via gateway: ${err instanceof Error ? err.message : String(err)}`
              );
              console.error("[voice-rt] Ensure the gateway is running and reachable (`openclaw gateway --force`).");
            }
          });

        root
          .command("inspect")
          .description("Inspect a Twilio call by SID")
          .requiredOption("-s, --sid <callSid>", "Twilio Call SID (CA...)")
          .action(async (opts: { sid: string }) => {
            try {
              const result = await callGatewayMethodFromCli<InspectCallResult>(
                "voicecall-rt.inspect",
                { callSid: opts.sid },
                20_000
              );
              console.log(JSON.stringify(result, null, 2));
              if (!result.success) process.exitCode = 1;
            } catch (err) {
              process.exitCode = 1;
              console.error(
                `[voice-rt] Failed to inspect call via gateway: ${err instanceof Error ? err.message : String(err)}`
              );
              console.error("[voice-rt] Ensure the gateway is running and reachable (`openclaw gateway --force`).");
            }
          });
      },
      { commands: ["voicecall-rt"] }
    );

    // Background service
    api.registerService({
      id: "voicecall-rt",
      async start() {
        await assertPublicUrlResolvesToPublicIp(config.publicUrl);
        await server.start();
        logger.info(
          `[voice-rt] Server started on ${config.server.bind}:${config.server.port}`
        );
      },
      async stop() {
        await server.stop();
        logger.info("[voice-rt] Server stopped");
      },
    });
  },
};

async function initiateCall(
  params: { to: string; task: string; systemPrompt?: string },
  logger: { info: (m: string) => void; error: (m: string) => void }
): Promise<{
  success: boolean;
  callId: string;
  message: string;
  error?: string;
}> {
  const { to, task, systemPrompt } = params;

  // Enforce concurrent call limit
  const activeCalls = callManager.getActiveCalls();
  if (activeCalls.length >= config.calls.maxConcurrent) {
    return {
      success: false,
      callId: "",
      message: `Cannot initiate call: ${activeCalls.length} concurrent calls already active (max ${config.calls.maxConcurrent})`,
      error: "MAX_CONCURRENT_CALLS",
    };
  }

  const callId = `call_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  logger.info(`[voice-rt] Initiating call ${callId} to ${to} — task: ${task}`);
  logger.info(
    `[voice-rt] Call settings: timeout=${config.calls.timeoutSeconds}s maxDuration=${config.calls.maxDurationSeconds}s amd=${config.calls.enableAmd}`
  );

  const callContext: CallContext = {
    task,
    direction: "outbound",
    agentName,
    systemPrompt: sanitizeSystemPrompt(systemPrompt),
  };

  server.setCallContext(callId, callContext);
  callManager.createCall(callId, to, config.fromNumber, task);

  try {
    await assertPublicUrlResolvesToPublicIp(config.publicUrl);

    const result = await twilioClient.initiateCall({
      to,
      callId,
      publicUrl: config.publicUrl,
      timeoutSeconds: config.calls.timeoutSeconds,
      enableAmd: config.calls.enableAmd,
      maxDurationSeconds: config.calls.maxDurationSeconds,
    });

    callManager.setCallSid(callId, result.callSid);
    callManager.updateStatus(callId, "ringing");
    logger.info(`[voice-rt] Call ${callId} initiated (SID: ${result.callSid})`);

    return {
      success: true,
      callId,
      message: `Call initiated to ${to}. The AI caller will handle the conversation and report the outcome. Call ID: ${callId}`,
    };
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    callManager.setError(callId, errorMsg);
    callManager.updateStatus(callId, "failed");
    logger.error(`[voice-rt] Failed to initiate call ${callId}: ${errorMsg}`);

    return {
      success: false,
      callId,
      message: `Failed to initiate call to ${to}`,
      error: errorMsg,
    };
  }
}

async function inspectCall(
  params: { callSid: string },
  logger: { info: (m: string) => void; error: (m: string) => void }
): Promise<{
  success: boolean;
  callSid: string;
  message: string;
  details?: TwilioCallDetails;
  events?: TwilioCallEvent[];
  error?: string;
}> {
  const callSid = (params.callSid || "").trim();

  if (!/^CA[a-zA-Z0-9]{32}$/.test(callSid)) {
    return {
      success: false,
      callSid,
      message: "Invalid Call SID",
      error: "Call SID must match format CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    };
  }

  try {
    const details = await twilioClient.getCallDetails(callSid);
    const events = await twilioClient.getCallEvents(callSid);
    logger.info(`[voice-rt] Inspected call ${callSid}: status=${details.status} answeredBy=${details.answeredBy || "n/a"}`);
    return {
      success: true,
      callSid,
      message: `Fetched call details for ${callSid}`,
      details,
      events,
    };
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    logger.error(`[voice-rt] Failed to inspect call ${callSid}: ${errorMsg}`);
    return {
      success: false,
      callSid,
      message: `Failed to fetch call details for ${callSid}`,
      error: errorMsg,
    };
  }
}

export default voiceRealtimePlugin;

async function callGatewayMethodFromCli<T>(
  method: string,
  params: Record<string, unknown>,
  timeoutMs = 20_000
): Promise<T> {
  const cliEntrypoint = process.argv[1];
  if (!cliEntrypoint) {
    throw new Error("Unable to resolve OpenClaw CLI entrypoint for gateway call");
  }

  const args = [
    cliEntrypoint,
    "gateway",
    "call",
    method,
    "--json",
    "--timeout",
    String(timeoutMs),
    "--params",
    JSON.stringify(params),
  ];

  const { stdout, stderr, exitCode } = await runOpenclawCli(args, timeoutMs + 2_000);
  const parsed = parseJsonObject(stdout) ?? parseJsonObject(`${stdout}\n${stderr}`);

  if (exitCode !== 0) {
    const errOut = stderr.trim() || stdout.trim() || `exit code ${exitCode}`;
    throw new Error(`gateway call ${method} failed: ${errOut}`);
  }

  if (!parsed) {
    throw new Error(`gateway call ${method} returned non-JSON output`);
  }

  return parsed as T;
}

function runOpenclawCli(
  args: string[],
  timeoutMs: number
): Promise<{ stdout: string; stderr: string; exitCode: number | null }> {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, args, {
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGTERM");
    }, timeoutMs);

    child.stdout.on("data", (chunk: Buffer | string) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk: Buffer | string) => {
      stderr += chunk.toString();
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });

    child.on("close", (exitCode) => {
      clearTimeout(timer);
      if (timedOut) {
        reject(new Error(`openclaw CLI timed out after ${timeoutMs}ms`));
        return;
      }
      resolve({ stdout, stderr, exitCode });
    });
  });
}

function parseJsonObject(text: string): unknown | null {
  const trimmed = text.trim();
  if (!trimmed) return null;

  try {
    return JSON.parse(trimmed);
  } catch {
    // fall through
  }

  const firstBrace = trimmed.indexOf("{");
  const lastBrace = trimmed.lastIndexOf("}");
  if (firstBrace < 0 || lastBrace <= firstBrace) return null;

  try {
    return JSON.parse(trimmed.slice(firstBrace, lastBrace + 1));
  } catch {
    return null;
  }
}
