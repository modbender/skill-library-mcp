const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

// Serve execution logs
app.get('/api/logs', (req, res) => {
  try {
    const logPath = path.join(__dirname, '../execution-log.jsonl');
    
    if (!fs.existsSync(logPath)) {
      return res.json([]);
    }

    const content = fs.readFileSync(logPath, 'utf8');
    const logs = content
      .split('\n')
      .filter(line => line.trim())
      .map(line => {
        try {
          const parsed = JSON.parse(line);
          // Ensure all fields are safe
          return {
            timestamp: parsed.timestamp || 0,
            cycle: parsed.cycle || 0,
            action: parsed.action || 'UNKNOWN',
            vault: parsed.vault || parsed.vault_id || 'unknown',
            vault_id: parsed.vault_id || parsed.vault || 'unknown',
            vault_name: parsed.vault_name || '',
            tx_hash: parsed.tx_hash || '',
            rewards_usd: parsed.rewards_usd || parsed.amount_tokens || 0,
            confidence: parsed.confidence || 0,
            status: parsed.status || 'unknown',
            error: parsed.error || '',
            gas_used: parsed.gas_used || '',
            ...parsed
          };
        } catch (e) {
          return null;
        }
      })
      .filter(log => log !== null);
    
    res.json(logs);
  } catch (err) {
    console.error('Error reading logs:', err);
    res.status(500).json({ error: err.message });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Fallback
app.get('*', (req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Yield Farming Agent API listening on port ${PORT}`);
});

module.exports = app;
