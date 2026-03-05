/**
 * Parse Kimi stream-json output: one JSON object per line.
 * Find last assistant message and extract last content part with type "text".
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type JsonValue = any;

export interface ParseResult {
  finalText: string;
  raw: JsonValue[];
}

interface StreamMessage {
  role?: string;
  content?: string | JsonValue[];
  [key: string]: JsonValue;
}

function extractTextFromContent(content: JsonValue): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  let text = "";
  for (const part of content) {
    if (
      part &&
      typeof part === "object" &&
      part.type === "text" &&
      typeof part.text === "string"
    ) {
      text = part.text;
    }
  }
  return text;
}

export function parseStreamJson(lines: string[]): ParseResult {
  const raw: JsonValue[] = [];
  let lastAssistantText = "";

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      const obj = JSON.parse(trimmed) as JsonValue;
      raw.push(obj);
      const msg = obj as StreamMessage;
      if (msg.role === "assistant" && msg.content !== undefined) {
        lastAssistantText = extractTextFromContent(msg.content);
      }
    } catch {
      // skip non-JSON lines
    }
  }

  return { finalText: lastAssistantText, raw };
}
