/**
 * Wallet Storage Layer
 *
 * Stores and retrieves per-user wallet data
 * Currently uses file-based storage (can migrate to MongoDB later)
 *
 * ⭐ AgentKit 0.10.4 Update:
 * - Wallets are now managed server-side by CDP
 * - We only need to store the wallet address (not full wallet data)
 * - CDP retrieves wallets by address using API credentials
 *
 * ⭐ Security Update:
 * - Local wallet private keys are encrypted with AES-256-GCM
 * - Uses WALLET_ENCRYPTION_SECRET from environment
 * - Production-ready secure storage
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { encryptPrivateKey, decryptPrivateKey, validateEncryptionSecret } from './encryption';

export interface UserWalletRecord {
  userId: string;
  walletAddress: `0x${string}`;
  network: string;
  createdAt: string;
  lastUsedAt: string;
  encryptedPrivateKey?: string;  // ⭐ Encrypted with AES-256-GCM (for local wallets)
}

const STORAGE_DIR = path.join(process.cwd(), '.wallet-storage');
const STORAGE_FILE = path.join(STORAGE_DIR, 'user-wallets.json');

/**
 * Wallet Storage Manager
 */
export class WalletStorage {
  /**
   * Initialize storage directory
   */
  private async ensureStorageExists(): Promise<void> {
    try {
      await fs.access(STORAGE_DIR);
    } catch {
      await fs.mkdir(STORAGE_DIR, { recursive: true });
      await fs.writeFile(STORAGE_FILE, JSON.stringify({}), 'utf-8');
    }
  }

  /**
   * Load all wallet records
   */
  private async loadRecords(): Promise<Record<string, UserWalletRecord>> {
    await this.ensureStorageExists();

    try {
      const content = await fs.readFile(STORAGE_FILE, 'utf-8');
      return JSON.parse(content);
    } catch {
      return {};
    }
  }

  /**
   * Save all wallet records
   */
  private async saveRecords(records: Record<string, UserWalletRecord>): Promise<void> {
    await this.ensureStorageExists();
    await fs.writeFile(STORAGE_FILE, JSON.stringify(records, null, 2), 'utf-8');
  }

  /**
   * Get wallet for a specific user
   *
   * ⭐ Decrypts private key if present
   */
  async getUserWallet(userId: string): Promise<(UserWalletRecord & { privateKey?: `0x${string}` }) | null> {
    const records = await this.loadRecords();
    const record = records[userId];

    if (!record) {
      return null;
    }

    // Decrypt private key if present
    if (record.encryptedPrivateKey) {
      const secret = process.env.WALLET_ENCRYPTION_SECRET;
      if (!secret) {
        throw new Error('WALLET_ENCRYPTION_SECRET not set - cannot decrypt wallet');
      }

      try {
        const privateKey = decryptPrivateKey(record.encryptedPrivateKey, secret);
        return {
          ...record,
          privateKey,
        };
      } catch (error) {
        console.error('❌ Failed to decrypt private key:', error);
        throw new Error('Failed to decrypt wallet - invalid encryption secret or corrupted data');
      }
    }

    return record;
  }

  /**
   * Save wallet for a specific user
   *
   * ⭐ AgentKit 0.10.4: Only stores address (CDP manages wallet server-side)
   * ⭐ Security: Encrypts private keys with AES-256-GCM before storage
   */
  async saveUserWallet(
    userId: string,
    walletAddress: `0x${string}`,
    network: string,
    privateKey?: `0x${string}`  // ⭐ Optional for local wallets
  ): Promise<void> {
    const records = await this.loadRecords();

    const now = new Date().toISOString();

    // Encrypt private key if provided
    let encryptedPrivateKey: string | undefined;
    if (privateKey) {
      const secret = process.env.WALLET_ENCRYPTION_SECRET;
      if (!secret) {
        throw new Error('WALLET_ENCRYPTION_SECRET not set - cannot encrypt wallet');
      }

      // Validate encryption secret strength
      const validation = validateEncryptionSecret(secret);
      if (!validation.valid) {
        throw new Error(`Invalid encryption secret: ${validation.reason}`);
      }

      encryptedPrivateKey = encryptPrivateKey(privateKey, secret);
    }

    records[userId] = {
      userId,
      walletAddress,
      network,
      createdAt: records[userId]?.createdAt || now,
      lastUsedAt: now,
      ...(encryptedPrivateKey && { encryptedPrivateKey }),  // ⭐ Store encrypted
    };

    await this.saveRecords(records);
  }

  /**
   * Update last used timestamp
   */
  async updateLastUsed(userId: string): Promise<void> {
    const records = await this.loadRecords();

    if (records[userId]) {
      records[userId].lastUsedAt = new Date().toISOString();
      await this.saveRecords(records);
    }
  }

  /**
   * Delete user wallet (for testing/cleanup)
   */
  async deleteUserWallet(userId: string): Promise<void> {
    const records = await this.loadRecords();
    delete records[userId];
    await this.saveRecords(records);
  }

  /**
   * List all users with wallets
   */
  async listUsers(): Promise<string[]> {
    const records = await this.loadRecords();
    return Object.keys(records);
  }

  /**
   * Get wallet count
   */
  async getWalletCount(): Promise<number> {
    const records = await this.loadRecords();
    return Object.keys(records).length;
  }
}

/**
 * Singleton instance
 */
export const walletStorage = new WalletStorage();
