import { describe, it, expect } from "vitest";
import { simpleSummary, formatOutput, type LLMSummary } from "../summarize";

describe("simpleSummary", () => {
  it("should extract agent name from identity", () => {
    const data = { identity: "**Name:** Otto" };
    const result = simpleSummary(data);
    expect(result.title).toBe("Otto");
  });

  it("should fall back to 'OpenClaw Agent' when no identity", () => {
    const result = simpleSummary({});
    expect(result.title).toBe("OpenClaw Agent");
  });

  it("should not use [USER] as title", () => {
    const data = { identity: "**Name:** [USER]" };
    const result = simpleSummary(data);
    expect(result.title).toBe("OpenClaw Agent");
  });

  it("should build tagline from tool names", () => {
    const data = { tools: { toolNames: ["calendar", "email", "browser"] } };
    const result = simpleSummary(data);
    expect(result.tagline).toBe("Assistant with calendar, email, browser integration");
  });

  it("should use generic tagline when no tools", () => {
    const result = simpleSummary({});
    expect(result.tagline).toBe("Personal AI assistant");
  });

  it("should extract enabled cron jobs as automation", () => {
    const data = {
      cronJobs: [
        { name: "daily-check", description: "Check inbox", enabled: true },
        { name: "disabled-job", description: "Disabled", enabled: false },
      ],
    };
    const result = simpleSummary(data);
    expect(result.interestingAutomation).toHaveLength(1);
    expect(result.interestingAutomation[0]).toBe("daily-check: Check inbox");
  });

  it("should return empty arrays for missing sections", () => {
    const result = simpleSummary({});
    expect(result.keyPatterns).toEqual([]);
    expect(result.lessonsLearned).toEqual([]);
    expect(result.toolsUsed).toEqual([]);
  });
});

describe("formatOutput", () => {
  const baseSummary: LLMSummary = {
    title: "Test Agent",
    tagline: "A test agent",
    summary: "Testing.",
    keyPatterns: ["Pattern 1"],
    lessonsLearned: ["Lesson 1"],
    interestingAutomation: [],
    toolsUsed: ["calendar"],
  };

  const baseData = {
    soul: "# SOUL.md",
    agents: "# AGENTS.md",
    identity: "# IDENTITY.md",
    toolsRaw: "# TOOLS.md",
    skills: [{ name: "weather" }],
    cronJobs: [{ name: "check", schedule: "0 9 * * *", description: "Morning check", enabled: true }],
  };

  it("should include profile fields from summary", () => {
    const output = formatOutput(baseSummary, baseData, false);
    expect(output.profile.title).toBe("Test Agent");
    expect(output.profile.tagline).toBe("A test agent");
    expect(output.profile.keyPatterns).toEqual(["Pattern 1"]);
  });

  it("should include raw file contents", () => {
    const output = formatOutput(baseSummary, baseData, false);
    expect(output.raw.soul).toBe("# SOUL.md");
    expect(output.raw.agents).toBe("# AGENTS.md");
  });

  it("should set usedLLM flag in meta", () => {
    const withLLM = formatOutput(baseSummary, baseData, true);
    expect(withLLM.meta.usedLLM).toBe(true);
    expect(withLLM.meta.model).toBeTruthy();

    const withoutLLM = formatOutput(baseSummary, baseData, false);
    expect(withoutLLM.meta.usedLLM).toBe(false);
    expect(withoutLLM.meta.model).toBeNull();
  });

  it("should extract skill names", () => {
    const output = formatOutput(baseSummary, baseData, false);
    expect(output.profile.skills).toEqual(["weather"]);
  });

  it("should include enabled cron jobs", () => {
    const output = formatOutput(baseSummary, baseData, false);
    expect(output.profile.cronJobs).toHaveLength(1);
    expect(output.profile.cronJobs[0].name).toBe("check");
  });
});
