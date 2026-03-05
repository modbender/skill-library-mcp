import fs from "node:fs";
import fsPromises from "node:fs/promises";
import path from "node:path";
import type { Embedder, ListOpts, MemoryItem, MemoryKind, MemoryStore, SearchHit, SearchOpts } from "./types.js";
import { cosine } from "./embedding.js";

const VALID_KINDS = new Set<string>(["fact", "decision", "doc", "note"]);

type RecordLine = {
  item: MemoryItem;
  embedding?: number[];
};

/** Loose guard: ensure required MemoryItem fields are present, types are correct, and kind is valid. */
function isValidMemoryItem(x: unknown): x is MemoryItem {
  if (!x || typeof x !== "object") return false;
  const o = x as Record<string, unknown>;
  return (
    typeof o["id"] === "string" &&
    typeof o["kind"] === "string" &&
    VALID_KINDS.has(o["kind"]) &&
    typeof o["text"] === "string" &&
    typeof o["createdAt"] === "string"
  );
}

/** Returns true if the item has an expiresAt in the past. */
function isExpired(item: MemoryItem, now: string): boolean {
  return item.expiresAt !== undefined && item.expiresAt <= now;
}

function matchesFilter(item: MemoryItem, kind?: MemoryKind, tags?: string[], includeExpired?: boolean, now?: string): boolean {
  if (!includeExpired && now && isExpired(item, now)) return false;
  if (kind && item.kind !== kind) return false;
  if (tags && tags.length > 0) {
    const itemTags = item.tags ?? [];
    if (!tags.every((t) => itemTags.includes(t))) return false;
  }
  return true;
}

export class JsonlMemoryStore implements MemoryStore {
  private filePath: string;
  private embedder: Embedder;
  private maxItems: number;
  /** Serialises all write operations to prevent concurrent read-modify-write races. */
  private _writeLock: Promise<void> = Promise.resolve();
  /** In-memory cache; null means not yet loaded. Invalidated on every write. */
  private _cache: RecordLine[] | null = null;

  constructor(opts: { filePath: string; embedder: Embedder; maxItems?: number }) {
    this.filePath = opts.filePath;
    this.embedder = opts.embedder;
    this.maxItems = opts.maxItems ?? 5000;
    fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
    if (!fs.existsSync(this.filePath)) fs.writeFileSync(this.filePath, "", "utf-8");
  }

  async add(item: MemoryItem): Promise<void> {
    if (!VALID_KINDS.has(item.kind)) {
      throw new TypeError(`[JsonlMemoryStore] Invalid kind "${item.kind}". Expected one of: ${[...VALID_KINDS].join(", ")}`);
    }
    return this._enqueue(async () => {
      const embedding = await this.embedder.embed(item.text);
      const line: RecordLine = { item, embedding };
      const records = await this._readAll();
      records.push(line);
      if (records.length > this.maxItems) {
        // Over capacity - must rewrite the whole file to trim old entries.
        const trimmed = records.slice(records.length - this.maxItems);
        await this._writeAll(trimmed);
      } else {
        // Under capacity - append a single line instead of rewriting everything.
        await this._appendLines([line]);
      }
    });
  }

  async addMany(items: MemoryItem[]): Promise<void> {
    if (items.length === 0) return;
    for (const it of items) {
      if (!VALID_KINDS.has(it.kind)) {
        throw new TypeError(`[JsonlMemoryStore] Invalid kind "${it.kind}". Expected one of: ${[...VALID_KINDS].join(", ")}`);
      }
    }
    return this._enqueue(async () => {
      const newRecords: RecordLine[] = await Promise.all(
        items.map(async (it) => {
          const embedding = await this.embedder.embed(it.text);
          return { item: it, embedding } as RecordLine;
        })
      );
      const records = await this._readAll();
      records.push(...newRecords);
      if (records.length > this.maxItems) {
        const trimmed = records.slice(records.length - this.maxItems);
        await this._writeAll(trimmed);
      } else {
        // Append all new lines in a single write - no full rewrite needed.
        await this._appendLines(newRecords);
      }
    });
  }

  async get(id: string): Promise<MemoryItem | undefined> {
    const records = await this._readAll();
    const record = records.find((r) => r.item.id === id);
    if (!record) return undefined;
    if (isExpired(record.item, new Date().toISOString())) return undefined;
    return record.item;
  }

  async update(id: string, partial: Partial<Omit<MemoryItem, "id">>): Promise<MemoryItem | undefined> {
    return this._enqueue(async () => {
      const records = await this._readAll();
      const idx = records.findIndex((r) => r.item.id === id);
      if (idx === -1) return undefined;

      const existing = records[idx]!;
      const merged: MemoryItem = { ...existing.item, ...partial, id }; // id is immutable

      // Validate kind if it was changed
      if (partial.kind !== undefined && !VALID_KINDS.has(partial.kind)) {
        throw new TypeError(
          `[JsonlMemoryStore] Invalid kind "${partial.kind}". Expected one of: ${[...VALID_KINDS].join(", ")}`
        );
      }

      // Re-embed only when the text content changed
      const needsReEmbed = partial.text !== undefined && partial.text !== existing.item.text;
      const embedding = needsReEmbed ? await this.embedder.embed(merged.text) : existing.embedding;

      records[idx] = { item: merged, embedding };
      await this._writeAll(records);
      return merged;
    });
  }

  async delete(id: string): Promise<boolean> {
    return this._enqueue(async () => {
      const records = await this._readAll();
      const filtered = records.filter((r) => r.item.id !== id);
      if (filtered.length === records.length) return false;
      await this._writeAll(filtered);
      return true;
    });
  }

  async list(opts?: ListOpts): Promise<MemoryItem[]> {
    const records = await this._readAll();
    const now = new Date().toISOString();
    const includeExpired = opts?.includeExpired ?? false;
    const filtered = records.filter((r) => matchesFilter(r.item, opts?.kind, opts?.tags, includeExpired, now));
    const lim = opts?.limit ? Math.max(1, opts.limit) : filtered.length;
    return filtered.slice(-lim).map((r) => r.item);
  }

  async search(query: string, opts?: SearchOpts): Promise<SearchHit[]> {
    const q = await this.embedder.embed(query);
    const records = await this._readAll();
    const now = new Date().toISOString();
    const includeExpired = opts?.includeExpired ?? false;
    const hits: SearchHit[] = [];

    for (const r of records) {
      if (!r.embedding) continue;
      if (!matchesFilter(r.item, opts?.kind, opts?.tags, includeExpired, now)) continue;
      hits.push({ item: r.item, score: clamp01((cosine(q, r.embedding) + 1) / 2) });
    }

    hits.sort((a, b) => b.score - a.score);
    const limit = Math.max(1, Math.trunc(opts?.limit ?? 10));
    return hits.slice(0, limit);
  }

  async purgeExpired(): Promise<number> {
    return this._enqueue(async () => {
      const records = await this._readAll();
      const now = new Date().toISOString();
      const kept = records.filter((r) => !isExpired(r.item, now));
      const purged = records.length - kept.length;
      if (purged > 0) await this._writeAll(kept);
      return purged;
    });
  }

  /** Queue a write-side operation so concurrent callers never interleave. */
  private _enqueue<T>(fn: () => Promise<T>): Promise<T> {
    const next = this._writeLock.then(fn, fn) as Promise<T>;
    this._writeLock = (next as Promise<unknown>).then(() => {}, () => {});
    return next;
  }

  /** Read and parse all valid records from the JSONL file, with in-memory caching. */
  private async _readAll(): Promise<RecordLine[]> {
    if (this._cache !== null) return this._cache;
    try {
      const raw = await fsPromises.readFile(this.filePath, "utf-8");
      const out: RecordLine[] = [];
      for (const ln of raw.split("\n")) {
        if (!ln.trim()) continue;
        try {
          const parsed = JSON.parse(ln) as unknown;
          if (
            parsed !== null &&
            typeof parsed === "object" &&
            isValidMemoryItem((parsed as Record<string, unknown>)["item"])
          ) {
            out.push(parsed as RecordLine);
          }
        } catch {
          // skip malformed lines
        }
      }
      this._cache = out;
      return out;
    } catch (err: unknown) {
      // Only suppress "file not found" - rethrow real I/O errors.
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        this._cache = [];
        return [];
      }
      throw err;
    }
  }

  /** Append one or more JSONL lines to the file without rewriting the whole thing. */
  private async _appendLines(lines: RecordLine[]): Promise<void> {
    const data = lines.map((r) => JSON.stringify(r)).join("\n") + "\n";
    await fsPromises.appendFile(this.filePath, data, "utf-8");
    // Cache is already up-to-date because the caller pushed into _readAll()'s array.
  }

  /** Atomically write records to the JSONL file (tmp -> rename), then refresh cache. */
  private async _writeAll(records: RecordLine[]): Promise<void> {
    const dir = path.dirname(this.filePath);
    const tmp = path.join(dir, `.${path.basename(this.filePath)}.tmp`);
    const content = records.map((r) => JSON.stringify(r)).join("\n") + (records.length > 0 ? "\n" : "");
    await fsPromises.writeFile(tmp, content, { encoding: "utf-8", flag: "w" });
    await fsPromises.rename(tmp, this.filePath);
    // Update cache in-place so subsequent reads don't hit disk.
    this._cache = records;
  }
}

function clamp01(x: number): number {
  return Math.max(0, Math.min(1, x));
}
