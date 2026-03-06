#!/usr/bin/env node
/**
 * SkillScout MCP Server
 * 
 * Agent-first skill discovery. Agents query this to find trusted skills.
 * Protocol: MCP (Model Context Protocol) over stdio
 * Data: Fetches from static JSON API (GitHub Pages)
 * 
 * Tools:
 *   - search_skills: Find skills by description/category/tag
 *   - get_skill: Get full review details for a specific skill
 *   - list_categories: List all skill categories with counts
 *   - get_safe_skills: Get all skills rated "safe"
 */

import { createInterface } from 'readline';

const DATA_URL = 'https://nashbot67.github.io/skillscout/data/skills.json';
const CATEGORIES_URL = 'https://nashbot67.github.io/skillscout/data/categories.json';

let skillsCache = null;
let categoriesCache = null;
let cacheTime = 0;
const CACHE_TTL = 300_000; // 5 minutes

async function fetchData() {
  if (skillsCache && Date.now() - cacheTime < CACHE_TTL) return;
  try {
    const [skillsRes, catsRes] = await Promise.all([
      fetch(DATA_URL),
      fetch(CATEGORIES_URL),
    ]);
    skillsCache = await skillsRes.json();
    categoriesCache = await catsRes.json();
    cacheTime = Date.now();
  } catch (e) {
    if (!skillsCache) throw new Error('Failed to fetch SkillScout data: ' + e.message);
    // Use stale cache on failure
  }
}

// MCP Tool definitions
const TOOLS = [
  {
    name: 'search_skills',
    description: 'Search for AI agent skills by what you want to accomplish. Returns security-reviewed skills with trust scores.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'What you want your agent to help with (e.g., "manage my email", "research papers")' },
        category: { type: 'string', description: 'Filter by category (e.g., "Productivity & Tasks", "Security & Passwords")' },
        trustScore: { type: 'string', enum: ['safe', 'caution', 'avoid'], description: 'Filter by trust level' },
        limit: { type: 'number', description: 'Max results (default: 10)' },
      },
      required: ['query'],
    },
  },
  {
    name: 'get_skill',
    description: 'Get the full security review for a specific skill by name.',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Skill name (e.g., "apple-notes", "bitwarden")' },
      },
      required: ['name'],
    },
  },
  {
    name: 'list_categories',
    description: 'List all skill categories with counts of reviewed skills.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'get_safe_skills',
    description: 'Get all skills rated "safe" — zero or minimal security risk.',
    inputSchema: {
      type: 'object',
      properties: {
        category: { type: 'string', description: 'Optional category filter' },
      },
    },
  },
];

// Tool handlers
async function handleTool(name, args) {
  await fetchData();
  const skills = skillsCache?.skills || [];

  switch (name) {
    case 'search_skills': {
      const q = (args.query || '').toLowerCase();
      const limit = args.limit || 10;
      let results = skills.filter(s => {
        const text = [s.name, s.description, s.plainDescription, ...(s.tags || [])].join(' ').toLowerCase();
        const matchesQuery = !q || text.includes(q);
        const matchesCat = !args.category || s.category === args.category;
        const matchesTrust = !args.trustScore || s.trustScore === args.trustScore;
        return matchesQuery && matchesCat && matchesTrust;
      });
      // Sort: safe first, then by rating
      results.sort((a, b) => {
        const trustOrder = { safe: 0, caution: 1, avoid: 2 };
        const ta = trustOrder[a.trustScore] ?? 1;
        const tb = trustOrder[b.trustScore] ?? 1;
        if (ta !== tb) return ta - tb;
        return (b.rating || 0) - (a.rating || 0);
      });
      results = results.slice(0, limit);
      return results.map(s => ({
        name: s.name,
        author: s.author,
        category: s.category,
        description: s.plainDescription || s.description,
        trustScore: s.trustScore,
        rating: s.rating,
        permissions: s.permissions,
        install: `npx clawhub@latest install ${s.author}/${s.name}`,
      }));
    }

    case 'get_skill': {
      const skill = skills.find(s => s.name === args.name);
      if (!skill) return { error: `Skill "${args.name}" not found in SkillScout catalog.` };
      return skill;
    }

    case 'list_categories': {
      const cats = {};
      for (const s of skills) {
        const c = s.category || 'Other';
        if (!cats[c]) cats[c] = { count: 0, safe: 0, caution: 0, avoid: 0 };
        cats[c].count++;
        cats[c][s.trustScore || 'caution']++;
      }
      return Object.entries(cats).map(([name, data]) => ({
        name,
        ...data,
        emoji: (categoriesCache?.categories?.find(c => c.slug === name) || {}).emoji || '📦',
      })).sort((a, b) => b.count - a.count);
    }

    case 'get_safe_skills': {
      let safe = skills.filter(s => s.trustScore === 'safe');
      if (args.category) safe = safe.filter(s => s.category === args.category);
      return safe.map(s => ({
        name: s.name,
        author: s.author,
        category: s.category,
        description: s.plainDescription || s.description,
        rating: s.rating,
        install: `npx clawhub@latest install ${s.author}/${s.name}`,
      }));
    }

    default:
      return { error: `Unknown tool: ${name}` };
  }
}

// MCP stdio protocol handler
const rl = createInterface({ input: process.stdin });
let requestId = 0;

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

rl.on('line', async (line) => {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }

  const { id, method, params } = msg;

  switch (method) {
    case 'initialize':
      send({
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: {
            name: 'skillscout',
            version: '0.1.0',
          },
        },
      });
      break;

    case 'notifications/initialized':
      // No response needed
      break;

    case 'tools/list':
      send({
        jsonrpc: '2.0',
        id,
        result: { tools: TOOLS },
      });
      break;

    case 'tools/call': {
      const { name, arguments: args } = params;
      try {
        const result = await handleTool(name, args || {});
        send({
          jsonrpc: '2.0',
          id,
          result: {
            content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
          },
        });
      } catch (e) {
        send({
          jsonrpc: '2.0',
          id,
          result: {
            content: [{ type: 'text', text: `Error: ${e.message}` }],
            isError: true,
          },
        });
      }
      break;
    }

    default:
      send({
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: `Method not found: ${method}` },
      });
  }
});

process.stderr.write('SkillScout MCP server started\n');
