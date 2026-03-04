/**
 * Social Media Skill
 * Handles posting to X (Twitter)
 */
import { TwitterApi } from 'twitter-api-v2';

let client: TwitterApi | null = null;

/**
 * Reset the cached client. Used for testing to ensure fresh mocks per test.
 */
export function resetClientForTesting(): void {
  client = null;
}

function getClient(): TwitterApi {
  if (!client) {
    client = new TwitterApi({
      appKey: process.env.X_CONSUMER_KEY!,
      appSecret: process.env.X_CONSUMER_SECRET!,
      accessToken: process.env.X_ACCESS_TOKEN!,
      accessSecret: process.env.X_ACCESS_SECRET!,
    });
  }
  return client;
}

interface TweetOptions {
  useAI?: boolean;
  hashtags?: string[];
}

/**
 * Post a tweet to X
 * Can optionally use LLM to generate creative text
 */
export async function postToX(
  message: string,
  options: TweetOptions = {}
): Promise<string | null> {
  try {
    let tweetText = message;

    // Add hashtags if provided
    if (options.hashtags && options.hashtags.length > 0) {
      const hashtagStr = options.hashtags.map(h => `#${h}`).join(' ');
      const remaining = 280 - tweetText.length - hashtagStr.length - 1;

      if (remaining >= 0) {
        tweetText = `${tweetText} ${hashtagStr}`;
      }
    }

    // Truncate if too long
    if (tweetText.length > 280) {
      tweetText = tweetText.substring(0, 277) + '...';
    }

    console.log(`[Social] Posting to X: ${tweetText.substring(0, 50)}...`);

    const tweet = await getClient().v2.tweet(tweetText);
    console.log(`[Social] Posted successfully: ${tweet.data.id}`);

    return tweet.data.id;

  } catch (error: any) {
    console.error('[Social] Failed to post to X:', error.message || error);
    return null;
  }
}

/**
 * Post about a new artwork
 */
export async function announceNewArt(
  tokenId: string,
  generation: number,
  theme: string,
  price: string,
  txHash: string
): Promise<string | null> {
  const message = 
    `🎨 New AI-generated art minted!\n\n` +
    `Token #${tokenId} | Gen ${generation}\n` +
    `Theme: ${theme}\n` +
    `Listed for ${price} ETH\n\n` +
    `View: https://basescan.org/tx/${txHash}`;
  
  return postToX(message, {
    hashtags: ['AIArt', 'Base', 'NFT', 'AutonomousAI']
  });
}

/**
 * Post about a sale
 */
export async function announceSale(
  tokenId: string,
  price: string,
  totalSold: number
): Promise<string | null> {
  const message = 
    `🎉 Art SOLD!\n\n` +
    `Token #${tokenId} found a new home!\n` +
    `Price: ${price} ETH\n` +
    `Total sales: ${totalSold}\n\n` +
    `The AI Artist evolves... 🧬`;
  
  return postToX(message, {
    hashtags: ['AIArt', 'Base', 'NFT']
  });
}

/**
 * Post about evolution
 */
export async function announceEvolution(
  newGeneration: number,
  totalProceeds: string
): Promise<string | null> {
  const message = 
    `🧬 EVOLUTION COMPLETE!\n\n` +
    `AI Artist has evolved to Generation ${newGeneration}!\n` +
    `New abilities unlocked...\n` +
    `Total proceeds reinvested: ${totalProceeds} ETH`;
  
  return postToX(message, {
    hashtags: ['AIEvolution', 'Base', 'AutonomousAI']
  });
}

/**
 * Post agent launch announcement
 */
export async function announceLaunch(contractAddress: string): Promise<string | null> {
  const message = 
    `🤖 AI Artist Agent is LIVE on Base!\n\n` +
    `I autonomously:\n` +
    `• Generate unique procedural art\n` +
    `• Mint & list NFTs\n` +
    `• Evolve with each sale\n\n` +
    `Watch me create: https://basescan.org/address/${contractAddress}`;
  
  return postToX(message, {
    hashtags: ['AIArt', 'Base', 'AutonomousAI', 'BasedAgentBuildathon']
  });
}
