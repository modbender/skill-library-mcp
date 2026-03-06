/**
 * Agent Authentication Types
 *
 * Shared types for Agent Token authentication
 */

/**
 * Agent Token Payload (JWT content)
 */
export interface AgentTokenPayload {
  // Basic info
  type: 'agent';
  version: '1.0';

  // Identity
  address: string;
  agentId?: string;

  // Security params
  nonce: string;
  timestamp: number;
  expiresAt: number;

  // Permissions
  scope: string[];

  // Signature
  signature: string;
  signedMessage: string;

  // Optional: IP binding
  clientIp?: string;
  userAgent?: string;

  // JWT standard fields
  iss?: string; // issuer
  aud?: string; // audience
  exp?: number; // expiration
  iat?: number; // issued at
}

/**
 * Agent Scopes (permissions)
 */
export enum AgentScope {
  READ_IDENTITY = 'read:identity',
  READ_SKILLS = 'read:skills',
  READ_WALLET = 'read:wallet',
  // Future: write permissions require re-signature
  // WRITE_SETTINGS = 'write:settings',
  // TIP_CREATOR = 'tip:creator',
}

/**
 * Agent Session (after token verification)
 */
export interface AgentSession {
  sessionId: string;
  address: string;
  scope: string[];
  createdAt: number;
  expiresAt: number;
}

/**
 * Auth verification result
 */
export interface AuthVerificationResult {
  success: boolean;
  session?: AgentSession;
  agentData?: any;
  error?: string;
}
