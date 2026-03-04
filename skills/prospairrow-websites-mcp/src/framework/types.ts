import type { BrowserContext, Page } from "playwright";

export enum Capability {
  READ_ONLY = "READ_ONLY",
  WRITE = "WRITE",
  DESTRUCTIVE = "DESTRUCTIVE"
}

export type JsonRecord = Record<string, unknown>;

export interface SiteConfigFile {
  baseUrl: string;
  allowedHosts: string[];
  capabilities: Capability[];
}

export interface SiteDefinition {
  siteId: string;
  baseUrl: string;
  allowedHosts: string[];
  capabilities: Capability[];
  tasks: TaskDefinition[];
}

export interface TaskDefinition {
  taskId: string;
  capability: Capability;
  description: string;
  run: (context: TaskContext, params?: JsonRecord) => Promise<JsonRecord>;
}

export interface TaskContext {
  site: SiteDefinition;
  task: TaskDefinition;
  context: BrowserContext;
  page: Page;
  safeGoto: (url: string) => Promise<void>;
  runId: string;
  apiKeys?: {
    prospairrow?: string;
  };
}

export interface RegistrySummary {
  policy: {
    enabledCapabilities: Capability[];
  };
  sites: SiteDefinition[];
}

export interface RunTaskInput {
  siteId: string;
  taskId: string;
  params?: JsonRecord;
  apiKey?: string;
}

export interface TaskRunResponse {
  run_id: string;
  timestamp: string;
  site: string;
  task: string;
  result: JsonRecord;
}

export interface BootstrapLoginInput {
  siteId: string;
}
