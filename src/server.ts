import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { SkillEntry } from "./types.js";
import { searchSkills } from "./search.js";
import { loadSkill } from "./loader.js";

export function createServer(index: SkillEntry[], skillsDir: string): McpServer {
  const server = new McpServer({
    name: "skill-library",
    version: "1.0.0",
  });

  // Build lookup map keyed by both dirName and frontmatter name
  const lookupMap = new Map<string, SkillEntry>();
  for (const entry of index) {
    lookupMap.set(entry.dirName.toLowerCase(), entry);
    lookupMap.set(entry.frontmatter.name.toLowerCase(), entry);
  }

  server.tool(
    "search_skill",
    "Search for skills by keyword. Returns ranked list of matching skill names and descriptions.",
    { query: z.string().describe("Keywords to search for (e.g. 'debugging', 'react patterns', 'terraform')") },
    async ({ query }) => {
      const results = searchSkills(index, query);

      if (results.length === 0) {
        return {
          content: [{ type: "text", text: `No skills found matching "${query}".` }],
        };
      }

      const lines = results.map(
        (r) => `- **${r.name}** (${r.dirName})${r.hasResources ? " [+resources]" : ""} — ${r.description}`,
      );

      return {
        content: [{
          type: "text",
          text: `Found ${results.length} skills matching "${query}":\n\n${lines.join("\n")}`,
        }],
      };
    },
  );

  server.tool(
    "load_skill",
    "Load the full content of a skill by name. Returns the complete SKILL.md content and optionally resources.",
    {
      name: z.string().describe("Skill name or directory name (e.g. 'brainstorming', 'ai-engineer')"),
      include_resources: z.boolean().default(false).describe("Whether to include resource files"),
    },
    async ({ name, include_resources }) => {
      const entry = lookupMap.get(name.toLowerCase());

      if (!entry) {
        // Try fuzzy match
        const results = searchSkills(index, name, 5);
        if (results.length > 0) {
          const suggestions = results.map((r) => r.name).join(", ");
          return {
            content: [{
              type: "text",
              text: `Skill "${name}" not found. Did you mean: ${suggestions}?`,
            }],
          };
        }

        return {
          content: [{ type: "text", text: `Skill "${name}" not found.` }],
        };
      }

      const content = await loadSkill(entry, skillsDir, include_resources);

      return {
        content: [{ type: "text", text: content }],
      };
    },
  );

  return server;
}
