/**
 * Tork Guardian — Configuration schema and shared types.
 *
 * Uses Zod for runtime validation of user-supplied config.
 * All governance modules import their types from here.
 */

import { z } from 'zod';

export const TorkConfigSchema = z.object({
  apiKey: z.string().min(1),
  baseUrl: z.string().url().default('https://tork.network'),
  policy: z.enum(['strict', 'standard', 'minimal']).default('standard'),
  redactPII: z.boolean().default(true),
  blockShellCommands: z.array(z.string()).default([
    'rm -rf',
    'mkfs',
    'dd if=',
    'chmod 777',
    ':(){:|:&};:',
    'shutdown',
    'reboot',
    'halt',
    'init 0',
    'init 6',
  ]),
  allowedPaths: z.array(z.string()).default([]),
  blockedPaths: z.array(z.string()).default([
    '/etc/shadow',
    '/etc/passwd',
    '~/.ssh',
    '~/.aws',
    '~/.env',
    '.env',
    '.env.local',
    'credentials.json',
    'id_rsa',
    'id_ed25519',
  ]),

  // Network policy configuration
  networkPolicy: z.enum(['default', 'strict', 'custom']).default('default'),
  allowedInboundPorts: z.array(z.number().int().min(0).max(65535)).optional(),
  allowedOutboundPorts: z.array(z.number().int().min(0).max(65535)).optional(),
  allowedDomains: z.array(z.string()).optional(),
  blockedDomains: z.array(z.string()).optional(),
  maxConnectionsPerMinute: z.number().int().min(1).optional(),
});

export type TorkConfig = z.infer<typeof TorkConfigSchema>;

export interface GovernOptions {
  mode?: 'detect' | 'redact' | 'deny';
}

export interface GovernResponse {
  action: 'allow' | 'redact' | 'deny';
  output: string;
  pii_detected?: { type: string; count: number }[];
  receipt?: {
    receipt_id: string;
    timestamp: string;
    policy_version: string;
  };
  usage?: {
    calls_used: number;
    calls_limit: number;
    calls_remaining: number;
  };
}

export interface ToolCallDecision {
  allowed: boolean;
  reason?: string;
  modified_args?: Record<string, unknown>;
}

export interface NetworkPolicyConfig {
  networkPolicy: 'default' | 'strict' | 'custom';
  allowedInboundPorts: number[];
  allowedOutboundPorts: number[];
  allowedDomains: string[];
  blockedDomains: string[];
  maxConnectionsPerMinute: number;
  detectPortHijacking: boolean;
  detectReverseShells: boolean;
  blockPrivilegedPorts: boolean;
  blockPrivateNetworks: boolean;
  logAllActivity: boolean;
}

export interface NetworkDecision {
  allowed: boolean;
  reason?: string;
}

export interface NetworkActivityLog {
  timestamp: string;
  skillId: string;
  action: string;
  allowed: boolean;
  reason: string;
}
