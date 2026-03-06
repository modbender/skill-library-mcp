import { validateConfig, KNOWN_HA_DOMAINS } from "../config";

describe("validateConfig", () => {
  const validConfig = { url: "http://ha.local:8123", token: "my-token" };

  describe("valid configs", () => {
    test("accepts minimal config with url and token", () => {
      const result = validateConfig(validConfig);
      expect(result).toEqual({
        url: "http://ha.local:8123",
        token: "my-token",
        allowedDomains: [],
        readOnly: false
      });
    });

    test("accepts https URL", () => {
      const result = validateConfig({ url: "https://ha.example.com", token: "tok" });
      expect(result.url).toBe("https://ha.example.com");
    });

    test("strips trailing slash from URL", () => {
      const result = validateConfig({ url: "http://ha.local:8123/", token: "tok" });
      expect(result.url).toBe("http://ha.local:8123");
    });

    test("strips multiple trailing slashes", () => {
      const result = validateConfig({ url: "http://ha.local:8123///", token: "tok" });
      expect(result.url).toBe("http://ha.local:8123");
    });

    test("trims whitespace from URL and token", () => {
      const result = validateConfig({ url: "  http://ha.local:8123  ", token: "  tok  " });
      expect(result.url).toBe("http://ha.local:8123");
      expect(result.token).toBe("tok");
    });

    test("accepts full config with all optional fields", () => {
      const result = validateConfig({
        url: "http://ha.local:8123",
        token: "my-token",
        allowedDomains: ["light", "switch"],
        readOnly: true
      });
      expect(result).toEqual({
        url: "http://ha.local:8123",
        token: "my-token",
        allowedDomains: ["light", "switch"],
        readOnly: true
      });
    });

    test("normalizes allowedDomains to lowercase", () => {
      const result = validateConfig({
        url: "http://ha.local:8123",
        token: "tok",
        allowedDomains: ["Light", "SWITCH", "Climate"]
      });
      expect(result.allowedDomains).toEqual(["light", "switch", "climate"]);
    });

    test("defaults readOnly to false when omitted", () => {
      const result = validateConfig(validConfig);
      expect(result.readOnly).toBe(false);
    });

    test("defaults allowedDomains to empty array when omitted", () => {
      const result = validateConfig(validConfig);
      expect(result.allowedDomains).toEqual([]);
    });
  });

  describe("invalid configs", () => {
    test("rejects null config", () => {
      expect(() => validateConfig(null)).toThrow("non-null object");
    });

    test("rejects undefined config", () => {
      expect(() => validateConfig(undefined)).toThrow("non-null object");
    });

    test("rejects non-object config", () => {
      expect(() => validateConfig("string")).toThrow("non-null object");
    });

    test("rejects missing url", () => {
      expect(() => validateConfig({ token: "tok" })).toThrow("url: required");
    });

    test("rejects missing token", () => {
      expect(() => validateConfig({ url: "http://ha.local:8123" })).toThrow("token: required");
    });

    test("rejects empty url", () => {
      expect(() => validateConfig({ url: "", token: "tok" })).toThrow("url: required");
    });

    test("rejects empty token", () => {
      expect(() => validateConfig({ url: "http://ha.local:8123", token: "" })).toThrow("token: required");
    });

    test("rejects whitespace-only token", () => {
      expect(() => validateConfig({ url: "http://ha.local:8123", token: "   " })).toThrow("token: must be non-empty");
    });

    test("rejects non-http URL", () => {
      expect(() => validateConfig({ url: "ftp://ha.local", token: "tok" })).toThrow("http:// or https://");
    });

    test("rejects URL without protocol", () => {
      expect(() => validateConfig({ url: "ha.local:8123", token: "tok" })).toThrow("http:// or https://");
    });

    test("rejects non-string url", () => {
      expect(() => validateConfig({ url: 123, token: "tok" })).toThrow("url: must be a string");
    });

    test("rejects non-string token", () => {
      expect(() => validateConfig({ url: "http://ha.local:8123", token: 42 })).toThrow("token: must be a string");
    });

    test("rejects non-array allowedDomains", () => {
      expect(() => validateConfig({ ...validConfig, allowedDomains: "light" })).toThrow("must be an array");
    });

    test("rejects non-boolean readOnly", () => {
      expect(() => validateConfig({ ...validConfig, readOnly: "yes" })).toThrow("must be a boolean");
    });

    test("rejects empty strings in allowedDomains", () => {
      expect(() => validateConfig({ ...validConfig, allowedDomains: ["light", ""] })).toThrow("allowedDomains[1]");
    });

    test("rejects non-string items in allowedDomains", () => {
      expect(() => validateConfig({ ...validConfig, allowedDomains: ["light", 42] })).toThrow("allowedDomains[1]");
    });

    test("collects multiple errors", () => {
      try {
        validateConfig({ url: 123, token: 456 });
        fail("Expected error");
      } catch (err) {
        const msg = (err as Error).message;
        expect(msg).toContain("url:");
        expect(msg).toContain("token:");
      }
    });
  });
});

describe("KNOWN_HA_DOMAINS", () => {
  test("includes common domains", () => {
    expect(KNOWN_HA_DOMAINS).toContain("light");
    expect(KNOWN_HA_DOMAINS).toContain("switch");
    expect(KNOWN_HA_DOMAINS).toContain("sensor");
    expect(KNOWN_HA_DOMAINS).toContain("climate");
    expect(KNOWN_HA_DOMAINS).toContain("cover");
    expect(KNOWN_HA_DOMAINS).toContain("automation");
    expect(KNOWN_HA_DOMAINS).toContain("script");
    expect(KNOWN_HA_DOMAINS).toContain("scene");
    expect(KNOWN_HA_DOMAINS).toContain("media_player");
  });

  test("is a frozen/readonly array", () => {
    expect(() => (KNOWN_HA_DOMAINS as string[]).push("test")).toThrow();
  });
});
