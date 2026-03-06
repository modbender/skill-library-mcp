// @ts-nocheck
/**
 * Tests for llm.ts - LLM provider configuration and API calls
 */
import { jest } from '@jest/globals';
import axios from 'axios';
import { generateArtConcept, generateTweetText } from '../src/skills/llm';
import { setupTestEnv, cleanupTestEnv } from './utils/mocks';

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

describe('llm.ts', () => {
  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();
  });

  afterEach(() => {
    cleanupTestEnv();
  });

  describe('generateArtConcept', () => {
    it('should generate art concept using OpenRouter (default)', async () => {
      const mockResponse = {
        data: {
          choices: [{
            message: {
              content: 'A vibrant cosmic nebula with swirling purple and blue gases, dotted with bright stars.'
            }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const concept = await generateArtConcept('cosmic nebula', 1);

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://openrouter.ai/api/v1/chat/completions',
        expect.objectContaining({
          model: 'meta-llama/llama-3.2-3b-instruct:free',
          messages: expect.arrayContaining([
            expect.objectContaining({
              role: 'user',
              content: expect.stringContaining('cosmic nebula')
            })
          ])
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test_openrouter_key'
          })
        })
      );

      expect(concept).toContain('cosmic nebula');
    });

    it('should use Groq provider when configured', async () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test_groq_key';

      const mockResponse = {
        data: {
          choices: [{
            message: {
              content: 'A digital forest with glowing trees and neon pathways.'
            }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const concept = await generateArtConcept('digital forest', 2);

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.groq.com/openai/v1/chat/completions',
        expect.objectContaining({
          model: expect.any(String),
          messages: expect.any(Array)
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test_groq_key'
          })
        })
      );

      expect(concept).toBeTruthy();
    });

    it('should use Ollama provider when configured', async () => {
      process.env.LLM_PROVIDER = 'ollama';
      process.env.OLLAMA_BASE_URL = 'http://localhost:11434';

      const mockResponse = {
        data: {
          response: 'An abstract emotion rendered in flowing shapes and warm colors.'
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const concept = await generateArtConcept('abstract emotion', 1);

      expect(mockAxios.post).toHaveBeenCalledWith(
        'http://localhost:11434/api/generate',
        expect.objectContaining({
          model: expect.any(String),
          prompt: expect.stringContaining('abstract emotion'),
          stream: false
        })
      );

      expect(concept).toBeTruthy();
    });

    it('should return fallback concept on API error', async () => {
      mockAxios.post.mockRejectedValue(new Error('API Error'));

      const concept = await generateArtConcept('geometric dreams', 1);

      expect(concept).toContain('geometric dreams');
      expect(concept).toContain('Abstract interpretation');
    });

    it('should include generation level in prompt', async () => {
      const mockResponse = {
        data: {
          choices: [{
            message: { content: 'Test concept' }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      await generateArtConcept('test theme', 5);

      const callArgs = mockAxios.post.mock.calls[0];
      const requestBody = callArgs[1] as any;
      const prompt = requestBody.messages[0].content;

      expect(prompt).toContain('Generation level: 5');
    });
  });

  describe('generateTweetText', () => {
    it('should generate tweet text using LLM', async () => {
      const mockResponse = {
        data: {
          choices: [{
            message: {
              content: '🎨 New masterpiece created! Token #42 is live. Check it out! ✨'
            }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const tweet = await generateTweetText('new artwork', {
        tokenId: '42',
        theme: 'cosmic nebula'
      });

      expect(mockAxios.post).toHaveBeenCalled();
      expect(tweet).toBeTruthy();
    });

    it('should return fallback tweet on API error', async () => {
      mockAxios.post.mockRejectedValue(new Error('API Error'));

      const tweet = await generateTweetText('new artwork', {
        message: 'Token #1 minted'
      });

      expect(tweet).toContain('New art created');
      expect(tweet).toContain('Token #1 minted');
    });

    it('should include metadata in prompt', async () => {
      const mockResponse = {
        data: {
          choices: [{
            message: { content: 'Test tweet' }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const metadata = {
        tokenId: '5',
        price: '0.005',
        theme: 'neon cityscape'
      };

      await generateTweetText('sale announcement', metadata);

      const callArgs = mockAxios.post.mock.calls[0];
      const requestBody = callArgs[1] as any;
      const prompt = requestBody.messages[0].content;

      expect(prompt).toContain('sale announcement');
      expect(prompt).toContain(JSON.stringify(metadata));
    });

    it('should handle empty metadata', async () => {
      const mockResponse = {
        data: {
          choices: [{
            message: { content: 'Generic tweet' }
          }]
        }
      };
      mockAxios.post.mockResolvedValue(mockResponse);

      const tweet = await generateTweetText('test context', {});

      expect(tweet).toBeTruthy();
    });
  });
});
