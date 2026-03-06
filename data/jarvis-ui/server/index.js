// ── JARVIS 後端入口 ──

import express from 'express';
import path from 'path';
import os from 'os';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';

import { initGateway, gwRequest } from './gateway.js';
import { addClient, removeClient, broadcastChat } from './sse.js';
import { initTTS } from './tts.js';
import { startSystemMonitor } from './system-monitor.js';

// Routes
import chatRoutes from './routes/chat.js';
import statusRoutes from './routes/status.js';
import ttsRoutes from './routes/tts-routes.js';
import tasksRoutes from './routes/tasks.js';
import skillsRoutes from './routes/skills.js';
import memoryRoutes from './routes/memory.js';
import scheduleRoutes from './routes/schedule.js';
import voiceRoutes from './routes/voice.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// ── 讀取設定 ──
let config;
try {
  config = JSON.parse(await readFile(path.join(ROOT, 'config.local.json'), 'utf-8'));
} catch {
  config = JSON.parse(await readFile(path.join(ROOT, 'config.json'), 'utf-8'));
}

const GATEWAY_URL = process.env.GATEWAY_URL || config.server.gatewayUrl;
const GATEWAY_TOKEN = process.env.GATEWAY_TOKEN;
if (!GATEWAY_TOKEN) { console.error('[JARVIS] GATEWAY_TOKEN env is required'); process.exit(1); }
const PORT = process.env.PORT || config.server.port;
const SERVE_STATIC = process.env.SERVE_STATIC !== 'false';
const SESSION_KEY = config.agent.sessionKey;
const OC_CONFIG = path.join(os.homedir(), '.openclaw', 'openclaw.json');

// ── Express ──
const app = express();
app.use(express.json());

// 共享 sessionKey 供路由使用
app.locals.sessionKey = SESSION_KEY;

// ── SSE ──
app.get('/api/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache',
    Connection: 'keep-alive', 'Access-Control-Allow-Origin': '*',
  });
  res.write('data: {"type":"connected"}\n\n');
  addClient(res);
  req.on('close', () => removeClient(res));
});

// ── 掛載路由 ──
app.use('/api', chatRoutes);
app.use('/api', statusRoutes(config, OC_CONFIG));
app.use('/api', ttsRoutes);
app.use('/api', tasksRoutes);
app.use('/api', skillsRoutes);
app.use('/api', memoryRoutes);
app.use('/api', scheduleRoutes);
app.use('/api', voiceRoutes);

// ── 靜態檔案 ──
if (SERVE_STATIC) {
  const distPath = path.join(ROOT, 'dist');
  app.use(express.static(distPath));
  app.get('/{*splat}', (req, res) => res.sendFile(path.join(distPath, 'index.html')));
}

// ── 初始化 ──
initTTS(config.tts);
initGateway({ url: GATEWAY_URL, token: GATEWAY_TOKEN, sessionKey: SESSION_KEY, onChat: broadcastChat });
startSystemMonitor();

app.listen(PORT, () => {
  console.log(`[JARVIS] API server on http://localhost:${PORT}`);
  if (SERVE_STATIC) console.log(`[JARVIS] Serving static files from dist/`);
});
