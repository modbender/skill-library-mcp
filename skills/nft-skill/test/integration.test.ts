// @ts-nocheck
/**
 * Integration tests - verifies skill modules work together
 */
import { jest } from '@jest/globals';
import { createAndUploadArt } from '../src/skills/generateArt';
import {
  evolveAgent,
  getEvolutionState,
  calculateListPrice,
  shouldEvolve,
  selectTheme,
  updateStats
} from '../src/skills/evolve';
import { setupTestEnv, cleanupTestEnv, createMockEvolutionState } from './utils/mocks';

// Mock external dependencies
jest.mock('fs');
jest.mock('axios');

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
  generateArtConcept: jest.fn().mockResolvedValue('Integration test art concept')
}));

const fs = require('fs');

describe('Integration: Skill Modules', () => {
  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();
    fs.existsSync.mockReturnValue(false);
    fs.mkdirSync.mockImplementation(() => undefined);
    fs.createWriteStream.mockImplementation(() => ({
      write: jest.fn((_chunk: any, _enc?: any, cb?: () => void) => {
        if (typeof _enc === 'function') _enc();
        else if (cb) cb();
        return true;
      }),
      end: jest.fn((cb?: () => void) => cb?.()),
      on: jest.fn()
    }));
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('Generate -> Evolve flow', () => {
    it('should generate art with evolution state influencing metadata', async () => {
      const axios = require('axios');
      axios.post.mockImplementation((url: string) => {
        if (url.includes('pinFileToIPFS')) {
          return Promise.resolve({ data: { IpfsHash: 'QmImg' } });
        }
        if (url.includes('pinJSONToIPFS')) {
          return Promise.resolve({ data: { IpfsHash: 'QmMeta' } });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      // Evolution state exists with custom palette
      fs.existsSync.mockImplementation((p: string) => p.includes('evolution'));
      fs.readFileSync.mockReturnValue(JSON.stringify(
        createMockEvolutionState({ generation: 2, complexity_boost: 3, color_palette: 'cool' })
      ));

      const result = await createAndUploadArt(2, 'cosmic flow');

      expect(result.metadata.attributes).toContainEqual({ trait_type: 'Palette', value: 'cool' });
      expect(result.metadata.attributes).toContainEqual({ trait_type: 'Complexity', value: '3' });
      expect(result.metadataUri).toBe('QmMeta');
    });

    it('should evolve agent and increase generation', () => {
      fs.existsSync.mockReturnValue(false);
      fs.mkdirSync.mockImplementation(() => undefined);
      fs.writeFileSync.mockImplementation(() => undefined);

      const result = evolveAgent({
        proceeds: '0.02',
        generation: 1,
        trigger: 'sales_milestone'
      });

      expect(result.previousGeneration).toBe(1);
      expect(result.newGeneration).toBe(2);
      expect(result.improvements.length).toBeGreaterThan(0);
    });
  });

  describe('Evolution state flow', () => {
    it('should trigger evolution when sales threshold met', () => {
      fs.existsSync.mockReturnValue(false);

      expect(shouldEvolve(2)).toBe(false);
      expect(shouldEvolve(3)).toBe(true);
    });

    it('should select theme from unlocked themes', () => {
      fs.existsSync.mockReturnValue(false);

      const theme = selectTheme();
      const defaultThemes = ['cosmic nebula', 'digital forest', 'abstract emotion', 'geometric dreams'];
      expect(defaultThemes).toContain(theme);
    });

    it('should calculate valid list price', () => {
      fs.existsSync.mockReturnValue(false);

      const price = calculateListPrice();
      expect(parseFloat(price)).toBeGreaterThan(0);
      expect(price).toMatch(/^\d+\.\d+$/);
    });

    it('should update stats without evolving', () => {
      fs.existsSync.mockReturnValue(false);
      fs.mkdirSync.mockImplementation(() => undefined);
      fs.writeFileSync.mockImplementation(() => undefined);

      updateStats(5, 2, '0.01');

      expect(fs.writeFileSync).toHaveBeenCalled();
      const writtenData = JSON.parse(fs.writeFileSync.mock.calls[0][1]);
      expect(writtenData.total_minted).toBe(5);
      expect(writtenData.total_sold).toBe(2);
      expect(writtenData.total_proceeds).toBe('0.01');
    });
  });
});
