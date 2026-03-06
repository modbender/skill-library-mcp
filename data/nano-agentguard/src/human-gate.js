/**
 * HumanGate - Human Approval System
 *
 * Push confirmation requests to owners for dangerous operations
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { promisify } = require('util');

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

class HumanGate {
  constructor(options = {}) {
    this.pendingPath = options.pendingPath || path.join(process.env.HOME, '.agentguard', 'pending');
    this.timeout = options.timeout || 300; // 5 minutes default
    this.channels = options.channels || ['feishu', 'telegram', 'console'];
    this.onRequest = options.onRequest || null; // Callback for custom notification
  }

  /**
   * Initialize pending directory
   */
  async init() {
    await mkdir(this.pendingPath, { recursive: true });
  }

  /**
   * Generate unique request ID
   */
  generateId() {
    return crypto.randomBytes(16).toString('hex');
  }

  /**
   * Create approval request
   */
  async request(agentId, operation, details) {
    await this.init();

    const requestId = this.generateId();
    const expiresAt = new Date(Date.now() + this.timeout * 1000).toISOString();

    const request = {
      id: requestId,
      agentId,
      operation,
      details,
      status: 'pending',
      createdAt: new Date().toISOString(),
      expiresAt,
      response: null
    };

    // Save to pending
    const requestFile = path.join(this.pendingPath, `${requestId}.json`);
    await writeFile(requestFile, JSON.stringify(request, null, 2));

    // Send notification
    await this.notify(request);

    return request;
  }

  /**
   * Send notification to owner
   */
  async notify(request) {
    const message = this.formatMessage(request);

    // Use custom callback if provided
    if (this.onRequest) {
      return this.onRequest(request, message);
    }

    // Default: log to console
    console.log('\n' + '='.repeat(60));
    console.log('🔐 APPROVAL REQUIRED');
    console.log('='.repeat(60));
    console.log(`Agent: ${request.agentId}`);
    console.log(`Operation: ${request.operation}`);
    console.log(`Details: ${JSON.stringify(request.details, null, 2)}`);
    console.log(`Request ID: ${request.id}`);
    console.log(`Expires: ${request.expiresAt}`);
    console.log('='.repeat(60));
    console.log(`To approve: agentguard approve ${request.id}`);
    console.log(`To deny: agentguard deny ${request.id}`);
    console.log('='.repeat(60) + '\n');

    return { notified: true, channels: ['console'] };
  }

  /**
   * Format notification message
   */
  formatMessage(request) {
    return {
      title: '🔐 AgentGuard: Approval Required',
      body: `Agent "${request.agentId}" requests permission to:\n\n${request.operation}\n\nDetails: ${JSON.stringify(request.details)}`,
      requestId: request.id,
      expiresAt: request.expiresAt,
      actions: [
        { label: 'Approve', command: `agentguard approve ${request.id}` },
        { label: 'Deny', command: `agentguard deny ${request.id}` }
      ]
    };
  }

  /**
   * Approve a request
   */
  async approve(requestId, approvedBy = 'owner') {
    const requestFile = path.join(this.pendingPath, `${requestId}.json`);

    if (!fs.existsSync(requestFile)) {
      throw new Error(`Request not found: ${requestId}`);
    }

    const request = JSON.parse(await readFile(requestFile, 'utf8'));

    // Check expiration
    if (new Date() > new Date(request.expiresAt)) {
      request.status = 'expired';
      await writeFile(requestFile, JSON.stringify(request, null, 2));
      throw new Error('Request has expired');
    }

    // Check already processed
    if (request.status !== 'pending') {
      throw new Error(`Request already ${request.status}`);
    }

    // Approve
    request.status = 'approved';
    request.response = {
      approved: true,
      approvedBy,
      respondedAt: new Date().toISOString()
    };

    await writeFile(requestFile, JSON.stringify(request, null, 2));

    return request;
  }

  /**
   * Deny a request
   */
  async deny(requestId, deniedBy = 'owner', reason = '') {
    const requestFile = path.join(this.pendingPath, `${requestId}.json`);

    if (!fs.existsSync(requestFile)) {
      throw new Error(`Request not found: ${requestId}`);
    }

    const request = JSON.parse(await readFile(requestFile, 'utf8'));

    // Check expiration
    if (new Date() > new Date(request.expiresAt)) {
      request.status = 'expired';
      await writeFile(requestFile, JSON.stringify(request, null, 2));
      throw new Error('Request has expired');
    }

    // Check already processed
    if (request.status !== 'pending') {
      throw new Error(`Request already ${request.status}`);
    }

    // Deny
    request.status = 'denied';
    request.response = {
      approved: false,
      deniedBy,
      reason,
      respondedAt: new Date().toISOString()
    };

    await writeFile(requestFile, JSON.stringify(request, null, 2));

    return request;
  }

  /**
   * Get request status
   */
  async getStatus(requestId) {
    const requestFile = path.join(this.pendingPath, `${requestId}.json`);

    if (!fs.existsSync(requestFile)) {
      throw new Error(`Request not found: ${requestId}`);
    }

    return JSON.parse(await readFile(requestFile, 'utf8'));
  }

  /**
   * Wait for approval (with timeout)
   */
  async waitForApproval(requestId, pollInterval = 2000) {
    const startTime = Date.now();

    while (true) {
      const request = await this.getStatus(requestId);

      if (request.status === 'approved') {
        return { approved: true, request };
      }

      if (request.status === 'denied') {
        return { approved: false, request };
      }

      if (request.status === 'expired' || Date.now() > new Date(request.expiresAt).getTime()) {
        return { approved: false, request, reason: 'expired' };
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
  }

  /**
   * List pending requests
   */
  async listPending(agentId = null) {
    await this.init();

    const files = fs.readdirSync(this.pendingPath);
    const pending = [];

    for (const file of files) {
      if (!file.endsWith('.json')) continue;

      const request = JSON.parse(await readFile(path.join(this.pendingPath, file), 'utf8'));

      // Filter by agent if specified
      if (agentId && request.agentId !== agentId) continue;

      // Only return pending (not expired)
      if (request.status === 'pending' && new Date() <= new Date(request.expiresAt)) {
        pending.push(request);
      }
    }

    return pending;
  }

  /**
   * Clean up expired requests
   */
  async cleanup() {
    await this.init();

    const files = fs.readdirSync(this.pendingPath);
    const cleaned = [];

    for (const file of files) {
      if (!file.endsWith('.json')) continue;

      const request = JSON.parse(await readFile(path.join(this.pendingPath, file), 'utf8'));

      if (request.status !== 'pending' || new Date() > new Date(request.expiresAt)) {
        // Move to processed folder
        const processedPath = path.join(this.pendingPath, '..', 'processed');
        await mkdir(processedPath, { recursive: true });

        const oldPath = path.join(this.pendingPath, file);
        const newPath = path.join(processedPath, file);

        fs.renameSync(oldPath, newPath);
        cleaned.push(file);
      }
    }

    return { cleaned: cleaned.length };
  }
}

module.exports = HumanGate;
