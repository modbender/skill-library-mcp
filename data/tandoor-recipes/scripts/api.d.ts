import { z } from 'zod';
export interface ApiRequestOptions {
    method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
    body?: unknown;
    headers?: Record<string, string>;
}
export declare class TandoorApiError extends Error {
    statusCode: number;
    statusText: string;
    responseBody: string;
    constructor(statusCode: number, statusText: string, responseBody: string);
}
/**
 * Make a validated API request to Tandoor
 */
export declare function apiRequest<T>(endpoint: string, schema: z.ZodType<T>, options?: ApiRequestOptions): Promise<T>;
/**
 * Make an unvalidated API request (for mutations that don't need response validation)
 */
export declare function apiRequestRaw(endpoint: string, options?: ApiRequestOptions): Promise<unknown>;
//# sourceMappingURL=api.d.ts.map