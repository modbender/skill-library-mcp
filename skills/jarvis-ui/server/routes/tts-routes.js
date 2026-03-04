// ── TTS Routes: /api/tts, /api/tts/engines, /api/tts/engine ──

import { Router } from 'express';
import { getEngines, setEngine, synthesizeToResponse } from '../tts.js';

const router = Router();

router.get('/tts/engines', (req, res) => res.json(getEngines()));

router.post('/tts/engine', (req, res) => {
  try {
    const engine = setEngine(req.body.engine);
    res.json({ engine });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/tts', async (req, res) => {
  const { text, voice } = req.body;
  if (!text) return res.status(400).json({ error: 'text required' });
  await synthesizeToResponse(text, voice, res);
});

export default router;
