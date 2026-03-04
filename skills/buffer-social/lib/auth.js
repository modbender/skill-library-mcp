import { BUFFER_API_KEY_URL } from './constants.js';

/**
 * Validates API key presence and basic shape.
 * @param {string|undefined} apiKey
 */
export function validateApiKey(apiKey) {
  if (!apiKey || !apiKey.trim()) {
    throw new Error(
      `Missing Buffer API key. Add BUFFER_API_KEY to your .env file.\nGet one at: ${BUFFER_API_KEY_URL}`
    );
  }

  if (apiKey.length < 10) {
    throw new Error(
      `Invalid Buffer API key format. It looks too short.\nRegenerate your key at: ${BUFFER_API_KEY_URL}`
    );
  }

  return apiKey.trim();
}
