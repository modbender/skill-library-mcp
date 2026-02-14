import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { buildIndex } from "./skill-index.js";
import { createServer } from "./server.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Skills directory is at the project root, sibling to dist/
const skillsDir = join(__dirname, "..", "skills");

async function main() {
  const index = await buildIndex(skillsDir);
  console.error(`[skill-library] Indexed ${index.entries.length} skills from ${skillsDir}`);

  const server = createServer(index, skillsDir);
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[skill-library] MCP server running on stdio");
}

main().catch((err) => {
  console.error("[skill-library] Fatal error:", err);
  process.exit(1);
});
