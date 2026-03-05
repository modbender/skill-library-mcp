// @ts-nocheck
/**
 * Tests for evolve.ts - Evolution state management and logic
 */
import { jest } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import {
  getEvolutionState,
  updateStats,
  evolveAgent,
  selectTheme,
  calculateListPrice,
  shouldEvolve
} from '../src/skills/evolve';
import { setupTestEnv, cleanupTestEnv, createMockEvolutionState } from './utils/mocks';

// Mock fs module
jest.mock('fs');
const mockFs = fs as jest.Mocked<typeof fs>;

// Path-aware mocks: evolve uses evolution.json (state) and evolution-rules.json (rules)
const EVOLUTION_RULES = {
  scarcityBonus: 0.002,
  demandBonus: 0.003,
  basePrice: 0.005,
  generationBonus: 0.001,
  themes: { "2": "neon cityscape", "3": "organic flow", "4": "fractal universe" },
  salesThresholdMultiplier: 3
};

function setupPathAwareMocks(configExists: boolean, configData?: any, rulesExist = true) {
  mockFs.existsSync.mockImplementation((p: string) => {
    if (p.includes('evolution-rules')) return rulesExist;
    if (p.includes('evolution.json')) return configExists;
    return false;
  });
  mockFs.readFileSync.mockImplementation((p: string) => {
    if (p.includes('evolution-rules')) return JSON.stringify(EVOLUTION_RULES);
    if (p.includes('evolution.json') && configData) return JSON.stringify(configData);
    return '{}';
  });
}

describe('evolve.ts', () => {
  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('getEvolutionState', () => {
    it('should return default state when config file does not exist', () => {
      setupPathAwareMocks(false);

      const state = getEvolutionState();

      expect(state.generation).toBe(1);
      expect(state.complexity_boost).toBe(1);
      expect(state.color_palette).toBe('vibrant');
      expect(state.themes_unlocked).toHaveLength(4);
      expect(state.total_minted).toBe(0);
      expect(state.total_sold).toBe(0);
    });

    it('should load state from config file when it exists', () => {
      const savedState = createMockEvolutionState({
        generation: 3,
        total_sold: 6,
        total_proceeds: '0.03'
      });

      setupPathAwareMocks(true, savedState);

      const state = getEvolutionState();

      expect(state.generation).toBe(3);
      expect(state.total_sold).toBe(6);
      expect(state.total_proceeds).toBe('0.03');
    });

    it('should handle corrupted config file gracefully', () => {
      mockFs.existsSync.mockImplementation((p: string) => p.includes('evolution.json'));
      mockFs.readFileSync.mockReturnValue('invalid json');

      const state = getEvolutionState();

      expect(state.generation).toBe(1); // Should return default state
    });
  });

  describe('updateStats', () => {
    it('should update stats without evolving', () => {
      setupPathAwareMocks(false);
      mockFs.mkdirSync.mockImplementation(() => undefined);
      mockFs.writeFileSync.mockImplementation(() => undefined);

      updateStats(5, 2, '0.01');

      expect(mockFs.writeFileSync).toHaveBeenCalled();
      const writtenData = JSON.parse(mockFs.writeFileSync.mock.calls[0][1] as string);
      expect(writtenData.total_minted).toBe(5);
      expect(writtenData.total_sold).toBe(2);
      expect(writtenData.total_proceeds).toBe('0.01');
      expect(writtenData.generation).toBe(1); // Generation should not change
    });
  });

  describe('evolveAgent', () => {
    beforeEach(() => {
      setupPathAwareMocks(false);
      mockFs.mkdirSync.mockImplementation(() => undefined);
      mockFs.writeFileSync.mockImplementation(() => undefined);
    });

    it('should unlock new theme at generation 2', () => {
      const result = evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      expect(result.newAbilities).toContain('New theme unlocked: "neon cityscape"');
    });

    it('should increase generation number', () => {
      const result = evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      expect(result.previousGeneration).toBe(1);
      expect(result.newGeneration).toBe(2);
    });

    it('should increase complexity boost', () => {
      evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      const writtenData = JSON.parse(mockFs.writeFileSync.mock.calls[0][1] as string);
      expect(writtenData.complexity_boost).toBe(2);
    });

    it('should rotate color palette', () => {
      evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      const writtenData = JSON.parse(mockFs.writeFileSync.mock.calls[0][1] as string);
      expect(['warm', 'cool', 'vibrant', 'monochrome']).toContain(writtenData.color_palette);
    });

    it('should increase element variety', () => {
      evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      const writtenData = JSON.parse(mockFs.writeFileSync.mock.calls[0][1] as string);
      expect(writtenData.element_variety).toBe(4);
    });

    it('should record evolution in history', () => {
      evolveAgent({
        proceeds: '0.015',
        generation: 1,
        trigger: 'sales_milestone'
      });

      const writeCalls = mockFs.writeFileSync.mock.calls;
      expect(writeCalls.length).toBeGreaterThan(0);
      const writtenData = JSON.parse(writeCalls[writeCalls.length - 1][1] as string);
      expect(writtenData.evolution_history).toHaveLength(1);
      expect(writtenData.evolution_history[0].generation).toBe(2);
      expect(writtenData.evolution_history[0].trigger).toBe('sales_milestone');
    });

    it('should cap complexity boost at 10', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 10, complexity_boost: 10 }));

      evolveAgent({
        proceeds: '0.1',
        generation: 10,
        trigger: 'sales_milestone'
      });

      const writtenData = JSON.parse(mockFs.writeFileSync.mock.calls[0][1] as string);
      expect(writtenData.complexity_boost).toBe(10); // Should not exceed 10
    });
  });

  describe('selectTheme', () => {
    it('should return a theme from unlocked themes', () => {
      setupPathAwareMocks(false);

      const theme = selectTheme();

      const defaultThemes = ['cosmic nebula', 'digital forest', 'abstract emotion', 'geometric dreams'];
      expect(defaultThemes).toContain(theme);
    });

    it('should select from expanded theme list after evolution', () => {
      setupPathAwareMocks(true, createMockEvolutionState({
        themes_unlocked: ['cosmic nebula', 'digital forest', 'neon cityscape', 'organic flow']
      }));

      const theme = selectTheme();

      expect(['cosmic nebula', 'digital forest', 'neon cityscape', 'organic flow']).toContain(theme);
    });
  });

  describe('calculateListPrice', () => {
    it('should calculate base price for generation 1', () => {
      setupPathAwareMocks(false);

      const price = calculateListPrice();

      expect(parseFloat(price)).toBe(0.006); // 0.005 base + 0.001 generation bonus
    });

    it('should increase price with generation', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 5, total_sold: 0 }));

      const price = calculateListPrice();

      expect(parseFloat(price)).toBe(0.010); // 0.005 + (5 * 0.001)
    });

    it('should add scarcity bonus after 5 sales', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 1, total_sold: 6 }));

      const price = calculateListPrice();

      expect(parseFloat(price)).toBe(0.008); // 0.005 + 0.001 + 0.002 scarcity
    });

    it('should add demand bonus after 10 sales', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 1, total_sold: 11 }));

      const price = calculateListPrice();

      expect(parseFloat(price)).toBe(0.011); // 0.005 + 0.001 + 0.002 + 0.003 demand
    });
  });

  describe('shouldEvolve', () => {
    it('should return false when sales threshold not met', () => {
      setupPathAwareMocks(false);

      const result = shouldEvolve(2);

      expect(result).toBe(false); // Need 3 sales for gen 1
    });

    it('should return true when sales threshold met', () => {
      setupPathAwareMocks(false);

      const result = shouldEvolve(3);

      expect(result).toBe(true); // 3 sales triggers evolution for gen 1
    });

    it('should scale threshold with generation', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 3, total_sold: 8 }));

      const result = shouldEvolve(9);

      expect(result).toBe(true); // Gen 3 needs 9 sales (3 * 3)
    });

    it('should not trigger if total sold has not increased', () => {
      setupPathAwareMocks(true, createMockEvolutionState({ generation: 1, total_sold: 3 }));

      const result = shouldEvolve(3);

      expect(result).toBe(false); // Same as current total_sold
    });
  });
});
