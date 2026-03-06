export * from "./types.js";
export * from "./redaction.js";
export * from "./embedding.js";
export * from "./store-jsonl.js";
export * from "./utils.js";

import { randomUUID as nodeRandomUUID } from "node:crypto";

export function uuid(): string {
  // Prefer globalThis.crypto.randomUUID (available in Node 19+ and browsers)
  const c = globalThis.crypto;
  if (c?.randomUUID) return c.randomUUID();
  // Fallback to node:crypto module (works on Node 18 where globalThis.crypto
  // does not expose randomUUID)
  if (nodeRandomUUID) return nodeRandomUUID();
  // Manual fallback using getRandomValues
  if (c?.getRandomValues) {
    const bytes = new Uint8Array(16);
    c.getRandomValues(bytes);
    bytes[6] = (bytes[6]! & 0x0f) | 0x40; // version 4
    bytes[8] = (bytes[8]! & 0x3f) | 0x80; // variant
    const hex = Array.from(bytes).map((b) => b.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
  }
  throw new RangeError("[openclaw] crypto.randomUUID and crypto.getRandomValues are unavailable. Node 18+ required.");
}
