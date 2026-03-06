#!/usr/bin/env node

/**
 * Notion Page to Markdown Converter
 * Converts Notion pages to markdown using the Notion API and notion-to-md library
 *
 * Usage:
 *   node convert.js <pageId> [outputPath]
 *   node convert.js <pageId> --database [queryFilter]
 *
 * Environment:
 *   NOTION_API_KEY - Your Notion API token (required)
 *   .env file - Create a .env file with NOTION_API_KEY=your_token
 */

require("dotenv").config();

const { NotionToMarkdown } = require("notion-to-md");
const { Client } = require("@notionhq/client");
const fs = require("fs");
const path = require("path");

// Validate API key
const apiKey = process.env.NOTION_API_KEY;
if (!apiKey) {
  console.error(
    "❌ Error: NOTION_API_KEY environment variable is not set.\n" +
      "Please set your Notion API token:\n" +
      "  export NOTION_API_KEY=your_token_here\n" +
      "See README for how to get your API key."
  );
  process.exit(1);
}

// Initialize clients
const notion = new Client({ auth: apiKey });
const n2m = new NotionToMarkdown({ notionClient: notion });

async function convertPageToMarkdown(pageId) {
  try {
    // Fetch page metadata
    const page = await notion.pages.retrieve({ page_id: pageId });
    const pageTitle =
      page.properties.title?.title?.[0]?.plain_text ||
      page.properties.Name?.title?.[0]?.plain_text ||
      "Untitled";

    // Convert blocks to markdown
    const mdblocks = await n2m.pageToMarkdown(pageId);
    const mdResult = n2m.toMarkdownString(mdblocks);
    const mdString = typeof mdResult === 'string' ? mdResult : mdResult.parent || mdResult;

    return {
      title: pageTitle,
      markdown: mdString,
      pageId: pageId,
    };
  } catch (error) {
    if (error.code === "validation_error") {
      console.error("❌ Error: Invalid page ID format or page not found");
    } else if (error.status === 401) {
      console.error("❌ Error: Invalid Notion API key");
    } else if (error.status === 404) {
      console.error("❌ Error: Page not found or not accessible");
    } else {
      console.error("❌ Error converting page:", error.message);
    }
    process.exit(1);
  }
}

async function convertDatabaseToMarkdown(databaseId, outputDir = "./notion-exports") {
  try {
    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Query database
    const response = await notion.databases.query({ database_id: databaseId });
    const pages = response.results;

    console.log(`📚 Found ${pages.length} pages in database`);

    const results = [];

    for (const page of pages) {
      const pageId = page.id;
      const pageTitle =
        page.properties.title?.title?.[0]?.plain_text ||
        page.properties.Name?.title?.[0]?.plain_text ||
        `Untitled-${pageId.substring(0, 8)}`;

      try {
        const mdblocks = await n2m.pageToMarkdown(pageId);
        const mdResult = n2m.toMarkdownString(mdblocks);
        const mdString = typeof mdResult === 'string' ? mdResult : mdResult.parent || mdResult;

        // Write to file
        const safeFileName = pageTitle
          .replace(/[^\w\s-]/g, "")
          .replace(/\s+/g, "-")
          .toLowerCase();
        const filePath = path.join(outputDir, `${safeFileName}.md`);

        fs.writeFileSync(filePath, mdString);

        results.push({
          title: pageTitle,
          file: path.basename(filePath),
          status: "✅",
        });

        console.log(`✅ Converted: ${pageTitle}`);
      } catch (error) {
        results.push({
          title: pageTitle,
          status: "❌",
          error: error.message,
        });
        console.log(`❌ Failed: ${pageTitle} - ${error.message}`);
      }
    }

    return {
      outputDir,
      totalPages: pages.length,
      results,
    };
  } catch (error) {
    console.error("❌ Error querying database:", error.message);
    process.exit(1);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(
      "Usage: node convert.js <pageId|databaseId> [--database] [outputPath]\n"
    );
    console.log("Examples:");
    console.log("  node convert.js abc123def456 > page.md");
    console.log(
      "  node convert.js abc123def456 --database ./notion-export\n"
    );
    console.log("Environment:");
    console.log("  NOTION_API_KEY=your_token (required)");
    process.exit(0);
  }

  const id = args[0];
  const isDatabase = args.includes("--database");
  const outputPath = args[args.length - 1];

  if (isDatabase) {
    // Database export mode
    const result = await convertDatabaseToMarkdown(id, outputPath);
    console.log(`\n✨ Exported to: ${result.outputDir}`);
  } else {
    // Single page conversion mode
    const result = await convertPageToMarkdown(id);
    process.stdout.write(result.markdown);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
