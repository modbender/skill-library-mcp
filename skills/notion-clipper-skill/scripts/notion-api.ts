import { readFile } from "node:fs/promises";
import * as https from "node:https";
import { resolveNotionApiKeyPath } from "./paths.js";
import { NOTION_API_VERSION, NOTION_API_BASE_URL } from "./constants.js";

export interface NotionBlock {
  object: string;
  type: string;
  [key: string]: unknown;
}

export interface CreatePageOptions {
  databaseId: string;
  title: string;
  url?: string;
  blocks: NotionBlock[];
}

export interface AppendBlocksOptions {
  pageId: string;
  blocks: NotionBlock[];
}

export interface NotionPageResponse {
  id: string;
  url: string;
  [key: string]: unknown;
}

/**
 * Inspect a database schema to decide which properties to use.
 * - titlePropertyName: the canonical Notion title property (type === "title")
 * - urlPropertyName: an optional URL property if one exists (prefer names containing "url"/"link")
 */
async function resolveDatabasePropertyNames(
  apiKey: string,
  databaseId: string
): Promise<{ titlePropertyName: string; urlPropertyName?: string }> {
  const db = await notionRequest<{
    properties: Record<
      string,
      {
        type: string;
      }
    >;
  }>(apiKey, "GET", `/databases/${databaseId}`);

  const entries = Object.entries(db.properties);

  // 1) 标准做法：找出唯一的 title 类型属性（Notion 每个数据库恰好有一个）
  const titleEntry = entries.find(([, prop]) => prop.type === "title");
  const titlePropertyName = titleEntry ? titleEntry[0] : "Name";

  // 2) 可选：URL 属性，优先匹配名字里包含 url/link/website 的
  const urlCandidates = entries.filter(([, prop]) => prop.type === "url");
  let urlPropertyName: string | undefined;

  if (urlCandidates.length > 0) {
    const scored = urlCandidates.map(([name]) => {
      const n = name.toLowerCase();
      if (n.includes("url") || n.includes("link") || n.includes("website")) return { name, score: 2 };
      return { name, score: 1 };
    });
    scored.sort((a, b) => b.score - a.score);
    urlPropertyName = scored[0]?.name;
  }

  return { titlePropertyName, urlPropertyName };
}

/**
 * Read Notion API key from ~/.config/notion/api_key
 */
export async function readNotionApiKey(): Promise<string> {
  const keyPath = resolveNotionApiKeyPath();
  try {
    const key = await readFile(keyPath, "utf-8");
    return key.trim();
  } catch (error) {
    throw new Error(
      `Failed to read Notion API key from ${keyPath}. ` +
        `Please create the file with your API key (starts with 'ntn_' or 'secret_'). ` +
        `See: https://notion.so/my-integrations`
    );
  }
}

/**
 * Call Notion API with Node https.
 *
 * NETWORK OPTIMIZATIONS APPLIED:
 * - 6 retries with exponential backoff (handles unstable networks)
 * - 30s timeout (increased from 25s)
 * - Retry on: ECONNREFUSED, ECONNRESET, ETIMEDOUT, timeout
 *
 * Note: Node.js https module doesn't support proxy env vars.
 * For best results: use network without proxy or use tsx runtime.
 */
async function notionRequest<T>(
  apiKey: string,
  method: string,
  endpoint: string,
  body?: Record<string, unknown>,
  retries: number = 6
): Promise<T> {
  const url = `${NOTION_API_BASE_URL}${endpoint}`;
  const parsed = new URL(url);
  const postData = body ? JSON.stringify(body) : undefined;

  const options: https.RequestOptions = {
    hostname: parsed.hostname,
    port: 443,
    path: parsed.pathname + parsed.search,
    method,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Notion-Version": NOTION_API_VERSION,
      "Content-Type": "application/json",
    },
  };
  if (postData) {
    (options.headers as Record<string, string>)["Content-Length"] = String(
      Buffer.byteLength(postData, "utf8")
    );
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) {
      const backoffMs = Math.min(1000 * Math.pow(2, attempt - 1), 4000);
      console.log(`  Retry ${attempt}/${retries} after ${backoffMs}ms...`);
      await new Promise((resolve) => setTimeout(resolve, backoffMs));
    }

    try {
      const { statusCode, responseBody } = await new Promise<{
        statusCode: number;
        responseBody: string;
      }>((resolve, reject) => {
        const req = https.request(options, (res) => {
          const chunks: Buffer[] = [];
          res.on("data", (chunk: Buffer) => chunks.push(chunk));
          res.on("end", () =>
            resolve({
              statusCode: res.statusCode ?? 0,
              responseBody: Buffer.concat(chunks).toString("utf8"),
            })
          );
          res.on("error", reject);
        });
        req.on("error", reject);
        req.setTimeout(30_000, () => {
          req.destroy();
          reject(new Error("Notion API request timeout"));
        });
        if (postData) req.write(postData, "utf8");
        req.end();
      });

      if (responseBody.length === 0) {
        throw new Error(
          `Notion API returned empty body (status ${statusCode}).`
        );
      }

      let data: unknown;
      try {
        data = JSON.parse(responseBody);
      } catch (e) {
        throw new Error(
          `Notion API returned invalid JSON (status ${statusCode}). First 200 chars: ${responseBody.slice(0, 200)}`
        );
      }

      if (statusCode < 200 || statusCode >= 300) {
        const msg = (data as { message?: string })?.message ?? JSON.stringify(data);
        throw new Error(`Notion API error (${statusCode}): ${msg}`);
      }

      if (data == null) {
        throw new Error("Notion API returned empty body");
      }

      return data as T;
    } catch (error) {
      lastError = error as Error;
      const isRetryable =
        lastError.message.includes("ECONNREFUSED") ||
        lastError.message.includes("ECONNRESET") ||
        lastError.message.includes("ETIMEDOUT") ||
        lastError.message.includes("timeout") ||
        lastError.message.includes("empty body");

      if (!isRetryable || attempt >= retries) {
        throw lastError;
      }
    }
  }

  throw lastError || new Error("Notion API request failed");
}

/**
 * Create a new page in a database with content blocks
 */
export async function createPageInDatabase(
  apiKey: string,
  options: CreatePageOptions
): Promise<NotionPageResponse> {
  const { databaseId, title, url, blocks } = options;

  // 动态读取数据库字段，由代码“聪明地”决定用哪个属性来写入标题 / URL
  const { titlePropertyName, urlPropertyName } = await resolveDatabasePropertyNames(
    apiKey,
    databaseId
  );

  const properties: Record<string, unknown> = {};

  // 标题字段：使用数据库中真正的 title 属性，而不是死写 Name
  properties[titlePropertyName] = {
    title: [{ text: { content: title } }],
  };

  // URL 字段（如果数据库里有合适的 URL 属性就写，没有就忽略）
  if (url && urlPropertyName) {
    properties[urlPropertyName] = { url };
  }

  const body: Record<string, unknown> = {
    parent: { database_id: databaseId },
    properties,
    children: blocks.slice(0, 100),
  };

  const page = await notionRequest<NotionPageResponse>(apiKey, "POST", "/pages", body);

  if (blocks.length > 100) {
    await appendBlocksToPage(apiKey, {
      pageId: page.id,
      blocks: blocks.slice(100),
    });
  }

  return page;
}

/**
 * Append blocks to an existing page
 */
export async function appendBlocksToPage(
  apiKey: string,
  options: AppendBlocksOptions
): Promise<void> {
  const { pageId, blocks } = options;
  for (let i = 0; i < blocks.length; i += 100) {
    const chunk = blocks.slice(i, i + 100);
    await notionRequest(apiKey, "PATCH", `/blocks/${pageId}/children`, {
      children: chunk,
    });
  }
}

export interface NotionDatabase {
  id: string;
  title: string;
  url: string;
}

/**
 * Search for databases by name
 */
export async function searchDatabases(
  apiKey: string,
  query?: string
): Promise<NotionDatabase[]> {
  const body: Record<string, unknown> = {
    filter: { property: "object", value: "database" },
    page_size: 100,
  };
  if (query) body.query = query;

  const response = await notionRequest<{
    results?: Array<{
      id: string;
      url?: string;
      title?: Array<{ plain_text?: string }>;
    }>;
  }>(apiKey, "POST", "/search", body);

  // Add null check for response
  if (!response) {
    throw new Error(
      "Notion search returned null response. Check your API key and integration access."
    );
  }

  const results = response.results;
  if (!Array.isArray(results)) {
    throw new Error(
      "Notion search returned unexpected format. Share at least one database with your integration."
    );
  }

  return results.map((db) => ({
    id: db.id,
    title: db.title?.[0]?.plain_text ?? "Untitled",
    url: db.url ?? "",
  }));
}

/**
 * Find a database by name (case-insensitive partial match)
 */
export async function findDatabaseByName(
  apiKey: string,
  name: string
): Promise<NotionDatabase | null> {
  const databases = await searchDatabases(apiKey, name);
  const exact = databases.find((db) => db.title.toLowerCase() === name.toLowerCase());
  if (exact) return exact;
  const partial = databases.find((db) =>
    db.title.toLowerCase().includes(name.toLowerCase())
  );
  return partial ?? null;
}

/**
 * List all databases the integration has access to
 */
export async function listAllDatabases(apiKey: string): Promise<NotionDatabase[]> {
  return searchDatabases(apiKey);
}

/**
 * Create a new page as a child of another page
 */
export async function createChildPage(
  apiKey: string,
  parentPageId: string,
  title: string,
  blocks: NotionBlock[]
): Promise<NotionPageResponse> {
  const body: Record<string, unknown> = {
    parent: { page_id: parentPageId },
    properties: {
      title: { title: [{ text: { content: title } }] },
    },
    children: blocks.slice(0, 100),
  };

  const page = await notionRequest<NotionPageResponse>(apiKey, "POST", "/pages", body);

  if (blocks.length > 100) {
    await appendBlocksToPage(apiKey, {
      pageId: page.id,
      blocks: blocks.slice(100),
    });
  }

  return page;
}
