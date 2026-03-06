import fs from "node:fs";
import path from "node:path";
import os from "node:os";

import { HashEmbedder, JsonlMemoryStore, uuid, type MemoryItem } from "@elvatis_com/openclaw-memory-core";

export function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return p;
}

const DEFAULT_TODO_TEMPLATE = `# TODO

- [ ] My first task
`;

function ensureTodoFile(filePath: string): void {
  if (fs.existsSync(filePath)) return;
  const dir = path.dirname(filePath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, DEFAULT_TODO_TEMPLATE, "utf-8");
}

function readTodoFile(filePath: string): string {
  ensureTodoFile(filePath);
  return fs.readFileSync(filePath, "utf-8");
}

export type Priority = "high" | "medium" | "low";

export type TodoItem = {
  lineNo: number;
  raw: string;
  done: boolean;
  text: string;
  tags: string[];
  priority: Priority | null;
  dueDate: string | null;
};

const PRIORITY_RE = /\s*!(high|medium|low)\b/gi;
const TAG_RE = /#([\w-]+)/g;
const DUE_DATE_RE = /@due\((\d{4}-\d{2}-\d{2})\)/i;

export function extractTags(text: string): string[] {
  const tags: string[] = [];
  let m: RegExpExecArray | null;
  TAG_RE.lastIndex = 0;
  while ((m = TAG_RE.exec(text)) !== null) {
    const tag = m[1].toLowerCase();
    if (!tags.includes(tag)) tags.push(tag);
  }
  return tags;
}

export function extractPriority(text: string): Priority | null {
  PRIORITY_RE.lastIndex = 0;
  const m = PRIORITY_RE.exec(text);
  return m ? (m[1].toLowerCase() as Priority) : null;
}

export function extractDueDate(text: string): string | null {
  DUE_DATE_RE.lastIndex = 0;
  const m = DUE_DATE_RE.exec(text);
  return m ? m[1] : null;
}

export function isOverdue(dueDate: string, today?: string): boolean {
  const ref = today ?? new Date().toISOString().slice(0, 10);
  return dueDate < ref;
}

export function isDueToday(dueDate: string, today?: string): boolean {
  const ref = today ?? new Date().toISOString().slice(0, 10);
  return dueDate === ref;
}

export function cleanText(text: string): string {
  return text
    .replace(PRIORITY_RE, "")
    .replace(TAG_RE, "")
    .replace(DUE_DATE_RE, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

export function parseTodos(md: string): TodoItem[] {
  const lines = md.split("\n");
  const out: TodoItem[] = [];
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    const m = ln.match(/^\s*-\s*\[( |x)\]\s*(.+)$/i);
    if (!m) continue;
    const done = m[1].toLowerCase() === "x";
    const text = m[2].trim();
    out.push({
      lineNo: i,
      raw: ln,
      done,
      text,
      tags: extractTags(text),
      priority: extractPriority(text),
      dueDate: extractDueDate(text),
    });
  }
  return out;
}

export function sortByDueDate(items: TodoItem[], today?: string): TodoItem[] {
  const ref = today ?? new Date().toISOString().slice(0, 10);
  return [...items].sort((a, b) => {
    // Overdue items first, then due today, then future due dates, then no due date
    const aScore = a.dueDate ? (a.dueDate < ref ? 0 : a.dueDate === ref ? 1 : 2) : 3;
    const bScore = b.dueDate ? (b.dueDate < ref ? 0 : b.dueDate === ref ? 1 : 2) : 3;
    if (aScore !== bScore) return aScore - bScore;
    // Within the same category, sort by date ascending (earliest first)
    if (a.dueDate && b.dueDate) return a.dueDate.localeCompare(b.dueDate);
    return 0;
  });
}

export function markDone(md: string, item: TodoItem): string {
  const lines = md.split("\n");
  const ln = lines[item.lineNo];
  lines[item.lineNo] = ln.replace(/^\s*-\s*\[ \]/, "- [x]");
  return lines.join("\n");
}

export function editTodo(md: string, item: TodoItem, newText: string): string {
  const lines = md.split("\n");
  lines[item.lineNo] = lines[item.lineNo].replace(/^(\s*-\s*\[[ xX]\]\s*).*$/, `$1${newText}`);
  return lines.join("\n");
}

export function removeTodo(md: string, item: TodoItem): string {
  const lines = md.split("\n");
  lines.splice(item.lineNo, 1);
  return lines.join("\n");
}

export function searchTodos(items: TodoItem[], query: string, today?: string): TodoItem[] {
  const parts = query.trim().split(/\s+/);
  const tagFilters: string[] = [];
  const priorityFilters: Priority[] = [];
  const textParts: string[] = [];
  let dueFilter: "overdue" | "today" | "upcoming" | null = null;

  for (const p of parts) {
    if (/^#[\w-]+$/.test(p)) {
      tagFilters.push(p.slice(1).toLowerCase());
    } else if (/^!(high|medium|low)$/i.test(p)) {
      priorityFilters.push(p.slice(1).toLowerCase() as Priority);
    } else if (/^@due$/i.test(p)) {
      // @due alone means "has any due date"
      dueFilter = "upcoming";
    } else if (/^@overdue$/i.test(p)) {
      dueFilter = "overdue";
    } else if (/^@today$/i.test(p)) {
      dueFilter = "today";
    } else {
      textParts.push(p);
    }
  }

  const textQuery = textParts.join(" ").toLowerCase();
  const ref = today ?? new Date().toISOString().slice(0, 10);

  return items.filter((item) => {
    if (tagFilters.length > 0 && !tagFilters.every((tf) => item.tags.includes(tf))) return false;
    if (priorityFilters.length > 0 && (!item.priority || !priorityFilters.includes(item.priority))) return false;
    if (textQuery && !item.text.toLowerCase().includes(textQuery)) return false;
    if (dueFilter === "overdue" && (!item.dueDate || item.dueDate >= ref)) return false;
    if (dueFilter === "today" && (!item.dueDate || item.dueDate !== ref)) return false;
    if (dueFilter === "upcoming" && !item.dueDate) return false;
    return true;
  });
}

export function addTodo(md: string, text: string, sectionHeader?: string): string {
  const lines = md.split("\n");
  const bullet = `- [ ] ${text}`;

  let insertAt = -1;

  if (sectionHeader) {
    // Insert under the configured section header if found
    const needle = sectionHeader.toLowerCase();
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes(needle)) {
        insertAt = i + 1;
        break;
      }
    }
  }

  if (insertAt === -1) {
    // Fallback: append after the last existing todo item, or at end of file
    for (let i = lines.length - 1; i >= 0; i--) {
      if (/^\s*-\s*\[[ x]\]/i.test(lines[i])) {
        insertAt = i + 1;
        break;
      }
    }
  }

  if (insertAt === -1) {
    lines.push(bullet);
    return lines.join("\n");
  }

  // Skip blank lines after the header
  while (insertAt < lines.length && lines[insertAt].trim() === "") insertAt++;
  lines.splice(insertAt, 0, bullet);
  return lines.join("\n");
}

function formatTodoLine(t: TodoItem, idx: number, today: string): string {
  const pri = t.priority ? `[${t.priority.toUpperCase()}] ` : "";
  let dueLabel = "";
  if (t.dueDate) {
    if (t.dueDate < today) dueLabel = `(OVERDUE: ${t.dueDate}) `;
    else if (t.dueDate === today) dueLabel = `(Due today) `;
    else dueLabel = `(Due: ${t.dueDate}) `;
  }
  return `${idx + 1}. ${pri}${dueLabel}${t.text}`;
}

async function brainLog(storePath: string, text: string): Promise<void> {
  const embedder = new HashEmbedder(256);
  const store = new JsonlMemoryStore({ filePath: storePath, embedder });
  const item: MemoryItem = {
    id: uuid(),
    kind: "note",
    text: `TODO: ${text}`,
    createdAt: new Date().toISOString(),
    tags: ["todo"],
  };
  await store.add(item);
}

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    todoFile?: string;
    brainLog?: boolean;
    brainStorePath?: string;
    maxListItems?: number;
    sectionHeader?: string;
  };

  if (cfg.enabled === false) return;

  const todoFile = expandHome(cfg.todoFile ?? "~/.openclaw/workspace/TODO.md");
  const doBrainLog = cfg.brainLog !== false;
  const brainStorePath = expandHome(cfg.brainStorePath ?? "~/.openclaw/workspace/memory/brain-memory.jsonl");
  const maxListItems = cfg.maxListItems ?? 30;
  const sectionHeader = cfg.sectionHeader;

  ensureTodoFile(todoFile);
  api.logger?.info?.(`[todo] enabled. file=${todoFile}`);

  api.registerCommand({
    name: "todo-list",
    description: "List open TODO items (overdue items shown first)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const today = new Date().toISOString().slice(0, 10);
      const md = readTodoFile(todoFile);
      const todos = parseTodos(md).filter((t) => !t.done);
      const sorted = sortByDueDate(todos, today);
      const top = sorted.slice(0, maxListItems);
      if (top.length === 0) return { text: "No open TODOs." };
      const lines = top.map((t, idx) => formatTodoLine(t, idx, today));
      return { text: `Open TODOs (${todos.length}):\n` + lines.join("\n") };
    },
  });

  api.registerCommand({
    name: "todo-add",
    description: "Add a TODO item (supports @due(YYYY-MM-DD), #tag, !priority)",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const text = String(ctx?.args ?? "").trim();
      if (!text) return { text: "Usage: /todo-add <text> (supports @due(YYYY-MM-DD), #tag, !priority)" };

      const md = readTodoFile(todoFile);
      const next = addTodo(md, text, sectionHeader);
      fs.writeFileSync(todoFile, next, "utf-8");

      if (doBrainLog) await brainLog(brainStorePath, `added - ${text}`);
      return { text: `Added TODO: ${text}` };
    },
  });

  api.registerCommand({
    name: "todo-done",
    description: "Mark a TODO item done",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const idxStr = String(ctx?.args ?? "").trim();
      const idx = Number(idxStr);
      if (!idxStr || !Number.isFinite(idx) || idx < 1) {
        return { text: "Usage: /todo-done <index> (see /todo-list)" };
      }

      const md = readTodoFile(todoFile);
      const open = parseTodos(md).filter((t) => !t.done);
      const item = open[idx - 1];
      if (!item) return { text: `No open TODO at index ${idx}.` };

      const next = markDone(md, item);
      fs.writeFileSync(todoFile, next, "utf-8");

      if (doBrainLog) await brainLog(brainStorePath, `done - ${item.text}`);
      return { text: `Done: ${item.text}` };
    },
  });

  api.registerCommand({
    name: "todo-edit",
    description: "Edit a TODO item's text",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const raw = String(ctx?.args ?? "").trim();
      const spaceIdx = raw.indexOf(" ");
      if (!raw || spaceIdx === -1) {
        return { text: "Usage: /todo-edit <index> <new text> (see /todo-list)" };
      }

      const idx = Number(raw.slice(0, spaceIdx));
      const newText = raw.slice(spaceIdx + 1).trim();
      if (!Number.isFinite(idx) || idx < 1 || !newText) {
        return { text: "Usage: /todo-edit <index> <new text> (see /todo-list)" };
      }

      const md = readTodoFile(todoFile);
      const open = parseTodos(md).filter((t) => !t.done);
      const item = open[idx - 1];
      if (!item) return { text: `No open TODO at index ${idx}.` };

      const oldText = item.text;
      const next = editTodo(md, item, newText);
      fs.writeFileSync(todoFile, next, "utf-8");

      if (doBrainLog) await brainLog(brainStorePath, `edited - "${oldText}" -> "${newText}"`);
      return { text: `Edited TODO #${idx}: "${oldText}" -> "${newText}"` };
    },
  });

  api.registerCommand({
    name: "todo-remove",
    description: "Remove a TODO item",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const idxStr = String(ctx?.args ?? "").trim();
      const idx = Number(idxStr);
      if (!idxStr || !Number.isFinite(idx) || idx < 1) {
        return { text: "Usage: /todo-remove <index> (see /todo-list)" };
      }

      const md = readTodoFile(todoFile);
      const open = parseTodos(md).filter((t) => !t.done);
      const item = open[idx - 1];
      if (!item) return { text: `No open TODO at index ${idx}.` };

      const next = removeTodo(md, item);
      fs.writeFileSync(todoFile, next, "utf-8");

      if (doBrainLog) await brainLog(brainStorePath, `removed - ${item.text}`);
      return { text: `Removed TODO: ${item.text}` };
    },
  });

  api.registerCommand({
    name: "todo-search",
    description: "Search TODO items by text, #tag, !priority, @due, @overdue, or @today",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const query = String(ctx?.args ?? "").trim();
      if (!query) return { text: "Usage: /todo-search <query> (supports text, #tag, !priority, @due, @overdue, @today)" };

      const today = new Date().toISOString().slice(0, 10);
      const md = readTodoFile(todoFile);
      const open = parseTodos(md).filter((t) => !t.done);
      const matches = searchTodos(open, query, today);
      if (matches.length === 0) return { text: `No open TODOs matching "${query}".` };

      const sorted = sortByDueDate(matches, today);
      const lines = sorted.slice(0, maxListItems).map((t, idx) => formatTodoLine(t, idx, today));
      return { text: `Search results for "${query}" (${matches.length}):\n` + lines.join("\n") };
    },
  });

  // Tool: todo_status
  api.registerTool({
    name: "todo_status",
    description: "Return structured TODO status from TODO.md",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        limit: { type: "number", minimum: 1, maximum: 200, default: 50 },
        overdue: { type: "boolean", description: "If true, return only overdue items" },
      },
    },
    handler: async (params: any) => {
      const limit = Number(params?.limit ?? 50);
      const filterOverdue = params?.overdue === true;
      const today = new Date().toISOString().slice(0, 10);
      const md = readTodoFile(todoFile);
      const all = parseTodos(md);
      let open = all.filter((t) => !t.done);
      if (filterOverdue) {
        open = open.filter((t) => t.dueDate && t.dueDate < today);
      }
      const done = all.filter((t) => t.done);
      const allTags = [...new Set(open.flatMap((t) => t.tags))].sort();
      const overdueCount = all.filter((t) => !t.done && t.dueDate && t.dueDate < today).length;
      return {
        todoFile,
        openCount: open.length,
        doneCount: done.length,
        overdueCount,
        open: sortByDueDate(open, today).slice(0, limit).map((t) => ({
          text: t.text,
          tags: t.tags,
          priority: t.priority,
          dueDate: t.dueDate,
          overdue: t.dueDate ? t.dueDate < today : false,
        })),
        tags: allTags,
      };
    },
  });
}
