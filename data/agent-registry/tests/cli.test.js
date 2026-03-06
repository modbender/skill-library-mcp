const { describe, test, expect, beforeAll, afterAll } = require("bun:test");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const BIN = path.resolve(__dirname, "..");

/**
 * Runs a bun script and captures stdout, stderr, exit code.
 */
function run(script, args = [], opts = {}) {
  return new Promise((resolve) => {
    const proc = spawn("bun", [path.join(BIN, script), ...args], {
      cwd: BIN,
      env: { ...process.env, AGENT_REGISTRY_NO_TELEMETRY: "1" },
      ...opts,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));

    proc.on("close", (code) => {
      resolve({ stdout, stderr, code });
    });
  });
}

/**
 * Runs a bun script with data piped to stdin.
 */
function runWithStdin(script, stdinData, args = []) {
  return new Promise((resolve) => {
    const proc = spawn("bun", [path.join(BIN, script), ...args], {
      cwd: BIN,
      env: { ...process.env, AGENT_REGISTRY_NO_TELEMETRY: "1" },
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));

    proc.on("close", (code) => {
      resolve({ stdout, stderr, code });
    });

    proc.stdin.write(stdinData);
    proc.stdin.end();
  });
}

// Check if a real registry exists for integration tests that need it
const registryPath = path.join(BIN, "references", "registry.json");
const hasRegistry = fs.existsSync(registryPath);

describe("CLI integration", () => {
  describe("bin/cli.js (dispatcher)", () => {
    test("shows help with no arguments", async () => {
      const { stdout, code } = await run("bin/cli.js");
      expect(code).toBe(0);
      expect(stdout).toContain("Agent Registry");
      expect(stdout).toContain("Commands:");
      expect(stdout).toContain("search");
      expect(stdout).toContain("get");
      expect(stdout).toContain("list");
      expect(stdout).toContain("init");
      expect(stdout).toContain("rebuild");
    });

    test("shows help with --help flag", async () => {
      const { stdout, code } = await run("bin/cli.js", ["--help"]);
      expect(code).toBe(0);
      expect(stdout).toContain("Usage:");
    });

    test("exits with error for unknown command", async () => {
      const { stderr, code } = await run("bin/cli.js", ["unknown-command"]);
      expect(code).toBe(1);
      expect(stderr).toContain("Unknown command");
    });
  });

  describe("bin/search.js", () => {
    test("shows usage with no arguments", async () => {
      const { stdout, code } = await run("bin/search.js");
      expect(code).toBe(1);
      expect(stdout).toContain("Usage:");
    });

    if (hasRegistry) {
      test("returns results for a valid query", async () => {
        const { stdout, code } = await run("bin/search.js", ["code review"]);
        expect(code).toBe(0);
        expect(stdout).toContain("matching agent");
      });

      test("supports --json flag", async () => {
        const { stdout, code } = await run("bin/search.js", [
          "code review",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(Array.isArray(parsed)).toBe(true);
      });

      test("supports --top flag", async () => {
        const { stdout, code } = await run("bin/search.js", [
          "test",
          "--top",
          "2",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed.length).toBeLessThanOrEqual(2);
      });

      test("returns empty for nonsense query", async () => {
        const { stdout, code } = await run("bin/search.js", [
          "zzzzxxxxxyyyyy",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed).toEqual([]);
      });
    }
  });

  describe("bin/get.js", () => {
    test("shows help with --help", async () => {
      const { stdout, code } = await run("bin/get.js", ["--help"]);
      expect(code).toBe(0);
      expect(stdout).toContain("Usage:");
      expect(stdout).toContain("--json");
      expect(stdout).toContain("--raw");
    });

    if (hasRegistry) {
      test("lists agents when no name given", async () => {
        const { stdout, code } = await run("bin/get.js");
        expect(code).toBe(0);
        expect(stdout).toContain("Available agents:");
      });

      test("exits with error for non-existent agent", async () => {
        const { stderr, code } = await run("bin/get.js", [
          "zzz-nonexistent-agent-zzz",
        ]);
        expect(code).toBe(1);
        expect(stderr).toContain("not found");
      });
    }
  });

  describe("bin/list.js", () => {
    test("shows help with --help", async () => {
      const { stdout, code } = await run("bin/list.js", ["--help"]);
      expect(code).toBe(0);
      expect(stdout).toContain("Usage:");
      expect(stdout).toContain("--detailed");
      expect(stdout).toContain("--simple");
      expect(stdout).toContain("--json");
    });

    if (hasRegistry) {
      test("shows table by default", async () => {
        const { stdout, code } = await run("bin/list.js");
        expect(code).toBe(0);
        expect(stdout).toContain("Agent Name");
        expect(stdout).toContain("Tokens");
        expect(stdout).toContain("Total:");
      });

      test("supports --json output", async () => {
        const { stdout, code } = await run("bin/list.js", ["--json"]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed).toHaveProperty("agents");
        expect(Array.isArray(parsed.agents)).toBe(true);
      });

      test("supports --simple output", async () => {
        const { stdout, code } = await run("bin/list.js", ["--simple"]);
        expect(code).toBe(0);
        // Simple output is just agent names, one per line
        const lines = stdout.trim().split("\n");
        expect(lines.length).toBeGreaterThan(0);
        // No header row in simple mode
        expect(stdout).not.toContain("Agent Name");
      });

      test("supports --detailed output", async () => {
        const { stdout, code } = await run("bin/list.js", ["--detailed"]);
        expect(code).toBe(0);
        expect(stdout).toContain("Summary:");
        expect(stdout).toContain("Tokens:");
        expect(stdout).toContain("Keywords:");
      });
    }
  });

  describe("bin/search-paged.js", () => {
    test("shows usage with no arguments", async () => {
      const { stdout, code } = await run("bin/search-paged.js");
      expect(code).toBe(1);
      expect(stdout).toContain("Usage:");
    });

    if (hasRegistry) {
      test("returns paginated results", async () => {
        const { stdout, code } = await run("bin/search-paged.js", [
          "code",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed).toHaveProperty("total_results");
        expect(parsed).toHaveProperty("results");
        expect(Array.isArray(parsed.results)).toBe(true);
      });

      test("supports --page and --page-size", async () => {
        const { stdout, code } = await run("bin/search-paged.js", [
          "test",
          "--page",
          "1",
          "--page-size",
          "3",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed.page).toBe(1);
        expect(parsed.page_size).toBe(3);
        expect(parsed.results.length).toBeLessThanOrEqual(3);
      });

      test("supports --offset and --limit", async () => {
        const { stdout, code } = await run("bin/search-paged.js", [
          "code",
          "--offset",
          "0",
          "--limit",
          "2",
          "--json",
        ]);
        expect(code).toBe(0);
        const parsed = JSON.parse(stdout);
        expect(parsed).toHaveProperty("offset");
        expect(parsed).toHaveProperty("limit");
        expect(parsed.results.length).toBeLessThanOrEqual(2);
      });
    }
  });

  describe("bin/rebuild.js", () => {
    // Rebuild needs an agents/ dir with .md files. We create a temporary one.
    const testAgentsDir = path.join(BIN, "agents", "_test_rebuild_agent");
    const testAgentFile = path.join(testAgentsDir, "rebuild-test-agent.md");

    beforeAll(() => {
      fs.mkdirSync(testAgentsDir, { recursive: true });
      fs.writeFileSync(
        testAgentFile,
        "# Rebuild Test Agent\n\nA test agent for rebuild testing.\n\n## Skills\n- Testing\n- JavaScript\n",
        "utf8"
      );
    });

    afterAll(() => {
      fs.rmSync(testAgentsDir, { recursive: true, force: true });
    });

    test("rebuilds registry from agents directory", async () => {
      const { stdout, code } = await run("bin/rebuild.js");
      expect(code).toBe(0);
      expect(stdout).toContain("Scanning agents directory");
      expect(stdout).toContain("Registry rebuilt");
      expect(stdout).toContain("rebuild-test-agent");
    });
  });
});

describe("hooks/user_prompt_search.js", () => {
  if (hasRegistry) {
    test("outputs additionalContext for matching prompts", async () => {
      const input = JSON.stringify({
        prompt: "I need help with code review and security auditing my project",
      });
      const { stdout, code } = await runWithStdin(
        "hooks/user_prompt_search.js",
        input
      );
      // The hook may or may not find high-confidence matches depending on the registry
      // But it should exit cleanly (0)
      expect(code).toBe(0);
      if (stdout.trim()) {
        const parsed = JSON.parse(stdout);
        expect(parsed).toHaveProperty("additionalContext");
      }
    });

    test("exits silently for short prompts (< 3 words)", async () => {
      const input = JSON.stringify({ prompt: "help me" });
      const { stdout, code } = await runWithStdin(
        "hooks/user_prompt_search.js",
        input
      );
      expect(code).toBe(0);
      expect(stdout.trim()).toBe("");
    });

    test("exits silently for slash commands", async () => {
      const input = JSON.stringify({ prompt: "/help with something here" });
      const { stdout, code } = await runWithStdin(
        "hooks/user_prompt_search.js",
        input
      );
      expect(code).toBe(0);
      expect(stdout.trim()).toBe("");
    });

    test("exits silently for empty prompts", async () => {
      const input = JSON.stringify({ prompt: "" });
      const { stdout, code } = await runWithStdin(
        "hooks/user_prompt_search.js",
        input
      );
      expect(code).toBe(0);
      expect(stdout.trim()).toBe("");
    });
  }

  test("exits silently for invalid JSON input", async () => {
    const { stdout, code } = await runWithStdin(
      "hooks/user_prompt_search.js",
      "NOT VALID JSON"
    );
    expect(code).toBe(0);
    expect(stdout.trim()).toBe("");
  });
});
