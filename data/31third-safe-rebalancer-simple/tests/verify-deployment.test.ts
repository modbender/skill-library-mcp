import { describe, expect, it } from 'vitest';

import { verify_deployment_config } from '../index.js';

const troubleshootingSummary = `
Safe=0x8987f6e8Dc890E7Bb0EF41179e47F8aB5Ef46Bd1
ExecutorModule=0x2D133d3085a7db8B54b175ec595C7ED4e430e2D8 | Deployed
Scheduler=0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5
Registry=0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5
BatchTrade=0xD20c024560ccA40288C05BAB650ac087ae9b0f6e
FeedRegistry=0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A
CooldownSec=3600

AssetUniversePolicy=0xF1A8d4ad61a8147B4Ca61D1b9f5817Dc81697900 | Deployed
AssetUniverseAssets:
- USDC | 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
- WETH | 0x4200000000000000000000000000000000000006

StaticAllocationPolicy=0xd814BDCD7660df4fd76386665F4eA200d075aDEC | Deployed
StaticAllocationDriftThresholdPercent=0.50%
StaticAllocationToleranceThresholdPercent=0.50%
StaticAllocationTargets:
- USDC | 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 | AllocationPercent=10.00%
- WETH | 0x4200000000000000000000000000000000000006 | AllocationPercent=90.00%

SlippagePolicy=0xFB5AFfB6B5495Da3EF84a10b31ffa126E3E70BF1 | Deployed
MaxSlippagePercent=0.50%
`.trim();

describe('verify_deployment_config', () => {
  it('passes when summary and chain match', async () => {
    const result = await verify_deployment_config({
      troubleshootingSummary,
      deps: {
        fetchOnChainDeploymentFn: async () => ({
          safeAddress: '0x8987f6e8Dc890E7Bb0EF41179e47F8aB5Ef46Bd1',
          executorModuleAddress: '0x2D133d3085a7db8B54b175ec595C7ED4e430e2D8',
          scheduler: '0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5',
          registry: '0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5',
          batchTrade: '0xD20c024560ccA40288C05BAB650ac087ae9b0f6e',
          cooldownSec: 3600,
          assetUniversePolicy: '0xF1A8d4ad61a8147B4Ca61D1b9f5817Dc81697900',
          assetUniverseAssets: [
            '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
            '0x4200000000000000000000000000000000000006'
          ],
          staticAllocationPolicy: '0xd814BDCD7660df4fd76386665F4eA200d075aDEC',
          staticAllocationDriftThresholdPercent: 0.5,
          staticAllocationToleranceThresholdPercent: 0.5,
          staticAllocationTargets: [
            { tokenAddress: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913', allocationPercent: 10 },
            { tokenAddress: '0x4200000000000000000000000000000000000006', allocationPercent: 90 }
          ],
          staticFeedRegistry: '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A',
          slippagePolicy: '0xFB5AFfB6B5495Da3EF84a10b31ffa126E3E70BF1',
          maxSlippagePercent: 0.5,
          slippageFeedRegistry: '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A'
        })
      }
    });

    expect(result.ok).toBe(true);
    expect(result.mismatches).toEqual([]);
  });

  it('flags mismatch when summary and chain differ', async () => {
    const result = await verify_deployment_config({
      troubleshootingSummary,
      deps: {
        fetchOnChainDeploymentFn: async () => ({
          safeAddress: '0x8987f6e8Dc890E7Bb0EF41179e47F8aB5Ef46Bd1',
          executorModuleAddress: '0x2D133d3085a7db8B54b175ec595C7ED4e430e2D8',
          scheduler: '0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5',
          registry: '0xd488ebA2e5534af8DA6c0BC3915189024DFcAff5',
          batchTrade: '0xD20c024560ccA40288C05BAB650ac087ae9b0f6e',
          cooldownSec: 900,
          assetUniversePolicy: '0xF1A8d4ad61a8147B4Ca61D1b9f5817Dc81697900',
          assetUniverseAssets: [
            '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
            '0x4200000000000000000000000000000000000006'
          ],
          staticAllocationPolicy: '0xd814BDCD7660df4fd76386665F4eA200d075aDEC',
          staticAllocationDriftThresholdPercent: 0.5,
          staticAllocationToleranceThresholdPercent: 0.5,
          staticAllocationTargets: [
            { tokenAddress: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913', allocationPercent: 10 },
            { tokenAddress: '0x4200000000000000000000000000000000000006', allocationPercent: 90 }
          ],
          staticFeedRegistry: '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A',
          slippagePolicy: '0xFB5AFfB6B5495Da3EF84a10b31ffa126E3E70BF1',
          maxSlippagePercent: 0.5,
          slippageFeedRegistry: '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A'
        })
      }
    });

    expect(result.ok).toBe(false);
    expect(result.mismatches.some((mismatch) => mismatch.startsWith('CooldownSec:'))).toBe(true);
  });
});
