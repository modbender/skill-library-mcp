import type { RenderData } from "declare-render";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  image?: string;
  /** Agent name — when set, this is an agent step message (display only, not sent to backend). */
  agent?: string;
  /** Thinking content accumulated from the agent's <think> output. */
  thinking?: string;
  /** Hidden messages are sent to backend as context but not displayed. */
  hidden?: boolean;
}

export interface ChatRequestBody {
  messages: ChatMessage[];
  currentRenderData?: RenderData | null;
}

export interface ChatResponse {
  message: { role: "assistant"; content: string };
  renderData?: RenderData;
}

// ── Stream event types (mirrors server StreamEvent) ──

export type StreamEvent =
  | { type: "agent_start"; agent: string; attempt?: number }
  | { type: "agent_end"; agent: string }
  | { type: "thinking_delta"; agent: string; delta: string }
  | { type: "text_delta"; agent: string; delta: string }
  | { type: "text"; agent: string; content: string }
  | { type: "render_data"; renderData: RenderData; attempt?: number; isNewCanvas?: boolean }
  | { type: "verification"; passed: boolean; errors: string[]; feedback: string; attempt: number }
  | { type: "done" }
  | { type: "error"; message: string };

// ── SSE streaming chat ──

export async function postChatStream(
  body: ChatRequestBody,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error((err as { error?: string }).error ?? "Chat failed");
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;
      try {
        const event = JSON.parse(trimmed.slice(6)) as StreamEvent;
        onEvent(event);
      } catch {
        // skip malformed
      }
    }
  }

  if (buffer.trim().startsWith("data: ")) {
    try {
      const event = JSON.parse(buffer.trim().slice(6)) as StreamEvent;
      onEvent(event);
    } catch {
      // ignore
    }
  }
}

