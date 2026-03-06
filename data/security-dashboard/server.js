#!/usr/bin/env node
/**
 * Security Dashboard for OpenClaw
 * Monitors OpenClaw and Linux server security metrics
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = 18791;
const PUBLIC_DIR = path.join(__dirname, 'public');

// Execute command safely
function exec(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', timeout: 5000 }).trim();
  } catch (error) {
    return null;
  }
}

// Get OpenClaw metrics
function getOpenClawMetrics() {
  const configPath = `${process.env.HOME}/.openclaw/openclaw.json`;
  let config = {};
  
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    // Config not readable
  }

  // Check if gateway is running (by process name or port)
  const gatewayProcess = exec('pgrep -f "openclaw-gateway"');
  const gatewayStatus = gatewayProcess ? 'Active' : 'Inactive';
  
  const sessionCount = exec('ls -1 ~/.openclaw/agents/main/sessions/ 2>/dev/null | wc -l') || '0';
  const subagentCount = exec('ls -1 ~/.openclaw/subagents/ 2>/dev/null | wc -l') || '0';
  const skillsCount = exec('ls -1 ~/clawd/skills/ 2>/dev/null | wc -l') || '0';

  const currentVersion = exec('openclaw --version 2>&1') || 'Unknown';
  const latestVersion = exec('npm view openclaw version 2>/dev/null') || null;
  
  let updateStatus = 'Up to date';
  let updateAvailable = false;
  
  if (latestVersion && currentVersion !== 'Unknown') {
    if (currentVersion.trim() !== latestVersion.trim()) {
      updateStatus = `Update available: ${latestVersion}`;
      updateAvailable = true;
    }
  }

  const gateway = config.gateway || {};
  const auth = gateway.auth || {};
  
  return {
    gatewayStatus: gatewayStatus,
    bind: gateway.bind || 'unknown',
    tokenLength: auth.token ? auth.token.length : 0,
    authMode: auth.mode || 'unknown',
    sessionCount: sessionCount.trim(),
    subagentCount: subagentCount.trim(),
    skillsCount: skillsCount.trim(),
    currentVersion: currentVersion.trim(),
    updateStatus: updateStatus,
    updateAvailable: updateAvailable
  };
}

// Get network metrics
function getNetworkMetrics() {
  const tailscaleStatus = exec('tailscale status --json 2>/dev/null');
  const tailscaleIP = exec('tailscale ip -4 2>/dev/null') || 'Not available';
  const openPorts = exec('sudo ss -tlnp | grep -v "127.0.0.1" | wc -l') || '0';
  const firewallStatus = exec('sudo ufw status 2>/dev/null | head -1') || exec('sudo firewall-cmd --state 2>/dev/null') || 'Unknown';
  const connections = exec('ss -tn state established | wc -l') || '0';

  let tailscale = 'Disconnected';
  if (tailscaleStatus) {
    try {
      const ts = JSON.parse(tailscaleStatus);
      tailscale = ts.BackendState === 'Running' ? 'Connected' : 'Disconnected';
    } catch (e) {
      tailscale = 'Unknown';
    }
  }

  return {
    tailscale,
    tailscaleIP,
    openPorts: parseInt(openPorts) - 1, // Exclude header line
    firewall: firewallStatus.includes('active') ? 'Active' : 'Inactive',
    connections: parseInt(connections) - 1
  };
}

// Get system metrics
function getSystemMetrics() {
  const updates = exec('apt list --upgradable 2>/dev/null | grep -c upgradable') || '0';
  const uptime = exec('uptime -p') || 'Unknown';
  const load = exec('uptime | awk -F"load average:" \'{ print $2 }\' | awk \'{ print $1 }\'') || '0';
  const failedLogins = exec('sudo journalctl -u sshd --since "24 hours ago" 2>/dev/null | grep -c "Failed password"') || '0';
  const rootProcesses = exec('ps aux | grep -c "^root"') || '0';

  return {
    updates: parseInt(updates),
    uptime: uptime.replace('up ', ''),
    load: load.replace(',', ''),
    failedLogins: parseInt(failedLogins),
    rootProcesses: parseInt(rootProcesses)
  };
}

// Get SSH metrics
function getSSHMetrics() {
  const sshStatus = exec('systemctl is-active sshd') || exec('systemctl is-active ssh') || 'Unknown';
  const passwordAuth = exec('grep "^PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null') || 'Unknown';
  const fail2banStatus = exec('systemctl is-active fail2ban') || 'Inactive';
  const bannedIPs = exec('sudo fail2ban-client status sshd 2>/dev/null | grep "Currently banned:" | awk \'{print $4}\'') || '0';
  const activeSessions = exec('who | wc -l') || '0';

  return {
    status: sshStatus.charAt(0).toUpperCase() + sshStatus.slice(1),
    passwordAuth: passwordAuth.includes('no') ? 'Disabled' : 'Enabled',
    fail2ban: fail2banStatus.charAt(0).toUpperCase() + fail2banStatus.slice(1),
    bannedIPs: bannedIPs.trim(),
    activeSessions: activeSessions.trim()
  };
}

// Get certificate metrics
function getCertMetrics() {
  const caddyStatus = exec('systemctl is-active caddy') || 'Stopped';
  const publicTLS = caddyStatus === 'active' ? 'Enabled' : 'Disabled';

  return {
    caddyStatus: caddyStatus.charAt(0).toUpperCase() + caddyStatus.slice(1),
    publicTLS
  };
}

// Get resource metrics
function getResourceMetrics() {
  const cpu = exec('top -bn1 | grep "Cpu(s)" | awk \'{print $2}\' | cut -d"%" -f1') || '0';
  const memory = exec('free | grep Mem | awk \'{printf("%.0f", $3/$2 * 100.0)}\'') || '0';
  const disk = exec('df -h / | tail -1 | awk \'{print $5}\' | sed \'s/%//\'') || '0';
  const configPerms = exec('stat -c "%a" ~/.openclaw/openclaw.json 2>/dev/null') || '000';

  return {
    cpu: parseFloat(cpu).toFixed(1),
    memory: memory,
    disk: disk,
    configPerms: configPerms
  };
}

// Add after line 154 (after getResourceMetrics function)

// Get public exposure metrics  
function getPublicExposure() {
  // Check for publicly bound ports (0.0.0.0 or [::])
  const publicPortsRaw = exec('ss -tlnp 2>/dev/null | awk \'$4 ~ /^0\\.0\\.0\\.0/ || $4 ~ /^\\[::\\]/ {print $4}\'') || '';
  const publicPorts = publicPortsRaw.split('\n').filter(l => l.trim()).map(line => {
    const port = line.includes(':') ? line.split(':').pop() : 'unknown';
    return port;
  }).filter(p => p !== 'unknown');
  
  // Get service names for each port
  const portDetails = publicPorts.map(port => {
    const proc = exec(`ss -tlnp | grep ":${port}" | head -1`) || '';
    let service = 'unknown';
    if (proc.includes('sshd')) service = 'SSH';
    else if (proc.includes('node')) {
      if (proc.includes('18789')) service = 'OpenClaw Gateway';
      else if (proc.includes('18790')) service = 'Kanban Board';
      else if (proc.includes('18791')) service = 'Security Dashboard';
      else service = 'Node.js';
    } else if (proc.includes('cupsd')) service = 'CUPS';
    else if (proc.includes('nginx')) service = 'Nginx';
    else if (proc.includes('apache')) service = 'Apache';
    return { port, service };
  });
  
  // Check Tailscale status
  const tailscaleStatus = exec('tailscale status --json 2>/dev/null');
  let tailscaleActive = false;
  let tailscaleIP = 'Not available';
  if (tailscaleStatus) {
    try {
      const ts = JSON.parse(tailscaleStatus);
      tailscaleActive = ts.BackendState === 'Running';
      if (tailscaleActive) {
        tailscaleIP = exec('tailscale ip -4 2>/dev/null') || 'Not available';
      }
    } catch (e) {}
  }
  
  // Check OpenClaw gateway bind
  const openclawConfig = exec('cat ~/.openclaw/openclaw.json 2>/dev/null');
  let openclawBind = 'unknown';
  let openclawPort = 'unknown';
  if (openclawConfig) {
    try {
      const config = JSON.parse(openclawConfig);
      openclawBind = config.gateway?.bind || 'unknown';
      openclawPort = config.gateway?.port || 'unknown';
    } catch (e) {}
  }
  
  // Check localhost binding for internal dashboards
  const kanbanBind = exec('ss -tlnp | grep ":18790 "') || '';
  const securityBind = exec('ss -tlnp | grep ":18791 "') || '';
  
  const kanbanLocalhost = kanbanBind.includes('127.0.0.1:18790');
  const securityLocalhost = securityBind.includes('127.0.0.1:18791');
  
  const dashboardBindings = {
    kanban: kanbanLocalhost ? 'localhost' : (kanbanBind ? 'public' : 'not running'),
    security: securityLocalhost ? 'localhost' : (securityBind ? 'public' : 'not running')
  };
  
  // Determine exposure level
  const sshOnly = portDetails.length === 1 && portDetails[0].service === 'SSH';
  const hasInternalServices = portDetails.some(p => 
    p.service.includes('OpenClaw') || p.service.includes('Kanban') || p.service.includes('Security')
  );
  
  let exposureLevel = 'Minimal';
  if (sshOnly && tailscaleActive) {
    exposureLevel = 'Excellent'; // SSH only + Tailscale active
  } else if (hasInternalServices && !tailscaleActive) {
    exposureLevel = 'Warning'; // Internal services exposed without Tailscale
  } else if (portDetails.length > 3) {
    exposureLevel = 'High'; // Many ports exposed
  }
  
  return {
    publicPorts: portDetails.length,
    portDetails: portDetails.slice(0, 10),
    tailscaleActive,
    tailscaleIP,
    openclawBind,
    openclawPort,
    dashboardBindings,
    exposureLevel,
    recommendations: generateExposureRecommendations(portDetails, tailscaleActive, openclawBind, dashboardBindings)
  };
}

function generateExposureRecommendations(ports, tailscaleActive, openclawBind, dashboardBindings) {
  const recs = [];
  
  // Check for internal services on public IPs
  const internalServices = ports.filter(p => 
    p.service.includes('OpenClaw') || p.service.includes('Kanban') || p.service.includes('Security')
  );
  
  if (internalServices.length > 0 && openclawBind !== 'loopback') {
    recs.push('Change OpenClaw gateway bind to "loopback" in config');
  }
  
  // Check dashboard bindings
  if (dashboardBindings.kanban === 'public') {
    recs.push('⚠️ Kanban board exposed publicly - bind to 127.0.0.1 in server.js');
  }
  if (dashboardBindings.security === 'public') {
    recs.push('⚠️ Security dashboard exposed publicly - bind to 127.0.0.1 in server.js');
  }
  
  if (internalServices.length > 0 && !tailscaleActive) {
    recs.push('Enable Tailscale for secure remote access instead of public exposure');
  }
  
  if (!tailscaleActive) {
    recs.push('Install and enable Tailscale: tailscale up');
  }
  
  const nonSSH = ports.filter(p => p.service !== 'SSH');
  if (nonSSH.length > 0) {
    recs.push(`Review ${nonSSH.length} non-SSH public port(s): ${nonSSH.map(p => p.port).join(', ')}`);
  }
  
  if (recs.length === 0) {
    recs.push('✅ Configuration looks good!');
  }
  
  return recs;
}

// Generate alerts based on metrics
function generateAlerts(openclaw, network, system, ssh, certs, resources) {
  const alerts = [];

  // Critical alerts
  if (openclaw.tokenLength < 32) {
    alerts.push({
      level: 'critical',
      title: 'Weak Gateway Token',
      message: `Token is only ${openclaw.tokenLength} characters. Minimum 32 recommended.`
    });
  }

  if (ssh.passwordAuth === 'Enabled') {
    alerts.push({
      level: 'critical',
      title: 'SSH Password Authentication Enabled',
      message: 'Disable password authentication in /etc/ssh/sshd_config'
    });
  }

  if (resources.configPerms !== '600') {
    alerts.push({
      level: 'critical',
      title: 'Insecure Config Permissions',
      message: `Config file has ${resources.configPerms} permissions. Should be 600.`
    });
  }

  if (network.firewall === 'Inactive') {
    alerts.push({
      level: 'critical',
      title: 'Firewall Inactive',
      message: 'Enable UFW or firewalld for network protection immediately'
    });
  }

  if (ssh.fail2ban === 'Inactive' || ssh.fail2ban === 'inactive') {
    alerts.push({
      level: 'critical',
      title: 'fail2ban Inactive',
      message: 'SSH brute-force protection disabled. Enable fail2ban service.'
    });
  }

  // Warning alerts
  if (network.tailscale === 'Disconnected') {
    alerts.push({
      level: 'warning',
      title: 'Tailscale Disconnected',
      message: 'Secure remote access is not available. Run: tailscale up'
    });
  }

  if (system.updates > 20) {
    alerts.push({
      level: 'warning',
      title: `${system.updates} System Updates Available`,
      message: 'Run: sudo apt update && sudo apt upgrade'
    });
  }

  if (system.failedLogins > 10) {
    alerts.push({
      level: 'warning',
      title: `${system.failedLogins} Failed Login Attempts`,
      message: 'Possible brute force attack. Check logs.'
    });
  }

  if (parseInt(resources.disk) > 80) {
    alerts.push({
      level: 'warning',
      title: 'High Disk Usage',
      message: `Disk is ${resources.disk}% full. Clean up old files.`
    });
  }

  // Info alerts
  if (openclaw.bind !== 'loopback' && network.tailscale === 'Disconnected') {
    alerts.push({
      level: 'info',
      title: 'Gateway Exposed',
      message: 'Gateway binds to 0.0.0.0 but Tailscale is disconnected'
    });
  }

  return alerts;
}

// Calculate overall status
function calculateOverallStatus(alerts) {
  if (alerts.some(a => a.level === 'critical')) {
    return { level: 'critical', text: 'Critical Issues' };
  }
  if (alerts.some(a => a.level === 'warning')) {
    return { level: 'warning', text: 'Warnings Present' };
  }
  return { level: 'secure', text: 'All Secure' };
}

// Main request handler
const server = http.createServer((req, res) => {
  // API endpoint
  if (req.url === '/api/security' && req.method === 'GET') {
    const openclaw = getOpenClawMetrics();
    const network = getNetworkMetrics();
    const system = getSystemMetrics();
    const ssh = getSSHMetrics();
    const certificates = getCertMetrics();
    const resources = getResourceMetrics();
    const exposure = getPublicExposure();
    const alerts = generateAlerts(openclaw, network, system, ssh, certificates, resources);
    const status = calculateOverallStatus(alerts);

    const response = {
      timestamp: new Date().toISOString(),
      status,
      openclaw,
      network,
      system,
      ssh,
      certificates,
      resources,
      exposure,
      alerts
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(response));
    return;
  }

  // Serve static files
  let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
  const extname = path.extname(filePath);
  const contentType = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
  }[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404);
        res.end('404 Not Found');
      } else {
        res.writeHead(500);
        res.end('500 Internal Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Security Dashboard running on port ${PORT} (localhost only)`);
  console.log(`Access via: http://localhost:${PORT}`);
  console.log(`Or via Tailscale with port forwarding: ssh -L ${PORT}:localhost:${PORT} user@100.106.161.58`);
});
