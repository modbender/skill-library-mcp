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

async function fetchContent(url, headers) {
  const resp = await fetch(url, { headers });
  const text = await resp.text();
  try {
    return JSON.parse(text);
  } catch (err) {
    throw new Error(`Non-JSON response (${resp.status}): ${text.slice(0, 200)}`);
  }
}

function extractItemsFromContent(content) {
  if (!content || !Array.isArray(content.items)) {
    return [];
  }
  const seen = new Set();
  const items = [];
  for (const item of content.items) {
    const name = String(item.itemId || "").trim();
    if (!name) {
      continue;
    }
    const spec = String(item.spec || "").trim();
    const key = `${name}||${spec}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    items.push({ name, spec });
  }
  return items;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    const usage = [
      "Usage:",
      "  node bring_list.js --lists",
      '  node bring_list.js --create-list "Amazon"',
      '  node bring_list.js --list <uuid> --add "Item 1,Item 2"',
      '  node bring_list.js --list-name "Einkauf" --add "Item 1"',
      '  node bring_list.js --list-name "Einkauf" --content-url "<url>"',
      '  node bring_list.js --list-name "Einkauf" --add-recipe "Lasagne" --recipe-items "Nudeln,Hackfleisch,Tomaten"',
      '  node bring_list.js --list-name "Einkauf" --add-recipe-url "https://www.chefkoch.de/rezepte/123/lasagne.html"',
      '  node bring_list.js --list-name "Einkauf" --recipe-markers',
      "",
      "Flags:",
      "  --lists                   List all shopping lists",
      "  --create-list <name>      Create a new shopping list",
      "  --list <uuid>             Select list by UUID",
      "  --list-name <name>        Select list by name",
      '  --add "i1,i2"             Add plain items',
      '  --content-url "<url>"     Add items from Bring content URL',
      "  --add-recipe <name>       Add items tagged with a recipe marker",
      '  --recipe-items "i1,i2"    Items to add (used with --add-recipe)',
      "  --add-recipe-url <url>    Parse recipe URL and add all ingredients to list",
      "  --recipe-markers          Show distinct recipe markers on a list",
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

  if (args.lists) {
    const lists = await bring.loadLists();
    console.log(JSON.stringify(lists, null, 2));
    return;
  }

  // --create-list: create a new shopping list
  if (args["create-list"]) {
    const listName = String(args["create-list"]).trim();
    if (!listName) {
      throw new Error("--create-list requires a non-empty list name.");
    }

    // Check if list already exists
    const existingLists = await bring.loadLists();
    const existing = (existingLists.lists || []).find(
      (l) => String(l.name || "").toLowerCase() === listName.toLowerCase(),
    );
    if (existing) {
      console.log(
        JSON.stringify(
          {
            error: false,
            message: `List "${existing.name}" already exists.`,
            listUuid: existing.listUuid,
            name: existing.name,
            created: false,
          },
          null,
          2,
        ),
      );
      return;
    }

    // Generate a new UUID for the list
    const { randomUUID } = require("crypto");
    const newListUuid = randomUUID();

    // Create the list via the Bring API (POST with form-urlencoded)
    const userUuid = bring.uuid || bring.headers["X-BRING-USER-UUID"];
    const baseUrl = bring.url || "https://api.getbring.com/rest/v2/";
    const createUrl = `${baseUrl}bringusers/${userUuid}/lists`;

    const formBody = new URLSearchParams({
      listUuid: newListUuid,
      name: listName,
      theme: "ch.publisheria.bring.theme.home",
    }).toString();

    const resp = await fetch(createUrl, {
      method: "POST",
      headers: {
        ...bring.headers,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: formBody,
    });

    if (!resp.ok) {
      const body = await resp.text();
      throw new Error(`Cannot create list (${resp.status}): ${body.slice(0, 300)}`);
    }

    // Verify the list was created
    const updatedLists = await bring.loadLists();
    const created = (updatedLists.lists || []).find(
      (l) => String(l.name || "").toLowerCase() === listName.toLowerCase(),
    );

    if (created) {
      console.log(
        JSON.stringify(
          {
            error: false,
            message: `List "${created.name}" created successfully.`,
            listUuid: created.listUuid,
            name: created.name,
            created: true,
          },
          null,
          2,
        ),
      );
    } else {
      console.log(
        JSON.stringify(
          {
            error: false,
            message: `Create request succeeded but list "${listName}" not found in loadLists. It may take a moment to appear.`,
            requestedName: listName,
            requestedUuid: newListUuid,
            created: true,
          },
          null,
          2,
        ),
      );
    }
    return;
  }

  const RECIPE_PREFIX = "[Rezept] ";

  // --recipe-markers: list distinct recipe names found on a list
  if (args["recipe-markers"]) {
    let listUuid = args.list;
    if (!listUuid && args["list-name"]) {
      const lists = await bring.loadLists();
      const name = String(args["list-name"]).toLowerCase();
      const matches = (lists.lists || []).filter(
        (l) => String(l.name || "").toLowerCase() === name,
      );
      if (matches.length === 1) {
        listUuid = matches[0].listUuid;
      } else if (matches.length > 1) {
        throw new Error(`Multiple lists match name: ${args["list-name"]}`);
      } else {
        throw new Error(`No list matches name: ${args["list-name"]}`);
      }
    }
    if (!listUuid) {
      throw new Error('Missing --list <uuid> or --list-name "Name".');
    }
    const listItems = await bring.getItems(listUuid);
    const purchase = listItems.purchase || [];
    const markers = new Set();
    for (const item of purchase) {
      const spec = String(item.specification || "");
      if (spec.startsWith(RECIPE_PREFIX)) {
        const recipeName = spec.slice(RECIPE_PREFIX.length).trim();
        if (recipeName) {
          markers.add(recipeName);
        }
      }
    }
    console.log(JSON.stringify({ listUuid, recipeMarkers: [...markers].sort() }, null, 2));
    return;
  }

  // --add-recipe: add items tagged with a recipe marker
  if (args["add-recipe"]) {
    const recipeName = String(args["add-recipe"]).trim();
    if (!recipeName) {
      throw new Error("--add-recipe requires a non-empty recipe name.");
    }
    const recipeItemsRaw = args["recipe-items"] || "";
    if (!recipeItemsRaw) {
      throw new Error('--add-recipe requires --recipe-items "item1,item2".');
    }
    let listUuid = args.list;
    if (!listUuid && args["list-name"]) {
      const lists = await bring.loadLists();
      const name = String(args["list-name"]).toLowerCase();
      const matches = (lists.lists || []).filter(
        (l) => String(l.name || "").toLowerCase() === name,
      );
      if (matches.length === 1) {
        listUuid = matches[0].listUuid;
      } else if (matches.length > 1) {
        throw new Error(`Multiple lists match name: ${args["list-name"]}`);
      } else {
        throw new Error(`No list matches name: ${args["list-name"]}`);
      }
    }
    if (!listUuid) {
      throw new Error('Missing --list <uuid> or --list-name "Name".');
    }
    const spec = `${RECIPE_PREFIX}${recipeName}`;
    const items = recipeItemsRaw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (items.length === 0) {
      throw new Error("No items found in --recipe-items.");
    }
    const results = [];
    for (const item of items) {
      const res = await bring.saveItem(listUuid, item, spec);
      results.push({ item, spec, result: res });
    }
    console.log(JSON.stringify({ listUuid, recipe: recipeName, added: results }, null, 2));
    return;
  }

  // --add-recipe-url: parse a recipe URL and add all ingredients via batch
  if (args["add-recipe-url"]) {
    const recipeUrl = String(args["add-recipe-url"]).trim();
    if (!recipeUrl) {
      throw new Error("--add-recipe-url requires a URL.");
    }
    let listUuid = args.list;
    if (!listUuid && args["list-name"]) {
      const lists = await bring.loadLists();
      const name = String(args["list-name"]).toLowerCase();
      const matches = (lists.lists || []).filter(
        (l) => String(l.name || "").toLowerCase() === name,
      );
      if (matches.length === 1) {
        listUuid = matches[0].listUuid;
      } else if (matches.length > 1) {
        throw new Error(`Multiple lists match name: ${args["list-name"]}`);
      } else {
        throw new Error(`No list matches name: ${args["list-name"]}`);
      }
    }
    if (!listUuid) {
      throw new Error('Missing --list <uuid> or --list-name "Name".');
    }

    // Parse recipe from URL
    const template = await bring.parseRecipe(recipeUrl);
    const recipeName = template.name || template.title || "Rezept";

    // Convert BringTemplate items to Recipe format
    const recipeItems = Array.isArray(template.items)
      ? template.items
          .map((i) => ({
            name: String(i.itemId || i.name || "").trim(),
            amount: String(i.spec || i.amount || "").trim(),
          }))
          .filter((i) => i.name)
      : [];

    if (recipeItems.length === 0) {
      throw new Error(`No ingredients found in recipe: ${recipeName}`);
    }

    const recipe = { name: recipeName, items: recipeItems };
    const result = await bring.addRecipeToList(listUuid, recipe);

    console.log(
      JSON.stringify(
        {
          listUuid,
          recipe: recipeName,
          sourceUrl: recipeUrl,
          itemCount: result.added.length,
          marker: result.marker || null,
          added: result.added,
        },
        null,
        2,
      ),
    );
    return;
  }

  const contentUrlRaw =
    args["content-url"] || args["content-urls"] || args["from-content-url"] || "";
  const itemsRaw = args.add || "";
  if (!itemsRaw && !contentUrlRaw) {
    throw new Error('Missing --add "item1,item2" or --content-url "<url>".');
  }

  let listUuid = args.list;
  if (!listUuid && args["list-name"]) {
    const lists = await bring.loadLists();
    const name = String(args["list-name"]).toLowerCase();
    const matches = (lists.lists || []).filter((l) => String(l.name || "").toLowerCase() === name);
    if (matches.length === 1) {
      listUuid = matches[0].listUuid;
    } else if (matches.length > 1) {
      throw new Error(`Multiple lists match name: ${args["list-name"]}`);
    } else {
      throw new Error(`No list matches name: ${args["list-name"]}`);
    }
  }

  if (!listUuid) {
    throw new Error('Missing --list <uuid> or --list-name "Name".');
  }

  if (contentUrlRaw) {
    const urls = contentUrlRaw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const allItems = [];
    for (const url of urls) {
      const content = await fetchContent(url, bring.headers);
      const items = extractItemsFromContent(content);
      allItems.push(...items);
    }
    if (allItems.length === 0) {
      throw new Error("No items found in content payload.");
    }
    const results = [];
    for (const item of allItems) {
      const res = await bring.saveItem(listUuid, item.name, item.spec);
      results.push({ item: item.name, spec: item.spec, result: res });
    }
    console.log(JSON.stringify({ listUuid, added: results }, null, 2));
    return;
  }

  const items = itemsRaw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const results = [];
  for (const item of items) {
    const res = await bring.saveItem(listUuid, item, "");
    results.push({ item, result: res });
  }

  console.log(JSON.stringify({ listUuid, added: results }, null, 2));
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
