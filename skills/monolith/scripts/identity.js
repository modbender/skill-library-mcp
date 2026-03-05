import { daemon } from '../lib/daemon-client.js';
import { formatDaemonError } from '../lib/format.js';

/**
 * ERC-8004 identity operations.
 * Usage: node scripts/identity.js [query|register]
 *
 * NOTE: ERC-8004 registry addresses are not yet standardized.
 * This script provides wallet deployment status checking and documents
 * the intended registration flow for when registries are available.
 */
async function main() {
  const [, , action = 'query'] = process.argv;

  if (action === 'query') {
    try {
      const addr = await daemon.address();
      if (addr.status !== 200) {
        console.error(formatDaemonError(addr));
        process.exit(1);
      }

      const walletAddress = addr.data.walletAddress;
      const homeChainId = addr.data.homeChainId;

      console.log(`Wallet: ${walletAddress}`);
      console.log(`Home chain: ${homeChainId}`);

      if (walletAddress === 'not deployed') {
        console.log('Status: wallet not deployed — deploy first before identity registration');
        return;
      }

      // Check if wallet has code deployed on-chain
      const caps = await daemon.capabilities();
      if (caps.status === 200) {
        console.log(`Profile: ${caps.data.profile}`);
        console.log(`Frozen: ${caps.data.frozen}`);
        console.log('Status: wallet deployed — ready for identity registration when ERC-8004 registries are available');
      } else {
        console.log('Status: could not verify wallet deployment status');
      }

      console.log('\nERC-8004 identity registration is not yet implemented.');
      console.log('Registry contract addresses are pending standardization.');
      console.log('The wallet supports ERC-1271 signature verification for identity proofs.');
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  } else if (action === 'register') {
    console.log('ERC-8004 identity registration is not yet implemented.');
    console.log('');
    console.log('When available, registration will work as follows:');
    console.log('1. The agent builds a registration intent with:');
    console.log('   - target: ERC-8004 registry contract address');
    console.log('   - calldata: register(address wallet, bytes identity) encoded');
    console.log('   - value: "0" (no ETH needed)');
    console.log('2. The intent is sent to POST /sign');
    console.log('3. The daemon verifies the registration via policy');
    console.log('4. The wallet signs via ERC-1271 for on-chain verification');
    console.log('');
    console.log('The home chain for identity is chain ' +
      '(where the wallet is deployed) — not forced to L1.');
  } else {
    console.error('Usage: identity [query|register]');
    process.exit(1);
  }
}

main();
