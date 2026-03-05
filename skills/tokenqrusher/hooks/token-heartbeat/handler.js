/**
 * Token Heartbeat Hook
 *
 * SECURITY MANIFEST:
 *   Environment variables: none
 *   External endpoints: none (simulated checks only)
 *   Local files read: ~/.openclaw/hooks/token-heartbeat/config.json, ~/.openclaw/workspace/memory/heartbeat-state.json
 *   Local files written: none (state not persisted in current implementation)
 */

const { readFileSync, existsSync } = require('fs');
const { join, dirname } = require('path');
const { execSync } = require('child_process');

// Check types
const CHECK_TYPES = ['email', 'calendar', 'weather', 'monitoring'];

/**
 * Load configuration
 */
function loadConfig() {
  const configPath = join(dirname(__filename), 'config.json');
  
  if (existsSync(configPath)) {
    try {
      return JSON.parse(readFileSync(configPath, 'utf-8'));
    } catch (e) {
      console.error('[token-heartbeat] Config error:', e.message);
    }
  }
  
  return {
    enabled: true,
    intervals: {
      email: 7200,       // 2 hours
      calendar: 14400,   // 4 hours
      weather: 14400,   // 4 hours
      monitoring: 7200  // 2 hours
    },
    quietHours: {
      start: 23,
      end: 8
    },
    tokensPerCheck: 100,
    maxTokensPerHeartbeat: 5000
  };
}

/**
 * Get heartbeat optimizer state
 */
function getOptimizerState() {
  try {
    const statePath = join(
      process.env.HOME || '/home/q',
      '.openclaw/workspace/memory/heartbeat-state.json'
    );
    
    if (existsSync(statePath)) {
      return JSON.parse(readFileSync(statePath, 'utf-8'));
    }
  } catch (e) {
    // Ignore
  }
  return {};
}

/**
 * Check if we're in quiet hours
 */
function isQuietHours(config) {
  const now = new Date();
  const hour = now.getHours();
  
  const start = config.quietHours?.start || 23;
  const end = config.quietHours?.end || 8;
  
  if (start > end) {
    // Spans midnight
    return hour >= start || hour < end;
  } else {
    return hour >= start && hour < end;
  }
}

/**
 * Determine which checks should run
 */
function getChecksToRun(config, optimizerState) {
  const checks = [];
  const now = new Date();
  
  for (const checkType of CHECK_TYPES) {
    const interval = config.intervals?.[checkType] || 7200;
    const lastCheck = optimizerState[checkType]?.last_check;
    
    let shouldCheck = true;
    let reason = 'initial';
    
    if (lastCheck) {
      const lastTime = new Date(lastCheck);
      const elapsed = (now - lastTime) / 1000;  // seconds
      
      if (elapsed < interval) {
        shouldCheck = false;
        reason = `interval (${Math.round(interval - elapsed)}s remaining)`;
      }
    }
    
    checks.push({
      type: checkType,
      shouldRun: shouldCheck,
      reason
    });
  }
  
  return checks;
}

/**
 * Get emoji for check type
 */
function getCheckEmoji(checkType) {
  const emojis = {
    email: '📧',
    calendar: '📅',
    weather: '🌤️',
    monitoring: '📊'
  };
  return emojis[checkType] || '🔔';
}

/**
 * Simulate running checks (in production, these would actually run)
 */
function runChecks(checks, config) {
  const results = [];
  
  for (const check of checks) {
    if (!check.shouldRun) continue;
    
    // In production, this would actually check the service
    // For now, simulate no alerts (most common case)
    const hadAlerts = false;  // Would be true if alerts found
    
    results.push({
      type: check.type,
      hadAlerts,
      emoji: getCheckEmoji(check.type)
    });
    
    // Update state (would write to heartbeat-state.json)
    updateCheckState(check.type, hadAlerts);
  }
  
  return results;
}

/**
 * Update check state in memory (for next check)
 */
function updateCheckState(checkType, hadAlerts) {
  // In production, would persist to disk
  // This is a simplified in-memory version
}

/**
 * Format heartbeat response
 */
function formatResponse(results, config) {
  // Filter to only checks with alerts
  const alerts = results.filter(r => r.hadAlerts);
  
  if (alerts.length === 0) {
    return 'HEARTBEAT_OK';
  }
  
  // Format alerts
  const lines = alerts.map(a => {
    return `${a.emoji} ${a.type.charAt(0).toUpperCase() + a.type.slice(1)}: Alert detected`;
  });
  
  return lines.join('\n');
}

/**
 * Estimate token usage
 */
function estimateTokens(results, config) {
  const checksRun = results.length;
  return checksRun * (config.tokensPerCheck || 100);
}

/**
 * Main handler
 */
async function handler(event) {
  // Check if this is a heartbeat poll
  // Heartbeat polls have specific characteristics
  const message = event.context?.sessionEntry?.lastMessage || '';
  const isHeartbeat = message.toLowerCase().includes('heartbeat');
  
  // For now, we always process (hook runs on agent:bootstrap)
  // In production, could check for heartbeat-specific triggers
  
  const config = loadConfig();
  
  if (config.enabled === false) {
    return;
  }

  // Check quiet hours
  if (isQuietHours(config)) {
    console.log('[token-heartbeat] ⏸️ Quiet hours active (23:00-08:00)');
    console.log('[token-heartbeat] HEARTBEAT_OK');
    return;
  }

  // Get optimizer state
  const optimizerState = getOptimizerState();
  
  // Determine which checks should run
  const checks = getChecksToRun(config, optimizerState);
  const checksToRun = checks.filter(c => c.shouldRun);
  
  // Log what we're checking
  if (config.logLevel === 'debug') {
    console.log('[token-heartbeat] === Heartbeat Check Debug ===');
    for (const check of checks) {
      console.log(`[token-heartbeat] ${check.type}: ${check.shouldRun ? '✓' : '✗'} (${check.reason})`);
    }
  }
  
  // Run checks that are due
  const results = runChecks(checksToRun, config);
  
  // Estimate tokens
  const tokens = estimateTokens(results, config);
  
  // Format response
  const response = formatResponse(results, config);
  
  // Log result
  if (response === 'HEARTBEAT_OK') {
    console.log('[token-heartbeat] ✅ HEARTBEAT_OK');
    console.log(`[token-heartbeat]    Tokens: ~${tokens} (${checksToRun.length} checks)`);
  } else {
    console.log(`[token-heartbeat] ${response}`);
  }
  
  // Update session context if needed
  if (event.context?.sessionEntry) {
    // Could add metadata about checks run
  }
}

/**
 * Export for OpenClaw
 */
module.exports = handler;
module.exports.default = handler;
