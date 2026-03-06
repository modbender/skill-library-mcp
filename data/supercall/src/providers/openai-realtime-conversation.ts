/**
 * OpenAI Realtime Conversation Provider
 *
 * Uses the OpenAI Realtime API for full speech-to-speech conversations.
 * This replaces the separate STT → LLM → TTS pipeline with a single
 * bidirectional audio stream to OpenAI's GPT-4o Realtime model.
 *
 * Benefits:
 * - Much lower latency (~500ms vs ~6s)
 * - Native audio format support (G.711 µ-law)
 * - Built-in VAD for natural turn-taking
 * - Streaming audio output
 */

import WebSocket from "ws";

export interface RealtimeConversationConfig {
  /** OpenAI API key */
  apiKey: string;
  /** Model to use (default: gpt-realtime) */
  model?: string;
  /** Voice for audio output (default: alloy) */
  voice?: string;
  /** System instructions for the AI */
  instructions?: string;
  /** Initial greeting to speak when call connects (triggers AI to speak first) */
  initialGreeting?: string;
  /** Temperature for response randomness (default: 0.8) */
  temperature?: number;
  /** VAD silence duration in ms (default: 800) */
  silenceDurationMs?: number;
  /** VAD threshold 0-1 (default: 0.5) */
  vadThreshold?: number;
}

export interface RealtimeConversationSession {
  /** Connect to the conversation service */
  connect(): Promise<void>;
  /** Send µ-law audio data (8kHz mono) from Twilio */
  sendAudio(audio: Buffer): void;
  /** Set callback for audio output (to send back to Twilio) */
  onAudioOutput(callback: (audio: Buffer) => void): void;
  /** Set callback for transcript of user speech */
  onUserTranscript(callback: (transcript: string) => void): void;
  /** Set callback for transcript of AI response */
  onAssistantTranscript(callback: (transcript: string) => void): void;
  /** Set callback when user starts speaking (for barge-in) */
  onSpeechStart(callback: () => void): void;
  /** Set callback when response is complete */
  onResponseDone(callback: () => void): void;
  /** Set callback when AI decides to hang up (via function call) */
  onHangupRequested(callback: (reason: string) => void): void;
  /** Set callback when AI wants to send DTMF tones (for IVR navigation) */
  onDtmfRequested(callback: (digits: string) => void): void;
  /** Update session instructions (for persona changes) */
  updateInstructions(instructions: string): void;
  /** Close the session */
  close(): void;
  /** Check if session is connected */
  isConnected(): boolean;
}

/**
 * Provider factory for OpenAI Realtime Conversation sessions.
 */
export class OpenAIRealtimeConversationProvider {
  readonly name = "openai-realtime-conversation";
  private config: RealtimeConversationConfig;

  constructor(config: RealtimeConversationConfig) {
    if (!config.apiKey) {
      throw new Error("OpenAI API key required for Realtime Conversation");
    }
    this.config = {
      model: "gpt-realtime",
      voice: "marin",
      temperature: 0.8,
      silenceDurationMs: 800,
      vadThreshold: 0.5,
      ...config,
    };
  }

  /**
   * Create a new realtime conversation session.
   */
  createSession(options?: { instructions?: string; initialGreeting?: string } | string): RealtimeConversationSession {
    // Support legacy string argument for backwards compatibility
    const opts = typeof options === 'string' 
      ? { instructions: options } 
      : (options ?? {});
    
    return new OpenAIRealtimeConversationSession({
      ...this.config,
      instructions: opts.instructions ?? this.config.instructions,
      initialGreeting: opts.initialGreeting ?? this.config.initialGreeting,
    });
  }
}

/**
 * WebSocket-based session for real-time speech-to-speech conversations.
 */
class OpenAIRealtimeConversationSession implements RealtimeConversationSession {
  private ws: WebSocket | null = null;
  private connected = false;
  private closed = false;
  private config: Required<RealtimeConversationConfig>;

  private onAudioOutputCallback: ((audio: Buffer) => void) | null = null;
  private onUserTranscriptCallback: ((transcript: string) => void) | null = null;
  private onAssistantTranscriptCallback: ((transcript: string) => void) | null = null;
  private onSpeechStartCallback: (() => void) | null = null;
  private onResponseDoneCallback: (() => void) | null = null;
  private onHangupRequestedCallback: ((reason: string) => void) | null = null;
  private onDtmfRequestedCallback: ((digits: string) => void) | null = null;

  /** Accumulator for streaming transcription deltas (gpt-4o-transcribe models) */
  private transcriptDeltas: Map<string, string> = new Map();

  constructor(config: RealtimeConversationConfig) {
    // Add current date to instructions so AI knows what day it is
    const currentDate = new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    const baseInstructions = config.instructions ?? "You are a helpful voice assistant. Be concise.";

    const ivrGuidance = `

## CRITICAL: Phone Menu (IVR) Navigation

You have a tool called send_dtmf. It is THE ONLY WAY to press buttons on a phone. Saying a number out loud does NOT press it — the phone system cannot hear your voice as a button press.

When you hear a phone menu that says "press X for Y":
1. Decide which option matches your goal
2. Call send_dtmf with the digits immediately
3. Do NOT narrate what you're doing. Do NOT say "I'm pressing 2" or "I've selected option 1". Just silently call send_dtmf.

When the system asks you to SPEAK (e.g. "tell me what you need", "say yes or no", "how can I help you"):
- Just talk to it normally. Do NOT use send_dtmf for voice-based menus.
- Speak clearly and briefly to answer what it's asking.

Examples:
- You hear "press 1 for X, press 2 for Y" → call send_dtmf("1") silently
- You hear "tell me what I can help you with" → speak your request out loud
- You hear "are you calling from a cell phone?" → say "no" out loud
- You hear "enter your account number followed by pound" → call send_dtmf("1234567890#")

Rules:
- Act FAST. Phone menus have short timeouts. Call send_dtmf as soon as you know the right option.
- NEVER narrate your actions on the phone. The other end can hear you. Stay silent except when the system expects speech.
- ALWAYS stay in English. If offered "para español" or other languages, ignore it and wait for the English menu. Never press buttons to switch languages.
- If a menu repeats, you missed your window. Call send_dtmf immediately on the second pass.
- If the system says "invalid option", listen for the menu again and retry with send_dtmf.
- If placed on hold with music, wait silently.
- When transferred to a human, resume normal conversation.`;

    const instructionsWithDate = `Today is ${currentDate}.\n\n${ivrGuidance}\n\n${baseInstructions}`;
    
    this.config = {
      apiKey: config.apiKey,
      model: config.model ?? "gpt-realtime",
      voice: config.voice ?? "marin",
      instructions: instructionsWithDate,
      initialGreeting: config.initialGreeting,
      temperature: config.temperature ?? 0.8,
      silenceDurationMs: config.silenceDurationMs ?? 800,
      vadThreshold: config.vadThreshold ?? 0.5,
    };
  }

  async connect(): Promise<void> {
    this.closed = false;
    return this.doConnect();
  }

  private async doConnect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `wss://api.openai.com/v1/realtime?model=${this.config.model}&temperature=${this.config.temperature}`;

      this.ws = new WebSocket(url, {
        headers: {
          Authorization: `Bearer ${this.config.apiKey}`,
        },
      });

      this.ws.on("open", () => {
        console.log("[RealtimeConversation] WebSocket connected");
        this.connected = true;

        // Send session configuration after short delay for stability
        setTimeout(() => this.sendSessionUpdate(), 250);
        resolve();
      });

      this.ws.on("message", (data: Buffer) => {
        try {
          const event = JSON.parse(data.toString());
          this.handleEvent(event);
        } catch (e) {
          console.error("[RealtimeConversation] Failed to parse event:", e);
        }
      });

      this.ws.on("error", (error) => {
        console.error("[RealtimeConversation] WebSocket error:", error);
        if (!this.connected) reject(error);
      });

      this.ws.on("close", (code, reason) => {
        console.log(
          `[RealtimeConversation] WebSocket closed (code: ${code}, reason: ${reason?.toString() || "none"})`,
        );
        this.connected = false;
      });

      setTimeout(() => {
        if (!this.connected) {
          reject(new Error("Realtime Conversation connection timeout"));
        }
      }, 10000);
    });
  }

  private sendSessionUpdate(): void {
    const sessionUpdate = {
      type: "session.update",
      session: {
        type: "realtime",
        model: this.config.model,
        output_modalities: ["audio"],
        audio: {
          input: {
            format: { type: "audio/pcmu" },
            turn_detection: {
              type: "semantic_vad",
              eagerness: "high",
              create_response: true,
              interrupt_response: true,
            },
            transcription: {
              model: "gpt-4o-mini-transcribe",
            },
          },
          output: {
            format: { type: "audio/pcmu" },
            voice: this.config.voice,
          },
        },
        instructions: this.config.instructions,
        tools: [
          {
            type: "function",
            name: "hangup",
            description: "End the phone call. Use this when: (1) the goal has been achieved, (2) the conversation has naturally concluded, (3) the other party has said goodbye, or (4) the other party has firmly refused twice. Always say goodbye before hanging up.",
            parameters: {
              type: "object",
              properties: {
                reason: {
                  type: "string",
                  description: "Brief reason for ending the call (e.g., 'goal achieved', 'goodbye', 'refused')",
                },
              },
              required: ["reason"],
            },
          },
          {
            type: "function",
            name: "send_dtmf",
            description: "Press a button on the phone keypad. You MUST call this function to interact with automated phone menus. When you hear 'press 1 for X', call send_dtmf with digits='1'. Speaking the number out loud does NOT press it — only this function does. Call it immediately when you know which option to pick.",
            parameters: {
              type: "object",
              properties: {
                digits: {
                  type: "string",
                  description: "Digits to send (e.g. '1', '2', '411', '1234567890#')",
                },
              },
              required: ["digits"],
            },
          },
        ],
        tool_choice: "auto",
      },
    };

    console.log("[RealtimeConversation] Sending session update (with hangup + send_dtmf tools + transcription)");
    this.sendEvent(sessionUpdate);
  }

  private handleEvent(event: {
    type: string;
    delta?: string;
    transcript?: string;
    error?: unknown;
    [key: string]: unknown;
  }): void {
    switch (event.type) {
      case "session.created":
        console.log("[RealtimeConversation] Session created");
        break;

      case "session.updated":
        // Log the session config to verify tools were registered
        const sessionData = event.session as { tools?: unknown[] } | undefined;
        console.log(`[RealtimeConversation] Session updated - tools registered: ${sessionData?.tools?.length ?? 0}`);
        // Trigger initial greeting if configured
        if (this.config.initialGreeting) {
          console.log("[RealtimeConversation] Triggering initial greeting...");
          this.triggerInitialGreeting();
        }
        break;

      case "input_audio_buffer.speech_started":
        console.log("[RealtimeConversation] User started speaking");
        console.log(`[LATENCY:REALTIME] speech_started at ${new Date().toISOString()}`);
        this.onSpeechStartCallback?.();
        break;

      case "input_audio_buffer.speech_stopped":
        console.log(`[LATENCY:REALTIME] speech_stopped at ${new Date().toISOString()}`);
        console.log("[RealtimeConversation] User stopped speaking");
        break;

      case "input_audio_buffer.committed":
        console.log("[RealtimeConversation] Audio buffer committed");
        break;

      case "response.output_audio.delta":
        // Stream audio output back to Twilio
        if (event.delta) {
          const audioBuffer = Buffer.from(event.delta as string, "base64");
          this.onAudioOutputCallback?.(audioBuffer);
        }
        break;

      case "response.output_audio.done":
        console.log(`[LATENCY:REALTIME] audio output done at ${new Date().toISOString()}`);
        break;

      case "response.output_audio_transcript.delta":
        // Partial transcript of AI response (for logging/display)
        break;

      case "response.output_audio_transcript.done":
        if (event.transcript) {
          console.log(`[RealtimeConversation] AI said: "${event.transcript}"`);
          this.onAssistantTranscriptCallback?.(event.transcript as string);
        }
        break;

      case "conversation.item.input_audio_transcription.delta":
        // Streaming transcription delta (gpt-4o-transcribe models)
        if (event.delta) {
          const itemId = (event.item_id as string) ?? "unknown";
          const existing = this.transcriptDeltas.get(itemId) ?? "";
          this.transcriptDeltas.set(itemId, existing + event.delta);
        }
        break;

      case "conversation.item.input_audio_transcription.completed":
        if (event.transcript) {
          console.log(`[RealtimeConversation] User said: "${event.transcript}"`);
          this.onUserTranscriptCallback?.(event.transcript as string);
        } else {
          // For streaming models, transcript may come only via deltas
          const itemId = (event.item_id as string) ?? "unknown";
          const accumulated = this.transcriptDeltas.get(itemId);
          if (accumulated) {
            console.log(`[RealtimeConversation] User said (from deltas): "${accumulated}"`);
            this.onUserTranscriptCallback?.(accumulated);
            this.transcriptDeltas.delete(itemId);
          }
        }
        break;

      case "response.created":
        console.log(`[LATENCY:REALTIME] response.created at ${new Date().toISOString()}`);
        break;

      case "response.done":
        console.log("[RealtimeConversation] Response complete");
        // Check if response contains function calls
        const response = event.response as { output?: Array<{ type?: string; name?: string; call_id?: string; arguments?: string }> } | undefined;
        if (response?.output) {
          for (const item of response.output) {
            if (item.type === "function_call") {
              console.log(`[RealtimeConversation] Function call in response.done: ${item.name}`);
              this.processFunctionCall(item.name, item.call_id, item.arguments);
            }
          }
        }
        this.onResponseDoneCallback?.();
        break;

      case "response.function_call_arguments.done":
      case "response.output_item.done":
        // Handled in response.done to avoid triple-firing
        break;

      case "rate_limits.updated":
        // Rate limit info, log if needed
        break;

      case "error":
        console.error("[RealtimeConversation] Error:", JSON.stringify(event.error, null, 2));
        console.error("[RealtimeConversation] Full error event:", JSON.stringify(event, null, 2));
        break;

      default:
        // Log other events at debug level
        if (event.type.includes("delta")) {
          // Skip logging frequent delta events
        } else {
          console.log(`[RealtimeConversation] Event: ${event.type}`);
          // Debug: log any function-related events
          if (event.type.includes("function") || event.type.includes("tool")) {
            console.log(`[RealtimeConversation] Function event detail:`, JSON.stringify(event, null, 2));
          }
        }
    }
  }

  private sendEvent(event: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(event));
    }
  }

  /**
   * Process a function call (shared logic).
   */
  private processFunctionCall(
    functionName: string | undefined,
    callId: string | undefined,
    args: string | undefined
  ): void {
    if (functionName === "hangup") {
      let reason = "unknown";
      try {
        const parsed = JSON.parse(args || "{}");
        reason = parsed.reason || "goal achieved";
      } catch {
        reason = "goal achieved";
      }

      console.log(`[RealtimeConversation] AI requested hangup: ${reason}`);

      // Send function result to acknowledge the call
      if (callId) {
        this.sendEvent({
          type: "conversation.item.create",
          item: {
            type: "function_call_output",
            call_id: callId,
            output: JSON.stringify({ success: true, message: "Ending call..." }),
          },
        });
      }

      // Trigger hangup immediately - MediaStreamHandler uses Twilio marks
      // to wait for audio playback to finish before actually ending the call
      this.onHangupRequestedCallback?.(reason);
    } else if (functionName === "send_dtmf") {
      let digits = "";
      try {
        const parsed = JSON.parse(args || "{}");
        digits = parsed.digits || "";
      } catch {
        digits = "";
      }

      console.log(`[RealtimeConversation] AI sending DTMF: ${digits}`);

      // Acknowledge the function call so AI continues listening
      if (callId) {
        this.sendEvent({
          type: "conversation.item.create",
          item: {
            type: "function_call_output",
            call_id: callId,
            output: JSON.stringify({ success: true, digits_sent: digits }),
          },
        });
      }

      this.onDtmfRequestedCallback?.(digits);
    } else {
      console.log(`[RealtimeConversation] Unknown function: ${functionName}`);
    }
  }

  /**
   * Trigger the AI to speak the initial greeting.
   * This creates a user message asking the AI to deliver its opening line,
   * then triggers a response.
   */
  private triggerInitialGreeting(): void {
    if (!this.config.initialGreeting) return;
    
    // Add a system-like prompt as a user message to trigger the greeting
    this.sendEvent({
      type: "conversation.item.create",
      item: {
        type: "message",
        role: "user",
        content: [
          {
            type: "input_text",
            text: `[SYSTEM: The call just connected. Deliver your opening line now. Say exactly: "${this.config.initialGreeting}"]`,
          },
        ],
      },
    });

    // Trigger the AI to respond
    setTimeout(() => {
      this.sendEvent({
        type: "response.create",
      });
    }, 100);
  }

  sendAudio(muLawData: Buffer): void {
    if (!this.connected) return;
    this.sendEvent({
      type: "input_audio_buffer.append",
      audio: muLawData.toString("base64"),
    });
  }

  onAudioOutput(callback: (audio: Buffer) => void): void {
    this.onAudioOutputCallback = callback;
  }

  onUserTranscript(callback: (transcript: string) => void): void {
    this.onUserTranscriptCallback = callback;
  }

  onAssistantTranscript(callback: (transcript: string) => void): void {
    this.onAssistantTranscriptCallback = callback;
  }

  onSpeechStart(callback: () => void): void {
    this.onSpeechStartCallback = callback;
  }

  onResponseDone(callback: () => void): void {
    this.onResponseDoneCallback = callback;
  }

  onHangupRequested(callback: (reason: string) => void): void {
    this.onHangupRequestedCallback = callback;
  }

  onDtmfRequested(callback: (digits: string) => void): void {
    this.onDtmfRequestedCallback = callback;
  }

  updateInstructions(instructions: string): void {
    this.config.instructions = instructions;
    if (this.connected) {
      this.sendSessionUpdate();
    }
  }

  close(): void {
    this.closed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}
