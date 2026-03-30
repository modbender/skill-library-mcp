import { readdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, "..");
const dataDir = join(projectRoot, "data");
// Two output files: small index for startup, compressed content for load_skill
const indexPath = join(projectRoot, "dist", "skills-index.json");
const contentPath = join(projectRoot, "dist", "skills-content.json.gz");

interface BundleEntry {
  content: string;
  resources?: Record<string, string>;
}

interface IndexEntry {
  name: string;
  description: string;
  hasResources: boolean;
  resourceFiles: string[];
  metadata?: Record<string, unknown>;
  allowedTools?: string[];
}

async function main() {
  console.error(`[bundle-skills] Reading skills from ${dataDir}...`);

  let dirs: string[];
  try {
    dirs = await readdir(dataDir);
  } catch (err) {
    console.error(`[bundle-skills] Cannot read data directory: ${dataDir}`, err);
    process.exit(1);
  }

  // Parse minimal YAML frontmatter for index (name + description only)
  function parseName(content: string): { name: string; description: string; metadata?: Record<string, unknown>; allowedTools?: string[] } | null {
    const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!match) return null;
    try {
      // Simple key extraction without full YAML parser dependency in this script
      const block = match[1];
      const nameMatch = block.match(/^name:\s*(.+)$/m);
      const descMatch = block.match(/^description:\s*(.+)$/m);
      if (!nameMatch) return null;
      return {
        name: nameMatch[1].trim().replace(/^['"]|['"]$/g, ""),
        description: descMatch ? descMatch[1].trim().replace(/^['"]|['"]$/g, "") : "",
      };
    } catch {
      return null;
    }
  }

  const indexSkills: Record<string, IndexEntry> = {};
  const contentSkills: Record<string, BundleEntry> = {};
  let count = 0;

  for (const dirName of dirs) {
    const skillPath = join(dataDir, dirName, "SKILL.md");
    let content: string;
    try {
      content = await readFile(skillPath, "utf-8");
    } catch {
      continue;
    }

    const parsed = parseName(content);
    if (!parsed) continue;

    const resourceDir = join(dataDir, dirName, "resources");
    let resourceFiles: string[] = [];
    const resources: Record<string, string> = {};

    try {
      const files = await readdir(resourceDir);
      const mdFiles = files.filter((f) => f.endsWith(".md")).sort();
      resourceFiles = mdFiles;
      for (const file of mdFiles) {
        resources[file] = await readFile(join(resourceDir, file), "utf-8");
      }
    } catch {
      // No resources directory
    }

    indexSkills[dirName] = {
      name: parsed.name,
      description: parsed.description,
      hasResources: resourceFiles.length > 0,
      resourceFiles,
    };

    contentSkills[dirName] = {
      content,
      ...(resourceFiles.length > 0 ? { resources } : {}),
    };

    count++;
  }

  // Write small index (uncompressed, loaded at startup)
  await writeFile(indexPath, JSON.stringify({ version: 1, skills: indexSkills }));
  console.error(`[bundle-skills] Wrote index for ${count} skills → ${indexPath}`);

  // Write compressed content bundle (decompressed lazily on first load_skill call)
  const compressed = gzipSync(Buffer.from(JSON.stringify({ version: 1, skills: contentSkills })));
  await writeFile(contentPath, compressed);
  console.error(`[bundle-skills] Wrote compressed content (${Math.round(compressed.length / 1024 / 1024)}MB) → ${contentPath}`);
}

main().catch((err) => {
  console.error("[bundle-skills] Fatal error:", err);
  process.exit(1);
});
