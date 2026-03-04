const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8003;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));
app.use(express.static(path.join(__dirname, 'public')));

// Check if setup is needed (vault.json has all zeros or doesn't exist)
function needsSetup() {
  try {
    const vaultPath = path.join(__dirname, 'vault.json');
    if (!fs.existsSync(vaultPath)) return true;
    
    const vault = JSON.parse(fs.readFileSync(vaultPath, 'utf8'));
    const balances = ['openai', 'claude', 'kimi', 'deepseek', 'groq'];
    return balances.every(key => !vault[key] || vault[key] === 0);
  } catch (e) {
    return true;
  }
}

// Main billing page (redirect to setup if needed)
app.get('/', (req, res) => {
  if (needsSetup()) {
    return res.redirect('/setup');
  }
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Setup page
app.get('/setup', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'setup.html'));
});

// API: Get current vault data
app.get('/api/vault', (req, res) => {
  try {
    const vaultPath = path.join(__dirname, 'vault.json');
    if (!fs.existsSync(vaultPath)) return res.json({});
    const vault = JSON.parse(fs.readFileSync(vaultPath, 'utf8'));
    res.json(vault);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Function to immediately update usage.json after vault save
function updateUsageJsonImmediate(vault) {
  try {
    const usagePath = path.join(__dirname, 'dist', 'usage.json');
    const webLivePath = '/var/www/html/bill/usage_live.json';
    const webMainPath = '/var/www/html/bill/usage.json';
    
    let existingUsage = {};
    if (fs.existsSync(usagePath)) {
      existingUsage = JSON.parse(fs.readFileSync(usagePath, 'utf8'));
    }
    
    const BRANDS = ['openai', 'claude', 'gemini', 'deepseek', 'kimi', 'groq', 'xai', 'minimax', 'mistral', 'qwen', 'glm', 'llama'];
    const models = {};
    
    BRANDS.forEach(k => {
      const cost = parseFloat(existingUsage.models?.[k] || 0);
      const vaultItem = vault[k] || { balance: 0, mode: 'prepaid' };
      const balBase = parseFloat(vaultItem.balance || 0);
      const mode = vaultItem.mode || 'prepaid';
      
      models[k] = cost.toFixed(4);
      
      if (mode === 'postpaid') {
        models[k + '_bal'] = "POST";
      } else if (mode === 'subscribe') {
        models[k + '_bal'] = "SUB";
      } else if (mode === 'unused') {
        models[k + '_bal'] = "OFF";
      } else {
        models[k + '_bal'] = (balBase - cost).toFixed(2);
      }
      
      models[k + '_stats'] = existingUsage.models?.[k + '_stats'] || {};
    });
    
    const usageData = {
      timestamp: new Date().toISOString(),
      runtime: existingUsage.runtime || { provider: 'minimax-portal', model: 'MiniMax-M2.5' },
      models: models
    };
    
    fs.writeFileSync(usagePath, JSON.stringify(usageData, null, 2));
    if (fs.existsSync(webLivePath)) fs.writeFileSync(webLivePath, JSON.stringify(usageData, null, 2));
    if (fs.existsSync(webMainPath)) fs.writeFileSync(webMainPath, JSON.stringify(usageData, null, 2));
    
    console.log('[Setup] Usage.json updated immediately');
  } catch (e) {
    console.error('[Setup] Failed to update usage.json:', e.message);
  }
}

// API: Save setup
app.post('/api/setup', (req, res) => {
  try {
    const vaultPath = path.join(__dirname, 'vault.json');
    const fields = ['openai', 'claude', 'kimi', 'deepseek', 'groq', 'xai', 'minimax', 'mistral', 'qwen', 'glm', 'llama', 'gemini'];
    const data = {};
    fields.forEach(f => {
      if (req.body[f] && typeof req.body[f] === 'object') {
        data[f] = {
          balance: parseFloat(req.body[f].balance) || 0,
          mode: req.body[f].mode || 'prepaid'
        };
      } else {
        data[f] = { balance: parseFloat(req.body[f]) || 0, mode: 'prepaid' };
      }
    });
    
    fs.writeFileSync(vaultPath, JSON.stringify(data, null, 2));
    
    // Immediately update usage.json
    updateUsageJsonImmediate(data);
    
    res.json({ status: 'success', message: 'Configuration saved' });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// API endpoint for usage data
app.get('/api/usage', (req, res) => {
  try {
    const usageData = JSON.parse(fs.readFileSync(path.join(__dirname, 'dist', 'usage.json'), 'utf8'));
    res.json({
      status: 'success',
      timestamp: new Date().toISOString(),
      data: usageData
    });
  } catch (error) {
    res.json({
      status: 'error',
      message: 'Usage data not available',
      timestamp: new Date().toISOString()
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    service: 'ai-bill',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

// Direct file paths
app.get('/usage.json', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'usage.json'));
});

// Redirect from old path
app.get('/usage_live.json', (req, res) => {
  res.redirect('/usage.json?' + Date.now());
});

app.listen(PORT, () => {
  console.log(`AI Billing System running on port ${PORT}.`);
  if (needsSetup()) {
    console.log('⚠️  First time setup required. Visit http://localhost:8003/setup');
  }
});
