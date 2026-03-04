#!/usr/bin/env node
/**
 * Local development server
 * Runs API + scheduler together for testing
 * 
 * Usage: node server.js
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();

app.use(cors());
app.use(express.json());

// === API ENDPOINTS ===

app.get('/api/logs', (req, res) => {
  try {
    const logPath = path.join(__dirname, 'execution-log.jsonl');
    
    if (!fs.existsSync(logPath)) {
      return res.json([]);
    }

    const content = fs.readFileSync(logPath, 'utf8');
    const logs = content
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
    
    res.json(logs);
  } catch (err) {
    console.error('Error reading logs:', err);
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// === STATIC FILES ===

const dashboardDist = path.join(__dirname, 'dashboard', 'dist');
if (fs.existsSync(dashboardDist)) {
  app.use(express.static(dashboardDist));
  // SPA fallback: serve index.html for all non-API routes
  app.use((req, res) => {
    if (!req.url.startsWith('/api/')) {
      res.sendFile(path.join(dashboardDist, 'index.html'));
    } else {
      res.status(404).json({ error: 'Not Found' });
    }
  });
} else {
  console.warn('⚠️  Dashboard dist folder not found. Build with: npm run build:dashboard');
}

// === START SERVER ===

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║    Yield Farming Agent - Local Dev Server                ║
╠═══════════════════════════════════════════════════════════╣
║  API:       http://localhost:${PORT}/api/logs             ║
║  Dashboard: http://localhost:${PORT}                      ║
║  Health:    http://localhost:${PORT}/api/health           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

// === GRACEFUL SHUTDOWN ===
process.on('SIGINT', () => {
  console.log('\n✓ Server stopped');
  process.exit(0);
});
