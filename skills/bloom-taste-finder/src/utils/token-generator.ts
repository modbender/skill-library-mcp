/**
 * JWT Token Generator for Agent Authentication
 *
 * Generates secure JWT tokens with identity metadata for agent dashboard access
 */

import jwt, { SignOptions } from 'jsonwebtoken';
import crypto from 'crypto';
import { IdentityData } from '../bloom-identity-skill-v2';

export interface AgentTokenPayload {
  // Agent identification
  type: 'agent';
  version: '1.0';
  address: string;
  agentUserId?: number;

  // Identity metadata (for fallback if backend unavailable)
  identity: {
    personalityType: string;
    tagline: string;
    description: string;
    mainCategories: string[];
    subCategories: string[];
    confidence: number;
    mode: 'data' | 'manual';
  };

  // Security
  nonce: string;
  timestamp: number;
  expiresAt: number;

  // Permissions
  scope: string[];

  // JWT standard fields (automatically added by jwt.sign)
  iss?: string;  // issuer
  aud?: string;  // audience
  exp?: number;  // expiration
  iat?: number;  // issued at
}

export interface TokenGenerationOptions {
  walletAddress: string;
  agentUserId?: number;
  identityData: IdentityData;
  dataQuality: number;
  mode: 'data' | 'manual';
}

/**
 * Generate JWT token for agent authentication
 */
export function generateAgentToken(options: TokenGenerationOptions): string {
  const jwtSecret = process.env.JWT_SECRET;

  if (!jwtSecret) {
    throw new Error('JWT_SECRET not found in environment variables');
  }

  const {
    walletAddress,
    agentUserId,
    identityData,
    dataQuality,
    mode,
  } = options;

  // Generate nonce for replay attack prevention
  const nonce = crypto.randomUUID();
  const timestamp = Date.now();
  const expiresAt = timestamp + 24 * 60 * 60 * 1000; // 24 hours

  // Construct token payload
  const payload: AgentTokenPayload = {
    type: 'agent',
    version: '1.0',
    address: walletAddress,
    agentUserId,
    identity: {
      personalityType: identityData.personalityType,
      tagline: identityData.customTagline,
      description: identityData.customDescription,
      mainCategories: identityData.mainCategories,
      subCategories: identityData.subCategories,
      confidence: dataQuality,
      mode,
    },
    nonce,
    timestamp,
    expiresAt,
    scope: ['read:identity', 'read:skills', 'read:wallet'],
  };

  // Sign the token
  const token = jwt.sign(payload, jwtSecret, {
    algorithm: 'HS256',
    expiresIn: '24h',  // Fixed: always use 24h for agent tokens
    issuer: 'bloom-protocol',
    audience: 'bloom-dashboard',
  });

  return token;
}

/**
 * Verify JWT token (for testing)
 */
export function verifyAgentToken(token: string): AgentTokenPayload {
  const jwtSecret = process.env.JWT_SECRET;

  if (!jwtSecret) {
    throw new Error('JWT_SECRET not found in environment variables');
  }

  const decoded = jwt.verify(token, jwtSecret, {
    issuer: 'bloom-protocol',
    audience: 'bloom-dashboard',
    algorithms: ['HS256'],
  }) as AgentTokenPayload;

  return decoded;
}
