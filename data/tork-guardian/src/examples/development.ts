/** Dev-friendly config — permissive policies, full logging. */
export const DEVELOPMENT_CONFIG = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'minimal' as const,
  redactPII: true,
  networkPolicy: 'default' as const,
};
