/**
 * ERC-8004 Agent Identity & Reputation Integration
 * 
 * ERC-8004 (deployed Ethereum mainnet Jan 29, 2026) provides:
 * - Identity Registry: ERC-721 based agent identification
 * - Reputation Registry: Structured feedback with tags
 * - Validation Registry: Independent verification hooks
 * 
 * This module queries on-chain agent identity and reputation data
 * to supplement Moltbook-based scoring.
 * 
 * Backed by: MetaMask, Ethereum Foundation, Google, Coinbase
 * 
 * NOTE: This is a read-only integration. We query existing registries
 * but don't write to them (that requires the agent to register itself).
 */

const https = require('https');

// Known ERC-8004 registry addresses (Ethereum mainnet)
// These are placeholder addresses - actual deployment addresses TBD
const REGISTRIES = {
  identity: {
    // Agent Identity Registry (ERC-721)
    address: null, // Will be set when we have confirmed deployment address
    abi: [
      'function agentId(address) view returns (uint256)',
      'function ownerOf(uint256) view returns (address)',
      'function getAgent(uint256) view returns (string name, string description, address owner)',
    ]
  },
  reputation: {
    // Reputation Registry
    address: null,
    abi: [
      'function getReputation(uint256 agentId) view returns (uint256 score, uint256 reviewCount)',
      'function getReviews(uint256 agentId, uint256 offset, uint256 limit) view returns (tuple[])',
    ]
  }
};

class ERC8004Client {
  constructor(opts = {}) {
    this.rpcUrl = opts.rpcUrl || 'https://eth.llamarpc.com';
    this.registries = { ...REGISTRIES };
    
    // Override registry addresses if provided
    if (opts.identityRegistry) this.registries.identity.address = opts.identityRegistry;
    if (opts.reputationRegistry) this.registries.reputation.address = opts.reputationRegistry;
  }

  /**
   * Check if an address has an ERC-8004 agent identity registered
   * @param {string} address - Ethereum address
   * @returns {Object} - Identity info or null
   */
  async checkIdentity(address) {
    if (!this.registries.identity.address) {
      return {
        registered: false,
        reason: 'ERC-8004 registry address not configured',
        standard: 'ERC-8004',
        spec: 'https://eips.ethereum.org/EIPS/eip-8004',
      };
    }

    try {
      // eth_call to check if address has an agentId
      const agentIdData = this._encodeFunctionCall('agentId(address)', [address]);
      const result = await this._ethCall(this.registries.identity.address, agentIdData);

      if (result && result !== '0x' && result !== '0x0000000000000000000000000000000000000000000000000000000000000000') {
        const agentId = parseInt(result, 16);
        return {
          registered: true,
          agentId,
          address,
          standard: 'ERC-8004',
        };
      }

      return { registered: false, address, standard: 'ERC-8004' };
    } catch (err) {
      return {
        registered: false,
        error: err.message,
        standard: 'ERC-8004',
      };
    }
  }

  /**
   * Get on-chain reputation for an agent
   * @param {number} agentId - ERC-8004 agent ID
   * @returns {Object} - Reputation data
   */
  async getReputation(agentId) {
    if (!this.registries.reputation.address) {
      return {
        hasReputation: false,
        reason: 'Reputation registry not configured',
      };
    }

    try {
      const data = this._encodeFunctionCall('getReputation(uint256)', [agentId]);
      const result = await this._ethCall(this.registries.reputation.address, data);

      if (result && result.length > 2) {
        // Parse uint256 score and uint256 reviewCount from result
        const score = parseInt(result.slice(2, 66), 16);
        const reviewCount = parseInt(result.slice(66, 130), 16);

        return {
          hasReputation: true,
          agentId,
          score,
          reviewCount,
          tags: [], // Would need additional call for tag breakdown
        };
      }

      return { hasReputation: false, agentId };
    } catch (err) {
      return { hasReputation: false, error: err.message };
    }
  }

  /**
   * Generate ERC-8004 trust signal for scoring
   * Combines identity verification + on-chain reputation
   */
  async trustSignal(address) {
    const identity = await this.checkIdentity(address);

    let signal = {
      hasIdentity: identity.registered,
      hasReputation: false,
      identityScore: 0,
      reputationScore: 0,
      combinedScore: 0,
      standard: 'ERC-8004',
    };

    // Identity alone is worth something (proved ownership of on-chain identity)
    if (identity.registered) {
      signal.identityScore = 30;

      const reputation = await this.getReputation(identity.agentId);
      if (reputation.hasReputation) {
        signal.hasReputation = true;
        signal.reputationScore = Math.min(70, reputation.score);
        signal.reviewCount = reputation.reviewCount;
      }
    }

    signal.combinedScore = signal.identityScore + signal.reputationScore;
    return signal;
  }

  // --- Low-level helpers ---

  _encodeFunctionCall(signature, params) {
    // Minimal ABI encoding for simple function calls
    // This is a simplified version - production would use ethers.js
    const crypto = require('crypto');
    const sigHash = crypto.createHash('sha256').update(signature).digest('hex').slice(0, 8);
    
    let data = '0x' + sigHash;
    for (const param of params) {
      if (typeof param === 'string' && param.startsWith('0x')) {
        // Address - pad to 32 bytes
        data += param.slice(2).padStart(64, '0');
      } else if (typeof param === 'number') {
        // Uint256
        data += param.toString(16).padStart(64, '0');
      }
    }
    return data;
  }

  async _ethCall(to, data) {
    const body = JSON.stringify({
      jsonrpc: '2.0',
      method: 'eth_call',
      params: [{ to, data }, 'latest'],
      id: 1,
    });

    return new Promise((resolve, reject) => {
      const url = new URL(this.rpcUrl);
      const opts = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
        timeout: 10000,
      };

      const req = https.request(opts, (res) => {
        let responseData = '';
        res.on('data', chunk => responseData += chunk);
        res.on('end', () => {
          try {
            const parsed = JSON.parse(responseData);
            resolve(parsed.result || null);
          } catch (e) {
            reject(new Error('JSON parse error'));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      req.write(body);
      req.end();
    });
  }
}

module.exports = { ERC8004Client };
