import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import type { PluginConfig } from "./config.js";
import { ShieldUnavailableError } from "./errors.js";

/** Parsed result from any scan_* tool call. */
export interface ScanResult {
  verdict: string;
  is_blocked: boolean;
  threat_count: number;
  max_threat_level: string;
  elapsed_ms: number;
  threats: Array<{
    category: string;
    level: string;
    description: string;
    evidence: string;
    confidence: number;
    signature_id: string | null;
  }>;
}

/** Dashboard + audit data from get_threat_report. */
export interface ThreatReport {
  dashboard: Record<string, unknown>;
  recent_events: unknown[];
}

/** Logger interface matching OpenClaw's api.logger shape. */
export interface Logger {
  info(msg: string, ...args: unknown[]): void;
  warn(msg: string, ...args: unknown[]): void;
  error(msg: string, ...args: unknown[]): void;
  debug(msg: string, ...args: unknown[]): void;
}

/**
 * Manages a long-lived `zugashield-mcp` Python child process over stdio.
 *
 * Key behaviors:
 * - `start()` spawns the process and performs the MCP handshake
 * - `stop()` gracefully terminates the process
 * - If the process crashes, `_scheduleReconnect()` retries with exponential backoff + jitter
 * - Each scan method wraps `_callTool()` with a per-call timeout via `Promise.race`
 */
export class ShieldClient {
  private client: Client | null = null;
  private transport: StdioClientTransport | null = null;
  private config: PluginConfig;
  private logger: Logger;

  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private stopping = false;

  /** Scan counters for /shield report. */
  public stats = { scans: 0, blocks: 0, errors: 0 };

  constructor(config: PluginConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
  }

  /** True when the MCP client has an active connection. */
  get connected(): boolean {
    return this.client !== null;
  }

  // ─── Lifecycle ──────────────────────────────────────────

  async start(): Promise<void> {
    this.stopping = false;
    this.reconnectAttempt = 0;
    await this._connect();
  }

  async stop(): Promise<void> {
    this.stopping = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    await this._disconnect();
  }

  // ─── Scan Methods ───────────────────────────────────────

  async scanInput(text: string, sessionId?: string): Promise<ScanResult> {
    return this._callScan("scan_input", { text, session_id: sessionId });
  }

  async scanOutput(text: string, sessionId?: string): Promise<ScanResult> {
    return this._callScan("scan_output", { text, session_id: sessionId });
  }

  async scanToolCall(
    toolName: string,
    params: Record<string, unknown>,
    sessionId?: string,
  ): Promise<ScanResult> {
    return this._callScan("scan_tool_call", {
      tool_name: toolName,
      params,
      session_id: sessionId,
    });
  }

  async scanMemory(content: string, source?: string): Promise<ScanResult> {
    return this._callScan("scan_memory", { content, source });
  }

  async getThreatReport(limit = 20): Promise<ThreatReport> {
    const raw = await this._callTool("get_threat_report", { limit });
    return JSON.parse(raw) as ThreatReport;
  }

  async getConfig(): Promise<Record<string, unknown>> {
    const raw = await this._callTool("get_config", {});
    return JSON.parse(raw) as Record<string, unknown>;
  }

  // ─── Internal ───────────────────────────────────────────

  private async _callScan(
    tool: string,
    args: Record<string, unknown>,
  ): Promise<ScanResult> {
    this.stats.scans++;
    const raw = await this._callTool(tool, args);
    const result = JSON.parse(raw) as ScanResult;
    if (result.is_blocked) this.stats.blocks++;
    return result;
  }

  /**
   * Calls an MCP tool with a per-call timeout.
   * Throws `ShieldUnavailableError` if not connected.
   * Uses AbortController-style cleanup to avoid timer leaks on fast paths.
   */
  private async _callTool(
    name: string,
    args: Record<string, unknown>,
  ): Promise<string> {
    if (!this.client) {
      throw new ShieldUnavailableError("MCP server not connected");
    }

    const timeout = this.config.mcp.call_timeout_ms;
    let timer: ReturnType<typeof setTimeout>;

    const raw = await Promise.race([
      this.client.callTool({ name, arguments: args }),
      new Promise<never>((_, reject) => {
        timer = setTimeout(
          () => reject(new ShieldUnavailableError(`Tool "${name}" timed out after ${timeout}ms`)),
          timeout,
        );
      }),
    ]).finally(() => clearTimeout(timer));

    // Cast to concrete shape — Promise.race loses specificity due to index signature
    const result = raw as {
      content: Array<{ type: string; text?: string }>;
      isError?: boolean;
    };

    if (result.isError) {
      const text = result.content
        .filter((c): c is { type: "text"; text: string } => c.type === "text" && typeof c.text === "string")
        .map(c => c.text)
        .join("\n");
      throw new Error(`ZugaShield tool "${name}" error: ${text}`);
    }

    // Extract text content from the MCP response
    return result.content
      .filter((c): c is { type: "text"; text: string } => c.type === "text" && typeof c.text === "string")
      .map(c => c.text)
      .join("\n");
  }

  // ─── Connection Management ──────────────────────────────

  /**
   * Build a minimal environment for the child process.
   * Only passes through variables needed for Python to run correctly.
   * Prevents leaking host secrets (API keys, credentials) to the child.
   */
  private _buildChildEnv(): Record<string, string> {
    const allowlist = [
      // System essentials
      "PATH", "SYSTEMROOT", "TEMP", "TMP", "HOME", "USERPROFILE",
      "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA",
      // Python runtime
      "PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX",
      // ZugaShield config (safe — these are non-secret settings)
      "ZUGASHIELD_ENABLED", "ZUGASHIELD_STRICT_MODE", "ZUGASHIELD_FAIL_CLOSED",
      "ZUGASHIELD_LOG_LEVEL", "ZUGASHIELD_VERIFY_SIGNATURES",
      "ZUGASHIELD_FEED_ENABLED", "ZUGASHIELD_FEED_URL",
      "ZUGASHIELD_FEED_POLL_INTERVAL", "ZUGASHIELD_FEED_STATE_DIR",
    ];

    const env: Record<string, string> = { PYTHONUNBUFFERED: "1" };
    for (const key of allowlist) {
      const val = process.env[key];
      if (val !== undefined) env[key] = val;
    }
    return env;
  }

  private async _connect(): Promise<void> {
    this.transport = new StdioClientTransport({
      command: this.config.mcp.python_executable,
      args: ["-m", "zugashield_mcp.server"],
      env: this._buildChildEnv(),
      stderr: "pipe",
    });

    // Wire lifecycle events BEFORE connect
    this.transport.onclose = () => {
      this.logger.warn("ZugaShield MCP server disconnected");
      this.client = null;
      this.transport = null;
      if (!this.stopping) this._scheduleReconnect();
    };

    this.transport.onerror = (error: Error) => {
      this.logger.error("ZugaShield MCP transport error:", error.message);
      this.stats.errors++;
    };

    this.client = new Client(
      { name: "zugashield-openclaw", version: "0.1.0" },
      { capabilities: {} },
    );

    // connect() spawns the process + performs MCP handshake
    const startupTimeout = this.config.mcp.startup_timeout_ms;
    let startupTimer: ReturnType<typeof setTimeout>;
    await Promise.race([
      this.client.connect(this.transport),
      new Promise<never>((_, reject) => {
        startupTimer = setTimeout(
          () => reject(new Error(`MCP startup timed out after ${startupTimeout}ms`)),
          startupTimeout,
        );
      }),
    ]).finally(() => clearTimeout(startupTimer!));

    // Capture stderr for diagnostics
    this.transport.stderr?.on("data", (chunk: Buffer) => {
      this.logger.debug(`[zugashield-mcp] ${chunk.toString().trimEnd()}`);
    });

    this.reconnectAttempt = 0;
    this.logger.info("ZugaShield MCP server connected");
  }

  private async _disconnect(): Promise<void> {
    if (this.transport) {
      try {
        await this.transport.close();
      } catch {
        // Process may already be dead
      }
      this.transport = null;
      this.client = null;
    }
  }

  /**
   * Exponential backoff with jitter: 500ms * 2^attempt, capped at 30s.
   * Gives up after `max_reconnect_attempts`.
   */
  private _scheduleReconnect(): void {
    const max = this.config.mcp.max_reconnect_attempts;
    if (this.reconnectAttempt >= max) {
      this.logger.error(
        `ZugaShield: gave up reconnecting after ${max} attempts`,
      );
      return;
    }

    const base = 500;
    const cap = 30_000;
    const delay = Math.min(base * 2 ** this.reconnectAttempt, cap);
    const jitter = delay * (0.5 + Math.random() * 0.5);

    this.reconnectAttempt++;
    this.logger.warn(
      `ZugaShield: reconnecting in ${Math.round(jitter)}ms (attempt ${this.reconnectAttempt}/${max})`,
    );

    this.reconnectTimer = setTimeout(async () => {
      try {
        await this._connect();
      } catch (err) {
        this.logger.error("ZugaShield: reconnect failed:", (err as Error).message);
        this._scheduleReconnect();
      }
    }, jitter);
  }
}
