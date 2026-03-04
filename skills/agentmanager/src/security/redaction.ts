import { createHash } from 'node:crypto';
import { getConfig } from '../config.js';

const sensitiveKey = (key: string): boolean => {
  const v = key.toLowerCase();
  return v.includes('content') || v.includes('message') || v.includes('arguments') || v.includes('output') || v.includes('payload') || v.includes('artifact') || v.includes('api_key') || v.includes('authorization') || v.includes('token');
};

const redactString = (value: string): unknown => {
  const env = getConfig();
  if ((!env.REDACT_TELEMETRY && !env.REDACT_EVENTS) || env.REDACT_TELEMETRY_MODE === 'none') {
    if (env.REDACT_EVENTS && value.length > 500) return { redacted: true, mode: 'truncate', preview: value.slice(0, 200), length: value.length };
    return value;
  }
  if (env.REDACT_TELEMETRY_MODE === 'hash') {
    return { redacted: true, mode: 'hash', sha256: createHash('sha256').update(value).digest('hex'), length: value.length };
  }
  const n = env.REDACT_TELEMETRY_TRUNCATE_CHARS;
  return { redacted: true, mode: 'truncate', preview: value.slice(0, n), length: value.length };
};

export const redactTelemetryValue = (value: unknown, force = false): unknown => {
  const env = getConfig();
  if (!force && !env.REDACT_TELEMETRY && !env.REDACT_EVENTS) return value;
  if (typeof value === 'string') return redactString(value);
  if (Array.isArray(value)) return value.map((v) => redactTelemetryValue(v, force));
  if (value && typeof value === 'object') {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = sensitiveKey(k) ? redactTelemetryValue(v, true) : redactTelemetryValue(v, force);
    }
    return out;
  }
  return value;
};

export const redactEventForOutput = (event: { [k: string]: unknown }): { [k: string]: unknown } => ({
  ...event,
  data: redactTelemetryValue(event.data)
});
