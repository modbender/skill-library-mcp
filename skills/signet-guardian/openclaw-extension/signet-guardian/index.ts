/**
 * OpenClaw extension: Signet Guardian policy config schema + UI hints.
 * Register signet.policy in the Gateway config so the Control UI can render
 * editable fields in Settings.
 *
 * Install: copy or link this folder into your OpenClaw workspace:
 *   .openclaw/extensions/signet-guardian/
 * (e.g. from this repo: openclaw-extension/signet-guardian/)
 */

export const version = 1;
export const generatedAt = new Date().toISOString();

/** Schema fragment for signet.policy. Merge into Gateway config.schema. */
export const schema = {
  signet: {
    type: 'object',
    description: 'Signet Guardian payment guard',
    properties: {
      policy: {
        type: 'object',
        description: 'Payment policy (limits, switch, merchants)',
        properties: {
          paymentsEnabled: {
            type: 'boolean',
            description: 'Master switch for payments',
            default: false,
          },
          maxPerTransaction: {
            type: 'number',
            minimum: 0,
            description: 'Max amount per single transaction',
            default: 20,
          },
          maxPerMonth: {
            type: 'number',
            minimum: 0,
            description: 'Max total spend in the current calendar month',
            default: 500,
          },
          currency: {
            type: 'string',
            pattern: '^[A-Z]{3}$',
            description: 'ISO 4217 currency code (e.g. GBP, USD)',
            default: 'GBP',
          },
          requireConfirmationAbove: {
            type: 'number',
            minimum: 0,
            description: 'Above this amount, require explicit user confirmation',
            default: 5,
          },
          blockedMerchants: {
            type: 'array',
            items: { type: 'string' },
            description: 'Payee substrings to block',
            default: [],
          },
          allowedMerchants: {
            type: 'array',
            items: { type: 'string' },
            description: 'If non-empty, only these payee substrings are allowed',
            default: [],
          },
        },
        default: {
          paymentsEnabled: false,
          maxPerTransaction: 20,
          maxPerMonth: 500,
          currency: 'GBP',
          requireConfirmationAbove: 5,
          blockedMerchants: [],
          allowedMerchants: [],
        },
      },
    },
  },
} as const;

/** UI hints keyed by config path. Control UI uses these for labels and help. */
export const uiHints: Record<string, { label?: string; help?: string; group?: string; order?: number; advanced?: boolean; sensitive?: boolean; placeholder?: string }> = {
  'signet.policy': {
    label: 'Signet Guardian — Payment policy',
    help: 'Payment guard: master switch, per-transaction and monthly limits, currency, confirmation threshold, and merchant allow/block lists.',
    group: 'Skills',
    order: 100,
  },
  'signet.policy.paymentsEnabled': {
    label: 'Enable payments',
    help: 'Master switch. If off, all payments are denied.',
    order: 1,
  },
  'signet.policy.maxPerTransaction': {
    label: 'Max per transaction',
    help: 'Maximum amount allowed for a single payment (e.g. 20).',
    placeholder: '20',
    order: 2,
  },
  'signet.policy.maxPerMonth': {
    label: 'Max per month',
    help: 'Maximum total spend in the current calendar month (e.g. 500).',
    placeholder: '500',
    order: 3,
  },
  'signet.policy.currency': {
    label: 'Currency',
    help: 'ISO 4217 code, 3 letters uppercase (e.g. GBP, USD).',
    placeholder: 'GBP',
    order: 4,
  },
  'signet.policy.requireConfirmationAbove': {
    label: 'Require confirmation above',
    help: 'Above this amount, the agent must ask for explicit user confirmation before paying.',
    placeholder: '5',
    order: 5,
  },
  'signet.policy.blockedMerchants': {
    label: 'Blocked merchants',
    help: 'Comma-separated or list of payee substrings to block (e.g. gambling, adult).',
    order: 6,
  },
  'signet.policy.allowedMerchants': {
    label: 'Allowed merchants',
    help: 'If set, only payees matching one of these substrings are allowed. Leave empty to allow all (subject to blocked list).',
    order: 7,
    advanced: true,
  },
};

/** Validation: requireConfirmationAbove <= maxPerTransaction (soft warning). */
export function validateSignetPolicy(p: { requireConfirmationAbove?: number; maxPerTransaction?: number }): string | null {
  const above = Number(p?.requireConfirmationAbove ?? 5);
  const max = Number(p?.maxPerTransaction ?? 20);
  if (above > max) return `Confirmation threshold (${above}) should not exceed max per transaction (${max}).`;
  return null;
}

export default { schema, uiHints, version, generatedAt, validateSignetPolicy };
