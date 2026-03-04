#!/usr/bin/env npx tsx

/**
 * Zyla API Hub — Generate Popular APIs Section for SKILL.md
 *
 * Fetches the top 20 APIs by popularity from the catalog endpoint
 * and generates a markdown section to embed in SKILL.md.
 *
 * Usage:
 *   npx tsx scripts/generate-popular.ts
 *   npx tsx scripts/generate-popular.ts --limit 10
 *   npx tsx scripts/generate-popular.ts --url https://zylalabs.com
 *
 * Output goes to stdout. Pipe or paste into SKILL.md between the
 * <!-- POPULAR_APIS_START --> and <!-- POPULAR_APIS_END --> markers.
 */

const DEFAULT_HUB_URL = "https://zylalabs.com";

interface CatalogApi {
  id: number;
  name: string;
  description: string;
  category: string | null;
  popularity: number;
  endpoints: Array<{
    id: number;
    name: string;
    method: string;
    description: string;
    parameters: Array<{
      key: string;
      type: string;
      required: boolean;
      description: string;
      example: string;
    }>;
  }>;
}

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && i + 1 < args.length) {
      result[args[i].slice(2)] = args[i + 1];
      i++;
    }
  }
  return result;
}

/**
 * Generate trigger keywords from API name, category, and description.
 */
function generateKeywords(api: CatalogApi): string {
  const words = new Set<string>();

  // From name: split by spaces, hyphens, and common separators
  const nameTokens = api.name
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !["api", "the", "and", "for", "with"].includes(w));

  nameTokens.forEach((w) => words.add(w));

  // From category
  if (api.category) {
    api.category
      .toLowerCase()
      .replace(/[^a-z0-9\s&]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2 && w !== "and")
      .forEach((w) => words.add(w));
  }

  // From description (first 3 significant words)
  if (api.description) {
    api.description
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter(
        (w) =>
          w.length > 3 &&
          !["this", "that", "with", "from", "your", "about", "data", "provides", "access"].includes(w)
      )
      .slice(0, 3)
      .forEach((w) => words.add(w));
  }

  return Array.from(words).slice(0, 8).join(", ");
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

async function main() {
  const flags = parseArgs(process.argv.slice(2));
  const hubUrl = flags["url"] || DEFAULT_HUB_URL;
  const limit = parseInt(flags["limit"] || "20", 10);

  // Fetch catalog
  const res = await fetch(`${hubUrl}/api/openclaw/catalog?limit=${limit}&sort=popularity`, {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    console.error(`Error: Failed to fetch catalog (HTTP ${res.status})`);
    process.exit(1);
  }

  const data = await res.json();
  const apis: CatalogApi[] = data.apis || [];

  if (apis.length === 0) {
    console.error("Error: No APIs returned from catalog");
    process.exit(1);
  }

  // Generate markdown
  const lines: string[] = [];
  lines.push(`<!-- Auto-generated on ${new Date().toISOString().split("T")[0]} from ${hubUrl} -->`);
  lines.push(`<!-- Top ${apis.length} APIs by popularity_score -->`);
  lines.push("");

  for (const api of apis) {
    const keywords = generateKeywords(api);
    const apiSlug = slugify(api.name);

    lines.push(`### ${api.name} (ID: ${api.id})`);
    lines.push(`- **Use when**: ${keywords}`);
    if (api.category) {
      lines.push(`- **Category**: ${api.category}`);
    }

    // List endpoints with parameters
    for (const ep of api.endpoints.slice(0, 3)) {
      // Show up to 3 endpoints per API
      const epSlug = slugify(ep.name);
      const requiredParams = ep.parameters.filter((p) => p.required);
      const paramStr = requiredParams.map((p) => `${p.key} (${p.type}, required)`).join(", ");
      const optionalParams = ep.parameters.filter((p) => !p.required);
      const optParamStr = optionalParams.length > 0
        ? ` + optional: ${optionalParams.map((p) => p.key).join(", ")}`
        : "";

      lines.push(
        `- **${ep.method}** \`${ep.name}\` (ID: ${ep.id}): ${paramStr || "no required params"}${optParamStr}`
      );

      // Example call with required params filled
      const exampleParams = Object.fromEntries(
        requiredParams.map((p) => [p.key, p.example || `<${p.type}>`])
      );
      lines.push(
        `  - Example: \`npx tsx {baseDir}/scripts/zyla-api.ts call --api ${api.id} --endpoint ${ep.id} --params '${JSON.stringify(exampleParams)}'\``
      );
    }

    if (api.endpoints.length > 3) {
      lines.push(
        `- ... and ${api.endpoints.length - 3} more endpoints. Run: \`npx tsx {baseDir}/scripts/zyla-catalog.ts endpoints --api ${api.id}\``
      );
    }

    lines.push("");
  }

  console.log(lines.join("\n"));
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
