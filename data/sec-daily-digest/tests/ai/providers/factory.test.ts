import { describe, expect, test } from "bun:test";
import { createProvider } from "../../../src/ai/providers/factory";

describe("createProvider", () => {
  test("defaults to openai when provider is missing", () => {
    const provider = createProvider(undefined, {
      OPENAI_API_KEY: "test-key",
    } as NodeJS.ProcessEnv);
    expect(provider.id).toBe("openai");
  });

  test("uses explicit provider selection", () => {
    const provider = createProvider("gemini", {
      GEMINI_API_KEY: "test-key",
    } as NodeJS.ProcessEnv);
    expect(provider.id).toBe("gemini");
  });

  test("throws for unsupported provider", () => {
    expect(() =>
      createProvider("invalid" as never, process.env),
    ).toThrow("Unsupported provider");
  });
});
