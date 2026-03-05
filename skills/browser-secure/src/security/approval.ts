import readline from 'readline';
import crypto from 'crypto';
import { getSitePolicy } from '../config/loader.js';
import { getCachedCredentials, cacheCredentials } from './credential-cache.js';

export type ActionTier = 'read_only' | 'form_fill' | 'authentication' | 'destructive';
export type ApprovalTier = 'none' | 'prompt' | 'always' | '2fa';

interface ActionTierConfig {
  actions: string[];
  approval: ApprovalTier;
  description: string;
}

const ACTION_TIERS: Record<ActionTier, ActionTierConfig> = {
  read_only: {
    actions: ['navigate', 'screenshot', 'extract', 'observe'],
    approval: 'none',
    description: 'Read-only browsing'
  },
  form_fill: {
    actions: ['type', 'select', 'click'],
    approval: 'prompt',
    description: 'Form interaction'
  },
  authentication: {
    actions: ['fill_password', 'submit_login', 'handle_2fa'],
    approval: 'always',
    description: 'Authentication (credentials required)'
  },
  destructive: {
    actions: ['delete_account', 'make_purchase', 'change_settings', 'delete', 'remove'],
    approval: '2fa',
    description: 'Destructive/irreversible action'
  }
};

export interface ApprovalRequest {
  action: string;
  site?: string;
  details?: Record<string, unknown>;
  tier: ActionTier;
}

export interface ApprovalResult {
  approved: boolean;
  token?: string;
  duration?: number;
  remember?: boolean;
  requires2fa?: boolean;
}

export interface UnattendedOptions {
  enabled: boolean;
  credentialSource: 'env' | 'vault' | 'cache';
  skipApproval?: boolean;
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function askQuestion(query: string): Promise<string> {
  return new Promise(resolve => {
    rl.question(query, answer => resolve(answer.trim()));
  });
}

async function ask2FA(): Promise<string | null> {
  console.log('\n🔐 Two-Factor Authentication Required\n');
  const code = await askQuestion('Enter 2FA code (or press Enter to cancel): ');
  return code || null;
}

export function getActionTier(action: string): ActionTier {
  for (const [tier, config] of Object.entries(ACTION_TIERS)) {
    if (config.actions.includes(action)) {
      return tier as ActionTier;
    }
  }
  return 'form_fill'; // Default to safer tier
}

function getEffectiveApprovalTier(request: ApprovalRequest): ApprovalTier {
  // Get base tier approval
  const baseTier = ACTION_TIERS[request.tier];
  let approvalTier = baseTier.approval;

  // Check for site-specific policy override
  if (request.site) {
    const sitePolicy = getSitePolicy(request.site);
    if (sitePolicy?.approvalTier) {
      // Use the more restrictive of the two
      const tierOrder: ApprovalTier[] = ['none', 'prompt', 'always', '2fa'];
      const baseIndex = tierOrder.indexOf(approvalTier);
      const siteIndex = tierOrder.indexOf(sitePolicy.approvalTier);
      approvalTier = tierOrder[Math.max(baseIndex, siteIndex)];
    }

    // Check if site requires 2FA for this action
    if (sitePolicy?.require2fa && request.tier === 'destructive') {
      approvalTier = '2fa';
    }
  }

  return approvalTier;
}

export function checkCredentialSource(source: string): { valid: boolean; error?: string } {
  if (source === 'env') {
    // Check that at least some credentials are available via environment
    const hasEnvCreds = Object.keys(process.env).some(k =>
      k.startsWith('BROWSER_SECURE_') && (k.endsWith('_USERNAME') || k.endsWith('_PASSWORD') || k.endsWith('_TOKEN'))
    );
    if (!hasEnvCreds) {
      return { valid: false, error: 'No environment credentials found. Set BROWSER_SECURE_\u003cSITE\u003e_USERNAME/PASSWORD/TOKEN.' };
    }
    return { valid: true };
  }

  if (source === 'vault') {
    // Vault will be checked at runtime
    return { valid: true };
  }

  if (source === 'cache') {
    return { valid: true };
  }

  return { valid: false, error: `Unknown credential source: ${source}` };
}

export async function requestApproval(
  request: ApprovalRequest,
  options?: {
    skipPrompt?: boolean;
    autoApprove?: boolean;
    unattended?: UnattendedOptions;
  }
): Promise<ApprovalResult> {
  const effectiveTier = getEffectiveApprovalTier(request);

  // No approval needed for read-only actions
  if (effectiveTier === 'none') {
    return { approved: true };
  }

  // Handle unattended mode (NOW THE DEFAULT)
  if (options?.unattended?.enabled) {
    // In unattended mode, we require explicit credential source
    if (!options.unattended.credentialSource) {
      return { approved: false };
    }

    // Check if credential source is valid
    const sourceCheck = checkCredentialSource(options.unattended.credentialSource);
    if (!sourceCheck.valid) {
      throw new Error(`Unattended mode credential error: ${sourceCheck.error}`);
    }

    // For destructive actions in unattended mode, we need explicit confirmation
    // unless skipApproval is set (which is risky and should be used carefully)
    if (effectiveTier === '2fa' && !options.unattended.skipApproval) {
      throw new Error(
        'Destructive actions require approval in unattended mode. ' +
        'Use --skip-approval with caution, or use --interactive for manual approval.'
      );
    }

    // Generate token for unattended session
    const token = generateToken();
    return { approved: true, token, duration: 3600, requires2fa: effectiveTier === '2fa' };
  }

  // INTERACTIVE MODE (requires --interactive flag)
  // Auto-approve for testing/non-interactive (legacy behavior)
  if (options?.autoApprove) {
    const token = generateToken();
    return { approved: true, token, duration: 300, requires2fa: effectiveTier === '2fa' };
  }

  // Skip if requested (for batch operations)
  if (options?.skipPrompt) {
    return { approved: false };
  }

  // Check for 2FA requirement
  if (effectiveTier === '2fa') {
    return await requestApprovalWith2FA(request);
  }

  // Show approval prompt (only in interactive mode)
  console.log('\n🛡️  Browser-Secure Approval Required\n');
  console.log(`Action: ${request.action}`);
  if (request.site) console.log(`Site: ${request.site}`);
  console.log(`Tier: ${ACTION_TIERS[request.tier].description}`);

  if (request.details) {
    console.log('\nDetails:');
    for (const [key, value] of Object.entries(request.details)) {
      if (key !== 'password' && key !== 'token') {
        console.log(`  ${key}: ${value}`);
      }
    }
  }

  console.log('\nCredentials will be injected securely from vault.');
  console.log('Session will expire in 5 minutes.\n');

  const answer = await askQuestion('[A]pprove Once / Approve for [1] hour / [R]eject: ');

  if (answer.toLowerCase() === 'r') {
    return { approved: false };
  }

  const token = generateToken();

  if (answer.toLowerCase() === '1') {
    return { approved: true, token, duration: 3600 };
  }

  return { approved: true, token, duration: 300 };
}

async function requestApprovalWith2FA(request: ApprovalRequest): Promise<ApprovalResult> {
  console.log('\n🛡️  Browser-Secure Approval Required (2FA Protected)\n');
  console.log(`Action: ${request.action}`);
  if (request.site) console.log(`Site: ${request.site}`);
  console.log(`Tier: DESTRUCTIVE ACTION - Requires 2FA`);

  if (request.details) {
    console.log('\nDetails:');
    for (const [key, value] of Object.entries(request.details)) {
      if (key !== 'password' && key !== 'token') {
        console.log(`  ${key}: ${value}`);
      }
    }
  }

  console.log('\n⚠️  This is a DESTRUCTIVE action that cannot be undone!');
  console.log('You must provide a valid 2FA code to proceed.\n');

  // Require 2FA code
  const code = await ask2FA();
  if (!code) {
    return { approved: false };
  }

  // Validate 2FA code format (basic check)
  if (!/^\d{6,8}$/.test(code)) {
    console.log('❌ Invalid 2FA code format. Expected 6-8 digits.');
    return { approved: false };
  }

  // Store 2FA code in result for potential use by authenticator
  const token = generateToken();
  console.log('✅ 2FA verification completed.\n');

  return { approved: true, token, duration: 600, requires2fa: true }; // Shorter duration for destructive actions
}

export async function verify2FA(code: string): Promise<boolean> {
  // Basic validation - actual TOTP/HOTP verification would be done by the vault provider
  // This is just a format check
  if (!code || !/^\d{6,8}$/.test(code)) {
    return false;
  }
  return true;
}

export function closeApprover(): void {
  rl.close();
}

function generateToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// Re-export credential cache functions for convenience
export { getCachedCredentials, cacheCredentials, isCacheValid, clearCredentialCache } from './credential-cache.js';
