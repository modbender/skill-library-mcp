// @ts-nocheck
/**
 * Shared test utilities and mocks
 */
import { jest } from '@jest/globals';

// Mock environment variables for testing
export const mockEnv = {
  BASE_RPC_URL: 'http://localhost:8545',
  BASE_PRIVATE_KEY: '0x1234567890123456789012345678901234567890123456789012345678901234',
  NFT_CONTRACT_ADDRESS: '0x1111111111111111111111111111111111111111',
  MARKETPLACE_ADDRESS: '0x2222222222222222222222222222222222222222',
  PINATA_API_KEY: 'test_pinata_key',
  PINATA_SECRET: 'test_pinata_secret',
  LLM_PROVIDER: 'openrouter',
  LLM_MODEL: 'meta-llama/llama-3.2-3b-instruct:free',
  OPENROUTER_API_KEY: 'test_openrouter_key',
  X_CONSUMER_KEY: 'test_consumer_key',
  X_CONSUMER_SECRET: 'test_consumer_secret',
  X_ACCESS_TOKEN: 'test_access_token',
  X_ACCESS_SECRET: 'test_access_secret'
};

// Setup environment variables before each test
export function setupTestEnv() {
  Object.entries(mockEnv).forEach(([key, value]) => {
    process.env[key] = value;
  });
}

// Clean up environment after each test
export function cleanupTestEnv() {
  Object.keys(mockEnv).forEach(key => {
    delete process.env[key];
  });
}

// Mock ethers provider
export const mockProvider = {
  getBalance: jest.fn().mockResolvedValue(BigInt('1000000000000000000')) as any, // 1 ETH
  getBlockNumber: jest.fn().mockResolvedValue(12345) as any,
  estimateGas: jest.fn().mockResolvedValue(BigInt('100000')) as any
};

// Mock ethers wallet
export const mockWallet = {
  address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
  signTransaction: jest.fn() as any,
  sendTransaction: jest.fn() as any
};

// Mock ethers contract
export function createMockContract(overrides = {}) {
  const safeMintFn = jest.fn().mockImplementation(() => ({
      hash: '0xabcdef1234567890',
      wait: jest.fn().mockResolvedValue({
        blockNumber: 12345,
        gasUsed: BigInt('100000'),
        logs: [{
          topics: [
            '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', // Transfer event
            '0x0000000000000000000000000000000000000000000000000000000000000000',
            '0x000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266',
            '0x0000000000000000000000000000000000000000000000000000000000000001' // tokenId = 1
          ]
        }]
      })
    } as any)) as any;
  (safeMintFn as any).estimateGas = jest.fn().mockResolvedValue(BigInt('100000'));
  return {
    safeMint: safeMintFn,
    tokenCounter: jest.fn().mockResolvedValue(BigInt('5')) as any,
    ownerOf: jest.fn().mockResolvedValue('0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266') as any,
    isApprovedForAll: jest.fn().mockResolvedValue(true) as any,
    setApprovalForAll: jest.fn().mockImplementation(() => ({
      hash: '0xapproval123',
      wait: jest.fn().mockResolvedValue({ blockNumber: 12344 })
    } as any)) as any,
    listItem: jest.fn().mockImplementation(() => ({
      hash: '0xlist123',
      wait: jest.fn().mockResolvedValue({ blockNumber: 12346 })
    } as any)) as any,
    getListing: jest.fn().mockResolvedValue({
      seller: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
      price: BigInt('5000000000000000'), // 0.005 ETH
      active: true
    }) as any,
    on: jest.fn() as any,
    off: jest.fn() as any,
    filters: {
      ItemSold: jest.fn().mockReturnValue({}) as any
    },
    queryFilter: jest.fn().mockResolvedValue([]) as any,
    ...overrides
  };
}

// Mock axios for API calls
export const mockAxios = {
  post: jest.fn() as any,
  get: jest.fn() as any
};

// Mock Twitter API client
export const mockTwitterClient = {
  v2: {
    tweet: jest.fn().mockResolvedValue({
      data: { id: '1234567890' }
    }) as any
  }
};

// Mock file system operations
export const mockFs = {
  existsSync: jest.fn().mockReturnValue(false) as any,
  readFileSync: jest.fn().mockReturnValue('{}') as any,
  writeFileSync: jest.fn() as any,
  mkdirSync: jest.fn() as any,
  createReadStream: jest.fn() as any
};

// Mock canvas
export const mockCanvas = {
  toBuffer: jest.fn().mockReturnValue(Buffer.from('fake-image-data')) as any,
  getContext: jest.fn().mockReturnValue({
    fillStyle: '',
    fillRect: jest.fn(),
    beginPath: jest.fn(),
    arc: jest.fn(),
    fill: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    closePath: jest.fn(),
    save: jest.fn(),
    restore: jest.fn(),
    globalAlpha: 1
  }) as any
};

export function createMockCanvas() {
  return mockCanvas;
}

// Helper to create mock evolution state
export function createMockEvolutionState(overrides = {}) {
  return {
    generation: 1,
    complexity_boost: 1,
    color_palette: 'vibrant' as const,
    element_variety: 3,
    themes_unlocked: ['cosmic nebula', 'digital forest', 'abstract emotion', 'geometric dreams'],
    total_proceeds: '0',
    total_minted: 0,
    total_sold: 0,
    last_evolved: new Date().toISOString(),
    evolution_history: [],
    ...overrides
  };
}

// Helper to wait for async operations
export function waitFor(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
