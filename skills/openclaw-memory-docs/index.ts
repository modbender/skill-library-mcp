import { mkdir, writeFile, readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import {
  DefaultRedactor,
  HashEmbedder,
  JsonlMemoryStore,
  uuid,
  expandHome,
  safePath,
  safeLimit,
  type MemoryItem,
  type PluginApi,
  type CommandContext,
  type ToolCallParams,
} from "@elvatis_com/openclaw-memory-core";

// ---------------------------------------------------------------------------
// Flag parser: extracts --tags and --project from an argument string.
// Returns the remaining text with flags stripped out.
// ---------------------------------------------------------------------------

export interface ParsedFlags {
  tags: string[];
  project: string | undefined;
  text: string;
}

export function parseFlags(raw: string): ParsedFlags {
  let tags: string[] = [];
  let project: string | undefined;

  // Match --tags=val or --tags val (comma-separated, no spaces in values)
  const tagsEq = raw.match(/--tags=(\S+)/);
  const tagsSp = !tagsEq ? raw.match(/--tags\s+(\S+)/) : null;
  if (tagsEq) {
    tags = tagsEq[1]!.split(",").map((t) => t.trim()).filter(Boolean);
    raw = raw.replace(tagsEq[0], "");
  } else if (tagsSp) {
    tags = tagsSp[1]!.split(",").map((t) => t.trim()).filter(Boolean);
    raw = raw.replace(tagsSp[0], "");
  }

  // Match --project=val or --project val
  const projEq = raw.match(/--project=(\S+)/);
  const projSp = !projEq ? raw.match(/--project\s+(\S+)/) : null;
  if (projEq) {
    project = projEq[1]!;
    raw = raw.replace(projEq[0], "");
  } else if (projSp) {
    project = projSp[1]!;
    raw = raw.replace(projSp[0], "");
  }

  return { tags, project, text: raw.replace(/\s+/g, " ").trim() };
}

// ---------------------------------------------------------------------------
// Format helpers for displaying tags and project in output lines.
// ---------------------------------------------------------------------------

function formatTagsBadge(tags: string[], defaultTags: string[]): string {
  const extra = tags.filter((t) => !defaultTags.includes(t));
  if (extra.length === 0) return "";
  return ` [tags:${extra.join(",")}]`;
}

function formatProjectBadge(meta: Record<string, unknown> | undefined): string {
  if (!meta || typeof meta.project !== "string") return "";
  return ` [project:${meta.project}]`;
}

// ---------------------------------------------------------------------------
// Markdown export helper: converts a MemoryItem to a markdown file with
// YAML frontmatter containing metadata and the memory text as body.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Markdown import helper: parses a markdown file with YAML frontmatter back
// into a MemoryItem. Returns undefined if the format is invalid.
// ---------------------------------------------------------------------------

export function parseMarkdownToItem(content: string): MemoryItem | undefined {
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n\n?([\s\S]*)/);
  if (!fmMatch) return undefined;

  const frontmatter = fmMatch[1] ?? "";
  const body = (fmMatch[2] ?? "").trimEnd();

  // Parse frontmatter fields
  const idMatch = frontmatter.match(/^id:\s*(.+)$/m);
  const kindMatch = frontmatter.match(/^kind:\s*(.+)$/m);
  const createdAtMatch = frontmatter.match(/^createdAt:\s*(.+)$/m);
  const projectMatch = frontmatter.match(/^project:\s*(.+)$/m);

  const id = idMatch?.[1]?.trim();
  const kind = kindMatch?.[1]?.trim();
  const createdAt = createdAtMatch?.[1]?.trim();

  if (!id || !kind || !createdAt || !body) return undefined;

  // Parse tags (YAML list format)
  const tags: string[] = [];
  const tagsSection = frontmatter.match(/^tags:\n((?:\s+-\s+.+\n?)*)/m);
  if (tagsSection) {
    const tagLines = tagsSection[1]?.match(/^\s+-\s+(.+)$/gm) ?? [];
    for (const line of tagLines) {
      const val = line.match(/^\s+-\s+(.+)$/)?.[1]?.trim();
      if (val) tags.push(val);
    }
  }

  const meta: Record<string, unknown> = {};
  const project = projectMatch?.[1]?.trim();
  if (project) meta.project = project;

  const item: MemoryItem = {
    id,
    kind: kind as MemoryItem["kind"],
    text: body,
    createdAt,
  };
  if (tags.length > 0) item.tags = tags;
  if (Object.keys(meta).length > 0) item.meta = meta;

  return item;
}

export function formatAsMarkdown(item: MemoryItem): string {
  const lines: string[] = ["---"];
  lines.push(`id: ${item.id}`);
  lines.push(`kind: ${item.kind}`);
  lines.push(`createdAt: ${item.createdAt}`);
  if (item.tags && item.tags.length > 0) {
    lines.push("tags:");
    for (const tag of item.tags) {
      lines.push(`  - ${tag}`);
    }
  }
  const project =
    item.meta && typeof (item.meta as Record<string, unknown>).project === "string"
      ? ((item.meta as Record<string, unknown>).project as string)
      : undefined;
  if (project) {
    lines.push(`project: ${project}`);
  }
  lines.push("---");
  lines.push("");
  lines.push(item.text);
  lines.push("");
  return lines.join("\n");
}

export default function register(api: PluginApi) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    storePath?: string;
    dims?: number;
    redactSecrets?: boolean;
    defaultTags?: string[];
    maxItems?: number;
    exportPath?: string;
  };

  if (cfg.enabled === false) return;

  let storePath: string;
  try {
    storePath = safePath(expandHome(cfg.storePath ?? "~/.openclaw/workspace/memory/docs-memory.jsonl"), "[memory-docs] storePath");
  } catch (err: unknown) {
    api.logger?.error?.(`[memory-docs] ${(err as Error).message}`);
    return;
  }

  const embedder = new HashEmbedder(cfg.dims ?? 256);
  const store = new JsonlMemoryStore({ filePath: storePath, embedder, maxItems: cfg.maxItems ?? 5000 });
  const redactor = new DefaultRedactor();
  const defaultTags = cfg.defaultTags ?? ["docs"];
  const redactSecrets = cfg.redactSecrets !== false;

  api.logger?.info?.(`[memory-docs] enabled. store=${storePath}`);

  // Command: /remember-doc [--tags t1,t2] [--project name] <text>
  api.registerCommand({
    name: "remember-doc",
    description: "Save a documentation memory item (explicit capture)",
    usage: "/remember-doc [--tags t1,t2] [--project name] <text>",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const rawArgs = String(ctx?.args ?? "").trim();
      if (!rawArgs) {
        return { text: "Usage: /remember-doc [--tags t1,t2] [--project name] <text>" };
      }

      const flags = parseFlags(rawArgs);
      const text = flags.text;
      if (!text) {
        return { text: "Usage: /remember-doc [--tags t1,t2] [--project name] <text>" };
      }

      const r = redactSecrets ? redactor.redact(text) : { redactedText: text, hadSecrets: false, matches: [] };

      // Merge user-provided tags with defaultTags (deduplicated)
      const mergedTags = [...new Set([...defaultTags, ...flags.tags])];

      // Build meta object
      const meta: Record<string, unknown> = {};
      if (r.hadSecrets) {
        meta.redaction = { hadSecrets: true, matches: r.matches };
      }
      if (flags.project) {
        meta.project = flags.project;
      }

      const item: MemoryItem = {
        id: uuid(),
        kind: "doc",
        text: r.redactedText,
        createdAt: new Date().toISOString(),
        tags: mergedTags,
        source: {
          channel: ctx?.channel,
          from: ctx?.from,
          conversationId: ctx?.conversationId,
          messageId: ctx?.messageId,
        },
        meta: Object.keys(meta).length > 0 ? meta : undefined,
      };

      await store.add(item);

      const parts: string[] = ["Saved docs memory."];
      if (flags.tags.length > 0) parts.push(`Tags: ${mergedTags.join(", ")}.`);
      if (flags.project) parts.push(`Project: ${flags.project}.`);
      if (r.hadSecrets) parts.push("(note: secrets were redacted)");
      return { text: parts.join(" ") };
    },
  });

  // Command: /search-docs [--tags t1,t2] [--project name] <query> [limit]
  api.registerCommand({
    name: "search-docs",
    description: "Search documentation memory items by query",
    usage: "/search-docs [--tags t1,t2] [--project name] <query> [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const rawArgs = String(ctx?.args ?? "").trim();
      const flags = parseFlags(rawArgs);
      const words = flags.text.split(/\s+/).filter(Boolean);
      const lastWord = words[words.length - 1] ?? "";
      const maybeLimit = Number(lastWord);
      let query: string;
      let limit: number;
      if (!isNaN(maybeLimit) && maybeLimit >= 1 && words.length > 1) {
        limit = safeLimit(maybeLimit, 5, 20);
        query = words.slice(0, -1).join(" ");
      } else {
        limit = 5;
        query = words.join(" ");
      }
      if (!query) return { text: "Usage: /search-docs [--tags t1,t2] [--project name] <query> [limit]" };

      const searchOpts: { limit: number; tags?: string[] } = { limit };
      if (flags.tags.length > 0) searchOpts.tags = flags.tags;

      const hits = await store.search(query, searchOpts);

      // Post-filter by project if requested
      const filtered = flags.project
        ? hits.filter((h) => h.item.meta && (h.item.meta as Record<string, unknown>).project === flags.project)
        : hits;

      if (filtered.length === 0) return { text: `No docs memories found for: ${query}` };
      const lines = filtered.map((h, n) => {
        const shortId = h.item.id.length > 8 ? h.item.id.slice(0, 8) : h.item.id;
        const tagsBadge = formatTagsBadge(h.item.tags ?? [], defaultTags);
        const projBadge = formatProjectBadge(h.item.meta);
        return `${n + 1}. [id:${shortId}] [score:${h.score.toFixed(2)}]${tagsBadge}${projBadge} ${h.item.text.slice(0, 120)}${h.item.text.length > 120 ? "…" : ""}`;
      });
      return { text: `Docs memory results for "${query}":\n${lines.join("\n")}` };
    },
  });

  // Command: /list-docs [--tags t1,t2] [--project name] [limit]
  api.registerCommand({
    name: "list-docs",
    description: "List the most recent documentation memory items",
    usage: "/list-docs [--tags t1,t2] [--project name] [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const rawArgs = String(ctx?.args ?? "").trim();
      const flags = parseFlags(rawArgs);
      const limit = safeLimit(flags.text, 10, 50);

      const listOpts: { limit: number; tags?: string[] } = { limit };
      if (flags.tags.length > 0) listOpts.tags = flags.tags;

      const items = await store.list(listOpts);

      // Post-filter by project if requested
      const filtered = flags.project
        ? items.filter((i) => i.meta && (i.meta as Record<string, unknown>).project === flags.project)
        : items;

      if (filtered.length === 0) return { text: "No docs memories stored yet." };
      const lines = filtered.map((i, n) => {
        const shortId = i.id.length > 8 ? i.id.slice(0, 8) : i.id;
        const tagsBadge = formatTagsBadge(i.tags ?? [], defaultTags);
        const projBadge = formatProjectBadge(i.meta);
        return `${n + 1}. [id:${shortId}] [${i.createdAt.slice(0, 10)}]${tagsBadge}${projBadge} ${i.text.slice(0, 120)}${i.text.length > 120 ? "…" : ""}`;
      });
      return { text: `Docs memories (${filtered.length}):\n${lines.join("\n")}\n\nUse /forget-doc <id> to delete an item. Full IDs: ${filtered.map((i) => i.id).join(", ")}` };
    },
  });

  // Command: /forget-doc <id>
  api.registerCommand({
    name: "forget-doc",
    description: "Delete a documentation memory item by ID",
    usage: "/forget-doc <id>",
    requireAuth: true,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const id = String(ctx?.args ?? "").trim();
      if (!id) return { text: "Usage: /forget-doc <id>" };
      const deleted = await store.delete(id);
      return { text: deleted ? `Deleted docs memory: ${id}` : `No memory found with id: ${id}` };
    },
  });

  // Command: /export-docs [--tags t1,t2] [--project name] [path]
  api.registerCommand({
    name: "export-docs",
    description: "Export documentation memories as markdown files",
    usage: "/export-docs [--tags t1,t2] [--project name] [path]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const rawArgs = String(ctx?.args ?? "").trim();
      const flags = parseFlags(rawArgs);

      // Determine target directory
      let targetDir: string;
      try {
        const rawPath = flags.text || cfg.exportPath || "~/.openclaw/workspace/memory/docs-export";
        targetDir = safePath(expandHome(rawPath), "[memory-docs] export path");
      } catch (err: unknown) {
        return { text: `Invalid export path: ${(err as Error).message}` };
      }

      // Get items with optional filtering (no limit - export all)
      const listOpts: { tags?: string[] } = {};
      if (flags.tags.length > 0) listOpts.tags = flags.tags;

      const items = await store.list(listOpts);

      // Post-filter by project if requested
      const filtered = flags.project
        ? items.filter((i) => i.meta && (i.meta as Record<string, unknown>).project === flags.project)
        : items;

      if (filtered.length === 0) {
        return { text: "No docs memories to export." };
      }

      // Create output directory
      await mkdir(targetDir, { recursive: true });

      // Write each item as a markdown file
      let count = 0;
      for (const item of filtered) {
        const date = item.createdAt.slice(0, 10);
        const shortId = item.id.length > 8 ? item.id.slice(0, 8) : item.id;
        const filename = `${date}_${shortId}.md`;
        const content = formatAsMarkdown(item);
        await writeFile(join(targetDir, filename), content, "utf-8");
        count++;
      }

      return {
        text: `Exported ${count} memory item${count !== 1 ? "s" : ""} to ${targetDir}`,
      };
    },
  });

  // Command: /import-docs [path]
  api.registerCommand({
    name: "import-docs",
    description: "Import documentation memories from exported markdown files",
    usage: "/import-docs [path]",
    requireAuth: true,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const rawArgs = String(ctx?.args ?? "").trim();

      // Determine source directory
      let sourceDir: string;
      try {
        const rawPath = rawArgs || cfg.exportPath || "~/.openclaw/workspace/memory/docs-export";
        sourceDir = safePath(expandHome(rawPath), "[memory-docs] import path");
      } catch (err: unknown) {
        return { text: `Invalid import path: ${(err as Error).message}` };
      }

      // Read all .md files from the directory
      let files: string[];
      try {
        const entries = await readdir(sourceDir);
        files = entries.filter((f) => f.endsWith(".md")).sort();
      } catch (err: unknown) {
        const code = (err as NodeJS.ErrnoException).code;
        if (code === "ENOENT") {
          return { text: `Import directory not found: ${sourceDir}` };
        }
        return { text: `Failed to read import directory: ${(err as Error).message}` };
      }

      if (files.length === 0) {
        return { text: `No markdown files found in ${sourceDir}` };
      }

      let imported = 0;
      let skipped = 0;

      for (const file of files) {
        const content = await readFile(join(sourceDir, file), "utf-8");
        const item = parseMarkdownToItem(content);
        if (!item) {
          skipped++;
          continue;
        }

        // Check if item already exists (by ID) to avoid duplicates
        const existing = await store.get(item.id);
        if (existing) {
          skipped++;
          continue;
        }

        await store.add(item);
        imported++;
      }

      const parts: string[] = [`Imported ${imported} memory item${imported !== 1 ? "s" : ""} from ${sourceDir}.`];
      if (skipped > 0) parts.push(`Skipped ${skipped} (duplicate or invalid).`);
      return { text: parts.join(" ") };
    },
  });

  // Tool: docs_memory_search
  api.registerTool({
    name: "docs_memory_search",
    description: "Search documentation memory items (local JSONL store)",
    parameters: {
      type: "object",
      additionalProperties: false,
      properties: {
        query: { type: "string" },
        limit: { type: "number", minimum: 1, maximum: 20, default: 5 },
        tags: { type: "array", items: { type: "string" }, description: "Filter results to items matching all given tags" },
        project: { type: "string", description: "Filter results to items with this project name" },
      },
      required: ["query"],
    },
    async execute(params: ToolCallParams) {
      const q = String(params['query'] ?? "").trim();
      const limit = safeLimit(params['limit'], 5, 20);
      if (!q) return { hits: [] };

      const searchOpts: { limit: number; tags?: string[] } = { limit };
      const paramTags = params['tags'];
      if (Array.isArray(paramTags) && paramTags.length > 0) {
        searchOpts.tags = paramTags.map(String);
      }

      const hits = await store.search(q, searchOpts);

      // Post-filter by project if requested
      const paramProject = typeof params['project'] === "string" ? params['project'] : undefined;
      const filtered = paramProject
        ? hits.filter((h) => h.item.meta && (h.item.meta as Record<string, unknown>).project === paramProject)
        : hits;

      return {
        hits: filtered.map((h) => ({
          score: h.score,
          id: h.item.id,
          createdAt: h.item.createdAt,
          tags: h.item.tags,
          project: h.item.meta && typeof (h.item.meta as Record<string, unknown>).project === "string"
            ? (h.item.meta as Record<string, unknown>).project
            : undefined,
          text: h.item.text,
        })),
      };
    },
  });
}
