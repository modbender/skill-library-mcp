/**
 * OpenClaw Gateway WebSocket Client
 *
 * Connects to the OpenClaw Gateway control plane and provides:
 * - Auto-reconnection with exponential backoff
 * - Request/response correlation via message IDs
 * - Event stream subscription
 * - Agent turn execution with streaming
 *
 * Protocol reference: https://docs.openclaw.ai/concepts/architecture
 *
 * Frame format:
 *   Request:  { type: "req",   id, method, params }
 *   Response: { type: "res",   id, ok, payload | error }
 *   Event:    { type: "event", event, payload, seq?, stateVersion? }
 */

import type {
  GatewayFrame,
  GatewayResponse,
  GatewayEvent,
} from "../types";

type EventHandler = (event: GatewayEvent) => void;
type ConnectionHandler = (connected: boolean) => void;

interface PendingRequest {
  resolve: (res: GatewayResponse) => void;
  reject: (err: Error) => void;
  timeout: ReturnType<typeof setTimeout>;
}

interface GatewayClientOptions {
  url: string;
  token?: string;
  /** Called on every event frame */
  onEvent?: EventHandler;
  /** Called when connection state changes */
  onConnection?: ConnectionHandler;
  /** Max reconnection attempts (default: Infinity) */
  maxReconnectAttempts?: number;
  /** Base reconnect delay in ms (default: 1000) */
  reconnectBaseDelay?: number;
  /** Request timeout in ms (default: 30000) */
  requestTimeout?: number;
}

export class GatewayClient {
  private ws: WebSocket | null = null;
  private options: Required<GatewayClientOptions>;
  private pending = new Map<string, PendingRequest>();
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionalClose = false;
  private _connected = false;
  private msgCounter = 0;

  constructor(opts: GatewayClientOptions) {
    this.options = {
      url: opts.url,
      token: opts.token ?? "",
      onEvent: opts.onEvent ?? (() => {}),
      onConnection: opts.onConnection ?? (() => {}),
      maxReconnectAttempts: opts.maxReconnectAttempts ?? Infinity,
      reconnectBaseDelay: opts.reconnectBaseDelay ?? 1000,
      requestTimeout: opts.requestTimeout ?? 30_000,
    };
  }

  get connected() {
    return this._connected;
  }

  /** Open the WebSocket connection and perform the handshake */
  connect(): void {
    this.intentionalClose = false;
    this.createSocket();
  }

  /** Gracefully close the connection */
  disconnect(): void {
    this.intentionalClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close(1000, "client disconnect");
  }

  /**
   * Send a request and await the correlated response.
   * Rejects if the gateway returns ok:false or on timeout.
   */
  async request(
    method: string,
    params?: Record<string, unknown>
  ): Promise<unknown> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("Gateway not connected");
    }

    const id = this.nextId();

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Request ${method} timed out`));
      }, this.options.requestTimeout);

      this.pending.set(id, {
        resolve: (res) => {
          clearTimeout(timeout);
          this.pending.delete(id);
          if (res.ok) {
            resolve(res.payload);
          } else {
            reject(
              new Error(res.error?.message ?? `Request ${method} failed`)
            );
          }
        },
        reject: (err) => {
          clearTimeout(timeout);
          this.pending.delete(id);
          reject(err);
        },
        timeout,
      });

      this.send({ type: "req", id, method, params: params ?? {} });
    });
  }

  /**
   * Run an agent turn. Sends `req:agent` and returns the initial ack.
   * Streaming content arrives as `event:agent` frames via onEvent.
   *
   * @param agentId - The agent to address
   * @param message - User message text
   * @param sessionKey - Optional session key override
   * @returns The initial response with { runId, status }
   */
  async runAgent(
    agentId: string,
    message: string,
    sessionKey?: string
  ): Promise<{ runId: string; status: string }> {
    const idempotencyKey = `agent-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 8)}`;

    const result = await this.request("agent", {
      agentId,
      message,
      sessionKey,
      idempotencyKey,
    });

    return result as { runId: string; status: string };
  }

  /**
   * Send a message to a channel via the gateway.
   */
  async sendMessage(
    channel: string,
    peerId: string,
    text: string
  ): Promise<unknown> {
    const idempotencyKey = `send-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 8)}`;

    return this.request("send", {
      channel,
      peerId,
      text,
      idempotencyKey,
    });
  }

  /** Get current gateway health */
  async health(): Promise<unknown> {
    return this.request("health");
  }

  // ─── Private ───

  private createSocket() {
    try {
      this.ws = new WebSocket(this.options.url);
    } catch (err) {
      console.error("[GatewayClient] Failed to create WebSocket:", err);
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = async () => {
      console.log("[GatewayClient] Socket opened, sending handshake...");
      try {
        await this.request("connect", {
          client: {
            id: "gateway-client",
            version: "0.1.0",
            platform: "web",
            mode: "webchat",
          },
          minProtocol: 3,
          maxProtocol: 3,
          auth: this.options.token
            ? { token: this.options.token }
            : undefined,
        });
        this._connected = true;
        this.reconnectAttempts = 0;
        this.options.onConnection(true);
        console.log("[GatewayClient] Connected to gateway");
      } catch (err) {
        console.error("[GatewayClient] Handshake failed:", err);
        this.ws?.close(4001, "handshake failed");
      }
    };

    this.ws.onmessage = (evt) => {
      try {
        const frame: GatewayFrame = JSON.parse(evt.data as string);
        this.handleFrame(frame);
      } catch (err) {
        console.warn("[GatewayClient] Failed to parse frame:", err);
      }
    };

    this.ws.onclose = (evt) => {
      const wasConnected = this._connected;
      this._connected = false;

      if (wasConnected) {
        this.options.onConnection(false);
      }

      // Reject all pending requests
      for (const [, pending] of this.pending) {
        pending.reject(new Error("Connection closed"));
      }
      this.pending.clear();

      if (!this.intentionalClose) {
        console.log(
          `[GatewayClient] Connection closed (code=${evt.code}), will reconnect...`
        );
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (err) => {
      console.error("[GatewayClient] WebSocket error:", err);
    };
  }

  private handleFrame(frame: GatewayFrame) {
    switch (frame.type) {
      case "res": {
        const pending = this.pending.get(frame.id);
        if (pending) {
          pending.resolve(frame);
        }
        break;
      }
      case "event": {
        this.options.onEvent(frame);
        break;
      }
      default:
        break;
    }
  }

  private send(frame: GatewayFrame) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(frame));
    }
  }

  private nextId(): string {
    return `deck-${++this.msgCounter}-${Date.now()}`;
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error("[GatewayClient] Max reconnect attempts reached");
      return;
    }

    const delay = Math.min(
      this.options.reconnectBaseDelay * Math.pow(2, this.reconnectAttempts),
      30_000
    );

    console.log(
      `[GatewayClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})...`
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.createSocket();
    }, delay);
  }
}
