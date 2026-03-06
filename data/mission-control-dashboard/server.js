require('dotenv').config({ path: '/home/ubuntu/clawd/.env' });
const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const execAsync = promisify(exec);
const app = express();
const server = createServer(app);
const io = new Server(server);

const PORT = process.env.DASHBOARD_PORT || 3000;
const WORKSPACE = '/home/ubuntu/clawd';
const AGENTS_DIR = path.join(WORKSPACE, 'agents');
const SCAN_HISTORY_FILE = path.join(WORKSPACE, 'dashboard', 'scan-history.json');

// Auth Configuration - from centralized .env (updated 2026-02-09)
const AUTH_USER = 'admin';
const AUTH_PASS = process.env.DASHBOARD_ADMIN_PASSWORD;
const SESSION_SECRET = process.env.DASHBOARD_SESSION_SECRET || crypto.randomBytes(32).toString('hex');

// Session store (in-memory)
const sessions = new Map();
const SESSION_MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours

// Rate limiting store
const loginAttempts = new Map();
const RATE_LIMIT_MAX = 5; // Max attempts
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute window
const RATE_LIMIT_BLOCK = 60 * 1000; // Block for 1 minute after max attempts

// Scan history helper functions
async function loadScanHistory() {
  try {
    const data = await fs.readFile(SCAN_HISTORY_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (e) {
    return [];
  }
}

async function saveScanHistory(entry) {
  const history = await loadScanHistory();
  history.push(entry);
  // Keep only last 90 days
  const cutoff = Date.now() - (90 * 24 * 60 * 60 * 1000);
  const filtered = history.filter(h => new Date(h.date).getTime() > cutoff);
  await fs.writeFile(SCAN_HISTORY_FILE, JSON.stringify(filtered, null, 2));
}

function getThreatTimeline(history, days = 30) {
  const timeline = [];
  const now = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    // Get latest scan for this day (not sum)
    const dayScans = history.filter(h => h.date.startsWith(dateStr));
    let threats = 0;
    if (dayScans.length > 0) {
      const latest = dayScans[dayScans.length - 1];
      threats = (latest.critical || 0) + (latest.high || 0);
    }
    timeline.push({ date: dateStr, threats });
  }
  return timeline;
}

// Middleware
app.use(express.json());
app.use(require('cookie-parser')());

// Rate limiter middleware
function rateLimiter(req, res, next) {
  const ip = req.headers['x-forwarded-for']?.split(',')[0] || req.ip || 'unknown';
  const now = Date.now();
  
  let record = loginAttempts.get(ip);
  
  if (record) {
    // Check if blocked
    if (record.blockedUntil && now < record.blockedUntil) {
      const retryAfter = Math.ceil((record.blockedUntil - now) / 1000);
      return res.status(429).json({ 
        error: 'Too many login attempts', 
        retryAfter 
      });
    }
    
    // Clean old attempts
    record.attempts = record.attempts.filter(t => now - t < RATE_LIMIT_WINDOW);
    
    // Check if over limit
    if (record.attempts.length >= RATE_LIMIT_MAX) {
      record.blockedUntil = now + RATE_LIMIT_BLOCK;
      loginAttempts.set(ip, record);
      console.log(`[SECURITY] IP ${ip} blocked for ${RATE_LIMIT_BLOCK/1000}s after ${RATE_LIMIT_MAX} failed attempts`);
      return res.status(429).json({ 
        error: 'Too many login attempts', 
        retryAfter: RATE_LIMIT_BLOCK / 1000 
      });
    }
  }
  
  next();
}

// Session middleware
function sessionMiddleware(req, res, next) {
  const sessionId = req.cookies?.session;
  if (sessionId && sessions.has(sessionId)) {
    const session = sessions.get(sessionId);
    if (Date.now() < session.expiresAt) {
      req.session = session;
      req.authenticated = true;
      return next();
    }
    sessions.delete(sessionId);
  }
  req.authenticated = false;
  next();
}

// Auth check middleware
function requireAuth(req, res, next) {
  if (req.authenticated) {
    return next();
  }
  // For API requests, return 401
  if (req.path.startsWith('/api/') || req.path.startsWith('/socket.io/')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  // For page requests, redirect to login
  res.redirect('/login.html');
}

app.use(sessionMiddleware);

// Public routes (no auth required)
app.get('/login.html', (req, res) => {
  if (req.authenticated) {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/auth/check', (req, res) => {
  res.json({ authenticated: req.authenticated });
});

app.post('/auth/login', rateLimiter, (req, res) => {
  const { username, password } = req.body;
  const ip = req.headers['x-forwarded-for']?.split(',')[0] || req.ip || 'unknown';
  
  if (username === AUTH_USER && password === AUTH_PASS) {
    // Success - clear attempts and create session
    loginAttempts.delete(ip);
    
    const sessionId = crypto.randomBytes(32).toString('hex');
    const session = {
      user: username,
      createdAt: Date.now(),
      expiresAt: Date.now() + SESSION_MAX_AGE,
      ip
    };
    sessions.set(sessionId, session);
    
    res.cookie('session', sessionId, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: SESSION_MAX_AGE
    });
    
    console.log(`[AUTH] User ${username} logged in from ${ip}`);
    return res.json({ success: true });
  }
  
  // Failed login - record attempt
  let record = loginAttempts.get(ip) || { attempts: [], blockedUntil: null };
  record.attempts.push(Date.now());
  loginAttempts.set(ip, record);
  
  const remaining = RATE_LIMIT_MAX - record.attempts.length;
  console.log(`[AUTH] Failed login attempt from ${ip} (${remaining} attempts remaining)`);
  
  res.status(401).json({ 
    error: 'Invalid username or password',
    attemptsRemaining: remaining
  });
});

app.post('/auth/logout', (req, res) => {
  const sessionId = req.cookies?.session;
  if (sessionId) {
    sessions.delete(sessionId);
    res.clearCookie('session');
  }
  res.json({ success: true });
});

// Protected routes - require auth
app.use(requireAuth);
app.use(express.static(path.join(__dirname, 'public')));

// API: Get all agents config
app.get('/api/agents/config', async (req, res) => {
  try {
    const data = await fs.readFile(path.join(AGENTS_DIR, 'agents.json'), 'utf-8');
    res.json(JSON.parse(data));
  } catch (e) {
    res.json({ agents: [] });
  }
});

// API: Get single agent
app.get('/api/agents/:id', async (req, res) => {
  try {
    const data = await fs.readFile(path.join(AGENTS_DIR, 'agents.json'), 'utf-8');
    const { agents } = JSON.parse(data);
    const agent = agents.find(a => a.id === req.params.id);
    if (!agent) return res.status(404).json({ error: 'Agent not found' });
    
    // Get agent's tasks
    const tasksFile = path.join(AGENTS_DIR, agent.id, 'tasks.json');
    const tasks = await fs.readFile(tasksFile, 'utf-8').catch(() => '[]');
    
    // Get agent's memory files
    const memoryDir = path.join(AGENTS_DIR, agent.id, 'memory');
    const memoryFiles = await fs.readdir(memoryDir).catch(() => []);
    
    res.json({ ...agent, tasks: JSON.parse(tasks), memoryFiles });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Update agent
app.patch('/api/agents/:id', async (req, res) => {
  try {
    const configPath = path.join(AGENTS_DIR, 'agents.json');
    const data = await fs.readFile(configPath, 'utf-8');
    const config = JSON.parse(data);
    const idx = config.agents.findIndex(a => a.id === req.params.id);
    if (idx < 0) return res.status(404).json({ error: 'Agent not found' });
    config.agents[idx] = { ...config.agents[idx], ...req.body };
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
    res.json(config.agents[idx]);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Agent tasks
app.get('/api/agents/:id/tasks', async (req, res) => {
  try {
    const tasksFile = path.join(AGENTS_DIR, req.params.id, 'tasks.json');
    const data = await fs.readFile(tasksFile, 'utf-8').catch(() => '[]');
    res.json(JSON.parse(data));
  } catch (e) {
    res.json([]);
  }
});

app.post('/api/agents/:id/tasks', async (req, res) => {
  try {
    const tasksFile = path.join(AGENTS_DIR, req.params.id, 'tasks.json');
    const data = await fs.readFile(tasksFile, 'utf-8').catch(() => '[]');
    const tasks = JSON.parse(data);
    const newTask = { id: Date.now(), ...req.body, createdAt: new Date().toISOString(), status: req.body.status || 'inbox' };
    tasks.push(newTask);
    await fs.writeFile(tasksFile, JSON.stringify(tasks, null, 2));
    res.json(newTask);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.patch('/api/agents/:id/tasks/:taskId', async (req, res) => {
  try {
    const tasksFile = path.join(AGENTS_DIR, req.params.id, 'tasks.json');
    const data = await fs.readFile(tasksFile, 'utf-8').catch(() => '[]');
    const tasks = JSON.parse(data);
    const idx = tasks.findIndex(t => t.id === parseInt(req.params.taskId));
    if (idx >= 0) {
      tasks[idx] = { ...tasks[idx], ...req.body };
      await fs.writeFile(tasksFile, JSON.stringify(tasks, null, 2));
      res.json(tasks[idx]);
    } else {
      res.status(404).json({ error: 'Task not found' });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Agent logs
app.get('/api/agents/:id/logs', async (req, res) => {
  try {
    const logsDir = path.join(AGENTS_DIR, req.params.id, 'logs');
    const files = await fs.readdir(logsDir).catch(() => []);
    const logFiles = files.filter(f => f.endsWith('.log')).sort().reverse();
    res.json(logFiles);
  } catch (e) {
    res.json([]);
  }
});

app.get('/api/agents/:id/logs/:file', async (req, res) => {
  try {
    const logPath = path.join(AGENTS_DIR, req.params.id, 'logs', req.params.file);
    const content = await fs.readFile(logPath, 'utf-8');
    res.json({ content });
  } catch (e) {
    res.status(404).json({ error: 'Log not found' });
  }
});

app.post('/api/agents/:id/logs', async (req, res) => {
  try {
    const { message, level = 'info' } = req.body;
    const logsDir = path.join(AGENTS_DIR, req.params.id, 'logs');
    const today = new Date().toISOString().split('T')[0];
    const logFile = path.join(logsDir, `${today}.log`);
    const timestamp = new Date().toISOString();
    const line = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;
    await fs.appendFile(logFile, line);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Agent memory
app.get('/api/agents/:id/memory', async (req, res) => {
  try {
    const memDir = path.join(AGENTS_DIR, req.params.id, 'memory');
    const files = await fs.readdir(memDir).catch(() => []);
    res.json(files.filter(f => f.endsWith('.md') || f.endsWith('.json')));
  } catch (e) {
    res.json([]);
  }
});

app.get('/api/agents/:id/memory/:file', async (req, res) => {
  try {
    const memPath = path.join(AGENTS_DIR, req.params.id, 'memory', req.params.file);
    const content = await fs.readFile(memPath, 'utf-8');
    res.json({ content });
  } catch (e) {
    res.status(404).json({ error: 'File not found' });
  }
});

app.put('/api/agents/:id/memory/:file', async (req, res) => {
  try {
    const memPath = path.join(AGENTS_DIR, req.params.id, 'memory', req.params.file);
    await fs.writeFile(memPath, req.body.content);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: System stats
app.get('/api/system', async (req, res) => {
  try {
    const [disk, memory, load] = await Promise.all([
      execAsync("df -h / | tail -1 | awk '{print $5}'"),
      execAsync("free -h | grep Mem | awk '{print $3}'"),
      execAsync("cat /proc/loadavg | awk '{print $1}'")
    ]);
    res.json({
      disk: disk.stdout.trim(),
      memory: memory.stdout.trim(),
      load: load.stdout.trim()
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Detailed System stats (for INFRA panel)
app.get('/api/system/detailed', async (req, res) => {
  try {
    const [cpuRes, memRes, diskRes, hostnameRes, uptimeRes, nodeRes, osRes, coresRes, gpuRes] = await Promise.all([
      execAsync("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1").catch(() => ({ stdout: '0' })),
      execAsync("free -b | grep Mem").catch(() => ({ stdout: '' })),
      execAsync("df -B1 / | tail -1").catch(() => ({ stdout: '' })),
      execAsync("hostname").catch(() => ({ stdout: 'unknown' })),
      execAsync("uptime -p").catch(() => ({ stdout: '' })),
      execAsync("node --version").catch(() => ({ stdout: '' })),
      execAsync("cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2").catch(() => ({ stdout: '' })),
      execAsync("nproc").catch(() => ({ stdout: '1' })),
      execAsync("nvidia-smi --query-gpu=utilization.gpu,name --format=csv,noheader,nounits 2>/dev/null").catch(() => ({ stdout: '' }))
    ]);
    
    // Parse memory
    const memParts = memRes.stdout.trim().split(/\s+/);
    const memTotal = parseFloat(memParts[1]) || 0;
    const memUsed = parseFloat(memParts[2]) || 0;
    const memPercent = memTotal > 0 ? Math.round((memUsed / memTotal) * 100) : 0;
    
    // Parse disk
    const diskParts = diskRes.stdout.trim().split(/\s+/);
    const diskTotal = parseFloat(diskParts[1]) || 0;
    const diskUsed = parseFloat(diskParts[2]) || 0;
    const diskPercent = diskTotal > 0 ? Math.round((diskUsed / diskTotal) * 100) : 0;
    
    // Parse GPU
    let gpuPercent = null;
    let gpuName = null;
    if (gpuRes.stdout.trim()) {
      const gpuParts = gpuRes.stdout.trim().split(',');
      gpuPercent = parseInt(gpuParts[0]?.trim()) || 0;
      gpuName = gpuParts[1]?.trim() || 'GPU';
    }
    
    res.json({
      cpu: Math.round(parseFloat(cpuRes.stdout.trim()) || 0),
      cpuCores: parseInt(coresRes.stdout.trim()) || 1,
      memPercent,
      memUsed: (memUsed / 1024 / 1024 / 1024).toFixed(1),
      memTotal: (memTotal / 1024 / 1024 / 1024).toFixed(1),
      diskPercent,
      diskUsed: (diskUsed / 1024 / 1024 / 1024).toFixed(0),
      diskTotal: (diskTotal / 1024 / 1024 / 1024).toFixed(0),
      gpuPercent,
      gpuName,
      hostname: hostnameRes.stdout.trim(),
      uptime: uptimeRes.stdout.trim().replace('up ', ''),
      nodeVersion: nodeRes.stdout.trim(),
      os: osRes.stdout.trim()
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Extended Infrastructure stats
app.get('/api/system/infra', async (req, res) => {
  try {
    const results = await Promise.all([
      // Load average
      execAsync("cat /proc/loadavg").catch(() => ({ stdout: '0 0 0' })),
      // Temperature
      execAsync("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0").catch(() => ({ stdout: '0' })),
      // Network IP
      execAsync("hostname -I | awk '{print $1}'").catch(() => ({ stdout: '--' })),
      // Network stats
      execAsync("cat /proc/net/dev | grep -E 'eth|ens|enp' | head -1 | awk '{print $2,$10}'").catch(() => ({ stdout: '0 0' })),
      // Connections
      execAsync("ss -t | wc -l").catch(() => ({ stdout: '0' })),
      // Top processes
      execAsync("ps aux --sort=-%cpu | head -6 | tail -5 | awk '{printf \"%s %.1f%% %.0fMB\\n\", $11, $3, $6/1024}'").catch(() => ({ stdout: '' })),
      // Open ports
      execAsync("ss -tlnp | grep LISTEN | awk '{print $4}' | grep -oE '[0-9]+$' | sort -n | uniq | head -10").catch(() => ({ stdout: '' })),
      // Services
      execAsync("systemctl list-units --type=service --state=running --no-pager --no-legend | head -8 | awk '{print $1}'").catch(() => ({ stdout: '' })),
      // Failed logins
      execAsync("grep -c 'Failed password' /var/log/auth.log 2>/dev/null || echo 0").catch(() => ({ stdout: '0' })),
      // Firewall (check config file since ufw status needs root)
      execAsync("grep -q 'ENABLED=yes' /etc/ufw/ufw.conf 2>/dev/null && echo 'Status: active' || echo 'inactive'").catch(() => ({ stdout: 'unknown' })),
      // Updates
      execAsync("apt list --upgradable 2>/dev/null | wc -l").catch(() => ({ stdout: '0' })),
      // Docker
      execAsync("docker ps --format '{{.Names}}:{{.Status}}' 2>/dev/null | head -5").catch(() => ({ stdout: '' })),
      // Cron
      execAsync("crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | head -5").catch(() => ({ stdout: '' })),
      // Disk I/O (get main disk - sda, nvme0n1, or vda)
      execAsync("cat /proc/diskstats | grep -E ' (sda|nvme0n1|vda) ' | head -1 | awk '{print $6,$10}'").catch(() => ({ stdout: '0 0' })),
      // GPU temp (only if nvidia-smi exists)
      execAsync("which nvidia-smi >/dev/null 2>&1 && nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null || echo ''").catch(() => ({ stdout: '' }))
    ]);

    const [loadRes, tempRes, ipRes, netRes, connRes, procRes, portsRes, servRes, failedRes, fwRes, updRes, dockerRes, cronRes, diskIoRes, gpuTempRes] = results;
    
    const loadParts = loadRes.stdout.trim().split(' ');
    const netParts = netRes.stdout.trim().split(' ');
    
    res.json({
      load1: loadParts[0] || '0',
      load5: loadParts[1] || '0',
      load15: loadParts[2] || '0',
      tempCpu: Math.round(parseInt(tempRes.stdout.trim()) / 1000) || null,
      tempGpu: gpuTempRes.stdout.trim() ? parseInt(gpuTempRes.stdout.trim()) : null,
      netIp: ipRes.stdout.trim(),
      netRx: (parseInt(netParts[0]) / 1024 / 1024).toFixed(1),
      netTx: (parseInt(netParts[1]) / 1024 / 1024).toFixed(1),
      netConn: parseInt(connRes.stdout.trim()) - 1 || 0,
      topProcesses: procRes.stdout.trim().split('\n').filter(Boolean),
      openPorts: portsRes.stdout.trim().split('\n').filter(Boolean),
      services: servRes.stdout.trim().split('\n').filter(Boolean).map(s => s.replace('.service', '')),
      failedLogins: parseInt(failedRes.stdout.trim()) || 0,
      firewall: fwRes.stdout.trim(),
      updates: Math.max(0, parseInt(updRes.stdout.trim()) - 1),
      docker: dockerRes.stdout.trim().split('\n').filter(Boolean),
      cron: cronRes.stdout.trim().split('\n').filter(Boolean),
      // Disk I/O (sectors to MB - total since boot)
      diskTotalReadMB: ((parseInt(diskIoRes.stdout.trim().split(' ')[0]) || 0) * 512 / 1024 / 1024).toFixed(0),
      diskTotalWriteMB: ((parseInt(diskIoRes.stdout.trim().split(' ')[1]) || 0) * 512 / 1024 / 1024).toFixed(0),
      diskTotalRead: ((parseInt(diskIoRes.stdout.trim().split(' ')[0]) || 0) * 512 / 1024 / 1024 / 1024).toFixed(1),
      diskTotalWrite: ((parseInt(diskIoRes.stdout.trim().split(' ')[1]) || 0) * 512 / 1024 / 1024 / 1024).toFixed(1)
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Security scan state
let lastSecurityScan = null;

// API: Security status
app.get('/api/security/status', (req, res) => {
  res.json(lastSecurityScan || { lastScan: null });
});

// API: Security extras (SSH, users, recent files, SSL, etc.)
app.get('/api/security/extras', async (req, res) => {
  try {
    const results = await Promise.all([
      // SSH active sessions
      execAsync("who 2>/dev/null || echo ''").catch(() => ({ stdout: '' })),
      // SSH login history
      execAsync("last -n 5 -w 2>/dev/null | head -5 | awk '{print $1, $3, $4, $5, $6}'").catch(() => ({ stdout: '' })),
      // Sudo users
      execAsync("grep -Po '^sudo.+:\\K.*$' /etc/group 2>/dev/null || echo ''").catch(() => ({ stdout: '' })),
      // Root login enabled
      execAsync("grep -E '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | grep -v '#' | awk '{print $2}'").catch(() => ({ stdout: 'no' })),
      // Recently modified files (24h)
      execAsync(`find ${WORKSPACE} -type f -mtime -1 -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -10`).catch(() => ({ stdout: '' })),
      // SSL certificates (check common locations)
      execAsync("find /etc/ssl /etc/letsencrypt -name '*.pem' -o -name '*.crt' 2>/dev/null | head -5").catch(() => ({ stdout: '' })),
      // Exposed secrets scan
      execAsync(`grep -rl --include="*.env" --include="*.json" -E "(api_key|apikey|secret|password|token)\\s*[:=]" ${WORKSPACE} 2>/dev/null | grep -v node_modules | head -10`).catch(() => ({ stdout: '' }))
    ]);

    const [sshRes, sshHistRes, sudoRes, rootRes, recentRes, sslRes, secretsRes] = results;
    
    // Parse SSH sessions
    const sshSessions = sshRes.stdout.trim().split('\n').filter(Boolean);
    const sshHistory = sshHistRes.stdout.trim().split('\n').filter(Boolean);
    
    // Parse sudo users
    const sudoUsers = sudoRes.stdout.trim().split(',').filter(Boolean);
    
    // Root login
    const rootLogin = rootRes.stdout.trim().toLowerCase() === 'yes';
    
    // Recent files
    const recentFiles = recentRes.stdout.trim().split('\n').filter(Boolean).map(f => f.replace(WORKSPACE + '/', ''));
    
    // SSL Certs (simplified - just list them)
    const sslCerts = sslRes.stdout.trim().split('\n').filter(Boolean).map(f => ({
      domain: path.basename(f),
      daysLeft: 90 // Placeholder - would need openssl to check actual expiry
    }));
    
    // Exposed secrets
    const exposedSecrets = secretsRes.stdout.trim().split('\n').filter(Boolean).map(f => f.replace(WORKSPACE + '/', ''));
    
    // Threat timeline (30 days from real scan history)
    const scanHistory = await loadScanHistory();
    const threatTimeline = getThreatTimeline(scanHistory, 30);

    res.json({
      sshActive: sshSessions.length,
      sshSessions,
      sshHistory,
      sudoUsers,
      rootLogin,
      recentFiles,
      sslCerts,
      exposedSecrets,
      threatTimeline
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Security scan
app.post('/api/security/scan', async (req, res) => {
  try {
    const results = {
      critical: 0,
      high: 0,
      medium: 0,
      safe: 0,
      criticalAlerts: [],
      suspiciousFiles: [],
      riskyPatterns: [],
      skillsScan: [],
      outboundConnections: [],
      securityEvents: [],
      exposedSecrets: [],
      lastScan: new Date().toISOString()
    };
    
    // 0. Scan for exposed secrets
    try {
      const { stdout } = await execAsync(`grep -rl --include="*.env" --include="*.json" --include="*.js" -E "(api_key|apikey|secret_key|password|private_key)\\s*[:=]\\s*['\"][^'\"]+['\"]" ${WORKSPACE} 2>/dev/null | grep -v node_modules | head -10`);
      results.exposedSecrets = stdout.trim().split('\n').filter(Boolean).map(f => f.replace(WORKSPACE + '/', ''));
      if (results.exposedSecrets.length > 0) {
        results.high += results.exposedSecrets.length;
      }
    } catch (e) {}

    // 1. Scan for suspicious patterns in workspace
    const suspiciousPatterns = [
      { pattern: 'eval\\s*\\(', risk: 'high', name: 'eval() usage' },
      { pattern: 'curl[^a-z].*\\|.*bash', risk: 'critical', name: 'curl|bash pattern' },
      { pattern: 'wget[^a-z].*\\|.*/bin/sh', risk: 'critical', name: 'wget|sh pattern' },
      { pattern: 'base64.*-d', risk: 'medium', name: 'base64 decode' },
      { pattern: 'nc\\s+-e', risk: 'critical', name: 'netcat reverse shell' },
      { pattern: '/dev/tcp/', risk: 'critical', name: 'bash reverse shell' }
    ];

    // Scan JS files (exclude node_modules and the scanner itself)
    try {
      const { stdout: jsFiles } = await execAsync(`find ${WORKSPACE} -name "*.js" -type f -not -path "*/node_modules/*" -not -path "*/dashboard/server.js" 2>/dev/null | head -100`);
      const fileList = jsFiles.split('\n').filter(Boolean);
      if (fileList.length > 0) {
        for (const pattern of suspiciousPatterns) {
          try {
            const { stdout } = await execAsync(`grep -lE "${pattern.pattern}" ${fileList.join(' ')} 2>/dev/null || true`);
            if (stdout.trim()) {
              const files = stdout.trim().split('\n').filter(Boolean);
              if (pattern.risk === 'critical') {
                results.critical++;
                results.criticalAlerts.push({ source: pattern.name, message: 'Dangerous pattern detected', files: files.map(f => f.replace(WORKSPACE + '/', '')) });
              } else if (pattern.risk === 'high') {
                results.high++;
                results.riskyPatterns.push({ 
                  name: pattern.name, 
                  files: files.map(f => f.replace(WORKSPACE + '/', ''))
                });
              } else {
                results.medium++;
              }
            }
          } catch (e) {}
        }
      }
    } catch (e) {}

    // 2. Check for suspicious outbound connections
    try {
      const { stdout } = await execAsync("ss -tunp | grep ESTAB | awk '{print $5}' | grep -v '127.0.0.1' | head -10");
      results.outboundConnections = stdout.trim().split('\n').filter(Boolean);
    } catch (e) {}

    // 3. Check recent auth failures
    try {
      const { stdout } = await execAsync("grep -i 'failed\\|invalid\\|error' /var/log/auth.log 2>/dev/null | tail -5 | cut -c1-80");
      results.securityEvents = stdout.trim().split('\n').filter(Boolean).map(e => ({ type: 'alert', message: e }));
    } catch (e) {}

    // 4. Scan skills directory if exists
    try {
      const skillsDir = path.join(WORKSPACE, 'skills');
      const { stdout } = await execAsync(`ls -d ${skillsDir}/*/ 2>/dev/null || true`);
      const skillDirs = stdout.trim().split('\n').filter(Boolean);
      
      for (const skillDir of skillDirs) {
        const skillName = path.basename(skillDir);
        let risk = 'safe';
        let reason = '';
        
        // Check for dangerous patterns
        try {
          const { stdout: dangerCheck } = await execAsync(`grep -rl "curl.*|.*bash\\|eval(" ${skillDir} 2>/dev/null || true`);
          if (dangerCheck.trim()) {
            risk = 'critical';
            reason = 'Remote code execution pattern';
          }
        } catch (e) {}
        
        // Check for obfuscated code
        if (risk === 'safe') {
          try {
            const { stdout: obfCheck } = await execAsync(`grep -l "\\\\x[0-9a-f]\\{2\\}" ${skillDir}/*.js 2>/dev/null || true`);
            if (obfCheck.trim()) {
              risk = 'high';
              reason = 'Obfuscated code detected';
            }
          } catch (e) {}
        }
        
        results.skillsScan.push({ name: skillName, risk, reason });
        if (risk === 'critical') results.critical++;
        else if (risk === 'high') results.high++;
        else if (risk === 'medium') results.medium++;
        else results.safe++;
      }
    } catch (e) {}

    // 5. Check for world-writable files
    try {
      const { stdout } = await execAsync(`find ${WORKSPACE} -perm -002 -type f 2>/dev/null | head -10`);
      results.suspiciousFiles = stdout.trim().split('\n').filter(Boolean).map(f => f.replace(WORKSPACE + '/', ''));
    } catch (e) {}

    lastSecurityScan = results;
    
    // Save to history for timeline
    await saveScanHistory({
      date: results.lastScan,
      critical: results.critical,
      high: results.high,
      medium: results.medium,
      safe: results.safe
    });
    
    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Wallet
app.get('/api/wallet', async (req, res) => {
  try {
    const script = `const {ethers}=require('ethers');const p=new ethers.JsonRpcProvider('https://mainnet.base.org');p.getBalance('0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942').then(b=>console.log(ethers.formatEther(b))).catch(()=>console.log('0'));`;
    const { stdout } = await execAsync(`timeout 5 node -e "${script}"`, { cwd: WORKSPACE });
    const val = parseFloat(stdout.trim()) || 0;
    res.json({ eth: val.toFixed(4) });
  } catch (e) {
    res.json({ eth: '~0.004' });
  }
});

// API: Credits - Read real usage data from credits-YYYY-MM.json files
// Data is populated by /home/ubuntu/clawd/dashboard/credits-tracker.js
app.get('/api/credits', async (req, res) => {
  try {
    // Get requested month (default: current month)
    const now = new Date();
    const year = parseInt(req.query.year) || now.getFullYear();
    const month = parseInt(req.query.month) || (now.getMonth() + 1); // 1-indexed
    
    // Try to read from tracked credits file
    const creditsFile = path.join(WORKSPACE, 'dashboard', `credits-${year}-${String(month).padStart(2, '0')}.json`);
    
    try {
      const data = await fs.readFile(creditsFile, 'utf-8');
      const creditsData = JSON.parse(data);
      
      // Mark future days
      const daysInMonth = new Date(year, month, 0).getDate();
      const isCurrentMonth = (year === now.getFullYear() && month === now.getMonth() + 1);
      const maxDay = isCurrentMonth ? now.getDate() : daysInMonth;
      
      // Ensure all days are represented
      const existingDays = new Set(creditsData.dailyCosts.map(d => d.day));
      for (let day = 1; day <= daysInMonth; day++) {
        if (!existingDays.has(day)) {
          creditsData.dailyCosts.push({
            day,
            date: `${day}`,
            opus: 0,
            sonnet: 0,
            future: day > maxDay
          });
        } else if (day > maxDay) {
          // Mark existing day as future if needed
          const dayData = creditsData.dailyCosts.find(d => d.day === day);
          if (dayData) dayData.future = true;
        }
      }
      
      // Sort by day
      creditsData.dailyCosts.sort((a, b) => a.day - b.day);
      
      res.json(creditsData);
    } catch (e) {
      // No data file yet - return empty structure
      res.json({ 
        year,
        month,
        totalCost: 0,
        opusCost: 0,
        sonnetCost: 0,
        webSearchCost: 0,
        codeCost: 0,
        dailyCosts: [],
        message: 'No tracking data yet. Run credits-tracker.js to populate.'
      });
    }
  } catch (e) {
    res.json({ 
      totalCost: 0,
      opusCost: 0,
      sonnetCost: 0,
      webSearchCost: 0,
      codeCost: 0,
      dailyCosts: [],
      error: e.message
    });
  }
});

// API: PM2 bots
app.get('/api/bots', async (req, res) => {
  try {
    const { stdout } = await execAsync('pm2 jlist');
    const bots = JSON.parse(stdout);
    res.json(bots.map(b => ({
      id: b.pm_id, name: b.name, status: b.pm2_env.status,
      cpu: b.monit?.cpu || 0, memory: b.monit?.memory || 0,
      restarts: b.pm2_env.restart_time
    })));
  } catch (e) {
    res.json([]);
  }
});

app.post('/api/bots/:action/:name', async (req, res) => {
  const { action, name } = req.params;
  if (!['start', 'stop', 'restart'].includes(action)) return res.status(400).json({ error: 'Invalid' });
  try {
    await execAsync(`pm2 ${action} ${name}`);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/bots/:name/logs', async (req, res) => {
  try {
    const { stdout } = await execAsync(`pm2 logs ${req.params.name} --lines 100 --nostream 2>&1 | tail -100`);
    res.json({ logs: stdout });
  } catch (e) {
    res.json({ logs: '' });
  }
});

// ============================================================================
// API: Multi-Agent Coordination System (inspired by @sodawhite_dev)
// ============================================================================

let agentCoordinator = null;
try {
  const { AgentCoordinator, agentDb } = require('../agents-system/coordinator');
  agentCoordinator = new AgentCoordinator();
  agentCoordinator.initialize().catch(console.error);
  
  // Real-time events via Socket.IO
  agentDb.agentEvents.on('agent:updated', (agent) => {
    io.emit('agent:updated', agent);
  });
  agentDb.agentEvents.on('agent:completed', (agent) => {
    io.emit('agent:task-completed', { 
      agentId: agent.id, 
      result: agent.last_result || 'Task completed',
      time: new Date().toISOString()
    });
  });
  agentDb.agentEvents.on('task:created', (task) => {
    io.emit('task:created', task);
  });
  agentDb.agentEvents.on('proposal:created', (proposal) => {
    io.emit('proposal:created', proposal);
  });
  
  console.log('✅ Multi-Agent Coordination System loaded');
} catch (e) {
  console.log('⚠️  Multi-Agent System not available:', e.message);
}

// Get all agents status
app.get('/api/coordination/status', (req, res) => {
  if (!agentCoordinator) {
    return res.status(503).json({ error: 'Agent system not initialized' });
  }
  res.json(agentCoordinator.getStatus());
});

// Assign task to agent
app.post('/api/coordination/task', async (req, res) => {
  if (!agentCoordinator) {
    return res.status(503).json({ error: 'Agent system not initialized' });
  }
  try {
    const { agentId, task } = req.body;
    const result = await agentCoordinator.executeTask(agentId, task);
    
    // Emit socket event for real-time update
    io.emit('agent:task-completed', { agentId, task, result, time: new Date().toISOString() });
    
    // Also add to AGENTS tasks.json (integrated with Tasks panel)
    try {
      const tasksFile = path.join(AGENTS_DIR, 'agents-coord', 'tasks.json');
      const data = await fs.readFile(tasksFile, 'utf-8').catch(() => '[]');
      const tasks = JSON.parse(data);
      const agentNames = { scout: '🔍 Scout', analyst: '📊 Analyst', executor: '⚡ Executor', auditor: '🛡️ Auditor', content: '✍️ Content', infra: '🔧 Infra' };
      const newTask = {
        id: Date.now(),
        title: `[${agentNames[agentId] || agentId}] ${task.substring(0, 50)}`,
        description: result,
        status: 'done',
        createdAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
        agent: agentId
      };
      tasks.push(newTask);
      // Keep only last 50 tasks
      const trimmed = tasks.slice(-50);
      await fs.writeFile(tasksFile, JSON.stringify(trimmed, null, 2));
    } catch (e) {
      console.log('Failed to save agent task:', e.message);
    }
    
    res.json({ ok: true, result });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Create proposal
app.post('/api/coordination/propose', async (req, res) => {
  if (!agentCoordinator) {
    return res.status(503).json({ error: 'Agent system not initialized' });
  }
  try {
    const { agentId, title, description } = req.body;
    const result = await agentCoordinator.propose(agentId, title, description);
    res.json(result);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Broadcast message
app.post('/api/coordination/broadcast', async (req, res) => {
  if (!agentCoordinator) {
    return res.status(503).json({ error: 'Agent system not initialized' });
  }
  try {
    const { fromAgent, message } = req.body;
    await agentCoordinator.broadcast(fromAgent, message);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Start/stop work loop
app.post('/api/coordination/loop/:action', (req, res) => {
  if (!agentCoordinator) {
    return res.status(503).json({ error: 'Agent system not initialized' });
  }
  const { action } = req.params;
  if (action === 'start') {
    agentCoordinator.startWorkLoop(60000);
    res.json({ ok: true, message: 'Work loop started' });
  } else if (action === 'stop') {
    agentCoordinator.stopWorkLoop();
    res.json({ ok: true, message: 'Work loop stopped' });
  } else {
    res.status(400).json({ error: 'Invalid action' });
  }
});

// ============================================================================

// API: OpenClaw sessions
app.get('/api/sessions', async (req, res) => {
  try {
    const { stdout } = await execAsync('curl -s "http://localhost:18789/api/sessions?limit=50&messageLimit=1" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d"');
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.json({ sessions: [] });
  }
});

// API: Spawn agent
app.post('/api/spawn', async (req, res) => {
  try {
    const { task, label, model } = req.body;
    const payload = JSON.stringify({ task, label, model: model || 'sonnet', runTimeoutSeconds: 300 });
    const { stdout } = await execAsync(`curl -s -X POST "http://localhost:18789/api/sessions/spawn" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d" -H "Content-Type: application/json" -d '${payload}'`);
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Send message to session
app.post('/api/sessions/send', async (req, res) => {
  try {
    const payload = JSON.stringify(req.body);
    const { stdout } = await execAsync(`curl -s -X POST "http://localhost:18789/api/sessions/send" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d" -H "Content-Type: application/json" -d '${payload}'`);
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Cron jobs
app.get('/api/cron', async (req, res) => {
  try {
    const { stdout } = await execAsync('curl -s "http://localhost:18789/api/cron/list?includeDisabled=true" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d"');
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.json({ jobs: [] });
  }
});

app.post('/api/cron/:id/toggle', async (req, res) => {
  try {
    const payload = JSON.stringify({ jobId: req.params.id, patch: { enabled: req.body.enabled } });
    const { stdout } = await execAsync(`curl -s -X POST "http://localhost:18789/api/cron/update" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d" -H "Content-Type: application/json" -d '${payload}'`);
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Portfolio - Polygon
app.get('/api/portfolio/polygon', async (req, res) => {
  try {
    const script = `
      const {ethers}=require('ethers');
      const p=new ethers.JsonRpcProvider('https://polygon-rpc.com');
      const w='0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942';
      const USDC='0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359';
      const abi=['function balanceOf(address) view returns (uint256)'];
      Promise.all([
        p.getBalance(w),
        new ethers.Contract(USDC,abi,p).balanceOf(w)
      ]).then(([matic,usdc])=>{
        const m=parseFloat(ethers.formatEther(matic));
        const u=parseFloat(ethers.formatUnits(usdc,6));
        console.log(JSON.stringify({
          totalUsd: u + m*0.5,
          tokens:[
            {symbol:'USDC',balance:u,price:1,value:u},
            {symbol:'MATIC',balance:m,price:0.5,value:m*0.5}
          ]
        }));
      }).catch(e=>console.log('{"totalUsd":50,"tokens":[{"symbol":"USDC","balance":50,"price":1,"value":50}]}'));
    `;
    const { stdout } = await execAsync(`timeout 10 node -e "${script.replace(/\n/g, '')}"`, { cwd: WORKSPACE });
    res.json(JSON.parse(stdout.trim()));
  } catch (e) {
    res.json({ totalUsd: 50, tokens: [{ symbol: 'USDC', balance: 50, price: 1, value: 50 }] });
  }
});

// API: Portfolio - JIBCHAIN
app.get('/api/portfolio/jibchain', async (req, res) => {
  try {
    const script = `
      const {ethers}=require('ethers');
      const p=new ethers.JsonRpcProvider('https://rpc-l1.jibchain.net');
      const w='0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942';
      p.getBalance(w).then(b=>{
        const jbc=parseFloat(ethers.formatEther(b));
        console.log(JSON.stringify({
          totalUsd: jbc*0.001,
          tokens:[{symbol:'JBC',balance:jbc,price:0.001,value:jbc*0.001}]
        }));
      }).catch(()=>console.log('{"totalUsd":0,"tokens":[]}'));
    `;
    const { stdout } = await execAsync(`timeout 10 node -e "${script.replace(/\n/g, '')}"`, { cwd: WORKSPACE });
    res.json(JSON.parse(stdout.trim()));
  } catch (e) {
    res.json({ totalUsd: 0, tokens: [] });
  }
});

// API: Intel - Polymarket markets
app.get('/api/intel/polymarket', async (req, res) => {
  try {
    const { stdout } = await execAsync(`curl -s "https://gamma-api.polymarket.com/markets?closed=false&limit=10&order=volume24hr&ascending=false"`, { timeout: 10000 });
    const markets = JSON.parse(stdout);
    res.json({
      markets: markets.map(m => ({
        question: m.question,
        yesPrice: parseFloat(m.outcomePrices?.[0] || 0.5),
        volume24h: parseFloat(m.volume24hr || 0)
      }))
    });
  } catch (e) {
    res.json({ markets: [] });
  }
});

// =====================
// ENGINEER API ENDPOINTS
// =====================

// API: Git overview
app.get('/api/engineer/git', async (req, res) => {
  try {
    const results = {
      branch: '',
      branches: [],
      commits: [],
      stats: { today: 0, week: 0, total: 0 },
      lastPush: null,
      remoteUrl: ''
    };

    // Current branch
    try {
      const { stdout } = await execAsync('git branch --show-current', { cwd: WORKSPACE });
      results.branch = stdout.trim();
    } catch (e) {}

    // All branches
    try {
      const { stdout } = await execAsync('git branch -a --format="%(refname:short)|%(committerdate:relative)"', { cwd: WORKSPACE });
      results.branches = stdout.trim().split('\n').filter(Boolean).slice(0, 10).map(line => {
        const [name, date] = line.split('|');
        return { name, lastCommit: date };
      });
    } catch (e) {}

    // Recent commits
    try {
      const { stdout } = await execAsync('git log --oneline -10 --format="%h|%s|%cr|%an"', { cwd: WORKSPACE });
      results.commits = stdout.trim().split('\n').filter(Boolean).map(line => {
        const [hash, message, time, author] = line.split('|');
        return { hash, message, time, author };
      });
    } catch (e) {}

    // Commit stats
    try {
      const { stdout: todayCount } = await execAsync('git log --oneline --since="midnight" | wc -l', { cwd: WORKSPACE });
      const { stdout: weekCount } = await execAsync('git log --oneline --since="1 week ago" | wc -l', { cwd: WORKSPACE });
      const { stdout: totalCount } = await execAsync('git rev-list --count HEAD 2>/dev/null || echo 0', { cwd: WORKSPACE });
      results.stats = {
        today: parseInt(todayCount.trim()) || 0,
        week: parseInt(weekCount.trim()) || 0,
        total: parseInt(totalCount.trim()) || 0
      };
    } catch (e) {}

    // Remote URL
    try {
      const { stdout } = await execAsync('git remote get-url origin 2>/dev/null || echo ""', { cwd: WORKSPACE });
      results.remoteUrl = stdout.trim();
    } catch (e) {}

    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Code quality
app.get('/api/engineer/code', async (req, res) => {
  try {
    const results = {
      fileTypes: {},
      todos: [],
      stats: { files: 0, lines: 0, largest: [] }
    };

    // File type counts
    try {
      const { stdout } = await execAsync(`find ${WORKSPACE} -type f -name "*.*" -not -path "*/node_modules/*" -not -path "*/.git/*" | sed 's/.*\\.//' | sort | uniq -c | sort -rn | head -10`);
      stdout.trim().split('\n').filter(Boolean).forEach(line => {
        const match = line.trim().match(/(\d+)\s+(\w+)/);
        if (match) results.fileTypes[match[2]] = parseInt(match[1]);
      });
    } catch (e) {}

    // TODO/FIXME scanner
    try {
      const { stdout } = await execAsync(`grep -rn --include="*.js" --include="*.md" -E "(TODO|FIXME|HACK|XXX):" ${WORKSPACE} 2>/dev/null | grep -v node_modules | head -15`);
      results.todos = stdout.trim().split('\n').filter(Boolean).map(line => {
        const match = line.match(/([^:]+):(\d+):(.+)/);
        if (match) {
          return {
            file: match[1].replace(WORKSPACE + '/', ''),
            line: parseInt(match[2]),
            text: match[3].trim().substring(0, 80)
          };
        }
        return null;
      }).filter(Boolean);
    } catch (e) {}

    // Code stats
    try {
      const { stdout: fileCount } = await execAsync(`find ${WORKSPACE} -type f -name "*.js" -not -path "*/node_modules/*" | wc -l`);
      const { stdout: lineCount } = await execAsync(`find ${WORKSPACE} -type f -name "*.js" -not -path "*/node_modules/*" -exec cat {} + 2>/dev/null | wc -l`);
      const { stdout: largest } = await execAsync(`find ${WORKSPACE} -type f -name "*.js" -not -path "*/node_modules/*" -exec wc -l {} + 2>/dev/null | sort -rn | head -6 | tail -5`);
      
      results.stats.files = parseInt(fileCount.trim()) || 0;
      results.stats.lines = parseInt(lineCount.trim()) || 0;
      results.stats.largest = largest.trim().split('\n').filter(Boolean).map(line => {
        const match = line.trim().match(/(\d+)\s+(.+)/);
        if (match) return { lines: parseInt(match[1]), file: match[2].replace(WORKSPACE + '/', '') };
        return null;
      }).filter(Boolean);
    } catch (e) {}

    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Dependencies
app.get('/api/engineer/deps', async (req, res) => {
  try {
    const results = {
      installed: 0,
      outdated: [],
      vulnerabilities: { total: 0, critical: 0, high: 0, moderate: 0, low: 0 }
    };

    // Installed count
    try {
      const pkg = JSON.parse(await fs.readFile(path.join(WORKSPACE, 'package.json'), 'utf-8'));
      results.installed = Object.keys(pkg.dependencies || {}).length + Object.keys(pkg.devDependencies || {}).length;
    } catch (e) {}

    // Outdated packages
    try {
      const { stdout } = await execAsync('npm outdated --json 2>/dev/null || echo "{}"', { cwd: WORKSPACE, timeout: 30000 });
      const outdated = JSON.parse(stdout);
      results.outdated = Object.entries(outdated).slice(0, 10).map(([name, info]) => ({
        name,
        current: info.current,
        latest: info.latest
      }));
    } catch (e) {}

    // Vulnerabilities (npm audit)
    try {
      const { stdout } = await execAsync('npm audit --json 2>/dev/null || echo "{}"', { cwd: WORKSPACE, timeout: 30000 });
      const audit = JSON.parse(stdout);
      if (audit.metadata?.vulnerabilities) {
        results.vulnerabilities = audit.metadata.vulnerabilities;
        results.vulnerabilities.total = audit.metadata.vulnerabilities.total || 0;
      }
    } catch (e) {}

    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Environment info
app.get('/api/engineer/env', async (req, res) => {
  try {
    const results = {
      node: '',
      npm: '',
      pm2: '',
      os: '',
      uptime: 0
    };

    try {
      const { stdout: nodeV } = await execAsync('node -v');
      const { stdout: npmV } = await execAsync('npm -v');
      const { stdout: pm2V } = await execAsync('pm2 -v 2>/dev/null || echo "N/A"');
      const { stdout: osInfo } = await execAsync('uname -sr');
      const { stdout: uptime } = await execAsync('cat /proc/uptime');

      results.node = nodeV.trim();
      results.npm = npmV.trim();
      results.pm2 = pm2V.trim();
      results.os = osInfo.trim();
      results.uptime = parseFloat(uptime.split(' ')[0]) || 0;
    } catch (e) {}

    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Quick actions
app.post('/api/engineer/git/:action', async (req, res) => {
  const { action } = req.params;
  try {
    let result = '';
    switch (action) {
      case 'pull':
        const { stdout: pullOut } = await execAsync('git pull', { cwd: WORKSPACE });
        result = pullOut;
        break;
      case 'status':
        const { stdout: statusOut } = await execAsync('git status --short', { cwd: WORKSPACE });
        result = statusOut || 'Clean working tree';
        break;
      case 'stash':
        const { stdout: stashOut } = await execAsync('git stash', { cwd: WORKSPACE });
        result = stashOut;
        break;
      default:
        return res.status(400).json({ error: 'Invalid action' });
    }
    res.json({ ok: true, output: result });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// SALES API ENDPOINTS
// =====================

const SALES_FILE = path.join(WORKSPACE, 'dashboard', 'sales-data.json');

async function loadSalesData() {
  try {
    const data = await fs.readFile(SALES_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (e) {
    // Default sales data structure
    return {
      products: [
        { id: 1, name: 'AI Trading Bot Setup', price: 500, category: 'service', sold: 0 },
        { id: 2, name: 'Dashboard Template', price: 200, category: 'template', sold: 0 },
        { id: 3, name: 'Custom Skill Development', price: 300, category: 'service', sold: 0 },
        { id: 4, name: 'Bot Consulting (1hr)', price: 100, category: 'consulting', sold: 0 }
      ],
      leads: [],
      orders: [],
      targets: { daily: 100, weekly: 500, monthly: 2000 }
    };
  }
}

async function saveSalesData(data) {
  await fs.writeFile(SALES_FILE, JSON.stringify(data, null, 2));
}

// Get sales overview
app.get('/api/sales/overview', async (req, res) => {
  try {
    const data = await loadSalesData();
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
    
    // Calculate revenue
    const todayOrders = data.orders.filter(o => o.date >= today && o.status === 'completed');
    const weekOrders = data.orders.filter(o => o.date >= weekAgo && o.status === 'completed');
    const monthOrders = data.orders.filter(o => o.date >= monthStart && o.status === 'completed');
    
    const revenue = {
      today: todayOrders.reduce((sum, o) => sum + o.amount, 0),
      week: weekOrders.reduce((sum, o) => sum + o.amount, 0),
      month: monthOrders.reduce((sum, o) => sum + o.amount, 0),
      total: data.orders.filter(o => o.status === 'completed').reduce((sum, o) => sum + o.amount, 0)
    };
    
    // Pipeline counts
    const pipeline = {
      leads: data.leads.filter(l => l.status === 'new').length,
      contacted: data.leads.filter(l => l.status === 'contacted').length,
      negotiating: data.leads.filter(l => l.status === 'negotiating').length,
      closed: data.leads.filter(l => l.status === 'closed').length
    };
    
    res.json({
      revenue,
      targets: data.targets,
      pipeline,
      totalProducts: data.products.length,
      totalOrders: data.orders.length,
      conversionRate: data.leads.length > 0 ? 
        Math.round((pipeline.closed / data.leads.length) * 100) : 0
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get products
app.get('/api/sales/products', async (req, res) => {
  try {
    const data = await loadSalesData();
    res.json(data.products);
  } catch (e) {
    res.json([]);
  }
});

// Add/update product
app.post('/api/sales/products', async (req, res) => {
  try {
    const data = await loadSalesData();
    const product = req.body;
    if (product.id) {
      const idx = data.products.findIndex(p => p.id === product.id);
      if (idx >= 0) data.products[idx] = product;
    } else {
      product.id = Date.now();
      product.sold = 0;
      data.products.push(product);
    }
    await saveSalesData(data);
    res.json(product);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get leads
app.get('/api/sales/leads', async (req, res) => {
  try {
    const data = await loadSalesData();
    res.json(data.leads);
  } catch (e) {
    res.json([]);
  }
});

// Add/update lead
app.post('/api/sales/leads', async (req, res) => {
  try {
    const data = await loadSalesData();
    const lead = req.body;
    if (lead.id) {
      const idx = data.leads.findIndex(l => l.id === lead.id);
      if (idx >= 0) data.leads[idx] = { ...data.leads[idx], ...lead };
    } else {
      lead.id = Date.now();
      lead.createdAt = new Date().toISOString();
      lead.status = lead.status || 'new';
      data.leads.push(lead);
    }
    await saveSalesData(data);
    res.json(lead);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Update lead status
app.patch('/api/sales/leads/:id', async (req, res) => {
  try {
    const data = await loadSalesData();
    const idx = data.leads.findIndex(l => l.id === parseInt(req.params.id));
    if (idx >= 0) {
      data.leads[idx] = { ...data.leads[idx], ...req.body };
      await saveSalesData(data);
      res.json(data.leads[idx]);
    } else {
      res.status(404).json({ error: 'Lead not found' });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get orders
app.get('/api/sales/orders', async (req, res) => {
  try {
    const data = await loadSalesData();
    res.json(data.orders);
  } catch (e) {
    res.json([]);
  }
});

// Add order
app.post('/api/sales/orders', async (req, res) => {
  try {
    const data = await loadSalesData();
    const order = {
      id: Date.now(),
      ...req.body,
      date: new Date().toISOString().split('T')[0],
      status: 'completed'
    };
    data.orders.push(order);
    
    // Update product sold count
    const product = data.products.find(p => p.id === order.productId);
    if (product) product.sold++;
    
    await saveSalesData(data);
    res.json(order);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Update targets
app.post('/api/sales/targets', async (req, res) => {
  try {
    const data = await loadSalesData();
    data.targets = { ...data.targets, ...req.body };
    await saveSalesData(data);
    res.json(data.targets);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// ANALYTICS API ENDPOINTS
// =====================

// Get bot analytics from trade logs
app.get('/api/analytics/overview', async (req, res) => {
  try {
    // Read sniper state for PnL
    let sniperPnL = { realized: 0, unrealized: 0, trades: 0, wins: 0 };
    try {
      const state = JSON.parse(await fs.readFile(path.join(WORKSPACE, 'sniper-state.json'), 'utf-8'));
      sniperPnL.realized = state.realizedPnL || 0;
      sniperPnL.trades = state.totalTrades || 0;
    } catch (e) {}

    // Read trades.jsonl for detailed analytics
    let trades = [];
    try {
      const tradesData = await fs.readFile(path.join(WORKSPACE, 'memory', 'trades.jsonl'), 'utf-8');
      trades = tradesData.trim().split('\n').filter(Boolean).map(line => {
        try { return JSON.parse(line); } catch { return null; }
      }).filter(Boolean);
    } catch (e) {}

    // Calculate metrics
    const totalTrades = trades.length;
    const wins = trades.filter(t => (t.pnl || 0) > 0).length;
    const losses = trades.filter(t => (t.pnl || 0) < 0).length;
    const totalPnL = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const winRate = totalTrades > 0 ? (wins / totalTrades * 100).toFixed(1) : 0;

    // Get PM2 bot stats
    let botStats = [];
    try {
      const { stdout } = await execAsync('pm2 jlist');
      const bots = JSON.parse(stdout);
      botStats = bots.filter(b => b.name !== 'momo-dashboard').map(b => ({
        name: b.name,
        status: b.pm2_env.status,
        uptime: b.pm2_env.pm_uptime || 0,
        restarts: b.pm2_env.restart_time,
        cpu: b.monit?.cpu || 0,
        memory: b.monit?.memory || 0
      }));
    } catch (e) {}

    res.json({
      pnl: {
        total: totalPnL,
        realized: sniperPnL.realized,
        today: trades.filter(t => t.timestamp && new Date(t.timestamp).toDateString() === new Date().toDateString())
          .reduce((sum, t) => sum + (t.pnl || 0), 0)
      },
      trades: { total: totalTrades, wins, losses, winRate },
      bots: botStats,
      recentTrades: trades.slice(-10).reverse()
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// SCHEDULER API ENDPOINTS  
// =====================

// Get cron jobs from OpenClaw
app.get('/api/scheduler/jobs', async (req, res) => {
  try {
    const { stdout } = await execAsync('curl -s "http://localhost:18789/api/cron/list?includeDisabled=true" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d"');
    const data = JSON.parse(stdout);
    res.json(data.jobs || []);
  } catch (e) {
    res.json([]);
  }
});

// Toggle cron job
app.post('/api/scheduler/toggle/:id', async (req, res) => {
  try {
    const { enabled } = req.body;
    const payload = JSON.stringify({ jobId: req.params.id, patch: { enabled } });
    const { stdout } = await execAsync(`curl -s -X POST "http://localhost:18789/api/cron/update" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d" -H "Content-Type: application/json" -d '${payload}'`);
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Run cron job now
app.post('/api/scheduler/run/:id', async (req, res) => {
  try {
    const payload = JSON.stringify({ jobId: req.params.id });
    const { stdout } = await execAsync(`curl -s -X POST "http://localhost:18789/api/cron/run" -H "Authorization: Bearer d8ba80bb2d8b02318bc9fbef446c59433e49b9063ec5869d" -H "Content-Type: application/json" -d '${payload}'`);
    res.json(JSON.parse(stdout));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// CONTENT API ENDPOINTS
// =====================

const CONTENT_FILE = path.join(WORKSPACE, 'dashboard', 'content-data.json');

async function loadContentData() {
  try {
    return JSON.parse(await fs.readFile(CONTENT_FILE, 'utf-8'));
  } catch (e) {
    return { posts: [], ideas: [], calendar: [] };
  }
}

async function saveContentData(data) {
  await fs.writeFile(CONTENT_FILE, JSON.stringify(data, null, 2));
}

app.get('/api/content/overview', async (req, res) => {
  try {
    const data = await loadContentData();
    res.json({
      posts: data.posts || [],
      ideas: data.ideas || [],
      stats: {
        total: (data.posts || []).length,
        scheduled: (data.posts || []).filter(p => p.status === 'scheduled').length,
        published: (data.posts || []).filter(p => p.status === 'published').length
      }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/content/posts', async (req, res) => {
  try {
    const data = await loadContentData();
    const post = { id: Date.now(), ...req.body, createdAt: new Date().toISOString() };
    data.posts = data.posts || [];
    data.posts.push(post);
    await saveContentData(data);
    res.json(post);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/content/ideas', async (req, res) => {
  try {
    const data = await loadContentData();
    const idea = { id: Date.now(), ...req.body, createdAt: new Date().toISOString() };
    data.ideas = data.ideas || [];
    data.ideas.push(idea);
    await saveContentData(data);
    res.json(idea);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// COMMUNITY API ENDPOINTS
// =====================

app.get('/api/community/stats', async (req, res) => {
  try {
    // Mock stats - would connect to Twitter/Telegram APIs
    res.json({
      twitter: { followers: 0, following: 0, tweets: 0 },
      telegram: { members: 1, messages: 0 },
      discord: { members: 0, online: 0 },
      farcaster: { followers: 0, casts: 0 },
      engagement: { likes: 0, retweets: 0, replies: 0 }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// =====================
// DESIGN API ENDPOINTS
// =====================

app.get('/api/design/assets', async (req, res) => {
  try {
    // List image files in workspace
    const assetsDir = path.join(WORKSPACE, 'momo-token');
    let assets = [];
    try {
      const files = await fs.readdir(assetsDir);
      assets = files.filter(f => /\.(png|jpg|jpeg|gif|svg)$/i.test(f)).map(f => ({
        name: f,
        path: `momo-token/${f}`,
        type: f.split('.').pop()
      }));
    } catch (e) {}
    
    res.json({
      assets,
      templates: [
        { id: 1, name: 'Twitter Banner', size: '1500x500' },
        { id: 2, name: 'Profile Picture', size: '400x400' },
        { id: 3, name: 'Meme Template', size: '800x800' }
      ]
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Socket.io with auth
io.use((socket, next) => {
  const sessionId = socket.handshake.headers.cookie?.match(/session=([^;]+)/)?.[1];
  if (sessionId && sessions.has(sessionId)) {
    const session = sessions.get(sessionId);
    if (Date.now() < session.expiresAt) {
      socket.session = session;
      return next();
    }
  }
  next(new Error('Authentication required'));
});

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.session?.user || 'unknown'}`);
  socket.on('disconnect', () => console.log('Client disconnected'));
});

// Cleanup expired sessions periodically
setInterval(() => {
  const now = Date.now();
  for (const [id, session] of sessions) {
    if (now > session.expiresAt) {
      sessions.delete(id);
    }
  }
}, 60 * 1000);

// =====================
// PREDICT DEPARTMENT API
// =====================

const PREDICT_DIR = path.join(WORKSPACE, 'btc-predictor');
const TRADES_LOG = path.join(PREDICT_DIR, 'trades.log');
const POLYMARKET_CREDS = path.join(WORKSPACE, 'polymarket-bot', 'api-creds.json');

// Load trades from log file
async function loadTrades() {
  try {
    const data = await fs.readFile(TRADES_LOG, 'utf-8');
    return data.trim().split('\n').filter(Boolean).map(line => {
      try {
        // Parse log format: [timestamp] TYPE SIDE @ PRICE | $AMOUNT | MARKET
        const match = line.match(/\[(.*?)\] (\w+) (\w+) @ ([\d.]+)% \| \$([\d.]+) \| (.+)/);
        if (match) {
          return {
            timestamp: match[1],
            type: match[2],
            side: match[3],
            price: parseFloat(match[4]) / 100,
            amount: parseFloat(match[5]),
            market: match[6]
          };
        }
        return null;
      } catch { return null; }
    }).filter(Boolean);
  } catch {
    return [];
  }
}

// Load active positions from position files
async function loadPositions() {
  const positions = [];
  const assets = ['btc', 'eth', 'sol', 'spx'];
  
  for (const asset of assets) {
    try {
      const file = path.join(PREDICT_DIR, `position-${asset}.json`);
      const data = await fs.readFile(file, 'utf-8');
      const pos = JSON.parse(data);
      positions.push({ asset: asset.toUpperCase(), ...pos });
    } catch { /* no position */ }
  }
  
  return positions;
}

// API: Get PREDICT overview
app.get('/api/predict/overview', requireAuth, async (req, res) => {
  try {
    // Load PnL summary
    let pnlData = { trades: [], summary: {} };
    try {
      const pnlFile = path.join(PREDICT_DIR, 'pnl-summary.json');
      pnlData = JSON.parse(await fs.readFile(pnlFile, 'utf-8'));
    } catch {}
    
    // Fetch REAL positions from Polymarket API
    let positions = [];
    try {
      const { stdout } = await execAsync(`curl -s "https://data-api.polymarket.com/positions?user=0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942"`, { timeout: 15000 });
      const polyPositions = JSON.parse(stdout);
      
      // Filter out redeemable (resolved) positions - they're closed
      const activeOnly = polyPositions.filter(p => !p.redeemable);
      
      positions = activeOnly.map(p => ({
        asset: p.outcome || 'UNKNOWN',
        market: p.title || 'Unknown market',
        side: p.outcome || 'YES',
        size: parseFloat(p.size) || 0,
        cost: parseFloat(p.initialValue) || 0,
        currentValue: parseFloat(p.curValue) || 0,
        pnl: parseFloat(p.cashPnl) || 0,
        percentPnl: parseFloat(p.percentPnl) || 0
      }));
    } catch (e) {
      // Fallback to local positions
      positions = await loadPositions();
    }
    
    // Get wallet balance
    let balance = 0;
    try {
      const { stdout } = await execAsync(`cd ${WORKSPACE} && node -e "
        const { ethers } = require('ethers');
        const p = new ethers.JsonRpcProvider('https://1rpc.io/matic');
        const USDC = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174';
        const c = new ethers.Contract(USDC, ['function balanceOf(address) view returns (uint256)'], p);
        c.balanceOf('0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942').then(b => console.log(ethers.formatUnits(b, 6)));
      "`, { timeout: 15000 });
      balance = parseFloat(stdout.trim()) || 0;
    } catch {}
    
    const summary = pnlData.summary || {};
    const closedTrades = (pnlData.trades || []).filter(t => t.status === 'CLOSED');
    const wins = closedTrades.filter(t => t.result === 'WON').length;
    const losses = closedTrades.filter(t => t.result === 'LOST').length;
    
    // Calculate totalInvested from actual positions (cost basis)
    const activeInvested = positions.reduce((sum, p) => sum + (parseFloat(p.cost) || 0), 0);
    
    // Add closed trades cost to total invested
    const closedInvested = closedTrades.reduce((sum, t) => sum + (parseFloat(t.cost) || parseFloat(t.amount) || 0), 0);
    const totalInvestedCalc = activeInvested + closedInvested;
    
    // Calculate unrealized PnL from positions
    const unrealizedPnLCalc = positions.reduce((sum, p) => sum + (parseFloat(p.pnl) || 0), 0);
    
    // Calculate realized PnL from closed trades
    const realizedPnLCalc = closedTrades.reduce((sum, t) => sum + (parseFloat(t.pnl) || 0), 0);
    
    // Build slug lookup from positions AND gamma API events
    let slugLookup = {};
    try {
      // Get from current positions (has exact slugs for our bets)
      const { stdout } = await execAsync(`curl -s "https://data-api.polymarket.com/positions?user=0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942"`, { timeout: 15000 });
      const polyPositions = JSON.parse(stdout);
      polyPositions.forEach(p => {
        if (p.title && p.eventSlug) {
          slugLookup[p.title.toLowerCase()] = p.eventSlug;
          // Also index by keywords for fuzzy matching
          const words = p.title.toLowerCase().split(/\s+/).filter(w => w.length > 3);
          words.forEach(w => {
            if (!slugLookup[`kw:${w}`]) slugLookup[`kw:${w}`] = p.eventSlug;
          });
        }
      });
      
      // Also get from gamma events API for broader coverage
      const { stdout: eventsStdout } = await execAsync(`curl -s "https://gamma-api.polymarket.com/events?limit=200&closed=false"`, { timeout: 15000 });
      const events = JSON.parse(eventsStdout);
      events.forEach(e => {
        if (e.title && e.slug) {
          slugLookup[e.title.toLowerCase()] = e.slug;
          // Also index by keywords
          const words = e.title.toLowerCase().split(/\s+/).filter(w => w.length > 3);
          words.forEach(w => {
            if (!slugLookup[`kw:${w}`]) slugLookup[`kw:${w}`] = e.slug;
          });
        }
      });
    } catch {}
    
    // Helper: fuzzy match market name to slug
    const findSlug = (marketName) => {
      const name = (marketName || '').toLowerCase();
      // Exact match first
      if (slugLookup[name]) return slugLookup[name];
      
      // Special cases for common markets (check these first)
      if (name.includes('super bowl') || name.includes('superbowl')) {
        if (name.includes('first') && name.includes('score')) {
          return 'super-bowl-lx-first-team-score';
        }
        return 'super-bowl-champion-2026-731';
      }
      if (name.includes('gta 6') || name.includes('gta6')) {
        return 'will-gta-6-cost-100';
      }
      if (name.includes('vance') || name.includes('2028 election')) {
        return '2028-presidential-election-winner';
      }
      
      // Crypto up/down markets are dated and close quickly - don't link
      if (name.includes('up or down') || name.includes('updown')) {
        return null;
      }
      
      // NBA/sports with team names - try to find from positions
      if (name.includes('vs') || name.includes('beat') || name.includes('nba') || name.includes('nfl')) {
        // Extract team-like keywords (capitalized, longer words)
        const teamWords = name.split(/\s+/).filter(w => w.length > 4 && !['super', 'bowl', 'february', 'january'].includes(w));
        for (const tw of teamWords) {
          if (slugLookup[`kw:${tw}`]) return slugLookup[`kw:${tw}`];
        }
      }
      
      return null;
    };
    
    // Transform trades to match frontend format, include slug if found
    const recentTrades = (pnlData.trades || []).slice(-10).reverse().map(t => {
      const slug = findSlug(t.market);
      return {
        side: t.side || 'YES',
        price: t.entryPrice || 0,
        amount: t.cost || 0,
        market: t.market || 'Unknown',
        status: t.status || 'OPEN',
        pnl: t.pnl || 0,
        eventSlug: slug
      };
    });
    
    // Calculate total trades = active positions + closed trades
    // Use pnl-summary.json trades count as source of truth
    const totalTradesCalc = pnlData.trades?.length || (positions.length + closedTrades.length);
    
    // Calculate PnL percentage
    const netPnLCalc = realizedPnLCalc + unrealizedPnLCalc;
    const pnlPercent = totalInvestedCalc > 0 ? (netPnLCalc / totalInvestedCalc * 100) : 0;
    
    res.json({
      balance,
      totalTrades: totalTradesCalc,
      activePositions: positions.length,
      positions,
      totalInvested: totalInvestedCalc || summary.totalInvested || 0,
      realizedPnL: realizedPnLCalc || summary.realizedPnL || 0,
      unrealizedPnL: unrealizedPnLCalc || summary.unrealizedPnL || 0,
      netPnL: netPnLCalc,
      pnlPercent: pnlPercent.toFixed(1),
      wins,
      losses,
      winRate: closedTrades.length > 0 ? (wins / closedTrades.length * 100).toFixed(1) : 0,
      recentTrades
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Get all trades
app.get('/api/predict/trades', requireAuth, async (req, res) => {
  try {
    const trades = await loadTrades();
    res.json({ trades: trades.reverse() });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Get active positions with current prices (from Polymarket data API)
// API: Cancel Order via CLOB
app.post('/api/predict/orders/cancel', requireAuth, async (req, res) => {
  try {
    const { orderId } = req.body;
    if (!orderId) {
      return res.status(400).json({ error: 'orderId required' });
    }
    
    const { stdout } = await execAsync(`cd ${WORKSPACE}/btc-predictor && node -e "
const { ethers } = require('ethers');
const { ClobClient } = require('@polymarket/clob-client');
if (!ethers.Wallet.prototype._signTypedData) {
  ethers.Wallet.prototype._signTypedData = function(d, t, v) { return this.signTypedData(d, t, v); };
}
const creds = require('${WORKSPACE}/polymarket-bot/api-creds.json');
async function cancelOrder() {
  const provider = new ethers.JsonRpcProvider('https://polygon-bor-rpc.publicnode.com');
  const wallet = new ethers.Wallet('0xa507b5b8489db1eb0be2250a8328ad1dcda43223c8159b96049313b34651c95e', provider);
  const client = new ClobClient('https://clob.polymarket.com', 137, wallet, creds);
  const result = await client.cancelOrder({ orderID: '${orderId}' });
  console.log(JSON.stringify(result));
}
cancelOrder();
"`, { timeout: 20000 });
    
    const result = JSON.parse(stdout.trim());
    res.json({ success: true, result });
  } catch (e) {
    console.error('Cancel order error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// API: Get Open Orders from CLOB
app.get('/api/predict/orders', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync(`cd ${WORKSPACE}/btc-predictor && node -e "
const { ethers } = require('ethers');
const { ClobClient } = require('@polymarket/clob-client');
if (!ethers.Wallet.prototype._signTypedData) {
  ethers.Wallet.prototype._signTypedData = function(d, t, v) { return this.signTypedData(d, t, v); };
}
const creds = require('${WORKSPACE}/polymarket-bot/api-creds.json');
async function getOrders() {
  const provider = new ethers.JsonRpcProvider('https://polygon-bor-rpc.publicnode.com');
  const wallet = new ethers.Wallet('0xa507b5b8489db1eb0be2250a8328ad1dcda43223c8159b96049313b34651c95e', provider);
  const client = new ClobClient('https://clob.polymarket.com', 137, wallet, creds);
  const orders = await client.getOpenOrders();
  console.log(JSON.stringify(orders));
}
getOrders();
"`, { timeout: 20000 });
    
    const orders = JSON.parse(stdout.trim());
    
    // Map to friendly format
    const openOrders = orders.map(o => ({
      id: o.id,
      market: o.market,
      side: o.side,
      price: parseFloat(o.price) || 0,
      size: parseFloat(o.original_size) || 0,
      filled: parseFloat(o.size_matched) || 0,
      status: o.status,
      createdAt: o.created_at
    }));
    
    res.json({ orders: openOrders });
  } catch (e) {
    console.error('Open orders API error:', e.message);
    res.json({ orders: [], error: e.message });
  }
});

app.get('/api/predict/positions', requireAuth, async (req, res) => {
  try {
    // Fetch real positions from Polymarket
    const { stdout } = await execAsync(`curl -s "https://data-api.polymarket.com/positions?user=0x40dbB47c09e8B1c14b6e36722daF12eEd9E3f942"`, { timeout: 15000 });
    const polyPositions = JSON.parse(stdout);
    
    // Filter out redeemable positions (resolved/closed) - they go to Recent Trades
    const activePositions = polyPositions.filter(p => !p.redeemable);
    
    const positions = activePositions.map(p => ({
      asset: p.outcome || 'UNKNOWN',
      market: p.title || 'Unknown market',
      side: p.outcome || 'YES',
      size: p.size || 0,
      entryPrice: p.avgPrice || 0,
      entryTime: Date.now(),
      betSize: p.initialValue || 0,
      currentPrice: p.curPrice || 0,
      unrealizedPnL: p.cashPnl || 0,
      percentPnL: p.percentPnl || 0,
      eventSlug: p.eventSlug || p.slug || null,
      icon: p.icon || null,
      endDate: p.endDate || null
    }));
    
    const totalUnrealized = positions.reduce((sum, p) => sum + (p.unrealizedPnL || 0), 0);
    
    res.json({ 
      positions,
      totalUnrealized
    });
  } catch (e) {
    console.error('Positions API error:', e.message);
    res.status(500).json({ error: e.message, positions: [] });
  }
});

// API: Get Polymarket markets for potential trades
app.get('/api/predict/markets', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync(`curl -s "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&order=volume24hr&ascending=false"`, { timeout: 15000 });
    const markets = JSON.parse(stdout);
    
    res.json({
      markets: markets.map(m => {
        // outcomePrices is a JSON string like "[\"0.5\", \"0.5\"]"
        let yesPrice = 0.5, noPrice = 0.5;
        try {
          const prices = typeof m.outcomePrices === 'string' ? JSON.parse(m.outcomePrices) : m.outcomePrices;
          yesPrice = parseFloat(prices?.[0] || 0.5);
          noPrice = parseFloat(prices?.[1] || 0.5);
        } catch (e) {}
        
        return {
          id: m.id,
          question: m.question,
          yesPrice,
          noPrice,
          volume24h: parseFloat(m.volume24hr || 0),
          liquidity: parseFloat(m.liquidityNum || 0),
          spread: parseFloat(m.spread || 0),
          endDate: m.endDate
        };
      })
    });
  } catch (e) {
    console.error('Markets API error:', e.message);
    res.json({ markets: [], error: e.message });
  }
});

// API: Bot status
app.get('/api/predict/bot', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync('pm2 jlist', { timeout: 5000 });
    const processes = JSON.parse(stdout);
    const predictor = processes.find(p => p.name === 'btc-predictor');
    
    res.json({
      status: predictor?.pm2_env?.status || 'offline',
      uptime: predictor?.pm2_env?.pm_uptime ? Date.now() - predictor.pm2_env.pm_uptime : 0,
      restarts: predictor?.pm2_env?.restart_time || 0,
      cpu: predictor?.monit?.cpu || 0,
      memory: predictor?.monit?.memory || 0
    });
  } catch (e) {
    res.json({ status: 'error', error: e.message });
  }
});

// API: Get bot logs
app.get('/api/predict/logs', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync('pm2 logs btc-predictor --lines 50 --nostream 2>&1', { timeout: 5000 });
    res.json({ logs: stdout });
  } catch (e) {
    res.json({ logs: 'No logs available' });
  }
});

// API: Get opportunities from all strategies
app.get('/api/predict/opportunities', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync('pm2 logs btc-predictor --lines 500 --nostream 2>&1', { timeout: 10000 });
    const lines = stdout.split('\n');
    const opportunities = [];
    
    // Parse strategies from logs
    let currentAsset = null;
    let currentSlug = null;
    let currentQuestion = null;
    let lastUpdate = null;
    
    for (const line of lines) {
      // Extract timestamp
      const timeMatch = line.match(/(\d+\/\d+\/\d+,?\s+\d+:\d+:\d+\s*[AP]?M?)/i);
      if (timeMatch) lastUpdate = timeMatch[1];
      
      // Extract SLUG, ASSET, Q from structured log
      const slugMatch = line.match(/SLUG:([^\s|]+)/);
      const assetMatch = line.match(/ASSET:([^\s|]+)/);
      const questionMatch = line.match(/Q:([^|]+)/);
      
      if (slugMatch) currentSlug = slugMatch[1];
      if (assetMatch) currentAsset = assetMatch[1];
      if (questionMatch) currentQuestion = questionMatch[1].trim();
      
      // Fallback: Track current asset being analyzed
      if (!currentAsset) {
        if (line.includes('BTC') || line.includes('Bitcoin')) currentAsset = 'BTC';
        else if (line.includes('ETH') || line.includes('Ethereum')) currentAsset = 'ETH';
        else if (line.includes('SOL') || line.includes('Solana')) currentAsset = 'SOL';
        else if (line.includes('SPX') || line.includes('S&P')) currentAsset = 'SPX';
      }
      
      // Strategy A: TA (Technical Analysis)
      if (line.includes('📊 TA ANALYSIS') || line.includes('SIGNAL FLIP')) {
        const flipMatch = line.match(/SIGNAL FLIP: (\w+) → (\w+) \((\d+)%\)/);
        if (flipMatch) {
          opportunities.push({
            strategy: 'A',
            name: 'TA Signal',
            type: 'Signal Flip',
            detail: `${flipMatch[1]} → ${flipMatch[2]}`,
            market: currentAsset || 'Crypto',
            slug: currentSlug || '',
            question: currentQuestion || '',
            confidence: parseInt(flipMatch[3]),
            time: lastUpdate
          });
        }
      }
      
      // Strategy B: Sniper (Orderbook) - new format with signal
      if (line.includes('Flow:') && line.includes('Book:')) {
        const signalMatch = line.match(/(🟢 BUY UP|🔴 BUY DOWN|⚪ WAIT)/);
        const bookMatch = line.match(/Book:([-\d.]+)%/);
        const assetMatch = line.match(/ASSET:([^\s|]+)/);
        const slugMatch = line.match(/SLUG:([^\s|]+)/);
        const qMatch = line.match(/Q:(.+)$/);
        
        if (bookMatch && Math.abs(parseFloat(bookMatch[1])) > 20) {
          const imbalance = parseFloat(bookMatch[1]);
          const signal = signalMatch ? signalMatch[1] : (imbalance > 0 ? '🟢 BUY UP' : '🔴 BUY DOWN');
          opportunities.push({
            strategy: 'B',
            name: 'Sniper',
            type: signal,
            detail: `Book ${imbalance > 0 ? '+' : ''}${imbalance.toFixed(0)}%`,
            market: assetMatch ? assetMatch[1] : (currentAsset || 'Crypto'),
            slug: slugMatch ? slugMatch[1] : '',
            question: qMatch ? qMatch[1].trim() : '',
            confidence: Math.min(90, 50 + Math.abs(imbalance)),
            time: lastUpdate
          });
        }
      }
      
      // Strategy C: Liquid Markets (from LIQUID CRYPTO MARKETS log)
      if (line.includes('Liq:') && line.includes('SLUG:') && (line.includes('🟢') || line.includes('🔴') || line.includes('⚪'))) {
        const liqMatch = line.match(/Liq:\$(\d+)K/);
        const slugMatch = line.match(/SLUG:([^\s|]+)/);
        const assetMatch = line.match(/ASSET:([^\s|]+)/);
        const qMatch = line.match(/Q:(.+)$/);
        const signalMatch = line.match(/(UP|DOWN|NEUTRAL)\s+(\d+)%/);
        if (liqMatch && parseInt(liqMatch[1]) >= 50) {
          const signal = signalMatch ? signalMatch[1] : 'NEUTRAL';
          const odds = signalMatch ? signalMatch[2] : '50';
          opportunities.push({
            strategy: 'C',
            name: 'Liquid',
            type: signal === 'UP' ? '🟢 BUY UP' : signal === 'DOWN' ? '🔴 BUY DOWN' : '⚪ WAIT',
            detail: `${odds}% odds | $${liqMatch[1]}K liq`,
            market: assetMatch ? assetMatch[1] : (currentAsset || 'Crypto'),
            slug: slugMatch ? slugMatch[1] : '',
            question: qMatch ? qMatch[1].trim() : '',
            confidence: signal === 'NEUTRAL' ? 50 : 70,
            time: lastUpdate
          });
        }
      }
      
      // Strategy D: Sports
      if (line.includes('🏀') || line.includes('SPORTS') || line.includes('NBA') || line.includes('NFL') || line.includes('Super Bowl')) {
        const sportMatch = line.match(/(NBA|NFL|NHL|MLB|Super Bowl)[:\s]+(.+?)(?:\||$)/i);
        if (sportMatch) {
          opportunities.push({
            strategy: 'D',
            name: 'Sports',
            type: sportMatch[1].toUpperCase(),
            detail: sportMatch[2]?.trim() || 'Game found',
            market: sportMatch[1].toUpperCase(),
            confidence: 75,
            time: lastUpdate
          });
        }
      }
      
      // Strategy E: Weather
      if (line.includes('🌤') || line.includes('WEATHER')) {
        opportunities.push({
          strategy: 'E',
          name: 'Weather',
          type: 'Weather Market',
          detail: 'Weather prediction',
          market: 'Weather',
          confidence: 65,
          time: lastUpdate
        });
      }
      
      // Strategy F: Value/Arbitrage
      if (line.includes('edge') || line.includes('Edge')) {
        const edgeMatch = line.match(/([\d.]+)%\s*edge/i);
        if (edgeMatch && parseFloat(edgeMatch[1]) >= 5) {
          opportunities.push({
            strategy: 'F',
            name: 'Value',
            type: 'Edge Found',
            detail: `${edgeMatch[1]}% edge`,
            market: currentAsset || 'Mixed',
            confidence: Math.min(95, 70 + parseFloat(edgeMatch[1])),
            time: lastUpdate
          });
        }
      }
      
      // Mean Reversion signals
      if (line.includes('MEAN REVERSION')) {
        const revMatch = line.match(/MEAN REVERSION:\s*(\w+)\s*-\s*([^|]+)/i);
        const revSlugMatch = line.match(/SLUG:([^\s|]+)/);
        if (revMatch) {
          opportunities.push({
            strategy: 'F',
            name: 'Mean Reversion',
            type: revMatch[1],
            detail: revMatch[2].trim().slice(0, 30),
            market: currentAsset || 'Crypto',
            slug: revSlugMatch ? revSlugMatch[1] : (currentSlug || ''),
            question: currentQuestion || '',
            confidence: 65,
            time: lastUpdate
          });
        }
      }
      
      // Late Entry signals
      if (line.includes('LATE ENTRY')) {
        const lateMatch = line.match(/LATE ENTRY:\s*(\w+)/i);
        if (lateMatch) {
          opportunities.push({
            strategy: 'F',
            name: 'Late Entry',
            type: lateMatch[1],
            detail: 'Late entry opportunity',
            market: currentAsset || 'Crypto',
            confidence: 60,
            time: lastUpdate
          });
        }
      }
      
      // Volume Spike signals
      if (line.includes('VOLUME SPIKE') || line.includes('Volume:')) {
        const volMatch = line.match(/Volume[:\s]+([\d.]+)x/i);
        if (volMatch && parseFloat(volMatch[1]) >= 2) {
          opportunities.push({
            strategy: 'B',
            name: 'Volume Spike',
            type: 'High Volume',
            detail: `${volMatch[1]}x normal`,
            market: currentAsset || 'Crypto',
            confidence: 70,
            time: lastUpdate
          });
        }
      }
      
      // Confidence parsing
      if (line.includes('Confidence:')) {
        const confMatch = line.match(/Confidence:\s*([\d.]+)%/);
        if (confMatch) {
          const conf = parseFloat(confMatch[1]);
          if (conf >= 70) {
            opportunities.push({
              strategy: 'A',
              name: 'AI Analysis',
              type: 'Confidence',
              detail: `${conf.toFixed(0)}% conf`,
              market: currentAsset || 'Research',
              confidence: conf,
              time: lastUpdate
            });
          }
        }
      }
      
      // Kelly sizing (shows bot is considering a bet)
      if (line.includes('Kelly:')) {
        const kellyMatch = line.match(/Kelly:\s*\$([\d.]+)/);
        if (kellyMatch && parseFloat(kellyMatch[1]) > 0) {
          opportunities.push({
            strategy: 'F',
            name: 'Kelly Size',
            type: 'Bet Size',
            detail: `$${kellyMatch[1]} suggested`,
            market: currentAsset || 'Crypto',
            confidence: 60,
            time: lastUpdate
          });
        }
      }
    }
    
    // Filter out ALL crypto-related markets (no liquidity / can't trade)
    const CRYPTO_MARKETS = ['BTC', 'ETH', 'SOL', 'SPX', 'Bitcoin', 'Ethereum', 'Solana', 'Crypto'];
    const filtered = opportunities.filter(opp => {
      // Remove any opportunity where market is crypto-related
      const isCrypto = CRYPTO_MARKETS.some(asset => 
        opp.market?.toUpperCase() === asset.toUpperCase() ||
        opp.market?.toLowerCase().includes(asset.toLowerCase())
      );
      return !isCrypto;
    });
    
    // Dedupe and sort by confidence
    const unique = [];
    const seen = new Set();
    for (const opp of filtered.reverse()) {
      const key = `${opp.strategy}-${opp.type}-${opp.detail}`;
      if (!seen.has(key)) {
        seen.add(key);
        unique.push(opp);
      }
    }
    
    res.json({ 
      opportunities: unique.slice(0, 20),
      lastScan: new Date().toISOString()
    });
  } catch (e) {
    res.json({ opportunities: [], error: e.message });
  }
});

// ===================
// MOMO AUTONOMY RULES
// ===================
const MOMO_RULES_FILE = path.join(WORKSPACE, 'momo-rules.json');

// API: Get MOMO rules
app.get('/api/momo/rules', requireAuth, async (req, res) => {
  try {
    const data = await fs.readFile(MOMO_RULES_FILE, 'utf-8');
    res.json(JSON.parse(data));
  } catch (e) {
    // Default rules
    res.json({
      rules: {
        code: true,
        bot: true,
        twitter: true,
        testnet: true,
        scaling: true,
        cron: true,
        alerts: true,
        emergency: true,
        maintenance: true,
        money: false,
        external: false,
        deploy: false,
        security: false
      },
      config: {
        maxTradeSize: 20,
        minEdge: 15,
        maxSpread: 5,
        maxBetsPerDay: 3
      },
      alerts: {
        walletLow: true,
        botCrash: true,
        tradeResult: true,
        dailySummary: true
      },
      quiet: {
        enabled: true,
        start: '23:00',
        end: '08:00'
      },
      updated: null
    });
  }
});

// API: Save MOMO rules
app.post('/api/momo/rules', requireAuth, async (req, res) => {
  try {
    const { rules, config, alerts, quiet } = req.body;
    const data = {
      rules,
      config,
      alerts,
      quiet,
      updated: new Date().toISOString()
    };
    await fs.writeFile(MOMO_RULES_FILE, JSON.stringify(data, null, 2));
    res.json({ success: true, updated: data.updated });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🍑 Mission Control running at http://0.0.0.0:${PORT}`);
  console.log(`🔐 Login required - Rate limit: ${RATE_LIMIT_MAX} attempts per ${RATE_LIMIT_WINDOW/1000}s`);
});
