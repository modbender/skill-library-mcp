/**
 * REST client for Clawfinger gateway endpoints.
 *
 * Thin wrapper around fetch() — every method corresponds to a gateway
 * REST endpoint documented in skills/voice-gateway/SKILL.md.
 */

export class GatewayClient {
  private baseUrl: string;
  private bearerToken: string;

  constructor(baseUrl: string, bearerToken: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.bearerToken = bearerToken;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.bearerToken) {
      h["Authorization"] = `Bearer ${this.bearerToken}`;
    }
    return h;
  }

  private async get(path: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "GET",
      headers: this.headers(),
    });
    return res.json();
  }

  private async post(path: string, body?: any): Promise<any> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return res.json();
  }

  private async del(path: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    return res.json();
  }

  // --- Health / status ---

  async status(): Promise<any> {
    return this.get("/api/status");
  }

  // --- Call control ---

  async dial(number: string): Promise<any> {
    return this.post("/api/call/dial", { number });
  }

  async hangup(sessionId?: string): Promise<any> {
    return this.post("/api/call/hangup", { session_id: sessionId || "" });
  }

  async inject(text: string, sessionId?: string): Promise<any> {
    return this.post("/api/agent/inject", { text, session_id: sessionId || "" });
  }

  // --- Sessions ---

  async getSessions(): Promise<string[]> {
    return this.get("/api/agent/sessions");
  }

  async getCallState(sessionId: string): Promise<any> {
    return this.get(`/api/agent/call/${sessionId}`);
  }

  async endSession(sessionId: string): Promise<any> {
    return this.post("/api/session/end", { session_id: sessionId });
  }

  // --- Context ---

  async getContext(sessionId: string): Promise<any> {
    return this.get(`/api/agent/context/${sessionId}`);
  }

  async setContext(sessionId: string, text: string): Promise<any> {
    return this.post(`/api/agent/context/${sessionId}`, { context: text });
  }

  async clearContext(sessionId: string): Promise<any> {
    return this.del(`/api/agent/context/${sessionId}`);
  }

  // --- Config: Call ---

  async getCallConfig(): Promise<any> {
    return this.get("/api/config/call");
  }

  async setCallConfig(patch: Record<string, unknown>): Promise<any> {
    return this.post("/api/config/call", patch);
  }

  // --- Config: TTS ---

  async getTtsConfig(): Promise<any> {
    return this.get("/api/config/tts");
  }

  async setTtsConfig(patch: Record<string, unknown>): Promise<any> {
    return this.post("/api/config/tts", patch);
  }

  // --- Config: LLM ---

  async getLlmConfig(): Promise<any> {
    return this.get("/api/config/llm");
  }

  async setLlmConfig(patch: Record<string, unknown>): Promise<any> {
    return this.post("/api/config/llm", patch);
  }
}
