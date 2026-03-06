/**
 * Cache Provider Index
 *
 * Auto-selects based on CACHE_PROVIDER env var. Defaults to memory.
 */

import type { CacheAdapter } from "./adapter";

let _cache: CacheAdapter | null = null;

export async function getCache(): Promise<CacheAdapter> {
    if (_cache) return _cache;

    const provider = process.env.CACHE_PROVIDER || "memory";

    switch (provider) {
        case "memory": {
            const { MemoryCacheAdapter } = await import("./memory");
            _cache = new MemoryCacheAdapter(
                parseInt(process.env.CACHE_MAX_SIZE || "500", 10),
            );
            break;
        }
        case "redis": {
            const { RedisCacheAdapter } = await import("./redis");
            _cache = new RedisCacheAdapter();
            break;
        }
        default:
            throw new Error(
                `Unsupported CACHE_PROVIDER: "${provider}". Supported: memory, redis`,
            );
    }

    return _cache;
}

export type { CacheAdapter } from "./adapter";
