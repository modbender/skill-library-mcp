import * as fs from 'fs';
import * as path from 'path';

/**
 * Token Manager - Finance Department for API Keys
 * Responsibilities:
 * - Track all API keys and their limits
 * - Monitor token usage across sessions
 * - Allocate optimal keys for tasks
 * - Alert BEFORE exhaustion (75% threshold)
 * - Handle key rotation
 */

export interface APIKey {
  id: string;
  provider: string;
  model: string;
  key: string;
  limits: {
    tokens_per_day: number;
    tokens_per_month: number | null;
    reset_hour_utc: number;
  };
  usage: {
    today: number;
    this_month: number;
    last_reset: string;
  };
  status: 'active' | 'inactive' | 'exhausted';
  cost_per_1k_tokens: number;
  priority: number;
}

export interface Allocation {
  key_id: string;
  allocated_tokens: number;
  rotation_threshold: number;
  used_tokens: number;
  started: string;
  prd: string | null;
  agent_name: string | null;
  alerted: boolean;
  status: 'active' | 'completed' | 'failed';
  rotated_at?: string;
}

export interface AllocationResult {
  success: boolean;
  key_id?: string;
  key?: string;
  provider?: string;
  model?: string;
  allocated?: number;
  rotation_threshold?: number;
  available_capacity?: number;
  cost_estimate?: number;
  message?: string;
  alternatives?: unknown;
  next_reset?: unknown;
}

export class TokenManager {
  private keys: Record<string, APIKey> = {};
  private allocations: Record<string, Allocation> = {};
  private alerts: unknown[] = [];
  private history: unknown[] = [];
  private keysPath: string;
  private statePath: string;

  constructor(
    keysPath = '/home/tokisaki/.openclaw/workspace/api-keys.json',
    statePath = '/home/tokisaki/.openclaw/workspace/token-manager-state.json'
  ) {
    this.keysPath = keysPath;
    this.statePath = statePath;
    this.initialize();
  }

  private initialize(): void {
    // Load API keys
    if (fs.existsSync(this.keysPath)) {
      const rawKeys = JSON.parse(fs.readFileSync(this.keysPath, 'utf8'));
      this.loadKeysFromRaw(rawKeys);
    } else {
      console.error(`❌ API keys file not found: ${this.keysPath}`);
      process.exit(1);
    }

    // Load or create state
    if (fs.existsSync(this.statePath)) {
      const state = JSON.parse(fs.readFileSync(this.statePath, 'utf8'));
      this.allocations = state.allocations || {};
      this.alerts = state.alerts || [];
      this.history = state.history || [];

      // Merge usage data
      if (state.keys) {
        Object.keys(state.keys).forEach(keyId => {
          if (this.keys[keyId]) {
            this.keys[keyId].usage = state.keys[keyId].usage;
          }
        });
      }
    }

    this.checkDailyReset();
  }

  private loadKeysFromRaw(rawKeys: Record<string, unknown>): void {
    const providerConfigs: Record<string, any> = {
      nvidia: {
        model: 'nvidia/llama-3.1-nemotron-70b-instruct',
        tokens_per_day: 5000000,
        tokens_per_month: null,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.0,
        priority: 1
      },
      anthropic: {
        model: 'anthropic/claude-sonnet-4-5',
        tokens_per_day: 1000000,
        tokens_per_month: 30000000,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.015,
        priority: 3
      },
      openai: {
        model: 'openai/gpt-4-turbo',
        tokens_per_day: 500000,
        tokens_per_month: 15000000,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.01,
        priority: 2
      },
      groq: {
        model: 'groq/llama-3.1-70b-versatile',
        tokens_per_day: 10000000,
        tokens_per_month: null,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.0,
        priority: 1
      },
      'openrouter-zen': {
        model: 'anthropic/claude-sonnet-4-5',
        tokens_per_day: 2000000,
        tokens_per_month: null,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.02,
        priority: 2
      }
    };

    Object.entries(rawKeys).forEach(([provider, keys]) => {
      const config = providerConfigs[provider] || {
        model: 'unknown',
        tokens_per_day: 100000,
        tokens_per_month: null,
        reset_hour_utc: 0,
        cost_per_1k_tokens: 0.01,
        priority: 0
      };

      const keyArray = Array.isArray(keys) ? keys : [keys];

      keyArray.forEach((keyValue: any, index: number) => {
        const keyId = `${provider}-${index + 1}`;
        this.keys[keyId] = {
          id: keyId,
          provider,
          model: config.model,
          key: keyValue,
          limits: {
            tokens_per_day: config.tokens_per_day,
            tokens_per_month: config.tokens_per_month,
            reset_hour_utc: config.reset_hour_utc
          },
          usage: {
            today: 0,
            this_month: 0,
            last_reset: new Date().toISOString().split('T')[0] + 'T00:00:00Z'
          },
          status: 'active',
          cost_per_1k_tokens: config.cost_per_1k_tokens,
          priority: config.priority
        };
      });
    });

    console.log(`✅ Loaded ${Object.keys(this.keys).length} API keys from ${Object.keys(rawKeys).length} providers`);
  }

  private checkDailyReset(): void {
    const now = new Date();
    const today = now.toISOString().split('T')[0];

    Object.values(this.keys).forEach(key => {
      const lastReset = new Date(key.usage.last_reset);
      const lastResetDate = lastReset.toISOString().split('T')[0];

      if (lastResetDate !== today) {
        key.usage.today = 0;
        key.usage.last_reset = today + 'T00:00:00Z';
        console.log(`🔄 Reset daily usage for ${key.id}`);
      }
    });

    this.save();
  }

  public estimateTokensForPRD(prdPath: string): { estimated: number; confidence: number; reasoning: string } {
    if (!fs.existsSync(prdPath)) {
      return {
        estimated: 100000,
        confidence: 0.3,
        reasoning: 'PRD file not found - using default estimate'
      };
    }

    const prd = fs.readFileSync(prdPath, 'utf8');
    const lines = prd.split('\n').length;
    const words = prd.split(/\s+/).length;

    const hasCode = prd.includes('```');
    const hasAPI = prd.includes('API') || prd.includes('endpoint');
    const hasIntegration = prd.includes('integration') || prd.includes('integrate');
    const hasSubAgents = prd.includes('sub-agent') || prd.includes('spawn');
    const isP0 = prd.includes('P0') || prd.includes('CRITICAL');

    let base = Math.ceil(words / 0.75);
    let multiplier = 1.0;

    if (hasCode) multiplier += 2.0;
    if (hasAPI) multiplier += 1.5;
    if (hasIntegration) multiplier += 1.5;
    if (hasSubAgents) multiplier += 1.0;
    if (isP0) multiplier += 0.5;

    if (lines > 500) multiplier += 1.0;
    if (words > 5000) multiplier += 1.0;

    const estimated = Math.ceil(base * multiplier);
    let confidence = 0.6;

    if (hasCode || hasAPI) confidence += 0.1;
    if (hasIntegration) confidence += 0.1;
    confidence = Math.min(confidence, 0.95);

    return {
      estimated,
      confidence,
      reasoning: `PRD analysis: ${words} words, ${lines} lines. ` +
        `Detected: ${hasCode ? 'code' : ''} ${hasAPI ? 'API' : ''} ${hasIntegration ? 'integration' : ''}. ` +
        `Multiplier: ${multiplier.toFixed(1)}x`
    };
  }

  public getAvailableKeys(): APIKey[] {
    return Object.values(this.keys).filter(key => {
      if (key.status !== 'active') return false;
      const available = key.limits.tokens_per_day - key.usage.today;
      return available > 10000;
    });
  }

  public selectKey(requiredTokens: number, preferredProvider: string | null = null): AllocationResult {
    const available = this.getAvailableKeys();

    if (available.length === 0) {
      return {
        success: false,
        message: 'No keys available with sufficient capacity',
        next_reset: this.getNextResetTime()
      };
    }

    let candidates = preferredProvider
      ? available.filter(k => k.provider === preferredProvider)
      : available;

    if (candidates.length === 0 && preferredProvider) {
      console.warn(`⚠️ No available keys for provider ${preferredProvider}, expanding search`);
      candidates = available;
    }

    candidates = candidates.filter(k => {
      const capacity = k.limits.tokens_per_day - k.usage.today;
      return capacity >= requiredTokens;
    });

    if (candidates.length === 0) {
      return {
        success: false,
        message: `No single key has ${requiredTokens} tokens available`
      };
    }

    candidates.sort((a, b) => {
      if (a.priority !== b.priority) return b.priority - a.priority;
      const aCapacity = a.limits.tokens_per_day - a.usage.today;
      const bCapacity = b.limits.tokens_per_day - b.usage.today;
      if (aCapacity !== bCapacity) return bCapacity - aCapacity;
      return a.cost_per_1k_tokens - b.cost_per_1k_tokens;
    });

    const best = candidates[0];
    const rotationThreshold = Math.floor(requiredTokens * 0.75); // 75% threshold

    return {
      success: true,
      key_id: best.id,
      key: best.key,
      provider: best.provider,
      model: best.model,
      allocated: requiredTokens,
      rotation_threshold: rotationThreshold,
      available_capacity: best.limits.tokens_per_day - best.usage.today,
      cost_estimate: (requiredTokens / 1000) * best.cost_per_1k_tokens
    };
  }

  public trackSession(sessionId: string, allocation: AllocationResult, metadata: Record<string, unknown> = {}): void {
    this.allocations[sessionId] = {
      key_id: allocation.key_id || '',
      allocated_tokens: allocation.allocated || 0,
      rotation_threshold: allocation.rotation_threshold || 0,
      used_tokens: 0,
      started: new Date().toISOString(),
      prd: (metadata.prd as string) || null,
      agent_name: (metadata.agent_name as string) || null,
      alerted: false,
      status: 'active'
    };

    this.history.push({
      timestamp: new Date().toISOString(),
      action: 'allocation',
      session: sessionId,
      key_id: allocation.key_id,
      tokens: allocation.allocated
    });

    this.save();
  }

  public updateUsage(sessionId: string, tokensUsed: number): void {
    const allocation = this.allocations[sessionId];
    if (!allocation) {
      console.warn(`⚠️ Session ${sessionId} not found`);
      return;
    }

    allocation.used_tokens = tokensUsed;

    const key = this.keys[allocation.key_id];
    if (key) {
      key.usage.today += tokensUsed;
      key.usage.this_month += tokensUsed;
    }

    this.save();
  }

  public monitorSession(sessionId: string): boolean {
    const allocation = this.allocations[sessionId];
    if (!allocation) return false;

    const usage = allocation.used_tokens;
    const threshold = allocation.rotation_threshold;

    if (usage >= threshold && !allocation.alerted) {
      console.log(`🔄 [${sessionId}] 75% budget used - Rotation recommended`);
      allocation.alerted = true;
      this.save();
      return true;
    }

    return false;
  }

  private getNextResetTime(): { timestamp: string; hours_until: string } {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);

    const hoursUntil = (tomorrow.getTime() - now.getTime()) / (1000 * 60 * 60);
    return {
      timestamp: tomorrow.toISOString(),
      hours_until: hoursUntil.toFixed(1)
    };
  }

  public getStatus(): Record<string, any> {
    const summary: Record<string, any> = {
      timestamp: new Date().toISOString(),
      total_keys: Object.keys(this.keys).length,
      active_keys: Object.values(this.keys).filter(k => k.status === 'active').length,
      active_sessions: Object.values(this.allocations).filter(a => a.status === 'active').length,
      pending_alerts: this.alerts.length,
      keys_by_provider: {}
    };

    Object.values(this.keys).forEach(key => {
      if (!summary.keys_by_provider[key.provider]) {
        summary.keys_by_provider[key.provider] = {
          count: 0,
          total_capacity: 0,
          used_today: 0,
          remaining: 0,
          cost_today: 0
        };
      }
      const stats = summary.keys_by_provider[key.provider];
      stats.count++;
      stats.total_capacity += key.limits.tokens_per_day || 0;
      stats.used_today += key.usage.today || 0;
      stats.remaining += (key.limits.tokens_per_day || 0) - (key.usage.today || 0);
      stats.cost_today += ((key.usage.today || 0) / 1000) * key.cost_per_1k_tokens;
    });

    return summary;
  }

  private save(): void {
    const state: Record<string, any> = {
      timestamp: new Date().toISOString(),
      keys: {},
      allocations: this.allocations,
      alerts: this.alerts,
      history: this.history
    };

    Object.entries(this.keys).forEach(([keyId, key]) => {
      state.keys[keyId] = {
        usage: key.usage,
        status: key.status
      };
    });

    fs.writeFileSync(this.statePath, JSON.stringify(state, null, 2), 'utf8');
  }
}
