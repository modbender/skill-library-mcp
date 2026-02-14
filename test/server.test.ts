import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { buildIndex } from "../src/skill-index.js";
import { createServer } from "../src/server.js";
import type { SearchIndex } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixturesDir = join(__dirname, "fixtures");

let client: Client;

beforeAll(async () => {
  const index = await buildIndex(fixturesDir);
  const server = createServer(index, fixturesDir);

  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await server.connect(serverTransport);

  client = new Client({ name: "test-client", version: "1.0.0" });
  await client.connect(clientTransport);
});

async function callTool(name: string, args: Record<string, unknown>): Promise<string> {
  const result = await client.callTool({ name, arguments: args });
  const content = result.content as Array<{ type: string; text: string }>;
  return content[0].text;
}

describe("search_skill tool", () => {
  it("returns matching skills for valid query", async () => {
    const text = await callTool("search_skill", { query: "basic" });
    expect(text).toContain("basic-skill");
    expect(text).toContain("Found");
  });

  it("returns 'no skills found' for unmatched query", async () => {
    const text = await callTool("search_skill", { query: "zzzznonexistent" });
    expect(text).toContain("No skills found");
  });

  it("includes [+resources] marker for skills with resources", async () => {
    const text = await callTool("search_skill", { query: "skill" });
    expect(text).toContain("[+resources]");
  });

  it("formats results as markdown list", async () => {
    const text = await callTool("search_skill", { query: "skill" });
    expect(text).toMatch(/^Found \d+ skills/);
    expect(text).toContain("- **");
    expect(text).toContain("** (");
  });
});

describe("list_categories tool", () => {
  it("returns formatted category list", async () => {
    const text = await callTool("list_categories", {});
    expect(text).toContain("categories:");
    expect(text).toContain("**Other**");
  });

  it("output contains category counts", async () => {
    const text = await callTool("list_categories", {});
    expect(text).toMatch(/\(\d+\)/);
  });

  it("mentions total skill count", async () => {
    const text = await callTool("list_categories", {});
    expect(text).toMatch(/^\d+ skills in/);
  });
});

describe("load_skill tool", () => {
  it("loads skill by exact dirName", async () => {
    const text = await callTool("load_skill", { name: "basic-skill" });
    expect(text).toContain("# Basic Skill");
    expect(text).toContain("basic skill used for testing");
  });

  it("loads skill case-insensitively", async () => {
    const text = await callTool("load_skill", { name: "Basic-Skill" });
    expect(text).toContain("# Basic Skill");
  });

  it("includes resources when requested", async () => {
    const text = await callTool("load_skill", {
      name: "skill-with-resources",
      include_resources: true,
    });
    expect(text).toContain("# Resource: examples.md");
    expect(text).toContain("# Resource: guide.md");
  });

  it("returns fuzzy suggestions for unknown skill name", async () => {
    const text = await callTool("load_skill", { name: "basik-skill" });
    expect(text).toContain("not found");
    expect(text).toContain("Did you mean");
  });

  it("returns plain 'not found' when no fuzzy matches", async () => {
    const text = await callTool("load_skill", { name: "zzzznonexistent" });
    expect(text).toBe('Skill "zzzznonexistent" not found.');
  });

  it("defaults include_resources to false", async () => {
    const text = await callTool("load_skill", { name: "skill-with-resources" });
    expect(text).toContain("# Skill With Resources");
    expect(text).not.toContain("# Resource:");
  });
});
