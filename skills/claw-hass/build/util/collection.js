import {} from 'home-assistant-js-websocket';
import {} from '../lib/JsonCache.js';
import { resolvable } from './promise.js';
export function wrapCollection(collection$, callback, cache) {
    let currentValue = undefined;
    const { promise, resolve } = resolvable();
    const $unsubscribe = collection$.then((collection) => {
        return collection.subscribe((state) => {
            if (!currentValue) {
                resolve(state);
            }
            callback(state);
            currentValue = state;
            if (cache) {
                cache.write(state);
            }
        });
    });
    if (cache) {
        const cachedResult = cache.read();
        if (cachedResult) {
            resolve(cachedResult);
            currentValue = cachedResult;
            callback(cachedResult);
        }
    }
    return {
        get value() {
            if (!currentValue) {
                throw new Error('Value access before loaded');
            }
            return currentValue;
        },
        unsubscribe: () => { $unsubscribe.then((unsubscribe) => unsubscribe()); },
        promise
    };
}
