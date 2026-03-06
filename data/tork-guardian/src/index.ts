/**
 * Tork Guardian — AI Governance SDK for OpenClaw Skills
 *
 * Provides PII redaction, tool call governance, network access control,
 * compliance receipts, and skill security scanning.
 */

import { TorkClient } from './client';
import { TorkConfig, TorkConfigSchema, GovernResponse, ToolCallDecision } from './config';
import { governLLMRequest, GovernedLLMRequest, LLMRequest } from './interceptors/llm';
import { governToolCall, ToolCall } from './interceptors/tool';
import { NetworkAccessHandler } from './handlers/network-access';

export class TorkGuardian {
  private client: TorkClient;
  private config: TorkConfig;
  private networkHandler: NetworkAccessHandler;

  constructor(config: Partial<TorkConfig> & { apiKey: string }) {
    this.config = TorkConfigSchema.parse(config);
    this.client = new TorkClient(this.config.apiKey, this.config.baseUrl);
    this.networkHandler = new NetworkAccessHandler(this.config, this.client);
  }

  async governLLM(request: LLMRequest): Promise<GovernedLLMRequest> {
    return governLLMRequest(this.client, request, this.config);
  }

  governTool(tool: ToolCall): ToolCallDecision {
    return governToolCall(tool, this.config);
  }

  async redactPII(content: string): Promise<GovernResponse> {
    return this.client.redact(content);
  }

  async generateReceipt(content: string): Promise<GovernResponse> {
    return this.client.govern(content);
  }

  getConfig(): Readonly<TorkConfig> {
    return { ...this.config };
  }

  getNetworkHandler(): NetworkAccessHandler {
    return this.networkHandler;
  }
}

// Standalone function exports
export async function redactPII(apiKey: string, content: string): Promise<GovernResponse> {
  const client = new TorkClient(apiKey);
  return client.redact(content);
}

export async function generateReceipt(apiKey: string, content: string): Promise<GovernResponse> {
  const client = new TorkClient(apiKey);
  return client.govern(content);
}

// Re-exports
export { governLLMRequest } from './interceptors/llm';
export { governToolCall } from './interceptors/tool';
export { NetworkAccessHandler, validatePortBind, validateEgress, validateDNS } from './handlers/network-access';

export type {
  TorkConfig,
  GovernOptions,
  GovernResponse,
  ToolCallDecision,
  NetworkPolicyConfig,
  NetworkDecision,
  NetworkActivityLog,
} from './config';
export type { LLMRequest, GovernedLLMRequest } from './interceptors/llm';
export type { ToolCall } from './interceptors/tool';

export { GovernanceDeniedError } from './interceptors/llm';
export { TorkClient } from './client';
export { DEFAULT_NETWORK_POLICY } from './policies/network-default';
export { STRICT_NETWORK_POLICY } from './policies/network-strict';
export { NetworkMonitor } from './utils/network-monitor';
export { MINIMAL_CONFIG, DEVELOPMENT_CONFIG, PRODUCTION_CONFIG, ENTERPRISE_CONFIG } from './examples';

// Scanner re-exports (source in dist/scanner/)
export { SkillScanner } from './scanner';
export { SCAN_RULES } from './scanner/rules';
export type { ScanFinding, ScanReport, ScanRule, Severity, Verdict } from './scanner/types';
export { generateBadge, generateBadgeMarkdown, generateBadgeJSON } from './scanner/badge';
export type { TorkBadge, BadgeTier } from './scanner/badge';
export { scanFromURL, scanFromSource, formatReportForAPI } from './scanner/api';
export type { APIReport, APIFinding } from './scanner/api';
export { ReportStore } from './scanner/report-store';
