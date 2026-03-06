import type { ProxyRequest, ProxyResponse, StreamingProxyResult, ProviderConfig } from './types.js';
import type { ThrottleConfig } from '../config/types.js';
import type { ApiProvider } from '../router/types.js';
import { callAnthropic } from './anthropic.js';
import { callGoogle } from './google.js';
import { callAnthropicStream } from './anthropic-stream.js';
import { callGoogleStream } from './google-stream.js';
import { callOpenAiCompat } from './openai-compat.js';
import { callOpenAiCompatStream } from './openai-compat-stream.js';

/**
 * Extract { apiKey, baseUrl } for any provider from the config.
 */
export function getProviderConfig(provider: ApiProvider, config: ThrottleConfig): ProviderConfig {
  const section = config[provider] as { apiKey: string; baseUrl: string };
  return { apiKey: section.apiKey, baseUrl: section.baseUrl };
}

export async function dispatch(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<ProxyResponse> {
  switch (request.provider) {
    case 'anthropic':
      return callAnthropic(request, config);
    case 'google':
      return callGoogle(request, config);
    default:
      // OpenAI, DeepSeek, xAI, Moonshot, Mistral, Ollama
      return callOpenAiCompat(request, getProviderConfig(request.provider, config));
  }
}

export async function streamDispatch(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<StreamingProxyResult> {
  switch (request.provider) {
    case 'anthropic':
      return callAnthropicStream(request, config);
    case 'google':
      return callGoogleStream(request, config);
    default:
      // OpenAI, DeepSeek, xAI, Moonshot, Mistral, Ollama
      return callOpenAiCompatStream(request, getProviderConfig(request.provider, config));
  }
}
