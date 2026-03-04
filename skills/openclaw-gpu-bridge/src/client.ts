// GPU Bridge - HTTP Client with multi-host load balancing/failover

import type {
  GpuBridgeConfig,
  GpuHostConfig,
  HealthResponse,
  InfoResponse,
  BertScoreRequest,
  BertScoreResponse,
  EmbedRequest,
  EmbedResponse,
  LoadBalancingStrategy,
  StatusResponse,
} from "./types.js";

const DEFAULT_MAX_BATCH_SIZE = 100;
const DEFAULT_MAX_TEXT_LENGTH = 10000;
const MAX_503_RETRIES = 3;

export class InputValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InputValidationError";
  }
}

interface RuntimeHost {
  id: string;
  url: string;
  name: string;
  apiKey?: string;
  healthy: boolean;
  consecutive503s: number;
  lastError?: string;
  lastInfo?: InfoResponse;
  lastCheckedAt?: number;
}

export class GpuBridgeClient {
  private hosts: RuntimeHost[];
  private timeout: number;
  private roundRobinIndex = 0;
  private strategy: LoadBalancingStrategy;
  private healthCheckIntervalMs: number;
  private maxBatchSize: number;
  private maxTextLength: number;

  constructor(config: GpuBridgeConfig) {
    this.hosts = this.normalizeHosts(config);
    this.timeout = (config.timeout ?? 45) * 1000;
    this.strategy = config.loadBalancing ?? "round-robin";
    this.healthCheckIntervalMs = (config.healthCheckIntervalSeconds ?? 30) * 1000;
    this.maxBatchSize = config.limits?.maxBatchSize ?? DEFAULT_MAX_BATCH_SIZE;
    this.maxTextLength = config.limits?.maxTextLength ?? DEFAULT_MAX_TEXT_LENGTH;

    const timer = setInterval(() => {
      void this.runHealthChecks();
    }, this.healthCheckIntervalMs);
    timer.unref?.();

    void this.runHealthChecks();
  }

  private normalizeHosts(config: GpuBridgeConfig): RuntimeHost[] {
    const hostsFromV2: GpuHostConfig[] = config.hosts ?? [];
    const v1Url = config.serviceUrl ?? config.url;

    const normalized: GpuHostConfig[] = hostsFromV2.length
      ? hostsFromV2
      : (v1Url ? [{ url: v1Url, apiKey: config.apiKey, name: "gpu-1" }] : []);

    if (!normalized.length) {
      throw new Error("GPU Bridge config invalid: set hosts[] (v0.2) or serviceUrl/url (v0.1)");
    }

    return normalized.map((host, i) => ({
      id: `host-${i + 1}`,
      url: host.url.replace(/\/+$/, ""),
      name: host.name ?? `gpu-${i + 1}`,
      apiKey: host.apiKey ?? config.apiKey,
      healthy: true,
      consecutive503s: 0,
    }));
  }

  private async requestFromHost<T>(host: RuntimeHost, path: string, options?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(host.apiKey ? { "X-API-Key": host.apiKey } : {}),
    };

    const timeoutMs = path === "/health" ? 5000 : this.timeout;

    for (let attempt = 0; attempt <= MAX_503_RETRIES; attempt += 1) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);

      try {
        const res = await fetch(`${host.url}${path}`, {
          ...options,
          headers: { ...headers, ...(options?.headers as Record<string, string> | undefined) },
          signal: controller.signal,
        });

        if (res.status === 503) {
          host.consecutive503s += 1;
          const retryAfter = res.headers.get("Retry-After");

          if (retryAfter && attempt < MAX_503_RETRIES) {
            const delaySec = parseInt(retryAfter, 10);
            const delayMs = (Number.isNaN(delaySec) ? 5 : delaySec) * 1000;
            await new Promise((resolve) => setTimeout(resolve, delayMs));
            continue;
          }

          // Exhausted retries or no Retry-After header - mark unhealthy
          host.healthy = false;
          host.lastError = `GPU host ${host.name} returned 503 after ${host.consecutive503s} consecutive attempt(s)`;
          throw new Error(host.lastError);
        }

        if (!res.ok) {
          const body = await res.text().catch(() => "");
          throw new Error(`GPU host ${host.name} ${path} returned ${res.status}: ${body}`);
        }

        host.healthy = true;
        host.lastError = undefined;
        host.consecutive503s = 0;
        return (await res.json()) as T;
      } catch (error) {
        // Only mark unhealthy for non-503 errors (503 handling is above)
        if (!(error instanceof Error && error.message.includes("returned 503"))) {
          host.healthy = false;
          host.lastError = error instanceof Error ? error.message : String(error);
        }
        if (attempt === MAX_503_RETRIES || !(error instanceof Error && error.message.includes("returned 503"))) {
          throw error;
        }
      } finally {
        clearTimeout(timer);
      }
    }

    // Should not reach here, but satisfies TypeScript
    throw new Error(`GPU host ${host.name} ${path} failed after ${MAX_503_RETRIES} retries`);
  }

  private getHealthyHosts(): RuntimeHost[] {
    const healthy = this.hosts.filter((h) => h.healthy);
    return healthy.length ? healthy : this.hosts;
  }

  private async selectHost(path: string): Promise<RuntimeHost> {
    const pool = this.getHealthyHosts();

    if (this.strategy === "least-busy" && path !== "/health") {
      await Promise.all(pool.map(async (host) => {
        try {
          const info = await this.requestFromHost<InfoResponse>(host, "/info");
          host.lastInfo = info;
          host.lastCheckedAt = Date.now();
        } catch {
          // host health is already updated in requestFromHost
        }
      }));

      const candidates = this.getHealthyHosts();
      const byLeastBusy = [...candidates].sort((a, b) => this.vramLoad(a) - this.vramLoad(b));
      return byLeastBusy[0];
    }

    const host = pool[this.roundRobinIndex % pool.length];
    this.roundRobinIndex += 1;
    return host;
  }

  private vramLoad(host: RuntimeHost): number {
    const total = host.lastInfo?.vram_total_mb;
    const used = host.lastInfo?.vram_used_mb;
    if (!total || total <= 0 || used === undefined) {
      return Number.POSITIVE_INFINITY;
    }
    return used / total;
  }

  private async requestWithFailover<T>(path: string, options?: RequestInit): Promise<T> {
    const attempts = this.hosts.length;
    const tried = new Set<string>();
    let lastError: unknown;

    for (let i = 0; i < attempts; i += 1) {
      const host = await this.selectHost(path);
      if (tried.has(host.id)) {
        continue;
      }
      tried.add(host.id);

      try {
        return await this.requestFromHost<T>(host, path, options);
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(`All GPU hosts failed for ${path}: ${lastError instanceof Error ? lastError.message : String(lastError)}`);
  }

  private async runHealthChecks(): Promise<void> {
    await Promise.all(this.hosts.map(async (host) => {
      try {
        await this.requestFromHost<HealthResponse>(host, "/health");
      } catch {
        // already tracked as unhealthy
      }
    }));
  }

  private validateTexts(texts: string[], fieldName: string): void {
    if (texts.length > this.maxBatchSize) {
      throw new InputValidationError(
        `${fieldName} array length ${texts.length} exceeds max batch size of ${this.maxBatchSize}`
      );
    }
    for (let i = 0; i < texts.length; i += 1) {
      if (texts[i].length > this.maxTextLength) {
        throw new InputValidationError(
          `${fieldName}[${i}] length ${texts[i].length} exceeds max text length of ${this.maxTextLength}`
        );
      }
    }
  }

  async health(): Promise<HealthResponse> {
    return this.requestWithFailover<HealthResponse>("/health");
  }

  async info(): Promise<InfoResponse> {
    return this.requestWithFailover<InfoResponse>("/info");
  }

  async bertscore(req: BertScoreRequest): Promise<BertScoreResponse> {
    this.validateTexts(req.candidates, "candidates");
    this.validateTexts(req.references, "references");
    return this.requestWithFailover<BertScoreResponse>("/bertscore", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async embed(req: EmbedRequest): Promise<EmbedResponse> {
    this.validateTexts(req.texts, "texts");
    return this.requestWithFailover<EmbedResponse>("/embed", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async status(): Promise<StatusResponse> {
    return this.requestWithFailover<StatusResponse>("/status");
  }
}
