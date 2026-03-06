/** Enterprise lockdown — strict network, explicit domain allowlist, tight rate limits. */
export const ENTERPRISE_CONFIG = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'strict' as const,
  redactPII: true,
  networkPolicy: 'strict' as const,
  allowedDomains: [
    'api.openai.com',
    'api.anthropic.com',
    'tork.network',
    'tork.network',
    'api.tork.network',
  ],
  maxConnectionsPerMinute: 20,
};
