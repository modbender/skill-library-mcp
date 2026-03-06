// ── Status Routes: /api/config, /api/status, /api/model-status ──

import { Router } from 'express';
import { readFile } from 'fs/promises';
import { isReady, getSessionKey, gwRequest } from '../gateway.js';
import { getMsgCount } from './chat.js';

const router = Router();

export default function statusRoutes(config, ocConfigPath) {
  // 前端設定
  router.get('/config', (req, res) => {
    res.json({ name: config.name, agent: config.agent, theme: config.theme });
  });

  // 健康檢查
  router.get('/status', async (req, res) => {
    let channel = null;
    try {
      const ocConfig = JSON.parse(await readFile(ocConfigPath, 'utf-8'));
      const channels = ocConfig?.channels;
      if (channels) {
        channel = Object.keys(channels).find(k => channels[k]?.enabled !== false) || Object.keys(channels)[0] || null;
      }
    } catch {}
    res.json({ gateway: isReady(), sessionKey: getSessionKey(), channel, msgCount: getMsgCount() });
  });

  // Model Status
  router.get('/model-status', async (req, res) => {
    try {
      const hist = await gwRequest('chat.history', {
        sessionKey: req.app.locals.sessionKey, limit: 1,
      });
      const msgs = hist.messages || [];
      const lastMsg = msgs.length ? msgs[msgs.length - 1] : null;

      let sessionInfo = {};
      try {
        const list = await gwRequest('sessions.list', { limit: 20 });
        const sessions = list.sessions || list;
        sessionInfo = sessions.find(s => s.key === req.app.locals.sessionKey) || {};
      } catch {}

      res.json({
        model: lastMsg?.model || sessionInfo.model || '',
        provider: lastMsg?.provider || '',
        contextTokens: sessionInfo.contextTokens || 0,
        totalTokens: sessionInfo.totalTokens || lastMsg?.usage?.totalTokens || 0,
        contextWindow: sessionInfo.contextWindow || 128000,
        usage: lastMsg?.usage || null,
      });
    } catch (err) {
      res.status(502).json({ error: err.message || 'gateway error' });
    }
  });

  return router;
}
