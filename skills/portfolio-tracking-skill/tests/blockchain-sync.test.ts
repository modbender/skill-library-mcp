import { describe, it, expect } from 'vitest';
import { CHAIN_CONFIGS, isValidEvmAddress } from '../scripts/blockchain-sync.js';
import type { ChainType } from '../scripts/blockchain-sync.js';

describe('CHAIN_CONFIGS', () => {
  it('should have 5 supported chains', () => {
    const chains = Object.keys(CHAIN_CONFIGS);
    expect(chains).toHaveLength(5);
    expect(chains).toContain('ETH');
    expect(chains).toContain('BSC');
    expect(chains).toContain('POLYGON');
    expect(chains).toContain('ARBITRUM');
    expect(chains).toContain('OPTIMISM');
  });

  it('should have valid RPC URLs', () => {
    for (const config of Object.values(CHAIN_CONFIGS)) {
      expect(config.rpcUrl).toMatch(/^https?:\/\//);
    }
  });

  it('should have native symbols for each chain', () => {
    expect(CHAIN_CONFIGS.ETH.nativeSymbol).toBe('ETH');
    expect(CHAIN_CONFIGS.BSC.nativeSymbol).toBe('BNB');
    expect(CHAIN_CONFIGS.POLYGON.nativeSymbol).toBe('MATIC');
    expect(CHAIN_CONFIGS.ARBITRUM.nativeSymbol).toBe('ETH');
    expect(CHAIN_CONFIGS.OPTIMISM.nativeSymbol).toBe('ETH');
  });
});

describe('isValidEvmAddress', () => {
  it('should validate correct EVM addresses', () => {
    expect(isValidEvmAddress('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045')).toBe(true);
    expect(isValidEvmAddress('0x0000000000000000000000000000000000000000')).toBe(true);
  });

  it('should reject invalid addresses', () => {
    expect(isValidEvmAddress('not-an-address')).toBe(false);
    expect(isValidEvmAddress('0x123')).toBe(false);
    expect(isValidEvmAddress('')).toBe(false);
  });

  it('should handle checksummed and non-checksummed addresses', () => {
    // All lowercase (non-checksummed)
    expect(isValidEvmAddress('0xd8da6bf26964af9d7eed9e03e53415d37aa96045')).toBe(true);
    // Mixed case (checksummed)
    expect(isValidEvmAddress('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045')).toBe(true);
  });
});

// Note: fetchWalletBalances and fetchAllChainBalances are not unit-tested here
// because they make real RPC calls to blockchain nodes. These should be tested
// in integration tests or with mocked ethers providers.
// The logic is straightforward and directly ported from the server version.
