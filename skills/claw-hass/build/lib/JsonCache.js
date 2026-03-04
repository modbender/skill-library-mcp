import { existsSync, readFileSync, writeFileSync } from 'fs';
export function createJsonCache(path) {
    const cache = {
        exists: () => existsSync(path),
        read: (defaultValue) => {
            if (!cache.exists()) {
                return defaultValue;
            }
            return JSON.parse(readFileSync(path, 'utf-8'));
        },
        write: (value) => {
            writeFileSync(path, JSON.stringify(value, null, 2));
        }
    };
    return cache;
}
