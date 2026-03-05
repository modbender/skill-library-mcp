/**
 * PROPOSE phase: ActionIntent serialization and cryptographic binding.
 *
 * Captures agent tool calls as structured ActionIntent objects with
 * SHA-256 hash binding for tamper-evident governance evaluation.
 */

import { createHash, randomUUID } from "node:crypto";

// ── Types ────────────────────────────────────────────────────────────

export type ActionType = "read" | "write" | "execute" | "network" | "create" | "delete";

const VALID_ACTION_TYPES: ReadonlySet<string> = new Set([
  "read", "write", "execute", "network", "create", "delete",
]);

export interface ActionIntent {
  id: string;
  timestamp: string;
  source: {
    skill: string;
    tool: string;
    model: string;
  };
  action: {
    type: ActionType;
    target: string;
    parameters: Record<string, unknown>;
    data_scope: string[];
  };
  context: {
    conversation_id: string;
    message_id: string;
    user_instruction: string;
  };
  intent_hash: string;
}

export interface CreateIntentParams {
  skill: string;
  tool: string;
  model: string;
  actionType: ActionType;
  target: string;
  parameters: Record<string, unknown>;
  dataScope: string[];
  conversationId: string;
  messageId: string;
  userInstruction: string;
}

// ── Canonical serialization ──────────────────────────────────────────

/**
 * Produces deterministic JSON: sorted keys at all levels, no whitespace.
 * This is the canonical form used for hash computation.
 */
export function canonicalize(obj: unknown): string {
  if (obj === null || obj === undefined) return "null";
  if (typeof obj === "string") return JSON.stringify(obj);
  if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
  if (Array.isArray(obj)) {
    return "[" + obj.map(canonicalize).join(",") + "]";
  }
  if (typeof obj === "object") {
    const keys = Object.keys(obj as Record<string, unknown>).sort();
    const pairs = keys.map(
      (k) => JSON.stringify(k) + ":" + canonicalize((obj as Record<string, unknown>)[k])
    );
    return "{" + pairs.join(",") + "}";
  }
  return String(obj);
}

/**
 * SHA-256 hash of canonical JSON serialization.
 */
export function computeHash(data: string): string {
  return createHash("sha256").update(data, "utf8").digest("hex");
}

/**
 * Compute the intent_hash for an ActionIntent (excludes the hash field itself).
 */
export function computeIntentHash(intent: Omit<ActionIntent, "intent_hash">): string {
  return computeHash(canonicalize(intent));
}

// ── Intent creation ──────────────────────────────────────────────────

export function createIntent(params: CreateIntentParams): ActionIntent {
  const partial = {
    id: randomUUID(),
    timestamp: new Date().toISOString(),
    source: {
      skill: params.skill,
      tool: params.tool,
      model: params.model,
    },
    action: {
      type: params.actionType,
      target: params.target,
      parameters: params.parameters,
      data_scope: params.dataScope,
    },
    context: {
      conversation_id: params.conversationId,
      message_id: params.messageId,
      user_instruction: params.userInstruction,
    },
  };

  const intent_hash = computeIntentHash(partial);
  return { ...partial, intent_hash };
}

// ── Validation ───────────────────────────────────────────────────────

export interface ValidationError {
  field: string;
  message: string;
}

export function validateIntent(intent: unknown): { valid: true; intent: ActionIntent } | { valid: false; errors: ValidationError[] } {
  const errors: ValidationError[] = [];

  if (intent === null || typeof intent !== "object") {
    return { valid: false, errors: [{ field: "root", message: "Intent must be an object" }] };
  }

  const obj = intent as Record<string, unknown>;

  // Top-level fields
  if (typeof obj["id"] !== "string" || obj["id"] === "") {
    errors.push({ field: "id", message: "Must be a non-empty string" });
  }
  if (typeof obj["timestamp"] !== "string" || obj["timestamp"] === "") {
    errors.push({ field: "timestamp", message: "Must be a non-empty ISO 8601 string" });
  }

  // Source
  if (obj["source"] === null || typeof obj["source"] !== "object") {
    errors.push({ field: "source", message: "Must be an object" });
  } else {
    const src = obj["source"] as Record<string, unknown>;
    if (typeof src["skill"] !== "string") errors.push({ field: "source.skill", message: "Must be a string" });
    if (typeof src["tool"] !== "string") errors.push({ field: "source.tool", message: "Must be a string" });
    if (typeof src["model"] !== "string") errors.push({ field: "source.model", message: "Must be a string" });
  }

  // Action
  if (obj["action"] === null || typeof obj["action"] !== "object") {
    errors.push({ field: "action", message: "Must be an object" });
  } else {
    const act = obj["action"] as Record<string, unknown>;
    if (typeof act["type"] !== "string" || !VALID_ACTION_TYPES.has(act["type"])) {
      errors.push({ field: "action.type", message: `Must be one of: ${[...VALID_ACTION_TYPES].join(", ")}` });
    }
    if (typeof act["target"] !== "string") {
      errors.push({ field: "action.target", message: "Must be a string" });
    }
    if (act["parameters"] === null || typeof act["parameters"] !== "object" || Array.isArray(act["parameters"])) {
      errors.push({ field: "action.parameters", message: "Must be an object" });
    }
    if (!Array.isArray(act["data_scope"])) {
      errors.push({ field: "action.data_scope", message: "Must be an array" });
    }
  }

  // Context
  if (obj["context"] === null || typeof obj["context"] !== "object") {
    errors.push({ field: "context", message: "Must be an object" });
  } else {
    const ctx = obj["context"] as Record<string, unknown>;
    if (typeof ctx["conversation_id"] !== "string") errors.push({ field: "context.conversation_id", message: "Must be a string" });
    if (typeof ctx["message_id"] !== "string") errors.push({ field: "context.message_id", message: "Must be a string" });
    if (typeof ctx["user_instruction"] !== "string") errors.push({ field: "context.user_instruction", message: "Must be a string" });
  }

  // Intent hash
  if (typeof obj["intent_hash"] !== "string" || obj["intent_hash"] === "") {
    errors.push({ field: "intent_hash", message: "Must be a non-empty string" });
  }

  if (errors.length > 0) return { valid: false, errors };

  // Verify hash integrity
  const typedObj = obj as unknown as ActionIntent;
  const { intent_hash: existingHash, ...rest } = typedObj;
  const expectedHash = computeIntentHash(rest);
  if (existingHash !== expectedHash) {
    errors.push({ field: "intent_hash", message: "Hash does not match canonical serialization" });
    return { valid: false, errors };
  }

  return { valid: true, intent: typedObj };
}
