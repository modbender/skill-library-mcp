# @elvatis_com/openclaw-memory-core

Core utilities for building OpenClaw memory plugins - redaction, embeddings, and JSONL-backed vector search.

## Installation

```bash
npm install @elvatis_com/openclaw-memory-core
```

Requires Node.js 18+.

## Quick start

```ts
import {
  JsonlMemoryStore,
  createEmbedder,
  DefaultRedactor,
  uuid,
} from "@elvatis_com/openclaw-memory-core";

// 1. Set up the store
const embedder = createEmbedder();
const store = new JsonlMemoryStore({
  filePath: "./data/memories.jsonl",
  embedder,
});

// 2. Redact secrets before storing
const redactor = new DefaultRedactor();
const { redactedText } = redactor.redact("My API key is sk-proj-abc123def456ghi789");

// 3. Store a memory
await store.add({
  id: uuid(),
  kind: "note",
  text: redactedText,
  createdAt: new Date().toISOString(),
  tags: ["api", "credentials"],
});

// 4. Search by natural language
const results = await store.search("API key");
console.log(results[0]?.item.text);
// => "My API key is [REDACTED:OPENAI_KEY]"
```

## API reference

All exports are available from the package root:

```ts
import { /* any export */ } from "@elvatis_com/openclaw-memory-core";
```

---

### Types

#### `MemoryKind`

```ts
type MemoryKind = "fact" | "decision" | "doc" | "note";
```

The four supported item categories.

#### `MemoryItem`

```ts
interface MemoryItem {
  id: string;
  kind: MemoryKind;
  text: string;
  createdAt: string;          // ISO 8601
  expiresAt?: string;         // ISO 8601 - optional TTL
  source?: {
    channel?: string;
    from?: string;
    conversationId?: string;
    messageId?: string;
  };
  tags?: string[];
  meta?: Record<string, unknown>;
}
```

The fundamental data unit stored by a `MemoryStore`.

#### `SearchHit`

```ts
interface SearchHit {
  item: MemoryItem;
  score: number;  // 0..1 (1 = best match)
}
```

Returned by `store.search()`. Results are sorted by score descending.

#### `SearchOpts`

```ts
interface SearchOpts {
  limit?: number;            // max results (default: 10)
  kind?: MemoryKind;         // filter by kind
  tags?: string[];           // filter: item must have ALL listed tags
  includeExpired?: boolean;  // include expired items (default: false)
}
```

#### `ListOpts`

```ts
interface ListOpts {
  limit?: number;            // max results (returns most recent)
  kind?: MemoryKind;
  tags?: string[];
  includeExpired?: boolean;
}
```

#### `RedactionResult`

```ts
interface RedactionResult {
  redactedText: string;
  hadSecrets: boolean;
  matches: Array<{ rule: string; count: number }>;
}
```

`matches` stores only which rule fired and how many times - never the actual secret text.

#### `Embedder`

```ts
interface Embedder {
  embed(text: string): Promise<number[]>;
  dims: number;
  id: string;
}
```

Pluggable embedding backend. Implement this interface to swap in OpenAI, Cohere, or any other provider.

#### `EmbedderOptions`

```ts
interface EmbedderOptions {
  custom?: Embedder;  // supply a custom embedder
  dims?: number;      // HashEmbedder dimensions (default: 256, ignored when custom is set)
}
```

#### `MemoryStore`

```ts
interface MemoryStore {
  add(item: MemoryItem): Promise<void>;
  addMany(items: MemoryItem[]): Promise<void>;
  get(id: string): Promise<MemoryItem | undefined>;
  update(id: string, partial: Partial<Omit<MemoryItem, "id">>): Promise<MemoryItem | undefined>;
  delete(id: string): Promise<boolean>;
  search(query: string, opts?: SearchOpts): Promise<SearchHit[]>;
  list(opts?: ListOpts): Promise<MemoryItem[]>;
  purgeExpired(): Promise<number>;
}
```

The store contract. `JsonlMemoryStore` is the built-in implementation.

---

### Classes

#### `JsonlMemoryStore`

JSONL-backed memory store with vector search. All writes are serialized to prevent data races.

```ts
const store = new JsonlMemoryStore({
  filePath: string;       // path to the .jsonl file (created if missing)
  embedder: Embedder;     // embedding backend
  maxItems?: number;      // cap on stored items (default: 5000, oldest trimmed)
});
```

**Methods:**

| Method | Description |
|--------|-------------|
| `add(item)` | Store a new memory item. Uses append-optimized writes when under capacity (no full rewrite). Throws `TypeError` if `kind` is invalid. |
| `addMany(items)` | Store multiple items in a single operation. Embeddings are computed in parallel, and all items are appended in one write. More efficient than calling `add()` in a loop. Throws `TypeError` if any item has an invalid `kind`. No-op for empty arrays. |
| `get(id)` | Retrieve an item by ID. Returns `undefined` if not found or expired. |
| `update(id, partial)` | Merge partial fields into an existing item. Re-embeds automatically when `text` changes. Returns the updated item or `undefined`. |
| `delete(id)` | Remove an item. Returns `true` if it existed. |
| `search(query, opts?)` | Vector similarity search. Returns `SearchHit[]` sorted by score. |
| `list(opts?)` | List items (most recent last). Supports filtering by kind, tags, and expiry. |
| `purgeExpired()` | Physically remove all expired items from storage. Returns the count of purged items. |

**Example - full CRUD cycle:**

```ts
import { JsonlMemoryStore, createEmbedder, uuid } from "@elvatis_com/openclaw-memory-core";

const store = new JsonlMemoryStore({
  filePath: "./data/memories.jsonl",
  embedder: createEmbedder(),
});

const id = uuid();

// Create
await store.add({
  id,
  kind: "fact",
  text: "TypeScript 5.6 added iterator helpers",
  createdAt: new Date().toISOString(),
  tags: ["typescript"],
});

// Read
const item = await store.get(id);
console.log(item?.text); // "TypeScript 5.6 added iterator helpers"

// Update
const updated = await store.update(id, {
  text: "TypeScript 5.6 added iterator helpers and --noUncheckedSideEffectImports",
  tags: ["typescript", "compiler"],
});
console.log(updated?.tags); // ["typescript", "compiler"]

// Search
const hits = await store.search("iterator helpers");
console.log(hits[0]?.score); // ~0.85

// Delete
const deleted = await store.delete(id);
console.log(deleted); // true
```

**Example - bulk insert with `addMany()`:**

```ts
import { JsonlMemoryStore, createEmbedder, uuid } from "@elvatis_com/openclaw-memory-core";

const store = new JsonlMemoryStore({
  filePath: "./data/memories.jsonl",
  embedder: createEmbedder(),
});

// Insert many items in one efficient operation
await store.addMany([
  { id: uuid(), kind: "fact", text: "Node 22 is LTS", createdAt: new Date().toISOString() },
  { id: uuid(), kind: "fact", text: "Bun supports workspaces", createdAt: new Date().toISOString() },
  { id: uuid(), kind: "doc", text: "Vitest v2 migration guide", createdAt: new Date().toISOString(), tags: ["testing"] },
]);

// All items are immediately searchable
const hits = await store.search("Vitest migration");
console.log(hits[0]?.item.text); // "Vitest v2 migration guide"
```

#### `DefaultRedactor`

Strips secrets and tokens from text before storage. Covers 20+ patterns including API keys (OpenAI, Anthropic, Stripe, GitHub, Google, AWS, Azure), JWTs, private key blocks, bearer tokens, database connection strings, and more.

```ts
const redactor = new DefaultRedactor();
const result = redactor.redact(text);
```

Returns a `RedactionResult` with the cleaned text, a boolean indicating whether secrets were found, and a summary of which rules matched (without exposing the actual secrets).

**Supported secret patterns:**

| Rule ID | Detects |
|---------|---------|
| `openai_api_key` | `sk-...`, `sk-proj-...`, `sk-svcacct-...` |
| `anthropic_api_key` | `sk-ant-api03-...` |
| `stripe_api_key` | `sk_live_...`, `sk_test_...` |
| `github_pat` | `github_pat_...` |
| `github_token` | `ghp_...`, `gho_...`, `ghu_...`, `ghs_...` |
| `google_api_key` | `AIzaSy...` |
| `aws_access_key` | `AKIA...` |
| `aws_secret_key` | `AWS_SECRET_ACCESS_KEY=...` |
| `azure_storage_key` | `AccountKey=...` |
| `jwt_token` | Three-segment base64url tokens |
| `private_key_block` | PEM private key blocks |
| `bearer_token` | `Bearer ...` |
| `vault_token` | `hvs....` (HashiCorp Vault) |
| `npm_token` | `npm_...` |
| `slack_token` | `xoxb-...`, `xoxp-...`, etc. |
| `sendgrid_api_key` | `SG....` |
| `twilio_sid` | `AC` + 32 hex chars |
| `generic_password` | `password=...`, `secret=...` patterns |
| `huggingface_token` | `hf_...` |
| `telegram_bot_token` | Bot ID + token format |
| `db_connection_string` | `mongodb://`, `postgres://`, `mysql://`, `redis://` with credentials |

**Example:**

```ts
const redactor = new DefaultRedactor();

const input = "Connect to postgres://admin:s3cret@db.host:5432/mydb";
const { redactedText, hadSecrets, matches } = redactor.redact(input);

console.log(redactedText);  // "Connect to [REDACTED:DB_CONN_STRING]"
console.log(hadSecrets);    // true
console.log(matches);       // [{ rule: "db_connection_string", count: 1 }]
```

#### `HashEmbedder`

Deterministic, local, zero-dependency embedder using FNV-1a hashing. Not state-of-the-art semantics, but stable and safe for offline vector search.

```ts
const embedder = new HashEmbedder(dims?); // default: 256 dimensions
const vector = await embedder.embed("some text");
```

---

### Functions

#### `createEmbedder(opts?)`

Factory that returns an `Embedder`. Uses `HashEmbedder` by default, or pass a custom implementation.

```ts
// Default (local, deterministic, 256 dims)
const embedder = createEmbedder();

// Custom dimensions
const embedder = createEmbedder({ dims: 512 });

// Custom provider
const embedder = createEmbedder({ custom: myOpenAIEmbedder });
```

#### `cosine(a, b)`

Compute cosine similarity between two vectors. Returns a value from -1 to 1.

```ts
const similarity = cosine(vectorA, vectorB);
```

#### `uuid()`

Generate a v4 UUID using `crypto.randomUUID()` with a `crypto.getRandomValues()` fallback.

```ts
const id = uuid(); // "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
```

#### `ttlMs(ms)`

Return an ISO 8601 timestamp `ms` milliseconds from now. Useful for setting `MemoryItem.expiresAt`.

```ts
const oneHour = ttlMs(60 * 60 * 1000);   // 1 hour from now
const oneDay  = ttlMs(24 * 60 * 60 * 1000); // 1 day from now
```

#### `expandHome(path)`

Expand a leading `~` to the user's home directory.

```ts
expandHome("~/data/memories.jsonl");
// => "/home/user/data/memories.jsonl"
```

#### `safePath(path, label?)`

Resolve a path and verify it stays inside the user's home directory. Throws on path traversal attempts. Case-insensitive on Windows.

```ts
safePath("~/data/store.jsonl"); // OK - returns resolved absolute path
safePath("/etc/passwd");        // throws Error
```

#### `safeLimit(val, dflt, max)`

Clamp an untrusted number to `[1, max]`, returning `dflt` when the input is invalid.

```ts
safeLimit(50, 10, 100);    // 50
safeLimit(-1, 10, 100);    // 10
safeLimit(999, 10, 100);   // 100
safeLimit("abc", 10, 100); // 10
```

---

### TTL / Expiry

Set `expiresAt` (ISO 8601 string) on any `MemoryItem` to make it auto-expire:

```ts
import { ttlMs, uuid } from "@elvatis_com/openclaw-memory-core";

await store.add({
  id: uuid(),
  kind: "note",
  text: "Remember this for 1 hour",
  createdAt: new Date().toISOString(),
  expiresAt: ttlMs(60 * 60 * 1000),
});
```

Expired items are automatically filtered from `get()`, `list()`, and `search()`. Pass `{ includeExpired: true }` to include them. Call `store.purgeExpired()` to physically remove expired items from storage.

---

### Plugin API types

These types define the contract for OpenClaw plugins (used by `openclaw-memory-brain`, `openclaw-memory-docs`):

| Type | Purpose |
|------|---------|
| `PluginLogger` | Logger with optional `info`, `warn`, `error` methods |
| `CommandContext` | Context passed to command handlers (`args`, `channel`, `from`, etc.) |
| `MessageEvent` | Incoming message with `content` and `from` fields |
| `MessageEventContext` | Context for message events (`messageProvider`, `sessionId`) |
| `CommandDefinition` | Defines a plugin command (name, description, handler) |
| `ToolDefinition` | Defines a plugin tool (name, description, input schema, handler) |
| `PluginApi` | Plugin registration interface - register commands, tools, and event handlers |

**Example - registering a plugin command:**

```ts
import type { PluginApi } from "@elvatis_com/openclaw-memory-core";

export function activate(api: PluginApi) {
  api.registerCommand({
    name: "remember",
    description: "Save a memory",
    usage: "/remember <text>",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx) => {
      // store ctx.args as a memory...
      return { text: `Remembered: ${ctx.args}` };
    },
  });
}
```

---

### Swapping the embedder

The store accepts any `Embedder` implementation. To use a real semantic model:

```ts
import type { Embedder } from "@elvatis_com/openclaw-memory-core";

const openaiEmbedder: Embedder = {
  id: "openai-text-embedding-3-small",
  dims: 1536,
  async embed(text) {
    const res = await fetch("https://api.openai.com/v1/embeddings", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: "text-embedding-3-small", input: text }),
    });
    const data = await res.json();
    return data.data[0].embedding;
  },
};

const store = new JsonlMemoryStore({
  filePath: "./data/memories.jsonl",
  embedder: openaiEmbedder,
});
```

## Design philosophy

- **Stable** - no external services required; everything runs locally
- **Safe** - built-in secret redaction, path traversal guards, no hidden data exfiltration
- **Portable** - single JSONL file storage, easy to back up and inspect
- **Pluggable** - swap the embedder without changing the store API

## Development

```bash
npm run build       # compile TypeScript
npm run test        # run tests (vitest)
npm run typecheck   # type-check without emitting
npm run scan-secrets # scan for leaked secrets
npm run ci          # run all checks (typecheck + build + test + scan-secrets)
```

## License

MIT
