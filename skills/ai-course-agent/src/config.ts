/**
 * Configuration management
 *
 * Reads credentials from environment variables or OpenClaw config
 * Never hardcode credentials in source code!
 */

export interface EdustemConfig {
  username: string;
  password: string;
}

/**
 * Get Edustem API credentials from environment
 */
export function getEdustemConfig(): EdustemConfig {
  const username = process.env.EDUSTEM_USERNAME;
  const password = process.env.EDUSTEM_PASSWORD;

  if (!username || !password) {
    throw new Error(
      "Missing Edustem credentials. Set EDUSTEM_USERNAME and EDUSTEM_PASSWORD environment variables.",
    );
  }

  return { username, password };
}

/**
 * Alternative: Get credentials from OpenClaw gateway token/API
 * This would be called when running as an OpenClaw Skill
 */
export function getEdustemConfigFromGateway(): EdustemConfig {
  // In production, this would fetch from OpenClaw's secure credential store
  // For now, fall back to environment variables
  return getEdustemConfig();
}

export default {
  getEdustemConfig,
  getEdustemConfigFromGateway,
};
