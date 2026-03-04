/**
 * Proxy rotation for avoiding blocks
 */

import { HttpsProxyAgent } from 'https-proxy-agent';
import { SocksProxyAgent } from 'socks-proxy-agent';
import type { Agent } from 'http';
import { createLogger } from '../../utils/logger.js';

const logger = createLogger('proxy-rotator');

export interface Proxy {
  url: string;
  type: 'http' | 'https' | 'socks5';
  lastUsed?: Date;
  failCount: number;
  successCount: number;
}

export interface ProxyRotatorConfig {
  /** Minimum time between uses of the same proxy (ms) */
  cooldownMs?: number;
  /** Max fail rate before removing proxy (0-1) */
  maxFailRate?: number;
  /** Whether to auto-remove failed proxies */
  autoRemove?: boolean;
}

/**
 * Rotates through a pool of proxies with health tracking
 */
export class ProxyRotator {
  private proxies: Proxy[] = [];
  private currentIndex = 0;
  private cooldownMs: number;
  private maxFailRate: number;
  private autoRemove: boolean;

  constructor(config: ProxyRotatorConfig = {}) {
    this.cooldownMs = config.cooldownMs ?? 5000;
    this.maxFailRate = config.maxFailRate ?? 0.5;
    this.autoRemove = config.autoRemove ?? false;
  }

  /**
   * Add proxies from a list of URLs
   */
  addProxies(urls: string[]): void {
    for (const url of urls) {
      const type = this.detectProxyType(url);
      this.proxies.push({
        url,
        type,
        failCount: 0,
        successCount: 0,
      });
    }
    logger.info(`Added ${urls.length} proxies (total: ${this.proxies.length})`);
  }

  /**
   * Get the next available proxy
   */
  getNext(): Proxy | null {
    if (this.proxies.length === 0) {
      return null;
    }

    // Try to find a healthy proxy
    let attempts = 0;
    while (attempts < this.proxies.length) {
      const proxy = this.proxies[this.currentIndex];
      this.currentIndex = (this.currentIndex + 1) % this.proxies.length;

      if (!proxy) {
        attempts++;
        continue;
      }

      // Check fail rate
      const totalRequests = proxy.successCount + proxy.failCount;
      if (totalRequests > 0) {
        const failRate = proxy.failCount / totalRequests;
        if (failRate >= this.maxFailRate) {
          if (this.autoRemove) {
            logger.warn(`Removing proxy ${proxy.url} (fail rate: ${(failRate * 100).toFixed(1)}%)`);
            this.proxies.splice(this.currentIndex, 1);
            if (this.proxies.length === 0) return null;
            this.currentIndex = this.currentIndex % this.proxies.length;
          }
          attempts++;
          continue;
        }
      }

      // Check cooldown
      if (proxy.lastUsed) {
        const elapsed = Date.now() - proxy.lastUsed.getTime();
        if (elapsed < this.cooldownMs) {
          attempts++;
          continue;
        }
      }

      proxy.lastUsed = new Date();
      return proxy;
    }

    // All proxies are on cooldown or degraded, return the first one anyway
    const proxy = this.proxies[0];
    if (proxy) {
      proxy.lastUsed = new Date();
    }
    return proxy ?? null;
  }

  /**
   * Mark a proxy request as successful
   */
  markSuccess(proxy: Proxy): void {
    proxy.successCount++;
  }

  /**
   * Mark a proxy request as failed
   */
  markFailure(proxy: Proxy): void {
    proxy.failCount++;
    logger.debug(
      `Proxy ${proxy.url} failed (${proxy.failCount}/${proxy.successCount + proxy.failCount} requests)`
    );
  }

  /**
   * Create an HTTP agent for a proxy
   */
  createAgent(proxy: Proxy): Agent {
    if (proxy.type === 'socks5') {
      return new SocksProxyAgent(proxy.url);
    }
    return new HttpsProxyAgent(proxy.url);
  }

  /**
   * Get count of available proxies
   */
  getProxyCount(): number {
    return this.proxies.length;
  }

  /**
   * Check if proxies are configured
   */
  hasProxies(): boolean {
    return this.proxies.length > 0;
  }

  /**
   * Get proxy stats
   */
  getStats(): { total: number; healthy: number; degraded: number } {
    let healthy = 0;
    let degraded = 0;

    for (const proxy of this.proxies) {
      const total = proxy.successCount + proxy.failCount;
      if (total === 0 || proxy.failCount / total < this.maxFailRate) {
        healthy++;
      } else {
        degraded++;
      }
    }

    return {
      total: this.proxies.length,
      healthy,
      degraded,
    };
  }

  /**
   * Detect proxy type from URL
   */
  private detectProxyType(url: string): Proxy['type'] {
    if (url.startsWith('socks5://') || url.startsWith('socks://')) {
      return 'socks5';
    }
    if (url.startsWith('https://')) {
      return 'https';
    }
    return 'http';
  }
}

// Singleton instance
let defaultRotator: ProxyRotator | null = null;

/**
 * Get the default proxy rotator instance
 */
export function getProxyRotator(): ProxyRotator {
  if (!defaultRotator) {
    defaultRotator = new ProxyRotator();
  }
  return defaultRotator;
}

/**
 * Initialize proxy rotator from config
 */
export function initProxyRotator(
  proxyUrls: string[],
  config?: ProxyRotatorConfig
): ProxyRotator {
  defaultRotator = new ProxyRotator(config);
  defaultRotator.addProxies(proxyUrls);
  return defaultRotator;
}
