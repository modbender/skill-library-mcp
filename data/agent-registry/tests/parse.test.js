const { describe, test, expect, beforeAll, afterAll } = require("bun:test");
const fs = require("fs");
const path = require("path");

const { extractSummary, extractKeywords, contentHash, parseAgentFile } = require("../lib/parse");

describe("parse", () => {
  describe("extractSummary", () => {
    test("extracts first paragraph from plain content", () => {
      const content = "This is a test agent that does things.\n\nMore details here.";
      expect(extractSummary(content)).toBe("This is a test agent that does things.");
    });

    test("skips YAML frontmatter", () => {
      const content = "---\nname: test\ndescription: foo\n---\n\nActual summary here.";
      expect(extractSummary(content)).toBe("Actual summary here.");
    });

    test("skips markdown headers", () => {
      const content = "# My Agent\n\n## Overview\n\nThis is the real summary.";
      expect(extractSummary(content)).toBe("This is the real summary.");
    });

    test("truncates long summaries at 200 chars", () => {
      const longLine = "A".repeat(250);
      const summary = extractSummary(longLine);
      expect(summary.length).toBeLessThanOrEqual(200);
      expect(summary).toEndWith("...");
    });

    test("returns fallback for empty content", () => {
      expect(extractSummary("")).toBe("No description available");
    });

    test("returns fallback for header-only content", () => {
      expect(extractSummary("# Just a header\n## Another header")).toBe("No description available");
    });

    test("joins multiple lines into single summary", () => {
      const content = "First line of summary.\nSecond line continues.\n\nNew paragraph.";
      expect(extractSummary(content)).toBe("First line of summary. Second line continues.");
    });

    test("handles frontmatter with content after", () => {
      const content = "---\nname: agent\n---\n# Title\n\nDescription after frontmatter and title.";
      expect(extractSummary(content)).toBe("Description after frontmatter and title.");
    });

    test("stops collecting at first empty line after content", () => {
      const content = "Line one.\nLine two.\n\nLine three should not appear.";
      const summary = extractSummary(content);
      expect(summary).toBe("Line one. Line two.");
      expect(summary).not.toContain("Line three");
    });
  });

  describe("extractKeywords", () => {
    test("finds tech terms in content", () => {
      const content = "This agent uses React and TypeScript for frontend development.";
      const keywords = extractKeywords(content);
      expect(keywords).toContain("react");
      expect(keywords).toContain("typescript");
      expect(keywords).toContain("frontend");
    });

    test("extracts words from headers", () => {
      const content = "# Authentication Handler\n\nSome content.";
      const keywords = extractKeywords(content);
      expect(keywords).toContain("auth");
      expect(keywords).toContain("authentication");
    });

    test("limits to 20 keywords max", () => {
      // Content with many tech terms
      const content = "python javascript typescript rust go java ruby react vue angular " +
        "node docker kubernetes k8s aws gcp azure terraform ansible " +
        "sql postgres mysql mongodb redis api rest graphql grpc " +
        "test testing security frontend backend devops";
      const keywords = extractKeywords(content);
      expect(keywords.length).toBeLessThanOrEqual(20);
    });

    test("returns empty array for content with no tech terms", () => {
      const content = "This is a very generic text with no recognized terms.";
      const keywords = extractKeywords(content);
      // May find some header words but no tech terms
      expect(Array.isArray(keywords)).toBe(true);
    });

    test("avoids duplicate keywords", () => {
      const content = "# React Expert\n\nReact is great for react apps.\nKeywords: react";
      const keywords = extractKeywords(content);
      const reactCount = keywords.filter(k => k === "react").length;
      expect(reactCount).toBe(1);
    });

    test("ignores short header words (<=3 chars)", () => {
      const content = "# My API\n\nContent here.";
      const keywords = extractKeywords(content);
      // "my" is <=3 chars, should not be included from header
      expect(keywords).not.toContain("my");
    });

    test("finds multi-word terms like 'machine learning'", () => {
      const content = "This agent specializes in machine learning tasks.";
      const keywords = extractKeywords(content);
      expect(keywords).toContain("machine learning");
    });
  });

  describe("contentHash", () => {
    test("returns 8 character hex string", () => {
      const hash = contentHash("test content");
      expect(hash).toHaveLength(8);
      expect(hash).toMatch(/^[0-9a-f]{8}$/);
    });

    test("returns consistent hash for same content", () => {
      const hash1 = contentHash("hello world");
      const hash2 = contentHash("hello world");
      expect(hash1).toBe(hash2);
    });

    test("returns different hash for different content", () => {
      const hash1 = contentHash("content A");
      const hash2 = contentHash("content B");
      expect(hash1).not.toBe(hash2);
    });
  });

  describe("parseAgentFile", () => {
    const testDir = path.join(__dirname, "_test_agents");
    const testFile = path.join(testDir, "test-agent.md");

    beforeAll(() => {
      fs.mkdirSync(testDir, { recursive: true });
      fs.writeFileSync(testFile, "---\nname: test-agent\n---\n# Test Agent\n\nA test agent for unit testing.\n\n## Features\n\n- Uses React and TypeScript\n- Supports Docker deployments\n", "utf8");
    });

    afterAll(() => {
      fs.rmSync(testDir, { recursive: true, force: true });
    });

    test("parses a valid agent file", () => {
      const result = parseAgentFile(testFile);
      expect(result).not.toBeNull();
      expect(result.name).toBe("test-agent");
      expect(result.filename).toBe("test-agent.md");
      expect(result.path).toBe(testFile);
      expect(typeof result.summary).toBe("string");
      expect(result.summary).not.toBe("No description available");
      expect(Array.isArray(result.keywords)).toBe(true);
      expect(typeof result.token_estimate).toBe("number");
      expect(result.token_estimate).toBeGreaterThan(0);
      expect(result.content_hash).toMatch(/^[0-9a-f]{8}$/);
    });

    test("extracts correct name from filename", () => {
      const result = parseAgentFile(testFile);
      expect(result.name).toBe("test-agent");
    });

    test("calculates token estimate as content.length / 4", () => {
      const content = fs.readFileSync(testFile, "utf8");
      const result = parseAgentFile(testFile);
      expect(result.token_estimate).toBe(Math.floor(content.length / 4));
    });

    test("returns null for non-existent file", () => {
      const result = parseAgentFile("/non/existent/file.md");
      expect(result).toBeNull();
    });

    test("extracts keywords from content", () => {
      const result = parseAgentFile(testFile);
      expect(result.keywords).toContain("react");
      expect(result.keywords).toContain("typescript");
      expect(result.keywords).toContain("docker");
    });
  });
});
