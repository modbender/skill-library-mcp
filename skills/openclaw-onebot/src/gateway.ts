import WebSocket from "ws";
import { exec } from "node:child_process";
import { writeFile, readFile, unlink, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { promisify } from "node:util";
import type {
  ResolvedOneBotAccount,
  OneBotEvent,
  OneBotMessageEvent,
  OneBotMessageSegment,
} from "./types.js";
import { getOneBotRuntime } from "./runtime.js";
import { sendText as sendOutboundText, sendImage, sendRecord } from "./outbound.js";

const execAsync = promisify(exec);

// Reconnect configuration
const RECONNECT_DELAYS = [1000, 2000, 5000, 10000, 30000, 60000];
const MAX_RECONNECT_ATTEMPTS = 100;

// Message batching — aligned with telegram text fragment gap
const BATCH_GAP_MS = 1500;
const BATCH_MAX_MESSAGES = 12;
const BATCH_MAX_CHARS = 50000;

// Voice processing
const VOICE_TMP_DIR = join(tmpdir(), "openclaw-onebot-voice");
const EXEC_PATH = `/opt/homebrew/bin:/usr/local/bin:${process.env.PATH || "/usr/bin:/bin"}`;

export interface GatewayContext {
  account: ResolvedOneBotAccount;
  abortSignal: AbortSignal;
  cfg: unknown;
  onReady?: (data: unknown) => void;
  onError?: (error: Error) => void;
  log?: {
    info: (msg: string) => void;
    error: (msg: string) => void;
    debug?: (msg: string) => void;
  };
}

// ── Text / image extraction ──

function extractText(segments: OneBotMessageSegment[]): string {
  return segments
    .filter((seg) => seg.type === "text")
    .map((seg) => String(seg.data.text ?? ""))
    .join("");
}

function extractImages(segments: OneBotMessageSegment[]): string[] {
  return segments
    .filter((seg) => seg.type === "image")
    .map((seg) => String(seg.data.url ?? seg.data.file ?? ""))
    .filter(Boolean);
}

function extractRecordSegments(segments: OneBotMessageSegment[]): OneBotMessageSegment[] {
  return segments.filter((seg) => seg.type === "record");
}

// ── Voice processing ──

function isSilkFormat(buf: Buffer): boolean {
  // SILK files: optional 0x02 prefix byte, then "#!SILK"
  const h = buf.toString("utf-8", 0, 10);
  return h.includes("#!SILK");
}

function isAmrFormat(buf: Buffer): boolean {
  const h = buf.toString("utf-8", 0, 6);
  return h.startsWith("#!AMR");
}

async function ensureVoiceTmpDir(): Promise<void> {
  await mkdir(VOICE_TMP_DIR, { recursive: true });
}

async function downloadVoiceFile(
  url: string,
  log?: GatewayContext["log"],
): Promise<string | null> {
  try {
    await ensureVoiceTmpDir();
    const response = await fetch(url);
    if (!response.ok) {
      log?.error(`Voice download failed: ${response.status}`);
      return null;
    }
    const buffer = Buffer.from(await response.arrayBuffer());
    if (buffer.length === 0) {
      log?.error("Voice download returned empty file");
      return null;
    }
    const suffix = isSilkFormat(buffer) ? ".silk" : isAmrFormat(buffer) ? ".amr" : ".ogg";
    const filePath = join(
      VOICE_TMP_DIR,
      `voice-${Date.now()}-${Math.random().toString(36).slice(2, 8)}${suffix}`,
    );
    await writeFile(filePath, buffer);
    log?.debug?.(`Downloaded voice: ${filePath} (${buffer.length} bytes)`);
    return filePath;
  } catch (err) {
    log?.error(`Voice download error: ${err}`);
    return null;
  }
}

async function convertSilkToMp3(
  silkPath: string,
  log?: GatewayContext["log"],
): Promise<string | null> {
  const pcmPath = silkPath.replace(/\.[^.]+$/, ".pcm");
  const mp3Path = silkPath.replace(/\.[^.]+$/, ".mp3");
  try {
    // silk → pcm via pilk
    await execAsync(
      `uv run --with pilk python3 -c "import pilk; pilk.decode('${silkPath}', '${pcmPath}')"`,
      { env: { ...process.env, PATH: EXEC_PATH }, timeout: 15000 },
    );
    // pcm → mp3 (silk is typically 24000Hz mono 16-bit LE)
    await execAsync(
      `ffmpeg -y -f s16le -ar 24000 -ac 1 -i "${pcmPath}" "${mp3Path}"`,
      { env: { ...process.env, PATH: EXEC_PATH }, timeout: 10000 },
    );
    try { await unlink(pcmPath); } catch { /* ignore */ }
    if (existsSync(mp3Path)) {
      log?.info(`SILK → mp3 OK: ${mp3Path}`);
      try { await unlink(silkPath); } catch { /* ignore */ }
      return mp3Path;
    }
    return null;
  } catch (err) {
    log?.error(`SILK conversion failed: ${err}`);
    try { await unlink(pcmPath); } catch { /* ignore */ }
    return null;
  }
}

async function convertAmrToMp3(
  amrPath: string,
  log?: GatewayContext["log"],
): Promise<string | null> {
  const mp3Path = amrPath.replace(/\.[^.]+$/, ".mp3");
  try {
    await execAsync(
      `ffmpeg -y -i "${amrPath}" -ar 16000 -ac 1 "${mp3Path}"`,
      { env: { ...process.env, PATH: EXEC_PATH }, timeout: 10000 },
    );
    if (existsSync(mp3Path)) {
      log?.info(`AMR → mp3 OK: ${mp3Path}`);
      try { await unlink(amrPath); } catch { /* ignore */ }
      return mp3Path;
    }
    return null;
  } catch (err) {
    log?.error(`AMR conversion failed: ${err}`);
    return null;
  }
}

async function processVoiceSegments(
  segments: OneBotMessageSegment[],
  log?: GatewayContext["log"],
): Promise<{ path: string; contentType: string }[]> {
  const results: { path: string; contentType: string }[] = [];
  for (const seg of segments) {
    const url = String(seg.data.url ?? seg.data.file ?? "");
    log?.info(`[voice] segment data: url=${seg.data.url}, file=${seg.data.file}, resolved=${url.slice(0, 200)}`);
    if (!url) continue;

    let filePath: string | null = null;
    if (url.startsWith("http")) {
      filePath = await downloadVoiceFile(url, log);
    } else {
      const localPath = url.replace(/^file:\/\//, "");
      if (existsSync(localPath)) filePath = localPath;
    }
    if (!filePath) continue;

    try {
      const buf = await readFile(filePath);
      const hexHead = buf.subarray(0, 16).toString("hex");
      log?.info(`[voice] file=${filePath} size=${buf.length} hex=${hexHead} isSilk=${isSilkFormat(buf)} isAmr=${isAmrFormat(buf)}`);
      if (isSilkFormat(buf)) {
        const mp3 = await convertSilkToMp3(filePath, log);
        if (mp3) results.push({ path: mp3, contentType: "audio/mpeg" });
      } else if (isAmrFormat(buf)) {
        const mp3 = await convertAmrToMp3(filePath, log);
        if (mp3) results.push({ path: mp3, contentType: "audio/mpeg" });
      } else {
        let ct = "audio/ogg";
        if (filePath.endsWith(".mp3")) ct = "audio/mpeg";
        else if (filePath.endsWith(".wav")) ct = "audio/wav";
        else if (filePath.endsWith(".amr")) ct = "audio/amr";
        results.push({ path: filePath, contentType: ct });
      }
    } catch (err) {
      log?.error(`Voice processing error: ${err}`);
    }
  }
  return results;
}

function cleanupVoiceFiles(paths: string[]): void {
  for (const p of paths) {
    unlink(p).catch(() => { /* ignore */ });
  }
}

// ── Message batching ──

interface BufferedMessage {
  event: OneBotMessageEvent;
  text: string;
  images: string[];
  recordSegments: OneBotMessageSegment[];
}

interface ChatBatch {
  messages: BufferedMessage[];
  timer: ReturnType<typeof setTimeout>;
  totalChars: number;
}

// ── Gateway ──

export async function startGateway(ctx: GatewayContext): Promise<void> {
  const { account, abortSignal, cfg, onReady, onError, log } = ctx;

  if (!account.wsUrl) {
    throw new Error("OneBot not configured (missing wsUrl)");
  }

  let reconnectAttempts = 0;
  let isAborted = false;
  let currentWs: WebSocket | null = null;
  let isConnecting = false;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  // Per-chat message batch buffers
  const chatBatches = new Map<string, ChatBatch>();

  abortSignal.addEventListener("abort", () => {
    isAborted = true;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    // Flush all pending batches
    for (const [key, batch] of chatBatches) {
      clearTimeout(batch.timer);
      chatBatches.delete(key);
    }
    cleanup();
  });

  const cleanup = () => {
    if (currentWs && (currentWs.readyState === WebSocket.OPEN || currentWs.readyState === WebSocket.CONNECTING)) {
      currentWs.close();
    }
    currentWs = null;
  };

  const getReconnectDelay = () => {
    const idx = Math.min(reconnectAttempts, RECONNECT_DELAYS.length - 1);
    return RECONNECT_DELAYS[idx];
  };

  const scheduleReconnect = (customDelay?: number) => {
    if (isAborted || reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      log?.error(`[onebot:${account.accountId}] Max reconnect attempts reached or aborted`);
      return;
    }

    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    const delay = customDelay ?? getReconnectDelay();
    reconnectAttempts++;
    log?.info(`[onebot:${account.accountId}] Reconnecting in ${delay}ms (attempt ${reconnectAttempts})`);

    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      if (!isAborted) {
        connect();
      }
    }, delay);
  };

  const connect = async () => {
    if (isConnecting) {
      log?.debug?.(`[onebot:${account.accountId}] Already connecting, skip`);
      return;
    }
    isConnecting = true;

    try {
      cleanup();

      const wsUrl = account.wsUrl;
      const wsOptions: WebSocket.ClientOptions = {};

      let connectUrl = wsUrl;
      if (account.accessToken) {
        const separator = wsUrl.includes("?") ? "&" : "?";
        connectUrl = `${wsUrl}${separator}access_token=${account.accessToken}`;
      }

      log?.info(`[onebot:${account.accountId}] Connecting to ${wsUrl}`);

      const ws = new WebSocket(connectUrl, wsOptions);
      currentWs = ws;

      const pluginRuntime = getOneBotRuntime();

      // ── Dispatch a (possibly batched) set of messages ──

      const dispatchMessages = async (batchKey: string, messages: BufferedMessage[]) => {
        if (messages.length === 0) return;

        const first = messages[0];
        const last = messages[messages.length - 1];
        const event = first.event;
        const isGroup = event.message_type === "group";
        const senderId = String(event.user_id);
        const senderName = event.sender.card || event.sender.nickname || senderId;

        // Combine text, images, and record segments from all buffered messages
        const combinedText = messages.map((m) => m.text).filter(Boolean).join("\n");
        const combinedImages = messages.flatMap((m) => m.images);
        const combinedRecordSegs = messages.flatMap((m) => m.recordSegments);

        if (messages.length > 1) {
          log?.info(
            `[onebot:${account.accountId}] Batched ${messages.length} messages from ${senderName}: ${combinedText.slice(0, 100)}`,
          );
        }

        pluginRuntime.channel.activity.record({
          channel: "onebot",
          accountId: account.accountId,
          direction: "inbound",
        });

        const peerId = isGroup ? `group:${event.group_id}` : `private:${senderId}`;

        const route = pluginRuntime.channel.routing.resolveAgentRoute({
          cfg,
          channel: "onebot",
          accountId: account.accountId,
          peer: {
            kind: isGroup ? "group" : "dm",
            id: peerId,
          },
        });

        const envelopeOptions = pluginRuntime.channel.reply.resolveEnvelopeFormatOptions(cfg);

        // Process voice segments → download, convert SILK, get local paths
        const voiceMedia = await processVoiceSegments(combinedRecordSegs, log);
        const voiceFilePaths = voiceMedia.map((v) => v.path);

        // Build text body — images as placeholders, voice handled via MediaPath
        let attachmentInfo = "";
        for (const img of combinedImages) {
          attachmentInfo += `\n[Image: ${img}]`;
        }
        if (voiceMedia.length > 0) {
          attachmentInfo += "\n<media:audio>";
        } else if (combinedRecordSegs.length > 0) {
          // Voice download/conversion failed — add text placeholder
          attachmentInfo += "\n[语音]";
        }

        const userContent = combinedText + attachmentInfo;

        const body = pluginRuntime.channel.reply.formatInboundEnvelope({
          channel: "OneBot",
          from: senderName,
          timestamp: last.event.time * 1000,
          body: userContent,
          chatType: isGroup ? "group" : "direct",
          sender: {
            id: senderId,
            name: senderName,
          },
          envelope: envelopeOptions,
          ...(combinedImages.length > 0 ? { imageUrls: combinedImages } : {}),
        });

        const fromAddress = isGroup
          ? `onebot:group:${event.group_id}`
          : `onebot:private:${senderId}`;
        const toAddress = fromAddress;

        // Build media payload for the platform's unified audio pipeline
        const mediaPayload: Record<string, unknown> = {};
        if (voiceMedia.length > 0) {
          mediaPayload.MediaPath = voiceMedia[0].path;
          mediaPayload.MediaType = voiceMedia[0].contentType;
          mediaPayload.MediaUrl = voiceMedia[0].path;
          if (voiceMedia.length > 1) {
            mediaPayload.MediaPaths = voiceMedia.map((v) => v.path);
            mediaPayload.MediaTypes = voiceMedia.map((v) => v.contentType);
            mediaPayload.MediaUrls = voiceMedia.map((v) => v.path);
          }
        }

        const ctxPayload = pluginRuntime.channel.reply.finalizeInboundContext({
          Body: body,
          RawBody: combinedText,
          CommandBody: combinedText,
          From: fromAddress,
          To: toAddress,
          SessionKey: route.sessionKey,
          AccountId: route.accountId,
          ChatType: isGroup ? "group" : "direct",
          SenderId: senderId,
          SenderName: senderName,
          Provider: "onebot",
          Surface: "onebot",
          MessageSid: String(last.event.message_id),
          Timestamp: last.event.time * 1000,
          OriginatingChannel: "onebot",
          OriginatingTo: toAddress,
          ...mediaPayload,
        });

        log?.info(
          `[onebot:${account.accountId}] ctxPayload: From=${fromAddress}, SessionKey=${route.sessionKey}, ChatType=${isGroup ? "group" : "direct"}, hasAudio=${voiceMedia.length > 0}`,
        );

        const sendErrorMessage = async (errorText: string) => {
          try {
            await sendOutboundText({ to: fromAddress, text: errorText, account });
          } catch (sendErr) {
            log?.error(`[onebot:${account.accountId}] Failed to send error message: ${sendErr}`);
          }
        };

        try {
          const messagesConfig = pluginRuntime.channel.reply.resolveEffectiveMessagesConfig(cfg, route.agentId);

          let hasResponse = false;
          const responseTimeout = 90000;
          let timeoutId: ReturnType<typeof setTimeout> | null = null;

          const timeoutPromise = new Promise<void>((_, reject) => {
            timeoutId = setTimeout(() => {
              if (!hasResponse) reject(new Error("Response timeout"));
            }, responseTimeout);
          });

          const dispatchPromise = pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher({
            ctx: ctxPayload,
            cfg,
            dispatcherOptions: {
              responsePrefix: messagesConfig.responsePrefix,
              deliver: async (
                payload: { text?: string; mediaUrls?: string[]; mediaUrl?: string },
                info: { kind: string },
              ) => {
                hasResponse = true;
                if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; }

                log?.info(
                  `[onebot:${account.accountId}] deliver(${info.kind}): textLen=${payload.text?.length ?? 0}`,
                );

                let replyText = payload.text ?? "";

                const mediaPaths: string[] = [];
                if (payload.mediaUrls?.length) mediaPaths.push(...payload.mediaUrls);
                if (payload.mediaUrl && !mediaPaths.includes(payload.mediaUrl)) {
                  mediaPaths.push(payload.mediaUrl);
                }

                const AUDIO_EXTS = new Set([".mp3", ".ogg", ".wav", ".m4a", ".flac", ".aac", ".opus", ".amr", ".silk"]);
                for (const mediaPath of mediaPaths) {
                  try {
                    const targetType = isGroup ? "group" as const : "private" as const;
                    const targetId = isGroup ? event.group_id! : event.user_id;
                    const ext = mediaPath.toLowerCase().replace(/.*(\.[^.]+)$/, "$1");
                    if (AUDIO_EXTS.has(ext)) {
                      await sendRecord(account, targetType, targetId, mediaPath);
                      log?.info(`[onebot:${account.accountId}] Sent voice: ${mediaPath}`);
                    } else {
                      await sendImage(account, targetType, targetId, mediaPath);
                      log?.info(`[onebot:${account.accountId}] Sent media: ${mediaPath}`);
                    }
                  } catch (err) {
                    log?.error(`[onebot:${account.accountId}] Media send failed: ${err}`);
                  }
                }

                if (replyText.trim()) {
                  try {
                    await sendOutboundText({ to: fromAddress, text: replyText, account });
                    pluginRuntime.channel.activity.record({
                      channel: "onebot",
                      accountId: account.accountId,
                      direction: "outbound",
                    });
                  } catch (err) {
                    log?.error(`[onebot:${account.accountId}] Send failed: ${err}`);
                  }
                }
              },
              onError: async (err: unknown) => {
                log?.error(`[onebot:${account.accountId}] Dispatch error: ${err}`);
                hasResponse = true;
                if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; }
                await sendErrorMessage(`[OpenClaw] Error: ${String(err).slice(0, 500)}`);
              },
            },
            replyOptions: {},
          });

          try {
            await Promise.race([dispatchPromise, timeoutPromise]);
          } catch (err) {
            if (timeoutId) clearTimeout(timeoutId);
            if (!hasResponse) {
              log?.error(`[onebot:${account.accountId}] No response within timeout`);
              await sendErrorMessage("[OpenClaw] Request received, processing...");
            }
          }
        } catch (err) {
          log?.error(`[onebot:${account.accountId}] Message processing failed: ${err}`);
          await sendErrorMessage(`[OpenClaw] Processing failed: ${String(err).slice(0, 500)}`);
        } finally {
          // Cleanup temp voice files after dispatch
          cleanupVoiceFiles(voiceFilePaths);
        }
      };

      // ── Buffer an incoming message and debounce dispatch ──

      const bufferMessage = (event: OneBotMessageEvent) => {
        const isGroup = event.message_type === "group";
        const senderId = String(event.user_id);
        const senderName = event.sender.card || event.sender.nickname || senderId;
        const text = extractText(event.message) || event.raw_message;
        const images = extractImages(event.message);
        const recordSegments = extractRecordSegments(event.message);

        // allowFrom check
        const peerId = isGroup ? `group:${event.group_id}` : `private:${senderId}`;
        if (account.allowFrom && account.allowFrom.length > 0) {
          if (!account.allowFrom.some((pattern) => peerId === pattern || pattern === "*")) {
            log?.debug?.(`[onebot:${account.accountId}] Ignoring message from unlisted ${peerId}`);
            return;
          }
        }

        // Skip own messages
        if (event.user_id === event.self_id) return;

        log?.info(
          `[onebot:${account.accountId}] ${isGroup ? "Group" : "Private"} message from ${senderName}(${senderId}): ${text.slice(0, 100)}`,
        );

        // Batch key: per-chat + per-sender for groups
        const batchKey = isGroup
          ? `group:${event.group_id}::${senderId}`
          : `private:${senderId}`;

        const buffered: BufferedMessage = { event, text, images, recordSegments };

        const existing = chatBatches.get(batchKey);
        if (existing) {
          // Check limits
          if (
            existing.messages.length >= BATCH_MAX_MESSAGES ||
            existing.totalChars + text.length > BATCH_MAX_CHARS
          ) {
            // Flush current batch immediately, then start new one
            clearTimeout(existing.timer);
            chatBatches.delete(batchKey);
            dispatchMessages(batchKey, existing.messages).catch((err) =>
              log?.error(`[onebot:${account.accountId}] Batch dispatch error: ${err}`),
            );
            // Start fresh batch with this message
            const timer = setTimeout(() => {
              const batch = chatBatches.get(batchKey);
              if (batch) {
                chatBatches.delete(batchKey);
                dispatchMessages(batchKey, batch.messages).catch((err) =>
                  log?.error(`[onebot:${account.accountId}] Batch dispatch error: ${err}`),
                );
              }
            }, BATCH_GAP_MS);
            chatBatches.set(batchKey, {
              messages: [buffered],
              timer,
              totalChars: text.length,
            });
          } else {
            // Append to existing batch and reset timer
            existing.messages.push(buffered);
            existing.totalChars += text.length;
            clearTimeout(existing.timer);
            existing.timer = setTimeout(() => {
              const batch = chatBatches.get(batchKey);
              if (batch) {
                chatBatches.delete(batchKey);
                dispatchMessages(batchKey, batch.messages).catch((err) =>
                  log?.error(`[onebot:${account.accountId}] Batch dispatch error: ${err}`),
                );
              }
            }, BATCH_GAP_MS);
          }
        } else {
          // New batch
          const timer = setTimeout(() => {
            const batch = chatBatches.get(batchKey);
            if (batch) {
              chatBatches.delete(batchKey);
              dispatchMessages(batchKey, batch.messages).catch((err) =>
                log?.error(`[onebot:${account.accountId}] Batch dispatch error: ${err}`),
              );
            }
          }, BATCH_GAP_MS);
          chatBatches.set(batchKey, {
            messages: [buffered],
            timer,
            totalChars: text.length,
          });
        }
      };

      ws.on("open", () => {
        log?.info(`[onebot:${account.accountId}] WebSocket connected`);
        isConnecting = false;
        reconnectAttempts = 0;
        onReady?.({});
      });

      ws.on("message", async (data) => {
        try {
          const rawData = data.toString();
          const event = JSON.parse(rawData) as OneBotEvent;

          log?.debug?.(`[onebot:${account.accountId}] Event: post_type=${event.post_type}`);

          switch (event.post_type) {
            case "meta_event":
              if (event.meta_event_type === "lifecycle" && event.sub_type === "connect") {
                log?.info(`[onebot:${account.accountId}] Lifecycle: connected`);
              }
              break;

            case "message":
              bufferMessage(event as OneBotMessageEvent);
              break;

            case "notice":
              log?.debug?.(`[onebot:${account.accountId}] Notice: ${(event as { notice_type?: string }).notice_type}`);
              break;
          }
        } catch (err) {
          log?.error(`[onebot:${account.accountId}] Message parse error: ${err}`);
        }
      });

      ws.on("close", (code, reason) => {
        log?.info(`[onebot:${account.accountId}] WebSocket closed: ${code} ${reason.toString()}`);
        isConnecting = false;
        cleanup();

        if (!isAborted && code !== 1000) {
          scheduleReconnect();
        }
      });

      ws.on("error", (err) => {
        log?.error(`[onebot:${account.accountId}] WebSocket error: ${err.message}`);
        isConnecting = false;
        onError?.(err);
      });
    } catch (err) {
      isConnecting = false;
      log?.error(`[onebot:${account.accountId}] Connection failed: ${err}`);
      scheduleReconnect();
    }
  };

  // Start connection
  await connect();

  // Wait for abort signal
  return new Promise((resolve) => {
    abortSignal.addEventListener("abort", () => resolve());
  });
}
