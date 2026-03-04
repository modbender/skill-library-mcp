/**
 * AgentGuard - Agent Identity & Permission Guardian
 *
 * Main entry point
 */

const Vault = require('./vault-op'); // Use 1Password-aware vault
const Registry = require('./registry');
const Scope = require('./scope');
const Audit = require('./audit');
const HumanGate = require('./human-gate');
const OnePasswordProvider = require('./1password');
const FeishuNotifier = require('./feishu-notifier');
const CreditScore = require('./credit-score');
const ComplianceReporter = require('./compliance-reporter');

const path = require('path');

class AgentGuard {
  constructor(options = {}) {
    const basePath = options.basePath || path.join(process.env.HOME, '.agentguard');
    const masterPassword = options.masterPassword || process.env.AGENTGUARD_PASSWORD;

    // 1Password integration options
    this.use1Password = options.use1Password || process.env.AGENTGUARD_USE_1PASSWORD === 'true';

    // Feishu notification options
    this.feishuNotifier = null;
    if (options.feishu || process.env.AGENTGUARD_FEISHU === 'true') {
      this.feishuNotifier = new FeishuNotifier({
        openId: options.feishuOpenId || process.env.FEISHU_OPEN_ID,
        webhookUrl: options.feishuWebhook || process.env.FEISHU_WEBHOOK_URL,
        useOpenClaw: options.useOpenClaw !== false
      });
    }

    // Initialize components
    this.vault = new Vault(
      path.join(basePath, 'vault'),
      masterPassword,
      {
        use1Password: this.use1Password,
        opAccount: options.opAccount,
        opVault: options.opVault
      }
    );

    // Expose 1Password provider
    this.opProvider = this.vault.opProvider;

    this.registry = new Registry(
      path.join(basePath, 'registry.json')
    );

    this.scope = new Scope(this.registry);

    this.audit = new Audit(
      path.join(basePath, 'audit')
    );

    this.humanGate = new HumanGate({
      pendingPath: path.join(basePath, 'pending'),
      timeout: options.timeout || 300,
      channels: options.channels || ['feishu', 'console'],
      onRequest: options.onRequest || this._getDefaultNotifier()
    });
  }

  /**
   * Get default notification handler (Feishu if configured)
   */
  _getDefaultNotifier() {
    if (!this.feishuNotifier) return null;

    return async (request, message) => {
      const payload = await this.feishuNotifier.sendApprovalRequest(request);
      // Return payload for OpenClaw to send, or send via webhook
      if (this.feishuNotifier.useOpenClaw) {
        // Log that we would send to Feishu
        console.log('\n📱 Feishu notification prepared:');
        console.log('Target:', payload.target);
        console.log('Use: message tool to send');
        return payload;
      }
    };
  }

  /**
   * Initialize AgentGuard
   */
  async init() {
    await this.vault.init();
    await this.audit.init();
    await this.humanGate.init();
    await this.registry.load();

    // Initialize credit score system
    this.creditScore = new CreditScore(this.audit, this.registry);

    // Initialize compliance reporter
    this.complianceReporter = new ComplianceReporter(this.audit, this.registry, this.scope);
  }

  /**
   * Register a new agent
   */
  async registerAgent(agentId, options = {}) {
    const agent = await this.registry.register(agentId, options);
    await this.audit.log(agentId, 'agent_registered', { agent });
    return agent;
  }

  /**
   * Store a credential
   */
  async storeCredential(agentId, key, value) {
    // Check permission
    const check = await this.scope.check(agentId, 'access_credential');
    if (!check.allowed) {
      throw new Error(`Permission denied: ${check.reason}`);
    }

    const result = await this.vault.store(agentId, key, value);
    await this.audit.log(agentId, 'credential_stored', { key });
    return result;
  }

  /**
   * Get a credential
   */
  async getCredential(agentId, key) {
    // Check permission
    const check = await this.scope.check(agentId, 'access_credential');
    if (!check.allowed) {
      throw new Error(`Permission denied: ${check.reason}`);
    }

    const value = await this.vault.get(agentId, key);
    await this.audit.log(agentId, 'credential_accessed', { key });
    return value;
  }

  /**
   * Check permission and request approval if needed
   */
  async checkOrApprove(agentId, operation, details = {}) {
    const check = await this.scope.check(agentId, operation, details);

    // Log the check
    await this.audit.log(agentId, 'permission_check', {
      operation,
      result: check
    });

    if (!check.allowed) {
      throw new Error(`Permission denied: ${check.reason}`);
    }

    if (check.requiresApproval) {
      // Request human approval
      const request = await this.humanGate.request(agentId, operation, details);
      await this.audit.log(agentId, 'approval_requested', {
        operation,
        requestId: request.id
      });

      // Wait for approval
      const result = await this.humanGate.waitForApproval(request.id);

      await this.audit.log(agentId, 'approval_result', {
        operation,
        requestId: request.id,
        approved: result.approved
      });

      if (!result.approved) {
        throw new Error(`Operation denied: ${result.reason || 'human denied'}`);
      }

      return { allowed: true, requestId: request.id };
    }

    return { allowed: true, requiresApproval: false };
  }

  /**
   * Execute an operation with permission check
   */
  async execute(agentId, operation, details, fn) {
    const check = await this.checkOrApprove(agentId, operation, details);

    await this.registry.incrementStats(agentId, 'operations');

    const result = await fn();

    await this.audit.log(agentId, 'operation_executed', {
      operation,
      success: true
    });

    return result;
  }

  /**
   * Get agent info
   */
  async getAgent(agentId) {
    return this.registry.get(agentId);
  }

  /**
   * List agents
   */
  async listAgents(filter = {}) {
    return this.registry.list(filter);
  }

  /**
   * Get audit logs
   */
  async getAuditLogs(agentId, options = {}) {
    return this.audit.getLogs(agentId, options);
  }

  /**
   * Verify audit integrity
   */
  async verifyAudit(agentId, date) {
    return this.audit.verify(agentId, date);
  }

  /**
   * Get agent statistics
   */
  async getStats(agentId, days = 7) {
    return this.audit.stats(agentId, days);
  }

  /**
   * Set permission level
   */
  async setPermissionLevel(agentId, level) {
    return this.scope.setLevel(agentId, level);
  }

  /**
   * Set dangerous policy
   */
  async setDangerousPolicy(agentId, policy) {
    return this.scope.setDangerousPolicy(agentId, policy);
  }

  /**
   * Approve pending request
   */
  async approveRequest(requestId, approvedBy) {
    const request = await this.humanGate.approve(requestId, approvedBy);
    await this.registry.incrementStats(request.agentId, 'approvals');
    return request;
  }

  /**
   * Deny pending request
   */
  async denyRequest(requestId, deniedBy, reason) {
    const request = await this.humanGate.deny(requestId, deniedBy, reason);
    await this.registry.incrementStats(request.agentId, 'denials');
    return request;
  }

  /**
   * List pending requests
   */
  async listPendingRequests(agentId = null) {
    return this.humanGate.listPending(agentId);
  }

  // ============ 1Password Integration ============

  /**
   * Check if 1Password is available
   */
  async is1PasswordAvailable() {
    if (!this.opProvider) return false;
    return this.opProvider.isAvailable();
  }

  /**
   * Get 1Password status
   */
  async get1PasswordStatus() {
    if (!this.opProvider) {
      return { available: false, reason: '1Password not configured' };
    }

    const available = this.opProvider.isAvailable();
    if (!available) {
      return { available: false, reason: '1Password CLI not installed' };
    }

    try {
      const whoami = await this.opProvider.whoami();
      return {
        available: true,
        account: whoami?.email || whoami?.account_name || 'unknown',
        signedIn: !!whoami
      };
    } catch (e) {
      return { available: true, signedIn: false, reason: e.message };
    }
  }

  /**
   * Sync credentials from 1Password
   */
  async syncFrom1Password(agentId) {
    if (!this.use1Password) {
      throw new Error('1Password integration not enabled. Set use1Password: true');
    }

    const result = await this.vault.syncFrom1Password(agentId);
    await this.audit.log(agentId, '1password_sync', result);
    return result;
  }

  /**
   * Get 1Password reference for a credential
   */
  getOpReference(agentId, key) {
    if (!this.use1Password) {
      throw new Error('1Password integration not enabled');
    }
    return this.vault.getOpReference(agentId, key);
  }

  /**
   * Enable 1Password integration
   */
  async enable1Password(options = {}) {
    this.use1Password = true;

    // Reinitialize vault with 1Password
    const basePath = options.basePath || path.join(process.env.HOME, '.agentguard');
    this.vault = new Vault(
      path.join(basePath, 'vault'),
      this.vault.masterPassword,
      {
        use1Password: true,
        opAccount: options.opAccount,
        opVault: options.opVault || 'Private'
      }
    );

    await this.vault.init();
    this.opProvider = this.vault.opProvider;

    return this.get1PasswordStatus();
  }

  // ============ Feishu Integration ============

  /**
   * Enable Feishu notifications
   */
  enableFeishu(options = {}) {
    this.feishuNotifier = new FeishuNotifier({
      openId: options.openId,
      webhookUrl: options.webhookUrl,
      useOpenClaw: options.useOpenClaw !== false
    });

    // Update HumanGate callback
    this.humanGate.onRequest = async (request, message) => {
      const payload = await this.feishuNotifier.sendApprovalRequest(request);
      return payload;
    };

    return { enabled: true };
  }

  /**
   * Get Feishu notification payload for a request
   * (for OpenClaw to send via message tool)
   */
  async getFeishuPayload(request) {
    if (!this.feishuNotifier) {
      throw new Error('Feishu not configured. Call enableFeishu() first');
    }
    return this.feishuNotifier.sendApprovalRequest(request);
  }

  /**
   * Send approval result to Feishu
   */
  async notifyApprovalResult(request, approved, by) {
    if (!this.feishuNotifier) return null;
    return this.feishuNotifier.sendApprovalResult(request, approved, by);
  }

  // ============ Credit Score System ============

  /**
   * Calculate credit score for an agent
   */
  async getCreditScore(agentId, days = 30) {
    return this.creditScore.calculate(agentId, days);
  }

  /**
   * Generate credit report
   */
  async getCreditReport(agentId, days = 30) {
    return this.creditScore.generateReport(agentId, days);
  }

  /**
   * Compare credit scores of multiple agents
   */
  async compareCreditScores(agentIds, days = 30) {
    return this.creditScore.compare(agentIds, days);
  }

  /**
   * Get all agents ranked by credit score
   */
  async getAgentRankings(days = 30) {
    const agents = await this.listAgents();
    const agentIds = agents.map(a => a.id);
    return this.creditScore.compare(agentIds, days);
  }

  // ============ Compliance Reporting ============

  /**
   * Generate GDPR compliance report
   */
  async getGDPRReport(agentId, options = {}) {
    return this.complianceReporter.gdprReport(agentId, options);
  }

  /**
   * Generate CCPA compliance report
   */
  async getCCPAReport(agentId, options = {}) {
    return this.complianceReporter.ccpaReport(agentId, options);
  }

  /**
   * Generate full compliance report (GDPR + CCPA)
   */
  async getFullComplianceReport(agentId, options = {}) {
    const [gdpr, ccpa] = await Promise.all([
      this.getGDPRReport(agentId, options),
      this.getCCPAReport(agentId, options)
    ]);

    return {
      agentId,
      generatedAt: new Date().toISOString(),
      gdpr,
      ccpa,
      overallScore: Math.round((gdpr.summary.complianceScore + ccpa.summary.complianceScore) / 2),
      allRisks: [...gdpr.risks, ...ccpa.risks].sort((a, b) => {
        const order = { high: 0, medium: 1, low: 2 };
        return order[a.level] - order[b.level];
      }),
      allRecommendations: [...gdpr.recommendations, ...ccpa.recommendations]
        .sort((a, b) => {
          const order = { high: 0, medium: 1, low: 2 };
          return order[a.priority] - order[b.priority];
        })
    };
  }
}

// Export components and main class
module.exports = AgentGuard;
module.exports.Vault = Vault;
module.exports.Registry = Registry;
module.exports.Scope = Scope;
module.exports.Audit = Audit;
module.exports.HumanGate = HumanGate;
module.exports.OnePasswordProvider = OnePasswordProvider;
module.exports.FeishuNotifier = FeishuNotifier;
module.exports.CreditScore = CreditScore;
module.exports.ComplianceReporter = ComplianceReporter;
