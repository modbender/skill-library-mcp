#!/usr/bin/env node
"use strict";

/**
 * Voice Agent using Deepgram Voice Agent API with Telnyx Phone Integration.
 * JavaScript port of the original Python implementation.
 */

const http = require("node:http");
const fs = require("node:fs/promises");
const path = require("node:path");
const process = require("node:process");

const dotenv = require("dotenv");
const express = require("express");
const { WebSocket, WebSocketServer } = require("ws");
const yargs = require("yargs/yargs");
const { hideBin } = require("yargs/helpers");

dotenv.config();

let ngrokSdk = null;
let ngrokLegacy = null;
try {
  ngrokSdk = require("@ngrok/ngrok");
} catch (_err) {
  ngrokSdk = null;
}
try {
  ngrokLegacy = require("ngrok");
} catch (_err) {
  ngrokLegacy = null;
}

const logger = {
  isDebugEnabled: false,
  setDebug(enabled) {
    this.isDebugEnabled = enabled;
  },
  info(message) {
    console.log(`${new Date().toISOString()} - INFO - ${message}`);
  },
  warn(message) {
    console.warn(`${new Date().toISOString()} - WARN - ${message}`);
  },
  error(message) {
    console.error(`${new Date().toISOString()} - ERROR - ${message}`);
  },
  debug(message) {
    if (this.isDebugEnabled) {
      console.debug(`${new Date().toISOString()} - DEBUG - ${message}`);
    }
  },
};

const VALID_MODELS = {
  anthropic: ["claude-3-5-haiku-latest", "claude-sonnet-4-20250514"],
  open_ai: [
    "gpt-5.1-chat-latest",
    "gpt-5.1",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
  ],
};

const DEFAULT_MODEL = "gpt-4o-mini";

const VALID_VOICES = {
  deepgram: {
    "aura-2-thalia-en": { description: "Thalia (Female, American)" },
    "aura-2-luna-en": { description: "Luna (Female, American)" },
    "aura-2-stella-en": { description: "Stella (Female, American)" },
    "aura-2-athena-en": { description: "Athena (Female, British)" },
    "aura-2-hera-en": { description: "Hera (Female, American)" },
    "aura-2-orion-en": { description: "Orion (Male, American)" },
    "aura-2-arcas-en": { description: "Arcas (Male, American)" },
    "aura-2-perseus-en": { description: "Perseus (Male, American)" },
    "aura-2-angus-en": { description: "Angus (Male, Irish)" },
    "aura-2-orpheus-en": { description: "Orpheus (Male, American)" },
    "aura-2-helios-en": { description: "Helios (Male, British)" },
    "aura-2-zeus-en": { description: "Zeus (Male, American)" },
  },
  elevenlabs: {
    rachel: {
      voice_id: "21m00Tcm4TlvDq8ikWAM",
      description: "Rachel (Female, American)",
    },
    adam: {
      voice_id: "pNInz6obpgDQGcFmaJgB",
      description: "Adam (Male, American)",
    },
    bella: {
      voice_id: "EXAVITQu4vr4xnSDxMaL",
      description: "Bella (Female, American)",
    },
    josh: {
      voice_id: "TxGEqnHWrfWFTfGW9XjX",
      description: "Josh (Male, American)",
    },
    elli: {
      voice_id: "MF3mGyEYCl7XYWbV9V6O",
      description: "Elli (Female, American)",
    },
    sam: {
      voice_id: "yoZ06aMxZJJ28mfd3POQ",
      description: "Sam (Male, American)",
    },
  },
};

const DEFAULT_VOICE = "elevenlabs/rachel";

function getVoiceConfig(voiceString) {
  if (!voiceString.includes("/")) {
    throw new Error(`Invalid voice format '${voiceString}'. Use 'provider/voice-id' format.`);
  }

  const [provider, voiceName] = voiceString.split("/", 2);

  if (!Object.hasOwn(VALID_VOICES, provider)) {
    throw new Error(
      `Unknown voice provider '${provider}'. Valid providers: ${Object.keys(VALID_VOICES).join(", ")}`,
    );
  }

  if (!Object.hasOwn(VALID_VOICES[provider], voiceName)) {
    throw new Error(
      `Unknown voice '${voiceName}' for provider '${provider}'. Valid voices: ${Object.keys(
        VALID_VOICES[provider],
      ).join(", ")}`,
    );
  }

  return {
    provider,
    voiceName,
    voiceConfig: VALID_VOICES[provider][voiceName],
  };
}

function validateVoice(voiceString) {
  try {
    getVoiceConfig(voiceString);
    return true;
  } catch (_err) {
    return false;
  }
}

function getAllValidVoices() {
  const voices = [];
  for (const [provider, voiceDict] of Object.entries(VALID_VOICES)) {
    for (const voiceName of Object.keys(voiceDict)) {
      voices.push(`${provider}/${voiceName}`);
    }
  }
  return voices;
}

function getVoiceSampleRate(voiceString) {
  const { provider } = getVoiceConfig(voiceString);
  if (provider === "elevenlabs") {
    return 24000;
  }
  return 16000;
}

function getProviderForModel(model) {
  for (const [provider, models] of Object.entries(VALID_MODELS)) {
    if (models.includes(model)) {
      return provider;
    }
  }
  return null;
}

function validateModel(model) {
  return getProviderForModel(model) !== null;
}

function getAllValidModels() {
  return Object.values(VALID_MODELS).flat();
}

class Config {
  constructor({ personality, task, greeting, model, voice }) {
    this.telnyxApiKey = process.env.TELNYX_API_KEY || "";
    this.telnyxConnectionId = process.env.TELNYX_CONNECTION_ID || "";
    this.telnyxPhoneNumber = process.env.TELNYX_PHONE_NUMBER || "";
    this.deepgramApiKey = process.env.DEEPGRAM_API_KEY || "";
    this.publicWsUrl = process.env.PUBLIC_WS_URL || "";
    this.serverHost = process.env.SERVER_HOST || "0.0.0.0";
    this.serverPort = Number.parseInt(process.env.SERVER_PORT || "8765", 10);
    this.recordingsDir = path.resolve(process.env.RECORDINGS_DIR || path.join(process.cwd(), "recordings"));

    this.agentPersonality = personality || null;
    this.agentTask = task || null;
    this.agentGreeting = greeting || null;
    this.agentModel = model || DEFAULT_MODEL;
    this.agentVoice = voice || DEFAULT_VOICE;
  }
}

const BASE_PROMPT = `You're on a real phone call. Talk like a human, not an AI.

KEEP IT CONVERSATIONAL:
- Shorter responses tend to sound more natural - one or two sentences usually works well
- You can break information into smaller pieces across multiple turns
- Examples that often work well:
  "Yeah, so... Tuesday at 3 works great."
  "Got it. Let me check on that."
  "Right, and what's the best number to reach you?"
  "Perfect. I'll get that updated for you."

NATURAL SPEECH PATTERNS (use your judgment):
- Starting with "So...", "Yeah, so...", "Right...", "Got it.", "Okay, so..." can feel natural
- Acknowledging first often helps: "Makes sense.", "I hear you.", "Got it."
- Occasional filler words like "Hmm, let me see..." or "Um, actually..." can sound human
- Casual confirmations work well: "Perfect.", "Great.", "Sounds good."

VOICE OUTPUT FORMAT (CRITICAL):
- Plain text only - no lists, bullets, or markdown
- Spell out numbers: "three fifteen" not "3:15"
- Spell out phone numbers digit by digit: "five one seven, nine four four..."
- Spell out dates: "Tuesday, January fifteenth"
- No abbreviations: say "Doctor" not "Dr."

THINGS THAT CAN SOUND ROBOTIC (try to avoid):
- Overly formal phrases like "I'd be happy to help" or "Certainly"
- Giving lots of information all at once
- Corporate/scripted language
- Long compound sentences with multiple clauses

INFORMATION RULES:
- Only use facts you were explicitly given
- If you don't know something, say "I don't have that info handy, let me call you back"
- Never make up names, dates, times, or details

ENDING CALLS:
- You decide when to end - task complete, user done, or need to call back
- A quick goodbye keeps it natural: "Thanks! Take care.", "Great, bye!", "Talk soon!"`;

const DEFAULT_GREETING = "Hi there! How are you doing today?";

function buildSystemPrompt(personality, task) {
  const promptParts = [BASE_PROMPT];

  if (personality) {
    promptParts.push(`\nYOUR PERSONALITY:\n${personality}`);
  }

  if (task) {
    promptParts.push(`\nYOUR TASK FOR THIS CALL:\n${task}`);
  }

  promptParts.push("\nRemember: Be natural, be human, and NEVER assume information you weren't given.");

  return promptParts.join("\n");
}

function int16BufferToArray(buffer) {
  const length = Math.floor(buffer.length / 2);
  const samples = new Int16Array(length);
  for (let i = 0; i < length; i += 1) {
    samples[i] = buffer.readInt16LE(i * 2);
  }
  return samples;
}

function int16ArrayToBuffer(samples) {
  const output = Buffer.alloc(samples.length * 2);
  for (let i = 0; i < samples.length; i += 1) {
    output.writeInt16LE(samples[i], i * 2);
  }
  return output;
}

function resampleLinear(samples, inputRate, outputRate) {
  if (samples.length === 0) {
    return new Int16Array(0);
  }
  if (inputRate === outputRate) {
    return Int16Array.from(samples);
  }

  const ratio = inputRate / outputRate;
  const outputLength = Math.max(1, Math.round(samples.length / ratio));
  const output = new Int16Array(outputLength);

  for (let i = 0; i < outputLength; i += 1) {
    const sourceIndex = i * ratio;
    const leftIndex = Math.floor(sourceIndex);
    const rightIndex = Math.min(leftIndex + 1, samples.length - 1);
    const interpolation = sourceIndex - leftIndex;

    const value = samples[leftIndex] + (samples[rightIndex] - samples[leftIndex]) * interpolation;
    output[i] = Math.max(-32768, Math.min(32767, Math.round(value)));
  }

  return output;
}

function decodeMuLaw(muLawByte) {
  const transformed = (~muLawByte) & 0xff;
  const sign = transformed & 0x80;
  const exponent = (transformed >> 4) & 0x07;
  const mantissa = transformed & 0x0f;

  let sample = ((mantissa << 3) + 0x84) << exponent;
  sample -= 0x84;

  return sign ? -sample : sample;
}

function encodeMuLaw(sample) {
  const BIAS = 0x84;
  const CLIP = 32635;

  let pcm = sample;
  let sign = 0;

  if (pcm < 0) {
    sign = 0x80;
    pcm = -pcm;
  }

  if (pcm > CLIP) {
    pcm = CLIP;
  }

  pcm += BIAS;

  let exponent = 7;
  for (let expMask = 0x4000; (pcm & expMask) === 0 && exponent > 0; expMask >>= 1) {
    exponent -= 1;
  }

  const mantissa = (pcm >> (exponent + 3)) & 0x0f;
  return (~(sign | (exponent << 4) | mantissa)) & 0xff;
}

function mulaw8kToLinear16k(muLawData) {
  const linear8k = new Int16Array(muLawData.length);
  for (let i = 0; i < muLawData.length; i += 1) {
    linear8k[i] = decodeMuLaw(muLawData[i]);
  }

  const linear16k = resampleLinear(linear8k, 8000, 16000);
  return int16ArrayToBuffer(linear16k);
}

function linear16kToMulaw8k(linearData) {
  const linear16k = int16BufferToArray(linearData);
  const linear8k = resampleLinear(linear16k, 16000, 8000);

  const output = Buffer.alloc(linear8k.length);
  for (let i = 0; i < linear8k.length; i += 1) {
    output[i] = encodeMuLaw(linear8k[i]);
  }

  return output;
}

function linear24kToMulaw8k(linearData) {
  const linear24k = int16BufferToArray(linearData);
  const linear8k = resampleLinear(linear24k, 24000, 8000);

  const output = Buffer.alloc(linear8k.length);
  for (let i = 0; i < linear8k.length; i += 1) {
    output[i] = encodeMuLaw(linear8k[i]);
  }

  return output;
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

const DTMF_ALLOWED_SEQUENCE_PATTERN = /^[0-9A-Da-d*#wW]+$/;
const DTMF_HAS_TONE_PATTERN = /[0-9A-Da-d*#]/;
const MIN_DTMF_DURATION_MILLIS = 100;
const MAX_DTMF_DURATION_MILLIS = 500;

function parseSendDtmfParameters(parameters) {
  if (!parameters || typeof parameters !== "object") {
    throw new Error("send_dtmf expects an object with a digits field.");
  }

  if (typeof parameters.digits !== "string") {
    throw new Error("send_dtmf digits must be a string.");
  }

  const digits = parameters.digits.replace(/\s+/g, "");
  if (!digits) {
    throw new Error("send_dtmf digits cannot be empty.");
  }

  if (!DTMF_ALLOWED_SEQUENCE_PATTERN.test(digits)) {
    throw new Error("send_dtmf digits can only contain 0-9, A-D, *, #, w, or W.");
  }

  if (!DTMF_HAS_TONE_PATTERN.test(digits)) {
    throw new Error("send_dtmf digits must include at least one DTMF tone (0-9, A-D, *, or #).");
  }

  const durationRaw = parameters.duration_millis;
  if (durationRaw === undefined || durationRaw === null) {
    return { digits, durationMillis: null };
  }

  if (!Number.isInteger(durationRaw)) {
    throw new Error("send_dtmf duration_millis must be an integer.");
  }

  if (durationRaw < MIN_DTMF_DURATION_MILLIS || durationRaw > MAX_DTMF_DURATION_MILLIS) {
    throw new Error(
      `send_dtmf duration_millis must be between ${MIN_DTMF_DURATION_MILLIS} and ${MAX_DTMF_DURATION_MILLIS}.`,
    );
  }

  return { digits, durationMillis: durationRaw };
}

async function hangupHandler(parameters, _context) {
  const reason = parameters.reason || "unspecified";
  logger.info(`[TOOL] hangup called - reason: ${reason}`);
  await sleep(1000);
  return "Call ended.";
}

async function sendDtmfHandler(parameters, context) {
  const { session, callManager: activeCallManager } = context || {};
  const { digits, durationMillis } = parseSendDtmfParameters(parameters || {});

  if (!activeCallManager) {
    throw new Error("Call manager unavailable for send_dtmf.");
  }

  if (!session || !session.callControlId) {
    throw new Error("Cannot send DTMF without an active call_control_id.");
  }

  logger.info(
    `[TOOL] send_dtmf called - digits: ${digits}, duration_millis: ${
      durationMillis === null ? "default" : durationMillis
    }`,
  );

  await activeCallManager.sendDtmf(session.callControlId, { digits, durationMillis });
  return `DTMF sent (${digits.length} chars).`;
}

const TOOL_HANDLERS = {
  hangup: hangupHandler,
  send_dtmf: sendDtmfHandler,
};

class CallSession {
  constructor(streamId, callControlId, outputSampleRate = 16000) {
    this.streamId = streamId;
    this.callControlId = callControlId;

    this.outputQueue = [];
    this.outputSampleRate = outputSampleRate;

    this.bargeInPending = false;
    this.stop = false;
    this.shouldHangup = false;

    this.deepgramSocket = null;
    this.outputInterval = null;

    this.audioInCount = 0;
    this.audioOutCount = 0;
  }
}

function createThinkConfig(model) {
  const providerType = getProviderForModel(model);

  if (providerType === "anthropic") {
    return {
      provider: {
        type: "anthropic",
        model,
      },
    };
  }

  if (providerType === "open_ai") {
    return {
      provider: {
        type: "open_ai",
        model,
      },
    };
  }

  logger.warn(`Unknown model ${model}, falling back to ${DEFAULT_MODEL}`);
  return {
    provider: {
      type: "open_ai",
      model: DEFAULT_MODEL,
    },
  };
}

function createSpeakProvider(voice) {
  const { provider, voiceName, voiceConfig } = getVoiceConfig(voice);

  if (provider === "deepgram") {
    return {
      type: "deepgram",
      model: voiceName,
    };
  }

  if (provider === "elevenlabs") {
    return {
      type: "eleven_labs",
      model_id: "eleven_turbo_v2_5",
      voice_id: voiceConfig.voice_id,
    };
  }

  logger.warn(`Unknown voice provider ${provider}, falling back to Deepgram`);
  return {
    type: "deepgram",
    model: "aura-2-thalia-en",
  };
}

function createAgentSettings({ personality, task, greeting, model, voice }) {
  const agentPrompt = buildSystemPrompt(personality, task);
  const agentGreeting = greeting || DEFAULT_GREETING;
  const agentModel = model || DEFAULT_MODEL;
  const agentVoice = voice || DEFAULT_VOICE;
  const outputSampleRate = getVoiceSampleRate(agentVoice);
  const thinkConfig = createThinkConfig(agentModel);

  return {
    type: "Settings",
    audio: {
      input: {
        encoding: "linear16",
        sample_rate: 16000,
      },
      output: {
        encoding: "linear16",
        sample_rate: outputSampleRate,
        container: "none",
      },
    },
    agent: {
      language: "en",
      listen: {
        provider: {
          type: "deepgram",
          model: "nova-3",
        },
      },
      think: {
        provider: thinkConfig.provider,
        ...(thinkConfig.endpoint ? { endpoint: thinkConfig.endpoint } : {}),
        prompt: agentPrompt,
        functions: [
          {
            name: "hangup",
            description:
              "End the phone call. You have full autonomy to decide when to end the conversation.\n\n" +
              "IMPORTANT: Before calling this function, ALWAYS say a brief, natural goodbye such as \"Goodbye!\", \"Take care!\", \"Have a great day!\", \"Thanks for your time!\", or similar.\n\n" +
              "End the conversation when:\n" +
              "- The task is complete and confirmed\n" +
              "- The user wants to end the call (says goodbye, hang up, stop, etc.)\n" +
              "- The user is unavailable and you've left a message or agreed to call back\n" +
              "- You're missing critical information and need to call back later\n" +
              "- The conversation has reached a natural conclusion\n" +
              "- The user is unresponsive or the call isn't productive\n" +
              "- Any other reason you deem appropriate to end politely\n\n" +
              "Always be polite and natural when ending - never hang up abruptly without a goodbye.",
            parameters: {
              type: "object",
              properties: {
                reason: {
                  type: "string",
                  description:
                    "Brief reason for ending the call (e.g., 'task complete', 'user requested', 'will call back', 'left message')",
                },
              },
              required: ["reason"],
            },
          },
          {
            name: "send_dtmf",
            description:
              "Send DTMF keypad tones to the live phone call (for IVR menus and keypad prompts).\n\n" +
              "Use this ONLY when the callee or IVR explicitly asks for keypad input. Do not guess menu options.\n\n" +
              "You may include pauses with 'w' (half second) or 'W' (one second), for example: '1ww2#'.",
            parameters: {
              type: "object",
              properties: {
                digits: {
                  type: "string",
                  description: "DTMF sequence to send. Allowed: 0-9, A-D, *, #, w, W. Example: '1ww2#'.",
                },
                duration_millis: {
                  type: "integer",
                  description: "Optional tone duration in milliseconds for each DTMF digit (100-500).",
                  minimum: MIN_DTMF_DURATION_MILLIS,
                  maximum: MAX_DTMF_DURATION_MILLIS,
                },
              },
              required: ["digits"],
            },
          },
        ],
      },
      speak: {
        provider: createSpeakProvider(agentVoice),
      },
      greeting: agentGreeting,
    },
  };
}

let config = null;
let sessionManager = null;
let callManager = null;
let serverOnlyMode = true;
let shutdownResolver = null;
let shutdownPromise = null;
let ngrokTunnelUrl = null;
let ngrokListener = null;
let httpServer = null;
let wsServer = null;

function createShutdownPromise() {
  shutdownPromise = new Promise((resolve) => {
    shutdownResolver = resolve;
  });
}

function resolveShutdown() {
  if (shutdownResolver) {
    const resolve = shutdownResolver;
    shutdownResolver = null;
    resolve();
  }
}

class SessionManager {
  constructor(appConfig) {
    this.config = appConfig;
    this.sessions = new Map();
  }

  createSession(streamId, callControlId) {
    const outputSampleRate = getVoiceSampleRate(this.config.agentVoice);
    const session = new CallSession(streamId, callControlId, outputSampleRate);

    this.sessions.set(streamId, session);
    logger.info(`[Session] Created session ${streamId}`);

    startDeepgramWorker(session, this.config);

    return session;
  }

  getSession(streamId) {
    return this.sessions.get(streamId);
  }

  closeSession(streamId) {
    const session = this.sessions.get(streamId);
    if (!session) {
      return;
    }

    session.stop = true;

    if (session.outputInterval) {
      clearInterval(session.outputInterval);
      session.outputInterval = null;
    }

    if (session.deepgramSocket && session.deepgramSocket.readyState === WebSocket.OPEN) {
      try {
        session.deepgramSocket.close();
      } catch (_err) {
        // No-op during cleanup.
      }
    }

    this.sessions.delete(streamId);
    logger.info(`[Session] Closed session ${streamId}`);
  }

  closeAllSessions() {
    for (const streamId of Array.from(this.sessions.keys())) {
      this.closeSession(streamId);
    }
  }
}

class CallManager {
  constructor(appConfig) {
    this.config = appConfig;
    this.recordingStartRequested = new Set();
    this.recordingUrlByCallControlId = new Map();
    this.recordingIdByCallControlId = new Map();
    this.deletedRecordingIds = new Set();
    this.recordingWaitersByCallControlId = new Map();
    this.recordingPersistPromisesByCallControlId = new Map();
    this.localRecordingPathByCallControlId = new Map();
  }

  getAuthHeaders() {
    return {
      Authorization: `Bearer ${this.config.telnyxApiKey}`,
      "Content-Type": "application/json",
    };
  }

  async initiateCall(toNumber, fromNumber = null) {
    const from = fromNumber || this.config.telnyxPhoneNumber;

    logger.info(`[Telnyx] Calling ${toNumber} from ${from}`);

    const response = await fetch("https://api.telnyx.com/v2/calls", {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        connection_id: this.config.telnyxConnectionId,
        to: toNumber,
        from,
        record: "record-from-answer",
        stream_url: this.config.publicWsUrl,
        stream_track: "both_tracks",
        stream_bidirectional_mode: "rtp",
        stream_bidirectional_codec: "PCMU",
        webhook_url_method: "POST",
      }),
    });

    if (!response.ok) {
      const bodyText = await response.text();
      throw new Error(`Telnyx dial failed (${response.status}): ${bodyText}`);
    }

    const responseBody = await response.json();
    const callControlId = responseBody?.data?.call_control_id || "";
    if (callControlId) {
      // Outbound calls are auto-recorded from answer; avoid issuing a duplicate record_start.
      this.recordingStartRequested.add(callControlId);
    }

    logger.info(`[Telnyx] Call initiated: ${callControlId}`);

    return {
      call_control_id: callControlId,
      status: "initiated",
    };
  }

  async hangup(callControlId) {
    logger.info(`[Telnyx] Hanging up ${callControlId}`);

    try {
      const response = await fetch(
        `https://api.telnyx.com/v2/calls/${encodeURIComponent(callControlId)}/actions/hangup`,
        {
          method: "POST",
          headers: this.getAuthHeaders(),
          body: JSON.stringify({}),
        },
      );

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Telnyx hangup failed (${response.status}): ${bodyText}`);
      }
    } catch (error) {
      logger.error(`[Telnyx] Hangup error: ${error.message}`);
    }
  }

  async sendDtmf(callControlId, { digits, durationMillis = null }) {
    if (!callControlId) {
      throw new Error("Missing call_control_id for send_dtmf.");
    }

    const payload = { digits };
    if (durationMillis !== null && durationMillis !== undefined) {
      payload.duration_millis = durationMillis;
    }

    const response = await fetch(
      `https://api.telnyx.com/v2/calls/${encodeURIComponent(callControlId)}/actions/send_dtmf`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: JSON.stringify(payload),
      },
    );

    if (!response.ok) {
      const bodyText = await response.text();
      throw new Error(`Telnyx send_dtmf failed (${response.status}): ${bodyText}`);
    }
  }

  extractRecordingUrl(payload) {
    const candidates = [
      payload?.recording_urls?.mp3,
      payload?.recording_urls?.wav,
      payload?.public_recording_urls?.mp3,
      payload?.public_recording_urls?.wav,
      payload?.download_urls?.mp3,
      payload?.download_urls?.wav,
      payload?.url,
    ];

    for (const candidate of candidates) {
      if (typeof candidate === "string" && candidate.length > 0) {
        return candidate;
      }
    }

    return null;
  }

  extractRecordingId(payload) {
    if (typeof payload?.recording_id === "string" && payload.recording_id.length > 0) {
      return payload.recording_id;
    }
    if (typeof payload?.id === "string" && payload.id.length > 0) {
      return payload.id;
    }
    return "";
  }

  setRecordingId(callControlId, recordingId) {
    if (!callControlId || !recordingId) {
      return;
    }
    this.recordingIdByCallControlId.set(callControlId, recordingId);
  }

  setRecordingUrl(callControlId, recordingUrl) {
    if (!callControlId || !recordingUrl) {
      return;
    }

    this.recordingUrlByCallControlId.set(callControlId, recordingUrl);
    logger.info(`[Recording] Saved recording URL for ${callControlId}`);

    const waiters = this.recordingWaitersByCallControlId.get(callControlId) || [];
    for (const resolve of waiters) {
      resolve(recordingUrl);
    }
    this.recordingWaitersByCallControlId.delete(callControlId);
  }

  async startRecording(callControlId) {
    if (!callControlId || this.recordingStartRequested.has(callControlId)) {
      return;
    }

    this.recordingStartRequested.add(callControlId);
    logger.info(`[Recording] Starting recording for ${callControlId}`);

    try {
      const response = await fetch(
        `https://api.telnyx.com/v2/calls/${encodeURIComponent(callControlId)}/actions/record_start`,
        {
          method: "POST",
          headers: this.getAuthHeaders(),
          body: JSON.stringify({
            format: "mp3",
            channels: "dual",
            recording_track: "both",
          }),
        },
      );

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Telnyx record_start failed (${response.status}): ${bodyText}`);
      }

      logger.info(`[Recording] Recording enabled for ${callControlId}`);
    } catch (error) {
      this.recordingStartRequested.delete(callControlId);
      logger.error(`[Recording] Failed to start recording for ${callControlId}: ${error.message}`);
    }
  }

  async fetchRecordingUrlById(callControlId, recordingId) {
    if (!recordingId) {
      return null;
    }

    try {
      const response = await fetch(`https://api.telnyx.com/v2/recordings/${encodeURIComponent(recordingId)}`, {
        method: "GET",
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Telnyx recording fetch failed (${response.status}): ${bodyText}`);
      }

      const responseBody = await response.json();
      const recordingData = responseBody?.data || {};
      const recordingUrl = this.extractRecordingUrl(recordingData);
      const resolvedCallControlId = callControlId || recordingData.call_control_id || "";
      const resolvedRecordingId = this.extractRecordingId(recordingData);

      if (resolvedCallControlId && resolvedRecordingId) {
        this.setRecordingId(resolvedCallControlId, resolvedRecordingId);
      }

      if (recordingUrl && resolvedCallControlId) {
        this.setRecordingUrl(resolvedCallControlId, recordingUrl);
      }

      return recordingUrl;
    } catch (error) {
      logger.error(`[Recording] Failed to fetch recording ${recordingId}: ${error.message}`);
      return null;
    }
  }

  async fetchRecordingByCallControlId(callControlId) {
    if (!callControlId) {
      return null;
    }

    const executeListRequest = async (queryParams, suppressErrorLogs = false) => {
      try {
        const query = queryParams.toString();
        const url = query ? `https://api.telnyx.com/v2/recordings?${query}` : "https://api.telnyx.com/v2/recordings";
        const response = await fetch(url, {
          method: "GET",
          headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
          const bodyText = await response.text();
          if (!suppressErrorLogs) {
            logger.warn(`[Recording] Recording list lookup failed (${response.status}): ${bodyText}`);
          }
          return [];
        }

        const responseBody = await response.json();
        return Array.isArray(responseBody?.data) ? responseBody.data : [];
      } catch (error) {
        if (!suppressErrorLogs) {
          logger.warn(`[Recording] Recording list lookup error: ${error.message}`);
        }
        return [];
      }
    };

    const filteredParams = new URLSearchParams({
      "page[size]": "25",
      "filter[call_control_id]": callControlId,
    });
    let recordings = await executeListRequest(filteredParams, true);

    if (!recordings.some((recording) => recording?.call_control_id === callControlId)) {
      const fallbackParams = new URLSearchParams({
        "page[size]": "25",
      });
      recordings = await executeListRequest(fallbackParams, false);
    }

    const recording = recordings.find((item) => item?.call_control_id === callControlId);
    if (!recording) {
      return null;
    }

    const recordingId = this.extractRecordingId(recording);
    if (recordingId) {
      this.setRecordingId(callControlId, recordingId);
    }

    const recordingUrl = this.extractRecordingUrl(recording);
    if (recordingUrl) {
      this.setRecordingUrl(callControlId, recordingUrl);
    }

    return recording;
  }

  async resolveRecordingIdForCall(callControlId) {
    if (!callControlId) {
      return "";
    }

    const knownRecordingId = this.recordingIdByCallControlId.get(callControlId);
    if (knownRecordingId) {
      return knownRecordingId;
    }

    await this.fetchRecordingByCallControlId(callControlId);
    return this.recordingIdByCallControlId.get(callControlId) || "";
  }

  async deleteRecordingFromTelnyx(recordingId) {
    if (!recordingId || this.deletedRecordingIds.has(recordingId)) {
      return true;
    }

    try {
      const response = await fetch(`https://api.telnyx.com/v2/recordings/${encodeURIComponent(recordingId)}`, {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Telnyx recording delete failed (${response.status}): ${bodyText}`);
      }

      this.deletedRecordingIds.add(recordingId);
      return true;
    } catch (error) {
      logger.error(`[Recording] Failed to delete remote recording ${recordingId}: ${error.message}`);
      return false;
    }
  }

  onRecordingSaved(eventPayload) {
    const callControlId = eventPayload?.call_control_id || "";
    const recordingId = this.extractRecordingId(eventPayload);
    const recordingUrl = this.extractRecordingUrl(eventPayload || {});

    if (callControlId && recordingId) {
      this.setRecordingId(callControlId, recordingId);
    }

    if (recordingUrl) {
      this.setRecordingUrl(callControlId, recordingUrl);
      return;
    }

    if (recordingId) {
      void this.fetchRecordingUrlById(callControlId, recordingId);
    }
  }

  waitForRecordingUrl(callControlId, timeoutMs = 15000) {
    if (!callControlId) {
      return Promise.resolve(null);
    }

    const existingUrl = this.recordingUrlByCallControlId.get(callControlId);
    if (existingUrl) {
      return Promise.resolve(existingUrl);
    }

    return new Promise((resolve) => {
      const waiters = this.recordingWaitersByCallControlId.get(callControlId) || [];
      const onReady = (url) => {
        clearTimeout(timeout);
        resolve(url);
      };

      const timeout = setTimeout(() => {
        const updatedWaiters = (this.recordingWaitersByCallControlId.get(callControlId) || []).filter(
          (waiter) => waiter !== onReady,
        );
        if (updatedWaiters.length > 0) {
          this.recordingWaitersByCallControlId.set(callControlId, updatedWaiters);
        } else {
          this.recordingWaitersByCallControlId.delete(callControlId);
        }
        resolve(null);
      }, timeoutMs);

      waiters.push(onReady);
      this.recordingWaitersByCallControlId.set(callControlId, waiters);
    });
  }

  async waitForRecordingUrlWithFallback(callControlId, timeoutMs = 20000) {
    if (!callControlId) {
      return null;
    }

    const deadline = Date.now() + timeoutMs;

    while (Date.now() < deadline) {
      const existingUrl = this.recordingUrlByCallControlId.get(callControlId);
      if (existingUrl) {
        return existingUrl;
      }

      const knownRecordingId = this.recordingIdByCallControlId.get(callControlId);
      if (knownRecordingId) {
        const urlFromRecording = await this.fetchRecordingUrlById(callControlId, knownRecordingId);
        if (urlFromRecording) {
          return urlFromRecording;
        }
      } else {
        await this.fetchRecordingByCallControlId(callControlId);
        const discoveredUrl = this.recordingUrlByCallControlId.get(callControlId);
        if (discoveredUrl) {
          return discoveredUrl;
        }
      }

      const remainingMs = deadline - Date.now();
      if (remainingMs <= 0) {
        break;
      }
      await sleep(Math.min(2000, remainingMs));
    }

    return this.recordingUrlByCallControlId.get(callControlId) || null;
  }

  sanitizeCallControlId(callControlId) {
    const safeValue = String(callControlId || "")
      .replace(/[^a-zA-Z0-9_-]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_+|_+$/g, "");
    return safeValue || "call";
  }

  inferRecordingExtension(recordingUrl, contentType = "") {
    const type = contentType.toLowerCase();
    if (type.includes("audio/wav") || type.includes("audio/x-wav")) {
      return ".wav";
    }
    if (type.includes("audio/mpeg") || type.includes("audio/mp3")) {
      return ".mp3";
    }

    try {
      const pathname = new URL(recordingUrl).pathname || "";
      const extension = path.extname(pathname).toLowerCase();
      if (extension === ".wav" || extension === ".mp3") {
        return extension;
      }
    } catch (_error) {
      // Ignore malformed URLs and fall back to mp3.
    }

    return ".mp3";
  }

  async downloadRecordingToLocalFile(callControlId, recordingUrl) {
    if (!recordingUrl || !/^https?:\/\//i.test(recordingUrl)) {
      logger.warn(`[Recording] Unsupported recording URL for local download: ${recordingUrl}`);
      return null;
    }

    try {
      await fs.mkdir(this.config.recordingsDir, { recursive: true });

      let response = await fetch(recordingUrl);
      if (!response.ok) {
        response = await fetch(recordingUrl, { headers: this.getAuthHeaders() });
      }

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Recording download failed (${response.status}): ${bodyText}`);
      }

      const extension = this.inferRecordingExtension(recordingUrl, response.headers.get("content-type") || "");
      const safeCallId = this.sanitizeCallControlId(callControlId);
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const localPath = path.join(this.config.recordingsDir, `${timestamp}_${safeCallId}${extension}`);
      const audioBuffer = Buffer.from(await response.arrayBuffer());

      await fs.writeFile(localPath, audioBuffer);
      this.localRecordingPathByCallControlId.set(callControlId, localPath);

      return localPath;
    } catch (error) {
      logger.error(`[Recording] Failed to save recording locally for ${callControlId}: ${error.message}`);
      return null;
    }
  }

  waitAndPersistRecording(callControlId, timeoutMs = 30000) {
    if (!callControlId) {
      return Promise.resolve(null);
    }

    const cachedPath = this.localRecordingPathByCallControlId.get(callControlId);
    if (cachedPath) {
      return Promise.resolve(cachedPath);
    }

    const existingPromise = this.recordingPersistPromisesByCallControlId.get(callControlId);
    if (existingPromise) {
      return existingPromise;
    }

    logger.info(`[Recording] Waiting for recording URL for ${callControlId}...`);

    const persistPromise = this.waitForRecordingUrlWithFallback(callControlId, timeoutMs)
      .then(async (recordingUrl) => {
        if (recordingUrl) {
          logger.info(`[Recording] Download URL: ${recordingUrl}`);
          const localPath = await this.downloadRecordingToLocalFile(callControlId, recordingUrl);
          if (localPath) {
            logger.info(`[Recording] Saved locally: ${localPath}`);

            const recordingId = await this.resolveRecordingIdForCall(callControlId);
            if (recordingId) {
              const deleted = await this.deleteRecordingFromTelnyx(recordingId);
              if (deleted) {
                logger.info(`[Recording] Deleted from Telnyx: ${recordingId}`);
              } else {
                logger.warn(`[Recording] Local copy saved, but failed to delete Telnyx recording: ${recordingId}`);
              }
            } else {
              logger.warn(`[Recording] Local copy saved, but could not resolve Telnyx recording ID for cleanup.`);
            }
          } else {
            logger.warn(`[Recording] Unable to save recording locally for ${callControlId}.`);
          }
          return localPath;
        } else {
          logger.warn(
            `[Recording] URL not available before timeout for ${callControlId}. Check Telnyx recordings.`,
          );
          return null;
        }
      })
      .finally(() => {
        this.recordingPersistPromisesByCallControlId.delete(callControlId);
      });

    this.recordingPersistPromisesByCallControlId.set(callControlId, persistPromise);
    return persistPromise;
  }
}

function sendFunctionCallResponse(deepgramSocket, funcName, funcId, content) {
  if (!deepgramSocket || deepgramSocket.readyState !== WebSocket.OPEN) {
    return;
  }

  deepgramSocket.send(
    JSON.stringify({
      type: "FunctionCallResponse",
      name: funcName,
      content: String(content),
      id: funcId,
    }),
  );
}

async function handleFunctionCallRequest(message, deepgramSocket, session) {
  const functions = Array.isArray(message.functions) ? message.functions : [];

  for (const func of functions) {
    const funcName = func?.name || "";
    const funcId = func?.id || "";
    const argsString = func?.arguments || "{}";

    logger.info(`[Function] ${funcName} called`);

    const handler = TOOL_HANDLERS[funcName];
    if (!handler) {
      logger.warn(`[Function] Unsupported function requested: ${funcName}`);
      sendFunctionCallResponse(deepgramSocket, funcName, funcId, `Unsupported function: ${funcName}`);
      continue;
    }

    let params = {};
    try {
      params = argsString ? JSON.parse(argsString) : {};
    } catch (error) {
      logger.error(`[Function] Invalid JSON arguments for ${funcName}: ${error.message}`);
      sendFunctionCallResponse(deepgramSocket, funcName, funcId, `Error: Invalid function arguments.`);
      continue;
    }

    try {
      const result = await handler(params, { session, callManager });

      if (funcName === "hangup") {
        session.shouldHangup = true;
        if (callManager && session.callControlId) {
          await callManager.hangup(session.callControlId);
        }
        session.stop = true;
      }

      sendFunctionCallResponse(deepgramSocket, funcName, funcId, result);
    } catch (error) {
      logger.error(`[Function] Error executing ${funcName}: ${error.message}`);
      sendFunctionCallResponse(deepgramSocket, funcName, funcId, `Error: ${error.message}`);
    }
  }
}

function startDeepgramWorker(session, appConfig) {
  logger.info(`[Deepgram] Starting worker for session ${session.streamId}`);

  const deepgramSocket = new WebSocket("wss://agent.deepgram.com/v1/agent/converse", {
    headers: {
      Authorization: `Token ${appConfig.deepgramApiKey}`,
    },
  });

  session.deepgramSocket = deepgramSocket;

  deepgramSocket.on("open", () => {
    logger.info("[Deepgram] WebSocket connection established");
    logger.info("[Deepgram] Sending agent settings...");

    deepgramSocket.send(
      JSON.stringify(
        createAgentSettings({
          personality: appConfig.agentPersonality,
          task: appConfig.agentTask,
          greeting: appConfig.agentGreeting,
          model: appConfig.agentModel,
          voice: appConfig.agentVoice,
        }),
      ),
    );
  });

  deepgramSocket.on("message", (data, isBinary) => {
    if (isBinary) {
      session.outputQueue.push(Buffer.from(data));
      return;
    }

    let message = null;
    try {
      message = JSON.parse(data.toString());
    } catch (_error) {
      logger.debug(`[Deepgram] Received non-JSON text message: ${data.toString()}`);
      return;
    }

    const msgType = message?.type || "Unknown";

    if (msgType === "Welcome") {
      logger.info("[Deepgram] Connected to Voice Agent API");
      return;
    }

    if (msgType === "SettingsApplied") {
      logger.info("[Deepgram] Settings applied - Agent ready");
      return;
    }

    if (msgType === "ConversationText") {
      if (message.role === "user") {
        logger.info(`User: ${message.content || ""}`);
      } else if (message.role === "assistant") {
        logger.info(`Agent: ${message.content || ""}`);
      }
      return;
    }

    if (msgType === "UserStartedSpeaking") {
      session.bargeInPending = true;
      logger.info("[Deepgram] User started speaking (barge-in)");
      return;
    }

    if (msgType === "AgentThinking") {
      logger.debug("[Deepgram] Agent thinking...");
      return;
    }

    if (msgType === "FunctionCallRequest") {
      void handleFunctionCallRequest(message, deepgramSocket, session);
      return;
    }

    if (msgType === "Error") {
      logger.error(`[Deepgram] Error: ${JSON.stringify(message)}`);
    }
  });

  deepgramSocket.on("error", (error) => {
    logger.error(`[Deepgram] Error: ${error.message}`);
  });

  deepgramSocket.on("close", () => {
    logger.info("[Deepgram] Connection closed");
    session.stop = true;
    logger.info(`[Deepgram] Worker ended for session ${session.streamId}`);
  });
}

function sendAudioToDeepgram(session, audioBuffer) {
  if (!session.deepgramSocket || session.deepgramSocket.readyState !== WebSocket.OPEN) {
    return;
  }

  try {
    session.deepgramSocket.send(audioBuffer);
    session.audioInCount += 1;

    if (session.audioInCount % 100 === 0) {
      logger.debug(`[Deepgram] Sent ${session.audioInCount} audio chunks`);
    }
  } catch (error) {
    logger.error(`[Deepgram] Error sending audio: ${error.message}`);
  }
}

function handleBargeIn(ws, session) {
  const cleared = session.outputQueue.length;
  session.outputQueue.length = 0;

  try {
    ws.send(
      JSON.stringify({
        event: "clear",
        stream_id: session.streamId,
      }),
    );
    logger.info(`[Barge-in] Cleared ${cleared} chunks + sent clear to Telnyx`);
  } catch (error) {
    logger.error(`[Barge-in] Error sending clear: ${error.message}`);
  }

  session.bargeInPending = false;
}

function startOutputAudioLoop(ws, session) {
  if (session.outputInterval) {
    clearInterval(session.outputInterval);
  }

  session.outputInterval = setInterval(() => {
    if (session.stop || ws.readyState !== WebSocket.OPEN) {
      return;
    }

    if (session.bargeInPending) {
      handleBargeIn(ws, session);
      return;
    }

    const audio = session.outputQueue.shift();
    if (!audio) {
      return;
    }

    if (session.bargeInPending) {
      handleBargeIn(ws, session);
      return;
    }

    try {
      const mulawAudio =
        session.outputSampleRate === 24000 ? linear24kToMulaw8k(audio) : linear16kToMulaw8k(audio);

      ws.send(
        JSON.stringify({
          event: "media",
          stream_id: session.streamId,
          media: {
            payload: mulawAudio.toString("base64"),
          },
        }),
      );

      session.audioOutCount += 1;
      if (session.audioOutCount % 50 === 0) {
        logger.debug(`[WebSocket] Sent ${session.audioOutCount} audio chunks to Telnyx`);
      }
    } catch (error) {
      logger.error(`[WebSocket] Output error: ${error.message}`);
    }
  }, 10);
}

function initApp({ personality, task, greeting, model, voice, serverOnly }) {
  config = new Config({ personality, task, greeting, model, voice });
  sessionManager = new SessionManager(config);
  callManager = new CallManager(config);
  serverOnlyMode = Boolean(serverOnly);
  createShutdownPromise();
}

const app = express();
app.use(express.json());

function isRecordingSavedEvent(eventType) {
  return (
    eventType === "call.recording.saved" ||
    eventType === "recording.saved" ||
    eventType === "recording_saved"
  );
}

app.post("/webhook", (req, res) => {
  try {
    const payload = req.body || {};
    const data = payload.data || {};
    const eventType = data.event_type || "";
    const eventPayload = data.payload || {};

    logger.info(`[Webhook] ${eventType}`);

    if (eventType === "streaming.started") {
      const callControlId = eventPayload.call_control_id || "";
      const streamId = eventPayload.stream_id || "";

      if (callControlId && streamId && sessionManager) {
        const session = sessionManager.getSession(streamId);
        if (session && !session.callControlId) {
          session.callControlId = callControlId;
          logger.info(`[Webhook] Updated session ${streamId} with call_control_id: ${callControlId}`);
        }
      }

      if (callManager && callControlId) {
        void callManager.startRecording(callControlId);
      }
    }

    if (isRecordingSavedEvent(eventType) && callManager) {
      callManager.onRecordingSaved(eventPayload);
    }

    res.json({ status: "ok" });
  } catch (error) {
    logger.error(`[Webhook] Error: ${error.message}`);
    res.status(500).json({ status: "error" });
  }
});

app.get("/health", (_req, res) => {
  res.json({ status: "healthy" });
});

function createWebSocketServer() {
  wsServer = new WebSocketServer({ noServer: true });

  wsServer.on("connection", (ws) => {
    logger.info("[WebSocket] Telnyx connected");

    let session = null;
    let cleanedUp = false;

    const cleanup = () => {
      if (cleanedUp) {
        return;
      }
      cleanedUp = true;

      const endedCallControlId = session?.callControlId || "";

      if (session) {
        sessionManager.closeSession(session.streamId);
        session = null;
      }

      if (callManager && endedCallControlId) {
        void callManager.waitAndPersistRecording(endedCallControlId, 30000);
      }

      if (!serverOnlyMode) {
        logger.info("[Server] Call ended, shutting down...");
        resolveShutdown();
      }
    };

    ws.on("message", (data, isBinary) => {
      if (isBinary) {
        return;
      }

      let message = null;
      try {
        message = JSON.parse(data.toString());
      } catch (_err) {
        return;
      }

      const event = message.event;

      if (event === "connected") {
        logger.info("[WebSocket] Telnyx stream connected");
        return;
      }

      if (event === "start") {
        const streamId = message.stream_id;
        const callControlId = message.start?.call_control_id || "";

        logger.info(`[WebSocket] Stream started: ${streamId}, call_control_id: ${callControlId}`);

        session = sessionManager.createSession(streamId, callControlId);
        startOutputAudioLoop(ws, session);

        if (callManager && callControlId) {
          void callManager.startRecording(callControlId);
        }
        return;
      }

      if (event === "media") {
        if (!session) {
          return;
        }

        const audioBase64 = message.media?.payload;
        const track = message.media?.track || "inbound";

        if (track === "inbound" && audioBase64) {
          const mulawAudio = Buffer.from(audioBase64, "base64");
          const linearAudio = mulaw8kToLinear16k(mulawAudio);
          sendAudioToDeepgram(session, linearAudio);
        }

        return;
      }

      if (event === "stop") {
        logger.info("[WebSocket] Stream stopped");
        cleanup();
      }
    });

    ws.on("close", () => {
      logger.info("[WebSocket] Telnyx disconnected");
      cleanup();
    });

    ws.on("error", (error) => {
      logger.error(`[WebSocket] Error: ${error.message}`);
      cleanup();
    });
  });
}

async function startServer() {
  createWebSocketServer();

  httpServer = http.createServer(app);

  httpServer.on("upgrade", (request, socket, head) => {
    let pathname = "";

    try {
      pathname = new URL(request.url || "", `http://${request.headers.host}`).pathname;
    } catch (_err) {
      socket.destroy();
      return;
    }

    if (pathname !== "/telnyx") {
      socket.destroy();
      return;
    }

    wsServer.handleUpgrade(request, socket, head, (ws) => {
      wsServer.emit("connection", ws, request);
    });
  });

  await new Promise((resolve, reject) => {
    httpServer.once("error", reject);
    httpServer.listen(config.serverPort, config.serverHost, () => {
      httpServer.off("error", reject);
      resolve();
    });
  });
}

async function stopServer() {
  if (sessionManager) {
    sessionManager.closeAllSessions();
  }

  if (wsServer) {
    for (const client of wsServer.clients) {
      try {
        client.close();
      } catch (_err) {
        // No-op during shutdown.
      }
    }
  }

  if (httpServer) {
    await new Promise((resolve) => {
      httpServer.close(() => {
        resolve();
      });
    });
    httpServer = null;
  }
}

async function startNgrok(port, domain = null) {
  const authToken = process.env.NGROK_AUTH_TOKEN;

  if (ngrokSdk) {
    const options = {
      addr: port,
      proto: "http",
    };

    if (authToken) {
      options.authtoken = authToken;
    } else {
      options.authtoken_from_env = true;
    }

    if (domain) {
      options.domain = domain;
    }

    ngrokListener = await ngrokSdk.connect(options);
    ngrokTunnelUrl = typeof ngrokListener.url === "function" ? ngrokListener.url() : String(ngrokListener);

    const wsUrl = `${ngrokTunnelUrl.replace("https://", "wss://").replace("http://", "ws://")}/telnyx`;

    logger.info(`[ngrok] Tunnel established: ${ngrokTunnelUrl}`);
    logger.info(`[ngrok] WebSocket URL: ${wsUrl}`);

    return wsUrl;
  }

  if (ngrokLegacy) {
    const options = {
      addr: port,
      proto: "http",
    };

    if (authToken) {
      options.authtoken = authToken;
    }

    if (domain) {
      options.hostname = domain;
    }

    ngrokTunnelUrl = await ngrokLegacy.connect(options);

    const wsUrl = `${ngrokTunnelUrl.replace("https://", "wss://").replace("http://", "ws://")}/telnyx`;

    logger.info(`[ngrok] Tunnel established: ${ngrokTunnelUrl}`);
    logger.info(`[ngrok] WebSocket URL: ${wsUrl}`);

    return wsUrl;
  }

  throw new Error("ngrok package not installed. Run: npm install");
}

async function stopNgrok() {
  if (ngrokSdk) {
    if (ngrokListener) {
      try {
        await ngrokListener.close();
      } catch (_err) {
        // Ignore listener close errors.
      }
      ngrokListener = null;
    }

    try {
      await ngrokSdk.kill();
    } catch (_err) {
      // Ignore SDK global cleanup errors.
    }
  }

  if (ngrokLegacy && ngrokTunnelUrl) {
    try {
      await ngrokLegacy.disconnect(ngrokTunnelUrl);
    } catch (_err) {
      // Ignore disconnect cleanup errors.
    }

    try {
      await ngrokLegacy.kill();
    } catch (_err) {
      // Ignore global cleanup errors.
    }
  }

  ngrokTunnelUrl = null;
}

function parseArgs() {
  const deepgramVoices = Object.keys(VALID_VOICES.deepgram).map((voice) => `deepgram/${voice}`);
  const elevenlabsVoices = Object.keys(VALID_VOICES.elevenlabs).map((voice) => `elevenlabs/${voice}`);

  return yargs(hideBin(process.argv))
    .scriptName("telnyx_voice_agent.js")
    .usage("$0 [options]")
    .option("to", {
      type: "string",
      description: "Phone number to call",
    })
    .option("personality", {
      type: "string",
      description: "Agent personality (e.g., 'friendly receptionist at a dental office')",
    })
    .option("task", {
      type: "string",
      description: "Task for this call (e.g., 'confirm appointment for John Smith tomorrow at 3pm')",
    })
    .option("greeting", {
      type: "string",
      description: "Initial greeting message",
    })
    .option("model", {
      type: "string",
      default: DEFAULT_MODEL,
      description: `LLM model to use (default: ${DEFAULT_MODEL})`,
    })
    .option("voice", {
      type: "string",
      default: DEFAULT_VOICE,
      description: `TTS voice as provider/voice-id (default: ${DEFAULT_VOICE})`,
    })
    .option("server-only", {
      type: "boolean",
      default: false,
      description: "Only run server",
    })
    .option("debug", {
      type: "boolean",
      default: false,
      description: "Enable debug logging",
    })
    .option("ngrok", {
      type: "boolean",
      default: false,
      description: "Start ngrok tunnel automatically",
    })
    .option("ngrok-domain", {
      type: "string",
      description: "Custom ngrok domain (requires paid plan)",
    })
    .check((argv) => {
      if (!argv.serverOnly && !argv.to) {
        throw new Error("--to is required unless using --server-only");
      }

      if (!validateModel(argv.model)) {
        throw new Error(`Invalid model '${argv.model}'. Valid models: ${getAllValidModels().join(", ")}`);
      }

      if (!validateVoice(argv.voice)) {
        throw new Error(`Invalid voice '${argv.voice}'. Valid voices: ${getAllValidVoices().join(", ")}`);
      }

      return true;
    })
    .epilog(
      [
        "Available models:",
        `  Anthropic: ${VALID_MODELS.anthropic.join(", ")}`,
        `  OpenAI:    ${VALID_MODELS.open_ai.join(", ")}`,
        "",
        "Available voices (format: provider/voice-id):",
        `  Deepgram:   ${deepgramVoices.slice(0, 4).join(", ")}`,
        `              ${deepgramVoices.slice(4, 8).join(", ")}`,
        `              ${deepgramVoices.slice(8).join(", ")}`,
        `  ElevenLabs: ${elevenlabsVoices.join(", ")}`,
        "",
        `Default model: ${DEFAULT_MODEL}`,
        `Default voice: ${DEFAULT_VOICE}`,
      ].join("\n"),
    )
    .help()
    .strict()
    .parse();
}

async function runServerAndCall(args) {
  initApp({
    personality: args.personality,
    task: args.task,
    greeting: args.greeting,
    model: args.model,
    voice: args.voice,
    serverOnly: args.serverOnly,
  });

  logger.info(`Starting server on ${config.serverHost}:${config.serverPort}`);
  if (config.agentPersonality) {
    logger.info(`Personality: ${config.agentPersonality.slice(0, 50)}...`);
  }
  if (config.agentTask) {
    logger.info(`Task: ${config.agentTask.slice(0, 50)}...`);
  }
  if (config.agentGreeting) {
    logger.info(`Custom greeting: ${config.agentGreeting}`);
  }

  logger.info(`Using model: ${config.agentModel} (${getProviderForModel(config.agentModel)})`);
  logger.info(`Using voice: ${config.agentVoice}`);
  logger.info(`Recordings directory: ${config.recordingsDir}`);

  await startServer();

  if (args.ngrok) {
    try {
      const ngrokUrl = await startNgrok(config.serverPort, args.ngrokDomain || null);
      config.publicWsUrl = ngrokUrl;
    } catch (error) {
      logger.error(`Failed to start ngrok: ${error.message}`);
      return;
    }
  }

  logger.info(`Public URL: ${config.publicWsUrl}`);

  if (!args.serverOnly && args.to) {
    let outboundCallControlId = "";

    try {
      const call = await callManager.initiateCall(args.to);
      outboundCallControlId = call.call_control_id || "";
      logger.info("Call initiated - waiting for call to complete...");
    } catch (error) {
      logger.error(`Call failed: ${error.message}`);
      return;
    }

    await shutdownPromise;
    logger.info("[Server] Shutdown signal received");

    if (outboundCallControlId) {
      await callManager.waitAndPersistRecording(outboundCallControlId, 30000);
    }
  } else {
    logger.info("Server running in server-only mode (press Ctrl+C to exit)");
    await new Promise((resolve) => {
      const handleSignal = () => {
        process.off("SIGINT", handleSignal);
        process.off("SIGTERM", handleSignal);
        resolve();
      };

      process.on("SIGINT", handleSignal);
      process.on("SIGTERM", handleSignal);
    });
  }
}

async function main() {
  const args = parseArgs();

  if (args.debug) {
    logger.setDebug(true);
  }

  try {
    await runServerAndCall(args);
  } catch (error) {
    logger.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
  } finally {
    await stopServer();
    await stopNgrok();
  }
}

void main();
