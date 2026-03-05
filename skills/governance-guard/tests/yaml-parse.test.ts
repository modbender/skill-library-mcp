import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { parseYaml, parsePolicyFile } from "../scripts/yaml-parse.js";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// Resolve project root relative to this test file
const __dirname_test = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname_test, "..");

describe("parseYaml", () => {
  it("parses scalar key-value pairs", () => {
    const result = parseYaml('name: foo\nversion: "0.1"') as Record<string, unknown>;
    assert.equal(result["name"], "foo");
    assert.equal(result["version"], "0.1");
  });

  it("parses integer values", () => {
    const result = parseYaml("count: 42\nnegative: -7") as Record<string, unknown>;
    assert.equal(result["count"], 42);
    assert.equal(result["negative"], -7);
  });

  it("parses boolean values", () => {
    const result = parseYaml("enabled: true\ndisabled: false") as Record<string, unknown>;
    assert.equal(result["enabled"], true);
    assert.equal(result["disabled"], false);
  });

  it("parses string arrays with dash syntax", () => {
    const result = parseYaml("items:\n  - foo\n  - bar\n  - baz") as Record<string, unknown>;
    assert.deepEqual(result["items"], ["foo", "bar", "baz"]);
  });

  it("parses inline arrays with bracket syntax", () => {
    const result = parseYaml('tags: [a, b, c]') as Record<string, unknown>;
    assert.deepEqual(result["tags"], ["a", "b", "c"]);
  });

  it("parses nested objects via indentation", () => {
    const yaml = "parent:\n  child1: val1\n  child2: val2";
    const result = parseYaml(yaml) as Record<string, unknown>;
    assert.deepEqual(result["parent"], { child1: "val1", child2: "val2" });
  });

  it("strips comments", () => {
    const result = parseYaml("name: foo # this is a comment") as Record<string, unknown>;
    assert.equal(result["name"], "foo");
  });

  it("handles quoted strings (single and double)", () => {
    const result = parseYaml(`single: 'hello world'\ndouble: "hello world"`) as Record<string, unknown>;
    assert.equal(result["single"], "hello world");
    assert.equal(result["double"], "hello world");
  });

  it("handles empty input as empty object", () => {
    const result = parseYaml("");
    assert.deepEqual(result, {});
  });

  it("handles empty lines between entries", () => {
    const result = parseYaml("a: 1\n\nb: 2\n\nc: 3") as Record<string, unknown>;
    assert.equal(result["a"], 1);
    assert.equal(result["b"], 2);
    assert.equal(result["c"], 3);
  });

  it("rejects tabs in indentation", () => {
    assert.throws(() => parseYaml("name:\n\tchild: val"), /Tabs/);
  });
});

describe("parsePolicyFile", () => {
  it("parses minimal.yaml correctly", () => {
    const content = readFileSync(join(projectRoot, "policies", "minimal.yaml"), "utf8");
    const policy = parsePolicyFile(content);
    assert.equal(policy.version, "0.1");
    assert.equal(policy.default_verdict, "approve");
    assert.ok(policy.rules.length >= 1);
    assert.equal(policy.rules[0]!.name, "block-credentials");
    assert.equal(policy.rules[0]!.verdict, "deny");
  });

  it("parses standard.yaml correctly", () => {
    const content = readFileSync(join(projectRoot, "policies", "standard.yaml"), "utf8");
    const policy = parsePolicyFile(content);
    assert.equal(policy.version, "0.1");
    assert.equal(policy.default_verdict, "deny");
    assert.ok(policy.rules.length >= 5);
    // First rule should be allow-read-local
    assert.equal(policy.rules[0]!.name, "allow-read-local");
    assert.equal(policy.rules[0]!.verdict, "approve");
  });

  it("parses strict.yaml correctly", () => {
    const content = readFileSync(join(projectRoot, "policies", "strict.yaml"), "utf8");
    const policy = parsePolicyFile(content);
    assert.equal(policy.version, "0.1");
    assert.equal(policy.default_verdict, "deny");
    assert.ok(policy.rules.length >= 1);
    assert.equal(policy.rules[0]!.name, "allow-read-workspace");
  });

  it("rejects missing version field", () => {
    assert.throws(
      () => parsePolicyFile("default_verdict: deny\nrules:\n  - name: test\n    verdict: deny"),
      /version/,
    );
  });

  it("rejects invalid default_verdict", () => {
    assert.throws(
      () => parsePolicyFile('version: "0.1"\ndefault_verdict: maybe'),
      /default_verdict/,
    );
  });

  it("rejects rules without name", () => {
    assert.throws(
      () => parsePolicyFile('version: "0.1"\ndefault_verdict: deny\nrules:\n  - verdict: deny'),
      /name/,
    );
  });

  it("rejects rules without verdict", () => {
    assert.throws(
      () => parsePolicyFile('version: "0.1"\ndefault_verdict: deny\nrules:\n  - name: test'),
      /verdict/,
    );
  });

  it("parses sensitive_data rules", () => {
    const yaml = `version: "0.1"
default_verdict: deny
sensitive_data:
  - category: credentials
    action: deny
    patterns:
      - "**/*.env"
      - "**/.ssh/**"`;
    const policy = parsePolicyFile(yaml);
    assert.equal(policy.sensitive_data.length, 1);
    assert.equal(policy.sensitive_data[0]!.category, "credentials");
    assert.equal(policy.sensitive_data[0]!.action, "deny");
    assert.deepEqual(policy.sensitive_data[0]!.patterns, ["**/*.env", "**/.ssh/**"]);
  });
});
