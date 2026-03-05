import { HAClientError, HAClientLike, HAEntityState, HAServiceDomain, HomeAssistantConfig, JsonMap, PluginConfig } from "./types";

const DEFAULT_TIMEOUT_MS = 30_000;

export class HAClient implements HAClientLike {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;

  public constructor(private readonly config: PluginConfig) {
    this.baseUrl = config.url.replace(/\/$/, "");
    this.timeoutMs = DEFAULT_TIMEOUT_MS;
  }

  public async checkConnection(): Promise<boolean> {
    await this.request<unknown>("GET", "/api/");
    return true;
  }

  public async getConfig(): Promise<HomeAssistantConfig> {
    return this.request<HomeAssistantConfig>("GET", "/api/config");
  }

  public async getStates(): Promise<HAEntityState[]> {
    return this.request<HAEntityState[]>("GET", "/api/states");
  }

  public async getState(entityId: string): Promise<HAEntityState> {
    return this.request<HAEntityState>("GET", `/api/states/${encodeURIComponent(entityId)}`);
  }

  public async getServices(): Promise<HAServiceDomain[]> {
    return this.request<HAServiceDomain[]>("GET", "/api/services");
  }

  public async callService(domain: string, service: string, serviceData: JsonMap = {}): Promise<unknown> {
    return this.request<unknown>("POST", `/api/services/${encodeURIComponent(domain)}/${encodeURIComponent(service)}`, serviceData);
  }

  public async getHistory(startTimestamp: string, entityId?: string, endTimestamp?: string): Promise<unknown> {
    const params = new URLSearchParams();
    if (entityId) {
      params.set("filter_entity_id", entityId);
    }
    if (endTimestamp) {
      params.set("end_time", endTimestamp);
    }

    const suffix = params.toString() ? `?${params.toString()}` : "";
    return this.request<unknown>("GET", `/api/history/period/${encodeURIComponent(startTimestamp)}${suffix}`);
  }

  public async getLogbook(startTimestamp: string, entityId?: string, endTimestamp?: string): Promise<unknown> {
    const params = new URLSearchParams();
    if (entityId) {
      params.set("entity", entityId);
    }
    if (endTimestamp) {
      params.set("end_time", endTimestamp);
    }

    const suffix = params.toString() ? `?${params.toString()}` : "";
    return this.request<unknown>("GET", `/api/logbook/${encodeURIComponent(startTimestamp)}${suffix}`);
  }

  public async renderTemplate(template: string, variables: JsonMap = {}): Promise<unknown> {
    return this.request<unknown>("POST", "/api/template", { template, ...variables });
  }

  public async fireEvent(eventType: string, eventData: JsonMap = {}): Promise<unknown> {
    return this.request<unknown>("POST", `/api/events/${encodeURIComponent(eventType)}`, eventData);
  }

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: {
          Authorization: `Bearer ${this.config.token}`,
          "Content-Type": "application/json"
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal
      });
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") {
        throw new Error(`Home Assistant request timed out after ${this.timeoutMs}ms: ${method} ${path}`);
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }

    const raw = await response.text();
    if (!response.ok) {
      throw new HAClientError(response.status, raw);
    }

    if (raw.length === 0) {
      return {} as T;
    }

    try {
      return JSON.parse(raw) as T;
    } catch {
      return raw as T;
    }
  }
}
