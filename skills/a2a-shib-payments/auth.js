/**
 * Authentication & Authorization System
 * Implements API key-based auth for A2A agents
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class AuthSystem {
  constructor(configPath = './auth-config.json') {
    this.configPath = configPath;
    this.config = this.loadConfig();
  }

  loadConfig() {
    if (!fs.existsSync(this.configPath)) {
      // Initialize with default config
      const defaultConfig = {
        agents: {
          'demo-requestor': {
            apiKey: this.generateApiKey(),
            permissions: ['balance', 'payment'],
            maxPaymentAmount: 1000, // SHIB
            enabled: true,
            createdAt: new Date().toISOString()
          }
        },
        requireAuth: true,
        defaultPermissions: ['balance']
      };
      this.saveConfig(defaultConfig);
      return defaultConfig;
    }
    
    const data = fs.readFileSync(this.configPath, 'utf8');
    return JSON.parse(data);
  }

  saveConfig(config = this.config) {
    fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2));
  }

  generateApiKey() {
    return 'sk_' + crypto.randomBytes(32).toString('hex');
  }

  /**
   * Validate API key and return agent info
   */
  authenticate(apiKey) {
    if (!this.config.requireAuth) {
      return { authenticated: true, agentId: 'anonymous', permissions: this.config.defaultPermissions };
    }

    for (const [agentId, agentConfig] of Object.entries(this.config.agents)) {
      if (agentConfig.apiKey === apiKey && agentConfig.enabled) {
        return {
          authenticated: true,
          agentId,
          permissions: agentConfig.permissions,
          maxPaymentAmount: agentConfig.maxPaymentAmount
        };
      }
    }

    return { authenticated: false, error: 'Invalid or disabled API key' };
  }

  /**
   * Check if agent has permission for action
   */
  authorize(agentId, action, amount = null) {
    const agentConfig = this.config.agents[agentId];
    if (!agentConfig) {
      return { authorized: false, reason: 'Agent not found' };
    }

    if (!agentConfig.enabled) {
      return { authorized: false, reason: 'Agent disabled' };
    }

    if (!agentConfig.permissions.includes(action)) {
      return { authorized: false, reason: `Missing permission: ${action}` };
    }

    // Check payment limits
    if (action === 'payment' && amount !== null) {
      if (amount > agentConfig.maxPaymentAmount) {
        return {
          authorized: false,
          reason: `Amount ${amount} exceeds limit ${agentConfig.maxPaymentAmount}`
        };
      }
    }

    return { authorized: true };
  }

  /**
   * Create new agent credentials
   */
  createAgent(agentId, permissions = ['balance'], maxPaymentAmount = 100) {
    if (this.config.agents[agentId]) {
      throw new Error(`Agent ${agentId} already exists`);
    }

    const apiKey = this.generateApiKey();
    this.config.agents[agentId] = {
      apiKey,
      permissions,
      maxPaymentAmount,
      enabled: true,
      createdAt: new Date().toISOString()
    };

    this.saveConfig();
    return { agentId, apiKey };
  }

  /**
   * Revoke agent access
   */
  revokeAgent(agentId) {
    if (!this.config.agents[agentId]) {
      throw new Error(`Agent ${agentId} not found`);
    }

    this.config.agents[agentId].enabled = false;
    this.config.agents[agentId].revokedAt = new Date().toISOString();
    this.saveConfig();
  }

  /**
   * Express middleware for A2A authentication
   */
  middleware() {
    return (req, res, next) => {
      // Extract API key from header
      const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');
      
      if (!apiKey && this.config.requireAuth) {
        return res.status(401).json({
          jsonrpc: '2.0',
          error: {
            code: -32001,
            message: 'Authentication required',
            data: { hint: 'Include X-API-Key header' }
          },
          id: req.body?.id || null
        });
      }

      const auth = this.authenticate(apiKey);
      if (!auth.authenticated) {
        return res.status(401).json({
          jsonrpc: '2.0',
          error: {
            code: -32001,
            message: auth.error
          },
          id: req.body?.id || null
        });
      }

      // Attach auth info to request
      req.agentAuth = auth;
      next();
    };
  }
}

module.exports = { AuthSystem };
