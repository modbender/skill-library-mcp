export { readConfigFromEnv, rebalance_now, type RuntimeConfig, type RebalanceNowResult, type TargetEntryInput } from './src/rebalance-now.js';
export {
  verify_deployment_config,
  type VerifyDeploymentResult,
  type VerificationCheck,
  type VerificationStatus
} from './src/verify-deployment-config.js';

export interface HelpResult {
  summary: string;
  requiredEnv: string[];
  setupSteps: string[];
}

export function help(): HelpResult {
  return {
    summary: 'Simple Safe rebalancer with one-step execution and deployment verification.',
    requiredEnv: [
      'SAFE_ADDRESS',
      'EXECUTOR_MODULE_ADDRESS',
      'EXECUTOR_WALLET_PRIVATE_KEY',
      'TOT_API_KEY',
      'RPC_URL (optional, default https://mainnet.base.org)',
      'CHAIN_ID (optional, default 8453)',
      'MIN_TRADE_VALUE (optional, default 0.1)'
    ],
    setupSteps: [
      'Deploy module + policies using the 31Third policy wizard: https://app.31third.com/safe-policy-deployer',
      'Use two wallets: Safe owner wallet (never share key) and executor wallet (configured on ExecutorModule)',
      'Copy env vars from the wizard final step',
      'Request a 31Third API key via https://31third.com or dev@31third.com',
      'Run only one command for normal usage: npm run cli -- rebalance-now',
      'For post-deploy validation use: npm run cli -- verify-deployment --troubleshooting-file ./summary.txt',
      'If StaticAllocation policy is not deployed, pass targetEntries manually to rebalance_now.'
    ]
  };
}
