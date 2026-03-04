import { describe, it, expect } from "vitest";
import { anonymize, anonymizeObject, extractNamesFromData, extractProjectNames, PATTERNS } from "../anonymize";

describe("anonymize", () => {
  const emptyNames = new Set<string>();
  const emptyProjects = new Set<string>();

  describe("PATTERNS", () => {
    it("should replace email addresses", () => {
      const result = anonymize("contact me at john@example.com please", emptyNames, emptyProjects, null);
      expect(result).toBe("contact me at [EMAIL] please");
    });

    it("should replace OpenAI-style API keys", () => {
      const result = anonymize("key: sk-abc123def456ghi789jkl012mno", emptyNames, emptyProjects, null);
      expect(result).toBe("key: [API_KEY]");
    });

    it("should replace opensoul API keys", () => {
      const result = anonymize("auth opensoul_sk_abcdef123456", emptyNames, emptyProjects, null);
      expect(result).toBe("auth [API_KEY]");
    });

    it("should replace macOS file paths", () => {
      const result = anonymize("file at /Users/johndoe/Documents/project", emptyNames, emptyProjects, null);
      expect(result).toBe("file at /Users/[USER]/Documents/project");
    });

    it("should replace Linux home paths", () => {
      const result = anonymize("file at /home/johndoe/project", emptyNames, emptyProjects, null);
      expect(result).toBe("file at /home/[USER]/project");
    });

    it("should replace Windows paths", () => {
      const result = anonymize("file at C:\\Users\\johndoe\\Documents", emptyNames, emptyProjects, null);
      expect(result).toBe("file at C:\\Users\\[USER]\\Documents");
    });

    it("should replace local IP addresses", () => {
      const result = anonymize("server at 192.168.1.100 and 10.0.0.1", emptyNames, emptyProjects, null);
      expect(result).toBe("server at [LOCAL_IP] and [LOCAL_IP]");
    });

    it("should replace phone numbers", () => {
      const result = anonymize("call me at +1 (555) 123-4567", emptyNames, emptyProjects, null);
      expect(result).toBe("call me at [PHONE]");
    });

    it("should replace personal date events", () => {
      const result = anonymize("Married: June 15, 2020", emptyNames, emptyProjects, null);
      expect(result).toBe("[DATE_EVENT]");
    });

    it("should replace timezone info", () => {
      const result = anonymize("Timezone: America/New_York", emptyNames, emptyProjects, null);
      expect(result).toBe("Timezone: [TIMEZONE]");
    });
  });

  describe("name replacement", () => {
    it("should replace user names with [USER]", () => {
      const names = new Set(["Felix"]);
      const result = anonymize("Felix is the user and Felix's files are here", names, emptyProjects, null);
      expect(result).toBe("[USER] is the user and [USER]'s files are here");
    });

    it("should preserve agent name", () => {
      const names = new Set(["Felix", "Otto"]);
      const result = anonymize("Felix created Otto", names, emptyProjects, "Otto");
      expect(result).toBe("[USER] created Otto");
    });

    it("should not replace short names (< 3 chars)", () => {
      const names = new Set(["Al"]);
      const result = anonymize("Al is here", names, emptyProjects, null);
      expect(result).toBe("Al is here");
    });
  });

  describe("project replacement", () => {
    it("should replace project names with [PROJECT_N]", () => {
      const projects = new Set(["Acme"]);
      const result = anonymize("Working at Acme on the Acme project", emptyNames, projects, null);
      expect(result).toBe("Working at [PROJECT_1] on the [PROJECT_1] project");
    });
  });
});

describe("anonymizeObject", () => {
  const emptyNames = new Set<string>();
  const emptyProjects = new Set<string>();

  it("should anonymize string values in objects", () => {
    const obj = { email: "test@example.com", nested: { path: "/Users/john/file" } };
    const result = anonymizeObject(obj, emptyNames, emptyProjects, null);
    expect(result.email).toBe("[EMAIL]");
    expect(result.nested.path).toBe("/Users/[USER]/file");
  });

  it("should anonymize strings in arrays", () => {
    const arr = ["test@example.com", "hello"];
    const result = anonymizeObject(arr, emptyNames, emptyProjects, null);
    expect(result[0]).toBe("[EMAIL]");
    expect(result[1]).toBe("hello");
  });

  it("should redact 'user' keys entirely", () => {
    const obj = { user: "sensitive data", title: "safe" };
    const result = anonymizeObject(obj, emptyNames, emptyProjects, null);
    expect(result.user).toBe("[REDACTED]");
    expect(result.title).toBe("safe");
  });

  it("should pass through non-string/non-object values", () => {
    expect(anonymizeObject(42, emptyNames, emptyProjects, null)).toBe(42);
    expect(anonymizeObject(null, emptyNames, emptyProjects, null)).toBe(null);
    expect(anonymizeObject(true, emptyNames, emptyProjects, null)).toBe(true);
  });
});

describe("extractNamesFromData", () => {
  it("should extract names from 'Named by:' patterns", () => {
    const data = { identity: "Named by: Felix" };
    const names = extractNamesFromData(data);
    expect(names.has("Felix")).toBe(true);
  });

  it("should extract names from memory section headers", () => {
    const data = { memory: "## Felix\nSome content\n## Lessons\nMore content" };
    const names = extractNamesFromData(data);
    expect(names.has("Felix")).toBe(true);
    // "Lessons" should be excluded (common section name)
    expect(names.has("Lessons")).toBe(false);
  });
});

describe("extractProjectNames", () => {
  it("should extract company names from 'Employee at' pattern", () => {
    const data = { soul: "Employee #123 at Acme" };
    const projects = extractProjectNames(data);
    expect(projects.has("Acme")).toBe(true);
  });

  it("should extract app-style folder names from paths", () => {
    const data = { agents: "working in /projects/myapp directory" };
    const projects = extractProjectNames(data);
    expect(projects.has("myapp")).toBe(true);
  });
});
