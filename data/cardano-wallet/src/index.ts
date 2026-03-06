/**
 * Cardano Wallet Skill for OpenClaw
 *
 * Generate, manage, and fund Cardano wallets
 *
 * @packageDocumentation
 */

// Wallet utilities
export {
  generateWallet,
  restoreWallet,
  createWalletInstance,
  validateMnemonic,
  type GeneratedWallet,
} from './utils/wallet-generator';

// Credential storage
export {
  saveCredentials,
  loadCredentials,
  credentialsExist,
  deleteCredentials,
  listAllCredentials,
  updateCredentials,
  exportCredentials,
  importCredentials,
  type StoredCredentials,
} from './utils/credential-store';

// Encryption utilities
export {
  encrypt,
  decrypt,
  isEncryptionKeySecure,
  generateEncryptionKey,
} from './utils/encryption';

// QR code generation
export {
  generateWalletFundingQR,
  generateWalletFundingQRFile,
} from './utils/qr-generator';

// Tools
export * from './tools';

// Types
export type { Network } from '../../shared/types/config';
