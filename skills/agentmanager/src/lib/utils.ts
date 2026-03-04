import { createHash, randomUUID } from 'node:crypto';
import { setTimeout as delay } from 'node:timers/promises';

export const nowMs = (): number => Date.now();

export const stableStringify = (value: unknown): string => {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((v) => stableStringify(v)).join(',')}]`;
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(obj[k])}`).join(',')}}`;
};

export const digestOf = (value: unknown): string => createHash('sha256').update(stableStringify(value)).digest('hex');

export const runId = (): string => randomUUID();

export const sleep = (ms: number, signal?: AbortSignal): Promise<void> => delay(ms, undefined, { signal }) as Promise<void>;
