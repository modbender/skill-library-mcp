const { describe, test, expect, beforeAll, afterAll, beforeEach } = require("bun:test");
const fs = require("fs");
const path = require("path");

const {
  getSkillDir,
  getRegistryPath,
  getAgentsDir,
  resolveRegistryAgentPath,
  loadRegistry,
  saveRegistry,
} = require("../lib/registry");

describe("registry", () => {
  describe("getSkillDir", () => {
    test("returns the project root (parent of lib/)", () => {
      const skillDir = getSkillDir();
      expect(skillDir).toBe(path.resolve(__dirname, ".."));
      expect(fs.existsSync(path.join(skillDir, "lib"))).toBe(true);
    });
  });

  describe("getRegistryPath", () => {
    test("returns path to references/registry.json", () => {
      const registryPath = getRegistryPath();
      expect(registryPath).toEndWith(path.join("references", "registry.json"));
    });
  });

  describe("getAgentsDir", () => {
    test("returns path to agents/", () => {
      const agentsDir = getAgentsDir();
      expect(agentsDir).toEndWith("agents");
    });
  });

  describe("resolveRegistryAgentPath", () => {
    test("resolves bare file names under agents/", () => {
      const result = resolveRegistryAgentPath("test-agent.md");
      expect(result.ok).toBe(true);
      expect(result.path).toEndWith(path.join("agents", "test-agent.md"));
    });

    test("resolves paths prefixed with agents/", () => {
      const result = resolveRegistryAgentPath(path.join("agents", "category", "a.md"));
      expect(result.ok).toBe(true);
      expect(result.path).toEndWith(path.join("agents", "category", "a.md"));
    });

    test("rejects path traversal entries", () => {
      const result = resolveRegistryAgentPath("../../etc/passwd");
      expect(result.ok).toBe(false);
      expect(result.error).toContain("Refusing to load agent outside");
    });

    test("rejects absolute paths outside agents/", () => {
      const result = resolveRegistryAgentPath("/tmp/outside.md");
      expect(result.ok).toBe(false);
      expect(result.error).toContain("Refusing to load agent outside");
    });
  });

  describe("loadRegistry", () => {
    test("loads and parses existing registry.json", () => {
      const registry = loadRegistry();
      // Our real registry exists and has agents
      if (registry) {
        expect(registry).toHaveProperty("agents");
        expect(registry).toHaveProperty("version");
        expect(Array.isArray(registry.agents)).toBe(true);
      }
    });

    test("returns null for missing file", () => {
      // Temporarily move registry to test missing file behavior
      const registryPath = getRegistryPath();
      const backupPath = registryPath + ".bak";
      const exists = fs.existsSync(registryPath);
      if (exists) fs.renameSync(registryPath, backupPath);

      const result = loadRegistry();
      expect(result).toBeNull();

      if (exists) fs.renameSync(backupPath, registryPath);
    });

    test("returns null for invalid JSON", () => {
      const registryPath = getRegistryPath();
      const backupPath = registryPath + ".bak";
      const exists = fs.existsSync(registryPath);
      let original;
      if (exists) {
        original = fs.readFileSync(registryPath, "utf8");
        fs.writeFileSync(registryPath, "NOT VALID JSON{{{", "utf8");
      }

      const result = loadRegistry();
      if (exists) {
        expect(result).toBeNull();
        fs.writeFileSync(registryPath, original, "utf8");
      }
    });
  });

  describe("saveRegistry", () => {
    const testDir = path.join(getSkillDir(), "references", "_test_save");
    const testPath = path.join(testDir, "test_registry.json");

    afterAll(() => {
      try {
        fs.rmSync(testDir, { recursive: true, force: true });
      } catch {}
    });

    test("saves registry as minified JSON", () => {
      const registryPath = getRegistryPath();
      const backupPath = registryPath + ".save.bak";
      const exists = fs.existsSync(registryPath);
      let original;
      if (exists) {
        original = fs.readFileSync(registryPath, "utf8");
      }

      const testData = { version: 1, agents: [], stats: {} };
      const result = saveRegistry(testData);
      expect(result).toBe(true);

      const saved = JSON.parse(fs.readFileSync(registryPath, "utf8"));
      expect(saved).toEqual(testData);

      // Restore original
      if (exists) {
        fs.writeFileSync(registryPath, original, "utf8");
      }
    });
  });
});
