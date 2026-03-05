/**
 * In-Memory LRU Cache Adapter
 *
 * Uses an LRU cache with configurable max size and TTL.
 * Suitable for development and single-instance deployments.
 */

import { LRUCache } from "lru-cache";
import type { CacheAdapter } from "./adapter";

export class MemoryCacheAdapter implements CacheAdapter {
    private cache: LRUCache<string, { value: unknown; expiresAt?: number }>;

    constructor(maxSize = 500) {
        this.cache = new LRUCache({ max: maxSize });
    }

    async get<T>(key: string): Promise<T | null> {
        const entry = this.cache.get(key);
        if (!entry) return null;
        if (entry.expiresAt && Date.now() > entry.expiresAt) {
            this.cache.delete(key);
            return null;
        }
        return entry.value as T;
    }

    async set<T>(key: string, value: T, ttlSeconds?: number): Promise<void> {
        this.cache.set(key, {
            value,
            expiresAt: ttlSeconds ? Date.now() + ttlSeconds * 1000 : undefined,
        });
    }

    async delete(key: string): Promise<void> {
        this.cache.delete(key);
    }

    async invalidatePattern(pattern: string): Promise<void> {
        const regex = new RegExp(pattern.replace(/\*/g, ".*"));
        for (const key of this.cache.keys()) {
            if (regex.test(key)) {
                this.cache.delete(key);
            }
        }
    }

    async close(): Promise<void> {
        this.cache.clear();
    }
}
