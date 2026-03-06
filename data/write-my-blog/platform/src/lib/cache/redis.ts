/**
 * Redis Cache Adapter
 *
 * Supports both standard Redis (via ioredis) and Upstash Redis.
 * Set REDIS_URL for standard Redis or UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN for Upstash.
 */

import type { CacheAdapter } from "./adapter";

export class RedisCacheAdapter implements CacheAdapter {
    private client: any;
    private isUpstash: boolean;

    constructor() {
        this.isUpstash = !!(
            process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN
        );
    }

    private async getClient() {
        if (this.client) return this.client;

        if (this.isUpstash) {
            const { Redis } = await import("@upstash/redis");
            this.client = new Redis({
                url: process.env.UPSTASH_REDIS_REST_URL!,
                token: process.env.UPSTASH_REDIS_REST_TOKEN!,
            });
        } else {
            const { default: IORedis } = await import("ioredis");
            this.client = new IORedis(process.env.REDIS_URL || "redis://localhost:6379");
        }

        return this.client;
    }

    async get<T>(key: string): Promise<T | null> {
        const client = await this.getClient();
        const value = await client.get(key);
        if (!value) return null;
        try {
            return JSON.parse(value as string) as T;
        } catch {
            return value as T;
        }
    }

    async set<T>(key: string, value: T, ttlSeconds?: number): Promise<void> {
        const client = await this.getClient();
        const serialized = JSON.stringify(value);
        if (ttlSeconds) {
            if (this.isUpstash) {
                await client.set(key, serialized, { ex: ttlSeconds });
            } else {
                await client.set(key, serialized, "EX", ttlSeconds);
            }
        } else {
            await client.set(key, serialized);
        }
    }

    async delete(key: string): Promise<void> {
        const client = await this.getClient();
        await client.del(key);
    }

    async invalidatePattern(pattern: string): Promise<void> {
        const client = await this.getClient();
        if (this.isUpstash) {
            // Upstash doesn't support SCAN in the same way, use KEYS cautiously
            const keys = await client.keys(pattern);
            if (keys.length > 0) {
                await client.del(...keys);
            }
        } else {
            const stream = client.scanStream({ match: pattern });
            const pipeline = client.pipeline();
            stream.on("data", (keys: string[]) => {
                for (const key of keys) {
                    pipeline.del(key);
                }
            });
            await new Promise<void>((resolve) => {
                stream.on("end", async () => {
                    await pipeline.exec();
                    resolve();
                });
            });
        }
    }

    async close(): Promise<void> {
        if (this.client && !this.isUpstash) {
            await this.client.quit();
        }
    }
}
