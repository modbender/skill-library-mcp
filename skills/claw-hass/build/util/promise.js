export function resolvable() {
    const result = { promise: null, resolve: null, reject: null };
    result.promise = new Promise((resolve, reject) => { result.resolve = resolve; result.reject = reject; });
    return result;
}
export function timeout(delay) {
    return new Promise((resolve) => setTimeout(resolve, delay));
}
