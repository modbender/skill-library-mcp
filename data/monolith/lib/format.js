/**
 * Human-readable formatting utilities for agent responses.
 */

/**
 * Format wei amount as ETH string.
 */
export function formatETH(wei) {
  const eth = Number(BigInt(wei)) / 1e18;
  if (eth >= 0.01) return `${eth.toFixed(4)} ETH`;
  return `${eth.toFixed(8)} ETH`;
}

/**
 * Format USDC minor units as human-readable string.
 */
export function formatUSDC(amount, decimals = 6) {
  const value = Number(BigInt(amount)) / 10 ** decimals;
  return `${value.toFixed(2)} USDC`;
}

/**
 * Shorten an Ethereum address.
 */
export function shortenAddress(addr) {
  if (!addr || addr.length < 10) return addr;
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

/**
 * Format a daemon response for the agent.
 */
export function formatDaemonError(response) {
  if (response.data?.error) return `Error: ${response.data.error}`;
  return `Error: Daemon returned status ${response.status}`;
}

/**
 * Format capabilities for display.
 */
export function formatCapabilities(caps) {
  const lines = [
    `**Profile:** ${caps.profile}`,
    `**Chain:** ${caps.homeChainId === 1 ? 'Ethereum Mainnet' : 'Base'}`,
    `**Status:** ${caps.frozen ? 'FROZEN' : 'Active'}`,
    `**Gas:** ${caps.gasStatus === 'ok' ? 'Sufficient' : 'LOW'}`,
    '',
    '**Daily Remaining:**',
    `  ETH: ${formatETH(caps.remaining?.ethDaily || 0)}`,
    `  Stablecoin: ${formatUSDC(caps.remaining?.stablecoinDaily || 0)}`,
    '',
    '**Limits:**',
    `  Per-tx ETH: ${formatETH(caps.limits?.perTxEthCap || 0)}`,
    `  Per-tx Stablecoin: ${formatUSDC(caps.limits?.perTxStablecoinCap || 0)}`,
    `  Max tx/hour: ${caps.limits?.maxTxPerHour || 0}`,
    `  Max slippage: ${(caps.limits?.maxSlippageBps || 0) / 100}%`,
  ];
  return lines.join('\n');
}
