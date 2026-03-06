/**
 * 🔧 Config Auditor
 * 
 * Audits OpenClaw configuration against security best practices
 * Checks for misconfigurations that could expose the system
 */

import fs from 'fs/promises';
import path from 'path';

// Security rules with severity and auto-fix capability
const SECURITY_RULES = [
  // Gateway rules
  {
    id: 'gateway-bind',
    category: 'gateway',
    severity: 'critical',
    check: (config) => config.gateway?.bind === 'loopback' || config.gateway?.bind === '127.0.0.1' || !config.gateway?.bind,
    message: 'Gateway should bind to loopback only',
    detail: 'Binding to 0.0.0.0 or public IP exposes the gateway to the internet',
    fix: 'Set gateway.bind to "loopback"',
    autoFixable: true,
    autoFix: (config) => {
      config.gateway = config.gateway || {};
      config.gateway.bind = 'loopback';
      return config;
    }
  },
  {
    id: 'gateway-auth-token',
    category: 'gateway',
    severity: 'high',
    check: (config) => !!config.gateway?.auth?.token || config.gateway?.bind === 'loopback',
    message: 'Gateway should have authentication token configured',
    detail: 'Without a token, anyone on the network can connect to the gateway',
    fix: 'Set gateway.auth.token or use loopback binding',
    autoFixable: false
  },
  {
    id: 'gateway-tailscale-funnel',
    category: 'gateway',
    severity: 'high',
    check: (config) => config.gateway?.tailscale?.mode !== 'funnel' || config.gateway?.auth?.mode === 'password',
    message: 'Tailscale Funnel requires password authentication',
    detail: 'Funnel exposes the gateway to the public internet',
    fix: 'Set gateway.auth.mode to "password" when using Funnel',
    autoFixable: true,
    autoFix: (config) => {
      if (config.gateway?.tailscale?.mode === 'funnel') {
        config.gateway.auth = config.gateway.auth || {};
        config.gateway.auth.mode = 'password';
      }
      return config;
    }
  },
  
  // Sandbox rules
  {
    id: 'sandbox-mode',
    category: 'sandbox',
    severity: 'critical',
    check: (config) => config.agents?.defaults?.sandbox?.mode === 'always',
    message: 'Sandbox mode should be "always" for maximum security',
    detail: 'Without sandboxing, the agent can execute arbitrary commands on the host',
    fix: 'Set agents.defaults.sandbox.mode to "always"',
    autoFixable: true,
    autoFix: (config) => {
      config.agents = config.agents || {};
      config.agents.defaults = config.agents.defaults || {};
      config.agents.defaults.sandbox = config.agents.defaults.sandbox || {};
      config.agents.defaults.sandbox.mode = 'always';
      return config;
    }
  },
  {
    id: 'sandbox-denylist',
    category: 'sandbox',
    severity: 'medium',
    check: (config) => {
      const denylist = config.agents?.defaults?.sandbox?.denylist || [];
      const dangerousTools = ['browser', 'canvas', 'nodes', 'gateway'];
      return dangerousTools.every(tool => denylist.includes(tool));
    },
    message: 'Dangerous tools should be in sandbox denylist',
    detail: 'Tools like browser, canvas, nodes can be exploited',
    fix: 'Add browser, canvas, nodes, gateway to sandbox.denylist',
    autoFixable: true,
    autoFix: (config) => {
      config.agents = config.agents || {};
      config.agents.defaults = config.agents.defaults || {};
      config.agents.defaults.sandbox = config.agents.defaults.sandbox || {};
      const current = config.agents.defaults.sandbox.denylist || [];
      const toAdd = ['browser', 'canvas', 'nodes', 'gateway'];
      config.agents.defaults.sandbox.denylist = [...new Set([...current, ...toAdd])];
      return config;
    }
  },
  
  // Channel rules - WhatsApp
  {
    id: 'whatsapp-dm-policy',
    category: 'channels',
    severity: 'critical',
    check: (config) => config.channels?.whatsapp?.dmPolicy !== 'open',
    message: 'WhatsApp DM policy should not be "open"',
    detail: 'Open DM policy allows anyone to interact with your assistant',
    fix: 'Set channels.whatsapp.dmPolicy to "pairing"',
    autoFixable: true,
    autoFix: (config) => {
      config.channels = config.channels || {};
      config.channels.whatsapp = config.channels.whatsapp || {};
      config.channels.whatsapp.dmPolicy = 'pairing';
      return config;
    }
  },
  {
    id: 'whatsapp-allowlist',
    category: 'channels',
    severity: 'high',
    check: (config) => {
      const allowFrom = config.channels?.whatsapp?.allowFrom;
      return !allowFrom || (Array.isArray(allowFrom) && !allowFrom.includes('*'));
    },
    message: 'WhatsApp should have explicit allowlist (not wildcard)',
    detail: 'Using "*" allows anyone to send messages',
    fix: 'Set channels.whatsapp.allowFrom to specific phone numbers',
    autoFixable: false
  },
  {
    id: 'whatsapp-group-mention',
    category: 'channels',
    severity: 'medium',
    check: (config) => {
      const groups = config.channels?.whatsapp?.groups;
      if (!groups) return true;
      return groups['*']?.requireMention !== false;
    },
    message: 'WhatsApp groups should require mention',
    detail: 'Without mention requirement, bot responds to all messages in groups',
    fix: 'Set channels.whatsapp.groups.*.requireMention to true',
    autoFixable: true,
    autoFix: (config) => {
      config.channels = config.channels || {};
      config.channels.whatsapp = config.channels.whatsapp || {};
      config.channels.whatsapp.groups = config.channels.whatsapp.groups || {};
      config.channels.whatsapp.groups['*'] = config.channels.whatsapp.groups['*'] || {};
      config.channels.whatsapp.groups['*'].requireMention = true;
      return config;
    }
  },
  
  // Channel rules - Telegram
  {
    id: 'telegram-dm-policy',
    category: 'channels',
    severity: 'critical',
    check: (config) => config.channels?.telegram?.dmPolicy !== 'open',
    message: 'Telegram DM policy should not be "open"',
    detail: 'Open DM policy allows anyone to interact with your bot',
    fix: 'Set channels.telegram.dmPolicy to "pairing"',
    autoFixable: true,
    autoFix: (config) => {
      config.channels = config.channels || {};
      config.channels.telegram = config.channels.telegram || {};
      config.channels.telegram.dmPolicy = 'pairing';
      return config;
    }
  },
  
  // Channel rules - Discord
  {
    id: 'discord-dm-policy',
    category: 'channels',
    severity: 'critical',
    check: (config) => config.channels?.discord?.dm?.policy !== 'open',
    message: 'Discord DM policy should not be "open"',
    detail: 'Open DM policy allows anyone to DM your bot',
    fix: 'Set channels.discord.dm.policy to "pairing"',
    autoFixable: true,
    autoFix: (config) => {
      config.channels = config.channels || {};
      config.channels.discord = config.channels.discord || {};
      config.channels.discord.dm = config.channels.discord.dm || {};
      config.channels.discord.dm.policy = 'pairing';
      return config;
    }
  },
  
  // Elevated mode
  {
    id: 'elevated-disabled',
    category: 'tools',
    severity: 'high',
    check: (config) => config.agents?.defaults?.tools?.elevated?.enabled !== true,
    message: 'Elevated mode should be disabled by default',
    detail: 'Elevated mode grants additional system permissions',
    fix: 'Set agents.defaults.tools.elevated.enabled to false',
    autoFixable: true,
    autoFix: (config) => {
      config.agents = config.agents || {};
      config.agents.defaults = config.agents.defaults || {};
      config.agents.defaults.tools = config.agents.defaults.tools || {};
      config.agents.defaults.tools.elevated = config.agents.defaults.tools.elevated || {};
      config.agents.defaults.tools.elevated.enabled = false;
      return config;
    }
  },
  {
    id: 'elevated-approval',
    category: 'tools',
    severity: 'medium',
    check: (config) => {
      if (config.agents?.defaults?.tools?.elevated?.enabled) {
        return config.agents.defaults.tools.elevated.requireApproval === true;
      }
      return true;
    },
    message: 'Elevated mode should require approval',
    detail: 'Without approval requirement, elevated commands run automatically',
    fix: 'Set agents.defaults.tools.elevated.requireApproval to true',
    autoFixable: true,
    autoFix: (config) => {
      if (config.agents?.defaults?.tools?.elevated?.enabled) {
        config.agents.defaults.tools.elevated.requireApproval = true;
      }
      return config;
    }
  },
  
  // Rate limiting
  {
    id: 'rate-limiting',
    category: 'security',
    severity: 'medium',
    check: (config) => config.security?.rateLimiting?.enabled === true,
    message: 'Rate limiting should be enabled',
    detail: 'Without rate limiting, abuse and cost overruns are possible',
    fix: 'Enable security.rateLimiting.enabled',
    autoFixable: true,
    autoFix: (config) => {
      config.security = config.security || {};
      config.security.rateLimiting = config.security.rateLimiting || {};
      config.security.rateLimiting.enabled = true;
      config.security.rateLimiting.maxRequestsPerMinute = config.security.rateLimiting.maxRequestsPerMinute || 30;
      config.security.rateLimiting.maxTokensPerHour = config.security.rateLimiting.maxTokensPerHour || 100000;
      return config;
    }
  },
  
  // Audit logging
  {
    id: 'audit-logging',
    category: 'security',
    severity: 'low',
    check: (config) => config.security?.audit?.enabled === true,
    message: 'Audit logging should be enabled',
    detail: 'Audit logs help track security events and debug issues',
    fix: 'Enable security.audit.enabled',
    autoFixable: true,
    autoFix: (config) => {
      config.security = config.security || {};
      config.security.audit = config.security.audit || {};
      config.security.audit.enabled = true;
      config.security.audit.logLevel = config.security.audit.logLevel || 'info';
      return config;
    }
  }
];

export class ConfigAuditor {
  constructor(config = {}) {
    this.suiteConfig = config;
    this.rules = SECURITY_RULES;
    this.strictMode = config.scanners?.config?.strictMode || false;
  }
  
  async scan(basePath, options = {}) {
    const findings = [];
    const summary = { critical: 0, high: 0, medium: 0, low: 0 };
    
    // Load OpenClaw config
    const configPath = path.join(basePath, 'openclaw.json');
    let openclawConfig = {};
    
    try {
      const configContent = await fs.readFile(configPath, 'utf-8');
      openclawConfig = JSON.parse(configContent);
    } catch (error) {
      if (error.code === 'ENOENT') {
        findings.push({
          type: 'config',
          severity: 'medium',
          message: 'No openclaw.json found - using defaults',
          location: configPath,
          fix: 'Create openclaw.json with secure defaults',
          autoFixable: true
        });
        summary.medium++;
      } else {
        findings.push({
          type: 'config',
          severity: 'high',
          message: `Failed to parse openclaw.json: ${error.message}`,
          location: configPath,
          fix: 'Fix JSON syntax errors',
          autoFixable: false
        });
        summary.high++;
        return { scanner: 'config', findings, summary };
      }
    }
    
    // Run all security rules
    for (const rule of this.rules) {
      const passed = rule.check(openclawConfig);
      
      if (!passed) {
        findings.push({
          type: 'config',
          ruleId: rule.id,
          category: rule.category,
          severity: rule.severity,
          message: rule.message,
          detail: rule.detail,
          fix: rule.fix,
          autoFixable: rule.autoFixable,
          autoFix: rule.autoFix
        });
        
        summary[rule.severity]++;
      } else if (options.verbose) {
        // In verbose mode, show passing checks too
        findings.push({
          type: 'config',
          ruleId: rule.id,
          category: rule.category,
          severity: 'pass',
          message: `✓ ${rule.message}`,
          passed: true
        });
      }
    }
    
    // Additional checks
    await this.checkNodeVersion(findings, summary);
    await this.checkFilePermissions(basePath, findings, summary);
    
    return {
      scanner: 'config',
      findings,
      summary,
      config: openclawConfig
    };
  }
  
  async checkNodeVersion(findings, summary) {
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion < 22) {
      findings.push({
        type: 'runtime',
        severity: 'critical',
        message: `Node.js version ${nodeVersion} is below required 22.x`,
        detail: 'Older Node versions have unpatched security vulnerabilities',
        fix: 'Upgrade to Node.js 22.12.0 or later',
        autoFixable: false
      });
      summary.critical++;
    }
  }
  
  async checkFilePermissions(basePath, findings, summary) {
    const sensitiveFiles = [
      'openclaw.json',
      'credentials.json',
      '.env'
    ];
    
    for (const filename of sensitiveFiles) {
      const filePath = path.join(basePath, filename);
      
      try {
        const stats = await fs.stat(filePath);
        const mode = stats.mode & 0o777;
        
        // Check if file is world-readable
        if (mode & 0o004) {
          findings.push({
            type: 'permissions',
            severity: 'high',
            message: `${filename} is world-readable`,
            detail: 'Sensitive files should not be readable by other users',
            fix: `chmod 600 ${filePath}`,
            autoFixable: true,
            autoFix: async () => {
              await fs.chmod(filePath, 0o600);
            }
          });
          summary.high++;
        }
        
        // Check if file is world-writable
        if (mode & 0o002) {
          findings.push({
            type: 'permissions',
            severity: 'critical',
            message: `${filename} is world-writable`,
            detail: 'Anyone can modify this file!',
            fix: `chmod 600 ${filePath}`,
            autoFixable: true,
            autoFix: async () => {
              await fs.chmod(filePath, 0o600);
            }
          });
          summary.critical++;
        }
      } catch {
        // File doesn't exist, skip
      }
    }
  }
}

export default ConfigAuditor;
