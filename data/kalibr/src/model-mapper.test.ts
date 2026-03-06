import { describe, it, expect } from "vitest";
import { openClawToKalibr, kalibrToOpenClaw, inferProvider } from "./model-mapper.js";

describe("openClawToKalibr", () => {
  it("maps known Anthropic models", () => {
    expect(openClawToKalibr("anthropic/claude-opus-4-6")).toBe("claude-opus-4-6");
    expect(openClawToKalibr("anthropic/claude-sonnet-4-5")).toBe("claude-sonnet-4-5");
  });

  it("maps known OpenAI models", () => {
    expect(openClawToKalibr("openai/gpt-5.2")).toBe("gpt-5.2");
    expect(openClawToKalibr("openai/gpt-5.2-mini")).toBe("gpt-5.2-mini");
    expect(openClawToKalibr("openai/gpt-5.1-codex")).toBe("gpt-5.1-codex");
  });

  it("strips provider prefix for unknown models", () => {
    expect(openClawToKalibr("google/gemini-ultra")).toBe("gemini-ultra");
    expect(openClawToKalibr("mistral/mixtral-8x22b")).toBe("mixtral-8x22b");
  });

  it("handles models with multiple slashes", () => {
    expect(openClawToKalibr("custom/org/model-name")).toBe("org/model-name");
  });

  it("returns as-is if no slash present", () => {
    expect(openClawToKalibr("standalone-model")).toBe("standalone-model");
  });

  it("returns as-is for empty string", () => {
    expect(openClawToKalibr("")).toBe("");
  });
});

describe("inferProvider", () => {
  it("infers anthropic from claude- prefix", () => {
    expect(inferProvider("claude-sonnet-4-5")).toBe("anthropic");
    expect(inferProvider("claude-opus-4-6")).toBe("anthropic");
    expect(inferProvider("claude-sonnet-4-5-20250929")).toBe("anthropic");
    expect(inferProvider("claude-3-haiku-20240307")).toBe("anthropic");
  });

  it("infers openai from gpt- prefix", () => {
    expect(inferProvider("gpt-5.2")).toBe("openai");
    expect(inferProvider("gpt-4o")).toBe("openai");
    expect(inferProvider("gpt-4o-mini")).toBe("openai");
    expect(inferProvider("gpt-5.2-mini")).toBe("openai");
  });

  it("infers openai from o1/o3/o4 prefixes", () => {
    expect(inferProvider("o1-preview")).toBe("openai");
    expect(inferProvider("o3-mini")).toBe("openai");
    expect(inferProvider("o4-mini")).toBe("openai");
  });

  it("infers google from gemini/gemma prefixes", () => {
    expect(inferProvider("gemini-ultra")).toBe("google");
    expect(inferProvider("gemini-2.0-flash")).toBe("google");
    expect(inferProvider("gemma-7b")).toBe("google");
  });

  it("infers mistral from mistral/mixtral/codestral prefixes", () => {
    expect(inferProvider("mistral-large")).toBe("mistral");
    expect(inferProvider("mixtral-8x22b")).toBe("mistral");
    expect(inferProvider("codestral-latest")).toBe("mistral");
  });

  it("infers meta from llama prefix", () => {
    expect(inferProvider("llama3.3:8b")).toBe("meta");
    expect(inferProvider("llama-3.1-70b")).toBe("meta");
  });

  it("infers cohere from command- prefix", () => {
    expect(inferProvider("command-r-plus")).toBe("cohere");
  });

  it("infers deepseek from deepseek- prefix", () => {
    expect(inferProvider("deepseek-coder")).toBe("deepseek");
    expect(inferProvider("deepseek-v3")).toBe("deepseek");
  });

  it("is case-insensitive", () => {
    expect(inferProvider("Claude-Sonnet-4-5")).toBe("anthropic");
    expect(inferProvider("GPT-5.2")).toBe("openai");
  });

  it("returns null for unknown patterns", () => {
    expect(inferProvider("unknown-model")).toBeNull();
    expect(inferProvider("")).toBeNull();
    expect(inferProvider("some-random-thing")).toBeNull();
  });
});

describe("kalibrToOpenClaw", () => {
  it("maps known model IDs via explicit lookup", () => {
    expect(kalibrToOpenClaw("claude-opus-4-6")).toEqual({
      provider: "anthropic",
      model: "claude-opus-4-6",
    });
    expect(kalibrToOpenClaw("gpt-5.2")).toEqual({
      provider: "openai",
      model: "gpt-5.2",
    });
    expect(kalibrToOpenClaw("gpt-5.2-mini")).toEqual({
      provider: "openai",
      model: "gpt-5.2-mini",
    });
  });

  it("splits model_id that already contains slash", () => {
    expect(kalibrToOpenClaw("google/gemini-ultra")).toEqual({
      provider: "google",
      model: "gemini-ultra",
    });
    expect(kalibrToOpenClaw("custom/org/model")).toEqual({
      provider: "custom",
      model: "org/model",
    });
  });

  it("infers provider from model name patterns for unknown models", () => {
    expect(kalibrToOpenClaw("claude-sonnet-4-5-20250929")).toEqual({
      provider: "anthropic",
      model: "claude-sonnet-4-5-20250929",
    });
    expect(kalibrToOpenClaw("gpt-4o")).toEqual({
      provider: "openai",
      model: "gpt-4o",
    });
    expect(kalibrToOpenClaw("gpt-4o-mini")).toEqual({
      provider: "openai",
      model: "gpt-4o-mini",
    });
    expect(kalibrToOpenClaw("gemini-2.0-flash")).toEqual({
      provider: "google",
      model: "gemini-2.0-flash",
    });
    expect(kalibrToOpenClaw("mixtral-8x22b")).toEqual({
      provider: "mistral",
      model: "mixtral-8x22b",
    });
    expect(kalibrToOpenClaw("llama3.3:8b")).toEqual({
      provider: "meta",
      model: "llama3.3:8b",
    });
    expect(kalibrToOpenClaw("deepseek-v3")).toEqual({
      provider: "deepseek",
      model: "deepseek-v3",
    });
  });

  it("returns null for completely unknown models", () => {
    expect(kalibrToOpenClaw("unknown-model")).toBeNull();
    expect(kalibrToOpenClaw("")).toBeNull();
  });
});
