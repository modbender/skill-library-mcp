/**
 * Notion Clipper - Save web pages to Notion
 *
 * NETWORK COMPATIBILITY:
 * - Use tsx runtime (NOT bun) - bun has proxy issues with https module
 * - Unset proxy env vars for direct connection: unset http_proxy https_proxy all_proxy
 * - Script includes 6 retries with exponential backoff for unstable networks
 * - All invalid URLs are removed to avoid Notion API validation errors
 *
 * RECOMMENDED USAGE:
 * (cd scripts && unset http_proxy https_proxy all_proxy && npx -y tsx main.ts <url> --database-name "Resources")
 */

import { createInterface } from "node:readline";
import process from "node:process";

import {
  CdpConnection,
  getFreePort,
  launchChrome,
  waitForChromeDebugPort,
  waitForNetworkIdle,
  waitForPageLoad,
  autoScroll,
  evaluateScript,
  killChrome,
} from "./cdp.js";
import {
  cleanupAndExtractScript,
  htmlToMarkdown,
  type PageMetadata,
  type ConversionResult,
} from "./html-to-markdown.js";
import {
  convertMarkdownToNotionBlocks,
  createBookmarkBlock,
  createDividerBlock,
} from "./markdown-to-notion.js";
import {
  readNotionApiKey,
  createPageInDatabase,
  appendBlocksToPage,
  createChildPage,
  findDatabaseByName,
  listAllDatabases,
  type NotionBlock,
} from "./notion-api.js";
import {
  DEFAULT_TIMEOUT_MS,
  CDP_CONNECT_TIMEOUT_MS,
  NETWORK_IDLE_TIMEOUT_MS,
  POST_LOAD_DELAY_MS,
  SCROLL_STEP_WAIT_MS,
  SCROLL_MAX_STEPS,
} from "./constants.js";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface Args {
  url: string;
  databaseId?: string;
  databaseName?: string;
  pageId?: string;
  wait: boolean;
  timeout: number;
  includeBookmark: boolean;
  listDatabases: boolean;
}

function parseArgs(argv: string[]): Args {
  const args: Args = {
    url: "",
    wait: false,
    timeout: DEFAULT_TIMEOUT_MS,
    includeBookmark: true,
    listDatabases: false,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--wait" || arg === "-w") {
      args.wait = true;
    } else if (arg === "--database" || arg === "-d") {
      args.databaseId = argv[++i];
    } else if (arg === "--database-name" || arg === "-n") {
      args.databaseName = argv[++i];
    } else if (arg === "--page" || arg === "-p") {
      args.pageId = argv[++i];
    } else if (arg === "--timeout" || arg === "-t") {
      args.timeout = parseInt(argv[++i], 10) || DEFAULT_TIMEOUT_MS;
    } else if (arg === "--no-bookmark") {
      args.includeBookmark = false;
    } else if (arg === "--list-databases" || arg === "-l") {
      args.listDatabases = true;
    } else if (!arg.startsWith("-") && !args.url) {
      args.url = arg;
    }
  }
  return args;
}

function printUsage(): void {
  console.log(`
Usage: bun main.ts <url> [options]

Options:
  --database, -d <id>       Save to Notion database by ID
  --database-name, -n <name> Save to Notion database by name (searches for match)
  --page, -p <id>           Append to existing Notion page
  --wait, -w                Wait for user signal before capturing
  --timeout, -t <ms>        Page load timeout (default: 30000)
  --no-bookmark             Don't include bookmark block at the top
  --list-databases, -l      List all accessible databases and exit

Examples:
  bun main.ts https://example.com -n "Resource"
  bun main.ts https://example.com -d abc123
  bun main.ts https://example.com -p def456 --wait
  bun main.ts --list-databases
`);
}

async function waitForUserSignal(): Promise<void> {
  console.log("Page opened. Press Enter when ready to capture...");
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  await new Promise<void>((resolve) => {
    rl.once("line", () => {
      rl.close();
      resolve();
    });
  });
}

async function captureUrl(args: Args): Promise<ConversionResult> {
  const port = await getFreePort();
  const chrome = await launchChrome(args.url, port, false);

  let cdp: CdpConnection | null = null;
  try {
    const wsUrl = await waitForChromeDebugPort(port, 30_000);
    cdp = await CdpConnection.connect(wsUrl, CDP_CONNECT_TIMEOUT_MS);

    const targets = await cdp.send<{
      targetInfos: Array<{ targetId: string; type: string; url: string }>;
    }>("Target.getTargets");
    const pageTarget = targets.targetInfos.find(
      (t) => t.type === "page" && t.url.startsWith("http")
    );
    if (!pageTarget) throw new Error("No page target found");

    const { sessionId } = await cdp.send<{ sessionId: string }>(
      "Target.attachToTarget",
      { targetId: pageTarget.targetId, flatten: true }
    );
    await cdp.send("Network.enable", {}, { sessionId });
    await cdp.send("Page.enable", {}, { sessionId });

    if (args.wait) {
      await waitForUserSignal();
    } else {
      console.log("Waiting for page to load...");
      await Promise.race([waitForPageLoad(cdp, sessionId, 15_000), sleep(8_000)]);
      await waitForNetworkIdle(cdp, sessionId, NETWORK_IDLE_TIMEOUT_MS);
      await sleep(POST_LOAD_DELAY_MS);
      console.log("Scrolling to trigger lazy load...");
      await autoScroll(cdp, sessionId, SCROLL_MAX_STEPS, SCROLL_STEP_WAIT_MS);
      await sleep(POST_LOAD_DELAY_MS);
    }

    console.log("Capturing page content...");
    const extracted = await evaluateScript<{
      title: string;
      description?: string;
      author?: string;
      published?: string;
      html: string;
    }>(cdp, sessionId, cleanupAndExtractScript, args.timeout);

    const metadata: PageMetadata = {
      url: args.url,
      title: extracted.title || new URL(args.url).hostname,
      description: extracted.description,
      author: extracted.author,
      published: extracted.published,
      captured_at: new Date().toISOString(),
    };

    const markdown = htmlToMarkdown(extracted.html);
    return { metadata, markdown };
  } finally {
    if (cdp) {
      try {
        await cdp.send("Browser.close", {}, { timeoutMs: 5_000 });
      } catch {}
      cdp.close();
    }
    killChrome(chrome);
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);

  // Read Notion API key first (needed for all operations)
  console.log("Reading Notion API key...");
  const apiKey = await readNotionApiKey();

  // Handle --list-databases option
  if (args.listDatabases) {
    console.log("Fetching accessible databases...\n");
    const databases = await listAllDatabases(apiKey);
    if (databases.length === 0) {
      console.log("No databases found. Make sure to share databases with your integration.");
    } else {
      console.log("Accessible databases:\n");
      for (const db of databases) {
        console.log(`  Name: ${db.title}`);
        console.log(`  ID:   ${db.id}`);
        console.log(`  URL:  ${db.url}\n`);
      }
    }
    return;
  }

  if (!args.url) {
    printUsage();
    process.exit(1);
  }

  if (!args.databaseId && !args.databaseName && !args.pageId) {
    console.error("Error: You must specify --database, --database-name, or --page");
    printUsage();
    process.exit(1);
  }

  try {
    new URL(args.url);
  } catch {
    console.error(`Invalid URL: ${args.url}`);
    process.exit(1);
  }

  // Resolve database name to ID if provided
  let targetDatabaseId = args.databaseId;
  if (args.databaseName && !targetDatabaseId) {
    console.log(`Searching for database: "${args.databaseName}"...`);
    const db = await findDatabaseByName(apiKey, args.databaseName);
    if (!db) {
      console.error(`Database not found: "${args.databaseName}"`);
      console.log("\nTip: Use --list-databases to see all accessible databases.");
      process.exit(1);
    }
    console.log(`Found database: "${db.title}" (${db.id})`);
    targetDatabaseId = db.id;
  }

  console.log(`Fetching: ${args.url}`);
  console.log(`Mode: ${args.wait ? "wait" : "auto"}`);

  // Capture the web page
  const result = await captureUrl(args);
  console.log(`Title: ${result.metadata.title}`);

  // Convert markdown to Notion blocks
  console.log("Converting to Notion blocks...");
  const contentBlocks = convertMarkdownToNotionBlocks(result.markdown);

  // Build final blocks array
  const blocks: NotionBlock[] = [];

  // Add bookmark block at the top if enabled
  if (args.includeBookmark) {
    blocks.push(createBookmarkBlock(args.url));
    blocks.push(createDividerBlock());
  }

  // Add content blocks
  blocks.push(...contentBlocks);

  // Save to Notion
  if (targetDatabaseId) {
    console.log("Creating page in Notion database...");
    const page = await createPageInDatabase(apiKey, {
      databaseId: targetDatabaseId,
      title: result.metadata.title,
      url: args.url,
      blocks,
    });
    console.log(`Created page: ${page.url}`);
  } else if (args.pageId) {
    console.log("Appending blocks to Notion page...");
    await appendBlocksToPage(apiKey, {
      pageId: args.pageId,
      blocks,
    });
    console.log(`Appended ${blocks.length} blocks to page`);
  }

  console.log("Done!");
}

main().catch((err) => {
  console.error("Error:", err instanceof Error ? err.message : String(err));
  process.exit(1);
});
