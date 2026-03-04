import { PluginConfig } from "./types";

export const WRITE_TOOLS = new Set<string>([
  "ha_light_on",
  "ha_light_off",
  "ha_light_toggle",
  "ha_switch_on",
  "ha_switch_off",
  "ha_switch_toggle",
  "ha_climate_set_temp",
  "ha_climate_set_mode",
  "ha_climate_set_preset",
  "ha_media_play",
  "ha_media_pause",
  "ha_media_stop",
  "ha_media_volume",
  "ha_media_play_media",
  "ha_cover_open",
  "ha_cover_close",
  "ha_cover_position",
  "ha_scene_activate",
  "ha_script_run",
  "ha_automation_trigger",
  "ha_call_service",
  "ha_fire_event",
  "ha_notify"
]);

const ENTITY_ID_RE = /^[a-z0-9_]+\.[a-z0-9_]+$/;

export function assertToolAllowed(config: PluginConfig, toolName: string): void {
  if ((config.readOnly ?? false) && WRITE_TOOLS.has(toolName)) {
    throw new Error(`Tool ${toolName} is blocked because readOnly=true`);
  }
}

export function assertDomainAllowed(config: PluginConfig, domain: string): void {
  const allowed = config.allowedDomains?.map((d) => d.toLowerCase()) ?? [];
  if (allowed.length > 0 && !allowed.includes(domain.toLowerCase())) {
    throw new Error(`Domain ${domain} is blocked by allowedDomains policy`);
  }
}

export function parseEntityId(entityId: string): { domain: string; objectId: string } {
  const normalized = String(entityId ?? "").trim().toLowerCase();
  if (!ENTITY_ID_RE.test(normalized)) {
    throw new Error(`Invalid entity_id '${entityId}'. Expected format: {domain}.{object_id}`);
  }

  const [domain, objectId] = normalized.split(".");
  return { domain, objectId };
}

export function assertEntityAllowed(config: PluginConfig, entityId: string): { domain: string; objectId: string } {
  const parsed = parseEntityId(entityId);
  assertDomainAllowed(config, parsed.domain);
  return parsed;
}
