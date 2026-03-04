#!/usr/bin/env node
/**
 * BaseCred SDK Wrapper
 * Provides simplified interface to @basecred/sdk with automatic configuration
 */

import { getUnifiedProfile } from '@basecred/sdk';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { homedir } from 'os';

// Load environment variables from OpenClaw .env (user-agnostic)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const openclawEnvPath = join(homedir(), '.openclaw', '.env');
dotenv.config({ path: openclawEnvPath });

/**
 * Check reputation for an Ethereum address
 * @param {string} address - Ethereum address (0x...)
 * @param {object} options - Configuration options
 * @returns {Promise<object>} Unified reputation profile
 */
export async function checkReputation(address, options = {}) {
  try {
    // Validate address format
    if (!address || !address.match(/^0x[a-fA-F0-9]{40}$/)) {
      return {
        error: 'Invalid address format',
        message: 'Please provide a valid Ethereum address (0x...)',
      };
    }

    // Build SDK configuration
    const config = buildConfig(options);

    // Fetch unified profile
    const profile = await getUnifiedProfile(address, config);

    // Return with metadata
    return {
      success: true,
      address,
      timestamp: new Date().toISOString(),
      profile,
      sources: {
        ethos: profile.availability.ethos === 'available',
        talent: config.talent ? profile.availability.talent === 'available' : false,
        farcaster: config.farcaster ? profile.availability.farcaster === 'available' : false,
      },
      availability: profile.availability,
    };

  } catch (error) {
    return {
      error: 'Reputation check failed',
      message: error.message,
      address,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Get summary view of reputation data
 * @param {object} response - Response from checkReputation
 * @returns {object} Summarized reputation data
 */
export function getSummary(response) {
  if (response.error) {
    return { error: response.error, message: response.message };
  }

  const { profile, address, timestamp, availability } = response;
  const summary = {
    address,
    timestamp,
    availability,
    data: {},
  };

  // Ethos summary
  if (profile.ethos?.data) {
    summary.data.ethos = {
      score: profile.ethos.data.score,
      level: profile.ethos.data.credibilityLevel?.level,
      vouches: profile.ethos.data.vouchesReceived,
      reviews: profile.ethos.data.reviews,
      hasNegativeReviews: profile.ethos.signals?.hasNegativeReviews,
    };
  }

  // Talent summary
  if (profile.talent?.data) {
    summary.data.talent = {
      builderScore: profile.talent.data.builderScore,
      builderLevel: profile.talent.data.builderLevel?.level,
      builderRank: profile.talent.data.builderRankPosition,
      creatorScore: profile.talent.data.creatorScore,
      creatorLevel: profile.talent.data.creatorLevel?.level,
      creatorRank: profile.talent.data.creatorRankPosition,
    };
  }

  // Farcaster summary
  if (profile.farcaster?.data) {
    summary.data.farcaster = {
      score: profile.farcaster.data.userScore,
      passesQuality: profile.farcaster.signals?.passesQualityThreshold,
    };
  }

  // Recency
  if (profile.recency) {
    summary.recency = profile.recency.bucket;
  }

  return summary;
}

/**
 * Build SDK configuration from environment and options
 * @param {object} options - User options
 * @returns {object} SDK config
 */
function buildConfig(options = {}) {
  const config = {
    ethos: {
      baseUrl: options.ethosUrl || 'https://api.ethos.network',
      clientId: options.clientId || 'basecred-sdk-skill@1.0.0',
    },
  };

  // Add Talent Protocol if API key available
  const talentApiKey = options.talentApiKey || process.env.TALENT_API_KEY;
  if (talentApiKey) {
    config.talent = {
      baseUrl: options.talentUrl || 'https://api.talentprotocol.com',
      apiKey: talentApiKey,
    };
  } else if (!options.skipWarnings) {
    console.warn('⚠️  TALENT_API_KEY not found - Talent Protocol scores unavailable');
  }

  // Add Farcaster (Neynar) if API key available
  const neynarApiKey = options.neynarApiKey || process.env.NEYNAR_API_KEY;
  if (neynarApiKey) {
    config.farcaster = {
      enabled: true,
      neynarApiKey,
      qualityThreshold: options.qualityThreshold || 0.5,
    };
  } else if (!options.skipWarnings) {
    console.warn('⚠️  NEYNAR_API_KEY not found - Farcaster scores unavailable');
  }

  // Level derivation (enabled by default)
  if (options.levels !== undefined) {
    config.levels = { enabled: options.levels };
  }

  return config;
}

/**
 * Format response for human-readable output
 * @param {object} data - Summary or full response
 * @returns {string} Formatted text
 */
export function formatHuman(data) {
  if (data.error) {
    return `❌ Error: ${data.message}`;
  }

  const lines = [];
  lines.push(`📊 Reputation Summary for ${data.address}`);
  lines.push(`⏰ ${data.timestamp}\n`);

  // Availability
  lines.push('📡 Data Sources:');
  Object.entries(data.availability || {}).forEach(([source, status]) => {
    const icon = status === 'available' ? '✅' : status === 'not_found' ? '🔍' : '❌';
    lines.push(`   ${icon} ${source}: ${status}`);
  });
  lines.push('');

  // Data summaries
  if (data.data?.ethos) {
    lines.push('🌐 Ethos Network:');
    lines.push(`   Score: ${data.data.ethos.score} (${data.data.ethos.level})`);
    lines.push(`   Vouches: ${data.data.ethos.vouches}`);
    lines.push(`   Reviews: ${data.data.ethos.reviews.positive}+ / ${data.data.ethos.reviews.neutral}• / ${data.data.ethos.reviews.negative}-`);
    lines.push('');
  }

  if (data.data?.talent) {
    lines.push('🛠️  Talent Protocol:');
    lines.push(`   Builder: ${data.data.talent.builderScore} (${data.data.talent.builderLevel})${data.data.talent.builderRank ? ` - Rank #${data.data.talent.builderRank}` : ''}`);
    lines.push(`   Creator: ${data.data.talent.creatorScore} (${data.data.talent.creatorLevel})${data.data.talent.creatorRank ? ` - Rank #${data.data.talent.creatorRank}` : ''}`);
    lines.push('');
  }

  if (data.data?.farcaster) {
    lines.push('🎭 Farcaster:');
    lines.push(`   Quality Score: ${data.data.farcaster.score}`);
    lines.push(`   Passes Threshold: ${data.data.farcaster.passesQuality ? '✅' : '❌'}`);
    lines.push('');
  }

  if (data.recency) {
    lines.push(`📅 Recency: ${data.recency}`);
  }

  return lines.join('\n');
}
