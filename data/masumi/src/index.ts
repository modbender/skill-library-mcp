/**
 * Masumi Payments Skill for OpenClaw
 *
 * Install payment service, generate API keys, register agents, handle payments
 *
 * @packageDocumentation
 */

// Managers
export { PaymentManager } from './managers/payment';
export { RegistryManager } from './managers/registry';

// Services
export { AutoProvisionService } from './services/auto-provision';
export {
  installPaymentService,
  checkPaymentServiceStatus,
  startPaymentService,
  generateApiKey,
  type InstallPaymentServiceOptions,
  type PaymentServiceInstallResult,
  type PaymentServiceStatus,
} from './services/payment-service-installer';

// Utilities
export {
  generateWallet,
  restoreWallet,
  createWalletInstance,
  validateMnemonic,
  type GeneratedWallet,
} from './utils/wallet-generator';

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

export {
  encrypt,
  decrypt,
  isEncryptionKeySecure,
  generateEncryptionKey,
} from './utils/encryption';

export {
  createMasumiInputHash,
  createMasumiOutputHash,
  generateRandomIdentifier,
} from './utils/hashing';

export { ApiClient, ApiError, withRetry } from './utils/api-client';

// Tools
export * from './tools';

// Types
export type {
  Network,
  MasumiPluginConfig,
  PricingTier,
  ProvisionedAgent,
  AutoProvisionParams,
} from '../../shared/types/config';

export type {
  PaymentRequest,
  CreatePaymentParams,
  PaymentState,
  PaymentAction,
  WalletBalance,
  PaymentListResponse,
  PaymentStateChangeEvent,
} from './types/payment';
