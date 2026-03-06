import { assertDomainAllowed, assertEntityAllowed, assertToolAllowed, parseEntityId } from "../guards";
import { createTools } from "../tools";
import { HAClientLike, HAEntityState, HAServiceDomain, PluginConfig } from "../types";

function makeConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
  return {
    url: "http://ha.local:8123",
    token: "token",
    allowedDomains: [],
    readOnly: false,
    ...overrides
  };
}

function makeClient(overrides: Partial<HAClientLike> = {}): jest.Mocked<HAClientLike> {
  return {
    getConfig: jest.fn().mockResolvedValue({ version: "2026.2.0", location_name: "Home" }),
    getStates: jest.fn().mockResolvedValue([]),
    getState: jest.fn().mockResolvedValue({ entity_id: "light.kitchen", state: "on", attributes: {} }),
    getServices: jest.fn().mockResolvedValue([]),
    callService: jest.fn().mockResolvedValue({ ok: true }),
    getHistory: jest.fn().mockResolvedValue([]),
    getLogbook: jest.fn().mockResolvedValue([]),
    renderTemplate: jest.fn().mockResolvedValue("ok"),
    fireEvent: jest.fn().mockResolvedValue({ message: "Event fired." }),
    checkConnection: jest.fn().mockResolvedValue(true),
    ...overrides
  } as jest.Mocked<HAClientLike>;
}

const SAMPLE_STATES: HAEntityState[] = [
  { entity_id: "light.kitchen", state: "on", attributes: { friendly_name: "Kitchen Light", brightness: 255 } },
  { entity_id: "light.bedroom", state: "off", attributes: { friendly_name: "Bedroom Light", brightness: 0 } },
  { entity_id: "switch.fan", state: "on", attributes: { friendly_name: "Ceiling Fan" } },
  { entity_id: "sensor.temperature", state: "22.5", attributes: { friendly_name: "Temperature Sensor", unit_of_measurement: "C" } },
  { entity_id: "sensor.humidity", state: "45", attributes: { friendly_name: "Humidity", unit_of_measurement: "%" } },
  { entity_id: "climate.thermostat", state: "heat", attributes: { friendly_name: "Thermostat", temperature: 21 } },
  { entity_id: "media_player.living_room", state: "playing", attributes: { friendly_name: "Living Room Speaker" } },
  { entity_id: "cover.blinds", state: "open", attributes: { friendly_name: "Blinds", current_position: 100 } },
  { entity_id: "scene.movie_night", state: "scening", attributes: { friendly_name: "Movie Night" } },
  { entity_id: "script.morning_routine", state: "off", attributes: { friendly_name: "Morning Routine" } },
  { entity_id: "automation.lights_off", state: "on", attributes: { friendly_name: "Lights Off at Night" } },
  { entity_id: "binary_sensor.door", state: "off", attributes: { friendly_name: "Front Door", area_id: "entrance" } }
];

const SAMPLE_SERVICES: HAServiceDomain[] = [
  { domain: "light", services: { turn_on: { name: "Turn on" }, turn_off: { name: "Turn off" }, toggle: { name: "Toggle" } } },
  { domain: "switch", services: { turn_on: { name: "Turn on" }, turn_off: { name: "Turn off" } } },
  { domain: "climate", services: { set_temperature: { name: "Set temperature" } } },
  { domain: "media_player", services: { media_play: { name: "Play" }, media_pause: { name: "Pause" } } }
];

// ---------------------------------------------------------------------------
// Guards
// ---------------------------------------------------------------------------

describe("guards", () => {
  test("parseEntityId accepts valid format", () => {
    expect(parseEntityId("light.kitchen_main")).toEqual({ domain: "light", objectId: "kitchen_main" });
  });

  test("parseEntityId accepts simple entity_id", () => {
    expect(parseEntityId("sensor.temp")).toEqual({ domain: "sensor", objectId: "temp" });
  });

  test("parseEntityId normalizes to lowercase", () => {
    expect(parseEntityId("Light.Kitchen")).toEqual({ domain: "light", objectId: "kitchen" });
  });

  test("parseEntityId rejects invalid format", () => {
    expect(() => parseEntityId("invalid")).toThrow("Invalid entity_id");
  });

  test("parseEntityId rejects empty string", () => {
    expect(() => parseEntityId("")).toThrow("Invalid entity_id");
  });

  test("parseEntityId rejects triple-dotted format", () => {
    expect(() => parseEntityId("a.b.c")).toThrow("Invalid entity_id");
  });

  test("assertToolAllowed blocks write tools in readOnly", () => {
    expect(() => assertToolAllowed(makeConfig({ readOnly: true }), "ha_light_on")).toThrow("readOnly=true");
  });

  test("assertToolAllowed allows read tools in readOnly", () => {
    expect(() => assertToolAllowed(makeConfig({ readOnly: true }), "ha_get_state")).not.toThrow();
    expect(() => assertToolAllowed(makeConfig({ readOnly: true }), "ha_list_entities")).not.toThrow();
    expect(() => assertToolAllowed(makeConfig({ readOnly: true }), "ha_status")).not.toThrow();
  });

  test("assertToolAllowed allows write tools when readOnly=false", () => {
    expect(() => assertToolAllowed(makeConfig({ readOnly: false }), "ha_light_on")).not.toThrow();
    expect(() => assertToolAllowed(makeConfig({ readOnly: false }), "ha_call_service")).not.toThrow();
  });

  test("assertDomainAllowed respects allowedDomains", () => {
    expect(() => assertDomainAllowed(makeConfig({ allowedDomains: ["light"] }), "switch")).toThrow("blocked");
  });

  test("assertDomainAllowed passes when allowedDomains is empty", () => {
    expect(() => assertDomainAllowed(makeConfig({ allowedDomains: [] }), "switch")).not.toThrow();
  });

  test("assertDomainAllowed is case-insensitive", () => {
    expect(() => assertDomainAllowed(makeConfig({ allowedDomains: ["light"] }), "Light")).not.toThrow();
  });

  test("assertEntityAllowed checks domain allow-list", () => {
    expect(() => assertEntityAllowed(makeConfig({ allowedDomains: ["sensor"] }), "light.kitchen")).toThrow("blocked");
  });

  test("assertEntityAllowed passes for allowed domain", () => {
    expect(() => assertEntityAllowed(makeConfig({ allowedDomains: ["light"] }), "light.kitchen")).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// ha_status
// ---------------------------------------------------------------------------

describe("ha_status", () => {
  test("calls getConfig and returns result", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    const result = await tools.ha_status();
    expect(client.getConfig).toHaveBeenCalledTimes(1);
    expect(result).toEqual({ version: "2026.2.0", location_name: "Home" });
  });
});

// ---------------------------------------------------------------------------
// ha_list_entities
// ---------------------------------------------------------------------------

describe("ha_list_entities", () => {
  test("returns all entities when no filters given", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_list_entities();
    expect(out).toHaveLength(SAMPLE_STATES.length);
  });

  test("filters by domain", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_list_entities({ domain: "light" });
    expect(out).toHaveLength(2);
    expect(out.every((e: HAEntityState) => e.entity_id.startsWith("light."))).toBe(true);
  });

  test("filters by state", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_list_entities({ state: "on" });
    const onEntities = SAMPLE_STATES.filter(s => s.state === "on");
    expect(out).toHaveLength(onEntities.length);
  });

  test("filters by area", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_list_entities({ area: "entrance" });
    expect(out).toHaveLength(1);
    expect(out[0].entity_id).toBe("binary_sensor.door");
  });

  test("respects allowedDomains config", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light", "sensor"] }) });
    const out = await tools.ha_list_entities();
    expect(out.every((e: HAEntityState) => e.entity_id.startsWith("light.") || e.entity_id.startsWith("sensor."))).toBe(true);
  });

  test("rejects domain not in allowedDomains", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_list_entities({ domain: "switch" })).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_get_state
// ---------------------------------------------------------------------------

describe("ha_get_state", () => {
  test("returns entity state for valid entity_id", async () => {
    const entity = { entity_id: "light.kitchen", state: "on", attributes: { brightness: 255 } };
    const client = makeClient({ getState: jest.fn().mockResolvedValue(entity) });
    const tools = createTools({ client, config: makeConfig() });
    const result = await tools.ha_get_state({ entity_id: "light.kitchen" });
    expect(client.getState).toHaveBeenCalledWith("light.kitchen");
    expect(result).toEqual(entity);
  });

  test("rejects invalid entity_id format", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_get_state({ entity_id: "bad" })).rejects.toThrow("Invalid entity_id");
  });

  test("rejects missing entity_id", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_get_state({ entity_id: "" })).rejects.toThrow();
  });

  test("enforces allowedDomains", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["sensor"] }) });
    await expect(tools.ha_get_state({ entity_id: "light.kitchen" })).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_search_entities
// ---------------------------------------------------------------------------

describe("ha_search_entities", () => {
  test("matches by entity_id substring", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_search_entities({ pattern: "kitchen" });
    expect(out).toHaveLength(1);
    expect(out[0].entity_id).toBe("light.kitchen");
  });

  test("matches by friendly_name", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_search_entities({ pattern: "Ceiling" });
    expect(out).toHaveLength(1);
    expect(out[0].entity_id).toBe("switch.fan");
  });

  test("search is case-insensitive", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_search_entities({ pattern: "TEMPERATURE" });
    expect(out).toHaveLength(1);
    expect(out[0].entity_id).toBe("sensor.temperature");
  });

  test("returns empty for no matches", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_search_entities({ pattern: "nonexistent_xyz" });
    expect(out).toHaveLength(0);
  });

  test("rejects missing pattern", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_search_entities({ pattern: "" })).rejects.toThrow("required");
  });

  test("respects allowedDomains", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["sensor"] }) });
    const out = await tools.ha_search_entities({ pattern: "kitchen" });
    expect(out).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// ha_list_services
// ---------------------------------------------------------------------------

describe("ha_list_services", () => {
  test("returns all services when no allowedDomains", async () => {
    const client = makeClient({ getServices: jest.fn().mockResolvedValue(SAMPLE_SERVICES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_list_services();
    expect(out).toEqual(SAMPLE_SERVICES);
  });

  test("filters services by allowedDomains", async () => {
    const client = makeClient({ getServices: jest.fn().mockResolvedValue(SAMPLE_SERVICES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    const out = await tools.ha_list_services();
    expect(out).toHaveLength(1);
    expect(out[0].domain).toBe("light");
  });
});

// ---------------------------------------------------------------------------
// ha_light_on
// ---------------------------------------------------------------------------

describe("ha_light_on", () => {
  test("calls light.turn_on with entity_id", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen" });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", { entity_id: "light.kitchen" });
  });

  test("passes brightness", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen", brightness: 120 });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", expect.objectContaining({ brightness: 120 }));
  });

  test("passes color_temp", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen", color_temp: 350 });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", expect.objectContaining({ color_temp: 350 }));
  });

  test("passes rgb_color", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen", rgb_color: [255, 0, 0] });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", expect.objectContaining({ rgb_color: [255, 0, 0] }));
  });

  test("passes transition", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen", transition: 2 });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", expect.objectContaining({ transition: 2 }));
  });

  test("passes all optional parameters together", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_on({ entity_id: "light.kitchen", brightness: 200, color_temp: 300, transition: 1 });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", expect.objectContaining({
      entity_id: "light.kitchen",
      brightness: 200,
      color_temp: 300,
      transition: 1
    }));
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_light_on({ entity_id: "light.kitchen" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-light entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_light_on({ entity_id: "switch.fan" })).rejects.toThrow("light domain");
  });

  test("enforces allowedDomains", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["switch"] }) });
    await expect(tools.ha_light_on({ entity_id: "light.kitchen" })).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_light_off
// ---------------------------------------------------------------------------

describe("ha_light_off", () => {
  test("calls light.turn_off", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_off({ entity_id: "light.kitchen" });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_off", { entity_id: "light.kitchen" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_light_off({ entity_id: "light.kitchen" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-light entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_light_off({ entity_id: "switch.fan" })).rejects.toThrow("light domain");
  });
});

// ---------------------------------------------------------------------------
// ha_light_toggle
// ---------------------------------------------------------------------------

describe("ha_light_toggle", () => {
  test("calls light.toggle", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_light_toggle({ entity_id: "light.kitchen" });
    expect(client.callService).toHaveBeenCalledWith("light", "toggle", { entity_id: "light.kitchen" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_light_toggle({ entity_id: "light.kitchen" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-light entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_light_toggle({ entity_id: "switch.fan" })).rejects.toThrow("light domain");
  });
});

// ---------------------------------------------------------------------------
// ha_light_list
// ---------------------------------------------------------------------------

describe("ha_light_list", () => {
  test("returns only light entities with selected attributes", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_light_list();
    expect(out).toHaveLength(2);
    expect(out[0]).toEqual({
      entity_id: "light.kitchen",
      state: "on",
      friendly_name: "Kitchen Light",
      brightness: 255,
      color_temp: undefined,
      rgb_color: undefined
    });
  });

  test("respects allowedDomains", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["sensor"] }) });
    await expect(tools.ha_light_list()).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_switch_on / ha_switch_off / ha_switch_toggle
// ---------------------------------------------------------------------------

describe("ha_switch_on", () => {
  test("calls switch.turn_on", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_switch_on({ entity_id: "switch.fan" });
    expect(client.callService).toHaveBeenCalledWith("switch", "turn_on", { entity_id: "switch.fan" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_switch_on({ entity_id: "switch.fan" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-switch entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_switch_on({ entity_id: "light.kitchen" })).rejects.toThrow("switch domain");
  });
});

describe("ha_switch_off", () => {
  test("calls switch.turn_off", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_switch_off({ entity_id: "switch.fan" });
    expect(client.callService).toHaveBeenCalledWith("switch", "turn_off", { entity_id: "switch.fan" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_switch_off({ entity_id: "switch.fan" })).rejects.toThrow("readOnly=true");
  });
});

describe("ha_switch_toggle", () => {
  test("calls switch.toggle", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_switch_toggle({ entity_id: "switch.fan" });
    expect(client.callService).toHaveBeenCalledWith("switch", "toggle", { entity_id: "switch.fan" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_switch_toggle({ entity_id: "switch.fan" })).rejects.toThrow("readOnly=true");
  });
});

// ---------------------------------------------------------------------------
// ha_climate_set_temp / ha_climate_set_mode / ha_climate_set_preset / ha_climate_list
// ---------------------------------------------------------------------------

describe("ha_climate_set_temp", () => {
  test("calls climate.set_temperature", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_climate_set_temp({ entity_id: "climate.thermostat", temperature: 22 });
    expect(client.callService).toHaveBeenCalledWith("climate", "set_temperature", {
      entity_id: "climate.thermostat",
      temperature: 22
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_climate_set_temp({ entity_id: "climate.thermostat", temperature: 22 })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-climate entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_climate_set_temp({ entity_id: "light.kitchen", temperature: 22 })).rejects.toThrow("climate domain");
  });

  test("rejects non-numeric temperature", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_climate_set_temp({ entity_id: "climate.thermostat", temperature: "abc" as any })).rejects.toThrow("valid number");
  });
});

describe("ha_climate_set_mode", () => {
  test("calls climate.set_hvac_mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_climate_set_mode({ entity_id: "climate.thermostat", hvac_mode: "cool" });
    expect(client.callService).toHaveBeenCalledWith("climate", "set_hvac_mode", {
      entity_id: "climate.thermostat",
      hvac_mode: "cool"
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_climate_set_mode({ entity_id: "climate.thermostat", hvac_mode: "heat" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-climate entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_climate_set_mode({ entity_id: "light.kitchen", hvac_mode: "heat" })).rejects.toThrow("climate domain");
  });

  test("rejects empty hvac_mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_climate_set_mode({ entity_id: "climate.thermostat", hvac_mode: "" })).rejects.toThrow("required");
  });
});

describe("ha_climate_set_preset", () => {
  test("calls climate.set_preset_mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_climate_set_preset({ entity_id: "climate.thermostat", preset_mode: "away" });
    expect(client.callService).toHaveBeenCalledWith("climate", "set_preset_mode", {
      entity_id: "climate.thermostat",
      preset_mode: "away"
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_climate_set_preset({ entity_id: "climate.thermostat", preset_mode: "away" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-climate entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_climate_set_preset({ entity_id: "switch.fan", preset_mode: "away" })).rejects.toThrow("climate domain");
  });
});

describe("ha_climate_list", () => {
  test("returns only climate entities", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_climate_list();
    expect(out).toHaveLength(1);
    expect(out[0].entity_id).toBe("climate.thermostat");
  });

  test("respects allowedDomains", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_climate_list()).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_media_play / ha_media_pause / ha_media_stop / ha_media_volume / ha_media_play_media
// ---------------------------------------------------------------------------

describe("ha_media_play", () => {
  test("calls media_player.media_play", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_play({ entity_id: "media_player.living_room" });
    expect(client.callService).toHaveBeenCalledWith("media_player", "media_play", { entity_id: "media_player.living_room" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_media_play({ entity_id: "media_player.living_room" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-media_player entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_play({ entity_id: "light.kitchen" })).rejects.toThrow("media_player domain");
  });
});

describe("ha_media_pause", () => {
  test("calls media_player.media_pause", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_pause({ entity_id: "media_player.living_room" });
    expect(client.callService).toHaveBeenCalledWith("media_player", "media_pause", { entity_id: "media_player.living_room" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_media_pause({ entity_id: "media_player.living_room" })).rejects.toThrow("readOnly=true");
  });
});

describe("ha_media_stop", () => {
  test("calls media_player.media_stop", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_stop({ entity_id: "media_player.living_room" });
    expect(client.callService).toHaveBeenCalledWith("media_player", "media_stop", { entity_id: "media_player.living_room" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_media_stop({ entity_id: "media_player.living_room" })).rejects.toThrow("readOnly=true");
  });
});

describe("ha_media_volume", () => {
  test("calls media_player.volume_set with valid level", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: 0.5 });
    expect(client.callService).toHaveBeenCalledWith("media_player", "volume_set", {
      entity_id: "media_player.living_room",
      volume_level: 0.5
    });
  });

  test("accepts volume_level 0.0 (mute)", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: 0 });
    expect(client.callService).toHaveBeenCalledWith("media_player", "volume_set", expect.objectContaining({ volume_level: 0 }));
  });

  test("accepts volume_level 1.0 (max)", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: 1.0 });
    expect(client.callService).toHaveBeenCalledWith("media_player", "volume_set", expect.objectContaining({ volume_level: 1.0 }));
  });

  test("rejects volume above 1.0", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: 1.2 })).rejects.toThrow("between 0.0 and 1.0");
  });

  test("rejects negative volume", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: -0.1 })).rejects.toThrow("between 0.0 and 1.0");
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_media_volume({ entity_id: "media_player.living_room", volume_level: 0.5 })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-media_player entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_volume({ entity_id: "light.kitchen", volume_level: 0.5 })).rejects.toThrow("media_player domain");
  });
});

describe("ha_media_play_media", () => {
  test("calls media_player.play_media with content details", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_media_play_media({
      entity_id: "media_player.living_room",
      content_id: "spotify:track:abc123",
      content_type: "music"
    });
    expect(client.callService).toHaveBeenCalledWith("media_player", "play_media", {
      entity_id: "media_player.living_room",
      media_content_id: "spotify:track:abc123",
      media_content_type: "music"
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_media_play_media({
      entity_id: "media_player.living_room",
      content_id: "test",
      content_type: "music"
    })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-media_player entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_play_media({
      entity_id: "light.kitchen",
      content_id: "test",
      content_type: "music"
    })).rejects.toThrow("media_player domain");
  });

  test("rejects empty content_id", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_play_media({
      entity_id: "media_player.living_room",
      content_id: "",
      content_type: "music"
    })).rejects.toThrow("required");
  });

  test("rejects empty content_type", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_media_play_media({
      entity_id: "media_player.living_room",
      content_id: "test",
      content_type: ""
    })).rejects.toThrow("required");
  });
});

// ---------------------------------------------------------------------------
// ha_cover_open / ha_cover_close / ha_cover_position
// ---------------------------------------------------------------------------

describe("ha_cover_open", () => {
  test("calls cover.open_cover", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_cover_open({ entity_id: "cover.blinds" });
    expect(client.callService).toHaveBeenCalledWith("cover", "open_cover", { entity_id: "cover.blinds" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_cover_open({ entity_id: "cover.blinds" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-cover entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_cover_open({ entity_id: "light.kitchen" })).rejects.toThrow("cover domain");
  });
});

describe("ha_cover_close", () => {
  test("calls cover.close_cover", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_cover_close({ entity_id: "cover.blinds" });
    expect(client.callService).toHaveBeenCalledWith("cover", "close_cover", { entity_id: "cover.blinds" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_cover_close({ entity_id: "cover.blinds" })).rejects.toThrow("readOnly=true");
  });
});

describe("ha_cover_position", () => {
  test("calls cover.set_cover_position with valid position", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_cover_position({ entity_id: "cover.blinds", position: 50 });
    expect(client.callService).toHaveBeenCalledWith("cover", "set_cover_position", {
      entity_id: "cover.blinds",
      position: 50
    });
  });

  test("accepts position 0 (fully closed)", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_cover_position({ entity_id: "cover.blinds", position: 0 });
    expect(client.callService).toHaveBeenCalledWith("cover", "set_cover_position", expect.objectContaining({ position: 0 }));
  });

  test("accepts position 100 (fully open)", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_cover_position({ entity_id: "cover.blinds", position: 100 });
    expect(client.callService).toHaveBeenCalledWith("cover", "set_cover_position", expect.objectContaining({ position: 100 }));
  });

  test("rejects position above 100", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_cover_position({ entity_id: "cover.blinds", position: 120 })).rejects.toThrow("between 0 and 100");
  });

  test("rejects negative position", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_cover_position({ entity_id: "cover.blinds", position: -5 })).rejects.toThrow("between 0 and 100");
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_cover_position({ entity_id: "cover.blinds", position: 50 })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-cover entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_cover_position({ entity_id: "light.kitchen", position: 50 })).rejects.toThrow("cover domain");
  });
});

// ---------------------------------------------------------------------------
// ha_scene_activate
// ---------------------------------------------------------------------------

describe("ha_scene_activate", () => {
  test("calls scene.turn_on", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_scene_activate({ entity_id: "scene.movie_night" });
    expect(client.callService).toHaveBeenCalledWith("scene", "turn_on", { entity_id: "scene.movie_night" });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_scene_activate({ entity_id: "scene.movie_night" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-scene entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_scene_activate({ entity_id: "light.kitchen" })).rejects.toThrow("scene domain");
  });
});

// ---------------------------------------------------------------------------
// ha_script_run
// ---------------------------------------------------------------------------

describe("ha_script_run", () => {
  test("calls script.turn_on with empty variables by default", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_script_run({ entity_id: "script.morning_routine" });
    expect(client.callService).toHaveBeenCalledWith("script", "turn_on", {
      entity_id: "script.morning_routine",
      variables: {}
    });
  });

  test("passes variables when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_script_run({ entity_id: "script.morning_routine", variables: { brightness: 100 } });
    expect(client.callService).toHaveBeenCalledWith("script", "turn_on", {
      entity_id: "script.morning_routine",
      variables: { brightness: 100 }
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_script_run({ entity_id: "script.morning_routine" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-script entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_script_run({ entity_id: "light.kitchen" })).rejects.toThrow("script domain");
  });
});

// ---------------------------------------------------------------------------
// ha_automation_trigger
// ---------------------------------------------------------------------------

describe("ha_automation_trigger", () => {
  test("calls automation.trigger", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_automation_trigger({ entity_id: "automation.lights_off" });
    expect(client.callService).toHaveBeenCalledWith("automation", "trigger", {
      entity_id: "automation.lights_off"
    });
  });

  test("passes skip_condition when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_automation_trigger({ entity_id: "automation.lights_off", skip_condition: true });
    expect(client.callService).toHaveBeenCalledWith("automation", "trigger", {
      entity_id: "automation.lights_off",
      skip_condition: true
    });
  });

  test("does not include skip_condition when undefined", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_automation_trigger({ entity_id: "automation.lights_off" });
    const callArgs = client.callService.mock.calls[0][2] as Record<string, unknown>;
    expect(callArgs).not.toHaveProperty("skip_condition");
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_automation_trigger({ entity_id: "automation.lights_off" })).rejects.toThrow("readOnly=true");
  });

  test("rejects non-automation entity", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_automation_trigger({ entity_id: "light.kitchen" })).rejects.toThrow("automation domain");
  });
});

// ---------------------------------------------------------------------------
// ha_sensor_list
// ---------------------------------------------------------------------------

describe("ha_sensor_list", () => {
  test("returns only sensor entities", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig() });
    const out = await tools.ha_sensor_list();
    expect(out).toHaveLength(2);
    expect(out.every((s: HAEntityState) => s.entity_id.startsWith("sensor."))).toBe(true);
  });

  test("respects allowedDomains", async () => {
    const client = makeClient({ getStates: jest.fn().mockResolvedValue(SAMPLE_STATES) });
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_sensor_list()).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_history
// ---------------------------------------------------------------------------

describe("ha_history", () => {
  test("calls getHistory with default start time when none provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_history();
    expect(client.getHistory).toHaveBeenCalledWith(expect.any(String), undefined, undefined);
  });

  test("passes entity_id when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_history({ entity_id: "sensor.temperature" });
    expect(client.getHistory).toHaveBeenCalledWith(expect.any(String), "sensor.temperature", undefined);
  });

  test("passes custom start and end times", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_history({ start: "2026-02-26T00:00:00Z", end: "2026-02-27T00:00:00Z" });
    expect(client.getHistory).toHaveBeenCalledWith("2026-02-26T00:00:00Z", undefined, "2026-02-27T00:00:00Z");
  });

  test("passes all params when all provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_history({ entity_id: "sensor.temperature", start: "2026-02-26T00:00:00Z", end: "2026-02-27T00:00:00Z" });
    expect(client.getHistory).toHaveBeenCalledWith("2026-02-26T00:00:00Z", "sensor.temperature", "2026-02-27T00:00:00Z");
  });

  test("enforces allowedDomains on entity_id", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_history({ entity_id: "sensor.temperature" })).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_logbook
// ---------------------------------------------------------------------------

describe("ha_logbook", () => {
  test("calls getLogbook with default start time when none provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_logbook();
    expect(client.getLogbook).toHaveBeenCalledWith(expect.any(String), undefined, undefined);
  });

  test("passes entity_id when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_logbook({ entity_id: "light.kitchen" });
    expect(client.getLogbook).toHaveBeenCalledWith(expect.any(String), "light.kitchen", undefined);
  });

  test("passes custom start and end times", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_logbook({ start: "2026-02-26T00:00:00Z", end: "2026-02-27T00:00:00Z" });
    expect(client.getLogbook).toHaveBeenCalledWith("2026-02-26T00:00:00Z", undefined, "2026-02-27T00:00:00Z");
  });

  test("enforces allowedDomains on entity_id", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["sensor"] }) });
    await expect(tools.ha_logbook({ entity_id: "light.kitchen" })).rejects.toThrow("blocked");
  });
});

// ---------------------------------------------------------------------------
// ha_call_service
// ---------------------------------------------------------------------------

describe("ha_call_service", () => {
  test("executes generic service call", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_call_service({ domain: "light", service: "turn_on", service_data: { entity_id: "light.kitchen" } });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", { entity_id: "light.kitchen" });
  });

  test("defaults service_data to empty object", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_call_service({ domain: "homeassistant", service: "restart" });
    expect(client.callService).toHaveBeenCalledWith("homeassistant", "restart", {});
  });

  test("normalizes domain to lowercase", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_call_service({ domain: "Light", service: "turn_on" });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", {});
  });

  test("normalizes service to lowercase", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_call_service({ domain: "light", service: "Turn_On" });
    expect(client.callService).toHaveBeenCalledWith("light", "turn_on", {});
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_call_service({ domain: "light", service: "turn_on" })).rejects.toThrow("readOnly=true");
  });

  test("enforces allowedDomains", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_call_service({ domain: "switch", service: "turn_on" })).rejects.toThrow("blocked");
  });

  test("rejects empty domain", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_call_service({ domain: "", service: "turn_on" })).rejects.toThrow("required");
  });

  test("rejects empty service", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_call_service({ domain: "light", service: "" })).rejects.toThrow("required");
  });
});

// ---------------------------------------------------------------------------
// ha_fire_event
// ---------------------------------------------------------------------------

describe("ha_fire_event", () => {
  test("calls fireEvent with event type and data", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_fire_event({ event_type: "custom_event", event_data: { key: "value" } });
    expect(client.fireEvent).toHaveBeenCalledWith("custom_event", { key: "value" });
  });

  test("defaults event_data to empty object", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_fire_event({ event_type: "my_event" });
    expect(client.fireEvent).toHaveBeenCalledWith("my_event", {});
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_fire_event({ event_type: "my_event" })).rejects.toThrow("readOnly=true");
  });

  test("rejects empty event_type", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_fire_event({ event_type: "" })).rejects.toThrow("required");
  });
});

// ---------------------------------------------------------------------------
// ha_render_template
// ---------------------------------------------------------------------------

describe("ha_render_template", () => {
  test("calls renderTemplate with template string", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_render_template({ template: "{{ 1 + 1 }}" });
    expect(client.renderTemplate).toHaveBeenCalledWith("{{ 1 + 1 }}", {});
  });

  test("passes variables when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_render_template({ template: "{{ greeting }}", variables: { greeting: "hello" } });
    expect(client.renderTemplate).toHaveBeenCalledWith("{{ greeting }}", { greeting: "hello" });
  });

  test("rejects empty template", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_render_template({ template: "" })).rejects.toThrow("required");
  });

  test("not blocked in readOnly mode (read-only operation)", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await tools.ha_render_template({ template: "{{ states('sensor.temp') }}" });
    expect(client.renderTemplate).toHaveBeenCalledTimes(1);
  });
});

// ---------------------------------------------------------------------------
// ha_notify
// ---------------------------------------------------------------------------

describe("ha_notify", () => {
  test("calls notify service with target and message", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_notify({ target: "mobile_app_phone", message: "hello" });
    expect(client.callService).toHaveBeenCalledWith("notify", "mobile_app_phone", { message: "hello" });
  });

  test("includes title when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_notify({ target: "mobile_app_phone", message: "hello", title: "Alert" });
    expect(client.callService).toHaveBeenCalledWith("notify", "mobile_app_phone", { message: "hello", title: "Alert" });
  });

  test("includes data when provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_notify({ target: "mobile_app_phone", message: "hello", data: { tag: "test" } });
    expect(client.callService).toHaveBeenCalledWith("notify", "mobile_app_phone", { message: "hello", data: { tag: "test" } });
  });

  test("includes title and data when both provided", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await tools.ha_notify({ target: "mobile_app_phone", message: "hello", title: "Alert", data: { tag: "test" } });
    expect(client.callService).toHaveBeenCalledWith("notify", "mobile_app_phone", {
      message: "hello",
      title: "Alert",
      data: { tag: "test" }
    });
  });

  test("blocked in readOnly mode", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(tools.ha_notify({ target: "mobile_app_phone", message: "hello" })).rejects.toThrow("readOnly=true");
  });

  test("enforces allowedDomains for notify", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ allowedDomains: ["light"] }) });
    await expect(tools.ha_notify({ target: "mobile_app_phone", message: "hello" })).rejects.toThrow("blocked");
  });

  test("rejects empty target", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_notify({ target: "", message: "hello" })).rejects.toThrow("required");
  });

  test("rejects empty message", async () => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig() });
    await expect(tools.ha_notify({ target: "mobile_app_phone", message: "" })).rejects.toThrow("required");
  });
});

// ---------------------------------------------------------------------------
// Cross-cutting: readOnly blocks all write tools
// ---------------------------------------------------------------------------

describe("readOnly guards all write tools", () => {
  const writeToolCalls: Array<{ name: string; call: (tools: ReturnType<typeof createTools>) => Promise<unknown> }> = [
    { name: "ha_light_on", call: (t) => t.ha_light_on({ entity_id: "light.x" }) },
    { name: "ha_light_off", call: (t) => t.ha_light_off({ entity_id: "light.x" }) },
    { name: "ha_light_toggle", call: (t) => t.ha_light_toggle({ entity_id: "light.x" }) },
    { name: "ha_switch_on", call: (t) => t.ha_switch_on({ entity_id: "switch.x" }) },
    { name: "ha_switch_off", call: (t) => t.ha_switch_off({ entity_id: "switch.x" }) },
    { name: "ha_switch_toggle", call: (t) => t.ha_switch_toggle({ entity_id: "switch.x" }) },
    { name: "ha_climate_set_temp", call: (t) => t.ha_climate_set_temp({ entity_id: "climate.x", temperature: 20 }) },
    { name: "ha_climate_set_mode", call: (t) => t.ha_climate_set_mode({ entity_id: "climate.x", hvac_mode: "heat" }) },
    { name: "ha_climate_set_preset", call: (t) => t.ha_climate_set_preset({ entity_id: "climate.x", preset_mode: "away" }) },
    { name: "ha_media_play", call: (t) => t.ha_media_play({ entity_id: "media_player.x" }) },
    { name: "ha_media_pause", call: (t) => t.ha_media_pause({ entity_id: "media_player.x" }) },
    { name: "ha_media_stop", call: (t) => t.ha_media_stop({ entity_id: "media_player.x" }) },
    { name: "ha_media_volume", call: (t) => t.ha_media_volume({ entity_id: "media_player.x", volume_level: 0.5 }) },
    { name: "ha_media_play_media", call: (t) => t.ha_media_play_media({ entity_id: "media_player.x", content_id: "a", content_type: "b" }) },
    { name: "ha_cover_open", call: (t) => t.ha_cover_open({ entity_id: "cover.x" }) },
    { name: "ha_cover_close", call: (t) => t.ha_cover_close({ entity_id: "cover.x" }) },
    { name: "ha_cover_position", call: (t) => t.ha_cover_position({ entity_id: "cover.x", position: 50 }) },
    { name: "ha_scene_activate", call: (t) => t.ha_scene_activate({ entity_id: "scene.x" }) },
    { name: "ha_script_run", call: (t) => t.ha_script_run({ entity_id: "script.x" }) },
    { name: "ha_automation_trigger", call: (t) => t.ha_automation_trigger({ entity_id: "automation.x" }) },
    { name: "ha_call_service", call: (t) => t.ha_call_service({ domain: "light", service: "turn_on" }) },
    { name: "ha_fire_event", call: (t) => t.ha_fire_event({ event_type: "test" }) },
    { name: "ha_notify", call: (t) => t.ha_notify({ target: "t", message: "m" }) }
  ];

  test.each(writeToolCalls)("$name is blocked in readOnly", async ({ call }) => {
    const client = makeClient();
    const tools = createTools({ client, config: makeConfig({ readOnly: true }) });
    await expect(call(tools)).rejects.toThrow("readOnly=true");
  });
});
