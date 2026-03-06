// @elvatis/openclaw-rss-feeds - Shared TypeScript types

export interface FeedConfig {
  id: string;
  name: string;
  url: string;
  keywords?: string[];
  enrichCve?: boolean;
  cvssThreshold?: number;
  tags?: string[];
  /** URL template for documentation links. Use {product} and {version} as placeholders.
   *  Example: "https://docs.example.com/{product}/{version}/release-notes" */
  docsUrlTemplate?: string;
  /** Optional regex string to highlight product names in CVE descriptions.
   *  Example: "Forti(?!net)[a-zA-Z0-9]+(?:\\s+Cloud)?" */
  productHighlightPattern?: string;
}

export interface RetryConfig {
  maxRetries?: number; // default 3
  initialDelayMs?: number; // default 1000
  backoffMultiplier?: number; // default 2
}

export interface GhostConfig {
  url: string;
  adminKey: string; // format: "id:secret" (hex secret)
}

export interface PluginConfig {
  feeds: FeedConfig[];
  schedule?: string; // cron expression, e.g. "0 9 1 * *"
  lookbackDays?: number; // default 31
  ghost?: GhostConfig;
  notify?: string[]; // format: "channel:target", e.g. "whatsapp:+49..."
  nvdApiKey?: string;
  retry?: RetryConfig;
}

export interface FeedItem {
  title: string;
  link: string;
  pubDate: Date;
  version?: string;
  product?: string;
  content?: string;
  docsUrl?: string;
  feedId: string;
  feedName: string;
}

// Subset used for firmware/versioned release entries
export interface FirmwareEntry {
  product: string;
  version: string;
  type: 'Major' | 'Feature' | 'Patch';
  pubDate: string; // ISO string
  docsUrl?: string;
  feedId: string;
  feedName: string;
}

export interface CveEntry {
  id: string;
  score: number;
  description: string;
  url: string;
  feedId: string; // which feed triggered this CVE lookup
}

export interface FeedResult {
  feedId: string;
  feedName: string;
  enrichCve?: boolean;
  productHighlightPattern?: string;
  items: FeedItem[];
  firmware: FirmwareEntry[];
  cves: CveEntry[];
  error?: string;
  cveError?: string;
}

export interface DigestResult {
  success: boolean;
  feedsProcessed: number;
  totalItems: number;
  totalCves: number;
  totalFirmware: number;
  ghostUrl?: string;
  ghostError?: string;
  notified: boolean;
  startDate: Date;
  endDate: Date;
  feedResults: FeedResult[];
}

// OpenClaw plugin API (minimal typing for what we use)
export interface PluginApi {
  config: PluginConfig;
  logger: {
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
  };
  registerService(service: PluginService): void;
  registerTool(tool: PluginTool): void;
}

export interface PluginService {
  id: string;
  start(): void | Promise<void>;
  stop(): void | Promise<void>;
}

export interface PluginTool {
  name: string;
  description: string;
  parameters?: Record<string, unknown>;
  execute(args: Record<string, unknown>): Promise<unknown>;
}
