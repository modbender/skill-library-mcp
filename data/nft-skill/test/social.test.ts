// @ts-nocheck
/**
 * Tests for social.ts - Social media posting
 */
import { jest } from '@jest/globals';
import { TwitterApi } from 'twitter-api-v2';
import {
  postToX,
  announceNewArt,
  announceSale,
  announceEvolution,
  announceLaunch,
  resetClientForTesting
} from '../src/skills/social';
import { setupTestEnv, cleanupTestEnv } from './utils/mocks';

// Mock twitter-api-v2
jest.mock('twitter-api-v2');

describe('social.ts', () => {
  let mockTwitterClient: any;

  beforeEach(() => {
    setupTestEnv();
    jest.clearAllMocks();

    mockTwitterClient = {
      v2: {
        tweet: jest.fn().mockResolvedValue({
          data: { id: '1234567890' }
        })
      }
    };

    (TwitterApi as jest.MockedClass<typeof TwitterApi>).mockImplementation(() => mockTwitterClient);
  });

  afterEach(() => {
    resetClientForTesting();
    cleanupTestEnv();
  });

  describe('postToX', () => {
    it('should post tweet successfully', async () => {
      const tweetId = await postToX('Test tweet message');

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalledWith('Test tweet message');
      expect(tweetId).toBe('1234567890');
    });

    it('should add hashtags when provided', async () => {
      await postToX('Test message', {
        hashtags: ['AIArt', 'Base', 'NFT']
      });

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalledWith(
        expect.stringContaining('#AIArt #Base #NFT')
      );
    });

    it('should truncate long tweets to 280 characters', async () => {
      const longMessage = 'A'.repeat(300);

      await postToX(longMessage);

      const calledWith = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(calledWith.length).toBeLessThanOrEqual(280);
      expect(calledWith).toContain('...');
    });

    it('should not add hashtags if they would exceed 280 chars', async () => {
      const message = 'A'.repeat(270);

      await postToX(message, {
        hashtags: ['VeryLongHashtag']
      });

      const calledWith = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(calledWith).not.toContain('#VeryLongHashtag');
    });

    it('should return null on API error', async () => {
      mockTwitterClient.v2.tweet.mockRejectedValue(new Error('Twitter API error'));

      const result = await postToX('Test message');

      expect(result).toBeNull();
    });

    it('should handle empty message', async () => {
      await postToX('');

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalledWith('');
    });
  });

  describe('announceNewArt', () => {
    it('should announce new artwork with all details', async () => {
      await announceNewArt('42', 3, 'cosmic nebula', '0.007', '0xabcdef123');

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalled();
      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];

      expect(tweetText).toContain('Token #42');
      expect(tweetText).toContain('Gen 3');
      expect(tweetText).toContain('cosmic nebula');
      expect(tweetText).toContain('0.007 ETH');
      expect(tweetText).toContain('0xabcdef123');
    });

    it('should include appropriate hashtags', async () => {
      await announceNewArt('1', 1, 'test theme', '0.005', '0xhash');

      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(tweetText).toContain('#AIArt');
      expect(tweetText).toContain('#Base');
      expect(tweetText).toContain('#NFT');
    });
  });

  describe('announceSale', () => {
    it('should announce sale with details', async () => {
      await announceSale('5', '0.008', 12);

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalled();
      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];

      expect(tweetText).toContain('Token #5');
      expect(tweetText).toContain('0.008 ETH');
      expect(tweetText).toContain('Total sales: 12');
    });

    it('should mention evolution', async () => {
      await announceSale('1', '0.005', 1);

      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(tweetText).toContain('evolves');
    });
  });

  describe('announceEvolution', () => {
    it('should announce evolution milestone', async () => {
      await announceEvolution(4, '0.045');

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalled();
      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];

      expect(tweetText).toContain('EVOLUTION');
      expect(tweetText).toContain('Generation 4');
      expect(tweetText).toContain('0.045 ETH');
    });

    it('should include evolution hashtags', async () => {
      await announceEvolution(2, '0.015');

      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(tweetText).toContain('#AIEvolution');
    });
  });

  describe('announceLaunch', () => {
    it('should announce agent launch', async () => {
      await announceLaunch('0x1111111111111111111111111111111111111111');

      expect(mockTwitterClient.v2.tweet).toHaveBeenCalled();
      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];

      expect(tweetText).toContain('LIVE');
      expect(tweetText).toContain('0x1111111111111111111111111111111111111111');
    });

    it('should describe agent capabilities', async () => {
      await announceLaunch('0xcontract');

      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(tweetText).toContain('Generate');
      expect(tweetText).toContain('Mint');
      expect(tweetText).toContain('Evolve');
    });

    it('should include buildathon hashtag', async () => {
      await announceLaunch('0xcontract');

      const tweetText = mockTwitterClient.v2.tweet.mock.calls[0][0];
      expect(tweetText).toContain('#BasedAgentBuildathon');
    });
  });
});
