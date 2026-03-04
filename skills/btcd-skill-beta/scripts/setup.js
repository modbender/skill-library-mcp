#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets, getEVMWallet } from './utils/wallet-manager.js';
import { saveState } from './utils/state-manager.js';

async function main() {
  logger.section('BTCD Collateralization Test - Setup');

  try {
    // Validate configuration
    logger.info('Validating configuration...');
    validateConfig();
    logger.success('Configuration validated');

    // Initialize wallets
    const { evmWallet, btcAddress } = initializeWallets();

    // Check balances
    logger.info('Checking balances...');
    const evmBalance = await evmWallet.getBalance();
    logger.data('EVM Balance', `${evmBalance.toString()} wei`);

    // Initialize state file
    const initialState = {
      createdAt: new Date().toISOString(),
      config: {
        evmAddress: evmWallet.address,
        btcAddress: btcAddress,
        network: config.btc.network,
        loanContractAddress: config.contracts.loanContract,
        issuerContractAddress: config.contracts.issuer,
        btcdTokenAddress: config.contracts.btcdToken
      },
      steps: {}
    };

    saveState(initialState);

    logger.success('Setup completed successfully!');
    logger.info('\nNext steps:');
    logger.info('1. Fund your wallets if needed');
    logger.info('2. Run: npm run 00-create-order (to create a new order)');
    logger.info('   OR set ORDER_ID in .env and run: npm run 01-take-order (to take existing order)');
  } catch (error) {
    logger.error('Setup failed:', error.message);
    process.exit(1);
  }
}

main();
