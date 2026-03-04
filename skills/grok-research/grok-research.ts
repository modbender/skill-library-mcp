#!/usr/bin/env bun
/**
 * grok-research — Forward research queries to Grok API as-is.
 *
 * Usage:
 *   bun run grok-research.ts <query>
 *   bun run grok-research.ts --model grok-4.1-thinking <query>
 *
 * Env: GROK_API_KEY (required)
 */

const BASE_URL = "https://ai.a9.bot/v1";
const DEFAULT_MODEL = "grok-4.20-beta";

function getApiKey(): string {
  const key = process.env.A9_GROK_API_KEY;
  if (!key) throw new Error("A9_GROK_API_KEY env var not set");
  return key;
}

async function callGrok(model: string, query: string): Promise<string> {
  const res = await fetch(`${BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getApiKey()}`,
    },
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: query }],
      stream: false,
      temperature: 0.3,
      max_tokens: 8192,
    }),
  });

  if (!res.ok) {
    throw new Error(`Grok API ${res.status}: ${(await res.text()).slice(0, 500)}`);
  }

  const rawText = await res.text();

  // Handle SSE streaming (some providers force it)
  if (rawText.startsWith("data: ")) {
    let content = "";
    for (const line of rawText.split("\n")) {
      if (!line.startsWith("data: ") || line.trim() === "data: [DONE]") continue;
      try {
        const delta = JSON.parse(line.slice(6)).choices?.[0]?.delta?.content;
        if (delta) content += delta;
      } catch {}
    }
    content = content.replace(/<thinking>[\s\S]*?<\/thinking>/g, "").trim();
    if (!content) throw new Error("Grok returned empty response");
    return content;
  }

  // Regular JSON
  const data = JSON.parse(rawText);
  const content = data.choices?.[0]?.message?.content;
  if (!content) throw new Error("Grok returned empty response");
  return content;
}

// --- CLI ---

const args = process.argv.slice(2);

let model = DEFAULT_MODEL;
const mi = args.indexOf("--model");
if (mi >= 0 && mi + 1 < args.length) {
  model = args[mi + 1];
  args.splice(mi, 2);
}

const query = args.join(" ").trim();
if (!query) {
  console.error("Usage: bun run grok-research.ts [--model <id>] <query>");
  process.exit(1);
}

console.error(`🔍 ${model} ...`);
try {
  console.log(await callGrok(model, query));
} catch (err: any) {
  console.error(`❌ ${err.message}`);
  process.exit(1);
}
