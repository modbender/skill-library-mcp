// @ts-nocheck
/**
 * Tests for mintNFT.ts - NFT minting and wallet operations
 */
import { jest } from '@jest/globals';
import { ethers } from 'ethers';
import { mintNFT, getWalletBalance, getWalletAddress, getTokenCount } from '../src/skills/mintNFT';
import { setupTestEnv, cleanupTestEnv, createMockContract } from './utils/mocks';

// Mock ethers
jest.mock('ethers', () => ({
  ethers: {
    JsonRpcProvider: jest.fn(),
    Wallet: jest.fn(),
    Contract: jest.fn(),
    formatEther: jest.fn((value: bigint) => (Number(value) / 1e18).toString()),
    toBigInt: jest.fn((value: any) => BigInt(value)),
    id: jest.fn(() => '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')
  }
}));

describe('mintNFT.ts', () => {
  let mockProvider: any;
  let mockWallet: any;
  let mockContract: any;

  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();

    mockProvider = {
      getBalance: jest.fn().mockResolvedValue(BigInt('1000000000000000000'))
    };

    mockWallet = {
      address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
    };

    mockContract = createMockContract();

    (ethers.JsonRpcProvider as jest.Mock).mockReturnValue(mockProvider);
    (ethers.Wallet as jest.Mock).mockReturnValue(mockWallet);
    (ethers.Contract as jest.Mock).mockReturnValue(mockContract);
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('mintNFT', () => {
    it('should mint NFT successfully', async () => {
      const result = await mintNFT('QmTestHash123');

      expect(mockContract.safeMint).toHaveBeenCalledWith(
        mockWallet.address,
        'ipfs://QmTestHash123',
        expect.objectContaining({
          gasLimit: expect.any(BigInt)
        })
      );

      expect(result.tokenId).toBe('1');
      expect(result.txHash).toBe('0xabcdef1234567890');
      expect(result.blockNumber).toBe(12345);
    });

    it('should estimate gas before minting', async () => {
      await mintNFT('QmTestHash456');

      expect(mockContract.safeMint.estimateGas).toHaveBeenCalledWith(
        mockWallet.address,
        'ipfs://QmTestHash456'
      );
    });

    it('should add 20% gas buffer', async () => {
      const gasEstimate = BigInt('100000');
      mockContract.safeMint.estimateGas = jest.fn().mockResolvedValue(gasEstimate);

      await mintNFT('QmTestHash789');

      const expectedGasLimit = (gasEstimate * 120n) / 100n;
      expect(mockContract.safeMint).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(String),
        expect.objectContaining({
          gasLimit: expectedGasLimit
        })
      );
    });

    it('should parse tokenId from Transfer event', async () => {
      const result = await mintNFT('QmTestHash');

      expect(result.tokenId).toBe('1');
    });

    it('should handle missing Transfer event', async () => {
      mockContract.safeMint.mockReturnValue({
        hash: '0xtest',
        wait: jest.fn().mockResolvedValue({
          blockNumber: 12345,
          gasUsed: BigInt('100000'),
          logs: [] // No logs
        })
      });

      const result = await mintNFT('QmTestHash');

      expect(result.tokenId).toBe('unknown');
    });
  });

  describe('getWalletBalance', () => {
    it('should return wallet balance in ETH', async () => {
      const balance = await getWalletBalance();

      expect(mockProvider.getBalance).toHaveBeenCalledWith(mockWallet.address);
      expect(balance).toBe('1'); // 1 ETH
    });

    it('should handle zero balance', async () => {
      mockProvider.getBalance.mockResolvedValue(BigInt('0'));

      const balance = await getWalletBalance();

      expect(balance).toBe('0');
    });
  });

  describe('getWalletAddress', () => {
    it('should return wallet address', async () => {
      const address = await getWalletAddress();

      expect(address).toBe('0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266');
    });
  });

  describe('getTokenCount', () => {
    it('should return token counter', async () => {
      const count = await getTokenCount();

      expect(mockContract.tokenCounter).toHaveBeenCalled();
      expect(count).toBe(5);
    });

    it('should handle zero tokens', async () => {
      mockContract.tokenCounter.mockResolvedValue(BigInt('0'));

      const count = await getTokenCount();

      expect(count).toBe(0);
    });
  });
});
