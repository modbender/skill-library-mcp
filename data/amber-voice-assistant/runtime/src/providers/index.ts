/**
 * Voice provider factory and registry.
 *
 * Usage:
 *   import { createProvider } from './providers/index.js';
 *   const provider = createProvider(process.env.VOICE_PROVIDER ?? 'twilio', config);
 *
 * Supported providers:
 *   'twilio'  — Default. Full implementation. Production-ready.
 *   'telnyx'  — Stub. ~40-60% cheaper than Twilio. Implement before use.
 */

export type {
  IVoiceProvider,
  ProviderConfig,
  CallResult,
  OutboundCallParams,
  SipBridgeParams,
} from './types.js';

export { TwilioProvider } from './twilio.js';
export type { TwilioProviderConfig } from './twilio.js';

export { TelnyxProvider } from './telnyx.js';
export type { TelnyxProviderConfig } from './telnyx.js';

import { TwilioProvider } from './twilio.js';
import type { TwilioProviderConfig } from './twilio.js';
import { TelnyxProvider } from './telnyx.js';
import type { TelnyxProviderConfig } from './telnyx.js';
import type { IVoiceProvider, ProviderConfig } from './types.js';

const SUPPORTED_PROVIDERS = ['twilio', 'telnyx'] as const;
type SupportedProvider = (typeof SUPPORTED_PROVIDERS)[number];

/**
 * Instantiate a voice provider by name.
 *
 * @param name   Provider key (case-insensitive). Defaults to 'twilio'.
 *               Read from the VOICE_PROVIDER environment variable.
 * @param config Provider-specific config. Cast to the appropriate typed interface
 *               by each provider's constructor.
 *
 * @throws       If `name` is not a supported provider key.
 *
 * @example
 *   const provider = createProvider('twilio', {
 *     accountSid: process.env.TWILIO_ACCOUNT_SID!,
 *     authToken:  process.env.TWILIO_AUTH_TOKEN!,
 *     openAiProjectId: process.env.OPENAI_PROJECT_ID!,
 *   });
 */
export function createProvider(
  name: string = 'twilio',
  config: ProviderConfig = {}
): IVoiceProvider {
  switch (name.toLowerCase() as SupportedProvider) {
    case 'twilio':
      return new TwilioProvider(config as unknown as TwilioProviderConfig);

    case 'telnyx':
      return new TelnyxProvider(config as unknown as TelnyxProviderConfig);

    default:
      throw new Error(
        `Unknown voice provider: "${name}". ` +
          `Supported providers: ${SUPPORTED_PROVIDERS.join(', ')}. ` +
          'Set VOICE_PROVIDER in your .env to a supported value.'
      );
  }
}
