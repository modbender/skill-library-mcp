// @ts-nocheck
/**
 * Tests for monitorSales.ts - Sales event monitoring
 */
import { jest } from '@jest/globals';
import { ethers } from 'ethers';
import { startSalesMonitor, checkRecentSales } from '../src/skills/monitorSales';
import { setupTestEnv, cleanupTestEnv } from './utils/mocks';

// Mock ethers
jest.mock('ethers', () => ({
  ethers: {
    JsonRpcProvider: jest.fn(),
    Contract: jest.fn(),
    formatEther: jest.fn((value: bigint) => (Number(value) / 1e18).toString())
  }
}));

describe('monitorSales.ts', () => {
  let mockProvider: any;
  let mockContract: any;

  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();

    mockProvider = {
      getBlockNumber: jest.fn().mockResolvedValue(12350)
    };

    mockContract = {
      filters: {
        ItemSold: jest.fn().mockReturnValue('mock-filter')
      },
      on: jest.fn(),
      off: jest.fn(),
      queryFilter: jest.fn().mockResolvedValue([])
    };

    (ethers.JsonRpcProvider as jest.Mock).mockReturnValue(mockProvider);
    (ethers.Contract as jest.Mock).mockReturnValue(mockContract);
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('startSalesMonitor', () => {
    it('should set up event listener', () => {
      const callback = jest.fn();

      startSalesMonitor(callback);

      expect(mockContract.on).toHaveBeenCalledWith('mock-filter', expect.any(Function));
    });

    it('should filter for NFT contract address', () => {
      const callback = jest.fn();

      startSalesMonitor(callback);

      expect(mockContract.filters.ItemSold).toHaveBeenCalledWith(
        null, // any buyer
        process.env.NFT_CONTRACT_ADDRESS
      );
    });

    it('should call callback when sale event occurs', async () => {
      const callback = jest.fn();
      let eventListener: any;

      mockContract.on.mockImplementation((filter: any, listener: any) => {
        eventListener = listener;
      });

      startSalesMonitor(callback);

      // Simulate sale event
      await eventListener(
        '0xbuyer123',
        process.env.NFT_CONTRACT_ADDRESS,
        BigInt('5'),
        BigInt('7000000000000000'), // 0.007 ETH
        {
          transactionHash: '0xsaletx',
          blockNumber: 12345
        }
      );

      expect(callback).toHaveBeenCalledWith({
        buyer: '0xbuyer123',
        tokenId: '5',
        price: '0.007',
        txHash: '0xsaletx',
        blockNumber: 12345
      });
    });

    it('should handle callback errors gracefully', async () => {
      const callback = jest.fn().mockRejectedValue(new Error('Callback error'));
      let eventListener: any;

      mockContract.on.mockImplementation((filter: any, listener: any) => {
        eventListener = listener;
      });

      startSalesMonitor(callback);

      // Should not throw
      await expect(eventListener(
        '0xbuyer',
        process.env.NFT_CONTRACT_ADDRESS,
        BigInt('1'),
        BigInt('5000000000000000'),
        { transactionHash: '0xtx', blockNumber: 12345 }
      )).resolves.not.toThrow();
    });

    it('should return cleanup function', () => {
      const callback = jest.fn();

      const cleanup = startSalesMonitor(callback);

      expect(typeof cleanup).toBe('function');
    });

    it('should remove listener when cleanup is called', () => {
      const callback = jest.fn();

      const cleanup = startSalesMonitor(callback);
      cleanup();

      expect(mockContract.off).toHaveBeenCalledWith('mock-filter', expect.any(Function));
    });
  });

  describe('checkRecentSales', () => {
    it('should query events from specified block', async () => {
      const callback = jest.fn();

      await checkRecentSales(12300, callback);

      expect(mockContract.queryFilter).toHaveBeenCalledWith(
        'mock-filter',
        12300,
        12350 // current block
      );
    });

    it('should return current block number', async () => {
      const callback = jest.fn();

      const currentBlock = await checkRecentSales(12300, callback);

      expect(currentBlock).toBe(12350);
    });

    it('should process all found events', async () => {
      const callback = jest.fn();
      const mockEvents = [
        {
          args: [
            '0xbuyer1',
            process.env.NFT_CONTRACT_ADDRESS,
            BigInt('1'),
            BigInt('5000000000000000')
          ],
          transactionHash: '0xtx1',
          blockNumber: 12301
        },
        {
          args: [
            '0xbuyer2',
            process.env.NFT_CONTRACT_ADDRESS,
            BigInt('2'),
            BigInt('6000000000000000')
          ],
          transactionHash: '0xtx2',
          blockNumber: 12302
        }
      ];

      mockContract.queryFilter.mockResolvedValue(mockEvents);

      await checkRecentSales(12300, callback);

      expect(callback).toHaveBeenCalledTimes(2);
      expect(callback).toHaveBeenNthCalledWith(1, {
        buyer: '0xbuyer1',
        tokenId: '1',
        price: '0.005',
        txHash: '0xtx1',
        blockNumber: 12301
      });
      expect(callback).toHaveBeenNthCalledWith(2, {
        buyer: '0xbuyer2',
        tokenId: '2',
        price: '0.006',
        txHash: '0xtx2',
        blockNumber: 12302
      });
    });

    it('should handle no events found', async () => {
      const callback = jest.fn();
      mockContract.queryFilter.mockResolvedValue([]);

      await checkRecentSales(12300, callback);

      expect(callback).not.toHaveBeenCalled();
    });

    it('should handle from block 0 on first run', async () => {
      const callback = jest.fn();

      await checkRecentSales(0, callback);

      expect(mockContract.queryFilter).toHaveBeenCalledWith(
        'mock-filter',
        0,
        12350
      );
    });
  });
});
