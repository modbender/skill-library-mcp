/**
 * Bird Twitter Integration
 *
 * Uses bird CLI tool to fetch real Twitter/X data
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface BirdProfile {
  bio: string;
  followers: number;
  following: number;
  tweets: Array<{
    text: string;
    likes: number;
    retweets: number;
    timestamp: number;
  }>;
}

export interface BirdFollowing {
  handles: string[];
}

/**
 * Fetch Twitter profile using bird CLI
 */
export async function fetchTwitterProfile(handle: string): Promise<BirdProfile | null> {
  try {
    // Remove @ if present
    const cleanHandle = handle.startsWith('@') ? handle.slice(1) : handle;

    // Execute bird command
    const { stdout } = await execAsync(`bird user ${cleanHandle} --with-tweets --limit 10 --json`);
    const data = JSON.parse(stdout);

    return {
      bio: data.description || data.bio || '',
      followers: data.followers_count || 0,
      following: data.following_count || 0,
      tweets: (data.tweets || []).map((tweet: any) => ({
        text: tweet.text || tweet.full_text || '',
        likes: tweet.favorite_count || tweet.likes || 0,
        retweets: tweet.retweet_count || 0,
        timestamp: new Date(tweet.created_at).getTime(),
      })),
    };
  } catch (error) {
    console.error(`Failed to fetch Twitter profile for ${handle}:`, error);
    return null;
  }
}

/**
 * Fetch Twitter following list using bird CLI
 */
export async function fetchTwitterFollowing(handle: string, limit: number = 100): Promise<BirdFollowing | null> {
  try {
    const cleanHandle = handle.startsWith('@') ? handle.slice(1) : handle;

    const { stdout } = await execAsync(`bird following ${cleanHandle} --limit ${limit} --json`);
    const data = JSON.parse(stdout);

    const handles = (data.users || data.following || [])
      .map((user: any) => '@' + (user.screen_name || user.username || ''))
      .filter((h: string) => h !== '@');

    return { handles };
  } catch (error) {
    console.error(`Failed to fetch Twitter following for ${handle}:`, error);
    return null;
  }
}

/**
 * Analyze Twitter interactions from recent tweets
 */
export function analyzeInteractions(tweets: Array<{ text: string }>): {
  likes: string[];
  retweets: string[];
  replies: string[];
} {
  const mentions = new Set<string>();

  // Extract @mentions from tweets
  tweets.forEach(tweet => {
    const regex = /@(\w+)/g;
    let match;
    while ((match = regex.exec(tweet.text)) !== null) {
      mentions.add('@' + match[1]);
    }
  });

  const mentionArray = Array.from(mentions);

  // For now, categorize all as replies
  // In a more sophisticated version, we'd track RT/like patterns
  return {
    likes: mentionArray.slice(0, 5),
    retweets: mentionArray.slice(0, 3),
    replies: mentionArray.slice(0, 3),
  };
}
