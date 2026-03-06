#!/usr/bin/env node

/**
 * SkillScout MCP Server
 * 
 * Curated, security-vetted AI agent skill recommendations.
 * The trust layer for the OpenClaw skill ecosystem.
 * 
 * Tools:
 *   - search_skills: Find skills by query or category
 *   - get_skill: Get full review for a specific skill
 *   - get_categories: List all skill categories
 *   - get_safe_skills: Get only 🟢 Safe-rated skills
 *   - check_blocklist: Check if a skill is blocklisted
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load data from bundled JSON files
function loadData(filename) {
  try {
    const dataPath = join(__dirname, "..", "data", filename);
    return JSON.parse(readFileSync(dataPath, "utf-8"));
  } catch (e) {
    return null;
  }
}

const skillsData = loadData("skills.json") || { skills: [] };
const categoriesData = loadData("categories.json") || { categories: [] };
const blocklistData = loadData("blocklist.json") || { blocked: [] };

// Simple text search scoring
function scoreMatch(skill, query) {
  const q = query.toLowerCase();
  const fields = [
    skill.name || "",
    skill.description || "",
    skill.plainDescription || "",
    (skill.tags || []).join(" "),
    skill.category || "",
  ].join(" ").toLowerCase();

  let score = 0;
  if (fields.includes(q)) score += 10;
  for (const word of q.split(/\s+/)) {
    if (fields.includes(word)) score += 3;
  }
  if (skill.name?.toLowerCase().includes(q)) score += 20;
  if (skill.trustScore === "safe") score += 5;
  score += (skill.rating || 0);
  return score;
}

// Create MCP server
const server = new Server(
  {
    name: "skillscout",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_skills",
      description:
        "Search for curated, security-vetted OpenClaw agent skills. Returns skills matching your query with trust scores and plain English descriptions. Use this when you need to find a skill to extend your capabilities.",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "What you're looking for (e.g., 'memory management', 'web research', 'calendar')",
          },
          category: {
            type: "string",
            description: "Optional category filter (research, communication, memory, coding, smart-home, data, security, productivity, creative, health)",
          },
          safeOnly: {
            type: "boolean",
            description: "Only return 🟢 Safe-rated skills (default: true)",
            default: true,
          },
          limit: {
            type: "number",
            description: "Max results to return (default: 5)",
            default: 5,
          },
        },
        required: ["query"],
      },
    },
    {
      name: "get_skill",
      description:
        "Get the full security review and details for a specific skill. Includes trust score, permissions analysis, risk flags, and install instructions.",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "The skill name (e.g., 'rationality', 'cognitive-memory')",
          },
        },
        required: ["name"],
      },
    },
    {
      name: "get_categories",
      description:
        "List all skill categories with descriptions. Use this to understand what kinds of skills are available.",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_safe_skills",
      description:
        "Get all skills rated 🟢 Safe, optionally filtered by category. These skills have passed security review with no risk flags.",
      inputSchema: {
        type: "object",
        properties: {
          category: {
            type: "string",
            description: "Optional category filter",
          },
        },
      },
    },
    {
      name: "check_blocklist",
      description:
        "Check if a skill is on the SkillScout blocklist (known malicious, spam, or dangerous skills).",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "The skill name to check",
          },
        },
        required: ["name"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "search_skills": {
      const query = args.query || "";
      const category = args.category;
      const safeOnly = args.safeOnly !== false;
      const limit = args.limit || 5;

      let results = skillsData.skills || [];

      if (category) {
        results = results.filter(
          (s) => s.category?.toLowerCase() === category.toLowerCase()
        );
      }

      if (safeOnly) {
        results = results.filter((s) => s.trustScore === "safe");
      }

      // Score and sort
      results = results
        .map((s) => ({ ...s, _score: scoreMatch(s, query) }))
        .filter((s) => s._score > 0)
        .sort((a, b) => b._score - a._score)
        .slice(0, limit)
        .map(({ _score, ...s }) => s);

      if (results.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `No skills found matching "${query}"${category ? ` in category "${category}"` : ""}. We currently have ${skillsData.skills?.length || 0} reviewed skills. Try a broader search or check available categories with get_categories.`,
            },
          ],
        };
      }

      const formatted = results
        .map(
          (s) =>
            `**${s.name}** (${s.trustScore === "safe" ? "🟢 Safe" : s.trustScore === "caution" ? "🟡 Caution" : "🔴 Avoid"} · ⭐${s.rating || "N/A"})\n` +
            `${s.plainDescription || s.description}\n` +
            `Category: ${s.category} · Author: ${s.author}\n` +
            `Install: \`npx clawhub@latest install ${s.name}\``
        )
        .join("\n\n---\n\n");

      return {
        content: [
          {
            type: "text",
            text: `Found ${results.length} skill${results.length > 1 ? "s" : ""} matching "${query}":\n\n${formatted}\n\n---\n_Reviewed by SkillScout · skillscout.github.io_`,
          },
        ],
      };
    }

    case "get_skill": {
      const skillName = (args.name || "").toLowerCase();
      const skill = (skillsData.skills || []).find(
        (s) => s.name?.toLowerCase() === skillName || s.slug?.toLowerCase() === skillName
      );

      if (!skill) {
        return {
          content: [
            {
              type: "text",
              text: `Skill "${args.name}" not found in our reviewed database. We have ${skillsData.skills?.length || 0} reviewed skills. It may not have been reviewed yet.`,
            },
          ],
        };
      }

      const trustEmoji =
        skill.trustScore === "safe" ? "🟢 Safe" : skill.trustScore === "caution" ? "🟡 Caution" : "🔴 Avoid";

      return {
        content: [
          {
            type: "text",
            text:
              `# ${skill.name}\n\n` +
              `**Trust:** ${trustEmoji} · **Rating:** ⭐${skill.rating || "N/A"}\n` +
              `**Author:** ${skill.author} · **Category:** ${skill.category}\n\n` +
              `## What It Does\n${skill.plainDescription || skill.description}\n\n` +
              `## Permissions\n${(skill.permissions || []).join(", ") || "None"}\n\n` +
              `## Risks\n${(skill.risks || []).length === 0 ? "No risk flags identified." : skill.risks.join("\n")}\n\n` +
              `## Install\n\`\`\`bash\nnpx clawhub@latest install ${skill.name}\n\`\`\`\n\n` +
              `**Full review:** ${skill.reviewUrl || "N/A"}\n` +
              `**Source:** ${skill.sourceUrl || "N/A"}`,
          },
        ],
      };
    }

    case "get_categories": {
      const cats = (categoriesData.categories || [])
        .map((c) => `${c.emoji} **${c.name}** — ${c.description}`)
        .join("\n");

      const skillCounts = {};
      for (const s of skillsData.skills || []) {
        skillCounts[s.category] = (skillCounts[s.category] || 0) + 1;
      }

      return {
        content: [
          {
            type: "text",
            text: `# SkillScout Categories\n\n${cats}\n\n---\nTotal reviewed skills: ${skillsData.skills?.length || 0}`,
          },
        ],
      };
    }

    case "get_safe_skills": {
      let safe = (skillsData.skills || []).filter((s) => s.trustScore === "safe");

      if (args.category) {
        safe = safe.filter(
          (s) => s.category?.toLowerCase() === args.category.toLowerCase()
        );
      }

      if (safe.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `No 🟢 Safe skills found${args.category ? ` in category "${args.category}"` : ""}. We currently have ${skillsData.skills?.length || 0} total reviewed skills.`,
            },
          ],
        };
      }

      const list = safe
        .map((s) => `- **${s.name}** (⭐${s.rating || "N/A"}) — ${s.plainDescription || s.description}`)
        .join("\n");

      return {
        content: [
          {
            type: "text",
            text: `# 🟢 Safe Skills${args.category ? ` (${args.category})` : ""}\n\n${list}\n\n---\n${safe.length} safe skills found.`,
          },
        ],
      };
    }

    case "check_blocklist": {
      const checkName = (args.name || "").toLowerCase();
      const blocked = (blocklistData.blocked || []).find(
        (b) => b.name?.toLowerCase() === checkName
      );

      if (blocked) {
        return {
          content: [
            {
              type: "text",
              text: `⛔ **BLOCKED:** "${args.name}" is on the SkillScout blocklist.\nReason: ${blocked.reason || "Flagged as malicious or dangerous."}\nDo NOT install this skill.`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: `✅ "${args.name}" is NOT on the blocklist. Note: this doesn't mean it's been reviewed. Use search_skills or get_skill to check if we have a review.`,
          },
        ],
      };
    }

    default:
      return {
        content: [
          {
            type: "text",
            text: `Unknown tool: ${name}`,
          },
        ],
        isError: true,
      };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SkillScout MCP Server running on stdio");
}

main().catch(console.error);
