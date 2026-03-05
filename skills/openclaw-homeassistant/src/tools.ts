import { assertDomainAllowed, assertEntityAllowed, assertToolAllowed } from "./guards";
import { HAEntityState, JsonMap, PluginConfig, ToolDeps } from "./types";

function nowIsoMinusHours(hours: number): string {
  return new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
}

function requiredString(value: unknown, name: string): string {
  const v = String(value ?? "").trim();
  if (!v) {
    throw new Error(`${name} is required`);
  }
  return v;
}

function toNumber(value: unknown, name: string): number {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    throw new Error(`${name} must be a valid number`);
  }
  return n;
}

function filteredEntities(states: HAEntityState[], config: PluginConfig): HAEntityState[] {
  const allowed = config.allowedDomains?.map((d) => d.toLowerCase()) ?? [];
  if (allowed.length === 0) {
    return states;
  }

  return states.filter((s) => {
    const domain = s.entity_id.split(".")[0]?.toLowerCase();
    return domain ? allowed.includes(domain) : false;
  });
}

function entityData(entityId: string): JsonMap {
  const parsed = assertEntityAllowed({ url: "", token: "" }, entityId);
  return { entity_id: `${parsed.domain}.${parsed.objectId}` };
}

export function createTools({ client, config }: ToolDeps) {
  return {
    ha_status: async () => client.getConfig(),

    ha_list_entities: async (input?: { domain?: string; area?: string; state?: string }) => {
      const states = filteredEntities(await client.getStates(), config);
      if (input?.domain) {
        const domain = input.domain.trim().toLowerCase();
        assertDomainAllowed(config, domain);
        return states.filter((s) => s.entity_id.startsWith(`${domain}.`));
      }

      return states.filter((s) => {
        if (input?.state && s.state !== input.state) return false;
        if (input?.area) {
          const areaId = String(s.attributes?.area_id ?? "");
          if (areaId !== input.area) return false;
        }
        return true;
      });
    },

    ha_get_state: async (input: { entity_id: string }) => {
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      assertDomainAllowed(config, domain);
      return client.getState(input.entity_id);
    },

    ha_search_entities: async (input: { pattern: string }) => {
      const pattern = requiredString(input?.pattern, "pattern").toLowerCase();
      const states = filteredEntities(await client.getStates(), config);
      return states.filter((s) => {
        const name = String(s.attributes?.friendly_name ?? "").toLowerCase();
        return s.entity_id.toLowerCase().includes(pattern) || name.includes(pattern);
      });
    },

    ha_list_services: async () => {
      const services = await client.getServices();
      const allowed = config.allowedDomains?.map((d) => d.toLowerCase()) ?? [];
      if (allowed.length === 0) return services;
      return services.filter((s) => allowed.includes(s.domain.toLowerCase()));
    },

    ha_light_on: async (input: { entity_id: string; brightness?: number; color_temp?: number; rgb_color?: [number, number, number]; transition?: number }) => {
      assertToolAllowed(config, "ha_light_on");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "light") throw new Error("entity_id must be in light domain");
      return client.callService("light", "turn_on", {
        ...entityData(input.entity_id),
        ...(input.brightness !== undefined ? { brightness: toNumber(input.brightness, "brightness") } : {}),
        ...(input.color_temp !== undefined ? { color_temp: toNumber(input.color_temp, "color_temp") } : {}),
        ...(input.rgb_color !== undefined ? { rgb_color: input.rgb_color } : {}),
        ...(input.transition !== undefined ? { transition: toNumber(input.transition, "transition") } : {})
      });
    },

    ha_light_off: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_light_off");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "light") throw new Error("entity_id must be in light domain");
      return client.callService("light", "turn_off", entityData(input.entity_id));
    },

    ha_light_toggle: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_light_toggle");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "light") throw new Error("entity_id must be in light domain");
      return client.callService("light", "toggle", entityData(input.entity_id));
    },

    ha_light_list: async () => {
      assertDomainAllowed(config, "light");
      const states = await client.getStates();
      return states
        .filter((s) => s.entity_id.startsWith("light."))
        .map((s) => ({
          entity_id: s.entity_id,
          state: s.state,
          friendly_name: s.attributes?.friendly_name,
          brightness: s.attributes?.brightness,
          color_temp: s.attributes?.color_temp,
          rgb_color: s.attributes?.rgb_color
        }));
    },

    ha_switch_on: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_switch_on");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "switch") throw new Error("entity_id must be in switch domain");
      return client.callService("switch", "turn_on", entityData(input.entity_id));
    },
    ha_switch_off: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_switch_off");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "switch") throw new Error("entity_id must be in switch domain");
      return client.callService("switch", "turn_off", entityData(input.entity_id));
    },
    ha_switch_toggle: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_switch_toggle");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "switch") throw new Error("entity_id must be in switch domain");
      return client.callService("switch", "toggle", entityData(input.entity_id));
    },

    ha_climate_set_temp: async (input: { entity_id: string; temperature: number }) => {
      assertToolAllowed(config, "ha_climate_set_temp");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "climate") throw new Error("entity_id must be in climate domain");
      return client.callService("climate", "set_temperature", { ...entityData(input.entity_id), temperature: toNumber(input.temperature, "temperature") });
    },
    ha_climate_set_mode: async (input: { entity_id: string; hvac_mode: string }) => {
      assertToolAllowed(config, "ha_climate_set_mode");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "climate") throw new Error("entity_id must be in climate domain");
      return client.callService("climate", "set_hvac_mode", { ...entityData(input.entity_id), hvac_mode: requiredString(input.hvac_mode, "hvac_mode") });
    },
    ha_climate_set_preset: async (input: { entity_id: string; preset_mode: string }) => {
      assertToolAllowed(config, "ha_climate_set_preset");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "climate") throw new Error("entity_id must be in climate domain");
      return client.callService("climate", "set_preset_mode", { ...entityData(input.entity_id), preset_mode: requiredString(input.preset_mode, "preset_mode") });
    },
    ha_climate_list: async () => {
      assertDomainAllowed(config, "climate");
      return (await client.getStates()).filter((s) => s.entity_id.startsWith("climate."));
    },

    ha_media_play: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_media_play");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "media_player") throw new Error("entity_id must be in media_player domain");
      return client.callService("media_player", "media_play", entityData(input.entity_id));
    },
    ha_media_pause: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_media_pause");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "media_player") throw new Error("entity_id must be in media_player domain");
      return client.callService("media_player", "media_pause", entityData(input.entity_id));
    },
    ha_media_stop: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_media_stop");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "media_player") throw new Error("entity_id must be in media_player domain");
      return client.callService("media_player", "media_stop", entityData(input.entity_id));
    },
    ha_media_volume: async (input: { entity_id: string; volume_level: number }) => {
      assertToolAllowed(config, "ha_media_volume");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "media_player") throw new Error("entity_id must be in media_player domain");
      const volume = toNumber(input.volume_level, "volume_level");
      if (volume < 0 || volume > 1) throw new Error("volume_level must be between 0.0 and 1.0");
      return client.callService("media_player", "volume_set", { ...entityData(input.entity_id), volume_level: volume });
    },
    ha_media_play_media: async (input: { entity_id: string; content_id: string; content_type: string }) => {
      assertToolAllowed(config, "ha_media_play_media");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "media_player") throw new Error("entity_id must be in media_player domain");
      return client.callService("media_player", "play_media", {
        ...entityData(input.entity_id),
        media_content_id: requiredString(input.content_id, "content_id"),
        media_content_type: requiredString(input.content_type, "content_type")
      });
    },

    ha_cover_open: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_cover_open");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "cover") throw new Error("entity_id must be in cover domain");
      return client.callService("cover", "open_cover", entityData(input.entity_id));
    },
    ha_cover_close: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_cover_close");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "cover") throw new Error("entity_id must be in cover domain");
      return client.callService("cover", "close_cover", entityData(input.entity_id));
    },
    ha_cover_position: async (input: { entity_id: string; position: number }) => {
      assertToolAllowed(config, "ha_cover_position");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "cover") throw new Error("entity_id must be in cover domain");
      const position = toNumber(input.position, "position");
      if (position < 0 || position > 100) throw new Error("position must be between 0 and 100");
      return client.callService("cover", "set_cover_position", { ...entityData(input.entity_id), position });
    },

    ha_scene_activate: async (input: { entity_id: string }) => {
      assertToolAllowed(config, "ha_scene_activate");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "scene") throw new Error("entity_id must be in scene domain");
      return client.callService("scene", "turn_on", entityData(input.entity_id));
    },
    ha_script_run: async (input: { entity_id: string; variables?: JsonMap }) => {
      assertToolAllowed(config, "ha_script_run");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "script") throw new Error("entity_id must be in script domain");
      return client.callService("script", "turn_on", { ...entityData(input.entity_id), variables: input.variables ?? {} });
    },
    ha_automation_trigger: async (input: { entity_id: string; skip_condition?: boolean }) => {
      assertToolAllowed(config, "ha_automation_trigger");
      const { domain } = assertEntityAllowed(config, requiredString(input?.entity_id, "entity_id"));
      if (domain !== "automation") throw new Error("entity_id must be in automation domain");
      return client.callService("automation", "trigger", {
        ...entityData(input.entity_id),
        ...(input.skip_condition !== undefined ? { skip_condition: Boolean(input.skip_condition) } : {})
      });
    },

    ha_sensor_list: async () => {
      assertDomainAllowed(config, "sensor");
      return (await client.getStates()).filter((s) => s.entity_id.startsWith("sensor."));
    },
    ha_history: async (input?: { entity_id?: string; start?: string; end?: string }) => {
      const start = input?.start ?? nowIsoMinusHours(24);
      if (input?.entity_id) {
        assertEntityAllowed(config, input.entity_id);
      }
      return client.getHistory(start, input?.entity_id, input?.end);
    },
    ha_logbook: async (input?: { entity_id?: string; start?: string; end?: string }) => {
      const start = input?.start ?? nowIsoMinusHours(24);
      if (input?.entity_id) {
        assertEntityAllowed(config, input.entity_id);
      }
      return client.getLogbook(start, input?.entity_id, input?.end);
    },

    ha_call_service: async (input: { domain: string; service: string; service_data?: JsonMap }) => {
      assertToolAllowed(config, "ha_call_service");
      const domain = requiredString(input?.domain, "domain").toLowerCase();
      assertDomainAllowed(config, domain);
      const service = requiredString(input?.service, "service").toLowerCase();
      return client.callService(domain, service, input?.service_data ?? {});
    },
    ha_fire_event: async (input: { event_type: string; event_data?: JsonMap }) => {
      assertToolAllowed(config, "ha_fire_event");
      return client.fireEvent(requiredString(input?.event_type, "event_type"), input?.event_data ?? {});
    },
    ha_render_template: async (input: { template: string; variables?: JsonMap }) => {
      return client.renderTemplate(requiredString(input?.template, "template"), input?.variables ?? {});
    },

    ha_notify: async (input: { target: string; message: string; title?: string; data?: JsonMap }) => {
      assertToolAllowed(config, "ha_notify");
      assertDomainAllowed(config, "notify");
      const target = requiredString(input?.target, "target");
      return client.callService("notify", target, {
        message: requiredString(input?.message, "message"),
        ...(input.title ? { title: input.title } : {}),
        ...(input.data ? { data: input.data } : {})
      });
    }
  };
}
