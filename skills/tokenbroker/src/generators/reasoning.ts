/**
 * Reasoning Generator
 * 
 * Generates the "Investment Thesis" - explains why this token should exist.
 */

import { RepoAnalysis } from './types.js';

/**
 * Input interface for reasoning generation
 */
export interface ReasoningInput {
    /** Repository analysis data */
    repoAnalysis: RepoAnalysis;
    /** Token identity (name, ticker) */
    identity: {
        name: string;
        ticker: string;
        description: string;
    };
}

/**
 * Output interface for reasoning generation
 */
export interface ReasoningOutput {
    /** The main investment thesis */
    investmentThesis: string;
    /** Problem statement the project solves */
    problemStatement: string;
    /** Solution approach */
    solution: string;
    /** Market opportunity */
    marketOpportunity: string;
    /** Competitive advantage */
    competitiveAdvantage: string;
    /** Token utility rationale */
    tokenUtilityRationale: string;
    /** Long-term vision */
    vision: string;
}

/**
 * Problem statement templates by category
 */
const PROBLEM_TEMPLATES: Record<string, string[]> = {
    defi: [
        "Users face fragmented liquidity and inefficient trading execution across decentralized exchanges, leading to slippage and missed opportunities.",
        "Traditional DeFi protocols often suffer from high barriers to entry, complex interfaces, and unreliable oracle data, limiting mainstream adoption.",
        "Yield generation opportunities remain scattered and inaccessible, forcing users to constantly monitor multiple protocols and sacrifice security for returns."
    ],
    ai: [
        "AI development and deployment remains centralized, with users unable to access or profit from valuable machine learning models.",
        "On-chain AI agents lack the infrastructure to autonomously execute complex strategies while maintaining transparency and trustlessness.",
        "The potential of AI in blockchain ecosystems remains largely untapped, with no robust framework for AI-powered governance or automation."
    ],
    nft: [
        "NFT marketplaces suffer from high gas fees, poor discoverability, and limited creator monetization tools, stifling digital creativity.",
        "Digital collectors struggle with verification challenges and lack of cross-chain compatibility for their valuable assets.",
        "The NFT ecosystem lacks meaningful utility beyond speculation, leaving holders without real-world applications for their digital collections."
    ],
    gaming: [
        "Traditional gaming economies are closed and exploitative, with players unable to truly own or monetize their in-game achievements.",
        "Play-to-earn models often fail to sustain long-term value, leaving early adopters with worthless tokens and abandoned games.",
        "Gamers lack genuine agency in game development decisions, with studios maintaining complete control over game economics and features."
    ],
    social: [
        "Online communities lack true ownership and governance over their collective resources and decision-making processes.",
        "DAOs suffer from low participation, complex governance mechanisms, and an inability to coordinate effectively at scale.",
        "Content creators receive minimal compensation from platforms that extract value from their communities without sharing rewards."
    ],
    infrastructure: [
        "Web3 developers face unreliable infrastructure with downtime, data inconsistencies, and limited RPC coverage across chains.",
        "On-chain data remains fragmented and difficult to access, hindering the development of sophisticated decentralized applications.",
        "Validators and node operators lack proper incentive structures to ensure network security and reliability at scale."
    ],
    tools: [
        "Web3 development remains unnecessarily complex, with developers wasting time on repetitive tasks and incompatible toolchains.",
        "Building and deploying decentralized applications requires integrating dozens of disparate services, increasing costs and reducing reliability.",
        "Developers lack comprehensive testing and monitoring tools, leading to vulnerabilities and downtime in production applications."
    ],
    meme: [
        "The crypto space needs projects that bring community joy and accessible entry points for new participants.",
        "Retail investors often feel excluded from high-level DeFi strategies and need fun, engaging ways to participate in the ecosystem.",
        "Community-driven movements have historically created significant value, but lack structured mechanisms to capture and distribute it."
    ]
};

/**
 * Solution templates by category
 */
const SOLUTION_TEMPLATES: Record<string, string[]> = {
    defi: [
        "The protocol provides a unified, efficient trading environment with concentrated liquidity and minimal slippage.",
        "By leveraging smart contract automation and verified oracle feeds, the platform delivers institutional-grade DeFi security.",
        "Users can access diverse yield strategies through a simple interface that abstracts away complexity while maintaining full control."
    ],
    ai: [
        "The platform democratizes access to advanced AI models through a decentralized network of node operators and model providers.",
        "AI agents can autonomously manage treasury positions, execute trading strategies, and participate in governance with full transparency.",
        "The ecosystem creates a marketplace for AI capabilities, allowing developers to monetize models and users to access cutting-edge intelligence."
    ],
    nft: [
        "The marketplace leverages layer-2 solutions to eliminate gas fees while maintaining Ethereum security and cross-chain compatibility.",
        "Advanced curation algorithms and social features help collectors discover rare gems and verify authenticity programmatically.",
        "NFT holders gain access to real-world utility, including licensing agreements, merchandise discounts, and exclusive experiences."
    ],
    gaming: [
        "Players earn true ownership of in-game assets as tradeable NFTs with real economic value outside the game ecosystem.",
        "The tokenomics model ensures sustainable rewards through a balanced combination of gameplay mechanics and treasury reserves.",
        "Community governance allows players to vote on game updates, economic parameters, and new feature development."
    ],
    social: [
        "The platform provides intuitive governance tools that increase participation and enable efficient, transparent decision-making.",
        "Token-based incentives reward active contributors while aligning individual interests with collective community goals.",
        "Decentralized coordination mechanisms enable communities to pool resources, execute complex initiatives, and share in the value created."
    ],
    infrastructure: [
        "Enterprise-grade infrastructure delivers reliable, low-latency RPC endpoints and comprehensive data indexing across all major chains.",
        "A distributed network of operators ensures redundancy and uptime, with economic incentives that guarantee service quality.",
        "Developers gain access to powerful APIs and SDKs that abstract away chain complexity, enabling faster iteration and deployment."
    ],
    tools: [
        "The comprehensive toolkit streamlines every aspect of Web3 development, from smart contract templates to production monitoring.",
        "Battle-tested utilities and automated testing frameworks reduce vulnerabilities and accelerate time-to-market for dApps.",
        "Integrated dashboards provide real-time insights into application performance, user behavior, and security metrics."
    ],
    meme: [
        "The project combines viral community culture with sustainable tokenomics designed for long-term growth and holder rewards.",
        "A fun, accessible entry point welcomes new participants to crypto while building a passionate, engaged community.",
        "The token serves as a community badge, granting access to exclusive events, merchandise, and future project opportunities."
    ]
};

/**
 * Value proposition templates by category
 */
const VALUE_PROPOSITION_TEMPLATES: Record<string, string[]> = {
    defi: [
        "Token holders gain preferential access to new pools, reduced fees, and enhanced yield opportunities through staking incentives.",
        "Governance rights allow the community to steer protocol development, fee structures, and treasury allocation.",
        "The token captures protocol revenue, creating sustainable buyback and burn mechanisms that benefit long-term holders."
    ],
    ai: [
        "Token holders access premium AI features, priority model inference, and early access to new capabilities.",
        "AI model providers earn tokens for contributing compute and improving model accuracy, creating a self-improving ecosystem.",
        "Governance tokens enable the community to shape AI ethics, model parameters, and resource allocation priorities."
    ],
    nft: [
        "Token holders receive discounts on marketplace fees, early access to exclusive drops, and voting rights on curation policies.",
        "Creators earn royalties automatically through smart contracts, ensuring consistent revenue from secondary sales.",
        "Staking tokens unlocks premium features like advanced analytics, portfolio tracking, and exclusive gallery access."
    ],
    gaming: [
        "Players stake tokens to access premium content, participate in tournaments, and earn rewards based on skill and engagement.",
        "Token holdings provide governance rights over game economics, including token issuance, reward rates, and new feature prioritization.",
        "Early supporters receive exclusiveNFT drops, founder status, and special in-game benefits that recognize their contribution."
    ],
    social: [
        "Token holders unlock advanced governance features, proposal creation rights, and delegated voting power.",
        "Active community members earn tokens through participation, content creation, and successful initiative execution.",
        "The token enables treasury participation, allowing holders to benefit from successful community investments and partnerships."
    ],
    infrastructure: [
        "Node operators stake tokens to provide services, earning rewards proportional to their contribution and reliability.",
        "Token holders gain access to premium infrastructure features, dedicated support, and early access to new chain integrations.",
        "Governance tokens enable the community to prioritize protocol development, adjust fee structures, and fund ecosystem grants."
    ],
    tools: [
        "Developers unlock premium SDKs, priority support, and access to private repositories by holding tokens.",
        "Token holders influence the roadmap, voting on new features, integrations, and improvement priorities.",
        "Staking tokens grants extended API rate limits, advanced analytics, and exclusive training materials."
    ],
    meme: [
        "Holders gain access to an exclusive community of like-minded enthusiasts, with tokens serving as a membership badge.",
        "The token enables community-driven initiatives, including charitable donations, viral marketing campaigns, and event sponsorships.",
        "Long-term holders benefit from regular buyback programs, community rewards, and the naturally deflationary tokenomics."
    ]
};

/**
 * Vision statement templates by category
 */
const VISION_TEMPLATES: Record<string, string[]> = {
    defi: [
        "To become the dominant liquidity layer powering all decentralized trading across chains.",
        "A future where anyone can access institutional-grade financial services without intermediaries or barriers."
    ],
    ai: [
        "To create the first truly autonomous, self-governing AI that benefits all stakeholders in the ecosystem.",
        "A world where AI capabilities are democratized and controlled by the communities that create value."
    ],
    nft: [
        "To establish the premier destination for digital art, collectibles, and creative expression across all chains.",
        "A future where digital ownership is universal, verified, and accessible to creators and collectors worldwide."
    ],
    gaming: [
        "To pioneer a new era of player-owned gaming economies that genuinely reward skill and engagement.",
        "A metaverse where players truly own their achievements and participate in the governance of their virtual worlds."
    ],
    social: [
        "To enable the first truly decentralized, community-owned internet platforms that rival centralized giants.",
        "A future where communities control their destiny and capture the value they create together."
    ],
    infrastructure: [
        "To become the backbone of Web3, powering every major dApp with reliable, scalable infrastructure.",
        "A decentralized internet built on robust, incentivized infrastructure that no single entity can control."
    ],
    tools: [
        "To empower every developer to build world-class Web3 applications without barriers or complexity.",
        "A future where Web3 development is as accessible and productive as traditional software engineering."
    ],
    meme: [
        "To build the most engaged, passionate community in crypto history while creating lasting value for holders.",
        "A celebration of crypto culture that welcomes everyone to participate in the revolution."
    ]
};

/**
 * Target audience templates by category
 */
const AUDIENCE_TEMPLATES: Record<string, string[]> = {
    defi: [
        "DeFi natives, yield farmers, and institutional investors seeking reliable returns in decentralized markets.",
        "Traders who require deep liquidity, low slippage, and secure execution for their strategies."
    ],
    ai: [
        "AI enthusiasts, machine learning developers, and crypto innovators exploring the intersection of intelligence and blockchain.",
        "Investors seeking exposure to the growing AI sector through a transparent, community-governed platform."
    ],
    nft: [
        "Digital artists, collectors, and enthusiasts who value authenticity, ownership rights, and cross-chain compatibility.",
        "Creative professionals seeking new revenue streams and global exposure for their digital artwork."
    ],
    gaming: [
        "Gamers who want true ownership of their in-game assets and meaningful participation in game development.",
        "Play-to-earn enthusiasts seeking sustainable economic models and engaging gameplay experiences."
    ],
    social: [
        "DAO participants, community leaders, and governance enthusiasts building the future of decentralized organization.",
        "Crypto natives seeking meaningful ways to coordinate and contribute to community success."
    ],
    infrastructure: [
        "Web3 developers requiring reliable, scalable infrastructure for production applications.",
        "Projects seeking enterprise-grade data services, indexing solutions, and RPC coverage across chains."
    ],
    tools: [
        "Web3 developers and engineering teams building decentralized applications and smart contracts.",
        "Technical teams seeking productivity tools, testing frameworks, and monitoring solutions."
    ],
    meme: [
        "Retail crypto enthusiasts who value community, culture, and fun participation in the ecosystem.",
        "Newcomers seeking an accessible entry point into crypto with a welcoming, engaged community."
    ]
};

/**
 * Competitive advantage templates by category
 */
const ADVANTAGE_TEMPLATES: Record<string, string[]> = {
    defi: [
        "Concentrated liquidity algorithms deliver better rates than traditional AMMs while maintaining capital efficiency.",
        "Verified oracle integrations and audited smart contracts provide institutional-grade security and reliability."
    ],
    ai: [
        "On-chain verification ensures AI model integrity and enables trustless verification of model outputs.",
        "Decentralized compute network eliminates single points of failure while scaling with demand."
    ],
    nft: [
        "Zero-gas minting and cross-chain compatibility eliminate barriers for creators and collectors.",
        "Proprietary verification algorithms ensure authenticity and provenance for all digital assets."
    ],
    gaming: [
        "Player-owned economies with transparent, auditable tokenomics that prioritize sustainability.",
        "Engaging gameplay mechanics that reward skill and strategy, not just time investment."
    ],
    social: [
        "Intuitive governance interfaces that dramatically increase participation compared to traditional DAOs.",
        "Proven coordination mechanisms that enable efficient resource allocation and community execution."
    ],
    infrastructure: [
        "99.99% uptime guarantee backed by economic incentives and distributed operator network.",
        "Comprehensive API coverage and dedicated support for enterprise-grade integration."
    ],
    tools: [
        "Battle-tested utilities used by top projects, ensuring reliability and security for production systems.",
        "Developer-first design philosophy that prioritizes productivity, documentation, and community support."
    ],
    meme: [
        "Authentic community culture built organically, not manufactured through influencer marketing.",
        "Sustainable tokenomics with real utility beyond speculation, ensuring long-term holder value."
    ]
};

/**
 * Market opportunity templates by category
 */
const MARKET_TEMPLATES: Record<string, string[]> = {
    defi: [
        "The DeFi market represents over $50 billion in total value locked with continued institutional adoption.",
        "Growing demand for decentralized trading solutions that combine security, efficiency, and user experience."
    ],
    ai: [
        "The AI sector is projected to contribute trillions to global GDP, with crypto-native AI remaining largely untapped.",
        "Increasing demand for autonomous, on-chain AI agents that can manage treasury and execute strategies."
    ],
    nft: [
        "NFT trading volumes continue to grow, with institutional interest in digital collectibles and real-world asset tokenization.",
        "The creator economy represents a $100B+ market opportunity for platforms enabling direct creator monetization."
    ],
    gaming: [
        "The gaming market exceeds $200 billion annually, with blockchain gaming representing a rapidly growing segment.",
        "Play-to-earn models attract millions of players in emerging markets seeking economic opportunity."
    ],
    social: [
        "DAO treasury management represents a multi-billion dollar opportunity with thousands of active organizations.",
        "Content creator platforms generate billions in revenue, but creators receive minimal compensation from platforms."
    ],
    infrastructure: [
        "RPC and indexing services represent a critical, growing market as Web3 adoption expands.",
        "Enterprise demand for reliable infrastructure increases as major institutions enter the space."
    ],
    tools: [
        "The developer tools market continues to grow as more teams build for Web3 and blockchain.",
        "Security and monitoring solutions are increasingly critical as DeFi grows and attracts institutional capital."
    ],
    meme: [
        "Community-driven tokens have created billions in market value, demonstrating the power of engaged communities.",
        "Retail crypto participation continues to grow, with demand for fun, accessible entry points."
    ]
};

/**
 * Detect project category based on repository analysis
 */
function detectCategory(analysis: RepoAnalysis): string {
    const combinedText = `
        ${analysis.repoName} ${analysis.description} ${analysis.readme} 
        ${analysis.features.join(' ')} ${analysis.techStack.join(' ')}
    `.toLowerCase();

    const categories: Record<string, string[]> = {
        defi: ['defi', 'decentralized', 'exchange', 'swap', 'liquidity', 'pool', 'yield', 'farm', 'staking', 'bridge', 'oracle', 'amm', 'trading', 'arbitrage', 'lending', 'borrowing', 'stablecoin', 'curve', 'uniswap', 'aave', 'compound'],
        ai: ['ai', 'ml', 'machine', 'learning', 'neural', 'gpt', 'llm', 'model', 'inference', 'training', 'agent', 'chatbot', 'cognitive', 'autonomous', 'intelligence', 'prediction', 'classifier'],
        nft: ['nft', 'collectible', 'art', 'digital', 'mint', 'marketplace', 'gallery', 'cryptoart', 'pixel', 'avatar', 'profile', 'tokenization', 'edition', 'generative'],
        gaming: ['game', 'gaming', 'play', 'guild', 'quest', 'loot', 'rpg', 'metaverse', 'virtual', 'world', 'character', 'pvp', 'pve', 'adventure', 'arcade', 'strategy', 'gamefi'],
        social: ['social', 'community', 'chat', 'messaging', 'forum', 'dao', 'governance', 'voting', 'proposal', 'collaboration', 'coordination', 'tribe', 'network'],
        infrastructure: ['infrastructure', 'node', 'validator', 'rpc', 'indexer', 'data', 'storage', 'compute', 'network', 'protocol', 'layer', 'sdk', 'api', 'middleware', 'backend'],
        tools: ['tool', 'utility', 'cli', 'dashboard', 'analytics', 'monitor', 'alert', 'notification', 'integration', 'library', 'framework', 'template', 'scaffold', 'boilerplate', 'generator'],
        meme: ['meme', 'fun', 'joke', 'pepe', 'dog', 'cat', 'bunny', 'frog', 'moon', 'rocket', 'doge', 'shib', 'inu', 'wojak', 'chad', 'diamond', 'hands', 'wagmi', 'wen', 'fair']
    };

    let maxScore = 0;
    let detectedCategory = 'tools';

    for (const [category, keywords] of Object.entries(categories)) {
        let score = 0;
        for (const keyword of keywords) {
            if (combinedText.includes(keyword.trim())) {
                score += 1;
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
 * Select a random item from an array
 */
function randomItem<T>(arr: T[]): T {
    return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Extract key pain points from repository analysis
 */
function extractPainPoints(analysis: RepoAnalysis, category: string): string[] {
    const painPoints: string[] = [];
    const combinedText = `${analysis.description} ${analysis.readme}`.toLowerCase();

    // Common pain point indicators
    const painIndicators = [
        { keywords: ['problem', 'issue', 'challenge', 'difficult', 'complex', 'broken'], context: 'complexity' },
        { keywords: ['expensive', 'costly', 'fee', 'gas'], context: 'cost' },
        { keywords: ['slow', 'latency', 'performance', 'speed'], context: 'performance' },
        { keywords: ['centralized', 'single point', 'reliance'], context: 'centralization' },
        { keywords: ['insecure', 'vulnerability', 'exploit', 'risk'], context: 'security' },
        { keywords: ['fragmented', 'scattered', 'disconnected'], context: 'fragmentation' },
        { keywords: ['inaccessible', 'barrier', '门槛', '门槛'], context: 'accessibility' }
    ];

    for (const indicator of painIndicators) {
        if (indicator.keywords.some(kw => combinedText.includes(kw))) {
            painPoints.push(indicator.context);
        }
    }

    // Category-specific pain points
    if (category === 'defi') {
        if (!painPoints.includes('fragmentation')) {
            painPoints.push('fragmented DeFi landscape');
        }
        if (!painPoints.includes('complexity')) {
            painPoints.push('complex DeFi interfaces');
        }
    } else if (category === 'ai') {
        if (!painPoints.includes('centralization')) {
            painPoints.push('centralized AI control');
        }
        if (!painPoints.includes('accessibility')) {
            painPoints.push('limited AI access');
        }
    } else if (category === 'gaming') {
        if (!painPoints.includes('ownership')) {
            painPoints.push('lack of true ownership');
        }
    } else if (category === 'tools') {
        if (!painPoints.includes('complexity')) {
            painPoints.push('development complexity');
        }
    }

    return painPoints.length > 0 ? painPoints : ['inefficiency', 'fragmentation'];
}

/**
 * Generate the main investment thesis
 */
function generateInvestmentThesis(
    analysis: RepoAnalysis,
    category: string,
    name: string,
    ticker: string
): string {
    const activityIndicator = analysis.isActive ? 'actively developed' : 'established';
    const tractionIndicator = analysis.stars > 100 ? 'growing' : 'emerging';
    const thesisTemplates = [
        `${name} (${ticker}) represents a ${tractionIndicator} opportunity in the ${category} space, addressing fundamental ${activityIndicator} with a novel approach that combines technical innovation with sustainable tokenomics.`,
        `The ${ticker} token captures value from ${analysis.repoName}'s mission to revolutionize ${category}, providing holders with both utility and governance rights in a rapidly expanding market.`,
        `${name} is positioned to lead the next wave of ${category} innovation, with the ${ticker} token serving as the foundation for a community-driven ecosystem that rewards early adopters.`
    ];

    return randomItem(thesisTemplates);
}

/**
 * Generate the problem statement
 */
function generateProblemStatement(analysis: RepoAnalysis, category: string): string {
    const painPoints = extractPainPoints(analysis, category);
    const templates = PROBLEM_TEMPLATES[category] || PROBLEM_TEMPLATES.tools;
    const baseProblem = randomItem(templates);

    return painPoints.length > 0
        ? `${baseProblem} The ecosystem struggles with ${painPoints.slice(0, 2).join(' and ')}, creating significant friction for users and limiting adoption.`
        : baseProblem;
}

/**
 * Generate the solution section
 */
function generateSolution(analysis: RepoAnalysis, category: string, name: string): string {
    const templates = SOLUTION_TEMPLATES[category] || SOLUTION_TEMPLATES.tools;
    const baseSolution = randomItem(templates);

    // Customize based on activity
    if (analysis.isActive && analysis.recentCommits > 10) {
        return `${baseSolution} With an active development team and committed community, ${name} is well-positioned to execute on this vision and deliver continuous improvements.`;
    }

    return baseSolution;
}

/**
 * Generate value proposition
 */
function generateValueProposition(category: string, ticker: string): string {
    const templates = VALUE_PROPOSITION_TEMPLATES[category] || VALUE_PROPOSITION_TEMPLATES.tools;
    return randomItem(templates).replace('tokens', ticker).replace('Token', ticker);
}

/**
 * Generate vision statement
 */
function generateVision(category: string): string {
    const templates = VISION_TEMPLATES[category] || VISION_TEMPLATES.tools;
    return randomItem(templates);
}

/**
 * Generate target audience
 */
function generateTargetAudience(category: string): string {
    const templates = AUDIENCE_TEMPLATES[category] || AUDIENCE_TEMPLATES.tools;
    return randomItem(templates);
}

/**
 * Generate competitive advantage
 */
function generateCompetitiveAdvantage(analysis: RepoAnalysis, category: string, name: string): string {
    const templates = ADVANTAGE_TEMPLATES[category] || ADVANTAGE_TEMPLATES.tools;
    const baseAdvantage = randomItem(templates);

    // Factor in project metrics
    if (analysis.stars > 500) {
        return `${baseAdvantage} The project's strong community with ${analysis.stars}+ GitHub stars demonstrates proven traction and market validation.`;
    }
    if (analysis.contributors > 5) {
        return `${baseAdvantage} A diverse contributor base of ${analysis.contributors} developers ensures robust development and continuous innovation.`;
    }

    return baseAdvantage;
}

/**
 * Generate market opportunity
 */
function generateMarketOpportunity(category: string): string {
    const templates = MARKET_TEMPLATES[category] || MARKET_TEMPLATES.tools;
    return randomItem(templates);
}

/**
 * Generate token utility rationale
 */
function generateTokenUtilityRationale(category: string, ticker: string): string {
    const templates = VALUE_PROPOSITION_TEMPLATES[category] || VALUE_PROPOSITION_TEMPLATES.tools;
    const rationale = randomItem(templates);

    return `The ${ticker} token serves multiple functions: it enables governance participation, provides access to premium features, and captures value generated by the protocol. This multi-faceted utility creates sustained demand while aligning holder interests with long-term ecosystem success.`;
}

/**
 * Generates the investment thesis and reasoning for why this token should exist.
 * 
 * @param input - The input containing repository analysis and token identity
 * @returns Promise resolving to reasoning output with investment thesis and supporting points
 * 
 * @example
 * ```typescript
 * const reasoning = await generateReasoning({
 *   repoAnalysis: { /* repo data * / },
 *   identity: { name: "AweSome", ticker: "AWE", description: "..." }
 * });
 * console.log(reasoning.investmentThesis);
 * ```
 */
export async function generateReasoning(input: ReasoningInput): Promise<ReasoningOutput> {
    const { repoAnalysis, identity } = input;
    const { name, ticker } = identity;

    // Detect project category
    const category = detectCategory(repoAnalysis);

    // Generate all components
    const investmentThesis = generateInvestmentThesis(repoAnalysis, category, name, ticker);
    const problemStatement = generateProblemStatement(repoAnalysis, category);
    const solution = generateSolution(repoAnalysis, category, name);
    const marketOpportunity = generateMarketOpportunity(category);
    const competitiveAdvantage = generateCompetitiveAdvantage(repoAnalysis, category, name);
    const tokenUtilityRationale = generateTokenUtilityRationale(category, ticker);
    const vision = generateVision(category);

    return {
        investmentThesis,
        problemStatement,
        solution,
        marketOpportunity,
        competitiveAdvantage,
        tokenUtilityRationale,
        vision
    };
}
