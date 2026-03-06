/**
 * NEAR DCA Manager
 * Manages Dollar Cost Averaging strategies for NEAR token purchases
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const { BigNumber } = require('bignumber.js');

// NEAR API Integration
class NEARIntegration {
  constructor(config) {
    this.network = config.network || 'mainnet';
    this.exchanges = {
      'ref-finance': new RefFinanceExchange(config),
      'jumbo': new JumboExchange(config),
      'bancor': new BancorExchange(config),
      'on-chain': new OnChainSwap(config)
    };
  }

  async getNearPrice() {
    // Fetch NEAR price from multiple sources for accuracy
    const sources = [
      this.fetchFromCoingecko('near'),
      this.fetchFromBinance('NEARUSDT'),
      this.fetchFromCoinbase('NEAR-USD')
    ];

    try {
      const results = await Promise.allSettled(sources);
      const validPrices = results
        .filter(r => r.status === 'fulfilled')
        .map(r => r.value);

      if (validPrices.length === 0) {
        throw new Error('Failed to fetch NEAR price from any source');
      }

      // Calculate average price
      const avgPrice = validPrices.reduce((sum, price) => sum + price, 0) / validPrices.length;
      return avgPrice;
    } catch (error) {
      throw new Error(`Price fetch failed: ${error.message}`);
    }
  }

  async fetchFromCoingecko(id) {
    // Mock implementation - in production, use actual API
    return 6.50; // Placeholder price
  }

  async fetchFromBinance(symbol) {
    // Mock implementation
    return 6.52;
  }

  async fetchFromCoinbase(symbol) {
    // Mock implementation
    return 6.48;
  }

  async executeSwap(accountId, privateKey, exchange, amountUSD) {
    const nearPrice = await this.getNearPrice();
    const nearAmount = amountUSD / nearPrice;

    const exchangeInstance = this.exchanges[exchange];
    if (!exchangeInstance) {
      throw new Error(`Unknown exchange: ${exchange}`);
    }

    const result = await exchangeInstance.swap({
      accountId,
      privateKey,
      amountUSD,
      nearAmount,
      nearPrice
    });

    return {
      txHash: result.txHash,
      nearAmount,
      nearPrice,
      usdSpent: amountUSD,
      timestamp: new Date().toISOString(),
      exchange
    };
  }
}

// Exchange implementations
class RefFinanceExchange {
  constructor(config) {
    this.poolId = 4; // NEAR/USDT pool on Ref Finance
  }

  async swap({ accountId, privateKey, nearAmount, nearPrice }) {
    // Implement Ref Finance swap logic
    // This would use near-api-js to interact with Ref Finance contract
    const txHash = crypto.randomBytes(32).toString('hex');
    
    return {
      txHash,
      success: true,
      nearReceived: nearAmount * 0.997, // Account for 0.3% fee
      slippage: 0.001
    };
  }
}

class JumboExchange {
  constructor(config) {
    this.routerAddress = 'token.jumbo_exchange.near';
  }

  async swap({ accountId, privateKey, nearAmount, nearPrice }) {
    const txHash = crypto.randomBytes(32).toString('hex');
    
    return {
      txHash,
      success: true,
      nearReceived: nearAmount * 0.997,
      slippage: 0.001
    };
  }
}

class BancorExchange {
  constructor(config) {
    this.poolId = 'near-usdt';
  }

  async swap({ accountId, privateKey, nearAmount, nearPrice }) {
    const txHash = crypto.randomBytes(32).toString('hex');
    
    return {
      txHash,
      success: true,
      nearReceived: nearAmount * 0.995,
      slippage: 0.002
    };
  }
}

class OnChainSwap {
  constructor(config) {
    this.routerAddress = 'v2.ref-finance.near';
  }

  async swap({ accountId, privateKey, nearAmount, nearPrice }) {
    const txHash = crypto.randomBytes(32).toString('hex');
    
    return {
      txHash,
      success: true,
      nearReceived: nearAmount * 0.997,
      slippage: 0.001
    };
  }
}

// DCA Strategy Manager
class DCAManager {
  constructor(config) {
    this.config = config;
    this.storagePath = config.storage_path || './data/dca_state.json';
    this.nearIntegration = new NEARIntegration(config);
    this.strategies = new Map();
    this.history = [];
    this.alerts = new Map();
  }

  async load() {
    try {
      const data = await fs.readFile(this.storagePath, 'utf-8');
      const state = JSON.parse(data);
      
      this.strategies = new Map(
        Object.entries(state.strategies || {}).map(([id, s]) => [id, { ...s, nextExecution: new Date(s.nextExecution) }])
      );
      this.history = state.history || [];
      this.alerts = new Map(Object.entries(state.alerts || {}));
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.error('Failed to load DCA state:', error);
      }
    }
  }

  async save() {
    const state = {
      strategies: Object.fromEntries(
        Array.from(this.strategies.entries()).map(([id, s]) => [id, { ...s, nextExecution: s.nextExecution.toISOString() }])
      ),
      history: this.history,
      alerts: Object.fromEntries(this.alerts)
    };
    
    const dir = path.dirname(this.storagePath);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(this.storagePath, JSON.stringify(state, null, 2));
  }

  createStrategy({ name, amount, frequency, exchange, start_date, end_date }) {
    const id = crypto.randomUUID();
    const now = new Date();
    const startDate = start_date ? new Date(start_date) : now;
    const endDate = end_date ? new Date(end_date) : null;

    const strategy = {
      id,
      name,
      amount: parseFloat(amount),
      frequency,
      exchange,
      startDate: startDate.toISOString(),
      endDate: endDate?.toISOString(),
      status: 'active',
      createdAt: now.toISOString(),
      nextExecution: this.calculateNextExecution(startDate, frequency),
      totalInvested: 0,
      totalNearAccumulated: 0,
      purchaseCount: 0
    };

    this.strategies.set(id, strategy);
    this.save();
    
    return strategy;
  }

  calculateNextExecution(startDate, frequency) {
    const next = new Date(startDate);
    const now = new Date();

    switch (frequency) {
      case 'hourly':
        while (next <= now) {
          next.setHours(next.getHours() + 1);
        }
        break;
      case 'daily':
        while (next <= now) {
          next.setDate(next.getDate() + 1);
        }
        break;
      case 'weekly':
        while (next <= now) {
          next.setDate(next.getDate() + 7);
        }
        break;
      case 'monthly':
        while (next <= now) {
          next.setMonth(next.getMonth() + 1);
        }
        break;
    }

    return next;
  }

  calculateNextExecutionFromLast(lastExecution, frequency) {
    const next = new Date(lastExecution);

    switch (frequency) {
      case 'hourly':
        next.setHours(next.getHours() + 1);
        break;
      case 'daily':
        next.setDate(next.getDate() + 1);
        break;
      case 'weekly':
        next.setDate(next.getDate() + 7);
        break;
      case 'monthly':
        next.setMonth(next.getMonth() + 1);
        break;
    }

    return next;
  }

  listStrategies() {
    return Array.from(this.strategies.values());
  }

  getStrategy(id) {
    return this.strategies.get(id);
  }

  async executePurchase(strategyId, accountId = null, privateKey = null) {
    const strategy = this.strategies.get(strategyId);
    if (!strategy) {
      throw new Error(`Strategy not found: ${strategyId}`);
    }

    if (strategy.status !== 'active') {
      throw new Error(`Strategy is not active: ${strategy.status}`);
    }

    if (strategy.endDate && new Date() > new Date(strategy.endDate)) {
      strategy.status = 'completed';
      await this.save();
      throw new Error('Strategy has ended');
    }

    try {
      // Execute the swap
      const result = await this.nearIntegration.executeSwap(
        accountId || this.config.account_id,
        privateKey || this.config.private_key,
        strategy.exchange,
        strategy.amount
      );

      // Update strategy
      strategy.totalInvested += result.usdSpent;
      strategy.totalNearAccumulated += result.nearAmount;
      strategy.purchaseCount++;
      strategy.lastExecution = result.timestamp;
      strategy.nextExecution = this.calculateNextExecutionFromLast(
        new Date(result.timestamp),
        strategy.frequency
      );

      // Add to history
      const historyEntry = {
        id: crypto.randomUUID(),
        strategyId,
        strategyName: strategy.name,
        ...result,
        status: 'success'
      };
      this.history.unshift(historyEntry);

      // Limit history to 1000 entries
      if (this.history.length > 1000) {
        this.history = this.history.slice(0, 1000);
      }

      await this.save();
      await this.sendAlert(strategy, historyEntry);

      return historyEntry;
    } catch (error) {
      const errorEntry = {
        id: crypto.randomUUID(),
        strategyId,
        strategyName: strategy.name,
        timestamp: new Date().toISOString(),
        status: 'failed',
        error: error.message
      };
      
      this.history.unshift(errorEntry);
      await this.save();
      await this.sendAlert(strategy, errorEntry);

      throw error;
    }
  }

  async executeScheduledPurchases() {
    const now = new Date();
    const results = [];

    for (const [id, strategy] of this.strategies) {
      if (strategy.status !== 'active') continue;
      
      if (strategy.endDate && now > new Date(strategy.endDate)) {
        strategy.status = 'completed';
        continue;
      }

      if (now >= strategy.nextExecution) {
        try {
          const result = await this.executePurchase(id);
          results.push({ strategyId: id, status: 'success', result });
        } catch (error) {
          results.push({ strategyId: id, status: 'failed', error: error.message });
        }
      }
    }

    await this.save();
    return results;
  }

  pauseStrategy(id) {
    const strategy = this.strategies.get(id);
    if (!strategy) {
      throw new Error(`Strategy not found: ${id}`);
    }

    strategy.status = 'paused';
    this.save();
    return strategy;
  }

  resumeStrategy(id) {
    const strategy = this.strategies.get(id);
    if (!strategy) {
      throw new Error(`Strategy not found: ${id}`);
    }

    strategy.status = 'active';
    strategy.nextExecution = this.calculateNextExecutionFromLast(
      strategy.lastExecution ? new Date(strategy.lastExecution) : new Date(),
      strategy.frequency
    );
    this.save();
    return strategy;
  }

  deleteStrategy(id) {
    const deleted = this.strategies.delete(id);
    if (!deleted) {
      throw new Error(`Strategy not found: ${id}`);
    }
    this.save();
    return { success: true, id };
  }

  getHistory(strategyId = null, limit = 50) {
    let history = this.history;

    if (strategyId) {
      history = history.filter(h => h.strategyId === strategyId);
    }

    return history.slice(0, limit);
  }

  calculateCostBasis(strategyId = null) {
    const strategies = strategyId
      ? [this.strategies.get(strategyId)].filter(Boolean)
      : Array.from(this.strategies.values()).filter(s => s.status === 'active' || s.status === 'completed');

    const results = strategies.map(strategy => {
      const strategyHistory = this.history.filter(
        h => h.strategyId === strategyId && h.status === 'success'
      );

      if (strategyHistory.length === 0) {
        return {
          strategyId: strategy.id,
          strategyName: strategy.name,
          totalInvested: 0,
          totalNear: 0,
          averagePrice: 0,
          purchaseCount: 0
        };
      }

      const totalInvested = strategyHistory.reduce((sum, h) => sum + h.usdSpent, 0);
      const totalNear = strategyHistory.reduce((sum, h) => sum + h.nearAmount, 0);
      const averagePrice = totalNear > 0 ? totalInvested / totalNear : 0;

      return {
        strategyId: strategy.id,
        strategyName: strategy.name,
        totalInvested,
        totalNear,
        averagePrice,
        purchaseCount: strategyHistory.length,
        currentPrice: this.getRecentPrice(strategyHistory)
      };
    });

    return strategyId ? results[0] : results;
  }

  getRecentPrice(history) {
    if (history.length === 0) return 0;
    return history[0].nearPrice; // Most recent purchase price
  }

  configureAlerts({ strategy_id, enabled, channels, on_success, on_failure }) {
    const alertConfig = {
      enabled,
      channels: channels || [],
      on_success: on_success !== undefined ? on_success : true,
      on_failure: on_failure !== undefined ? on_failure : true
    };

    if (strategy_id) {
      this.alerts.set(strategy_id, alertConfig);
    } else {
      this.alerts.set('default', alertConfig);
    }

    this.save();
    return alertConfig;
  }

  async sendAlert(strategy, execution) {
    const alertConfig = this.alerts.get(strategy.id) || this.alerts.get('default');

    if (!alertConfig || !alertConfig.enabled) return;

    const shouldSend = execution.status === 'success' ? alertConfig.on_success : alertConfig.on_failure;
    if (!shouldSend) return;

    const message = this.formatAlertMessage(strategy, execution);

    for (const channel of alertConfig.channels) {
      try {
        await this.sendToChannel(channel, message);
      } catch (error) {
        console.error(`Failed to send alert to ${channel}:`, error);
      }
    }
  }

  formatAlertMessage(strategy, execution) {
    if (execution.status === 'success') {
      return `✅ DCA Purchase Successful\n` +
             `Strategy: ${strategy.name}\n` +
             `Amount: $${execution.usdSpent.toFixed(2)}\n` +
             `NEAR Received: ${execution.nearAmount.toFixed(4)}\n` +
             `Price: $${execution.nearPrice.toFixed(4)}\n` +
             `Exchange: ${execution.exchange}\n` +
             `TX: ${execution.txHash}`;
    } else {
      return `❌ DCA Purchase Failed\n` +
             `Strategy: ${strategy.name}\n` +
             `Error: ${execution.error}`;
    }
  }

  async sendToChannel(channel, message) {
    // This would integrate with OpenClaw's notification system
    // For now, just log the message
    console.log(`[DCA Alert - ${channel}] ${message}`);
  }
}

module.exports = { DCAManager, NEARIntegration };
