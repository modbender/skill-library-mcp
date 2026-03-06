import { describe, it, expect } from "vitest";
import { validateConfig } from "./config";

describe("validateConfig", () => {
  const valid = { relay_url: "https://relay.example.com", node_id: "n1", auth_token: "secret" };

  it("returns validated config for valid input", () => {
    const result = validateConfig(valid);
    expect(result.relay_url).toBe("wss://relay.example.com");
    expect(result.node_id).toBe("n1");
    expect(result.auth_token).toBe("secret");
  });

  it("converts https to wss", () => {
    expect(validateConfig(valid).relay_url).toBe("wss://relay.example.com");
  });

  it("converts http to ws", () => {
    const result = validateConfig({ ...valid, relay_url: "http://localhost:8080" });
    expect(result.relay_url).toBe("ws://localhost:8080");
  });

  it("strips trailing slashes", () => {
    const result = validateConfig({ ...valid, relay_url: "https://relay.example.com///" });
    expect(result.relay_url).toBe("wss://relay.example.com");
  });

  it("preserves wss:// URLs", () => {
    const result = validateConfig({ ...valid, relay_url: "wss://relay.example.com" });
    expect(result.relay_url).toBe("wss://relay.example.com");
  });

  it("throws if relay_url is missing", () => {
    expect(() => validateConfig({ node_id: "n1", auth_token: "t" })).toThrow("relay_url is required");
  });

  it("throws if node_id is missing", () => {
    expect(() => validateConfig({ relay_url: "https://x.com", auth_token: "t" })).toThrow("node_id is required");
  });

  it("throws if auth_token is missing", () => {
    expect(() => validateConfig({ relay_url: "https://x.com", node_id: "n1" })).toThrow("auth_token is required");
  });

  it("throws for empty object", () => {
    expect(() => validateConfig({})).toThrow("relay_url is required");
  });
});
