/**
 * Identity Generator
 * 
 * Generates token Name, Ticker, and Description based on repository analysis.
 */

import { RepoAnalysis } from './types';

/**
 * Input interface for identity generation
 */
export interface IdentityInput {
    /** Repository analysis data */
    repoAnalysis: RepoAnalysis;
}

/**
 * Output interface for identity generation
 */
export interface IdentityOutput {
    /** Generated token name */
    name: string;
    /** Generated token ticker (3-5 characters) */
    ticker: string;
    /** Tagline for the token */
    tagline: string;
    /** Generated token description/summary */
    description: string;
    /** Reasoning behind the name choice */
    nameReasoning: string;
}

/**
 * Keyword mappings for project categorization
 */
const PROJECT_CATEGORIES = {
    defi: {
        keywords: ['defi', 'decentralized', 'exchange', 'swap', 'liquidity', 'pool', 'yield', 'farm', 'staking', 'bridge', 'oracle', 'amm', 'trading', ' arbitrage'],
        prefixes: ['SWAP', 'LIQ', 'POOL', 'YIELD', 'DEX', 'FLOW', 'TRADE', 'VAULT', 'CHAIN'],
        suffixes: ['FIN', 'DEX', 'SWAP', 'POOL', 'FARM', 'STAKE', 'BRIDGE', 'ORACLE']
    },
    ai: {
        keywords: ['ai', 'ml', 'machine', 'learning', 'neural', 'gpt', 'llm', 'model', 'inference', 'training', 'agent', 'chatbot', 'cognitive'],
        prefixes: ['NEUR', 'GPT', 'MIND', 'BRAIN', 'COG', 'THINK', 'CORTEX', 'SYNAPSE'],
        suffixes: ['AI', 'ML', 'GPT', 'CORE', 'NET', 'NODE', 'MIND', 'BOT']
    },
    nft: {
        keywords: ['nft', 'collectible', 'art', 'digital', 'mint', 'marketplace', 'gallery', 'cryptoart', 'pixel', 'avatar', 'profile'],
        prefixes: ['ART', 'PIXEL', 'CUBE', 'MINT', 'DROP', 'RARE', 'GEN', 'CULT'],
        suffixes: ['NFT', 'ART', 'PIX', 'CUBE', 'GEN', 'MINT', 'DROP', 'PFP']
    },
    gaming: {
        keywords: ['game', 'gaming', 'play', 'guild', 'quest', 'loot', 'rpg', 'metaverse', 'virtual', 'world', 'character', 'pvp', 'pve'],
        prefixes: ['PLAY', 'QUEST', 'LOOT', 'GAME', 'GUILD', 'WORLD', 'META', 'REALM'],
        suffixes: ['GAME', 'QUEST', 'LOOT', 'PVP', 'PVE', 'XP', 'Loot', 'BATTLE']
    },
    social: {
        keywords: ['social', 'community', 'chat', 'messaging', 'social', 'forum', 'dao', 'governance', 'voting', 'proposal'],
        prefixes: ['SOCIAL', 'COMM', 'CHAT', 'VOICE', 'POST', 'CIRCLE', 'TRIBE', 'CLAN'],
        suffixes: ['DAO', 'VOTE', 'CHAT', 'POST', 'HUB', 'NET', 'SOCIAL']
    },
    infrastructure: {
        keywords: ['infrastructure', 'infra', 'node', 'validator', 'rpc', 'indexer', 'data', 'storage', 'compute', 'network', 'protocol', 'layer'],
        prefixes: ['NODE', 'NET', 'CHAIN', 'LAYER', 'DATA', 'INDEX', 'VALID', 'PROTO'],
        suffixes: ['NODE', 'NET', 'DATA', 'INDEX', 'CHAIN', 'PROTO', 'LAYER', 'VALID']
    },
    tools: {
        keywords: ['tool', 'utility', 'cli', 'dashboard', 'analytics', 'monitor', 'alert', 'notification', 'integration', 'api', 'sdk', 'library', 'framework'],
        prefixes: ['TOOL', 'UTIL', 'CODE', 'BUILD', 'DEV', 'STACK', 'KIT', 'SUITE'],
        suffixes: ['TOOL', 'UTIL', 'KIT', 'SDK', 'LIB', 'API', 'CLI', 'DASH']
    },
    meme: {
        keywords: ['meme', 'fun', 'joke', 'pepe', 'dog', 'cat', 'bunny', 'frog', 'moon', 'rocket', 'doge', 'shib', 'inu'],
        prefixes: ['MOON', 'ROCKET', 'DOGE', 'PEPE', 'BUNNY', 'FROG', 'CAT', 'WOW'],
        suffixes: ['MOON', 'ROCKET', 'PEPE', 'DOGE', 'MEME', 'FUN', 'GAIN', 'WAGMI']
    }
};

/**
 * Common word transformations for token name generation
 */
const WORD_TRANSFORMATIONS: Record<string, string[]> = {
    'generate': ['GEN', 'SWEEP', 'FORGE', 'MAKE', 'BUILD'],
    'launch': ['LAUNCH', 'START', 'IGNITE', 'KICK', 'RISE'],
    'bot': ['BOT', 'AUTO', 'ROBO', 'AI', 'CORE'],
    'swap': ['SWAP', 'TRADE', 'EXCHANGE', 'FLIP', 'SWITCH'],
    'liquidity': ['LIQ', 'LIQUID', 'POOL', 'FLOW', 'DEPTH'],
    'token': ['TOKEN', 'COIN', 'ASSET', 'SYMBOL', 'UNIT'],
    'crypto': ['CRYPTO', 'COIN', 'BLOCK', 'CHAIN', 'DECENT'],
    'wallet': ['WALLET', 'VAULT', 'STORE', 'POCKET', 'CHEST'],
    'exchange': ['EX', 'SWAP', 'TRADE', 'MARKET', 'DEX'],
    'protocol': ['PROTO', 'RULE', 'SYSTEM', 'STACK', 'CODE'],
    'network': ['NET', 'WEB', 'CHAIN', 'NODE', 'GRID'],
    'agent': ['AGENT', 'BOT', 'AUTO', 'WORKER', 'RUNNER'],
    'trading': ['TRADE', 'DEAL', 'BUY', 'SELL', 'ARBITRAGE'],
    'staking': ['STAKE', 'LOCK', 'BOND', 'DEPOSIT', 'EARN'],
    'yield': ['YIELD', 'FARM', 'GROW', 'EARN', 'GOLD'],
    'mining': ['MINE', 'DIG', 'FORGE', 'HASH', 'WORK'],
    'oracle': ['ORACLE', 'DATA', 'FEED', 'TRUTH', 'SOURCE'],
    'index': ['INDEX', 'TRACK', 'BASKET', 'SET', 'COLLECT'],
    'options': ['OPTION', 'CALL', 'PUT', 'RIGHT', 'CHOICE'],
    'futures': ['FUTURE', 'TERM', 'FORWARD', 'NEXT', 'TOMORROW'],
    'stablecoin': ['STABLE', 'PEGGED', 'ANCHOR', 'FIRM', 'SOLID']
};

/**
 * Analyze the repository and determine its category based on keywords
 * 
 * @param analysis - Repository analysis data
 * @returns The detected project category
 */
function detectCategory(analysis: RepoAnalysis): keyof typeof PROJECT_CATEGORIES {
    const combinedText = `
        ${analysis.repoName} ${analysis.description} ${analysis.readme} ${analysis.features.join(' ')} ${analysis.techStack.join(' ')}
    `.toLowerCase();

    let maxScore = 0;
    let detectedCategory: keyof typeof PROJECT_CATEGORIES = 'tools';

    for (const [category, data] of Object.entries(PROJECT_CATEGORIES)) {
        let score = 0;
        for (const keyword of data.keywords) {
            if (combinedText.includes(keyword.trim())) {
                score += 1;
            }
        }
        if (score > maxScore) {
            maxScore = score;
            detectedCategory = category as keyof typeof PROJECT_CATEGORIES;
        }
    }

    return detectedCategory;
}

/**
 * Extract meaningful words from repository name
 * 
 * @param repoName - Repository name
 * @returns Array of cleaned words
 */
function extractWords(repoName: string): string[] {
    return repoName
        .split(/[-_/\s]+/)
        .map(word => word.replace(/[^a-zA-Z]/g, ''))
        .filter(word => word.length > 0);
}

/**
 * Transform a word into a token-friendly format
 * 
 * @param word - Word to transform
 * @returns Array of possible transformations
 */
function getWordTransformations(word: string): string[] {
    const lowerWord = word.toLowerCase();

    if (WORD_TRANSFORMATIONS[lowerWord]) {
        return WORD_TRANSFORMATIONS[lowerWord];
    }

    // Generate transformations based on word structure
    const transformations: string[] = [];

    // Uppercase first 4-6 characters
    if (word.length >= 4) {
        transformations.push(word.substring(0, Math.min(6, word.length)).toUpperCase());
    }

    // Take first 3 characters
    if (word.length >= 3) {
        transformations.push(word.substring(0, 3).toUpperCase());
    }

    // Interesting suffixes
    if (word.length > 4) {
        transformations.push(word.substring(word.length - 3).toUpperCase());
    }

    return transformations.length > 0 ? transformations : [word.toUpperCase()];
}

/**
 * Generate token ticker from project name
 * 
 * @param repoName - Repository name
 * @param category - Detected project category
 * @returns Generated ticker symbol
 */
function generateTicker(repoName: string, category: keyof typeof PROJECT_CATEGORIES): string {
    const words = extractWords(repoName);
    const categoryData = PROJECT_CATEGORIES[category];

    // Try to build ticker from meaningful words
    if (words.length >= 2) {
        const candidates: string[] = [];

        for (let i = 0; i < Math.min(words.length, 3); i++) {
            const word = words[i];
            const transformations = getWordTransformations(word);
            if (transformations.length > 0) {
                candidates.push(transformations[0]);
            }
        }

        if (candidates.length > 0) {
            return candidates.slice(0, 2).join('').substring(0, 5);
        }
    }

    // Fall back to category prefix
    const prefix = categoryData.prefixes[Math.floor(Math.random() * categoryData.prefixes.length)];
    return prefix.substring(0, Math.min(4, prefix.length));
}

/**
 * Generate token name based on repository analysis
 * 
 * @param analysis - Repository analysis data
 * @param category - Detected project category
 * @returns Generated token name
 */
function generateName(analysis: RepoAnalysis, category: keyof typeof PROJECT_CATEGORIES): string {
    const words = extractWords(analysis.repoName);
    const categoryData = PROJECT_CATEGORIES[category];

    // Try to create name from repo words
    if (words.length > 0) {
        const transformations = getWordTransformations(words[0]);
        if (transformations.length > 0 && transformations[0].length >= 4) {
            return transformations[0];
        }
    }

    // Fall back to category-based name
    const prefix = categoryData.prefixes[Math.floor(Math.random() * categoryData.prefixes.length)];
    const suffix = categoryData.suffixes[Math.floor(Math.random() * categoryData.suffixes.length)];

    return prefix + suffix;
}

/**
 * Generate tagline based on project description
 * 
 * @param analysis - Repository analysis data
 * @param category - Detected project category
 * @returns Generated tagline
 */
function generateTagline(analysis: RepoAnalysis, category: keyof typeof PROJECT_CATEGORIES): string {
    const taglines: Record<string, string[]> = {
        defi: [
            "The next generation DeFi protocol for automated trading",
            "Unlock yields with intelligent liquidity management",
            "Decentralized finance, simplified",
            "Your gateway to DeFi innovation",
            "Trustless trading meets seamless experience"
        ],
        ai: [
            "AI-powered intelligence for the blockchain era",
            "Machine learning meets decentralized automation",
            "The intelligent layer for Web3",
            "Cognitive computing for crypto natives",
            "Smart agents for the decentralized web"
        ],
        nft: [
            "Digital collectibles reimagined",
            "The marketplace for digital creativity",
            "Where art meets blockchain",
            "Mint, trade, and collect rare digital assets",
            "The home for digital collectors"
        ],
        gaming: [
            "Play-to-earn gaming redefined",
            "Your adventure in the metaverse",
            "Gaming meets blockchain rewards",
            "Level up with crypto incentives",
            "Immersive gaming in a decentralized world"
        ],
        social: [
            "Building communities on-chain",
            "Governance for the people",
            "Decentralized decision-making made simple",
            "Where communities gather and grow",
            "The voice of the decentralized web"
        ],
        infrastructure: [
            "The backbone of Web3 infrastructure",
            "Reliable data for decentralized apps",
            "Building the pipes of Web3",
            "Enterprise-grade infrastructure for DeFi",
            "The foundation for decentralized innovation"
        ],
        tools: [
            "The ultimate toolkit for Web3 developers",
            "Build faster, ship better",
            "Developer utilities for blockchain",
            "The tools you need for Web3 success",
            "Streamlined solutions for crypto projects"
        ],
        meme: [
            "To the moon and beyond",
            "The fun side of crypto",
            "HODL stronger",
            "Community first, moon next",
            "Diamond hands only"
        ]
    };

    const categoryTaglines = taglines[category] || taglines.tools;
    return categoryTaglines[Math.floor(Math.random() * categoryTaglines.length)];
}

/**
 * Generate full token description
 * 
 * @param analysis - Repository analysis data
 * @param category - Detected project category
 * @param name - Generated token name
 * @param ticker - Generated ticker
 * @returns Generated token description
 */
function generateDescription(
    analysis: RepoAnalysis,
    category: keyof typeof PROJECT_CATEGORIES,
    name: string,
    ticker: string
): string {
    const descriptions: Record<string, string[]> = {
        defi: [
            `${name} (${ticker}) is a revolutionary DeFi protocol designed to transform how users interact with decentralized finance. Built on cutting-edge smart contract technology, ${name} provides seamless swapping, yield farming, and liquidity provision with minimal slippage and maximum efficiency. The protocol emphasizes security, transparency, and community governance, ensuring that every token holder has a voice in the project's future direction.`,
            `${name} brings institutional-grade DeFi capabilities to the masses. By leveraging advanced automated market maker (AMM) algorithms, the protocol delivers optimal trading conditions across all market conditions. Users can stake ${ticker} tokens to earn rewards, participate in governance voting, and unlock exclusive features within the ecosystem.`
        ],
        ai: [
            `${name} (${ticker}) represents the convergence of artificial intelligence and blockchain technology. The platform leverages machine learning models to provide intelligent automation, predictive analytics, and autonomous decision-making for Web3 applications. By combining AI capabilities with decentralized infrastructure, ${name} creates a new paradigm of smart, self-evolving protocols.`,
            `At the heart of ${name} is a sophisticated AI engine that processes vast amounts of on-chain and off-chain data to deliver actionable insights. The ${ticker} token powers the network, enabling holders to access premium AI features, participate in model governance, and earn rewards for contributing to the ecosystem's growth.`
        ],
        nft: [
            `${name} (${ticker}) is the ultimate platform for digital collectibles and NFT innovation. The ecosystem provides artists, creators, and collectors with powerful tools to mint, trade, and showcase their digital assets. With zero-gas minting, cross-chain compatibility, and innovative curation features, ${name} democratizes access to the NFT space.`,
            `Discover a new world of digital ownership with ${name}. The ${ticker} token serves as the backbone of the marketplace, enabling holders to access exclusive drops, participate in curation governance, and earn rewards from marketplace activity. Join thousands of collectors in building the future of digital art.`
        ],
        gaming: [
            `${name} (${ticker}) revolutionizes gaming by integrating blockchain rewards with engaging gameplay. Players earn ${ticker} tokens through gameplay achievements, competitive battles, and community participation. The ecosystem features NFT items, tournaments, and a vibrant economy where skill and strategy are rewarded.`,
            `Step into the metaverse with ${name}. This innovative gaming platform combines traditional gaming mechanics with blockchain incentives, creating an experience where players truly own their in-game assets. The ${ticker} token powers the economy, enabling trading, staking, and governance of the game's future development.`
        ],
        social: [
            `${name} (${ticker}) empowers communities to organize, govern, and grow together on-chain. The platform provides tools for decentralized decision-making, resource allocation, and community coordination. With ${name}, DAOs become more accessible, efficient, and truly representative of their members' interests.`,
            `Building a stronger decentralized future through ${name}. The ${ticker} token enables community members to vote on proposals, allocate treasury funds, and shape the direction of the protocol. Experience governance that actually works, with quadratic voting, conviction voting, and delegation mechanisms.`
        ],
        infrastructure: [
            `${name} (${ticker}) delivers enterprise-grade infrastructure for the Web3 ecosystem. The platform provides reliable RPC endpoints, indexing services, and data solutions that power decentralized applications at scale. Developers trust ${name} for its uptime, performance, and comprehensive API coverage.`,
            `The backbone of Web3 infrastructure is here with ${name}. By providing essential services like on-chain data indexing, event streaming, and historical data queries, ${name} enables developers to build faster and smarter. The ${ticker} token powers the network, rewarding node operators and ensuring service quality.`
        ],
        tools: [
            `${name} (${ticker}) is the comprehensive toolkit that every Web3 developer needs. From smart contract templates to testing frameworks, from deployment scripts to monitoring dashboards, ${name} streamlines the entire development workflow. Ship faster with battle-tested utilities.`,
            `Developer productivity meets blockchain innovation in ${name}. The ${ticker} token unlocks premium features, grants access to private repositories, and provides governance rights over the toolset roadmap. Join thousands of developers building the future of Web3 with ${name}.`
        ],
        meme: [
            `${name} (${ticker}) is the meme token that brings joy, community, and potentially moon-sized gains to the crypto space. Born from internet culture and fueled by a passionate community, ${name} represents the fun and accessible side of cryptocurrency. HODL ${ticker} and join the movement!`,
            `Welcome to ${name}, where memes meet moonshots. The ${ticker} token embodies the spirit of crypto: community, fun, and the dream of financial freedom. Diamond hands earn rewards, and every holder is part of something bigger than themselves.`
        ]
    };

    const categoryDescriptions = descriptions[category] || descriptions.tools;
    return categoryDescriptions.join(' ');
}

/**
 * Generates token identity (name, ticker, description) based on repository analysis.
 * 
 * @param input - The input containing repository analysis
 * @returns Promise resolving to identity output with name, ticker, and description
 * 
 * @example
 * ```typescript
 * const identity = await generateIdentity({
 *   repoAnalysis: {
 *     repoName: "my-awesome-project",
 *     description: "A decentralized exchange",
 *     language: "TypeScript",
 *     // ... other fields
 *   }
 * });
 * console.log(identity.name); // e.g., "SWAPPRO"
 * console.log(identity.ticker); // e.g., "SWAP"
 * console.log(identity.description); // Full token description
 * ```
 */
export async function generateIdentity(input: IdentityInput): Promise<IdentityOutput> {
    const analysis = input.repoAnalysis;

    // Detect project category
    const category = detectCategory(analysis);

    // Generate components
    const name = generateName(analysis, category);
    const ticker = generateTicker(analysis.repoName, category);
    const tagline = generateTagline(analysis, category);
    const description = generateDescription(analysis, category, name, ticker);

    // Generate name reasoning
    const nameReasoning = `The name "${name}" was derived from analyzing the project as a ${category} category. The ticker "${ticker}" was chosen to be memorable, readable, and aligned with the project's core functionality.`;

    return {
        name,
        ticker,
        tagline,
        description,
        nameReasoning
    };
}
