import { PluginConfig } from "./types";

const HA_DOMAINS = [
  "alarm_control_panel", "automation", "binary_sensor", "button",
  "calendar", "camera", "climate", "cover", "device_tracker",
  "fan", "group", "humidifier", "input_boolean", "input_button",
  "input_datetime", "input_number", "input_select", "input_text",
  "light", "lock", "media_player", "notify", "number", "person",
  "remote", "scene", "script", "select", "sensor", "siren",
  "switch", "timer", "update", "vacuum", "water_heater", "weather", "zone"
] as const;

export type HADomain = typeof HA_DOMAINS[number];

export interface ConfigValidationError {
  field: string;
  message: string;
}

/**
 * Validates and normalizes a raw config object into a PluginConfig.
 * Throws with a descriptive message if validation fails.
 */
export function validateConfig(raw: unknown): PluginConfig {
  if (raw === null || raw === undefined || typeof raw !== "object") {
    throw new Error("Config must be a non-null object");
  }

  const errors: ConfigValidationError[] = [];
  const obj = raw as Record<string, unknown>;

  // url: required, must be http or https URL
  const url = validateUrl(obj.url, errors);

  // token: required, non-empty string
  const token = validateToken(obj.token, errors);

  // allowedDomains: optional array of non-empty strings
  const allowedDomains = validateAllowedDomains(obj.allowedDomains, errors);

  // readOnly: optional boolean
  const readOnly = validateReadOnly(obj.readOnly, errors);

  if (errors.length > 0) {
    const details = errors.map((e) => `  - ${e.field}: ${e.message}`).join("\n");
    throw new Error(`Invalid plugin config:\n${details}`);
  }

  return { url: url!, token: token!, allowedDomains, readOnly };
}

function validateUrl(value: unknown, errors: ConfigValidationError[]): string | undefined {
  if (value === undefined || value === null || value === "") {
    errors.push({ field: "url", message: "required" });
    return undefined;
  }
  if (typeof value !== "string") {
    errors.push({ field: "url", message: "must be a string" });
    return undefined;
  }
  const trimmed = value.trim().replace(/\/+$/, "");
  if (!/^https?:\/\/.+/i.test(trimmed)) {
    errors.push({ field: "url", message: "must be an http:// or https:// URL" });
    return undefined;
  }
  return trimmed;
}

function validateToken(value: unknown, errors: ConfigValidationError[]): string | undefined {
  if (value === undefined || value === null || value === "") {
    errors.push({ field: "token", message: "required" });
    return undefined;
  }
  if (typeof value !== "string") {
    errors.push({ field: "token", message: "must be a string" });
    return undefined;
  }
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    errors.push({ field: "token", message: "must be non-empty" });
    return undefined;
  }
  return trimmed;
}

function validateAllowedDomains(value: unknown, errors: ConfigValidationError[]): string[] {
  if (value === undefined || value === null) {
    return [];
  }
  if (!Array.isArray(value)) {
    errors.push({ field: "allowedDomains", message: "must be an array of strings" });
    return [];
  }
  for (let i = 0; i < value.length; i++) {
    if (typeof value[i] !== "string" || (value[i] as string).trim().length === 0) {
      errors.push({ field: `allowedDomains[${i}]`, message: "must be a non-empty string" });
    }
  }
  return value.filter((v) => typeof v === "string" && v.trim().length > 0).map((v) => (v as string).trim().toLowerCase());
}

function validateReadOnly(value: unknown, errors: ConfigValidationError[]): boolean {
  if (value === undefined || value === null) {
    return false;
  }
  if (typeof value !== "boolean") {
    errors.push({ field: "readOnly", message: "must be a boolean" });
    return false;
  }
  return value;
}

/** Known Home Assistant domains for reference. Not used for enforcement. */
export const KNOWN_HA_DOMAINS: readonly string[] = Object.freeze([...HA_DOMAINS]);
