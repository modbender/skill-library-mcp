/**
 * ideas-api.js
 * Express route handlers for the community build ideas board.
 * Mounts at /public/ideas — no auth required (public endpoint).
 *
 * Storage: flat JSON file (no database needed).
 *
 * Usage — mount in your Express app:
 *
 *   const ideasRouter = require('./ideas-api');
 *   app.use('/public/ideas', ideasRouter);
 *
 * Or inline into an existing Express app file:
 *   const { ideasRouter } = require('./ideas-api');
 *   app.use('/public/ideas', ideasRouter);
 *
 * Configuration (env vars):
 *   IDEAS_FILE  — path to JSON storage file (default: ./data/build-ideas.json)
 *   CORS_ORIGIN — allowed origin for CORS (default: * for public use)
 */

const express = require('express');
const fs      = require('fs');
const path    = require('path');
const crypto  = require('crypto');

// ── Config ──
const IDEAS_FILE  = process.env.IDEAS_FILE  || path.join(__dirname, '../data/build-ideas.json');
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';

// ── Helpers ──
function loadIdeas() {
  try {
    if (fs.existsSync(IDEAS_FILE)) {
      return JSON.parse(fs.readFileSync(IDEAS_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('[ideas-api] Failed to load ideas:', err.message);
  }
  return [];
}

function saveIdeas(ideas) {
  fs.mkdirSync(path.dirname(IDEAS_FILE), { recursive: true });
  fs.writeFileSync(IDEAS_FILE, JSON.stringify(ideas, null, 2));
}

// ── Router ──
const router = express.Router();

// CORS — allow public frontend access
router.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin',  CORS_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

// GET /public/ideas — list all ideas sorted by votes
router.get('/', (req, res) => {
  const ideas = loadIdeas();
  ideas.sort((a, b) => b.votes - a.votes);
  res.json(ideas);
});

// POST /public/ideas — submit a new idea
router.post('/', express.json(), (req, res) => {
  const { text, author } = req.body || {};

  if (!text || text.trim().length < 5) {
    return res.status(400).json({ error: 'Idea must be at least 5 characters.' });
  }

  const ideas = loadIdeas();
  const idea = {
    id:        crypto.randomBytes(8).toString('hex'),
    text:      text.trim().slice(0, 160),
    author:    (author || 'anon').trim().slice(0, 30),
    votes:     1,
    createdAt: new Date().toISOString(),
  };

  ideas.push(idea);
  saveIdeas(ideas);

  res.status(201).json(idea);
});

// POST /public/ideas/:id/vote — upvote an idea
router.post('/:id/vote', (req, res) => {
  const ideas = loadIdeas();
  const idea  = ideas.find(i => i.id === req.params.id);

  if (!idea) {
    return res.status(404).json({ error: 'Idea not found.' });
  }

  idea.votes = (idea.votes || 0) + 1;
  saveIdeas(ideas);

  res.json(idea);
});

module.exports = router;

// ── Standalone usage (for quick testing) ──
// Run: node ideas-api.js
// Then: curl http://localhost:3001/public/ideas
if (require.main === module) {
  const app = express();
  app.use('/public/ideas', router);
  const port = process.env.PORT || 3001;
  app.listen(port, () => {
    console.log(`[ideas-api] Listening on http://localhost:${port}/public/ideas`);
  });
}
