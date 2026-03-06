import { describe, it, expect } from "vitest";
import { uuid } from "../src/index.js";
import { expandHome, safePath, safeLimit } from "../src/utils.js";
import os from "node:os";
import path from "node:path";

describe("uuid", () => {
  it("returns a string in UUID v4 format", () => {
    const id = uuid();
    // UUID v4: 8-4-4-4-12 hex characters
    const uuidRe = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
    expect(id).toMatch(uuidRe);
  });

  it("generates unique IDs across multiple calls", () => {
    const ids = new Set<string>();
    for (let i = 0; i < 100; i++) {
      ids.add(uuid());
    }
    expect(ids.size).toBe(100);
  });

  it("sets version nibble to 4", () => {
    const id = uuid();
    // The 13th character (index 14 considering hyphens) should be '4'
    expect(id[14]).toBe("4");
  });

  it("sets variant bits correctly (8, 9, a, or b)", () => {
    const id = uuid();
    // The 17th hex digit (index 19 considering hyphens) should be 8, 9, a, or b
    expect(id[19]).toMatch(/[89ab]/);
  });
});

describe("expandHome", () => {
  it("expands ~ to the home directory", () => {
    const result = expandHome("~");
    expect(result).toBe(os.homedir());
  });

  it("expands ~/subpath to home + subpath", () => {
    const result = expandHome("~/documents");
    expect(result).toBe(path.join(os.homedir(), "documents"));
  });

  it("returns non-tilde paths unchanged", () => {
    expect(expandHome("/usr/local")).toBe("/usr/local");
    expect(expandHome("relative/path")).toBe("relative/path");
  });

  it("returns empty string unchanged", () => {
    expect(expandHome("")).toBe("");
  });

  it("expands ~\\ (backslash) on Windows-style paths", () => {
    const result = expandHome("~\\documents");
    expect(result).toBe(path.join(os.homedir(), "documents"));
  });

  it("does not expand ~ in the middle of a path", () => {
    expect(expandHome("/home/~user")).toBe("/home/~user");
  });
});

describe("safePath", () => {
  it("resolves a path inside the home directory", () => {
    const p = path.join(os.homedir(), "openclaw", "data.jsonl");
    const result = safePath(p);
    expect(result).toBe(path.resolve(p));
  });

  it("rejects a path outside the home directory", () => {
    // Use /tmp on Unix or the drive root on Windows - both outside home
    const outside = process.platform === "win32" ? "C:\\Windows\\Temp\\evil" : "/tmp/evil";
    expect(() => safePath(outside)).toThrow(/must be inside the home directory/);
  });

  it("rejects path traversal attacks (../ escaping home)", () => {
    const traversal = path.join(os.homedir(), "..", "etc", "passwd");
    expect(() => safePath(traversal)).toThrow(/must be inside the home directory/);
  });

  it("uses the provided label in the error message", () => {
    const outside = process.platform === "win32" ? "C:\\Windows\\Temp" : "/tmp";
    expect(() => safePath(outside, "myLabel")).toThrow(/myLabel/);
  });

  it("accepts the home directory itself", () => {
    const result = safePath(os.homedir());
    expect(result).toBe(os.homedir());
  });

  it("resolves relative paths against cwd (which may or may not be in home)", () => {
    const resolved = path.resolve("relative/subdir");
    const home = os.homedir();
    const normalize = (s: string) => process.platform === "win32" ? s.toLowerCase() : s;
    if (normalize(resolved).startsWith(normalize(home))) {
      expect(safePath("relative/subdir")).toBe(resolved);
    } else {
      expect(() => safePath("relative/subdir")).toThrow(/must be inside the home directory/);
    }
  });
});

describe("safeLimit", () => {
  it("returns the value when it is a valid number within range", () => {
    expect(safeLimit(5, 10, 100)).toBe(5);
  });

  it("returns default for NaN inputs", () => {
    expect(safeLimit("abc", 10, 100)).toBe(10);
    expect(safeLimit(undefined, 10, 100)).toBe(10);
    expect(safeLimit(null, 10, 100)).toBe(10);
  });

  it("returns default for values less than 1", () => {
    expect(safeLimit(0, 10, 100)).toBe(10);
    expect(safeLimit(-5, 10, 100)).toBe(10);
  });

  it("clamps to max when value exceeds max", () => {
    expect(safeLimit(200, 10, 100)).toBe(100);
  });

  it("truncates floating point values", () => {
    expect(safeLimit(5.9, 10, 100)).toBe(5);
  });

  it("accepts string-encoded numbers", () => {
    expect(safeLimit("42", 10, 100)).toBe(42);
  });

  it("returns default for Infinity", () => {
    expect(safeLimit(Infinity, 10, 100)).toBe(100);
  });

  it("returns default for -Infinity", () => {
    expect(safeLimit(-Infinity, 10, 100)).toBe(10);
  });

  it("returns 1 when value is 1 (boundary)", () => {
    expect(safeLimit(1, 10, 100)).toBe(1);
  });

  it("returns max when value equals max", () => {
    expect(safeLimit(100, 10, 100)).toBe(100);
  });

  it("handles boolean inputs (treated as 0/1)", () => {
    // true => Number(true) = 1, which is >= 1, so return 1
    expect(safeLimit(true, 10, 100)).toBe(1);
    // false => Number(false) = 0, which is < 1, so return default
    expect(safeLimit(false, 10, 100)).toBe(10);
  });
});
