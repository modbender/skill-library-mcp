import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { readFile } from "node:fs/promises";
import { gunzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { buildIndex, buildIndexFromBundle } from "./skill-index.js";
import { createServer } from "./server.js";
import type { SkillsBundle, SkillsIndex, SearchIndex } from "./types.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Skills directory is at the project root, sibling to dist/ (used in dev/fallback mode)
const skillsDir = join(__dirname, "..", "data");

// Lazily loaded content bundle (only decompressed on first load_skill call)
let contentBundle: SkillsBundle | undefined;
let contentBundlePath: string | undefined;

async function getContentBundle(): Promise<SkillsBundle | undefined> {
  if (contentBundle) return contentBundle;
  if (!contentBundlePath) return undefined;
  try {
    const compressed = await readFile(contentBundlePath);
    contentBundle = JSON.parse(gunzipSync(compressed).toString("utf-8")) as SkillsBundle;
    return contentBundle;
  } catch {
    return undefined;
  }
}

async function main() {
  let index: SearchIndex;

  // Try index bundle first (npm package mode — avoids thousands of files on Windows)
  const indexPath = join(__dirname, "skills-index.json");
  const contentPath = join(__dirname, "skills-content.json.gz");
  try {
    const raw = await readFile(indexPath, "utf-8");
    const skillsIndex = JSON.parse(raw) as SkillsIndex;
    index = buildIndexFromBundle(skillsIndex);
    contentBundlePath = contentPath;
    console.error(`[skill-library] Indexed ${index.entries.length} skills from bundle`);
  } catch {
    // Fall back to filesystem (dev mode)
    index = await buildIndex(skillsDir);
    console.error(`[skill-library] Indexed ${index.entries.length} skills from ${skillsDir}`);
  }

  const server = createServer(index, skillsDir, contentBundlePath ? getContentBundle : undefined);
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[skill-library] MCP server running on stdio");
}

main().catch((err) => {
  console.error("[skill-library] Fatal error:", err);
  process.exit(1);
});
