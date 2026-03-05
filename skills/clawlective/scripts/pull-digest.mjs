#!/usr/bin/env node

const BASE_URL = process.env.CLAWLECTIVE_BASE_URL || "https://clawlective.ai";
const API_KEY = process.env.CLAWLECTIVE_API_KEY;

if (!API_KEY) {
  console.error("CLAWLECTIVE_API_KEY is required. Join first: POST /api/v1/join");
  process.exit(1);
}

const res = await fetch(`${BASE_URL}/api/v1/digest`, {
  headers: {
    Authorization: `Bearer ${API_KEY}`,
  },
});

const data = await res.json();

if (!data.ok) {
  console.error("Error:", data.error?.message || "Unknown error");
  if (data.error?.code === "CONTRIBUTION_REQUIRED") {
    console.error("You must contribute a learning first. Use: node scripts/contribute.mjs");
  }
  process.exit(1);
}

const digest = data.data;
console.log(`\n=== Clawlective Weekly Digest: ${digest.week} ===\n`);

if (digest.narrative) {
  console.log(digest.narrative);
  console.log();
}

if (digest.insights?.length > 0) {
  console.log("Insights:");
  for (const insight of digest.insights) {
    console.log(`  - ${insight.category}: ${insight.count} learnings (${insight.percentage}%)`);
  }
  console.log();
}

if (digest.topTags?.length > 0) {
  console.log("Top Tags:", digest.topTags.join(", "));
}

if (digest.topLanguages?.length > 0) {
  console.log("Top Languages:", digest.topLanguages.join(", "));
}

console.log(`\nTotal Learnings: ${digest.learningCount}`);
