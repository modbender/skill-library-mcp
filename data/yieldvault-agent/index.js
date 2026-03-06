const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

/**
 * YieldFarmingAgent
 * Deterministic autonomous decision engine for cross-vault yield optimization
 */
class YieldFarmingAgent {
  constructor(config = {}) {
    const defaultConfig = require('./config.default.json');
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Calculate NET_APR with risk penalty
   * risk_penalty = risk_score * 0.10 (10% penalty per risk unit)
   * net_apr = apr - fees - risk_penalty
   */
  calculateNetAPR(vault) {
    const riskPenalty = vault.risk_score * 0.10;
    const netAPR = vault.apr - vault.fees - riskPenalty;
    return Math.max(0, netAPR); // Floor at 0
  }

  /**
   * Main decision loop
   * @param {Array} vaults - Array of vault objects
   * @param {Object} currentAllocation - Current allocation state { vault_id: { shares, amount_usd, pending_rewards_usd } }
   * @returns {Object} Execution record with deterministic output
   */
  decide(vaults, currentAllocation = {}) {
    const timestamp = new Date().toISOString();
    const cycleNum = this.getCycleNum();

    // Calculate total allocation across all vaults
    const totalAllocation = Object.values(currentAllocation).reduce(
      (sum, a) => sum + parseFloat(a.amount_usd || 0),
      0
    );

    // Step 1: Calculate vault states and filter by risk
    const vaultStates = vaults
      .filter(v => v.risk_score <= 0.5)
      .map(v => {
        const netAPR = this.calculateNetAPR(v);
        const allocation = currentAllocation[v.id] || { shares: "0", amount_usd: "0", pending_rewards_usd: "0" };
        const allocationPercent = totalAllocation > 0 ? parseFloat(allocation.amount_usd) / totalAllocation : 0;

        return {
          vault_id: v.id,
          name: v.name,
          apr: v.apr,
          fees: v.fees,
          risk_score: v.risk_score,
          net_apr: netAPR,
          tvl_usd: v.tvl_usd,
          allocation_usd: parseFloat(allocation.amount_usd || 0),
          allocation_percent: allocationPercent,
          pending_rewards_usd: parseFloat(allocation.pending_rewards_usd || 0),
          underlying: v.underlying,
          strategy: v.strategy
        };
      })
      .sort((a, b) => b.net_apr - a.net_apr); // Sort by net_apr descending

    // Step 2: Find best vault
    const bestVault = vaultStates.length > 0 ? vaultStates[0] : null;

    // Step 3: Determine action
    let decision = {
      best_vault_id: bestVault ? bestVault.vault_id : null,
      best_vault_net_apr: bestVault ? bestVault.net_apr.toFixed(6) : "0.000000",
      action: null,
      rationale: ""
    };

    if (!bestVault) {
      decision.action = {
        action: "NOOP",
        vault_id: null,
        reason: "no_eligible_vaults"
      };
      decision.rationale = "All vaults exceed risk_score threshold (0.5)";
    } else {
      // 3a. Check HARVEST condition
      if (bestVault.pending_rewards_usd >= this.config.harvest_threshold_usd) {
        decision.action = {
          action: "HARVEST",
          vault_id: bestVault.vault_id,
          token: bestVault.underlying,
          amount: bestVault.pending_rewards_usd.toString()
        };
        decision.rationale = `Pending rewards ($${bestVault.pending_rewards_usd.toFixed(2)}) >= threshold ($${this.config.harvest_threshold_usd})`;
      }
      // 3b. Check COMPOUND condition
      else if (bestVault.net_apr >= this.config.rebalance_apr_delta) {
        decision.action = {
          action: "COMPOUND",
          vault_id: bestVault.vault_id,
          token: bestVault.underlying,
          amount: (bestVault.allocation_usd * bestVault.net_apr).toString()
        };
        decision.rationale = `Net APR (${(bestVault.net_apr * 100).toFixed(2)}%) >= compound threshold (${(this.config.rebalance_apr_delta * 100).toFixed(2)}%)`;
      }
      // 3c. Check REBALANCE condition
      else {
        const rebalanceTarget = vaultStates.find(
          v => v.net_apr > bestVault.net_apr + this.config.rebalance_apr_delta &&
               v.risk_score <= bestVault.risk_score &&
               bestVault.allocation_percent > 0 &&
               v.allocation_percent + bestVault.allocation_percent <= this.config.max_allocation_percent
        );

        if (rebalanceTarget) {
          const rebalanceAmount = bestVault.allocation_usd * 0.5; // Rebalance 50% to target
          decision.action = {
            action: "REBALANCE",
            from_vault_id: bestVault.vault_id,
            to_vault_id: rebalanceTarget.vault_id,
            token: bestVault.underlying,
            amount: rebalanceAmount.toString()
          };
          decision.rationale = `Rebalance opportunity: target APR delta (${((rebalanceTarget.net_apr - bestVault.net_apr) * 100).toFixed(2)}%) >= threshold (${(this.config.rebalance_apr_delta * 100).toFixed(2)}%), risk acceptable`;
        } else {
          decision.action = {
            action: "NOOP",
            vault_id: bestVault.vault_id,
            reason: "all_optimized"
          };
          decision.rationale = "Portfolio allocation is optimal; no viable improvements";
        }
      }
    }

    // Step 4: Build vault states for audit
    const auditVaultStates = vaultStates.map(v => ({
      id: v.vault_id,
      name: v.name,
      net_apr: v.net_apr.toFixed(6),
      allocation_percent: (v.allocation_percent * 100).toFixed(2),
      pending_rewards_usd: v.pending_rewards_usd.toFixed(2),
      risk_score: v.risk_score.toFixed(2)
    }));

    // Step 5: Compute hashes
    const decisionHash = this.computeHash(decision);
    
    // Build record without execution_hash first
    const recordWithoutExecHash = {
      timestamp,
      cycle_num: cycleNum,
      chainId: this.config.chainId,
      decision,
      vault_states: auditVaultStates,
      decision_hash: decisionHash
    };

    // Compute execution hash of record without execution_hash field
    const executionHash = this.computeHash(recordWithoutExecHash);

    // Final record with execution_hash
    const executionRecord = {
      ...recordWithoutExecHash,
      execution_hash: executionHash
    };

    return executionRecord;
  }

  /**
   * Compute SHA256 hash of object
   */
  computeHash(obj) {
    const str = JSON.stringify(obj);
    return crypto.createHash('sha256').update(str).digest('hex');
  }

  /**
   * Get current cycle number (timestamp-based)
   */
  getCycleNum() {
    return Math.floor(Date.now() / 1000);
  }

  /**
   * Verify execution record integrity
   */
  verifyRecord(record) {
    const computedDecisionHash = this.computeHash(record.decision);
    const decisionHashMatch = computedDecisionHash === record.decision_hash;

    // Build record copy without execution_hash for verification (same as original compute)
    const recordCopy = {
      timestamp: record.timestamp,
      cycle_num: record.cycle_num,
      chainId: record.chainId,
      decision: record.decision,
      vault_states: record.vault_states,
      decision_hash: record.decision_hash
    };
    const computedExecutionHash = this.computeHash(recordCopy);
    const executionHashMatch = computedExecutionHash === record.execution_hash;

    return {
      valid: decisionHashMatch && executionHashMatch,
      decision_hash_valid: decisionHashMatch,
      execution_hash_valid: executionHashMatch,
      errors: [
        !decisionHashMatch && "Decision hash mismatch",
        !executionHashMatch && "Execution hash mismatch"
      ].filter(Boolean)
    };
  }
}

module.exports = YieldFarmingAgent;

// CLI Usage
if (require.main === module) {
  const mockdata = require('./mockdata.json');
  const args = process.argv.slice(2);
  
  // Example current allocation
  const currentAllocation = {
    vault_bnb_lp_001: {
      shares: "1000",
      amount_usd: "50000",
      pending_rewards_usd: "1200"
    },
    vault_eth_staking_001: {
      shares: "500",
      amount_usd: "40000",
      pending_rewards_usd: "50"
    },
    vault_usdc_stable_001: {
      shares: "2000",
      amount_usd: "30000",
      pending_rewards_usd: "15"
    }
  };

  const agent = new YieldFarmingAgent();
  const execution = agent.decide(mockdata.vaults, currentAllocation);

  if (args.includes('--verify')) {
    console.log(JSON.stringify(execution, null, 2));
    const verification = agent.verifyRecord(execution);
    console.log('\n=== Hash Verification ===');
    console.log(JSON.stringify(verification, null, 2));
  } else {
    console.log(JSON.stringify(execution, null, 2));
  }
}
