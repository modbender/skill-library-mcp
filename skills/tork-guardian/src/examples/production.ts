/** Production config — standard policies, blocked domains, all detection on. */
export const PRODUCTION_CONFIG = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'standard' as const,
  redactPII: true,
  networkPolicy: 'default' as const,
  blockedDomains: [
    'pastebin.com',
    'requestbin.com',
    'ngrok.io',
    'burpcollaborator.net',
    'interact.sh',
    'oastify.com',
    'webhook.site',
  ],
};
