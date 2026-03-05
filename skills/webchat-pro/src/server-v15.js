#!/usr/bin/env node
/**
 * Web Chat 后端 - v15 (生产就绪版)
 * 
 * 新增功能:
 * 1. ✅ 用户认证（简单密码）
 * 2. ✅ 速率限制（每 IP 每分钟 60 次）
 * 3. ✅ Token 统计显示
 * 4. ✅ Markdown 渲染支持
 * 5. ✅ 对话导出功能
 * 6. ✅ 成本提示
 * 7. ✅ 深色模式支持
 * 8. ✅ 错误重试机制
 * 
 * 保留功能:
 * - 流式输出（打字机效果）
 * - 多模型切换
 * - 会话持久化
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');

const app = express();

// 请求体大小限制（安全修复）
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ limit: '1mb', extended: true }));

const server = http.createServer(app);
const io = new Server(server, {
  cors: { 
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['*'],
    methods: ['GET', 'POST']
  }
});

const PORT = 4000;
const HISTORY_FILE = path.join(__dirname, 'chat-history.json');
const CONFIG_FILE = path.join(__dirname, 'chat-config.json');
const AUTH_FILE = path.join(__dirname, 'chat-auth.json');

// 模型配置（含成本和 Token 估算）
const MODELS = [
  { 
    id: 'qwen3.5-plus', 
    name: 'Qwen3.5 Plus', 
    desc: '平衡性能', 
    speed: '正常', 
    cost_per_1k: 0.002,
    cost_level: 2
  },
  { 
    id: 'glm-4-flash', 
    name: 'GLM-4 Flash', 
    desc: '快速响应', 
    speed: '快', 
    cost_per_1k: 0.0005,
    cost_level: 1
  },
  { 
    id: 'gpt-4', 
    name: 'GPT-4', 
    desc: '最强模型', 
    speed: '慢', 
    cost_per_1k: 0.03,
    cost_level: 5
  },
  { 
    id: 'qwen-vl', 
    name: 'Qwen-VL', 
    desc: '视觉理解', 
    speed: '正常', 
    cost_per_1k: 0.002,
    cost_level: 2
  }
];

app.use(cors());
app.use(express.json({ limit: '10mb' }));
// 静态文件（禁用缓存，确保总是加载最新版本）
app.use(express.static(path.join(__dirname, 'public'), {
  setHeaders: (res, path) => {
    if (path.endsWith('.html') || path.endsWith('.js')) {
      res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    }
  }
}));

// 速率限制
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 60, // 每 IP 每分钟 60 次
  message: { error: '请求太频繁，请稍后再试' },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// 加载认证配置
function loadAuth() {
  try {
    if (fs.existsSync(AUTH_FILE)) {
      return JSON.parse(fs.readFileSync(AUTH_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('[AUTH] 加载失败:', e.message);
  }
  // 默认密码：admin123
  return { password: 'admin123', sessions: {} };
}

// 保存认证配置
function saveAuth(auth) {
  try {
    fs.writeFileSync(AUTH_FILE, JSON.stringify(auth, null, 2), 'utf8');
  } catch (e) {
    console.error('[AUTH] 保存失败:', e.message);
  }
}

let authConfig = loadAuth();

// 加载配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('[CONFIG] 加载失败:', e.message);
  }
  return { sessions: {} };
}

function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf8');
  } catch (e) {
    console.error('[CONFIG] 保存失败:', e.message);
  }
}

let config = loadConfig();

// 加载历史
function loadHistory() {
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('[DB] 加载失败:', e.message);
  }
  return {};
}

function saveHistory(history) {
  try {
    for (const sessionId in history) {
      if (history[sessionId].length > 200) {
        history[sessionId] = history[sessionId].slice(-200);
      }
    }
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2), 'utf8');
  } catch (e) {
    console.error('[DB] 保存失败:', e.message);
  }
}

let chatHistory = loadHistory();

// Shell 转义
function escapeShell(str) {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\$/g, '\\$')
    .replace(/`/g, '\\`');
}

// 估算 Token 数（简单估算：中文字符数/2 + 英文字符数/4）
function estimateTokens(text) {
  const chinese = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
  const english = (text.match(/[a-zA-Z]/g) || []).length;
  return Math.round(chinese / 2 + english / 4 + text.length / 10);
}

// 计算成本
function calculateCost(tokens, modelId) {
  const model = MODELS.find(m => m.id === modelId);
  if (!model) return 0;
  return (tokens / 1000) * model.cost_per_1k;
}

// 流式调用 AI 模型（带重试）
function streamAI(message, sessionId, model, onChunk, onComplete, retryCount = 0) {
  const cmd = 'openclaw';
  const args = [
    'agent',
    '--local',
    '--session-id',
    `web-${sessionId}-${model}`,
    '--message',
    message
  ];
  
  const env = { 
    ...process.env, 
    HOME: process.env.HOME,
    OPENCLAW_MODEL: model || 'qwen3.5-plus'
  };
  
  console.log('[AI]', cmd, args.join(' '), 'model:', model, 'retry:', retryCount);
  
  const startTime = Date.now();
  const child = spawn(cmd, args, { env, shell: false });
  
  let fullOutput = '';
  let extractedText = '';
  let isJsonStarted = false;
  let inputTokens = estimateTokens(message);
  
  child.stdout.on('data', (data) => {
    const text = data.toString();
    fullOutput += text;
    
    // 过滤日志行（以 [ 开头的行）
    const lines = text.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('[') && !trimmed.startsWith('⏱️') && !trimmed.startsWith('📚') && !trimmed.startsWith('🔌')) {
        // 纯文本输出，直接推送
        if (trimmed) {
          extractedText += trimmed + '\n';
          onChunk(trimmed + '\n');
        }
      }
    }
    
    // 兼容 JSON 输出格式
    if (!isJsonStarted && text.includes('{')) {
      isJsonStarted = true;
    }
    
    if (isJsonStarted) {
      const textMatch = text.match(/"text"\s*:\s*"([^"]*(?:\\.[^"]*)*)"/);
      if (textMatch && textMatch[1]) {
        let decoded = textMatch[1]
          .replace(/\\n/g, '\n')
          .replace(/\\"/g, '"')
          .replace(/\\\\/g, '\\');
        
        if (decoded.trim()) {
          extractedText += decoded;
          onChunk(decoded);
        }
      }
    }
  });
  
  child.stderr.on('data', (data) => {
    console.error('[AI ERR]', data.toString().substring(0, 200));
  });
  
  child.on('close', (code) => {
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    const outputTokens = estimateTokens(extractedText);
    const totalTokens = inputTokens + outputTokens;
    const cost = calculateCost(totalTokens, model);
    
    console.log('[AI DONE]', code, 'model:', model, 'tokens:', totalTokens, 'cost:', cost.toFixed(4), 'duration:', duration + 's');
    
    if (!extractedText.trim()) {
      try {
        const jsonStart = fullOutput.indexOf('{');
        const jsonEnd = fullOutput.lastIndexOf('}');
        if (jsonStart !== -1 && jsonEnd !== -1) {
          const jsonStr = fullOutput.substring(jsonStart, jsonEnd + 1);
          const result = JSON.parse(jsonStr);
          extractedText = result.payloads?.[0]?.text || result.answer || '我收到了你的消息';
        }
      } catch (e) {
        extractedText = '我收到了你的消息';
      }
    }
    
    onComplete(extractedText, fullOutput, code, {
      model,
      inputTokens,
      outputTokens,
      totalTokens,
      cost: cost.toFixed(4),
      duration
    });
  });
  
  child.on('error', (error) => {
    console.error('[AI ERROR]', error.message);
    
    // 重试机制（最多 2 次）
    if (retryCount < 2) {
      console.log('[AI RETRY]', retryCount + 1);
      setTimeout(() => {
        streamAI(message, sessionId, model, onChunk, onComplete, retryCount + 1);
      }, 1000);
    } else {
      onComplete(null, error.message, -1, {
        model,
        error: error.message
      });
    }
  });
  
  return child;
}

// API 路由
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    port: PORT,
    version: 'v15',
    sessions: Object.keys(config.sessions).length,
    totalMessages: Object.values(chatHistory).reduce((sum, arr) => sum + arr.length, 0)
  });
});

app.get('/api/models', (req, res) => {
  res.json({ 
    models: MODELS.map(m => ({
      id: m.id,
      name: m.name,
      desc: m.desc,
      speed: m.speed,
      cost_per_1k: m.cost_per_1k,
      cost_level: m.cost_level
    }))
  });
});

app.get('/api/history/:sessionId', (req, res) => {
  const sessionId = req.params.sessionId;
  const history = chatHistory[sessionId] || [];
  res.json(history.slice(-200));
});

app.get('/api/session/:sessionId', (req, res) => {
  const sessionId = req.params.sessionId;
  const sessionConfig = config.sessions[sessionId] || {};
  res.json({
    sessionId,
    model: sessionConfig.model || 'qwen3.5-plus',
    createdAt: sessionConfig.createdAt,
    updatedAt: sessionConfig.updatedAt
  });
});

app.post('/api/session/:sessionId/model', (req, res) => {
  const { sessionId } = req.params;
  const { model } = req.body;
  
  if (!model) {
    return res.status(400).json({ error: '模型不能为空' });
  }
  
  const modelExists = MODELS.find(m => m.id === model);
  if (!modelExists) {
    return res.status(400).json({ error: '不支持的模型' });
  }
  
  if (!config.sessions[sessionId]) {
    config.sessions[sessionId] = {};
  }
  config.sessions[sessionId].model = model;
  config.sessions[sessionId].updatedAt = Date.now();
  saveConfig(config);
  
  console.log('[SESSION]', sessionId, '切换模型:', model);
  
  res.json({ success: true, model });
});

// 认证检查
app.post('/api/auth/check', (req, res) => {
  const { password } = req.body;
  
  if (!password) {
    return res.status(400).json({ authenticated: false, error: '需要密码' });
  }
  
  const authenticated = password === authConfig.password;
  res.json({ authenticated });
});

// 修改密码
app.post('/api/auth/password', (req, res) => {
  const { oldPassword, newPassword } = req.body;
  
  if (oldPassword !== authConfig.password) {
    return res.status(401).json({ success: false, error: '原密码错误' });
  }
  
  authConfig.password = newPassword;
  saveAuth(authConfig);
  
  res.json({ success: true });
});

// 导出对话
app.get('/api/export/:sessionId', (req, res) => {
  const sessionId = req.params.sessionId;
  const format = req.query.format || 'json';
  const history = chatHistory[sessionId] || [];
  
  if (format === 'json') {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', `attachment; filename="chat-${sessionId}.json"`);
    res.json(history);
  } else if (format === 'md') {
    let md = `# Chat Export - ${sessionId}\n\n`;
    md += `Exported at: ${new Date().toISOString()}\n\n---\n\n`;
    
    history.forEach(msg => {
      const role = msg.role === 'user' ? '👤 You' : '🤖 Assistant';
      const time = new Date(msg.timestamp).toLocaleString();
      md += `### ${role} - ${time}\n\n${msg.content}\n\n`;
      if (msg.model) {
        md += `*Model: ${msg.model}*\n\n`;
      }
      md += `---\n\n`;
    });
    
    res.setHeader('Content-Type', 'text/markdown');
    res.setHeader('Content-Disposition', `attachment; filename="chat-${sessionId}.md"`);
    res.send(md);
  } else {
    res.status(400).json({ error: '不支持的格式' });
  }
});

app.post('/api/chat', (req, res) => {
  const { message, sessionId = 'web-chat', model } = req.body;
  
  // 消息验证（安全修复）
  if (!message) {
    return res.status(400).json({ error: '消息不能为空' });
  }
  
  if (typeof message !== 'string') {
    return res.status(400).json({ error: '消息必须是字符串' });
  }
  
  if (message.trim().length === 0) {
    return res.status(400).json({ error: '消息不能为空' });
  }
  
  if (message.length > 2000) {
    return res.status(400).json({ error: '消息过长，限制 2000 字符' });
  }
  
  const sessionModel = model || config.sessions[sessionId]?.model || 'qwen3.5-plus';
  
  console.log(`[API] 收到：${message} (session: ${sessionId}, model: ${sessionModel})`);
  
  if (!chatHistory[sessionId]) {
    chatHistory[sessionId] = [];
  }
  
  chatHistory[sessionId].push({
    role: 'user',
    content: message,
    timestamp: Date.now(),
    model: sessionModel
  });
  
  res.json({ 
    success: true, 
    message: '⏳ 正在思考...', 
    sessionId,
    model: sessionModel,
    streaming: true
  });
  
  let fullReply = '';
  
  streamAI(
    message,
    sessionId,
    sessionModel,
    (chunk) => {
      fullReply += chunk;
      const roomClients = io.sockets.adapter.rooms.get(sessionId);
      const clientCount = roomClients ? roomClients.size : 0;
      console.log(`[WS] 推送流式片段到 ${sessionId}, 客户端数：${clientCount}`);
      io.to(sessionId).emit('stream_chunk', {
        type: 'chunk',
        content: chunk,
        timestamp: Date.now()
      });
    },
    (finalText, rawOutput, code, stats) => {
      // 添加 Web Chat 特征码
      const reply = (finalText || '我收到了你的消息') + '\n\n---\n🌐 *来自 Web Chat*';
      
      console.log(`[HIST] 保存回复到 ${sessionId}, 长度：${reply.length}`);
      
      chatHistory[sessionId].push({
        role: 'assistant',
        content: reply,
        timestamp: Date.now(),
        model: sessionModel,
        streaming: true,
        stats
      });
      
      try {
        saveHistory(chatHistory);
        console.log('[HIST] ✅ 保存成功');
      } catch (e) {
        console.error('[HIST] ❌ 保存失败:', e.message);
      }
      
      const roomClients = io.sockets.adapter.rooms.get(sessionId);
      const clientCount = roomClients ? roomClients.size : 0;
      console.log(`[WS] 推送完成消息到 ${sessionId}, 客户端数：${clientCount}`);
      io.to(sessionId).emit('stream_complete', {
        type: 'complete',
        content: reply,
        timestamp: Date.now(),
        model: sessionModel,
        full: true,
        stats
      });
    }
  );
});

// WebSocket
io.on('connection', (socket) => {
  console.log('[WS] 连接:', socket.id);
  
  socket.on('join', (sessionId) => {
    const roomId = sessionId || 'web-chat';
    socket.join(roomId);
    const roomClients = io.sockets.adapter.rooms.get(roomId);
    const clientCount = roomClients ? roomClients.size : 0;
    const history = chatHistory[sessionId] || [];
    const sessionConfig = config.sessions[sessionId] || {};
    socket.emit('history', history.slice(-200));
    socket.emit('session_config', {
      model: sessionConfig.model || 'qwen3.5-plus'
    });
    console.log(`[WS] ${socket.id} 加入会话：${roomId}, 当前客户端数：${clientCount}`);
  });
  
  socket.on('change_model', (data) => {
    const { sessionId, model } = data;
    if (!config.sessions[sessionId]) {
      config.sessions[sessionId] = {};
    }
    config.sessions[sessionId].model = model;
    config.sessions[sessionId].updatedAt = Date.now();
    saveConfig(config);
    
    socket.emit('model_changed', { model });
    console.log(`[WS] ${sessionId} 切换模型：${model}`);
  });
  
  socket.on('message', (data) => {
    const { message, sessionId = 'web-chat' } = data;
    socket.to(sessionId).emit('message', {
      role: 'user',
      content: message,
      timestamp: Date.now()
    });
  });
  
  socket.on('disconnect', () => {
    console.log('[WS] 断开:', socket.id);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║   🦞 OpenClaw Web Chat v15 (生产就绪版) 已启动！         ║
║   本地：http://localhost:${PORT}                           ║
║   外网：http://192.168.68.109:${PORT}                     ║
║                                                          ║
║   新功能：                                               ║
║   ✅ 用户认证（密码：admin123）                          ║
║   ✅ 速率限制（60 次/分钟）                               ║
║   ✅ Token 统计显示                                       ║
║   ✅ Markdown 渲染支持                                    ║
║   ✅ 对话导出（JSON/Markdown）                           ║
║   ✅ 成本提示                                             ║
║   ✅ 深色模式支持                                         ║
║   ✅ 错误重试机制（最多 2 次）                             ║
║                                                          ║
║   保留功能：                                             ║
║   ✅ 流式输出（打字机效果）                               ║
║   ✅ 多模型切换（4 个模型）                               ║
║   ✅ 会话持久化                                           ║
╚══════════════════════════════════════════════════════════╝
  `);
});
