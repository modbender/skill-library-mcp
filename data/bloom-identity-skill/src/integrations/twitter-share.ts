/**
 * Twitter Share Integration
 *
 * Generates Twitter share links for Bloom Identity Cards
 */

import { PersonalityType } from '../types/personality';

export interface TwitterShareOptions {
  userId: string;
  personalityType: PersonalityType;
  recommendations: Array<{ skillName: string; matchScore: number }>;
  agentWallet?: string;
}

/**
 * Twitter Share Client
 */
export class TwitterShare {
  /**
   * Generate Twitter share link with pre-filled text
   */
  generateShareLink(options: TwitterShareOptions): string {
    const { personalityType, recommendations, agentWallet } = options;

    // Craft share text
    const text = this.craftShareText(personalityType, recommendations, agentWallet);

    // Encode for URL
    const encodedText = encodeURIComponent(text);

    // Generate Twitter intent URL
    return `https://twitter.com/intent/tweet?text=${encodedText}`;
  }

  /**
   * Craft engaging share text
   */
  private craftShareText(
    personalityType: PersonalityType,
    recommendations: Array<{ skillName: string; matchScore: number }>,
    agentWallet?: string
  ): string {
    const emoji = this.getPersonalityEmoji(personalityType);
    const topSkills = recommendations.slice(0, 3);

    let text = `${emoji} Just discovered my Bloom Identity: ${personalityType}!\n\n`;

    if (topSkills.length > 0) {
      text += `🎯 Top OpenClaw Skills for me:\n`;
      topSkills.forEach((skill, i) => {
        text += `${i + 1}. ${skill.skillName} (${skill.matchScore}% match)\n`;
      });
      text += '\n';
    }

    if (agentWallet) {
      text += `🤖 My Agent is now on-chain with X402 wallet!\n\n`;
    }

    text += `Built with @openclaw @coinbase @base 🦞\n`;
    text += `#BloomIdentity #AgentKit #BuilderQuest`;

    return text;
  }

  /**
   * Get personality emoji
   */
  private getPersonalityEmoji(type: PersonalityType): string {
    const emojiMap = {
      [PersonalityType.THE_VISIONARY]: '💜',
      [PersonalityType.THE_EXPLORER]: '💚',
      [PersonalityType.THE_CULTIVATOR]: '🩵',
      [PersonalityType.THE_OPTIMIZER]: '🧡',
      [PersonalityType.THE_INNOVATOR]: '💙',
    };
    return emojiMap[type] || '🎴';
  }

  /**
   * Generate share link and log for user
   */
  async share(options: TwitterShareOptions): Promise<string> {
    const shareUrl = this.generateShareLink(options);

    console.log('\n📢 Twitter Share Link Generated:');
    console.log(shareUrl);
    console.log('\n💡 Copy this link to share your Bloom Identity on Twitter!\n');

    return shareUrl;
  }
}

/**
 * Create Twitter share client
 */
export function createTwitterShare(): TwitterShare {
  return new TwitterShare();
}
