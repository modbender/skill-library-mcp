import { runSetupWizard, initializeWallet, deployWallet } from '../lib/setup-wizard.js';

/**
 * Run the Monolith setup wizard and print status.
 * Usage: node scripts/setup.js
 */
async function main() {
  try {
    const status = await runSetupWizard();

    if (status.bootstrap) {
      console.log('Setup helper: no local services were started automatically.');
      for (const message of status.bootstrap.messages || []) {
        console.log(`  ${message}`);
      }
      if (status.bootstrap.manualCommands?.length) {
        console.log('Manual start commands:');
        for (const command of status.bootstrap.manualCommands) {
          console.log(`  ${command}`);
        }
      }
    }

    if (status.error) {
      console.error(`Setup error: ${status.error}`);
      process.exit(1);
    }

    // Daemon info
    console.log(`Daemon: running (v${status.daemon.version})`);

    // Wallet info
    if (status.wallet) {
      console.log(`Wallet address: ${status.wallet.address}`);
      console.log(`Signer public key: ${status.wallet.signerPublicKey}`);
      console.log(`Home chain: ${status.wallet.homeChainId}`);
      console.log(`Deployed: ${status.wallet.deployed ? 'Yes' : 'No'}`);
    }

    // Capabilities
    if (status.capabilities) {
      console.log(`Profile: ${status.capabilities.profile}`);
      console.log(`Frozen: ${status.capabilities.frozen}`);
      console.log(`Gas status: ${status.capabilities.gasStatus}`);

      if (status.capabilities.limits) {
        const l = status.capabilities.limits;
        console.log('Limits:');
        if (l.perTxEthCap) console.log(`  Per-tx ETH cap: ${l.perTxEthCap}`);
        if (l.perTxStablecoinCap) console.log(`  Per-tx stablecoin cap: ${l.perTxStablecoinCap}`);
        if (l.maxTxPerHour) console.log(`  Max tx/hour: ${l.maxTxPerHour}`);
        if (l.maxSlippageBps) console.log(`  Max slippage: ${l.maxSlippageBps / 100}%`);
      }

      if (status.capabilities.remaining) {
        const r = status.capabilities.remaining;
        console.log('Daily remaining:');
        if (r.ethDaily) console.log(`  ETH: ${r.ethDaily}`);
        if (r.stablecoinDaily) console.log(`  Stablecoin: ${r.stablecoinDaily}`);
      }

      if (status.capabilities.allowedProtocols) {
        console.log(`Allowed protocols: ${status.capabilities.allowedProtocols.join(', ')}`);
      }
    }

    // Policy
    if (status.policy) {
      console.log('Policy: configured');
    } else {
      console.log('Policy: not yet configured');
    }

    // Parse CLI args: node scripts/setup.js <action> [chainId] [profile] [recoveryAddress]
    const [, , action, chainId, profile, recoveryAddress] = process.argv;

    if (action === 'init' && chainId && profile) {
      console.log(`\nInitializing wallet on chain ${chainId} with profile "${profile}"...`);
      const initParams = { chainId: Number(chainId), profile };
      if (recoveryAddress) {
        initParams.recoveryAddress = recoveryAddress;
        console.log(`Recovery address: ${recoveryAddress}`);
      }
      const initResult = await initializeWallet(initParams);
      console.log(`Counterfactual address: ${initResult.walletAddress}`);
      console.log(`Precompile available: ${initResult.precompileAvailable}`);
      console.log('Send ETH to this address, then run: node scripts/setup.js deploy');
    } else if (action === 'deploy') {
      console.log('\nDeploying wallet on-chain...');
      const deployResult = await deployWallet();
      console.log(`Wallet deployed: ${deployResult.walletAddress}`);
      console.log(`UserOp hash: ${deployResult.userOpHash}`);
    } else if (status.wallet && !status.wallet.deployed) {
      console.log('\nWallet not yet deployed.');
      console.log('To initialize: node scripts/setup.js init <chainId> <profile> [recoveryAddress]');
      console.log('  chainId: 1 (Ethereum) or 8453 (Base)');
      console.log('  profile: "balanced" or "autonomous"');
      console.log('  recoveryAddress: (optional) EOA for emergency recovery');
    }
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}

main();
