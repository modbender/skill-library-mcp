// @ts-nocheck
/**
 * Tests for listNFT.ts - Marketplace listing operations
 */
import { jest } from '@jest/globals';
import { ethers } from 'ethers';
import { listNFT, checkListing } from '../src/skills/listNFT';
import { setupTestEnv, cleanupTestEnv, createMockContract } from './utils/mocks';

// Mock ethers
jest.mock('ethers', () => ({
  ethers: {
    JsonRpcProvider: jest.fn(),
    Wallet: jest.fn(),
    Contract: jest.fn(),
    parseEther: jest.fn((value: string) => BigInt(parseFloat(value) * 1e18)),
    formatEther: jest.fn((value: bigint) => (Number(value) / 1e18).toString())
  }
}));

describe('listNFT.ts', () => {
  let mockProvider: any;
  let mockWallet: any;
  let mockNftContract: any;
  let mockMarketplaceContract: any;

  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();

    mockProvider = {};
    mockWallet = {
      address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
    };

    mockNftContract = createMockContract();
    mockMarketplaceContract = createMockContract();

    (ethers.JsonRpcProvider as jest.Mock).mockReturnValue(mockProvider);
    (ethers.Wallet as jest.Mock).mockReturnValue(mockWallet);
    (ethers.Contract as jest.Mock).mockImplementation((address: string) => {
      if (address === process.env.NFT_CONTRACT_ADDRESS) {
        return mockNftContract;
      }
      return mockMarketplaceContract;
    });
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('listNFT', () => {
    it('should list NFT successfully when already approved', async () => {
      mockNftContract.isApprovedForAll.mockResolvedValue(true);

      const result = await listNFT('1', '0.005');

      expect(result.success).toBe(true);
      expect(result.price).toBe('0.005');
      expect(result.txHash).toBe('0xlist123');
    });

    it('should approve marketplace before listing if not approved', async () => {
      mockNftContract.isApprovedForAll.mockResolvedValue(false);

      const result = await listNFT('1', '0.005');

      expect(mockNftContract.setApprovalForAll).toHaveBeenCalledWith(
        process.env.MARKETPLACE_ADDRESS,
        true
      );
      expect(result.success).toBe(true);
    });

    it('should verify ownership before listing', async () => {
      await listNFT('1', '0.005');

      expect(mockNftContract.ownerOf).toHaveBeenCalledWith('1');
    });

    it('should fail if not the owner', async () => {
      mockNftContract.ownerOf.mockResolvedValue('0x0000000000000000000000000000000000000000');

      const result = await listNFT('1', '0.005');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Not the owner');
    });

    it('should convert price to wei', async () => {
      await listNFT('1', '0.005');

      expect(mockMarketplaceContract.listItem).toHaveBeenCalledWith(
        process.env.NFT_CONTRACT_ADDRESS,
        '1',
        BigInt(5000000000000000) // 0.005 ETH in wei
      );
    });

    it('should handle listing errors gracefully', async () => {
      mockMarketplaceContract.listItem.mockRejectedValue(new Error('Transaction failed'));

      const result = await listNFT('1', '0.005');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Transaction failed');
    });

    it('should wait for approval transaction to complete', async () => {
      mockNftContract.isApprovedForAll.mockResolvedValue(false);
      const mockApproveTx = {
        hash: '0xapproval123',
        wait: jest.fn().mockResolvedValue({ blockNumber: 12344 })
      };
      mockNftContract.setApprovalForAll.mockResolvedValue(mockApproveTx);

      await listNFT('1', '0.005');

      expect(mockApproveTx.wait).toHaveBeenCalled();
    });

    it('should wait for listing transaction to complete', async () => {
      const mockListTx = {
        hash: '0xlist123',
        wait: jest.fn().mockResolvedValue({ blockNumber: 12346 })
      };
      mockMarketplaceContract.listItem.mockResolvedValue(mockListTx);

      await listNFT('1', '0.005');

      expect(mockListTx.wait).toHaveBeenCalled();
    });
  });

  describe('checkListing', () => {
    it('should return listing details for active listing', async () => {
      mockMarketplaceContract.getListing.mockResolvedValue({
        seller: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        price: BigInt('5000000000000000'),
        active: true
      });

      const result = await checkListing('1');

      expect(result.listed).toBe(true);
      expect(result.price).toBe('0.005');
      expect(result.seller).toBe('0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266');
    });

    it('should return inactive for unlisted NFT', async () => {
      mockMarketplaceContract.getListing.mockResolvedValue({
        seller: '0x0000000000000000000000000000000000000000',
        price: BigInt('0'),
        active: false
      });

      const result = await checkListing('1');

      expect(result.listed).toBe(false);
      expect(result.price).toBe('0');
    });

    it('should handle errors gracefully', async () => {
      mockMarketplaceContract.getListing.mockRejectedValue(new Error('Contract error'));

      const result = await checkListing('1');

      expect(result.listed).toBe(false);
      expect(result.price).toBe('0');
      expect(result.seller).toBe('');
    });
  });
});
