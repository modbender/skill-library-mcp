/**
 * Bloom Identity Card Generator - OpenClaw Skill v2
 *
 * Enhanced version with:
 * - Permission handling
 * - Manual Q&A fallback
 * - Focus on Twitter/X integration
 * - Graceful degradation
 */

import { PersonalityAnalyzer } from './analyzers/personality-analyzer';
import { EnhancedDataCollector } from './analyzers/data-collector-enhanced';
import { ManualQAFallback, ManualAnswer } from './analyzers/manual-qa-fallback';
import { CategoryMapper } from './analyzers/category-mapper';
import { AgentWallet, AgentWalletInfo } from './blockchain/agent-wallet';
import { walletStorage } from './blockchain/wallet-storage';
import { mintIdentitySbt } from './blockchain/identity-sbt';
import { TwitterShare, createTwitterShare } from './integrations/twitter-share';
import { ClawHubClient, createClawHubClient } from './integrations/clawhub-client';
import { ClaudeCodeClient, createClaudeCodeClient } from './integrations/claude-code-client';
import { GitHubRecommendations } from './github-recommendations';
import { PersonalityType } from './types/personality';

// Re-export PersonalityType for backwards compatibility
export { PersonalityType };

export interface IdentityData {
  personalityType: PersonalityType;
  customTagline: string;
  customDescription: string;
  mainCategories: string[];
  subCategories: string[];
}

export interface SkillRecommendation {
  skillId: string;
  skillName: string;
  description: string;
  url: string;
  categories: string[];
  matchScore: number;
  creator?: string;
  creatorUserId?: number | string;
  source?: 'ClawHub' | 'GitHub';
  stars?: number;
  language?: string;
}

/**
 * Execution mode
 */
export enum ExecutionMode {
  AUTO = 'auto',           // Try data collection, fallback to Q&A if insufficient
  MANUAL = 'manual',       // Skip data collection, go straight to Q&A
  DATA_ONLY = 'data_only', // Only use data collection, fail if insufficient
}

/**
 * Main Bloom Identity Skill v2
 */
export class BloomIdentitySkillV2 {
  private personalityAnalyzer: PersonalityAnalyzer;
  private dataCollector: EnhancedDataCollector;
  private manualQA: ManualQAFallback;
  private categoryMapper: CategoryMapper;
  private agentWallet: AgentWallet | null = null;
  private twitterShare: TwitterShare;
  private clawHubClient: ClawHubClient;
  private claudeCodeClient: ClaudeCodeClient;
  private githubRecommendations: GitHubRecommendations;

  constructor() {
    this.personalityAnalyzer = new PersonalityAnalyzer();
    this.dataCollector = new EnhancedDataCollector();
    this.manualQA = new ManualQAFallback();
    this.categoryMapper = new CategoryMapper();
    this.twitterShare = createTwitterShare();
    this.clawHubClient = createClawHubClient();
    this.claudeCodeClient = createClaudeCodeClient();
    this.githubRecommendations = new GitHubRecommendations(process.env.GITHUB_TOKEN);
  }

  /**
   * Initialize agent wallet (one-time setup)
   *
   * ⭐ Creates per-user wallet using userId
   */
  private async initializeAgentWallet(userId: string): Promise<AgentWalletInfo> {
    if (this.agentWallet) {
      return this.agentWallet.getWalletInfo();
    }

    console.log('🤖 Initializing agent wallet...');

    // Network priority: NETWORK env var > NODE_ENV-based > default to mainnet
    const network = (process.env.NETWORK as 'base-mainnet' | 'base-sepolia') ||
                   (process.env.NODE_ENV === 'production' ? 'base-mainnet' : 'base-sepolia');

    // ⭐ Pass userId for per-user wallet
    this.agentWallet = new AgentWallet({ userId, network });

    const walletInfo = await this.agentWallet.initialize();

    // Pre-register with Bloom Protocol (wallet address only, no identity data yet)
    try {
      const registration = await this.agentWallet.registerWithBloom('Bloom Skill Discovery Agent');
      console.log(`✅ Agent pre-registered with Bloom: userId ${registration.agentUserId}`);
      walletInfo.x402Endpoint = registration.x402Endpoint;
    } catch (error) {
      // Not critical - identity will be saved in Step 5 via agent-save fallback
      console.warn('⚠️ Bloom pre-registration skipped (identity will be saved later)');
    }

    return walletInfo;
  }

  /**
   * Main skill execution with intelligent fallback
   */
  async execute(
    userId: string,
    options?: {
      mode?: ExecutionMode;
      skipShare?: boolean; // Twitter share is optional
      manualAnswers?: ManualAnswer[]; // If already collected
      conversationText?: string; // ⭐ NEW: Direct conversation text from OpenClaw bot
      mintToBase?: boolean; // ⭐ Optional: mint SBT on Base
    }
  ): Promise<{
    success: boolean;
    mode: 'data' | 'manual' | 'hybrid';
    identityData?: IdentityData;
    agentWallet?: AgentWalletInfo;
    recommendations?: SkillRecommendation[];
    dashboardUrl?: string;
    shareUrl?: string;
    dataQuality?: number;
    dimensions?: {
      conviction: number;
      intuition: number;
      contribution: number;
    };
    actions?: {
      share?: {
        url: string;
        text: string;
        hashtags: string[];
      };
      save?: {
        prompt: string;
        registerUrl: string;
        loginUrl: string;
      };
      mint?: {
        contractAddress: string;
        tokenUri: string;
        txHash: string;
        network: string;
      };
    };
    error?: string;
    needsManualInput?: boolean;
    manualQuestions?: string;
  }> {
    try {
      console.log(`🎴 Generating Bloom Identity for user: ${userId}`);

      const mode = options?.mode || ExecutionMode.AUTO;

      // Step 1: Try data collection (unless manual mode)
      let identityData: IdentityData | null = null;
      let dataQuality = 0;
      let usedManualQA = false;
      let dimensions: { conviction: number; intuition: number; contribution: number } | undefined;
      let mintAction: { contractAddress: string; tokenUri: string; txHash: string; network: string } | undefined;

      if (mode !== ExecutionMode.MANUAL) {
        console.log('📊 Step 1: Attempting data collection...');

        // ⭐ NEW: If conversationText is provided, use it directly
        let userData;
        if (options?.conversationText) {
          console.log('✅ Using provided conversation text (OpenClaw bot context)');
          userData = await this.dataCollector.collectFromConversationText(
            userId,
            options.conversationText,
            { skipTwitter: options.skipShare }
          );
        } else {
          // Original: Collect from session files
          userData = await this.dataCollector.collect(userId, {
            // Default: Conversation + Twitter only (no wallet analysis)
          });
        }

        dataQuality = this.dataCollector.getDataQualityScore(userData);
        // Data quality is calculated but not displayed (cleaner output)
        console.log(`📊 Available sources: ${userData.sources.join(', ')}`);

        // ⭐ CRITICAL: Check if we have ANY real data (conversation OR Twitter)
        const hasConversation = userData.conversationMemory && userData.conversationMemory.messageCount > 0;
        const hasTwitter = userData.twitter && (userData.twitter.bio || userData.twitter.tweets.length > 0);

        if (!hasConversation && !hasTwitter) {
          console.log('⚠️  No conversation or Twitter data available');

          // In AUTO mode, fallback to manual Q&A
          if (mode === ExecutionMode.AUTO) {
            console.log('🔄 Falling back to manual Q&A (no data available)...');
            usedManualQA = true;
          } else {
            // DATA_ONLY mode - fail explicitly
            throw new Error('No conversation or Twitter data available and manual Q&A not enabled');
          }
        } else {
          // Check if we have sufficient data quality
          const hasSufficientData = this.dataCollector.hasSufficientData(userData);

          if (hasSufficientData) {
            console.log('✅ Sufficient data available, proceeding with AI analysis...');

            // Analyze personality from data
            const analysis = await this.personalityAnalyzer.analyze(userData);

            identityData = {
              personalityType: analysis.personalityType,
              customTagline: analysis.tagline,
              customDescription: analysis.description,
              // ⭐ Use detected categories from actual conversation data
              // Priority: What they talk about > personality-based defaults
              mainCategories: analysis.detectedCategories.length > 0
                ? analysis.detectedCategories
                : this.categoryMapper.getMainCategories(analysis.personalityType),
              subCategories: analysis.detectedInterests,
            };

            // ⭐ Capture 2x2 metrics
            dimensions = analysis.dimensions;

            console.log(`✅ Analysis complete: ${identityData.personalityType}`);
          } else {
            console.log('⚠️  Insufficient data quality for AI analysis');

            // In AUTO mode, fallback to manual Q&A
            if (mode === ExecutionMode.AUTO) {
              console.log('🔄 Falling back to manual Q&A...');
              usedManualQA = true;
            } else {
              // DATA_ONLY mode - fail
              throw new Error('Insufficient data and manual Q&A not enabled');
            }
          }
        }
      } else {
        // MANUAL mode - go straight to Q&A
        console.log('📝 Manual mode enabled, skipping data collection');
        usedManualQA = true;
      }

      // Step 2: Manual Q&A if needed
      if (usedManualQA) {
        // If we don't have answers yet, request them from user
        if (!options?.manualAnswers) {
          console.log('❓ Manual input required from user');
          return {
            success: false,
            mode: 'manual',
            needsManualInput: true,
            manualQuestions: this.manualQA.formatQuestionsForUser(),
          };
        }

        console.log('🤔 Analyzing manual Q&A responses...');
        const manualResult = await this.manualQA.analyze(options.manualAnswers);

        identityData = {
          personalityType: manualResult.personalityType,
          customTagline: manualResult.tagline,
          customDescription: manualResult.description,
          mainCategories: manualResult.mainCategories,
          subCategories: manualResult.subCategories,
        };

        dataQuality = manualResult.confidence;
        console.log(`✅ Manual analysis complete: ${identityData.personalityType}`);
      }

      // Step 3: Recommend OpenClaw Skills ⭐ NEW
      console.log('🔍 Step 3: Finding matching OpenClaw Skills...');
      const recommendations = await this.recommendSkills(identityData!);
      console.log(`✅ Found ${recommendations.length} matching skills`);

      // Step 4: Initialize Agent Wallet ⭐ Per-User Wallet
      console.log('🤖 Step 4: Initializing Agent Wallet...');
      const agentWallet = await this.initializeAgentWallet(userId);  // ⭐ Pass userId
      console.log(`✅ Agent wallet deployed on ${agentWallet.network}`);

      // Step 5: Register agent and save identity card with Bloom
      // Try wallet-based registration first, fall back to wallet-free save
      let dashboardUrl: string | undefined;
      let agentUserId: number | undefined;

      const identityPayload = {
        personalityType: identityData!.personalityType,
        tagline: identityData!.customTagline,
        description: identityData!.customDescription,
        mainCategories: identityData!.mainCategories,
        subCategories: identityData!.subCategories,
        confidence: dataQuality,
        mode: (usedManualQA ? 'manual' : 'data') as 'data' | 'manual',
        dimensions,
        recommendations,
      };

      try {
        console.log('📝 Step 5: Registering agent with Bloom...');

        // Try wallet-based registration (with signature)
        const registration = await this.agentWallet!.registerWithBloom(
          'Bloom Skill Discovery Agent',
          identityPayload,
        );
        agentUserId = registration.agentUserId;
        console.log(`✅ Agent registered with wallet! User ID: ${agentUserId}`);
      } catch (walletError) {
        console.warn('⚠️  Wallet-based registration failed, trying wallet-free save...');
        console.warn('   Error:', walletError instanceof Error ? walletError.message : walletError);

        try {
          // Fallback: save without wallet signature
          const saveResult = await this.agentWallet!.saveIdentityWithBloom(
            'Bloom Skill Discovery Agent',
            identityPayload,
          );
          agentUserId = saveResult.agentUserId;
          console.log(`✅ Agent identity saved (wallet-free)! User ID: ${agentUserId}`);
        } catch (saveError) {
          console.error('❌ Both registration methods failed:', saveError);
        }
      }

      if (agentUserId) {
        const baseUrl = process.env.DASHBOARD_URL || 'https://preflight.bloomprotocol.ai';
        const cacheBust = Date.now();
        dashboardUrl = `${baseUrl}/agents/${agentUserId}?v=${cacheBust}`;
        console.log(`✅ Public URL created: ${dashboardUrl}`);
      }

      // Step 6: Twitter share (DISABLED - image embedding issues)
      // TODO: Re-enable when we can properly embed card images in Twitter
      let shareUrl: string | undefined;
      // if (!options?.skipShare) {
      //   try {
      //     console.log('📢 Step 6: Generating Twitter share link...');
      //     shareUrl = await this.twitterShare.share({
      //       userId,
      //       personalityType: identityData!.personalityType,
      //       recommendations: recommendations.slice(0, 3).map(r => ({
      //         skillName: r.skillName,
      //         matchScore: r.matchScore,
      //       })),
      //       agentWallet: undefined,
      //     });
      //     console.log(`✅ Share link ready`);
      //   } catch (error) {
      //     console.warn('⚠️  Twitter share link generation failed (skipping):', error);
      //   }
      // }

      // Success!
      console.log('🎉 Bloom Identity generation complete!');

      // Prepare share data for frontend buttons
      const shareData = dashboardUrl ? {
        url: dashboardUrl,
        text: `Just discovered my Bloom Identity: ${identityData!.personalityType}! 🌸\n\nCheck out my personalized skill recommendations on @bloomprotocol 🚀`,
        hashtags: ['BloomProtocol', 'Web3Identity', 'OpenClaw'],
      } : undefined;

      // Optional: Mint SBT on Base
      if (options?.mintToBase) {
        try {
          const contractAddress = process.env.SBT_CONTRACT_ADDRESS as `0x${string}` | undefined;
          if (!contractAddress) {
            throw new Error('SBT_CONTRACT_ADDRESS not set');
          }

          const walletRecord = await walletStorage.getUserWallet(userId);
          if (!walletRecord?.privateKey) {
            throw new Error('No local private key available for minting');
          }

          const tokenUri = this.buildTokenUri(identityData!, agentWallet, dashboardUrl);
          const txHash = await mintIdentitySbt({
            contractAddress,
            to: agentWallet.address as `0x${string}`,
            tokenUri,
            network: agentWallet.network as 'base-mainnet' | 'base-sepolia',
            privateKey: walletRecord.privateKey as `0x${string}`,
          });

          mintAction = {
            contractAddress,
            tokenUri,
            txHash,
            network: agentWallet.network,
          };
        } catch (error) {
          console.warn('⚠️  SBT mint failed (skipping):', error);
        }
      }

      return {
        success: true,
        mode: usedManualQA ? 'manual' : 'data',
        identityData: identityData!,
        agentWallet,
        recommendations,
        dashboardUrl,
        shareUrl,
        dataQuality,
        dimensions, // ⭐ Include 2x2 metrics in result
        // ⭐ Frontend action buttons data
        actions: {
          share: shareData, // For "Share on X" button
          save: dashboardUrl ? {
            // For "Save to Collection" button
            prompt: 'Save this card to your Bloom collection',
            registerUrl: `${process.env.DASHBOARD_URL || 'https://preflight.bloomprotocol.ai'}/register?return=${encodeURIComponent(dashboardUrl)}`,
            loginUrl: `${process.env.DASHBOARD_URL || 'https://preflight.bloomprotocol.ai'}/login?return=${encodeURIComponent(dashboardUrl)}`,
          } : undefined,
          mint: mintAction,
        },
      };
    } catch (error) {
      console.error('❌ Error generating Bloom Identity:', error);
      return {
        success: false,
        mode: 'data',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private buildTokenUri(identity: IdentityData, wallet: AgentWalletInfo, dashboardUrl?: string): string {
    const metadata = {
      name: `Bloom Identity — ${identity.personalityType}`,
      description: identity.customDescription,
      image: dashboardUrl || undefined,
      attributes: [
        { trait_type: 'Personality', value: identity.personalityType },
        { trait_type: 'Main Categories', value: identity.mainCategories.join(', ') },
        { trait_type: 'Sub Categories', value: identity.subCategories.join(', ') },
      ],
      properties: {
        wallet: wallet.address,
        network: wallet.network,
        dashboardUrl,
      },
    };

    const json = JSON.stringify(metadata);
    const base64 = Buffer.from(json).toString('base64');
    return `data:application/json;base64,${base64}`;
  }

  /**
   * Recommend skills from both ClawHub and GitHub
   *
   * Searches ClawHub for OpenClaw skills and GitHub for relevant repositories,
   * then merges and ranks results by match score.
   */
  private async recommendSkills(identity: IdentityData): Promise<SkillRecommendation[]> {
    console.log(`🔍 Searching for recommendations matching ${identity.personalityType}...`);

    try {
      // Search all sources in parallel
      const [clawHubSkills, claudeCodeSkills, githubRepos] = await Promise.all([
        this.getClawHubRecommendations(identity),
        this.getClaudeCodeRecommendations(identity),
        this.getGitHubRecommendations(identity),
      ]);

      // Merge results (keep all for categorized display)
      const allRecommendations = [...clawHubSkills, ...claudeCodeSkills, ...githubRepos];

      // Sort by match score within each source
      allRecommendations.sort((a, b) => b.matchScore - a.matchScore);

      console.log(`✅ Found ${clawHubSkills.length} ClawHub + ${claudeCodeSkills.length} Claude Code + ${githubRepos.length} GitHub recommendations`);
      console.log(`   Returning ${allRecommendations.length} total (categorized by source)`);

      return allRecommendations;

    } catch (error) {
      console.error('❌ Recommendation search failed:', error);
      return [];
    }
  }

  /**
   * Get recommendations from ClawHub
   */
  private async getClawHubRecommendations(identity: IdentityData): Promise<SkillRecommendation[]> {
    try {
      const clawHubSkills = await this.clawHubClient.getRecommendations({
        mainCategories: identity.mainCategories,
        subCategories: identity.subCategories,
        limit: 20,
      });

      // Convert ClawHub skills to our format and calculate enhanced match scores
      return clawHubSkills.map(skill => {
        // Base score from ClawHub similarity (0-100)
        let matchScore = skill.similarityScore * 100;

        // Boost score based on personality match
        const personalityKeywords = this.getPersonalityKeywords(identity.personalityType);
        const descLower = skill.description.toLowerCase();
        const keywordMatches = personalityKeywords.filter(k => descLower.includes(k)).length;
        matchScore += keywordMatches * 5;

        // Category match boost
        const categoryMatch = skill.categories?.some(c =>
          identity.mainCategories.includes(c) || identity.subCategories.includes(c.toLowerCase())
        );
        if (categoryMatch) {
          matchScore += 10;
        }

        return {
          skillId: skill.slug,
          skillName: skill.name,
          description: skill.description,
          url: skill.url,
          categories: skill.categories || ['General'],
          matchScore: Math.min(matchScore, 100),
          creator: skill.creator,
          creatorUserId: skill.creatorUserId,
          source: 'ClawHub' as const,
        };
      }).sort((a, b) => b.matchScore - a.matchScore);

    } catch (error) {
      console.error('⚠️  ClawHub search failed:', error);
      return [];
    }
  }

  /**
   * Get recommendations from Claude Code (Official Anthropic + Community)
   */
  private async getClaudeCodeRecommendations(identity: IdentityData): Promise<SkillRecommendation[]> {
    try {
      const claudeCodeSkills = await this.claudeCodeClient.getRecommendations({
        mainCategories: identity.mainCategories,
        subCategories: identity.subCategories,
        limit: 10,
      });

      // Convert to our SkillRecommendation format
      return claudeCodeSkills.map(skill => ({
        skillName: skill.skillName,
        matchScore: 85, // High score for official tools
        description: skill.description,
        url: skill.url,
        creator: skill.creator,
        source: 'ClaudeCode' as const,
      }));
    } catch (error) {
      console.error('⚠️  Claude Code search failed:', error);
      return [];
    }
  }

  /**
   * Get recommendations from GitHub
   */
  private async getGitHubRecommendations(identity: IdentityData): Promise<SkillRecommendation[]> {
    try {
      return await this.githubRecommendations.getRecommendations(identity, 15);
    } catch (error) {
      console.error('⚠️  GitHub search failed:', error);
      return [];
    }
  }

  /**
   * Get personality-specific keywords for matching
   */
  private getPersonalityKeywords(type: PersonalityType): string[] {
    const keywordMap = {
      [PersonalityType.THE_VISIONARY]: ['innovative', 'early-stage', 'vision', 'future', 'paradigm'],
      [PersonalityType.THE_EXPLORER]: ['diverse', 'experimental', 'discovery', 'research', 'explore'],
      [PersonalityType.THE_CULTIVATOR]: ['community', 'social', 'collaborate', 'nurture', 'build'],
      [PersonalityType.THE_OPTIMIZER]: ['efficiency', 'data-driven', 'optimize', 'systematic', 'analytics'],
      [PersonalityType.THE_INNOVATOR]: ['technology', 'ai', 'automation', 'creative', 'cutting-edge'],
    };
    return keywordMap[type] || [];
  }
}

/**
 * Skill registration for OpenClaw
 */
export const bloomIdentitySkillV2 = {
  name: 'bloom-identity',
  description: 'Generate your personalized Bloom Identity Card and discover matching projects',
  version: '2.0.0',

  triggers: [
    'generate my bloom identity',
    'create my identity card',
    'analyze my supporter profile',
    'mint my bloom card',
    'discover my personality',
  ],

  async execute(context: any) {
    const skill = new BloomIdentitySkillV2();

    // Check if this is a response to manual Q&A
    const manualAnswers = context.manualAnswers;

    const result = await skill.execute(context.userId, {
      mode: ExecutionMode.AUTO,
      skipShare: !context.enableShare, // Only if user enables
      manualAnswers,
    });

    if (!result.success) {
      if (result.needsManualInput) {
        // Return questions to user
        return {
          message: result.manualQuestions,
          data: { awaitingManualInput: true },
        };
      }

      return {
        message: `❌ Failed to generate identity: ${result.error}`,
        data: result,
      };
    }

    // Sanitize result: Remove wallet address for privacy
    const sanitizedResult = {
      ...result,
      agentWallet: result.agentWallet ? {
        network: result.agentWallet.network,
        hasWallet: true, // Flag that wallet exists, but don't expose address
      } : undefined,
    };

    return {
      message: formatSuccessMessage(result),
      data: sanitizedResult,
    };
  },
};

/**
 * Format success message for user
 */
function formatSuccessMessage(result: any): string {
  const { identityData, recommendations, mode, dimensions } = result;

  const modeEmoji = mode === 'manual' ? '📝' : '🤖';

  // Format 2x2 metrics display
  let metricsDisplay = '';
  if (dimensions) {
    const isCultivator = identityData.personalityType === 'The Cultivator';
    const contributionLine = isCultivator ? `   Contribution: ${dimensions.contribution}/100\n` : '';

    metricsDisplay = `
📊 **2x2 Metrics**
   Conviction ${dimensions.conviction} ← → Curiosity ${100 - dimensions.conviction}
   Intuition ${dimensions.intuition} ← → Analysis ${100 - dimensions.intuition}
${contributionLine}
`;
  }

  return `
🎉 **Your Bloom Identity Card is Ready!** ${modeEmoji}

${result.dashboardUrl ? `🌐 **View Your Card**\n→ ${result.dashboardUrl}\n\n💾 Save to your collection or share on X from the dashboard!\n` : ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${getPersonalityEmoji(identityData.personalityType)} **${identityData.personalityType}**
💬 *"${identityData.customTagline}"*

${identityData.customDescription}

**Categories**: ${identityData.mainCategories.join(' • ')}
${identityData.subCategories && identityData.subCategories.length > 0
  ? `**Interests**: ${identityData.subCategories.join(' • ')}\n`
  : ''}
${metricsDisplay}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Recommended for You** (${recommendations.length} total)

${(() => {
  const clawHubSkills = recommendations.filter((r: any) => r.source === 'ClawHub' || !r.source);
  const githubRepos = recommendations.filter((r: any) => r.source === 'GitHub');

  let output = '';

  // ClawHub Skills (top 3)
  if (clawHubSkills.length > 0) {
    output += '🦞 **ClawHub Skills**\n\n';
    output += clawHubSkills.slice(0, 3).map((s: any, i: number) => {
      const creatorInfo = s.creator ? ` • by @${s.creator}` : '';
      return `${i + 1}. **${s.skillName}**${creatorInfo}
   ${s.description}
   → ${s.url}`;
    }).join('\n\n');
  }

  // GitHub Repositories (top 3)
  if (githubRepos.length > 0) {
    if (output) output += '\n\n';
    output += '🐙 **GitHub Repositories**\n\n';
    output += githubRepos.slice(0, 3).map((s: any, i: number) => {
      const starsInfo = s.stars ? ` ⭐ ${s.stars >= 1000 ? `${(s.stars / 1000).toFixed(1)}k` : s.stars}` : '';
      const langInfo = s.language ? ` [${s.language}]` : '';
      return `${i + 1}. **${s.skillName}**${starsInfo}${langInfo}
   ${s.description}
   → ${s.url}`;
    }).join('\n\n');
  }

  return output;
})()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Your Agent Wallet is Ready**
More functions on tipping, recommendations, and autonomous actions will come soon! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${mode === 'manual' ? '📝 Q&A' : '🤖 On-chain'} • @openclaw @coinbase @base 🦞
  `.trim();
}

function getPersonalityEmoji(type: PersonalityType): string {
  const emojiMap = {
    [PersonalityType.THE_VISIONARY]: '💜',
    [PersonalityType.THE_EXPLORER]: '💚',
    [PersonalityType.THE_CULTIVATOR]: '🩵',
    [PersonalityType.THE_OPTIMIZER]: '🧡',
    [PersonalityType.THE_INNOVATOR]: '💙',
  };
  return emojiMap[type] || '🎴';
}

export default bloomIdentitySkillV2;
