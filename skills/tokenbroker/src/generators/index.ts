/**
 * TokenBroker Generators Index
 * 
 * Main entry point for the TokenBroker generator pipeline.
 * Orchestrates generators to produce complete token launch assets for nad.fun.
 * 
 * Architecture:
 * - Identity Generator: Creates token name, ticker, description
 * - Reasoning Generator: Creates investment thesis and narrative
 * - Promo Generator: Creates X/Twitter, Telegram, Discord content
 * - Nad.fun Launch Manager: Prepares token launch (image, metadata, salt)
 */

import { generateIdentity } from './identity.js';
import type { IdentityInput, IdentityOutput } from './identity.js';
import { generateReasoning } from './reasoning.js';
import type { ReasoningInput, ReasoningOutput } from './reasoning.js';
import { generatePromo } from './promo.js';
import type { PromoInput, PromoOutput, XThread, TelegramPost, DiscordAnnouncement } from './promo.js';
import {
    generateTokenImage,
    uploadImage,
    uploadMetadata,
    mineSalt,
    prepareLaunch,
    type ImageGenerationParams,
    type UploadImageResult,
    type UploadMetadataResult,
    type MineSaltResult,
    type PreparedLaunch
} from './nadfun.js';
import type { RepoAnalysis } from './types.js';

// Re-export types
export type { IdentityInput, IdentityOutput } from './identity.js';
export type { ReasoningInput, ReasoningOutput } from './reasoning.js';
export type { PromoInput, PromoOutput, XThread, TelegramPost, DiscordAnnouncement } from './promo.js';
export type { ImageGenerationParams, UploadImageResult, UploadMetadataResult, MineSaltResult, PreparedLaunch } from './nadfun.js';
export type { RepoAnalysis } from './types.js';

// Re-export functions
export { generateIdentity } from './identity.js';
export { generateReasoning } from './reasoning.js';
export { generatePromo } from './promo.js';
export { generateTokenImage, uploadImage, uploadMetadata, mineSalt, prepareLaunch } from './nadfun.js';

/**
 * Combined input for the full pipeline
 */
export interface PipelineInput {
    /** Repository analysis data */
    repoAnalysis: RepoAnalysis;
}

/**
 * Combined output from all generators (ready for nad.fun launch)
 */
export interface PipelineOutput {
    /** Identity generation results */
    identity: {
        name: string;
        ticker: string;
        description: string;
        nameReasoning: string;
    };
    /** Reasoning generation results */
    reasoning: {
        investmentThesis: string;
        problemStatement: string;
        solution: string;
        marketOpportunity: string;
        competitiveAdvantage: string;
        tokenUtilityRationale: string;
        vision: string;
    };
    /** Promo generation results */
    promo: {
        xThread: {
            title: string;
            tweets: { number: number; content: string; hasImage: boolean; imageDescription?: string }[];
            hashtags: string[];
            mentions: string[];
        };
        telegramPost: {
            title: string;
            content: string;
            hasButton: boolean;
            buttonText?: string;
            buttonUrl?: string;
        };
        discordAnnouncement: {
            title: string;
            content: string;
            hasEmbed: boolean;
            embedColor?: string;
            embedFields?: { name: string; value: string; inline: boolean }[];
        };
        tagline: string;
        elevatorPitch: string;
    };
    /** Metadata */
    metadata: {
        generatedAt: string;
        generatorVersion: string;
    };
}

/**
 * Runs the complete TokenBroker generation pipeline.
 * 
 * @param input - Pipeline input containing repository analysis
 * @returns Promise resolving to complete pipeline output with all generated assets
 * 
 * @example
 * ```typescript
 * const result = await generateAll({
 *   repoAnalysis: {
 *     owner: "somerepo",
 *     repoName: "awesome-project",
 *     description: "A decentralized exchange",
 *     language: "TypeScript",
 *     stars: 1000,
 *     forks: 100,
 *     openIssues: 50,
 *     license: "MIT",
 *     createdAt: "2020-01-01",
 *     updatedAt: "2024-01-01",
 *     readme: "# Awesome Project\n...",
 *     features: ["Feature 1", "Feature 2"],
 *     techStack: ["React", "Node.js"],
 *     contributors: 25,
 *     recentCommits: 50,
 *     isActive: true
 *   }
 * });
 * 
 * console.log(result.identity.name);
 * console.log(result.promo.xThread.tweets[0].content);
 * ```
 */
export async function generateAll(input: PipelineInput): Promise<PipelineOutput> {
    // Step 1: Generate identity
    const identityResult = await generateIdentity({
        repoAnalysis: input.repoAnalysis
    });

    // Step 2: Generate reasoning
    const reasoningResult = await generateReasoning({
        repoAnalysis: input.repoAnalysis,
        identity: {
            name: identityResult.name,
            ticker: identityResult.ticker,
            description: identityResult.description
        }
    });

    // Step 3: Generate promo content
    const promoResult = await generatePromo({
        repoAnalysis: input.repoAnalysis,
        identity: {
            name: identityResult.name,
            ticker: identityResult.ticker,
            description: identityResult.description
        },
        reasoning: {
            investmentThesis: reasoningResult.investmentThesis,
            problemStatement: reasoningResult.problemStatement,
            solution: reasoningResult.solution,
            vision: reasoningResult.vision
        }
    });

    // Return combined output
    return {
        identity: {
            name: identityResult.name,
            ticker: identityResult.ticker,
            description: identityResult.description,
            nameReasoning: identityResult.nameReasoning
        },
        reasoning: {
            investmentThesis: reasoningResult.investmentThesis,
            problemStatement: reasoningResult.problemStatement,
            solution: reasoningResult.solution,
            marketOpportunity: reasoningResult.marketOpportunity,
            competitiveAdvantage: reasoningResult.competitiveAdvantage,
            tokenUtilityRationale: reasoningResult.tokenUtilityRationale,
            vision: reasoningResult.vision
        },
        promo: {
            xThread: promoResult.xThread,
            telegramPost: promoResult.telegramPost,
            discordAnnouncement: promoResult.discordAnnouncement,
            tagline: promoResult.tagline,
            elevatorPitch: promoResult.elevatorPitch
        },
        metadata: {
            generatedAt: new Date().toISOString(),
            generatorVersion: '1.02'
        }
    };
}
