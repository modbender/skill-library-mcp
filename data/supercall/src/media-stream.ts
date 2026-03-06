/**
 * Media Stream Handler
 *
 * Handles bidirectional audio streaming between Twilio and OpenAI Realtime
 * Conversation. Full realtime only (speech-to-speech).
 */

import type { IncomingMessage } from "node:http";
import type { Duplex } from "node:stream";

import { WebSocket, WebSocketServer } from "ws";

import type {
  OpenAIRealtimeConversationProvider,
  RealtimeConversationSession,
} from "./providers/openai-realtime-conversation.js";
import { generateDtmfAudio, chunkDtmfAudio } from "./dtmf.js";

export interface MediaStreamConfig {
  /** Conversation provider for realtime speech-to-speech */
  conversationProvider: OpenAIRealtimeConversationProvider;
  /** Get instructions for a given call */
  getInstructionsForCall?: (callId: string) => string;
  /** Get initial greeting for a given call */
  getInitialGreetingForCall?: (callId: string) => string | undefined;
  /** User transcript callback */
  onUserTranscript?: (callId: string, transcript: string) => void;
  /** Assistant transcript callback */
  onAssistantTranscript?: (callId: string, transcript: string) => void;
  /** Stream connect callback */
  onConnect?: (callId: string, streamSid: string) => void;
  /** Stream disconnect callback */
  onDisconnect?: (callId: string) => void;
  /** Hangup requested callback (AI decided to end the call) */
  onHangupRequested?: (callId: string, reason: string) => void;
}

interface StreamSession {
  callId: string;
  streamSid: string;
  ws: WebSocket;
  conversationSession: RealtimeConversationSession;
  pendingHangup?: { reason: string; resolve: () => void };
  pendingDtmf?: { digits: string; resolve: () => void };
}

/**
 * Manages WebSocket connections for Twilio media streams.
 */
export class MediaStreamHandler {
  private wss: WebSocketServer | null = null;
  private sessions = new Map<string, StreamSession>();
  private config: MediaStreamConfig;
  private wsCounter = 0;

  constructor(config: MediaStreamConfig) {
    this.config = config;
  }

  /**
   * Handle WebSocket upgrade for media stream connections.
   */
  handleUpgrade(request: IncomingMessage, socket: Duplex, head: Buffer): void {
    if (!this.wss) {
      this.wss = new WebSocketServer({ noServer: true });
      this.wss.on("connection", (ws, req) => this.handleConnection(ws, req));
    }

    this.wss.handleUpgrade(request, socket, head, (ws) => {
      this.wss?.emit("connection", ws, request);
    });
  }

  /**
   * Handle new WebSocket connection from Twilio.
   */
  private async handleConnection(
    ws: WebSocket,
    _request: IncomingMessage,
  ): Promise<void> {
    const wsId = ++this.wsCounter;
    console.log(`[MediaStream] New WebSocket connection #${wsId}`);
    let session: StreamSession | null = null;

    ws.on("message", async (data: Buffer) => {
      try {
        const message = JSON.parse(data.toString()) as TwilioMediaMessage;

        switch (message.event) {
          case "connected":
            console.log(`[MediaStream] Twilio connected (ws #${wsId})`);
            break;

          case "start":
            session = await this.handleStart(ws, message);
            break;

          case "media":
            if (session && message.media?.payload) {
              const audioBuffer = Buffer.from(message.media.payload, "base64");
              session.conversationSession.sendAudio(audioBuffer);
            }
            break;

          case "stop":
            console.log(`[MediaStream] Stop event on ws #${wsId} (hasSession: ${!!session})`);
            if (session) {
              this.handleStop(session);
              session = null;
            }
            break;

          case "mark":
            // Twilio sends mark back when audio playback completes
            console.log(`[MediaStream] Mark received: ${JSON.stringify(message.mark)} for session ${session?.callId || 'unknown'}`);
            if (session?.pendingHangup && message.mark?.name === "hangup") {
              console.log(`[MediaStream] ✅ Hangup mark matched! Audio finished for ${session.callId}`);
              session.pendingHangup.resolve();
            } else if (session?.pendingDtmf && message.mark?.name === "dtmf") {
              console.log(`[MediaStream] ✅ DTMF mark matched! Audio finished for ${session.callId}`);
              session.pendingDtmf.resolve();
            } else if (session?.pendingHangup) {
              console.log(`[MediaStream] Mark name mismatch: expected 'hangup', got '${message.mark?.name}'`);
            }
            break;
        }
      } catch (error) {
        console.error("[MediaStream] Error processing message:", error);
      }
    });

    ws.on("close", (code, reason) => {
      console.log(`[MediaStream] WebSocket close event (code: ${code}, reason: ${reason?.toString() || 'none'}, hasSession: ${!!session})`);
      if (session) {
        this.handleStop(session);
        session = null;
      }
    });

    ws.on("error", (error) => {
      console.error("[MediaStream] WebSocket error:", error);
    });
  }

  /**
   * Handle stream start event.
   */
  private async handleStart(
    ws: WebSocket,
    message: TwilioMediaMessage,
  ): Promise<StreamSession | null> {
    const streamSid = message.streamSid || "";
    const callSid = message.start?.callSid || "";

    // Guard against duplicate Twilio WebSocket connections for the same call.
    // Twilio sometimes sends two WS upgrades; the second would create a
    // competing OpenAI session and both end up dying.
    for (const existing of this.sessions.values()) {
      if (existing.callId === callSid) {
        console.log(`[MediaStream] Ignoring duplicate stream ${streamSid} for call ${callSid} (already have ${existing.streamSid})`);
        ws.close();
        return null;
      }
    }

    console.log(`[MediaStream] Stream started: ${streamSid} (call: ${callSid})`);

    const instructions = this.config.getInstructionsForCall?.(callSid);
    const initialGreeting = this.config.getInitialGreetingForCall?.(callSid);
    const conversationSession = this.config.conversationProvider.createSession({
      instructions,
      initialGreeting,
    });

    // Create session object BEFORE setting up callbacks that reference it
    const session: StreamSession = {
      callId: callSid,
      streamSid,
      ws,
      conversationSession,
    };

    // Stream audio output back to Twilio
    conversationSession.onAudioOutput((audio) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            event: "media",
            streamSid,
            media: { payload: audio.toString("base64") },
          }),
        );
      }
    });

    conversationSession.onUserTranscript((transcript) => {
      this.config.onUserTranscript?.(callSid, transcript);
    });

    conversationSession.onAssistantTranscript((transcript) => {
      this.config.onAssistantTranscript?.(callSid, transcript);
    });

    conversationSession.onSpeechStart(() => {
      // Barge-in: Previously cleared Twilio's audio buffer here, but that was
      // too aggressive - any detected speech (even "mm-hmm") would cut off the bot.
      // Now we let OpenAI's interrupt_response handle it internally.
      // The bot's buffered audio may play out briefly, but that's less jarring
      // than cutting off on every small sound.
    });

    conversationSession.onHangupRequested((reason) => {
      // Guard against duplicate hangup requests (OpenAI Realtime API
      // can fire multiple hangup function calls in a single response.done)
      if (session.pendingHangup) {
        console.log(`[MediaStream] Ignoring duplicate hangup request for ${callSid}`);
        return;
      }

      console.log(`[MediaStream] AI requested hangup for call ${callSid}: ${reason}`);
      console.log(`[MediaStream] Sending hangup mark, will wait for Twilio to confirm playback complete`);
      
      // Send mark to Twilio, wait for it to come back (audio finished), then hangup
      const done = new Promise<void>(resolve => {
        session.pendingHangup = { reason, resolve };
      });
      
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          event: "mark",
          streamSid,
          mark: { name: "hangup" }
        }));
        console.log(`[MediaStream] Mark sent to Twilio for stream ${streamSid}`);
      } else {
        console.log(`[MediaStream] WebSocket not open, skipping mark`);
      }
      
      // When mark returns (or timeout), do the hangup
      const timeoutMs = 30000; // 30 second safety timeout for long sentences
      Promise.race([
        done,
        new Promise<void>(r => setTimeout(() => {
          console.log(`[MediaStream] ⚠️ Timeout reached (${timeoutMs}ms) - mark never received for ${callSid}`);
          r();
        }, timeoutMs))
      ]).then(() => {
        console.log(`[MediaStream] Executing hangup for ${callSid}`);
        this.config.onHangupRequested?.(callSid, reason);
      });
    });

    conversationSession.onDtmfRequested((digits) => {
      console.log(`[MediaStream] DTMF "${digits}" requested for call ${callSid}`);

      if (ws.readyState !== WebSocket.OPEN) {
        console.log(`[MediaStream] WebSocket not open, cannot send DTMF`);
        return;
      }

      // Send a mark first, wait for AI audio to finish, then inject tones
      const done = new Promise<void>(resolve => {
        session.pendingDtmf = { digits, resolve };
      });

      ws.send(JSON.stringify({
        event: "mark",
        streamSid,
        mark: { name: "dtmf" }
      }));
      console.log(`[MediaStream] Sent DTMF mark, waiting for audio to finish`);

      let dtmfResolved = false;
      Promise.race([
        done,
        new Promise<void>(r => setTimeout(() => {
          if (!dtmfResolved) {
            console.log(`[MediaStream] ⚠️ DTMF mark timeout for ${callSid}, sending tones anyway`);
            r();
          }
        }, 5000))
      ]).then(() => {
        if (dtmfResolved) return;
        dtmfResolved = true;
        session.pendingDtmf = undefined;
        console.log(`[MediaStream] Injecting DTMF tones "${digits}" into stream ${streamSid}`);

        const dtmfAudio = generateDtmfAudio(digits);
        const chunks = chunkDtmfAudio(dtmfAudio);

        for (const chunk of chunks) {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              event: "media",
              streamSid,
              media: { payload: chunk.toString("base64") },
            }));
          }
        }
      });
    });

    this.sessions.set(streamSid, session);
    this.config.onConnect?.(callSid, streamSid);

    conversationSession.connect().catch((err) => {
      console.error("[MediaStream] Realtime connection failed:", err.message);
    });

    return session;
  }

  /**
   * Handle stream stop event.
   */
  private handleStop(session: StreamSession): void {
    console.log(`[MediaStream] Stream stopped: ${session.streamSid}`);

    session.conversationSession.close();
    this.config.onDisconnect?.(session.callId);
    this.sessions.delete(session.streamSid);
  }

}

/**
 * Twilio Media Stream message format.
 */
interface TwilioMediaMessage {
  event: "connected" | "start" | "media" | "stop" | "mark" | "clear";
  sequenceNumber?: string;
  streamSid?: string;
  start?: {
    streamSid: string;
    accountSid: string;
    callSid: string;
    tracks: string[];
    mediaFormat: {
      encoding: string;
      sampleRate: number;
      channels: number;
    };
  };
  media?: {
    track?: string;
    chunk?: string;
    timestamp?: string;
    payload?: string;
  };
  mark?: {
    name: string;
  };
}
