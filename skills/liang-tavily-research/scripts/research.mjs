#!/usr/bin/env node

function usage() {
  console.error(`Usage: research.mjs "query" [options]

Options:
  --model <model>   Model: mini, pro, auto (default: mini)
  --output <file>   Save report to file
  --json            Output raw JSON

Examples:
  research.mjs "What is retrieval augmented generation?"
  research.mjs "LangGraph vs CrewAI" --pro
  research.mjs "Fintech landscape 2025" --pro --output report.md`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let model = "mini";
let outputFile = null;
let outputJson = false;

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "--model") {
    model = args[i + 1] ?? "mini";
    i++;
    continue;
  }
  if (a === "--output") {
    outputFile = args[i + 1];
    i++;
    continue;
  }
  if (a === "--json") {
    outputJson = true;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Error: TAVILY_API_KEY not set");
  console.error("Get your API key at https://tavily.com");
  process.exit(1);
}

const body = {
  query: query,
  search_depth: "advanced",
  include_answer: true,
  include_raw_content: false,
  max_results: 10,
  topic: "general",
};

// Map model to search_depth
if (model === "mini") {
  body.search_depth = "basic";
  body.max_results = 5;
} else if (model === "pro") {
  body.search_depth = "advanced";
  body.max_results = 10;
}

const resp = await fetch("https://api.tavily.com/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${apiKey}`,
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Research failed (${resp.status}): ${text}`);
}

const data = await resp.json();

if (outputJson) {
  console.log(JSON.stringify(data, null, 2));
  process.exit(0);
}

// Build report
let report = "";

report += `# Research Report: ${query}\n\n`;

if (data.answer) {
  report += `## Summary\n\n${data.answer}\n\n`;
  report += `---\n\n`;
}

// Sources
const results = data.results ?? [];
report += `## Sources (${results.length})\n\n`;

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.url ?? "").trim();
  const content = String(r?.content ?? "").trim();
  const score = r?.score ? ` (relevance: ${(r.score * 100).toFixed(0)}%)` : "";

  if (!title || !url) continue;

  report += `### ${title}${score}\n\n`;
  report += `${url}\n\n`;
  if (content) {
    report += `${content}\n\n`;
  }
}

if (data.response_time) {
  report += `\n---\n\nResponse time: ${data.response_time}s\n`;
}

// Output
if (outputFile) {
  const fs = await import("fs");
  fs.writeFileSync(outputFile, report, "utf-8");
  console.log(`Report saved to ${outputFile}`);
} else {
  console.log(report);
}