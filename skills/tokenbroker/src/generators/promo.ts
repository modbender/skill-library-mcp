/**
 * Promo Generator
 * 
 * Generates X (Twitter) threads, Telegram posts, and Discord announcements.
 */

import { RepoAnalysis } from './types.js';

/**
 * Input interface for promo generation
 */
export interface PromoInput {
    /** Repository analysis data */
    repoAnalysis: RepoAnalysis;
    /** Token identity */
    identity: {
        name: string;
        ticker: string;
        description: string;
    };
    /** Investment thesis */
    reasoning: {
        investmentThesis: string;
        problemStatement: string;
        solution: string;
        vision: string;
    };
}

/**
 * A single tweet in a thread
 */
export interface Tweet {
    /** Tweet number in thread (1-based) */
    number: number;
    /** Tweet content (max 280 chars) */
    content: string;
    /** Whether this tweet should include an image */
    hasImage: boolean;
    /** Image description (if hasImage is true) */
    imageDescription?: string;
}

/**
 * X Thread structure
 */
export interface XThread {
    /** Thread title */
    title: string;
    /** Array of tweets in order */
    tweets: Tweet[];
    /** Suggested hashtags */
    hashtags: string[];
    /** Suggested mentions */
    mentions: string[];
}

/**
 * Telegram post structure
 */
export interface TelegramPost {
    /** Post title */
    title: string;
    /** Post content (supports markdown) */
    content: string;
    /** Whether to include a button */
    hasButton: boolean;
    /** Button text (if hasButton is true) */
    buttonText?: string;
    /** Button URL (if hasButton is true) */
    buttonUrl?: string;
}

/**
 * Discord announcement structure
 */
export interface DiscordAnnouncement {
    /** Announcement title */
    title: string;
    /** Announcement content */
    content: string;
    /** Whether to include an embed */
    hasEmbed: boolean;
    /** Embed color (hex) */
    embedColor?: string;
    /** Fields to include in embed */
    embedFields?: { name: string; value: string; inline: boolean }[];
}

/**
 * Output interface for promo generation
 */
export interface PromoOutput {
    /** X (Twitter) thread */
    xThread: XThread;
    /** Telegram announcement */
    telegramPost: TelegramPost;
    /** Discord announcement */
    discordAnnouncement: DiscordAnnouncement;
    /** Additional marketing copy */
    tagline: string;
    /** One-liner elevator pitch */
    elevatorPitch: string;
}

/**
 * Detect category from repo analysis
 */
function detectCategory(analysis: RepoAnalysis): string {
    const combinedText = `
        ${analysis.repoName} ${analysis.description} ${analysis.readme} 
        ${analysis.features.join(' ')} ${analysis.techStack.join(' ')}
    `.toLowerCase();

    const categories: Record<string, string[]> = {
        defi: ['defi', 'decentralized', 'exchange', 'swap', 'liquidity', 'yield', 'farm', 'staking'],
        ai: ['ai', 'ml', 'machine', 'learning', 'neural', 'gpt', 'llm', 'model', 'agent'],
        nft: ['nft', 'collectible', 'art', 'digital', 'mint', 'marketplace'],
        gaming: ['game', 'gaming', 'play', 'guild', 'quest', 'metaverse', 'virtual'],
        social: ['social', 'community', 'dao', 'governance', 'voting'],
        infrastructure: ['infrastructure', 'node', 'validator', 'rpc', 'indexer', 'data'],
        meme: ['meme', 'fun', 'joke', 'pepe', 'dog', 'cat', 'moon', 'doge']
    };

    let maxScore = 0;
    let detectedCategory = 'meme';

    for (const [category, keywords] of Object.entries(categories)) {
        let score = 0;
        for (const keyword of keywords) {
            if (combinedText.includes(keyword)) {
                score++;
            }
        }
        if (score > maxScore) {
            maxScore = score;
            detectedCategory = category;
        }
    }

    return detectedCategory;
}

/**
 * Generate X thread title
 */
function generateThreadTitle(name: string, ticker: string): string {
    return `Introducing ${name} (${ticker}) 🚀`;
}

/**
 * Generate hashtags based on category
 */
function generateHashtags(category: string, ticker: string): string[] {
    const baseTags = [ticker, '#crypto', '#memecoin', '#airdrops'];

    const categoryTags: Record<string, string[]> = {
        defi: ['#defi', '#yield', '#liquidity'],
        ai: ['#ai', '#agent', '#agi'],
        nft: ['#nft', '#digitalart', '#collectibles'],
        gaming: ['#gaming', '#play2earn', '#metaverse'],
        social: ['#dao', '#governance', '#community'],
        infrastructure: ['#web3', '#infrastructure', '#rpc'],
        meme: ['#meme', '#moon', '#wagmi']
    };

    return [...baseTags, ...(categoryTags[category] || [])].slice(0, 5);
}

/**
 * Generate tweet content based on position in thread
 */
function generateTweet(
    position: number,
    total: number,
    identity: PromoInput['identity'],
    reasoning: PromoInput['reasoning']
): Tweet {
    const { name, ticker } = identity;
    const { investmentThesis, problemStatement, solution, vision } = reasoning;

    const templates: Record<number, () => Tweet> = {
        1: () => ({
            number: 1,
            content: `🧵 New token launch: ${name} (${ticker})\n\nA new chapter in crypto begins. Let me explain why this matters 👇`,
            hasImage: true,
            imageDescription: `${ticker} token logo - sleek, memorable design`
        }),
        2: () => ({
            number: 2,
            content: `The problem: ${problemStatement.substring(0, 150)}...`,
            hasImage: false
        }),
        3: () => ({
            number: 3,
            content: `The solution: ${solution.substring(0, 150)}...`,
            hasImage: false
        }),
        4: () => ({
            number: 4,
            content: `${ticker} is built for the community. No VCs, no presales, just pure diamond hands.`,
            hasImage: false
        }),
        5: () => ({
            number: 5,
            content: `Vision: ${vision}\n\nThis is just the beginning. ${name} is here to stay.`,
            hasImage: false
        }),
        6: () => ({
            number: 6,
            content: `🚀 Launching soon on nad.fun\n\nDon't miss out. ${ticker} to the moon!`,
            hasImage: true,
            imageDescription: `${ticker} rocket to the moon`
        })
    };

    const tweetGenerator = templates[position];
    return tweetGenerator ? tweetGenerator() : templates[1]();
}

/**
 * Generate X thread
 */
function generateXThread(
    identity: PromoInput['identity'],
    reasoning: PromoInput['reasoning']
): XThread {
    const category = detectCategory({ ...reasoning } as unknown as RepoAnalysis);
    const tweets = [1, 2, 3, 4, 5, 6].map(i => generateTweet(i, 6, identity, reasoning));

    return {
        title: generateThreadTitle(identity.name, identity.ticker),
        tweets,
        hashtags: generateHashtags(category, identity.ticker),
        mentions: ['@nadfun']
    };
}

/**
 * Generate Telegram post
 */
function generateTelegramPost(
    identity: PromoInput['identity'],
    reasoning: PromoInput['reasoning']
): TelegramPost {
    const { name, ticker, description } = identity;

    return {
        title: `🎉 ${name} (${ticker}) Launch Announcement`,
        content: `**${name}** is coming to nad.fun!

_${description.substring(0, 200)}_

**Why ${ticker}?**
• Community-driven from day one
• Fair launch, no presales
• Built for longevity

**Stay tuned for launch!** 🚀

#${ticker} #Memecoin #NadFun`,
        hasButton: true,
        buttonText: 'View on Nad.fun',
        buttonUrl: 'https://nad.fun'
    };
}

/**
 * Generate Discord announcement
 */
function generateDiscordAnnouncement(
    identity: PromoInput['identity'],
    reasoning: PromoInput['reasoning']
): DiscordAnnouncement {
    const { name, ticker } = identity;
    const { vision } = reasoning;

    return {
        title: `🎉 ${name} Launching on Nad.fun!`,
        content: `Hey everyone! Big news - **${name}** (${ticker}) is launching!

${vision}

Stay tuned for:
• 📢 Launch announcements
• 💰 Airdrop opportunities  
• 🎁 Community rewards

Let's go ${ticker}! 🚀`,
        hasEmbed: true,
        embedColor: '#6366f1',
        embedFields: [
            { name: 'Ticker', value: ticker, inline: true },
            { name: 'Platform', value: 'Nad.fun', inline: true },
            { name: 'Status', value: 'Coming Soon', inline: true }
        ]
    };
}

/**
 * Generate tagline
 */
function generateTagline(name: string, ticker: string): string {
    const taglines = [
        `${name}: Where mememons come to life`,
        `${ticker} - The future of community tokens`,
        `${name} (${ticker}): Built different`,
        `${ticker} to the moon and beyond`,
        `${name}: Powered by the community`
    ];
    return taglines[Math.floor(Math.random() * taglines.length)];
}

/**
 * Generate elevator pitch
 */
function generateElevatorPitch(identity: PromoInput['identity']): string {
    return `${identity.name} (${identity.ticker}) - ${identity.description.substring(0, 100)}...`;
}

/**
 * Generates promotional content including X threads, Telegram posts, and Discord announcements.
 * 
 * @param input - The input containing repository analysis, identity, and reasoning
 * @returns Promise resolving to promo output with all marketing content
 * 
 * @example
 * ```typescript
 * const promo = await generatePromo({
 *   repoAnalysis: { /* repo data * / },
 *   identity: { name: "AweSome", ticker: "AWE", description: "..." },
 *   reasoning: { investmentThesis: "...", problemStatement: "...", solution: "...", vision: "..." }
 * });
 * console.log(promo.xThread.tweets[0].content);
 * ```
 */
export async function generatePromo(input: PromoInput): Promise<PromoOutput> {
    const { identity, reasoning } = input;

    return {
        xThread: generateXThread(identity, reasoning),
        telegramPost: generateTelegramPost(identity, reasoning),
        discordAnnouncement: generateDiscordAnnouncement(identity, reasoning),
        tagline: generateTagline(identity.name, identity.ticker),
        elevatorPitch: generateElevatorPitch(identity)
    };
}
