export interface PluginConfig {
  url: string;
  token: string;
  allowedDomains?: string[];
  readOnly?: boolean;
}

export interface HomeAssistantConfig {
  latitude: number;
  longitude: number;
  elevation: number;
  unit_system: Record<string, unknown>;
  location_name: string;
  time_zone: string;
  components: string[];
  version: string;
  [key: string]: unknown;
}

export interface HAEntityState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed?: string;
  last_updated?: string;
  context?: Record<string, unknown>;
}

export interface HAServiceField {
  name: string;
  description?: string;
  example?: unknown;
  required?: boolean;
  selector?: Record<string, unknown>;
}

export interface HAService {
  name: string;
  description?: string;
  target?: Record<string, unknown>;
  fields?: Record<string, HAServiceField>;
}

export interface HAServiceDomain {
  domain: string;
  services: Record<string, HAService>;
}

export interface ToolDeps {
  client: HAClientLike;
  config: PluginConfig;
}

export type JsonMap = Record<string, unknown>;

export interface OpenClawApi {
  config?: unknown;
  registerTool?: (name: string, handler: (input: unknown) => Promise<unknown>) => void;
  tool?: (name: string, handler: (input: unknown) => Promise<unknown>) => void;
}

export interface HAClientLike {
  getConfig(): Promise<HomeAssistantConfig>;
  getStates(): Promise<HAEntityState[]>;
  getState(entityId: string): Promise<HAEntityState>;
  getServices(): Promise<HAServiceDomain[]>;
  callService(domain: string, service: string, serviceData?: JsonMap): Promise<unknown>;
  getHistory(startTimestamp: string, entityId?: string, endTimestamp?: string): Promise<unknown>;
  getLogbook(startTimestamp: string, entityId?: string, endTimestamp?: string): Promise<unknown>;
  renderTemplate(template: string, variables?: JsonMap): Promise<unknown>;
  fireEvent(eventType: string, eventData?: JsonMap): Promise<unknown>;
  checkConnection(): Promise<boolean>;
}

export class HAClientError extends Error {
  public readonly statusCode: number;
  public readonly body: string;

  constructor(statusCode: number, body: string) {
    super(`Home Assistant HTTP ${statusCode}: ${body}`);
    this.name = "HAClientError";
    this.statusCode = statusCode;
    this.body = body;
  }
}

// ---------------------------------------------------------------------------
// Tool input types - exported for consumers who want typed tool calls
// ---------------------------------------------------------------------------

/** Tools with no input parameters. */
export type EmptyInput = Record<string, never>;

/** ha_list_entities */
export interface ListEntitiesInput {
  domain?: string;
  area?: string;
  state?: string;
}

/** ha_get_state */
export interface GetStateInput {
  entity_id: string;
}

/** ha_search_entities */
export interface SearchEntitiesInput {
  pattern: string;
}

/** ha_light_on */
export interface LightOnInput {
  entity_id: string;
  brightness?: number;
  color_temp?: number;
  rgb_color?: [number, number, number];
  transition?: number;
}

/** ha_light_off, ha_light_toggle, ha_switch_on/off/toggle, ha_media_play/pause/stop, ha_cover_open/close, ha_scene_activate */
export interface EntityIdInput {
  entity_id: string;
}

/** ha_climate_set_temp */
export interface ClimateSetTempInput {
  entity_id: string;
  temperature: number;
}

/** ha_climate_set_mode */
export interface ClimateSetModeInput {
  entity_id: string;
  hvac_mode: string;
}

/** ha_climate_set_preset */
export interface ClimateSetPresetInput {
  entity_id: string;
  preset_mode: string;
}

/** ha_media_volume */
export interface MediaVolumeInput {
  entity_id: string;
  volume_level: number;
}

/** ha_media_play_media */
export interface MediaPlayMediaInput {
  entity_id: string;
  content_id: string;
  content_type: string;
}

/** ha_cover_position */
export interface CoverPositionInput {
  entity_id: string;
  position: number;
}

/** ha_script_run */
export interface ScriptRunInput {
  entity_id: string;
  variables?: JsonMap;
}

/** ha_automation_trigger */
export interface AutomationTriggerInput {
  entity_id: string;
  skip_condition?: boolean;
}

/** ha_history, ha_logbook */
export interface HistoryInput {
  entity_id?: string;
  start?: string;
  end?: string;
}

/** ha_call_service */
export interface CallServiceInput {
  domain: string;
  service: string;
  service_data?: JsonMap;
}

/** ha_fire_event */
export interface FireEventInput {
  event_type: string;
  event_data?: JsonMap;
}

/** ha_render_template */
export interface RenderTemplateInput {
  template: string;
  variables?: JsonMap;
}

/** ha_notify */
export interface NotifyInput {
  target: string;
  message: string;
  title?: string;
  data?: JsonMap;
}

/** Complete map of tool name to input type. */
export interface ToolInputMap {
  ha_status: EmptyInput;
  ha_list_entities: ListEntitiesInput;
  ha_get_state: GetStateInput;
  ha_search_entities: SearchEntitiesInput;
  ha_list_services: EmptyInput;
  ha_light_on: LightOnInput;
  ha_light_off: EntityIdInput;
  ha_light_toggle: EntityIdInput;
  ha_light_list: EmptyInput;
  ha_switch_on: EntityIdInput;
  ha_switch_off: EntityIdInput;
  ha_switch_toggle: EntityIdInput;
  ha_climate_set_temp: ClimateSetTempInput;
  ha_climate_set_mode: ClimateSetModeInput;
  ha_climate_set_preset: ClimateSetPresetInput;
  ha_climate_list: EmptyInput;
  ha_media_play: EntityIdInput;
  ha_media_pause: EntityIdInput;
  ha_media_stop: EntityIdInput;
  ha_media_volume: MediaVolumeInput;
  ha_media_play_media: MediaPlayMediaInput;
  ha_cover_open: EntityIdInput;
  ha_cover_close: EntityIdInput;
  ha_cover_position: CoverPositionInput;
  ha_scene_activate: EntityIdInput;
  ha_script_run: ScriptRunInput;
  ha_automation_trigger: AutomationTriggerInput;
  ha_sensor_list: EmptyInput;
  ha_history: HistoryInput;
  ha_logbook: HistoryInput;
  ha_call_service: CallServiceInput;
  ha_fire_event: FireEventInput;
  ha_render_template: RenderTemplateInput;
  ha_notify: NotifyInput;
}

/** All tool names as a union type. */
export type ToolName = keyof ToolInputMap;
