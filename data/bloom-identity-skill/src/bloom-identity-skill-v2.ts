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
import { captureAndUploadCardImage } from './blockchain/card-image';
import { TwitterShare, createTwitterShare } from './integrations/twitter-share';
import { PersonalityType } from './types/personality';
import { refreshRecommendations, SkillRecommendation } from './recommendation-pipeline';
import { syncDiscoveries } from './discovery-sync';
import { parseUserMd, UserMdSignals } from './parsers/user-md-parser';
import { mergeSignals, MergedSignals, FeedbackData } from './analyzers/signal-merger';

// Re-export for backwards compatibility
export { PersonalityType };
export type { SkillRecommendation, FeedbackData, UserMdSignals };

export interface IdentityData {
  personalityType: PersonalityType;
  customTagline: string;
  customDescription: string;
  mainCategories: string[];
  subCategories: string[];
  dimensions?: {
    conviction: number;
    intuition: number;
    contribution: number;
  };
  tasteSpectrums?: {
    learning: number;
    decision: number;
    novelty: number;
    risk: number;
  };
  strengths?: string[];
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

  constructor() {
    this.personalityAnalyzer = new PersonalityAnalyzer();
    this.dataCollector = new EnhancedDataCollector();
    this.manualQA = new ManualQAFallback();
    this.categoryMapper = new CategoryMapper();
    this.twitterShare = createTwitterShare();
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
      walletInfo.agentUserId = registration.agentUserId;
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
      userMdPath?: string;       // Path to USER.md, default ~/.config/claude/USER.md
      feedback?: FeedbackData;   // Feedback signals from recommendation interactions
      // SBT minting is automatic when SBT_CONTRACT_ADDRESS is set
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

      // Step 1.5: Parse USER.md for static profile signals
      console.log('📋 Step 1.5: Parsing USER.md...');
      const userMdSignals = parseUserMd(options?.userMdPath);
      if (userMdSignals) {
        console.log(`✅ USER.md signals: role=${userMdSignals.role || 'none'}, focus=${userMdSignals.currentFocus?.join(', ') || 'none'}, style=${userMdSignals.workingStyle || 'none'}`);
      } else {
        console.log('📋 No USER.md found (graceful degradation)');
      }

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

            // Pre-compute dimension nudges from USER.md + feedback
            const preNudges = (userMdSignals || options?.feedback)
              ? mergeSignals(
                  [], // categories not needed yet, just computing nudges
                  { conviction: 0, intuition: 0, contribution: 0 },
                  userMdSignals,
                  options?.feedback ?? null,
                )
              : null;

            // Inject USER.md raw text as first-class signal source
            if (userMdSignals?.raw) {
              userData.userMdContent = Object.values(userMdSignals.raw).join('\n');
            }

            // Analyze personality from data (with optional dimension nudges)
            const analysis = await this.personalityAnalyzer.analyze(
              userData,
              preNudges?.dimensionNudges,
            );

            // Build identity from conversation analysis
            const conversationCategories = analysis.detectedCategories.length > 0
              ? analysis.detectedCategories
              : this.categoryMapper.getMainCategories(analysis.personalityType);

            // Step 2.5: Merge signals (conversation + USER.md + feedback)
            const merged = mergeSignals(
              conversationCategories,
              analysis.dimensions,
              userMdSignals,
              options?.feedback ?? null,
            );

            identityData = {
              personalityType: analysis.personalityType,
              customTagline: analysis.tagline,
              customDescription: analysis.description,
              mainCategories: merged.mainCategories,
              subCategories: [...analysis.detectedInterests, ...merged.subCategories.filter(
                s => !analysis.detectedInterests.includes(s),
              )],
              dimensions: analysis.dimensions,
              tasteSpectrums: analysis.dimensions.tasteSpectrums,
              strengths: analysis.strengths,
            };

            // ⭐ Capture 2x2 metrics
            dimensions = analysis.dimensions;

            if (userMdSignals || options?.feedback) {
              console.log(`✅ Signals merged: categories=${merged.mainCategories.join(', ')}`);
            }

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
          tasteSpectrums: manualResult.tasteSpectrums,
        };

        dataQuality = manualResult.confidence;
        console.log(`✅ Manual analysis complete: ${identityData.personalityType}`);
      }

      // Step 3: Recommend OpenClaw Skills ⭐ NEW
      console.log('🔍 Step 3: Finding matching OpenClaw Skills...');
      const merged = (userMdSignals || options?.feedback)
        ? mergeSignals(
            identityData!.mainCategories,
            identityData!.dimensions || { conviction: 50, intuition: 50, contribution: 50 },
            userMdSignals,
            options?.feedback ?? null,
          )
        : null;
      const recommendations = await this.recommendSkills(identityData!, merged);
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
        tasteSpectrums: identityData!.tasteSpectrums,
        strengths: identityData!.strengths,
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
        console.debug('Wallet registration fallback:', walletError instanceof Error ? walletError.message : walletError);

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

      // Fallback: use agentUserId from pre-registration
      if (!agentUserId && agentWallet.agentUserId) {
        agentUserId = agentWallet.agentUserId;
        console.log(`✅ Using pre-registered agentUserId: ${agentUserId}`);
      }

      if (agentUserId) {
        // Seed discoveries file (fire-and-forget)
        syncDiscoveries(agentUserId).catch(err => {
          console.debug('[discovery-sync] fire-and-forget failed:', err instanceof Error ? err.message : err);
        });

        const baseUrl = process.env.DASHBOARD_URL || 'https://bloomprotocol.ai';
        dashboardUrl = `${baseUrl}/agents/${agentUserId}`;
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

      // Auto-mint SBT on Base when contract + minter key are configured
      const sbtContractAddress = process.env.SBT_CONTRACT_ADDRESS as `0x${string}` | undefined;
      const sbtMinterKey = process.env.SBT_MINTER_PRIVATE_KEY || process.env.DEPLOYER_PRIVATE_KEY;
      if (sbtContractAddress && sbtMinterKey) {
        try {
          const minterKey = (sbtMinterKey.startsWith('0x') ? sbtMinterKey : `0x${sbtMinterKey}`) as `0x${string}`;

          // Capture card screenshot from dashboard and upload to IPFS
          let cardImageUrl: string | undefined;
          if (dashboardUrl) {
            console.log('📸 Capturing Taste Card image...');
            const imageResult = await captureAndUploadCardImage(dashboardUrl, identityData!.personalityType);
            if (imageResult) {
              cardImageUrl = imageResult.ipfsUrl;
              console.log(`✅ Card image uploaded to IPFS: ${imageResult.gatewayUrl}`);
            }
          }

          const tokenUri = this.buildTokenUri(identityData!, agentWallet, dashboardUrl, dimensions, cardImageUrl);
          const txHash = await mintIdentitySbt({
            contractAddress: sbtContractAddress,
            to: agentWallet.address as `0x${string}`,
            tokenUri,
            network: agentWallet.network as 'base-mainnet' | 'base-sepolia',
            privateKey: minterKey,
          });

          mintAction = {
            contractAddress: sbtContractAddress,
            tokenUri,
            txHash,
            network: agentWallet.network,
          };
          console.log(`✅ Taste Card minted on Base (tx: ${txHash.slice(0, 10)}...)`);
        } catch (error) {
          // Non-blocking — skill still succeeds without SBT
          console.debug('SBT mint skipped:', error instanceof Error ? error.message : error);
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
            registerUrl: `${process.env.DASHBOARD_URL || 'https://bloomprotocol.ai'}/register?return=${encodeURIComponent(dashboardUrl)}`,
            loginUrl: `${process.env.DASHBOARD_URL || 'https://bloomprotocol.ai'}/login?return=${encodeURIComponent(dashboardUrl)}`,
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

  private buildTokenUri(
    identity: IdentityData,
    wallet: AgentWalletInfo,
    dashboardUrl?: string,
    dims?: { conviction: number; intuition: number; contribution: number },
    ipfsImageUrl?: string,
  ): string {
    const baseUrl = process.env.DASHBOARD_URL || 'https://bloomprotocol.ai';
    // Use IPFS screenshot if available, fallback to static OG image
    const typeSlug = identity.personalityType.replace(/^The /, '').toLowerCase();
    const ogImage = ipfsImageUrl || `${baseUrl}/og/${typeSlug}.png`;

    const metadata: Record<string, any> = {
      name: `Bloom Taste Card — ${identity.personalityType}`,
      description: identity.customTagline,
      image: ogImage,
      external_url: dashboardUrl,
      attributes: [
        { trait_type: 'Personality Type', value: identity.personalityType },
        ...identity.mainCategories.map(c => ({ trait_type: 'Category', value: c })),
        { trait_type: 'Discovery Mode', value: 'Active' },
      ],
    };

    // Add dimension scores when available
    if (dims) {
      metadata.attributes.push(
        { trait_type: 'Conviction', value: dims.conviction, display_type: 'number' },
        { trait_type: 'Intuition', value: dims.intuition, display_type: 'number' },
        { trait_type: 'Contribution', value: dims.contribution, display_type: 'number' },
      );
    }

    // Add taste spectrum scores
    if (identity.tasteSpectrums) {
      metadata.attributes.push(
        { trait_type: 'Learning Style', value: identity.tasteSpectrums.learning, display_type: 'number' },
        { trait_type: 'Decision Style', value: identity.tasteSpectrums.decision, display_type: 'number' },
        { trait_type: 'Novelty Style', value: identity.tasteSpectrums.novelty, display_type: 'number' },
        { trait_type: 'Risk Style', value: identity.tasteSpectrums.risk, display_type: 'number' },
      );
    }

    // Add strengths
    if (identity.strengths?.length) {
      for (const strength of identity.strengths) {
        metadata.attributes.push({ trait_type: 'Strength', value: strength });
      }
    }

    const json = JSON.stringify(metadata);
    const base64 = Buffer.from(json).toString('base64');
    return `data:application/json;base64,${base64}`;
  }

  /**
   * Recommend skills grouped by user's main categories
   *
   * Delegates to the extracted recommendation-pipeline module so that
   * the same logic can be reused by the backend Bull queue refresh job.
   */
  private async recommendSkills(
    identity: IdentityData,
    merged?: MergedSignals | null,
  ): Promise<SkillRecommendation[]> {
    return refreshRecommendations({
      mainCategories: identity.mainCategories,
      subCategories: identity.subCategories,
      personalityType: identity.personalityType,
      dimensions: identity.dimensions,
      tasteSpectrums: identity.tasteSpectrums,
      feedback: merged ? {
        categoryWeights: merged.categoryWeights,
        excludeSkillIds: merged.excludedSkillIds,
      } : undefined,
    });
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
  const { identityData, recommendations } = result;

  let msg = `${getPersonalityEmoji(identityData.personalityType)} **${identityData.personalityType}**
"${identityData.customTagline}"
**Categories**: ${identityData.mainCategories.join(' • ')}`;

  // SBT mint data is in result.actions.mint but not shown to users (web3-native only on dashboard)
  if (recommendations?.length > 0 && result.dashboardUrl) {
    msg += `\n\n✨ **Your Taste Card is ready**`;
    msg += `\n→ See your card & recommendations: ${result.dashboardUrl}`;
  } else if (result.dashboardUrl) {
    msg += `\n\n✨ **Your Taste Card is ready**`;
    msg += `\n→ See your card: ${result.dashboardUrl}`;
  }

  return msg;
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
