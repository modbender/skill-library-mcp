const fs = require("fs");
const path = require("path");

function loadBring() {
  const envPath = process.env.BRING_NODE_API_PATH;
  if (envPath) {
    return require(envPath);
  }

  const localPath = path.resolve(
    __dirname,
    "..",
    "..",
    "..",
    "node-bring-api",
    "build",
    "bring.js",
  );
  if (fs.existsSync(localPath)) {
    return require(localPath);
  }

  return require("bring-shopping");
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      args._.push(token);
      continue;
    }
    const key = token.replace(/^--/, "");
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    const usage = [
      "Usage:",
      "  node bring_inspirations.js --filters",
      '  node bring_inspirations.js --tags "winter,vegetarisch" --limit 10',
      '  node bring_inspirations.js --parse-url "https://www.chefkoch.de/rezepte/123/lasagne.html"',
      '  node bring_inspirations.js --parse-url "url1,url2,url3"',
      "",
      "Env:",
      "  BRING_EMAIL, BRING_PASSWORD, BRING_COUNTRY (default DE)",
      "  BRING_NODE_API_PATH (optional path to bring.js)",
    ];
    console.log(usage.join("\n"));
    return;
  }

  const email = args.email || process.env.BRING_EMAIL;
  const password = args.password || process.env.BRING_PASSWORD;
  const country = args.country || process.env.BRING_COUNTRY || "DE";

  if (!email || !password) {
    throw new Error("Missing BRING_EMAIL/BRING_PASSWORD (or --email/--password).");
  }

  const Bring = loadBring();
  const bring = new Bring({ mail: email, password });
  bring.headers["X-BRING-COUNTRY"] = country;
  await bring.login();

  if (args.filters) {
    const filters = await bring.getInspirationFilters();
    console.log(JSON.stringify(filters, null, 2));
    return;
  }

  if (args["parse-url"]) {
    const urls = String(args["parse-url"])
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (urls.length === 0) {
      throw new Error("--parse-url requires at least one URL.");
    }
    const results = [];
    for (const url of urls) {
      try {
        const template = await bring.parseRecipe(url);
        results.push({
          url,
          name: template.name || template.title || null,
          imageUrl: template.imageUrl || template.image || null,
          sourceUrl: template.sourceUrl || url,
          servings: template.servings || null,
          items: Array.isArray(template.items)
            ? template.items.map((i) => ({
                itemId: i.itemId || i.name || "",
                spec: i.spec || i.amount || "",
              }))
            : [],
          raw: template,
        });
      } catch (err) {
        results.push({ url, error: err.message });
      }
    }
    console.log(JSON.stringify(results.length === 1 ? results[0] : results, null, 2));
    return;
  }

  const filterTags = args.tags || args.filter || "mine";
  const inspirations = await bring.getInspirations(filterTags);
  console.log(JSON.stringify(inspirations, null, 2));
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
