/**
 * NEAR DCA Skill Actions
 * Entry point for all DCA operations
 */

const path = require('path');
const { DCAManager } = require('../src/dca-manager');

// Global manager instance
let dcaManager = null;

function getManager(config) {
  if (!dcaManager) {
    dcaManager = new DCAManager(config);
    dcaManager.load();
  }
  return dcaManager;
}

/**
 * Action: Create a new DCA strategy
 */
async function createStrategy(params, context) {
  const { name, amount, frequency, exchange, start_date, end_date } = params;
  const config = context.config || {};

  const manager = getManager(config);
  const strategy = manager.createStrategy({
    name,
    amount,
    frequency,
    exchange: exchange || config.default_exchange || 'ref-finance',
    start_date,
    end_date
  });

  return {
    success: true,
    data: strategy,
    message: `DCA strategy "${name}" created successfully`
  };
}

/**
 * Action: List all DCA strategies
 */
async function listStrategies(params, context) {
  const config = context.config || {};
  const manager = getManager(config);
  const strategies = manager.listStrategies();

  return {
    success: true,
    data: strategies,
    count: strategies.length
  };
}

/**
 * Action: Get details of a specific strategy
 */
async function getStrategy(params, context) {
  const { strategy_id } = params;
  const config = context.config || {};

  const manager = getManager(config);
  const strategy = manager.getStrategy(strategy_id);

  if (!strategy) {
    return {
      success: false,
      error: 'Strategy not found'
    };
  }

  // Add cost basis calculation
  const costBasis = manager.calculateCostBasis(strategy_id);

  return {
    success: true,
    data: {
      ...strategy,
      costBasis
    }
  };
}

/**
 * Action: Manually execute a DCA purchase
 */
async function executePurchase(params, context) {
  const { strategy_id, account_id, private_key } = params;
  const config = context.config || {};

  const manager = getManager(config);

  try {
    const result = await manager.executePurchase(strategy_id, account_id, private_key);

    return {
      success: true,
      data: result,
      message: `Purchase executed successfully: ${result.nearAmount.toFixed(4)} NEAR at $${result.nearPrice.toFixed(4)}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Action: Pause a DCA strategy
 */
async function pauseStrategy(params, context) {
  const { strategy_id } = params;
  const config = context.config || {};

  const manager = getManager(config);

  try {
    const strategy = manager.pauseStrategy(strategy_id);
    return {
      success: true,
      data: strategy,
      message: `Strategy "${strategy.name}" paused`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Action: Resume a paused DCA strategy
 */
async function resumeStrategy(params, context) {
  const { strategy_id } = params;
  const config = context.config || {};

  const manager = getManager(config);

  try {
    const strategy = manager.resumeStrategy(strategy_id);
    return {
      success: true,
      data: strategy,
      message: `Strategy "${strategy.name}" resumed`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Action: Delete a DCA strategy
 */
async function deleteStrategy(params, context) {
  const { strategy_id } = params;
  const config = context.config || {};

  const manager = getManager(config);

  try {
    const result = manager.deleteStrategy(strategy_id);
    return {
      success: true,
      data: result,
      message: `Strategy deleted successfully`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Action: Get DCA execution history
 */
async function getHistory(params, context) {
  const { strategy_id, limit = 50 } = params;
  const config = context.config || {};

  const manager = getManager(config);
  const history = manager.getHistory(strategy_id, limit);

  return {
    success: true,
    data: history,
    count: history.length
  };
}

/**
 * Action: Calculate average cost basis
 */
async function calculateCostBasis(params, context) {
  const { strategy_id } = params;
  const config = context.config || {};

  const manager = getManager(config);
  const costBasis = manager.calculateCostBasis(strategy_id);

  return {
    success: true,
    data: costBasis
  };
}

/**
 * Action: Configure alert settings
 */
async function configureAlerts(params, context) {
  const { strategy_id, enabled, channels, on_success, on_failure } = params;
  const config = context.config || {};

  const manager = getManager(config);
  const alertConfig = manager.configureAlerts({
    strategy_id,
    enabled,
    channels,
    on_success,
    on_failure
  });

  return {
    success: true,
    data: alertConfig,
    message: `Alert configuration updated`
  };
}

/**
 * Trigger: Execute scheduled purchases
 */
async function executeScheduledPurchases(params, context) {
  const config = context.config || {};
  const manager = getManager(config);

  const results = await manager.executeScheduledPurchases();

  return {
    success: true,
    data: results,
    executed: results.filter(r => r.status === 'success').length,
    failed: results.filter(r => r.status === 'failed').length
  };
}

// Export action handlers
module.exports = {
  createStrategy,
  listStrategies,
  getStrategy,
  executePurchase,
  pauseStrategy,
  resumeStrategy,
  deleteStrategy,
  getHistory,
  calculateCostBasis,
  configureAlerts,
  executeScheduledPurchases
};
