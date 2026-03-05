import { lookup } from 'node:dns/promises';
import net from 'node:net';
import { getConfig } from '../config.js';

export type SafeFetchOptions = {
  resolver?: (host: string) => Promise<Array<{ address: string }>>;
  method?: string;
  headers?: Record<string, string>;
  body?: string;
  timeoutMs?: number;
  maxBytes?: number;
  signal?: AbortSignal;
};

const isBlockedIp = (address: string): boolean => {
  const t = net.isIP(address);
  if (t === 4) {
    const [a, b] = address.split('.').map(Number);
    if (a === 10 || a === 127 || a === 0 || a >= 224) return true;
    if (a === 169 && b === 254) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
    if (a === 192 && b === 168) return true;
    return false;
  }
  if (t === 6) {
    const v = address.toLowerCase();
    if (v === '::1' || v === '::') return true;
    if (v.startsWith('fc') || v.startsWith('fd')) return true;
    if (v.startsWith('fe8') || v.startsWith('fe9') || v.startsWith('fea') || v.startsWith('feb')) return true;
    if (v.startsWith('ff')) return true;
    return false;
  }
  return true;
};

const hostAllowed = (host: string, allowlist: string[]): boolean => allowlist.some((rule) => {
  if (rule.startsWith('.')) return host.endsWith(rule) && host !== rule.slice(1);
  return host === rule;
});

const enforceDestination = async (url: URL, resolverOverride?: (host: string) => Promise<Array<{ address: string }>>): Promise<void> => {
  const cfg = getConfig();
  const host = url.hostname.toLowerCase();
  const ipLiteral = net.isIP(host) !== 0;
  if (ipLiteral) throw new Error('OUTBOUND_IP_LITERAL_FORBIDDEN');

  if (url.protocol !== 'https:') {
    const localhost = host === 'localhost';
    if (!(cfg.ALLOW_INSECURE_HTTP && localhost && url.protocol === 'http:')) {
      throw new Error('OUTBOUND_SCHEME_NOT_ALLOWED');
    }
  }

  if (!cfg.OUTBOUND_ALLOW_ALL) {
    const rules = (cfg.OUTBOUND_HOST_ALLOWLIST || cfg.OUTBOUND_ALLOWLIST).split(',').map((v) => v.trim().toLowerCase()).filter(Boolean);
    if (rules.length === 0) throw new Error('OUTBOUND_DISABLED');
    if (!hostAllowed(host, rules)) throw new Error('OUTBOUND_HOST_NOT_ALLOWED');
  }

  const addrs = resolverOverride ? await resolverOverride(host) : await lookup(host, { all: true, verbatim: true });
  if (addrs.length === 0) throw new Error('OUTBOUND_DNS_EMPTY');
  for (const addr of addrs) {
    if (isBlockedIp(addr.address)) throw new Error('OUTBOUND_PRIVATE_ADDRESS_BLOCKED');
  }
};

const readBodyLimited = async (res: Response, maxBytes: number): Promise<Uint8Array> => {
  const reader = res.body?.getReader();
  if (!reader) return new Uint8Array();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const next = await reader.read();
    if (next.done) break;
    total += next.value.byteLength;
    if (total > maxBytes) throw new Error('OUTBOUND_RESPONSE_TOO_LARGE');
    chunks.push(next.value);
  }
  const merged = new Uint8Array(total);
  let offset = 0;
  for (const c of chunks) {
    merged.set(c, offset);
    offset += c.byteLength;
  }
  return merged;
};

export const safeFetch = async (rawUrl: string, opts: SafeFetchOptions): Promise<{ status: number; headers: Headers; bodyText: string }> => {
  const started = Date.now();
  const url = new URL(rawUrl);
  await enforceDestination(url, opts.resolver);

  const timeoutSignal = AbortSignal.timeout(Math.max(1, opts.timeoutMs ?? 30_000));
  const signal = opts.signal ? AbortSignal.any([opts.signal, timeoutSignal]) : timeoutSignal;

  const res = await fetch(url, {
    method: opts.method ?? 'GET',
    headers: opts.headers,
    body: opts.body,
    redirect: 'error',
    signal
  });

  const bytes = await readBodyLimited(res, Math.max(1, opts.maxBytes ?? 1_000_000));
  const bodyText = new TextDecoder().decode(bytes);
  const elapsed = Date.now() - started;
  // eslint-disable-next-line no-console
  console.info(`[safeFetch] host=${url.hostname} path=${url.pathname} status=${res.status} duration_ms=${elapsed}`);
  return { status: res.status, headers: res.headers, bodyText };
};
