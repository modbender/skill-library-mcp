/**
 * Risk Profiles
 * Hardcoded strategy parameters for different risk tolerances
 */

const RISK_PROFILES = {
  conservative: {
    name: 'Conservative',
    description: 'Safe, steady growth. Lower yields, minimal risk.',
    harvest_threshold_usd: 30,
    rebalance_apr_delta: 3.0,
    gas_multiplier_limit: 1.5,
    concentrate_capital: false,
    confidence_threshold: 0.85,
    icon: '🛡️',
    color: '#4CAF50'
  },
  balanced: {
    name: 'Balanced',
    description: 'Moderate risk, good yields. Recommended.',
    harvest_threshold_usd: 25,
    rebalance_apr_delta: 2.0,
    gas_multiplier_limit: 2.0,
    concentrate_capital: true,
    confidence_threshold: 0.70,
    icon: '⚖️',
    color: '#2196F3'
  },
  aggressive: {
    name: 'Aggressive',
    description: 'High-yield, higher risk. Max opportunities.',
    harvest_threshold_usd: 15,
    rebalance_apr_delta: 1.0,
    gas_multiplier_limit: 1.2,
    concentrate_capital: true,
    confidence_threshold: 0.60,
    icon: '🚀',
    color: '#FF9800'
  }
};

function getProfile(name) {
  if (!RISK_PROFILES[name]) {
    throw new Error(`Unknown risk profile: ${name}. Available: ${Object.keys(RISK_PROFILES).join(', ')}`);
  }
  return RISK_PROFILES[name];
}

function listProfiles() {
  return Object.entries(RISK_PROFILES).map(([id, profile]) => ({
    id,
    ...profile
  }));
}

module.exports = {
  RISK_PROFILES,
  getProfile,
  listProfiles
};
