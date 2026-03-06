/**
 * Contract Client
 *
 * Low-level client for interacting with BloomIdentityCard smart contract
 */

import { ethers } from 'ethers';
import { PersonalityType, IdentityData } from '../bloom-identity-skill-v2';

// Contract address on Base Sepolia
const CONTRACT_ADDRESS = '0x33a5d347510a3ec95d10dB563e32fC8C91844B9E';

// Base Sepolia RPC
const RPC_URL = 'https://sepolia.base.org';

// Contract ABI (simplified - include only functions we need)
const CONTRACT_ABI = [
  'function mint(string identityType, string customTagline, string customDescription, string[] mainCategories, string[] subCategories) public returns (uint256)',
  'function hasMinted(address user) public view returns (bool)',
  'function getTokenIdByAddress(address user) public view returns (uint256)',
  'function getIdentityData(uint256 tokenId) public view returns (tuple(string identityType, string customTagline, string customDescription, string[] mainCategories, string[] subCategories, uint256 mintedAt))',
  'function updateIdentity(uint256 tokenId, string identityType, string customTagline, string customDescription, string[] mainCategories, string[] subCategories) public',
  'function isValidPersonalityType(string identityType) public view returns (bool)',
  'function getValidPersonalityTypes() public view returns (string[])',
];

export class ContractClient {
  private provider: ethers.Provider;
  private contract: ethers.Contract;
  private signer?: ethers.Signer;

  constructor() {
    this.provider = new ethers.JsonRpcProvider(RPC_URL);
    this.contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, this.provider);
  }

  /**
   * Set signer for write operations
   */
  setSigner(privateKey: string) {
    this.signer = new ethers.Wallet(privateKey, this.provider);
    this.contract = this.contract.connect(this.signer);
  }

  /**
   * Mint a new Identity Card
   */
  async mint(params: {
    userAddress: string;
    personalityType: PersonalityType;
    tagline: string;
    description: string;
    mainCategories: string[];
    subCategories: string[];
  }): Promise<{ tokenId: number; transactionHash: string }> {
    if (!this.signer) {
      throw new Error('Signer not set. Call setSigner() first.');
    }

    // Validate personality type
    const isValid = await this.contract.isValidPersonalityType(params.personalityType);
    if (!isValid) {
      throw new Error(`Invalid personality type: ${params.personalityType}`);
    }

    // Execute mint transaction
    const tx = await this.contract.mint(
      params.personalityType,
      params.tagline,
      params.description,
      params.mainCategories,
      params.subCategories
    );

    console.log(`🔄 Transaction sent: ${tx.hash}`);
    const receipt = await tx.wait();
    console.log(`✅ Transaction confirmed in block ${receipt.blockNumber}`);

    // Extract token ID from event logs
    const tokenId = await this.getTokenIdByAddress(params.userAddress);

    return {
      tokenId,
      transactionHash: tx.hash,
    };
  }

  /**
   * Check if address has minted
   */
  async hasMinted(address: string): Promise<boolean> {
    return await this.contract.hasMinted(address);
  }

  /**
   * Get token ID by address
   */
  async getTokenIdByAddress(address: string): Promise<number> {
    const tokenId = await this.contract.getTokenIdByAddress(address);
    return Number(tokenId);
  }

  /**
   * Get identity data by token ID
   */
  async getIdentityData(tokenId: number): Promise<IdentityData> {
    const data = await this.contract.getIdentityData(tokenId);

    return {
      personalityType: data.identityType as PersonalityType,
      customTagline: data.customTagline,
      customDescription: data.customDescription,
      mainCategories: data.mainCategories,
      subCategories: data.subCategories,
    };
  }

  /**
   * Update identity data
   */
  async updateIdentity(tokenId: number, identityData: IdentityData): Promise<void> {
    if (!this.signer) {
      throw new Error('Signer not set. Call setSigner() first.');
    }

    const tx = await this.contract.updateIdentity(
      tokenId,
      identityData.personalityType,
      identityData.customTagline,
      identityData.customDescription,
      identityData.mainCategories,
      identityData.subCategories
    );

    await tx.wait();
  }

  /**
   * Get all valid personality types
   */
  async getValidPersonalityTypes(): Promise<string[]> {
    return await this.contract.getValidPersonalityTypes();
  }
}
