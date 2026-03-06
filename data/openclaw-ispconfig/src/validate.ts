import { ISPConfigError } from "./errors";
import { JsonMap } from "./types";

// ---------------------------------------------------------------------------
// Schema types
// ---------------------------------------------------------------------------

interface ParamRule {
  /** Expected value type */
  type?: "string" | "number" | "boolean";
  /** Field must be present and non-null */
  required?: boolean;
  /** String value must not be empty/whitespace-only */
  notEmpty?: boolean;
  /** Allowed values (compared case-insensitively for strings) */
  enum?: string[];
}

interface ToolParamSchema {
  /** Per-field validation rules */
  fields?: Record<string, ParamRule>;
  /** At least one key from each group must be present (OR logic within group) */
  anyOf?: string[][];
}

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

const DNS_TYPES = ["A", "AAAA", "MX", "TXT", "CNAME"];

export const TOOL_SCHEMAS: Record<string, ToolParamSchema> = {
  isp_provision_site: {
    fields: {
      domain:      { type: "string", required: true, notEmpty: true },
      clientName:  { type: "string", required: true, notEmpty: true },
      clientEmail: { type: "string", required: true, notEmpty: true },
      serverIp:    { type: "string" },
      createMail:  { type: "boolean" },
      createDb:    { type: "boolean" },
      serverId:    { type: "number" },
    },
  },
  isp_client_get: {
    anyOf: [["client_id", "clientId"]],
  },
  isp_site_get: {
    anyOf: [["primary_id", "domain_id", "site_id"]],
  },
  isp_dns_record_list: {
    anyOf: [["zone_id", "zoneId"]],
  },
  isp_dns_record_add: {
    fields: {
      type: { type: "string", required: true, notEmpty: true, enum: DNS_TYPES },
    },
  },
  isp_dns_record_delete: {
    fields: {
      type: { type: "string", required: true, notEmpty: true, enum: DNS_TYPES },
    },
  },
  isp_quota_check: {
    anyOf: [["client_id", "clientId"]],
  },
};

// ---------------------------------------------------------------------------
// Validator
// ---------------------------------------------------------------------------

export function validateParams(toolName: string, params: JsonMap): void {
  const schema = TOOL_SCHEMAS[toolName];
  if (!schema) return;

  const errors: string[] = [];

  if (schema.fields) {
    for (const [key, rule] of Object.entries(schema.fields)) {
      const value = params[key];
      const present = value !== undefined && value !== null;

      if (rule.required && !present) {
        errors.push(`Missing required parameter: ${key}`);
        continue;
      }

      if (!present) continue;

      if (rule.notEmpty && String(value).trim() === "") {
        errors.push(`Parameter '${key}' must not be empty`);
      }

      if (rule.type === "number" && !Number.isFinite(Number(value))) {
        errors.push(`Parameter '${key}' must be a valid number, got: ${String(value)}`);
      }

      if (rule.enum) {
        const normalized = String(value).toUpperCase();
        if (!rule.enum.includes(normalized)) {
          errors.push(`Parameter '${key}' must be one of [${rule.enum.join(", ")}], got: ${String(value)}`);
        }
      }
    }
  }

  if (schema.anyOf) {
    for (const group of schema.anyOf) {
      const found = group.some((key) => params[key] !== undefined && params[key] !== null);
      if (!found) {
        errors.push(`One of [${group.join(", ")}] is required`);
      }
    }
  }

  if (errors.length > 0) {
    throw new ISPConfigError("validation_error",
      `Validation failed for ${toolName}: ${errors.join("; ")}`,
      { statusCode: 400 },
    );
  }
}
