import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env file from the test-flow directory
dotenv.config({ path: join(__dirname, '..', '.env') });

export const config = {
  evm: {
    privateKey: process.env.EVM_PRIVATE_KEY,
    rpcUrl: process.env.EVM_RPC_URL || 'http://localhost:20657'
  },
  btc: {
    privateKey: process.env.BTC_PRIVATE_KEY,
    network: process.env.BTC_NETWORK || 'mainnet'
  },
  contracts: {
    loanContract: process.env.LOAN_CONTRACT_ADDRESS || '0x5cD194C9d34e5B9b7A0E5cBC64C93c1c9277891e',
    issuer: process.env.ISSUER_CONTRACT_ADDRESS || '0x91cf47c5d2b44Da124d4B54E9207aE6FB63D5Fa7',
    btcdToken: process.env.BTCD_TOKEN_ADDRESS || '0xF9BF836FEd97a9c9Bfe4D4c28316b9400C59Cc6B',
    arbitratorManager: process.env.ARBITRATOR_MANAGER_ADDRESS || '0x1f739Ce4238FF2B06D79D802Cb196aaE2025eae0',
    stakingFactory: process.env.STAKING_FACTORY_ADDRESS || '0xaB5f3Fc4F4Db4B912818C2bF2abd9c2Cbee04A36',
    fistToken: process.env.FIST_TOKEN_ADDRESS || '0x800E5c441b84a3E809E2ec922BeEE9f32f954B11'
  },
  api: {
    nowNodesBtc: process.env.NOWNODES_BTC_URL || 'https://nownodes-btc.bel2.org'
  },
  test: {
    orderId: process.env.ORDER_ID,
    lendingAmount: process.env.LENDING_AMOUNT || '10',
    lendingDays: parseInt(process.env.LENDING_DAYS || '90')
  }
};

const VALID_LENDING_DAYS = [90, 180];
const MIN_LENDING_AMOUNT = 10;

export function validateConfig() {
  const errors = [];
  const warnings = [];

  if (!config.evm.privateKey) {
    errors.push('EVM_PRIVATE_KEY is required');
  }

  if (!config.btc.privateKey) {
    errors.push('BTC_PRIVATE_KEY is required');
  }

  if (parseFloat(config.test.lendingAmount) < MIN_LENDING_AMOUNT) {
    warnings.push(`LENDING_AMOUNT=${config.test.lendingAmount} is below minimum (${MIN_LENDING_AMOUNT}). Forcing to ${MIN_LENDING_AMOUNT}.`);
    config.test.lendingAmount = String(MIN_LENDING_AMOUNT);
  }

  if (!VALID_LENDING_DAYS.includes(config.test.lendingDays)) {
    const nearest = VALID_LENDING_DAYS.reduce((a, b) =>
      Math.abs(b - config.test.lendingDays) < Math.abs(a - config.test.lendingDays) ? b : a
    );
    warnings.push(`LENDING_DAYS=${config.test.lendingDays} is invalid (allowed: ${VALID_LENDING_DAYS.join(', ')}). Forcing to ${nearest}.`);
    config.test.lendingDays = nearest;
  }

  if (warnings.length > 0) {
    console.warn('\n⚠️  Configuration warnings:');
    warnings.forEach(w => console.warn(`   ${w}`));
    console.warn('');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}
