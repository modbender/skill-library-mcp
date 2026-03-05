import WebSocket from "ws";
import type { PluginConfig } from "./config.ts";
import type { CallManager } from "./call-manager.ts";
import type { TwilioClient } from "./twilio-client.ts";
import { DebugRecorder } from "./debug.ts";
import { generateDtmfTone } from "./dtmf.ts";
import { getSystemPrompt, type CallContext } from "./prompts.ts";

const OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime";

export class RealtimeBridge {
  private twilioWs: WebSocket;
  private openaiWs: WebSocket | null = null;
  private config: PluginConfig;
  private callManager: CallManager;
  private twilioClient: TwilioClient;
  private callId: string;
  private callContext: CallContext;
  private debug: DebugRecorder;
  private streamSid: string | null = null;
  private closed = false;

  constructor(
    twilioWs: WebSocket,
    config: PluginConfig,
    callManager: CallManager,
    twilioClient: TwilioClient,
    callId: string,
    callContext: CallContext
  ) {
    this.twilioWs = twilioWs;
    this.config = config;
    this.callManager = callManager;
    this.twilioClient = twilioClient;
    this.callId = callId;
    this.callContext = callContext;
    this.debug = new DebugRecorder(callId, config.debug);

    this.setupTwilioHandlers();
  }

  private setupTwilioHandlers(): void {
    this.twilioWs.on("message", (data) => {
      try {
        const msg = JSON.parse(data.toString());
        this.handleTwilioMessage(msg);
      } catch (err) {
        this.debug.logError("Failed to parse Twilio message", err);
      }
    });

    this.twilioWs.on("close", (code, reason) => {
      this.debug.logTwilio("close", `code=${code} reason=${reason}`);
      this.close();
    });

    this.twilioWs.on("error", (err) => {
      this.debug.logError("Twilio WebSocket error", err);
      this.close();
    });
  }

  private handleTwilioMessage(msg: TwilioStreamMessage): void {
    switch (msg.event) {
      case "connected":
        this.debug.logTwilio("connected");
        break;

      case "start":
        this.streamSid = msg.start!.streamSid;
        this.callManager.setStreamSid(this.callId, this.streamSid);
        this.debug.logTwilio("start", `streamSid=${this.streamSid} callSid=${msg.start!.callSid}`);
        this.connectToOpenAI();
        break;

      case "media":
        if (msg.media?.payload && this.openaiWs?.readyState === WebSocket.OPEN) {
          this.debug.recordInbound(msg.media.payload);
          // Forward audio to OpenAI Realtime
          this.openaiWs.send(
            JSON.stringify({
              type: "input_audio_buffer.append",
              audio: msg.media.payload,
            })
          );
        }
        break;

      case "stop":
        this.debug.logTwilio("stop");
        this.close();
        break;

      case "mark":
        this.debug.logTwilio("mark", msg.mark?.name);
        break;
    }
  }

  private connectToOpenAI(): void {
    const url = `${OPENAI_REALTIME_URL}?model=${this.config.openai.model}`;

    this.openaiWs = new WebSocket(url, {
      headers: {
        Authorization: `Bearer ${this.config.openai.apiKey}`,
        "OpenAI-Beta": "realtime=v1",
      },
    });

    this.openaiWs.on("open", () => {
      this.debug.logOpenAI("connected");
      this.configureSession();
    });

    this.openaiWs.on("message", (data) => {
      try {
        const event = JSON.parse(data.toString());
        this.handleOpenAIEvent(event);
      } catch (err) {
        this.debug.logError("Failed to parse OpenAI message", err);
      }
    });

    this.openaiWs.on("close", (code, reason) => {
      this.debug.logOpenAI("close", `code=${code} reason=${reason}`);
      this.close();
    });

    this.openaiWs.on("error", (err) => {
      this.debug.logError("OpenAI WebSocket error", err);
      this.close();
    });
  }

  private configureSession(): void {
    const systemPrompt = getSystemPrompt(this.callContext);

    // Always log the system prompt for debugging prompt issues
    console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m direction=${this.callContext.direction} model=${this.config.openai.model} voice=${this.config.openai.voice}`);
    console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m callContext.task=${this.callContext.task}`);
    if (this.callContext.systemPrompt) {
      console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m callContext.systemPrompt=${this.callContext.systemPrompt.slice(0, 200)}${this.callContext.systemPrompt.length > 200 ? "..." : ""}`);
    }
    if (this.callContext.agentName) {
      console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m agentName=${this.callContext.agentName}`);
    }
    console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m final instructions (${systemPrompt.length} chars):\n${systemPrompt}`);

    const sessionConfig: OpenAISessionConfig = {
      type: "session.update",
      session: {
        modalities: ["text", "audio"],
        instructions: systemPrompt,
        voice: this.config.openai.voice,
        input_audio_format: "g711_ulaw",
        output_audio_format: "g711_ulaw",
        input_audio_transcription: {
          model: "gpt-4o-transcribe",
        },
        turn_detection: {
          type: this.config.vad.type as "semantic_vad" | "server_vad",
          eagerness: this.config.vad.eagerness,
          silence_duration_ms: 500,
        },
        tools: [
          {
            type: "function",
            name: "send_dtmf",
            description:
              "Press a phone key to navigate an IVR menu or enter a number. Use this when you hear an automated phone menu asking you to press a key.",
            parameters: {
              type: "object",
              properties: {
                digits: {
                  type: "string",
                  description: "The digits to press (0-9, *, #). Can be multiple digits like '1234'.",
                },
              },
              required: ["digits"],
            },
          },
          {
            type: "function",
            name: "end_call",
            description:
              "Hang up the phone call. Use this when the conversation is complete, when you reach voicemail, or when asked to call back.",
            parameters: {
              type: "object",
              properties: {
                reason: {
                  type: "string",
                  description: "Why the call is ending (e.g. 'completed', 'voicemail', 'asked_to_call_back')",
                },
              },
              required: ["reason"],
            },
          },
          {
            type: "function",
            name: "report_outcome",
            description:
              "Report the structured result of the phone call. Call this before ending the call to record what was accomplished.",
            parameters: {
              type: "object",
              properties: {
                success: {
                  type: "boolean",
                  description: "Whether the call objective was achieved",
                },
                summary: {
                  type: "string",
                  description: "Brief summary of the call outcome",
                },
                details: {
                  type: "object",
                  description:
                    "Structured details (e.g. confirmation number, reservation time, price quotes)",
                  additionalProperties: true,
                },
              },
              required: ["success", "summary"],
            },
          },
        ],
      },
    };

    // For semantic_vad, remove silence_duration_ms (only used for server_vad)
    if (this.config.vad.type === "semantic_vad") {
      delete (sessionConfig.session.turn_detection as Record<string, unknown>).silence_duration_ms;
    }

    const sessionPayload = JSON.stringify(sessionConfig);
    this.openaiWs!.send(sessionPayload);
    this.debug.logOpenAI("session.update", "configured");
    if (this.config.debug) {
      console.log(`\x1b[35m[prompt]\x1b[0m \x1b[2m${this.callId}\x1b[0m full session.update payload:\n${JSON.stringify(sessionConfig, null, 2)}`);
    }

    if (this.callContext.direction === "inbound" && this.callContext.greeting) {
      // Inbound: speak the greeting immediately
      this.openaiWs!.send(
        JSON.stringify({
          type: "response.create",
          response: {
            modalities: ["text", "audio"],
            instructions: `Say exactly this greeting to the caller: "${this.callContext.greeting}". Say it naturally and warmly, then wait for their response.`,
          },
        })
      );
    }
    // Outbound: do NOT send response.create — "listen first" behavior
    // The model will wait for the callee's greeting via VAD
  }

  private handleOpenAIEvent(event: OpenAIEvent): void {
    switch (event.type) {
      case "session.created":
        this.debug.logOpenAI("session.created", `id=${event.session?.id}`);
        break;

      case "session.updated":
        this.debug.logOpenAI("session.updated");
        break;

      case "input_audio_buffer.speech_started":
        this.debug.logOpenAI("input_audio_buffer.speech_started");
        break;

      case "input_audio_buffer.speech_stopped":
        this.debug.logOpenAI("input_audio_buffer.speech_stopped");
        break;

      case "response.audio.delta":
        if (event.delta && this.twilioWs.readyState === WebSocket.OPEN) {
          this.debug.recordOutbound(event.delta);
          this.twilioWs.send(
            JSON.stringify({
              event: "media",
              streamSid: this.streamSid,
              media: { payload: event.delta },
            })
          );
        }
        break;

      case "response.audio.done":
        this.debug.logOpenAI("response.audio.done");
        break;

      case "response.audio_transcript.delta":
        // Partial AI transcript — just log in debug
        break;

      case "response.audio_transcript.done":
        if (event.transcript) {
          this.debug.logOpenAI("response.audio_transcript.done", event.transcript);
          this.callManager.addTranscript(this.callId, "assistant", event.transcript);
        }
        break;

      case "conversation.item.input_audio_transcription.completed":
        if (event.transcript) {
          const role = this.callContext.direction === "inbound" ? "caller" : "callee";
          this.debug.logOpenAI("input_transcription", event.transcript);
          this.callManager.addTranscript(this.callId, role, event.transcript);
        }
        break;

      case "response.function_call_arguments.done":
        this.handleFunctionCall(event);
        break;

      case "response.done":
        this.debug.logOpenAI("response.done");
        break;

      case "response.created":
        this.debug.logOpenAI("response.created");
        // Clear Twilio's audio buffer for barge-in support
        if (this.twilioWs.readyState === WebSocket.OPEN) {
          this.twilioWs.send(
            JSON.stringify({
              event: "clear",
              streamSid: this.streamSid,
            })
          );
        }
        break;

      case "error":
        this.debug.logError("OpenAI error", event.error);
        break;

      default:
        // Log unhandled events in debug mode
        if (this.config.debug) {
          this.debug.logOpenAI(event.type);
        }
    }
  }

  private async handleFunctionCall(event: OpenAIEvent): Promise<void> {
    const fnName = event.name;
    const callId = event.call_id;

    let args: Record<string, unknown>;
    try {
      args = JSON.parse(event.arguments || "{}");
    } catch {
      args = {};
    }

    this.debug.logTool(fnName!, JSON.stringify(args));

    let result: string;

    switch (fnName) {
      case "send_dtmf":
        result = await this.handleSendDtmf(args.digits as string);
        break;

      case "end_call":
        result = await this.handleEndCall(args.reason as string);
        break;

      case "report_outcome":
        result = this.handleReportOutcome(args as { success: boolean; summary: string; details?: Record<string, unknown> });
        break;

      default:
        result = `Unknown function: ${fnName}`;
    }

    // Send function result back to OpenAI
    if (this.openaiWs?.readyState === WebSocket.OPEN) {
      this.openaiWs.send(
        JSON.stringify({
          type: "conversation.item.create",
          item: {
            type: "function_call_output",
            call_id: callId,
            output: result,
          },
        })
      );

      // Trigger a new response after function result
      this.openaiWs.send(JSON.stringify({ type: "response.create" }));
    }
  }

  private async handleSendDtmf(digits: string): Promise<string> {
    if (!digits || !/^[0-9*#A-Da-d]+$/.test(digits)) {
      return "Invalid DTMF digits. Use 0-9, *, #, A-D.";
    }

    for (const digit of digits) {
      const tone = generateDtmfTone(digit);
      if (this.twilioWs.readyState === WebSocket.OPEN) {
        this.twilioWs.send(
          JSON.stringify({
            event: "media",
            streamSid: this.streamSid,
            media: { payload: tone },
          })
        );
      }
      // Small gap between tones
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    this.callManager.addTranscript(this.callId, "system", `[DTMF: ${digits}]`);
    return `Pressed ${digits}`;
  }

  private async handleEndCall(reason: string): Promise<string> {
    this.debug.logTool("end_call", reason);
    this.callManager.addTranscript(this.callId, "system", `[Call ended: ${reason}]`);

    // Give a moment for any final audio to play
    setTimeout(async () => {
      const record = this.callManager.getByCallId(this.callId);
      if (record?.callSid) {
        try {
          await this.twilioClient.hangup(record.callSid);
        } catch (err) {
          this.debug.logError("Failed to hangup via Twilio", err);
        }
      }
      this.close();
    }, 1500);

    return `Call will end. Reason: ${reason}`;
  }

  private handleReportOutcome(args: { success: boolean; summary: string; details?: Record<string, unknown> }): string {
    this.callManager.setOutcome(this.callId, {
      success: args.success,
      summary: args.summary,
      details: args.details,
    });

    this.debug.logTool("report_outcome", JSON.stringify(args));
    return "Outcome recorded.";
  }

  async close(): Promise<void> {
    if (this.closed) return;
    this.closed = true;

    this.debug.logTwilio("bridge_closing");

    // Close OpenAI connection
    if (this.openaiWs && this.openaiWs.readyState === WebSocket.OPEN) {
      this.openaiWs.close();
    }

    // Close Twilio connection
    if (this.twilioWs.readyState === WebSocket.OPEN) {
      this.twilioWs.close();
    }

    // Finalize debug recordings
    const record = this.callManager.getByCallId(this.callId);
    await this.debug.finalize(record?.transcript || []);

    // Update call status if not already completed
    if (record && record.status === "in-progress") {
      this.callManager.updateStatus(this.callId, "completed");
    }
  }
}

// TypeScript interfaces for Twilio stream messages
interface TwilioStreamMessage {
  event: "connected" | "start" | "media" | "stop" | "mark";
  start?: {
    streamSid: string;
    callSid: string;
    accountSid: string;
    tracks: string[];
    customParameters: Record<string, string>;
  };
  media?: {
    track: string;
    chunk: string;
    timestamp: string;
    payload: string;
  };
  mark?: {
    name: string;
  };
}

// OpenAI Realtime API types
interface OpenAISessionConfig {
  type: "session.update";
  session: {
    modalities: string[];
    instructions: string;
    voice: string;
    input_audio_format: string;
    output_audio_format: string;
    input_audio_transcription: { model: string };
    turn_detection: {
      type: "semantic_vad" | "server_vad";
      eagerness?: string;
      silence_duration_ms?: number;
    };
    tools: Array<{
      type: "function";
      name: string;
      description: string;
      parameters: Record<string, unknown>;
    }>;
  };
}

interface OpenAIEvent {
  type: string;
  session?: { id: string };
  delta?: string;
  transcript?: string;
  name?: string;
  call_id?: string;
  arguments?: string;
  error?: { type: string; message: string };
  [key: string]: unknown;
}
