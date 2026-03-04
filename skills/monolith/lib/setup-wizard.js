import { daemon } from './daemon-client.js';
import { attemptRuntimeBootstrap } from './runtime-bootstrap.js';

/**
 * Setup flow for Monolith (per spec §3.2).
 * The skill presents status; the actual interactive flow (chain selection,
 * profile selection, etc.) happens through the daemon's setup/config endpoints.
 */

/**
 * Check if the daemon is running and healthy.
 */
export async function checkDaemonHealth() {
  try {
    const response = await daemon.health();
    return {
      running: response.status === 200,
      version: response.data?.version,
    };
  } catch {
    return { running: false, version: null };
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForHealthyDaemon(maxAttempts = 10, delayMs = 400) {
  for (let i = 0; i < maxAttempts; i += 1) {
    const health = await checkDaemonHealth();
    if (health.running) {
      return health;
    }
    await sleep(delayMs);
  }
  return { running: false, version: null };
}

function buildBootstrapFailureMessage(bootstrap) {
  const parts = ['The Monolith daemon is not running.'];
  if (bootstrap?.messages?.length) {
    parts.push(bootstrap.messages.join(' '));
  } else {
    parts.push('Install MonolithDaemon.pkg, then run setup again.');
  }

  if (bootstrap?.manualCommands?.length) {
    parts.push(`Manual start commands: ${bootstrap.manualCommands.join(' ; ')}`);
  }

  return parts.join(' ');
}

/**
 * Get the wallet address and setup status.
 */
export async function getSetupStatus() {
  try {
    let health = await checkDaemonHealth();
    let bootstrap = null;

    if (!health.running) {
      bootstrap = attemptRuntimeBootstrap();
      health = await waitForHealthyDaemon();
    }

    if (!health.running) {
      return {
        step: 'daemon_not_running',
        message: buildBootstrapFailureMessage(bootstrap),
        bootstrap,
      };
    }

    const addr = await daemon.address();
    if (addr.status !== 200) {
      return {
        step: 'error',
        message: 'Could not get wallet address from daemon.',
      };
    }

    const caps = await daemon.capabilities();

    return {
      step: addr.data.walletAddress === 'not deployed' ? 'needs_deploy' : 'ready',
      walletAddress: addr.data.walletAddress,
      signerPublicKey: addr.data.signerPublicKey,
      homeChainId: addr.data.homeChainId,
      profile: caps.data?.profile,
      frozen: caps.data?.frozen,
      gasStatus: caps.data?.gasStatus,
      bootstrap,
    };
  } catch (err) {
    return {
      step: 'error',
      message: err.message,
    };
  }
}

/**
 * Run the setup wizard — gathers full status per spec §3.2.
 * Checks daemon health, wallet address, capabilities, and policy,
 * then returns structured data for each step so the agent can present it.
 *
 * @returns {Promise<object>} Structured setup status including:
 *   - daemon: { running, version }
 *   - wallet: { address, signerPublicKey, homeChainId, deployed }
 *   - capabilities: { profile, frozen, gasStatus, limits, remaining, allowedProtocols }
 *   - policy: current policy configuration (if available)
 *   - error: error message if something went wrong
 */
export async function runSetupWizard() {
  const result = {
    daemon: null,
    wallet: null,
    capabilities: null,
    policy: null,
    bootstrap: null,
    error: null,
  };

  // Step 1: Check daemon health
  try {
    let health = await checkDaemonHealth();
    if (!health.running) {
      result.bootstrap = attemptRuntimeBootstrap();
      health = await waitForHealthyDaemon();
    }

    result.daemon = health;
    if (!health.running) {
      result.error = buildBootstrapFailureMessage(result.bootstrap);
      return result;
    }
  } catch (err) {
    result.error = `Daemon health check failed: ${err.message}`;
    return result;
  }

  // Step 2: Get wallet address and key info
  try {
    const addr = await daemon.address();
    if (addr.status === 200) {
      result.wallet = {
        address: addr.data.walletAddress,
        signerPublicKey: addr.data.signerPublicKey,
        homeChainId: addr.data.homeChainId,
        deployed: addr.data.walletAddress !== 'not deployed',
      };
    } else {
      result.error = 'Could not get wallet address from daemon.';
      return result;
    }
  } catch (err) {
    result.error = `Failed to get wallet address: ${err.message}`;
    return result;
  }

  // Step 3: Get capabilities (profile, limits, budgets, gas)
  try {
    const caps = await daemon.capabilities();
    if (caps.status === 200) {
      result.capabilities = {
        profile: caps.data.profile,
        frozen: caps.data.frozen,
        gasStatus: caps.data.gasStatus,
        limits: caps.data.limits,
        remaining: caps.data.remaining,
        allowedProtocols: caps.data.allowedProtocols,
      };
    }
  } catch {
    // Non-fatal — capabilities may not be available before full setup
  }

  // Step 4: Get current policy configuration
  try {
    const pol = await daemon.policy();
    if (pol.status === 200) {
      result.policy = pol.data;
    }
  } catch {
    // Non-fatal — policy may not be configured yet
  }

  return result;
}

/**
 * Initialize the wallet with chain and profile configuration.
 * Calls POST /setup on the daemon.
 *
 * @param {object} params - { chainId: number, profile: string, recoveryAddress?: string }
 * @returns {Promise<object>} Setup result with walletAddress, precompileAvailable, etc.
 */
export async function initializeWallet(params) {
  const { chainId, profile, recoveryAddress, factoryAddress } = params;
  if (!chainId || !profile) {
    throw new Error('chainId and profile are required');
  }

  const body = { chainId, profile };
  if (recoveryAddress) {
    body.recoveryAddress = recoveryAddress;
  }
  if (factoryAddress) {
    body.factoryAddress = factoryAddress;
  }

  const response = await daemon.setup(body);
  if (response.status !== 200) {
    throw new Error(
      response.data?.error || `Setup failed with status ${response.status}`
    );
  }
  return response.data;
}

/**
 * Deploy the wallet on-chain.
 * Requires the wallet to be funded first.
 * Calls POST /setup/deploy on the daemon.
 *
 * @returns {Promise<object>} Deploy result with walletAddress, userOpHash, etc.
 */
export async function deployWallet() {
  const response = await daemon.setupDeploy();
  if (response.status !== 200) {
    throw new Error(
      response.data?.error || `Deploy failed with status ${response.status}`
    );
  }
  return response.data;
}
