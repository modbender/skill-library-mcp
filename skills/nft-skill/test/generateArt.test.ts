// @ts-nocheck
/**
 * Tests for generateArt.ts - Art generation and IPFS upload
 */
import { jest } from '@jest/globals';
import * as fs from 'fs';
import axios from 'axios';
import { createAndUploadArt } from '../src/skills/generateArt';
import { setupTestEnv, cleanupTestEnv, createMockEvolutionState } from './utils/mocks';

// Mock dependencies
jest.mock('fs');
jest.mock('axios');

// Mock pureimage (project uses pureimage, not canvas)
const mockContext = {
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 1,
  globalAlpha: 1,
  fillRect: jest.fn(),
  beginPath: jest.fn(),
  arc: jest.fn(),
  fill: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  closePath: jest.fn(),
  stroke: jest.fn()
};

jest.mock('pureimage', () => ({
  make: jest.fn(() => ({
    getContext: jest.fn(() => mockContext)
  })),
  encodePNGToStream: jest.fn().mockResolvedValue(undefined)
}));

jest.mock('../src/skills/llm', () => ({
  generateArtConcept: jest.fn().mockResolvedValue('A vibrant cosmic nebula with swirling colors')
}));
jest.mock('../src/skills/evolve', () => ({
  getEvolutionState: jest.fn()
}));

const mockFs = fs as jest.Mocked<typeof fs>;
const mockAxios = axios as jest.Mocked<typeof axios>;

function createMockWriteStream() {
  return {
    write: jest.fn((_chunk: any, _encoding?: any, cb?: () => void) => {
      if (typeof _encoding === 'function') _encoding();
      else if (cb) cb();
      return true;
    }),
    end: jest.fn((cb?: () => void) => cb?.()),
    on: jest.fn()
  };
}

describe('generateArt.ts', () => {
  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();

    // Mock file system
    mockFs.existsSync.mockReturnValue(false);
    mockFs.mkdirSync.mockImplementation(() => undefined);
    mockFs.createWriteStream.mockImplementation(() => createMockWriteStream() as any);

    // Mock evolution state
    const { getEvolutionState } = require('../src/skills/evolve');
    getEvolutionState.mockReturnValue(createMockEvolutionState());

    // Mock IPFS uploads
    mockAxios.post.mockImplementation((url: string) => {
      if (url.includes('pinFileToIPFS')) {
        return Promise.resolve({
          data: { IpfsHash: 'QmTestImageHash123' }
        });
      }
      if (url.includes('pinJSONToIPFS')) {
        return Promise.resolve({
          data: { IpfsHash: 'QmTestMetadataHash456' }
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('createAndUploadArt', () => {
    it('should create and upload art successfully', async () => {
      const result = await createAndUploadArt(1, 'cosmic nebula');

      expect(result).toHaveProperty('imagePath');
      expect(result).toHaveProperty('metadata');
      expect(result).toHaveProperty('metadataUri');
    });

    it('should generate art concept using LLM', async () => {
      const { generateArtConcept } = require('../src/skills/llm');

      await createAndUploadArt(2, 'digital forest');

      expect(generateArtConcept).toHaveBeenCalledWith('digital forest', 2);
    });

    it('should create metadata with correct attributes', async () => {
      const result = await createAndUploadArt(3, 'neon cityscape');

      expect(result.metadata.name).toContain('AI Artist');
      expect(result.metadata.description).toBeTruthy();
      expect(result.metadata.image).toContain('ipfs://');
      expect(result.metadata.attributes).toContainEqual({
        trait_type: 'Generation',
        value: '3'
      });
      expect(result.metadata.attributes).toContainEqual({
        trait_type: 'Theme',
        value: 'neon cityscape'
      });
    });

    it('should upload image to IPFS', async () => {
      await createAndUploadArt(1, 'test theme');

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.pinata.cloud/pinning/pinFileToIPFS',
        expect.anything(),
        expect.objectContaining({
          headers: expect.objectContaining({
            pinata_api_key: 'test_pinata_key',
            pinata_secret_api_key: 'test_pinata_secret'
          })
        })
      );
    });

    it('should upload metadata to IPFS', async () => {
      await createAndUploadArt(1, 'test theme');

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.pinata.cloud/pinning/pinJSONToIPFS',
        expect.objectContaining({
          name: expect.any(String),
          description: expect.any(String),
          image: expect.any(String),
          attributes: expect.any(Array)
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            pinata_api_key: 'test_pinata_key',
            pinata_secret_api_key: 'test_pinata_secret'
          })
        })
      );
    });

    it('should return IPFS hash for metadata', async () => {
      const result = await createAndUploadArt(1, 'test theme');

      expect(result.metadataUri).toBe('QmTestMetadataHash456');
    });

    it('should create temp directory if it does not exist', async () => {
      mockFs.existsSync.mockReturnValue(false);

      await createAndUploadArt(1, 'test theme');

      expect(mockFs.mkdirSync).toHaveBeenCalled();
    });

    it('should save image to temp directory via createWriteStream', async () => {
      await createAndUploadArt(1, 'test theme');

      expect(mockFs.createWriteStream).toHaveBeenCalledWith(
        expect.stringContaining('art_')
      );
    });

    it('should handle IPFS upload failure gracefully', async () => {
      mockAxios.post.mockRejectedValue(new Error('IPFS error'));

      const result = await createAndUploadArt(1, 'test theme');

      // Should fallback to local file path
      expect(result.metadata.image).toContain('file://');
      expect(result.metadataUri).toBe('QmTestHash123456789');
    });

    it('should use evolution state for art parameters', async () => {
      const { getEvolutionState } = require('../src/skills/evolve');
      getEvolutionState.mockReturnValue(createMockEvolutionState({
        complexity_boost: 5,
        color_palette: 'cool',
        element_variety: 7
      }));

      const result = await createAndUploadArt(5, 'test theme');

      expect(result.metadata.attributes).toContainEqual({
        trait_type: 'Complexity',
        value: '5'
      });
      expect(result.metadata.attributes).toContainEqual({
        trait_type: 'Palette',
        value: 'cool'
      });
    });

    it('should generate unique filenames', async () => {
      await createAndUploadArt(1, 'theme1');
      await createAndUploadArt(1, 'theme2');

      const calls = mockFs.createWriteStream.mock.calls;
      const path1 = calls[0][0];
      const path2 = calls[1][0];

      expect(path1).not.toBe(path2);
    });
  });
});
