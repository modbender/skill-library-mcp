/* ─── Cache Adapter Interface ─── */

export interface CacheAdapter {
    get<T>(key: string): Promise<T | null>;
    set<T>(key: string, value: T, ttlSeconds?: number): Promise<void>;
    delete(key: string): Promise<void>;
    invalidatePattern(pattern: string): Promise<void>;
    close(): Promise<void>;
}
