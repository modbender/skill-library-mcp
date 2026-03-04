import { lookup } from 'node:dns/promises';
import net from 'node:net';

export type AllowlistRule = {
  scheme?: 'https' | 'http';
  wildcard: boolean;
  hostname: string;
  port?: number;
};

export type OutboundResolver = (host: string) => Promise<Array<{ address: string }>>;

const dnsCache = new Map<string, { expiresAt: number; values: Array<{ address: string }> }>();

const defaultResolver: OutboundResolver = async (host: string) => {
  const now = Date.now();
  const cached = dnsCache.get(host);
  if (cached && cached.expiresAt > now) return cached.values;
  const values = await lookup(host, { all: true, verbatim: true });
  const mapped = values.map((v) => ({ address: v.address }));
  dnsCache.set(host, { expiresAt: now + 60_000, values: mapped });
  return mapped;
};

const parseRule = (raw: string): AllowlistRule | undefined => {
  const v = raw.trim().toLowerCase();
  if (!v) return undefined;
  const match = v.match(/^(?:(https?):\/\/)?(\*\.)?([a-z0-9.-]+)(?::(\d{1,5}))?$/);
  if (!match) return undefined;
  const scheme = match[1] as 'https' | 'http' | undefined;
  const wildcard = Boolean(match[2]);
  const hostname = match[3];
  const port = match[4] ? Number(match[4]) : undefined;
  if (net.isIP(hostname) !== 0) return undefined;
  if (port && (port < 1 || port > 65535)) return undefined;
  return { scheme, wildcard, hostname, port };
};

export const parseAllowlist = (raw: string): AllowlistRule[] => raw.split(',').map(parseRule).filter((v): v is AllowlistRule => Boolean(v));

const hostnameMatches = (rule: AllowlistRule, host: string): boolean => {
  if (!rule.wildcard) return host === rule.hostname;
  return host.endsWith(`.${rule.hostname}`) && host !== rule.hostname;
};

export const isIpLiteralHost = (host: string): boolean => net.isIP(host) !== 0;

export const isBlockedIp = (address: string): boolean => {
  const ipType = net.isIP(address);
  if (ipType === 4) {
    const [a, b] = address.split('.').map(Number);
    if (a === 0 || a === 10 || a === 127 || a >= 224) return true;
    if (a === 169 && b === 254) return true;
    if (a === 192 && b === 168) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
    return false;
  }
  if (ipType === 6) {
    const v = address.toLowerCase();
    if (v === '::' || v === '::1') return true;
    if (v.startsWith('fc') || v.startsWith('fd')) return true;
    if (v.startsWith('fe8') || v.startsWith('fe9') || v.startsWith('fea') || v.startsWith('feb')) return true;
    if (v.startsWith('ff')) return true;
    return false;
  }
  return true;
};

export const checkOutboundUrl = async (
  rawUrl: string,
  options: {
    allowlistRaw: string;
    allowHttp: boolean;
    resolver?: OutboundResolver;
  }
): Promise<void> => {
  const url = new URL(rawUrl);
  const host = url.hostname.toLowerCase();
  const scheme = url.protocol.replace(':', '');
  const port = url.port ? Number(url.port) : (scheme === 'https' ? 443 : 80);
  if (url.username || url.password) throw new Error('OUTBOUND_URL_AUTHORITY_NOT_ALLOWED');
  if (isIpLiteralHost(host)) throw new Error('OUTBOUND_IP_LITERAL_FORBIDDEN');
  if (scheme !== 'https' && !(options.allowHttp && scheme === 'http')) throw new Error('OUTBOUND_SCHEME_NOT_ALLOWED');

  const rules = parseAllowlist(options.allowlistRaw);
  if (rules.length === 0) throw new Error('OUTBOUND_NOT_ALLOWED');

  const rule = rules.find((r) => hostnameMatches(r, host) && (!r.port || r.port === port) && (!r.scheme || r.scheme === scheme));
  if (!rule) throw new Error('OUTBOUND_NOT_ALLOWED');

  const resolver = options.resolver ?? defaultResolver;
  const addresses = await resolver(host);
  if (addresses.length === 0) throw new Error('OUTBOUND_DNS_EMPTY');
  for (const addr of addresses) {
    if (isBlockedIp(addr.address)) throw new Error('OUTBOUND_PRIVATE_ADDRESS_BLOCKED');
  }
};
