import { TickTickApiClient } from "../api/ticktick-api-client.js";
import { createTickTickGateway, type TickTickGateway } from "../api/ticktick-gateway.js";
import { TickTickOAuth2Client } from "../auth/ticktick-oauth2-client.js";
import { parseTickTickEnv, parseTickTickEnvFromRuntime, type TickTickEnvSchema, type TickTickEnvSource } from "../config/ticktick-env.js";
import { createTickTickUseCases } from "./ticktick-usecases.js";
import type { TickTickUseCases } from "./usecase-contracts.js";

export interface TickTickRuntimeConfig {
  env: TickTickEnvSchema;
  getAccessToken: () => string | Promise<string>;
}

export interface TickTickRuntimeFromEnvConfig {
  getAccessToken: () => string | Promise<string>;
  envSource?: TickTickEnvSource;
}

export interface TickTickRuntime {
  oauth2Client: TickTickOAuth2Client;
  apiClient: TickTickApiClient;
  gateway: TickTickGateway;
  useCases: TickTickUseCases;
}

export function createTickTickRuntime(config: TickTickRuntimeConfig): TickTickRuntime {
  const oauthConfig: {
    tokenUrl: string;
    clientId: string;
    clientSecret: string;
    timeoutMs: number;
    userAgent?: string;
  } = {
    tokenUrl: config.env.oauthTokenUrl,
    clientId: config.env.clientId,
    clientSecret: config.env.clientSecret,
    timeoutMs: config.env.apiTimeoutMs,
  };
  if (config.env.userAgent !== undefined) {
    oauthConfig.userAgent = config.env.userAgent;
  }

  const oauth2Client = new TickTickOAuth2Client(oauthConfig);

  const defaultHeaders: Record<string, string> = {};
  if (config.env.userAgent !== undefined) {
    defaultHeaders["user-agent"] = config.env.userAgent;
  }

  const apiClient = new TickTickApiClient({
    baseUrl: config.env.apiBaseUrl,
    getAccessToken: config.getAccessToken,
    timeoutMs: config.env.apiTimeoutMs,
    maxRetries: config.env.apiMaxRetries,
    retryBaseDelayMs: config.env.apiRetryBaseDelayMs,
    defaultHeaders,
  });

  const gateway = createTickTickGateway(apiClient);
  const useCases = createTickTickUseCases(gateway);

  return {
    oauth2Client,
    apiClient,
    gateway,
    useCases,
  };
}

export function createTickTickRuntimeFromEnv(config: TickTickRuntimeFromEnvConfig): TickTickRuntime {
  const env = config.envSource === undefined ? parseTickTickEnvFromRuntime() : parseTickTickEnv(config.envSource);

  return createTickTickRuntime({
    env,
    getAccessToken: config.getAccessToken,
  });
}
