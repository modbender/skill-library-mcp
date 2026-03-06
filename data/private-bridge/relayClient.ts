import { RemoteRelayConfig, validateConfig } from "./config";
import {
  IncomingMessage,
  HeartbeatPayload,
  ConnectionState,
  OpenClawRuntime,
} from "./capabilities";

const HEARTBEAT_INTERVAL = 15_000;
const MAX_BACKOFF = 30_000;
const INITIAL_BACKOFF = 1_000;

export class RelayClient {
  private config: RemoteRelayConfig;
  private runtime: OpenClawRuntime;
  private ws: WebSocket | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private backoff = INITIAL_BACKOFF;
  private startTime = Date.now();
  private intentionalClose = false;
  private connectionState: ConnectionState = "offline";

  constructor(rawConfig: Partial<RemoteRelayConfig>, runtime: OpenClawRuntime) {
    this.config = validateConfig(rawConfig);
    this.runtime = runtime;
  }

  /** Start the relay connection. */
  connect(): void {
    this.intentionalClose = false;
    this.openSocket();
  }

  /** Gracefully disconnect. */
  disconnect(): void {
    this.intentionalClose = true;
    this.connectionState = "offline";
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, "shutdown");
      this.ws = null;
    }
  }

  private openSocket(): void {
    const url = `${this.config.relay_url}/connect`;
    this.connectionState = "reconnecting";
    console.log(`[private-bridge] Connecting to ${url}`);

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("[private-bridge] Connected, sending auth");
      this.send({
        type: "hello",
        data: {
          node_id: this.config.node_id,
          token: this.config.auth_token,
          meta: { kind: "openclaw" },
        },
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(String(event.data));
        this.handleMessage(msg);
      } catch {
        console.error("[private-bridge] Invalid message received");
      }
    };

    this.ws.onclose = () => {
      this.stopHeartbeat();
      if (!this.intentionalClose) {
        console.log(
          `[private-bridge] Disconnected, reconnecting in ${this.backoff}ms`
        );
        setTimeout(() => this.openSocket(), this.backoff);
        this.backoff = Math.min(this.backoff * 2, MAX_BACKOFF);
      }
    };

    this.ws.onerror = (err) => {
      console.error("[private-bridge] WebSocket error", err);
    };
  }

  private handleMessage(msg: { type: string; data?: unknown }): void {
    switch (msg.type) {
      case "hello_ok":
        console.log("[private-bridge] Authenticated");
        this.backoff = INITIAL_BACKOFF;
        this.connectionState = "online";
        this.startHeartbeat();
        break;

      case "prompt":
      case "status":
      case "restart":
      case "workflow":
        this.dispatch(msg as { type: string; data: IncomingMessage });
        break;

      case "error":
        console.error("[private-bridge] Relay error:", msg.data);
        break;

      default:
        console.warn(`[private-bridge] Rejecting unknown type: ${msg.type}`);
        break;
    }
  }

  private async dispatch(envelope: {
    type: string;
    data: IncomingMessage;
  }): Promise<void> {
    const { data } = envelope;
    const requestId = data?.request_id ?? "unknown";

    try {
      switch (envelope.type) {
        case "prompt": {
          const prompt = (data.data as { prompt?: string })?.prompt ?? "";
          await this.runtime.executePrompt(prompt, (token) => {
            this.send({
              type: "response",
              data: { type: "token", request_id: requestId, content: token },
            });
          });
          this.send({
            type: "response",
            data: { type: "done", request_id: requestId },
          });
          break;
        }

        case "status":
          this.send({
            type: "response",
            data: {
              type: "status",
              request_id: requestId,
              ...this.buildHeartbeat(),
            },
          });
          break;

        case "restart":
          this.send({
            type: "response",
            data: {
              type: "done",
              request_id: requestId,
            },
          });
          await this.runtime.restart();
          break;

        case "workflow": {
          const workflowId =
            (data.data as { workflow_id?: string })?.workflow_id ?? "";
          const params =
            (data.data as { params?: Record<string, unknown> })?.params ?? {};
          await this.runtime.executeWorkflow(workflowId, params);
          this.send({
            type: "response",
            data: { type: "done", request_id: requestId },
          });
          break;
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      this.send({
        type: "response",
        data: { type: "error", request_id: requestId, message },
      });
    }
  }

  private buildHeartbeat(): HeartbeatPayload {
    return {
      node_id: this.config.node_id,
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
      active_tasks: this.runtime.getRunningTaskCount(),
      last_error: this.runtime.getLastError(),
      connection_state: this.connectionState,
    };
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: "heartbeat", data: this.buildHeartbeat() });
    }, HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private send(msg: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    }
  }
}
