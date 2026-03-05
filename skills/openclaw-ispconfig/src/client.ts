import http from "node:http";
import https from "node:https";
import { URL } from "node:url";
import { ISPConfigError, classifyApiMessage } from "./errors";
import { ISPConfigApiEnvelope, ISPConfigPluginConfig, JsonMap } from "./types";

export class ISPConfigClient {
  private readonly url: URL;
  private readonly timeoutMs: number;
  private readonly verifySsl: boolean;
  private sessionId: string | null = null;
  private isLoggingIn = false;

  public constructor(private readonly config: ISPConfigPluginConfig) {
    this.url = new URL(config.apiUrl);
    this.timeoutMs = config.timeoutMs ?? 20_000;
    this.verifySsl = config.verifySsl ?? true;
  }

  public async login(): Promise<string> {
    if (this.sessionId) {
      return this.sessionId;
    }
    if (this.isLoggingIn) {
      await new Promise((resolve) => setTimeout(resolve, 150));
      return this.login();
    }

    this.isLoggingIn = true;
    try {
      const res = await this.rawCall<string>("login", {
        username: this.config.username,
        password: this.config.password,
      }, true);

      if (!res || typeof res !== "string") {
        throw new ISPConfigError("auth_error", "ISPConfig login failed: no session_id returned");
      }

      this.sessionId = res;
      return this.sessionId;
    } finally {
      this.isLoggingIn = false;
    }
  }

  public async logout(): Promise<unknown> {
    if (!this.sessionId) {
      return { ok: true, message: "No active session" };
    }

    try {
      return await this.rawCall<unknown>("logout", { session_id: this.sessionId }, true);
    } finally {
      this.sessionId = null;
    }
  }

  public async call<T>(method: string, params: JsonMap = {}): Promise<T> {
    const sessionId = await this.login();
    try {
      return await this.rawCall<T>(method, { session_id: sessionId, ...params }, true);
    } catch (error) {
      if (!this.shouldRetrySession(error)) {
        throw error;
      }

      this.sessionId = null;
      const refreshed = await this.login();
      return this.rawCall<T>(method, { session_id: refreshed, ...params }, true);
    }
  }

  private shouldRetrySession(error: unknown): boolean {
    if (error instanceof ISPConfigError) {
      return error.code === "auth_error" && error.retryable;
    }
    if (!(error instanceof Error)) {
      return false;
    }
    const msg = error.message.toLowerCase();
    return msg.includes("session") || msg.includes("invalid") || msg.includes("expired") || msg.includes("auth");
  }

  private async rawCall<T>(method: string, body: JsonMap, unwrapEnvelope: boolean): Promise<T> {
    const methodUrl = new URL(this.url.toString());
    methodUrl.search = method;

    const payload = JSON.stringify(body);
    const protocol = methodUrl.protocol === "https:" ? https : http;

    const requestOptions: https.RequestOptions = {
      method: "POST",
      hostname: methodUrl.hostname,
      port: methodUrl.port,
      path: `${methodUrl.pathname}${methodUrl.search}`,
      headers: {
        "content-type": "application/json",
        "content-length": Buffer.byteLength(payload),
      },
      timeout: this.timeoutMs,
      rejectUnauthorized: this.verifySsl,
    };

    const raw = await new Promise<string>((resolve, reject) => {
      const req = protocol.request(requestOptions, (res) => {
        const chunks: Buffer[] = [];
        res.on("data", (chunk: Buffer) => chunks.push(chunk));
        res.on("end", () => {
          const txt = Buffer.concat(chunks).toString("utf8");
          const status = res.statusCode ?? 500;
          if (status >= 400) {
            const code = status === 401 ? "auth_error"
              : status === 403 ? "permission_denied"
              : "api_error";
            reject(new ISPConfigError(code, `ISPConfig HTTP ${status}: ${txt}`, {
              statusCode: status,
              retryable: status >= 500 || status === 401,
            }));
            return;
          }
          resolve(txt);
        });
      });

      req.on("timeout", () => {
        req.destroy(new ISPConfigError("network_error",
          `ISPConfig request timeout after ${this.timeoutMs}ms`,
          { retryable: true },
        ));
      });

      req.on("error", (err) => {
        if (err instanceof ISPConfigError) {
          reject(err);
        } else {
          reject(new ISPConfigError("network_error", err.message, {
            retryable: true,
            cause: err,
          }));
        }
      });
      req.write(payload);
      req.end();
    });

    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch {
      throw new ISPConfigError("parse_error",
        `ISPConfig returned non-JSON response: ${raw}`);
    }

    if (!unwrapEnvelope) {
      return parsed as T;
    }

    const envelope = parsed as ISPConfigApiEnvelope<T>;

    if (envelope.code && envelope.code !== "ok") {
      const msg = `ISPConfig API ${envelope.code}: ${envelope.message ?? "Unknown error"}`;
      const errorCode = classifyApiMessage(msg);
      throw new ISPConfigError(errorCode, msg, {
        retryable: errorCode === "auth_error",
      });
    }

    if (Object.prototype.hasOwnProperty.call(envelope, "response")) {
      return envelope.response as T;
    }

    return parsed as T;
  }
}
