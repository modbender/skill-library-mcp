/**
 * SolArb - Funding Rate Arbitrage Agent for Solana
 * 
 * Entry point for the funding arbitrage bot.
 */

import { Keypair } from '@solana/web3.js';
import * as fs from 'fs';
import * as path from 'path';
import { FundingArbitrageEngine, FundingArbConfig } from './core/funding-arbitrage';
import { logger } from './utils/logger';

// Load configuration
function loadConfig(): FundingArbConfig {
  const configPath = process.env.CONFIG_PATH || path.join(__dirname, '../config/default.json');
  
  if (!fs.existsSync(configPath)) {
    logger.error(`Config file not found: ${configPath}`);
    logger.info('Copy config/default.example.json to config/default.json and configure');
    process.exit(1);
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  
  // Load wallet
  let wallet: Keypair;
  if (config.walletPath) {
    const walletData = JSON.parse(fs.readFileSync(config.walletPath, 'utf-8'));
    wallet = Keypair.fromSecretKey(Uint8Array.from(walletData));
  } else if (process.env.WALLET_PRIVATE_KEY) {
    wallet = Keypair.fromSecretKey(
      Uint8Array.from(JSON.parse(process.env.WALLET_PRIVATE_KEY))
    );
  } else {
    logger.error('No wallet configured. Set walletPath in config or WALLET_PRIVATE_KEY env var');
    process.exit(1);
  }

  return {
    rpcUrl: config.rpc || process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com',
    wallet,
    minFundingApy: config.minFundingApy || 20,
    maxPositionUsd: config.maxPositionUsd || 1000,
    markets: config.markets || ['SOL-PERP', 'BTC-PERP', 'ETH-PERP'],
    checkIntervalMs: config.checkIntervalMs || 60000,
    exitApyThreshold: config.exitApyThreshold || 5
  };
}

async function main() {
  const args = process.argv.slice(2);
  
  // Check for scan mode
  if (args.includes('--scan') || args.includes('-s')) {
    const { FundingArbitrageEngine } = await import('./core/funding-arbitrage');
    const config = loadConfig();
    const engine = new FundingArbitrageEngine(config);
    await engine.scanOpportunities();
    return;
  }

  // Full bot mode
  const config = loadConfig();
  
  logger.info(`Wallet: ${config.wallet.publicKey.toBase58().slice(0, 8)}...`);
  logger.info(`RPC: ${config.rpcUrl.slice(0, 30)}...`);
  logger.info(`Markets: ${config.markets.join(', ')}`);
  logger.info(`Min APY: ${config.minFundingApy}%`);
  logger.info(`Max Position: $${config.maxPositionUsd}`);
  
  const engine = new FundingArbitrageEngine(config);
  
  // Handle shutdown
  process.on('SIGINT', () => {
    logger.info('Shutting down...');
    engine.stop();
    process.exit(0);
  });

  // Start the engine
  await engine.start();
}

main().catch(error => {
  logger.error('Fatal error:', error);
  process.exit(1);
});
