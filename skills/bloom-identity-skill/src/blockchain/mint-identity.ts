/**
 * Mint Identity
 *
 * Handles minting and updating Bloom Identity Card SBTs on Base
 */

import { PersonalityType, IdentityData } from '../bloom-identity-skill-v2';
import { ContractClient } from './contract-client';

export interface MintResult {
  tokenId: number;
  explorerUrl: string;
  imageUrl: string;
  transactionHash: string;
}

export class MintIdentity {
  private contractClient: ContractClient;

  constructor() {
    this.contractClient = new ContractClient();
  }

  /**
   * Mint a new Identity Card SBT
   */
  async mint(
    userId: string,
    personalityType: PersonalityType,
    tagline: string,
    description: string,
    mainCategories: string[],
    subCategories: string[]
  ): Promise<MintResult> {
    console.log(`⛓️  Minting Identity Card for ${userId}...`);

    // Check if user already has a card
    const hasCard = await this.hasCard(userId);
    if (hasCard) {
      throw new Error('User already has an Identity Card');
    }

    // Mint the NFT
    const result = await this.contractClient.mint({
      userAddress: userId,
      personalityType,
      tagline,
      description,
      mainCategories,
      subCategories,
    });

    console.log(`✅ Identity Card minted! Token ID: ${result.tokenId}`);

    return {
      tokenId: result.tokenId,
      explorerUrl: `https://sepolia.basescan.org/token/0x33a5d347510a3ec95d10dB563e32fC8C91844B9E?a=${result.tokenId}`,
      imageUrl: `https://bloomprotocol.ai/api/identity/card/${result.tokenId}/image`,
      transactionHash: result.transactionHash,
    };
  }

  /**
   * Check if user has an Identity Card
   */
  async hasCard(userId: string): Promise<boolean> {
    return this.contractClient.hasMinted(userId);
  }

  /**
   * Get user's Identity Card data
   */
  async getIdentityData(userId: string): Promise<IdentityData | null> {
    const tokenId = await this.contractClient.getTokenIdByAddress(userId);
    if (tokenId === 0) {
      return null;
    }

    return this.contractClient.getIdentityData(tokenId);
  }

  /**
   * Update existing Identity Card
   */
  async update(userId: string, identityData: IdentityData): Promise<boolean> {
    console.log(`🔄 Updating Identity Card for ${userId}...`);

    const tokenId = await this.contractClient.getTokenIdByAddress(userId);
    if (tokenId === 0) {
      throw new Error('No Identity Card found for user');
    }

    await this.contractClient.updateIdentity(tokenId, identityData);

    console.log(`✅ Identity Card updated!`);
    return true;
  }
}
