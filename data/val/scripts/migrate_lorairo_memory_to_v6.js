#!/usr/bin/env node
/**
 * Migrate existing LoRAIro LTM pages created by older transforms (v5 and earlier)
 * where the full content (and enrichment) was stored in the Body property.
 *
 * New format (v6):
 * - Body property is a short preview
 * - Full content + enrichment is stored as page children blocks
 *
 * Safe-by-default:
 * - Migrates pages where either:
 *   - Body contains "# Enrichment (auto)" marker (old v5 style), OR
 *   - Body rich_text is longer than a threshold (default: 800 chars)
 * - Skips pages that already contain a "Main" heading_2 child
 */

import fs from "node:fs";

const NOTION_VERSION = "2025-09-03";
const NOTION_API = "https://api.notion.com/v1";
const DATA_SOURCE_ID = "2f544994-92c3-80d4-a975-000b5fcf09e9";

const RICH_TEXT_CHUNK = 1900;

function chunkString(s, chunkSize = RICH_TEXT_CHUNK) {
  if (!s) return [""];
  const chunks = [];
  for (let i = 0; i < s.length; i += chunkSize) chunks.push(s.slice(i, i + chunkSize));
  return chunks;
}
function richTextChunked(text) {
  return chunkString(text).map((part) => ({ type: "text", text: { content: part } }));
}

async function notionFetch(path, init) {
  const key = fs.readFileSync(`${process.env.HOME}/.config/notion/api_key`, "utf8").trim();
  if (!key) throw new Error("Notion api_key missing or empty at ~/.config/notion/api_key");
  const res = await fetch(`${NOTION_API}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${key}`,
      "Notion-Version": NOTION_VERSION,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const text = await res.text();
  let json;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { raw: text };
  }
  if (!res.ok) throw new Error(`Notion API error ${res.status}: ${json?.message || text || `HTTP ${res.status}`}`);
  return json;
}

function getTitle(page) {
  const props = page?.properties || {};
  for (const k of Object.keys(props)) {
    const v = props[k];
    if (v?.type === "title") {
      return (v.title || []).map((t) => t.plain_text || "").join("");
    }
  }
  return "";
}

function getRichText(page, propName) {
  const v = page?.properties?.[propName];
  if (!v || v.type !== "rich_text") return "";
  return (v.rich_text || []).map((t) => t.plain_text || "").join("");
}

async function pageHasMainHeading(pageId) {
  const res = await notionFetch(`/blocks/${pageId}/children?page_size=50`, { method: "GET" });
  const blocks = res?.results || [];
  for (const b of blocks) {
    if (b?.type === "heading_2") {
      const txt = (b.heading_2?.rich_text || []).map((t) => t.plain_text || "").join("");
      if (txt.trim().toLowerCase() === "main") return true;
    }
  }
  return false;
}

function paragraphBlocks(text) {
  const blocks = [];
  const parts = (text || "").split(/\n\n+/g);
  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    for (const chunk of chunkString(trimmed)) {
      blocks.push({ object: "block", type: "paragraph", paragraph: { rich_text: richTextChunked(chunk) } });
    }
  }
  if (blocks.length === 0) blocks.push({ object: "block", type: "paragraph", paragraph: { rich_text: richTextChunked("(empty)") } });
  return blocks;
}

function bullets(urls) {
  return (urls || []).slice(0, 20).map((u) => ({
    object: "block",
    type: "bulleted_list_item",
    bulleted_list_item: { rich_text: richTextChunked(String(u)) },
  }));
}

function buildChildren(mainText, enrichText) {
  const children = [];
  children.push({ object: "block", type: "heading_2", heading_2: { rich_text: richTextChunked("Main") } });
  children.push(...paragraphBlocks(mainText));

  if (enrichText && enrichText.trim()) {
    children.push({ object: "block", type: "divider", divider: {} });
    children.push({ object: "block", type: "heading_2", heading_2: { rich_text: richTextChunked("Enrichment (auto)") } });

    // If it contains a citations list, try to extract URLs and make them bullets.
    const m = enrichText.match(/\nCitations:\n([\s\S]*)$/);
    if (m) {
      const before = enrichText.slice(0, m.index).trim();
      if (before) children.push(...paragraphBlocks(before));
      const list = (m[1] || "")
        .split(/\n+/)
        .map((l) => l.trim())
        .filter((l) => l.startsWith("- "))
        .map((l) => l.slice(2).trim());
      if (list.length) {
        children.push({ object: "block", type: "paragraph", paragraph: { rich_text: richTextChunked("Citations:") } });
        children.push(...bullets(list));
      } else {
        children.push(...paragraphBlocks(m[1] || ""));
      }
    } else {
      children.push(...paragraphBlocks(enrichText.trim()));
    }
  }

  return children;
}

async function appendChildren(pageId, children) {
  // Notion limits children in one request. Chunk at 80 for safety.
  const chunkSize = 80;
  for (let i = 0; i < children.length; i += chunkSize) {
    const slice = children.slice(i, i + chunkSize);
    await notionFetch(`/blocks/${pageId}/children`, {
      method: "PATCH",
      body: JSON.stringify({ children: slice }),
    });
  }
}

async function updateBodyPreview(pageId, bodyPreview) {
  await notionFetch(`/pages/${pageId}`, {
    method: "PATCH",
    body: JSON.stringify({
      properties: {
        Body: { rich_text: richTextChunked(bodyPreview) },
      },
    }),
  });
}

function splitMainAndEnrichment(bodyText) {
  const marker = "# Enrichment (auto)";
  const idx = bodyText.indexOf(marker);
  if (idx === -1) return null;
  // Try to drop the leading separator
  const main = bodyText.slice(0, idx).replace(/\n\n---\n\n\s*$/m, "").trim();
  const enrich = bodyText.slice(idx + marker.length).trim();
  return { main, enrich };
}

function parseArgs() {
  const args = process.argv.slice(2);
  const out = { minBodyLen: 800, limit: 500 };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--min-body-len") out.minBodyLen = Number(args[++i] || out.minBodyLen);
    if (a === "--limit") out.limit = Number(args[++i] || out.limit);
  }
  if (!Number.isFinite(out.minBodyLen) || out.minBodyLen < 1) out.minBodyLen = 800;
  if (!Number.isFinite(out.limit) || out.limit < 1) out.limit = 500;
  return out;
}

async function queryCandidates(limit = 500) {
  // Notion can't filter by rich_text length, so we page through recent items and filter locally.
  const results = [];
  let cursor = undefined;
  while (true) {
    const payload = {
      page_size: 50,
      sorts: [{ property: "Created", direction: "descending" }],
      start_cursor: cursor,
    };
    if (!cursor) delete payload.start_cursor;
    const res = await notionFetch(`/data_sources/${DATA_SOURCE_ID}/query`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    results.push(...(res?.results || []));
    if (!res?.has_more) break;
    cursor = res?.next_cursor;
    if (!cursor) break;
    if (results.length >= limit) break;
  }
  return results.slice(0, limit);
}

async function main() {
  const { minBodyLen, limit } = parseArgs();
  const pages = await queryCandidates(limit);
  console.log(`scanned=${pages.length} minBodyLen=${minBodyLen}`);

  const migrated = [];
  for (const page of pages) {
    const id = page.id;
    const title = getTitle(page);
    const bodyText = getRichText(page, "Body");

    const hasMarker = bodyText.includes("# Enrichment (auto)");
    const isLong = bodyText.length >= minBodyLen;
    if (!hasMarker && !isLong) continue;

    const already = await pageHasMainHeading(id);
    if (already) {
      console.log(`skip(already_blocks): ${title} ${page.url}`);
      continue;
    }

    let mainText = bodyText;
    let enrichText = "";

    const split = splitMainAndEnrichment(bodyText);
    if (split) {
      mainText = split.main;
      enrichText = split.enrich;
    }

    const preview = mainText.length > 240 ? `${mainText.slice(0, 240)}…` : mainText;
    const children = buildChildren(mainText, enrichText);

    console.log(`migrate: ${title} bodyLen=${bodyText.length} blocks=${children.length}`);
    await updateBodyPreview(id, preview);
    await appendChildren(id, children);

    migrated.push({ title, url: page.url });
  }

  console.log(`migrated=${migrated.length}`);
  for (const m of migrated) console.log(`- ${m.title} | ${m.url}`);
}

main().catch((e) => {
  console.error(String(e?.stack || e));
  process.exit(1);
});
