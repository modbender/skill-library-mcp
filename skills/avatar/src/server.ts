import express, { Request, Response } from 'express';
import type { Server } from 'http';
import { WebSocket } from 'ws';
import crypto from 'crypto';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { loadConfig, getClientConfig, Config, ClientConfig } from './config/index.js';
import { initStreamDeck, BUTTON_PROMPTS, setHasDetail, setLoading, setSpeaking } from './streamdeck.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const isDev = process.env.NODE_ENV !== 'production' && process.argv[1]?.includes('tsx');

// Load configuration
const config: Config = loadConfig();

const PORT = config.app.port;
const GW_URL = config.openclaw.gatewayUrl;

// Generate a stable keypair for device identity
const KEYPAIR_PATH = './device-key.json';

let privateKey: crypto.KeyObject;
let publicKeyRaw: Buffer;
let publicKeyBase64url: string;

function toBase64url(buf: Buffer): string {
  return Buffer.from(buf).toString('base64').replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/g, '');
}

function loadOrCreateKeypair(): void {
  if (existsSync(KEYPAIR_PATH)) {
    const data = JSON.parse(readFileSync(KEYPAIR_PATH, 'utf8'));
    privateKey = crypto.createPrivateKey({
      key: Buffer.from(data.privateDer, 'base64'),
      format: 'der',
      type: 'pkcs8',
    });
    publicKeyRaw = Buffer.from(data.publicRaw, 'base64');
    publicKeyBase64url = toBase64url(publicKeyRaw);
  } else {
    const pair = crypto.generateKeyPairSync('ed25519');
    privateKey = pair.privateKey;
    // Extract raw 32-byte public key from SPKI (last 32 bytes of the DER)
    const spki = pair.publicKey.export({ format: 'der', type: 'spki' });
    publicKeyRaw = spki.subarray(spki.length - 32);
    publicKeyBase64url = toBase64url(publicKeyRaw);
    const privDer = pair.privateKey.export({ format: 'der', type: 'pkcs8' });
    writeFileSync(
      KEYPAIR_PATH,
      JSON.stringify({
        privateDer: privDer.toString('base64'),
        publicRaw: publicKeyRaw.toString('base64'),
      })
    );
  }
}

function signChallenge(nonce: string, signedAt: number): string {
  const deviceId = getDeviceId();
  const token = config.secrets.openclawToken || '';
  const payload = [
    'v2',
    deviceId,
    'webchat',
    'webchat',
    'operator',
    'operator.read,operator.write',
    String(signedAt),
    token,
    nonce,
  ].join('|');
  const sig = crypto.sign(null, Buffer.from(payload), privateKey);
  return toBase64url(sig);
}

function getDeviceId(): string {
  return crypto.createHash('sha256').update(publicKeyRaw).digest('hex');
}

let gwWs: WebSocket | null = null;
let msgId = 1;
let chatResponseResolve: ((value: string) => void) | null = null;
let chatResponseText = '';
let lastDetail: string | null = null;
let lastAlertTs: string | null = null;
let lastAlertChannel: string | null = null;
let isShuttingDown = false;
let gwConnected = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY_MS = 3000;

function connectGateway(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (isShuttingDown) {
      reject(new Error('Server is shutting down'));
      return;
    }

    gwWs = new WebSocket(GW_URL, { headers: { origin: `http://localhost:${PORT}` } });

    gwWs.on('open', () => {
      console.log('GW WS opened, waiting for challenge...');
    });

    let connected = false;
    let challengeNonce: string | null = null;

    gwWs.on('message', (raw) => {
      const data = JSON.parse(raw.toString());

      // Handle challenge
      if (data.type === 'event' && data.event === 'connect.challenge') {
        challengeNonce = data.payload.nonce;
        console.log('Got challenge, signing and connecting...');

        const now = Date.now();
        const signature = signChallenge(challengeNonce!, now);
        const deviceId = getDeviceId();
        const token = config.secrets.openclawToken || '';

        const id = msgId++;
        gwWs!.send(
          JSON.stringify({
            type: 'req',
            id: String(id),
            method: 'connect',
            params: {
              minProtocol: 3,
              maxProtocol: 3,
              client: {
                id: 'webchat',
                version: '1.0.0',
                platform: 'macos',
                mode: 'webchat',
              },
              role: 'operator',
              scopes: ['operator.read', 'operator.write'],
              caps: [],
              commands: [],
              permissions: {},
              auth: { token },
              locale: 'en-US',
              userAgent: `${config.app.name}/1.0`,
              device: {
                id: deviceId,
                publicKey: publicKeyBase64url,
                signature: signature,
                signedAt: now,
                nonce: challengeNonce,
              },
            },
          })
        );
        return;
      }

      // Log all responses
      if (data.type === 'res') {
        console.log('GW response:', JSON.stringify(data).substring(0, 300));
      }

      // Connect response
      if (data.type === 'res' && !connected) {
        if (data.ok) {
          connected = true;
          gwConnected = true;
          reconnectAttempts = 0;
          console.log('Gateway connected!', data.payload?.auth ? '(got device token)' : '');
          resolve();
        } else {
          console.error('Connect failed:', data.error);
          reject(new Error(data.error?.message || 'Connect failed'));
        }
        return;
      }

      // Log all events for debugging
      if (data.type === 'event') {
        console.log('Event:', data.event, JSON.stringify(data.payload || {}).substring(0, 200));
      }

      // Collect text from agent streaming events (avatar session only)
      if (data.type === 'event' && data.event === 'agent') {
        const p = data.payload || {};

        // Streaming text from assistant
        if (p.stream === 'assistant' && p.sessionKey === 'agent:main:avatar' && p.data?.text) {
          chatResponseText = p.data.text;
        }

        // Agent run ended
        const phase = p.data?.phase;
        if (phase === 'end' && p.sessionKey === 'agent:main:avatar' && chatResponseResolve) {
          console.log('Resolving with:', chatResponseText.substring(0, 100));
          chatResponseResolve(chatResponseText);
          chatResponseResolve = null;
          chatResponseText = '';
        }
      }

      // Also catch final chat message as fallback
      if (data.type === 'event' && data.event === 'chat') {
        const p = data.payload || {};
        if (p.state === 'final' && p.sessionKey === 'agent:main:avatar' && p.message?.content) {
          let text = '';
          for (const block of p.message.content) {
            if (block.type === 'text') text += block.text;
          }
          if (text && chatResponseResolve) {
            console.log('Resolving from final chat:', text.substring(0, 100));
            chatResponseResolve(text);
            chatResponseResolve = null;
            chatResponseText = '';
          }
        }
      }
    });

    gwWs.on('error', (err) => {
      console.error('GW WS error:', err.message);
      gwConnected = false;
      reject(err);
    });

    gwWs.on('close', (code, reason) => {
      console.log('GW WS closed:', code, reason.toString());
      gwConnected = false;

      // Attempt reconnection if not shutting down
      if (!isShuttingDown && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`Reconnecting to gateway (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(() => {
          connectGateway()
            .then(() => {
              reconnectAttempts = 0;
              console.log('Reconnected to gateway');
            })
            .catch((err) => {
              console.error('Reconnection failed:', err.message);
            });
        }, RECONNECT_DELAY_MS);
      }
    });
  });
}

function sendChat(text: string): Promise<string> {
  return new Promise((resolve) => {
    chatResponseText = '';
    chatResponseResolve = resolve;

    setTimeout(() => {
      if (chatResponseResolve === resolve) {
        console.log('Chat timeout! No response after 60s. Accumulated text:', chatResponseText.substring(0, 200));
        chatResponseResolve = null;
        resolve(chatResponseText || "Sorry, I couldn't respond in time.");
      }
    }, 60000);

    const id = msgId++;
    const payload = {
      type: 'req',
      id: String(id),
      method: 'chat.send',
      params: {
        sessionKey: 'agent:main:avatar',
        message: text,
        idempotencyKey: crypto.randomUUID(),
      },
    };
    console.log('Sending chat.send:', JSON.stringify(payload).substring(0, 200));
    gwWs!.send(JSON.stringify(payload));
  });
}

async function main(): Promise<void> {
  loadOrCreateKeypair();
  console.log('Device ID:', getDeviceId());
  console.log('Connecting to OpenClaw gateway...');

  await connectGateway();

  const app = express();
  app.use(express.json());

  // Health check endpoint
  app.get('/health', (_req: Request, res: Response) => {
    const status = {
      status: gwConnected ? 'healthy' : 'degraded',
      gateway: gwConnected ? 'connected' : 'disconnected',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    };
    res.status(gwConnected ? 200 : 503).json(status);
  });

  // Readiness check (for k8s)
  app.get('/ready', (_req: Request, res: Response) => {
    if (gwConnected && !isShuttingDown) {
      res.status(200).json({ ready: true });
    } else {
      res.status(503).json({ ready: false, reason: isShuttingDown ? 'shutting_down' : 'gateway_disconnected' });
    }
  });

  // Client config endpoint - safe to expose (no secrets except simli key)
  app.get('/api/client-config', (_req: Request, res: Response) => {
    const clientConfig: ClientConfig = getClientConfig(config);
    res.json(clientConfig);
  });

  app.post('/api/speaking-done', async (_req: Request, res: Response) => {
    await setSpeaking(false);
    res.json({ ok: true });
  });

  app.post('/api/chat', async (req: Request, res: Response) => {
    const { message, lang } = req.body;
    if (!message) {
      res.status(400).json({ error: 'No message' });
      return;
    }

    const isNorwegian = lang && lang.startsWith('nb');
    const langInstruction = isNorwegian
      ? 'LANGUAGE: You MUST respond in Norwegian bokmål (nb-NO). NOT Danish, NOT Swedish — Norwegian bokmål only. Both the <spoken> and <detail> sections must be entirely in Norwegian bokmål.'
      : 'LANGUAGE: Respond in English.';

    try {
      setLoading(true);
      const augmented = `[AVATAR MODE] The user is talking to you through a voice avatar. Read AVATAR-CONTEXT.md for your available tools if you haven't already. Use them to answer questions — you have full access to HubSpot, Gmail, Calendar, Notion, and Slack.

${langInstruction}

RESPONSE FORMAT (MANDATORY — always follow this exactly):

<spoken>
A short conversational summary (1-3 sentences). NO markdown, NO bullet points, NO formatting, NO emoji. Plain speech only.
</spoken>
<detail>
The full detailed response with markdown formatting (bullet points, headers, bold, etc). Always include this section — even for simple answers, provide a clean formatted version.
</detail>

User message: ${message}`;

      const response = await sendChat(augmented);

      // Parse spoken and detail from tagged response
      console.log('Raw response length:', response?.length, 'first 200:', response?.substring(0, 200));
      const spokenMatch = response.match(/<spoken>([\s\S]*?)<\/spoken>/);
      const detailMatch = response.match(/<detail>([\s\S]*?)<\/detail>/);
      const spoken = spokenMatch ? spokenMatch[1].trim() : (response || 'Sorry, I had trouble with that.').trim();
      const detail = detailMatch ? detailMatch[1].trim() : null;

      lastDetail = detail;
      // Stop loading animation
      setLoading(false);
      await new Promise((r) => setTimeout(r, 100));
      setHasDetail(!!detail);
      await new Promise((r) => setTimeout(r, 100));
      setSpeaking(true);
      res.json({ spoken, detail });
    } catch (err) {
      setLoading(false);
      console.error('Chat error:', (err as Error).message);
      res.status(500).json({ error: (err as Error).message });
    }
  });

  // Send to Slack DM
  app.post('/api/send-slack', async (req: Request, res: Response) => {
    const { text } = req.body;
    if (!text) {
      res.status(400).json({ error: 'No text' });
      return;
    }

    if (!config.integrations.slack.enabled) {
      res.status(400).json({ error: 'Slack integration not enabled' });
      return;
    }

    const targets = config.integrations.slack.dmTargets || [];
    const targetStr = targets.join(', ');

    try {
      const response = await sendChat(
        `[SYSTEM] Send the following message via Slack DM to targets: ${targetStr}. Do NOT modify the content, just send it as-is. Reply with just "Sent!" after.\n\n${text}`
      );
      res.json({ ok: true, response });
    } catch (err) {
      res.status(500).json({ error: (err as Error).message });
    }
  });

  // TTS proxy — keeps API key server-side
  app.post('/api/tts', async (req: Request, res: Response) => {
    const { text, lang, voiceId: customVoiceId } = req.body;
    if (!text || !text.trim()) {
      res.status(400).json({ error: 'No text' });
      return;
    }

    // Get voice ID from request, config, or default
    const voiceId = customVoiceId || config.secrets.elevenLabsVoiceId || config.avatars[0]?.voiceId || '21m00Tcm4TlvDq8ikWAM';

    try {
      const isNorwegian = lang && lang.startsWith('nb');
      const ttsBody = isNorwegian
        ? { text, model_id: 'eleven_turbo_v2_5', language_code: 'no' }
        : { text, model_id: 'eleven_multilingual_v2' };

      const ttsRes = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}?output_format=pcm_16000`, {
        method: 'POST',
        headers: {
          'xi-api-key': config.secrets.elevenLabsApiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ttsBody),
      });

      if (!ttsRes.ok) throw new Error(`TTS error: ${ttsRes.status}`);
      const buffer = Buffer.from(await ttsRes.arrayBuffer());
      res.set('Content-Type', 'application/octet-stream');
      res.send(buffer);
    } catch (err) {
      res.status(500).json({ error: (err as Error).message });
    }
  });

  // Send to self via email
  app.post('/api/send-email', async (req: Request, res: Response) => {
    const { text } = req.body;
    if (!text) {
      res.status(400).json({ error: 'No text' });
      return;
    }

    if (!config.integrations.email.enabled || !config.integrations.email.recipient) {
      res.status(400).json({ error: 'Email integration not enabled' });
      return;
    }

    try {
      const response = await sendChat(
        `[SYSTEM] Send the following content to ${config.integrations.email.recipient} as an email from ${config.app.name}. Use a suitable subject line based on the content. Do NOT modify the content. Reply with just "Sent!" after.\n\n${text}`
      );
      res.json({ ok: true, response });
    } catch (err) {
      res.status(500).json({ error: (err as Error).message });
    }
  });

  // Stream Deck integration
  let streamDeckClients: Response[] = [];

  // SSE endpoint for Stream Deck events to reach the browser
  app.get('/api/streamdeck-events', (req: Request, res: Response) => {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    });
    streamDeckClients.push(res);
    req.on('close', () => {
      streamDeckClients = streamDeckClients.filter((c) => c !== res);
    });
  });

  function sendStreamDeckEvent(data: Record<string, unknown>): void {
    console.log(`Sending SSE to ${streamDeckClients.length} client(s):`, JSON.stringify(data));
    for (const client of streamDeckClients) {
      client.write(`data: ${JSON.stringify(data)}\n\n`);
    }
  }

  // Initialize Stream Deck if enabled
  if (config.integrations.streamDeck.enabled) {
    try {
      await initStreamDeck(async (action) => {
        if (!action) return;

        // Send actions — handle server-side using lastDetail
        if (action === 'send_slack' && lastDetail && config.integrations.slack.enabled) {
          sendStreamDeckEvent({ action });
          const targets = config.integrations.slack.dmTargets || [];
          sendChat(
            `[SYSTEM] Send the following message via Slack DM to targets: ${targets.join(', ')}. Do NOT modify the content, just send it as-is. Reply with just "Sent!" after.\n\n${lastDetail}`
          );
          return;
        }

        if (action === 'send_email' && lastDetail && config.integrations.email.enabled) {
          sendStreamDeckEvent({ action });
          sendChat(
            `[SYSTEM] Send the following content to ${config.integrations.email.recipient} as an email from ${config.app.name}. Use a suitable subject line based on the content. Do NOT modify the content. Reply with just "Sent!" after.\n\n${lastDetail}`
          );
          return;
        }

        // Clear detail
        if (action === 'clear') {
          lastDetail = null;
          setHasDetail(false);
          sendStreamDeckEvent({ action: 'clear' });
          return;
        }

        // Follow up on current detail
        if (action === 'followup_detail' && lastDetail) {
          sendStreamDeckEvent({
            action: 'query',
            prompt: 'Based on what you just told me, what should I do next? What are the follow-up actions?',
          });
          return;
        }

        // Draft response based on detail
        if (action === 'draft_detail' && lastDetail) {
          sendStreamDeckEvent({
            action: 'query',
            prompt: 'Based on what you just told me, draft a response or action plan I can send out.',
          });
          return;
        }

        // Alert actions
        if (action === 'interrupt') {
          sendStreamDeckEvent({ action: 'interrupt' });
          setSpeaking(false);
          return;
        }

        if (action === 'alert_send' && config.integrations.slack.enabled && config.secrets.slackBotToken) {
          const alertChannel = config.integrations.slack.alertChannel;
          if (alertChannel) {
            try {
              const slackRes = await fetch('https://slack.com/api/chat.postMessage', {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${config.secrets.slackBotToken}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  channel: alertChannel,
                  text: `Alert from ${config.app.name}! Someone needs help.\nReact with a checkmark when handled.`,
                }),
              });
              const slackData = (await slackRes.json()) as { ok: boolean; ts?: string; channel?: string; error?: string };
              if (slackData.ok) {
                lastAlertTs = slackData.ts || null;
                lastAlertChannel = slackData.channel || null;
                console.log('Alert sent, ts:', lastAlertTs);
              } else {
                console.error('Alert send failed:', slackData.error);
              }
            } catch (e) {
              console.error('Alert error:', e);
            }
          }
          sendStreamDeckEvent({ action: 'speak', text: "Alright, I've alerted the team. Help is on the way!" });
          return;
        }

        if (action === 'alert_resolved' && config.secrets.slackBotToken) {
          if (lastAlertTs && lastAlertChannel) {
            try {
              await fetch('https://slack.com/api/reactions.add', {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${config.secrets.slackBotToken}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  channel: lastAlertChannel,
                  timestamp: lastAlertTs,
                  name: 'white_check_mark',
                }),
              });
              await fetch('https://slack.com/api/chat.postMessage', {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${config.secrets.slackBotToken}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  channel: lastAlertChannel,
                  text: 'Alert resolved — thanks!',
                  thread_ts: lastAlertTs,
                }),
              });
              console.log('Alert resolved');
            } catch (e) {
              console.error('Resolve error:', e);
            }
            lastAlertTs = null;
            lastAlertChannel = null;
          }
          return;
        }

        // Control actions — forward to browser
        if (['stop', 'push_to_talk', 'mute', 'unmute'].includes(action)) {
          sendStreamDeckEvent({ action });
          return;
        }

        // Query actions — send prompt to browser
        const prompt = BUTTON_PROMPTS[action];
        if (prompt) {
          sendStreamDeckEvent({ action: 'query', prompt });
        }
      });
    } catch (err) {
      console.log('Stream Deck init skipped:', (err as Error).message);
    }
  } else {
    console.log('Stream Deck disabled in config');
  }

  // Serve client files
  let vite: { close: () => Promise<void> } | null = null;

  if (isDev) {
    // Development: use Vite dev server with HMR
    const { createServer } = await import('vite');
    const viteServer = await createServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(viteServer.middlewares);
    vite = viteServer;
    console.log('Running in development mode with Vite HMR');
  } else {
    // Production: serve static files from dist/client
    const clientDir = join(__dirname, 'client');
    if (existsSync(clientDir)) {
      app.use(express.static(clientDir));
      // SPA fallback - serve index.html for all non-API routes
      app.get('*', (_req, res) => {
        res.sendFile(join(clientDir, 'index.html'));
      });
      console.log('Running in production mode, serving static files');
    } else {
      console.warn('Warning: dist/client not found. Run "npm run build" first.');
    }
  }

  const server: Server = app.listen(PORT, () => {
    console.log(`${config.app.name} running at http://localhost:${PORT}`);
  });

  // Graceful shutdown handling
  const shutdown = async (signal: string): Promise<void> => {
    if (isShuttingDown) return;
    isShuttingDown = true;
    console.log(`\n${signal} received, shutting down gracefully...`);

    // Close WebSocket connection
    if (gwWs) {
      try {
        gwWs.close();
      } catch {
        // Ignore errors during shutdown
      }
    }

    // Close Vite server if running
    if (vite) {
      try {
        await vite.close();
      } catch {
        // Ignore errors during shutdown
      }
    }

    // Close HTTP server with timeout
    const forceShutdownTimeout = setTimeout(() => {
      console.log('Forcing shutdown after timeout');
      process.exit(1);
    }, 10000);

    server.close((err) => {
      clearTimeout(forceShutdownTimeout);
      if (err) {
        console.error('Error during shutdown:', err);
        process.exit(1);
      }
      console.log('Server closed');
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
