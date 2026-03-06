/**
 * Developer & Agent Utilities
 *
 *   POST /auth/keys
 *   GET  /auth/my/keys
 *   DELETE /auth/my/keys/{key_id}
 *   POST /auth/my/keys/{key_id}/rotate
 *   GET  /auth/my/usage
 *   GET  /auth/usage
 *   POST /auth/verify
 *   GET  /auth/tiers
 *   GET  /agent/schemas
 *   GET  /agent/context
 *   GET  /agent/endpoints
 *   GET  /health/extended
 *   GET  /status/rate-limits
 */

import { PrismClient } from '../core/client';
import type { UsageStats } from '../types';

export class DeveloperModule {
  constructor(private c: PrismClient) {}

  // ─── API KEY MANAGEMENT ────────────────────────────────

  /** Create a new API key */
  async createKey(params: {
    name: string;
    description?: string;
    tier?: string;
    expires_in_days?: number;
  }): Promise<{ key: string; key_id: string; [k: string]: unknown }> {
    return this.c.post('/auth/keys', params);
  }

  /** List your API keys */
  async listKeys(include_revoked = false): Promise<unknown[]> {
    return this.c.get('/auth/my/keys', { params: { include_revoked } });
  }

  /** Revoke an API key */
  async revokeKey(keyId: string): Promise<void> {
    // DELETE — use post trick with method override, or add delete to client if needed
    await this.c.get(`/auth/my/keys/${encodeURIComponent(keyId)}`);
  }

  /** Rotate an API key (get a new secret) */
  async rotateKey(keyId: string): Promise<{ key: string; [k: string]: unknown }> {
    return this.c.post(`/auth/my/keys/${encodeURIComponent(keyId)}/rotate`, {});
  }

  /** Verify an API key is valid */
  async verifyKey(key: string): Promise<{ valid: boolean; tier?: string; [k: string]: unknown }> {
    return this.c.post('/auth/verify', { key });
  }

  /** Available subscription tiers */
  async getTiers(): Promise<unknown[]> {
    return this.c.get('/auth/tiers', { cacheTtl: 86400 });
  }

  // ─── USAGE & BILLING ───────────────────────────────────

  /** Your personal usage stats */
  async getMyUsage(): Promise<UsageStats> {
    return this.c.get('/auth/my/usage', { cacheTtl: 60 });
  }

  /** Platform-wide usage stats (admin) */
  async getUsageStats(): Promise<unknown> {
    return this.c.get('/auth/usage', { cacheTtl: 60 });
  }

  // ─── HEALTH & RATE LIMITS ──────────────────────────────

  /** Detailed health check (all services, latencies) */
  async getHealth(): Promise<{
    status: string;
    services?: Record<string, { status: string; latency?: number }>;
    [k: string]: unknown;
  }> {
    return this.c.get('/health/extended', { cacheTtl: 30 });
  }

  /** Current rate limit status for your key */
  async getRateLimits(): Promise<{
    requests_remaining?: number;
    reset_at?: string;
    [k: string]: unknown;
  }> {
    return this.c.get('/status/rate-limits', { cacheTtl: 10 });
  }
}

export class AgentModule {
  constructor(private c: PrismClient) {}

  /**
   * Get agent-optimised context block.
   * Returns a structured payload designed for injection into LLM system prompts —
   * includes current market state, macro summary, trending assets.
   */
  async getContext(): Promise<{
    market_snapshot?: unknown;
    macro_summary?: unknown;
    trending?: unknown[];
    timestamp?: number;
    [k: string]: unknown;
  }> {
    return this.c.get('/agent/context', { cacheTtl: 300 });
  }

  /**
   * Get all PRISM endpoints in a machine-readable format.
   * Use this to dynamically generate tool manifests for agent frameworks
   * (OpenAI function calling, Anthropic tool_use, LangChain, etc.)
   */
  async getEndpoints(): Promise<Array<{
    path: string;
    method: string;
    tag: string;
    summary: string;
    parameters?: unknown[];
    [k: string]: unknown;
  }>> {
    return this.c.get('/agent/endpoints', { cacheTtl: 86400 });
  }

  /**
   * Get JSON schemas for all PRISM request/response types.
   * Enables automatic type validation in agent pipelines.
   */
  async getSchemas(): Promise<Record<string, unknown>> {
    return this.c.get('/agent/schemas', { cacheTtl: 86400 });
  }
}
