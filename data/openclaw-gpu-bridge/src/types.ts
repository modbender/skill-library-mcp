// GPU Bridge - Shared TypeScript types

export type LoadBalancingStrategy = "round-robin" | "least-busy";

export interface GpuHostConfig {
  url: string;
  name?: string;
  apiKey?: string;
}

export interface InputLimits {
  /** Max number of items per batch (candidates, references, texts). Default: 100 */
  maxBatchSize?: number;
  /** Max character length per individual text. Default: 10000 */
  maxTextLength?: number;
}

export interface GpuBridgeConfig {
  /** v0.2 preferred config */
  hosts?: GpuHostConfig[];

  /** v0.1 compatibility */
  serviceUrl?: string;
  url?: string;
  apiKey?: string;

  timeout?: number;
  healthCheckIntervalSeconds?: number;
  loadBalancing?: LoadBalancingStrategy;
  models?: {
    embed?: string;
    bertscore?: string;
  };

  /** Configurable limits to prevent GPU OOM on large batches */
  limits?: InputLimits;
}

// --- Responses ---

export interface HealthResponse {
  status: "ok" | "error";
  device: string;
}

export interface InfoResponse {
  device: string;
  device_name: string;
  vram_total_mb?: number;
  vram_used_mb?: number;
  pytorch_version: string;
  cuda_version: string | null;
  loaded_models: string[];
}

export interface BertScoreRequest {
  candidates: string[];
  references: string[];
  lang?: string;
  model_type?: string;
}

export interface BertScoreResponse {
  precision: number[];
  recall: number[];
  f1: number[];
  model: string;
}

export interface EmbedRequest {
  texts: string[];
  model?: string;
}

export interface EmbedResponse {
  embeddings: number[][];
  model: string;
  dimensions: number;
}

export interface StatusResponse {
  queue: {
    max_concurrent: number;
    in_flight: number;
    available_slots: number;
    waiting_estimate: number;
  };
  active_jobs: Array<{
    id: string;
    type: "embed" | "bertscore";
    started_at: string;
    items: number;
    model: string;
    progress: number;
  }>;
}
