import { HAClient } from "../client";
import { HAClientError, PluginConfig } from "../types";

function makeConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
  return {
    url: "http://ha.local:8123",
    token: "test-llat-token",
    allowedDomains: [],
    readOnly: false,
    ...overrides
  };
}

function mockFetchResponse(status: number, body: unknown, ok?: boolean): jest.Mock {
  const text = typeof body === "string" ? body : JSON.stringify(body);
  return jest.fn().mockResolvedValue({
    ok: ok ?? (status >= 200 && status < 300),
    status,
    text: () => Promise.resolve(text)
  });
}

beforeEach(() => {
  jest.restoreAllMocks();
});

describe("HAClient", () => {
  describe("constructor", () => {
    test("strips trailing slash from base URL", () => {
      const client = new HAClient(makeConfig({ url: "http://ha.local:8123/" }));
      global.fetch = mockFetchResponse(200, { message: "API running." });
      client.checkConnection();
      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/",
        expect.any(Object)
      );
    });

    test("preserves URL without trailing slash", () => {
      const client = new HAClient(makeConfig({ url: "http://ha.local:8123" }));
      global.fetch = mockFetchResponse(200, { message: "API running." });
      client.checkConnection();
      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/",
        expect.any(Object)
      );
    });
  });

  describe("authentication", () => {
    test("sends Bearer token in Authorization header", async () => {
      const client = new HAClient(makeConfig({ token: "my-secret-token" }));
      global.fetch = mockFetchResponse(200, { version: "2026.2.0" });

      await client.getConfig();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer my-secret-token"
          })
        })
      );
    });

    test("sends Content-Type application/json", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.getStates();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            "Content-Type": "application/json"
          })
        })
      );
    });
  });

  describe("checkConnection", () => {
    test("returns true when API is reachable", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, { message: "API running." });

      const result = await client.checkConnection();

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/",
        expect.any(Object)
      );
    });

    test("throws HAClientError on 401 Unauthorized", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(401, "Unauthorized");

      await expect(client.checkConnection()).rejects.toThrow(HAClientError);
      await expect(client.checkConnection()).rejects.toMatchObject({ statusCode: 401 });
    });
  });

  describe("getConfig", () => {
    test("sends GET /api/config", async () => {
      const client = new HAClient(makeConfig());
      const mockBody = { version: "2026.2.0", location_name: "Home" };
      global.fetch = mockFetchResponse(200, mockBody);

      const result = await client.getConfig();

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/config",
        expect.objectContaining({ method: "GET" })
      );
      expect(result).toEqual(mockBody);
    });
  });

  describe("getStates", () => {
    test("sends GET /api/states and returns array", async () => {
      const client = new HAClient(makeConfig());
      const states = [
        { entity_id: "light.kitchen", state: "on", attributes: {} },
        { entity_id: "sensor.temp", state: "22", attributes: {} }
      ];
      global.fetch = mockFetchResponse(200, states);

      const result = await client.getStates();

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/states",
        expect.objectContaining({ method: "GET" })
      );
      expect(result).toEqual(states);
      expect(result).toHaveLength(2);
    });
  });

  describe("getState", () => {
    test("sends GET /api/states/{entity_id}", async () => {
      const client = new HAClient(makeConfig());
      const entity = { entity_id: "light.kitchen", state: "on", attributes: { brightness: 255 } };
      global.fetch = mockFetchResponse(200, entity);

      const result = await client.getState("light.kitchen");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/states/light.kitchen",
        expect.objectContaining({ method: "GET" })
      );
      expect(result).toEqual(entity);
    });

    test("encodes special characters in entity_id", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, { entity_id: "sensor.a%2Fb", state: "0", attributes: {} });

      await client.getState("sensor.a/b");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/states/sensor.a%2Fb",
        expect.any(Object)
      );
    });

    test("throws HAClientError on 404", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(404, "Entity not found");

      try {
        await client.getState("sensor.nonexistent");
        fail("Expected error");
      } catch (err) {
        expect(err).toBeInstanceOf(HAClientError);
        expect((err as HAClientError).statusCode).toBe(404);
        expect((err as HAClientError).body).toBe("Entity not found");
      }
    });
  });

  describe("getServices", () => {
    test("sends GET /api/services", async () => {
      const client = new HAClient(makeConfig());
      const services = [{ domain: "light", services: { turn_on: { name: "Turn on" } } }];
      global.fetch = mockFetchResponse(200, services);

      const result = await client.getServices();

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/services",
        expect.objectContaining({ method: "GET" })
      );
      expect(result).toEqual(services);
    });
  });

  describe("callService", () => {
    test("sends POST with service data", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, [{ entity_id: "light.kitchen", state: "on", attributes: {} }]);

      await client.callService("light", "turn_on", { entity_id: "light.kitchen", brightness: 200 });

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/services/light/turn_on",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ entity_id: "light.kitchen", brightness: 200 })
        })
      );
    });

    test("sends empty object when no service data provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.callService("homeassistant", "restart");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/services/homeassistant/restart",
        expect.objectContaining({
          body: JSON.stringify({})
        })
      );
    });

    test("encodes domain and service in URL", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.callService("my_domain", "my_service");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/services/my_domain/my_service",
        expect.any(Object)
      );
    });
  });

  describe("getHistory", () => {
    test("sends GET with start timestamp", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, [[]]);

      await client.getHistory("2026-02-27T00:00:00Z");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/history/period/2026-02-27T00%3A00%3A00Z",
        expect.objectContaining({ method: "GET" })
      );
    });

    test("adds filter_entity_id param when entityId provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, [[]]);

      await client.getHistory("2026-02-27T00:00:00Z", "sensor.temp");

      const url = (global.fetch as jest.Mock).mock.calls[0][0] as string;
      expect(url).toContain("filter_entity_id=sensor.temp");
    });

    test("adds end_time param when endTimestamp provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, [[]]);

      await client.getHistory("2026-02-27T00:00:00Z", undefined, "2026-02-28T00:00:00Z");

      const url = (global.fetch as jest.Mock).mock.calls[0][0] as string;
      expect(url).toContain("end_time=2026-02-28T00%3A00%3A00Z");
      expect(url).not.toContain("filter_entity_id");
    });

    test("includes both params when both provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, [[]]);

      await client.getHistory("2026-02-27T00:00:00Z", "sensor.temp", "2026-02-28T00:00:00Z");

      const url = (global.fetch as jest.Mock).mock.calls[0][0] as string;
      expect(url).toContain("filter_entity_id=sensor.temp");
      expect(url).toContain("end_time=");
    });
  });

  describe("getLogbook", () => {
    test("sends GET /api/logbook/{timestamp}", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.getLogbook("2026-02-27T00:00:00Z");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/logbook/2026-02-27T00%3A00%3A00Z",
        expect.objectContaining({ method: "GET" })
      );
    });

    test("adds entity param when entityId provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.getLogbook("2026-02-27T00:00:00Z", "light.kitchen");

      const url = (global.fetch as jest.Mock).mock.calls[0][0] as string;
      expect(url).toContain("entity=light.kitchen");
    });
  });

  describe("renderTemplate", () => {
    test("sends POST /api/template with template string", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, "42");

      const result = await client.renderTemplate("{{ 40 + 2 }}");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/template",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ template: "{{ 40 + 2 }}" })
        })
      );
      expect(result).toBe(42);
    });

    test("merges variables into body", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, "hello world");

      await client.renderTemplate("{{ greeting }}", { greeting: "hello world" });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ template: "{{ greeting }}", greeting: "hello world" })
        })
      );
    });
  });

  describe("fireEvent", () => {
    test("sends POST /api/events/{event_type}", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, { message: "Event my_event fired." });

      const result = await client.fireEvent("my_event", { key: "value" });

      expect(global.fetch).toHaveBeenCalledWith(
        "http://ha.local:8123/api/events/my_event",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ key: "value" })
        })
      );
      expect(result).toEqual({ message: "Event my_event fired." });
    });

    test("sends empty object when no event data provided", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, { message: "Event test fired." });

      await client.fireEvent("test");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({})
        })
      );
    });
  });

  describe("error handling", () => {
    test("throws HAClientError with status code and body on non-ok response", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(403, "Forbidden");

      try {
        await client.getConfig();
        fail("Expected error");
      } catch (err) {
        expect(err).toBeInstanceOf(HAClientError);
        const clientErr = err as HAClientError;
        expect(clientErr.statusCode).toBe(403);
        expect(clientErr.body).toBe("Forbidden");
        expect(clientErr.message).toBe("Home Assistant HTTP 403: Forbidden");
        expect(clientErr.name).toBe("HAClientError");
      }
    });

    test("throws HAClientError on 500 server error", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(500, "Internal Server Error");

      await expect(client.getStates()).rejects.toThrow(HAClientError);
      await expect(client.getStates()).rejects.toMatchObject({ statusCode: 500 });
    });

    test("returns empty object for empty response body", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, "");

      const result = await client.callService("homeassistant", "restart");

      expect(result).toEqual({});
    });

    test("returns raw text when body is not valid JSON", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        text: () => Promise.resolve("plain text result")
      });

      const result = await client.renderTemplate("{{ states('sensor.temp') }}");

      expect(result).toBe("plain text result");
    });

    test("does not send body for GET requests", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, []);

      await client.getStates();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: undefined
        })
      );
    });
  });

  describe("timeout", () => {
    test("includes AbortSignal in fetch requests", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = mockFetchResponse(200, { version: "2026.2.0" });

      await client.getConfig();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      );
    });

    test("throws descriptive error on abort", async () => {
      const client = new HAClient(makeConfig());
      const abortError = new DOMException("The operation was aborted.", "AbortError");
      global.fetch = jest.fn().mockRejectedValue(abortError);

      await expect(client.getConfig()).rejects.toThrow("timed out");
    });

    test("re-throws non-abort fetch errors", async () => {
      const client = new HAClient(makeConfig());
      global.fetch = jest.fn().mockRejectedValue(new TypeError("Failed to fetch"));

      await expect(client.getConfig()).rejects.toThrow("Failed to fetch");
    });
  });
});
