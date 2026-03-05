import { ApiClient } from "domrobot-client";
import { PluginConfig } from "./types";

type ApiResponse<T> = {
  code?: number;
  msg?: string;
  resData?: T;
  [key: string]: unknown;
};

interface ApiClientLike {
  login: (username: string, password: string, sharedSecret?: string) => Promise<unknown>;
  logout: () => Promise<unknown>;
  callApi: (method: string, params?: unknown) => Promise<ApiResponse<unknown>>;
}

const OK_CODE = 1000;

export const INWX_ERROR_MESSAGES: Record<number, string> = {
  1000: "Success",
  2200: "Authentication failed",
  2201: "Authorization failed",
  2302: "Domain not available",
  2400: "Insufficient balance",
  2500: "Object not found",
};

function apiUrlFor(environment: "production" | "ote"): string {
  return environment === "ote" ? ApiClient.API_URL_OTE : ApiClient.API_URL_LIVE;
}

export class InwxApiError extends Error {
  public readonly code: number;

  public constructor(code: number, message: string) {
    super(`INWX API ${code}: ${message}`);
    this.name = "InwxApiError";
    this.code = code;
  }
}

export class InwxClient {
  private readonly client: ApiClientLike;
  private readonly otpSecret?: string;
  private loggedIn = false;

  public constructor(config: PluginConfig, factory?: (apiUrl: string) => ApiClientLike) {
    const env = config.environment ?? "production";
    const apiUrl = apiUrlFor(env);
    this.otpSecret = config.otpSecret;
    this.client = factory ? factory(apiUrl) : new ApiClient(apiUrl);
    this.username = config.username;
    this.password = config.password;
  }

  private readonly username: string;
  private readonly password: string;

  public async login(): Promise<void> {
    if (this.loggedIn) {
      return;
    }

    const result = await this.client.login(this.username, this.password, this.otpSecret);
    if (!result) {
      throw new Error("INWX login failed");
    }
    this.loggedIn = true;
  }

  public async logout(): Promise<void> {
    if (!this.loggedIn) {
      return;
    }
    await this.client.logout();
    this.loggedIn = false;
  }

  public async call<T>(method: string, params: Record<string, unknown> = {}): Promise<T> {
    await this.login();
    const response = await this.client.callApi(method, params);
    return this.unwrapResponse<T>(response);
  }

  private unwrapResponse<T>(response: ApiResponse<unknown>): T {
    const code = typeof response.code === "number" ? response.code : -1;
    if (code !== OK_CODE) {
      const fallback = INWX_ERROR_MESSAGES[code] ?? "Unknown API error";
      const message = typeof response.msg === "string" && response.msg.length > 0 ? response.msg : fallback;
      throw new InwxApiError(code, message);
    }

    if (response.resData === undefined) {
      return {} as T;
    }

    return response.resData as T;
  }
}
