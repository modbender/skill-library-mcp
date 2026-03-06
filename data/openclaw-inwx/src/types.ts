export type JsonMap = Record<string, unknown>;

export interface Domain {
  domain: string;
  roid?: string;
  status?: string;
  created?: string;
  updated?: string;
  expires?: string;
  authCode?: string;
  [key: string]: unknown;
}

export interface DomainCheckResult {
  domain: string;
  avail: boolean;
  price?: number;
  currency?: string;
  period?: number;
  premium?: boolean;
  reason?: string;
  [key: string]: unknown;
}

export interface DnsRecord {
  id?: number;
  name?: string;
  type?: string;
  content?: string;
  ttl?: number;
  prio?: number;
  [key: string]: unknown;
}

export interface Contact {
  id?: number;
  type?: string;
  fname?: string;
  lname?: string;
  org?: string;
  email?: string;
  countryCode?: string;
  [key: string]: unknown;
}

export interface DnssecKey {
  id?: number;
  domain?: string;
  alg?: number;
  flags?: number;
  protocol?: number;
  publicKey?: string;
  [key: string]: unknown;
}

export interface AccountInfo {
  balance?: number;
  currency?: string;
  [key: string]: unknown;
}

export interface TldPricing {
  tld: string;
  registrationPrice?: number;
  renewalPrice?: number;
  transferPrice?: number;
  currency?: string;
  [key: string]: unknown;
}

export interface PluginConfig {
  username: string;
  password: string;
  otpSecret?: string;
  environment?: "production" | "ote";
  readOnly?: boolean;
  allowedOperations?: string[];
}

export interface ToolContext {
  config: PluginConfig;
}

export interface ToolHandler {
  name: string;
  description: string;
  run: (params: JsonMap, context: ToolContext) => Promise<unknown>;
}

export interface OpenClawRuntimeLike {
  registerTool: (name: string, definition: { description: string; run: (params: JsonMap) => Promise<unknown> }) => void;
}
