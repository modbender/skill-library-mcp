export interface IncomingMessage {
  type: "prompt" | "status" | "restart" | "workflow";
  request_id: string;
  data?: Record<string, unknown>;
}

export type ConnectionState = "online" | "reconnecting" | "offline";

export interface HeartbeatPayload {
  node_id: string;
  uptime: number;
  active_tasks: number;
  last_error: string | null;
  connection_state: ConnectionState;
}

export interface TokenChunk {
  type: "token";
  request_id: string;
  content: string;
}

export interface DoneMessage {
  type: "done";
  request_id: string;
}

export interface StatusResponse {
  type: "status";
  node_id: string;
  uptime: number;
  active_tasks: number;
  last_error: string | null;
  connection_state: ConnectionState;
}

export interface ErrorResponse {
  type: "error";
  request_id: string;
  message: string;
}

export type OutgoingMessage =
  | HeartbeatPayload
  | TokenChunk
  | DoneMessage
  | StatusResponse
  | ErrorResponse;

/**
 * Interface that the host OpenClaw runtime must implement
 * so the relay skill can execute prompts, tasks, and restarts.
 */
export interface OpenClawRuntime {
  /** Execute a prompt and yield streamed tokens via callback. */
  executePrompt(
    prompt: string,
    onToken: (token: string) => void
  ): Promise<void>;

  /** Execute a named workflow/task. */
  executeWorkflow(
    workflowId: string,
    params: Record<string, unknown>
  ): Promise<void>;

  /** Return the count of currently running tasks. */
  getRunningTaskCount(): number;

  /** Return the last error string, or null. */
  getLastError(): string | null;

  /** Gracefully restart the OpenClaw process. */
  restart(): Promise<void>;
}
