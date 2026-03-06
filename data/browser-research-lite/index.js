const { execSync } = require('child_process');
const path = require('path');

/**
 * Browser Research Lite - Main Entry Point
 * 
 * Provides a programmatic interface to browser-based research with fallbacks.
 */

const SCRIPTS_DIR = path.join(__dirname, 'scripts');

/**
 * Check if the browser is available using the guard script.
 * @returns {boolean} True if browser is available.
 */
function checkBrowserAvailability() {
  try {
    const scriptPath = path.join(SCRIPTS_DIR, 'browser_guard.py');
    const output = execSync(`python3 "${scriptPath}"`, { encoding: 'utf8', stdio: 'pipe' });
    
    // Parse the JSON output
    try {
      const data = JSON.parse(output.trim());
      // Check for browser_available flag
      return data.browser_available === true;
    } catch (parseError) {
      console.warn(`[browser-research-lite] Failed to parse guard output: ${output}`);
      return false;
    }
  } catch (e) {
    console.error(`[browser-research-lite] Guard script execution failed: ${e.message}`);
    return false;
  }
}

/**
 * Main function to execute a browser-based research task.
 * @param {string} query - The research query.
 */
exports.research = function(query) {
  console.log(`[browser-research-lite] Researching: "${query}"`);

  // 1. Check Availability
  const isAvailable = checkBrowserAvailability();
  if (!isAvailable) {
    console.warn('[browser-research-lite] Browser unavailable. Falling back to web_search suggestion.');
    return {
      status: 'skipped',
      reason: 'Browser control service unreachable or extension not connected.',
      suggestion: 'Use web_search tool instead.'
    };
  }

  // 2. Since this is a "lite" skill, we don't implement full automation here yet.
  // We return instructions or status.
  return {
    status: 'ready',
    message: 'Browser is available. Proceed with browser tool calls manually or via agent instructions.'
  };
};

/**
 * Main entry point for testing or CLI usage.
 */
exports.main = function() {
  const available = checkBrowserAvailability();
  console.log(`Browser Available: ${available}`);
  if (!available) {
    console.log("Suggestion: Ensure OpenClaw gateway is running and browser extension is connected.");
  }
};

// If run directly
if (require.main === module) {
  exports.main();
}
