const fs = require('fs');
const path = require('path');

/**
 * EventLogger - Append-only event logging with deterministic ordering
 * Ensures all events are recorded in JSONL format with stable key ordering
 */
class EventLogger {
  constructor(filepath = 'events.jsonl') {
    this.filepath = path.resolve(filepath);
    this.eventCount = 0;
    
    // Initialize file if it doesn't exist
    if (!fs.existsSync(this.filepath)) {
      fs.writeFileSync(this.filepath, '');
    }
  }

  /**
   * Sort object keys alphabetically for deterministic output
   */
  sortKeys(obj) {
    if (Array.isArray(obj)) {
      return obj.map(item => this.sortKeys(item));
    } else if (obj !== null && typeof obj === 'object') {
      const sorted = {};
      Object.keys(obj)
        .sort()
        .forEach(key => {
          sorted[key] = this.sortKeys(obj[key]);
        });
      return sorted;
    }
    return obj;
  }

  /**
   * Emit market snapshot event
   */
  emitMarketSnapshot(vaults, chainId) {
    const event = {
      event_type: 'market_snapshot',
      timestamp: Math.floor(Date.now() / 1000),
      vaults: vaults.map(v => ({
        fees: v.fees,
        id: v.id,
        name: v.name,
        risk_score: v.risk_score,
        strategy: v.strategy,
        tvl_usd: v.tvl_usd,
        underlying: v.underlying,
        apr: v.apr
      })),
      chainId
    };
    this._append(event);
  }

  /**
   * Emit portfolio snapshot event
   */
  emitPortfolioSnapshot(allocation) {
    const event = {
      allocation: allocation,
      event_type: 'portfolio_snapshot',
      timestamp: Math.floor(Date.now() / 1000)
    };
    this._append(event);
  }

  /**
   * Emit decision event
   */
  emitDecision(decision, vaultStates) {
    const event = {
      decision: decision,
      event_type: 'decision',
      timestamp: Math.floor(Date.now() / 1000),
      vault_states: vaultStates
    };
    this._append(event);
  }

  /**
   * Emit execution record event
   */
  emitExecutionRecord(executionRecord) {
    const event = {
      event_type: 'execution_record',
      record: executionRecord,
      timestamp: Math.floor(Date.now() / 1000)
    };
    this._append(event);
  }

  /**
   * Emit error event
   */
  emitError(errorMsg, details = {}) {
    const event = {
      details: details,
      error: errorMsg,
      event_type: 'error',
      timestamp: Math.floor(Date.now() / 1000)
    };
    this._append(event);
  }

  /**
   * Append event to JSONL file with sorted keys
   */
  _append(event) {
    const sorted = this.sortKeys(event);
    const line = JSON.stringify(sorted) + '\n';
    try {
      fs.appendFileSync(this.filepath, line);
      this.eventCount++;
    } catch (err) {
      console.error(`Failed to append event: ${err.message}`);
    }
  }

  /**
   * Read all events from file
   */
  readEvents() {
    if (!fs.existsSync(this.filepath)) {
      return [];
    }
    const content = fs.readFileSync(this.filepath, 'utf-8');
    return content
      .split('\n')
      .filter(line => line.trim())
      .map(line => {
        try {
          return JSON.parse(line);
        } catch (err) {
          console.error(`Failed to parse event line: ${err.message}`);
          return null;
        }
      })
      .filter(event => event !== null);
  }

  /**
   * Clear events file
   */
  clear() {
    fs.writeFileSync(this.filepath, '');
    this.eventCount = 0;
  }
}

module.exports = EventLogger;
