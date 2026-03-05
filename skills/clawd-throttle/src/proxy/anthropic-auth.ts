import type { ThrottleConfig } from '../config/types.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('anthropic-auth');

/**
 * Build authentication headers for Anthropic API calls.
 *
 * - 'api-key': uses x-api-key header (standard Anthropic API)
 * - 'bearer': uses Authorization: Bearer header (OAuth / proxy)
 * - 'auto': detects from key format — sk-ant-* uses api-key, else bearer
 */
export function buildAnthropicAuthHeaders(config: ThrottleConfig): Record<string, string> {
  const { apiKey, authType, baseUrl } = config.anthropic;

  const useApiKey = authType === 'api-key'
    || (authType === 'auto' && apiKey.startsWith('sk-ant-'));

  if (useApiKey) {
    return { 'x-api-key': apiKey };
  }

  if (baseUrl.includes('api.anthropic.com')) {
    log.warn(
      'Bearer auth with api.anthropic.com will likely fail. ' +
      'OAuth/setup-tokens require a proxy (e.g. claude-max-api-proxy). ' +
      'Set ANTHROPIC_BASE_URL to your proxy endpoint.',
    );
  }

  return { 'Authorization': `Bearer ${apiKey}` };
}
