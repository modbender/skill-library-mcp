/**
 * Persistent WebSocket bridge to the Clawfinger gateway agent endpoint.
 *
 * - Auto-reconnect with exponential backoff (1s -> 30s max)
 * - Ping/pong heartbeat every 15s
 * - request_id correlation for takeover replies
 * - Event dispatch to registered listeners
 */

type EventCallback = (event: any) => void;

interface PendingRequest {
  resolve: (value: boolean) => void;
  timer: ReturnType<typeof setTimeout>;
}

interface Logger {
  info(msg: string): void;
  warn(msg: string): void;
  error(msg: string): void;
}

interface TurnRequest {
  session_id: string;
  transcript: string;
  request_id: string;
}

interface TurnWaiter {
  resolve: (value: TurnRequest | null) => void;
  timer: ReturnType<typeof setTimeout>;
}

export class WsBridge {
  private gatewayUrl: string;
  private logger: Logger;
  private ws: WebSocket | null = null;
  private listeners: EventCallback[] = [];
  private pendingAcks: Map<string, PendingRequest> = new Map();
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30_000;
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private shouldConnect = false;
  private turnQueue: TurnRequest[] = [];
  private turnWaiters: TurnWaiter[] = [];

  isConnected = false;
  takenOverSessions: Set<string> = new Set();

  constructor(gatewayUrl: string, logger: Logger) {
    this.gatewayUrl = gatewayUrl.replace(/\/+$/, "");
    this.logger = logger;
  }

  async connect(): Promise<void> {
    this.shouldConnect = true;
    await this.doConnect();
  }

  async disconnect(): Promise<void> {
    this.shouldConnect = false;
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.takenOverSessions.clear();
    this.turnQueue.length = 0;
    for (const w of this.turnWaiters) {
      clearTimeout(w.timer);
      w.resolve(null);
    }
    this.turnWaiters.length = 0;
  }

  onEvent(callback: EventCallback): void {
    this.listeners.push(callback);
  }

  /**
   * Take over LLM control for a session.
   * Sends takeover message and waits for ack.
   */
  async takeover(sessionId: string): Promise<boolean> {
    if (!this.ws || !this.isConnected) return false;
    const ok = await this.sendAndWaitAck("takeover", { session_id: sessionId }, "takeover.ack");
    if (ok) this.takenOverSessions.add(sessionId);
    return ok;
  }

  /**
   * Release LLM control for a session back to local gateway.
   */
  async release(sessionId: string): Promise<boolean> {
    if (!this.ws || !this.isConnected) return false;
    const ok = await this.sendAndWaitAck("release", { session_id: sessionId }, "release.ack");
    if (ok) this.takenOverSessions.delete(sessionId);
    return ok;
  }

  /**
   * Send a turn reply with request_id correlation (matches A1 protocol).
   */
  sendTurnReply(requestId: string, reply: string): void {
    this.sendRaw({ reply, request_id: requestId });
  }

  /**
   * Wait for the next turn.request to arrive in the queue.
   * Returns null if timeout expires before a request arrives.
   */
  popTurnRequest(timeoutMs: number): Promise<TurnRequest | null> {
    // If there's already a queued request, return it immediately
    if (this.turnQueue.length > 0) {
      return Promise.resolve(this.turnQueue.shift()!);
    }

    // Otherwise, wait for one to arrive
    return new Promise<TurnRequest | null>((resolve) => {
      const timer = setTimeout(() => {
        const idx = this.turnWaiters.findIndex((w) => w.resolve === resolve);
        if (idx !== -1) this.turnWaiters.splice(idx, 1);
        resolve(null);
      }, timeoutMs);

      this.turnWaiters.push({ resolve, timer });
    });
  }

  /**
   * Inject context into a session via WS.
   */
  async injectContext(sessionId: string, text: string): Promise<boolean> {
    return this.sendAndWaitAck(
      "inject_context",
      { session_id: sessionId, context: text },
      "inject_context.ack",
    );
  }

  /**
   * Clear context for a session via WS.
   */
  async clearContext(sessionId: string): Promise<boolean> {
    return this.sendAndWaitAck(
      "clear_context",
      { session_id: sessionId },
      "clear_context.ack",
    );
  }

  /**
   * Send a raw JSON message on the WebSocket.
   */
  sendRaw(msg: Record<string, unknown>): void {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(msg));
    }
  }

  // --- Internal ---

  private async doConnect(): Promise<void> {
    const wsUrl = this.gatewayUrl.replace(/^http/, "ws") + "/api/agent/ws";
    return new Promise<void>((resolve) => {
      try {
        this.ws = new WebSocket(wsUrl);
      } catch (err) {
        this.logger.error(`WS connect error: ${err}`);
        this.scheduleReconnect();
        resolve();
        return;
      }

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectDelay = 1000;
        this.startHeartbeat();
        this.logger.info("WS bridge connected");
        resolve();
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(String(event.data));
          this.handleMessage(msg);
        } catch {
          // ignore non-JSON
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.stopHeartbeat();
        this.takenOverSessions.clear();
        this.turnQueue.length = 0;
        for (const w of this.turnWaiters) {
          clearTimeout(w.timer);
          w.resolve(null);
        }
        this.turnWaiters.length = 0;
        if (this.shouldConnect) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err: Event) => {
        this.logger.warn(`WS error: ${err}`);
      };
    });
  }

  private handleMessage(msg: any): void {
    const msgType = String(msg.type || "");

    // Check for pending ack resolution
    if (msgType && this.pendingAcks.has(msgType)) {
      const pending = this.pendingAcks.get(msgType)!;
      clearTimeout(pending.timer);
      this.pendingAcks.delete(msgType);
      pending.resolve(msg.ok !== false);
    }

    // Dispatch to listeners
    for (const cb of this.listeners) {
      try {
        cb(msg);
      } catch {
        // listener errors should not break the bridge
      }
    }

    // Queue turn.request events for popTurnRequest consumers
    if (msgType === "turn.request") {
      // Fields may be at top level or nested in msg.data
      const d = msg.data || msg;
      const request_id = d.request_id || msg.request_id;
      if (request_id) {
        const turn: TurnRequest = {
          session_id: d.session_id || msg.session_id || "",
          transcript: d.transcript || msg.transcript || "",
          request_id,
        };

        // Discard any older requests for the same session — they're stale
        // (gateway already timed out and fell back to local LLM)
        this.turnQueue = this.turnQueue.filter(
          (t) => t.session_id !== turn.session_id,
        );

        // If someone is waiting, deliver directly; otherwise queue
        if (this.turnWaiters.length > 0) {
          const waiter = this.turnWaiters.shift()!;
          clearTimeout(waiter.timer);
          waiter.resolve(turn);
        } else {
          this.turnQueue.push(turn);
        }
      }
    }
  }

  private async sendAndWaitAck(
    type: string,
    payload: Record<string, unknown>,
    ackType: string,
    timeout = 10_000,
  ): Promise<boolean> {
    if (!this.ws || !this.isConnected) return false;

    return new Promise<boolean>((resolve) => {
      const timer = setTimeout(() => {
        this.pendingAcks.delete(ackType);
        resolve(false);
      }, timeout);

      this.pendingAcks.set(ackType, { resolve, timer });
      this.ws!.send(JSON.stringify({ type, ...payload }));
    });
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.isConnected) {
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 15_000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private scheduleReconnect(): void {
    if (!this.shouldConnect) return;
    const delay = this.reconnectDelay;
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    this.logger.info(`WS reconnecting in ${delay}ms...`);
    setTimeout(() => {
      if (this.shouldConnect) this.doConnect();
    }, delay);
  }
}
