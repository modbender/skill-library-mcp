"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TECH_TERMS = [
  "python", "javascript", "typescript", "rust", "go", "java", "ruby",
  "react", "vue", "angular", "node", "docker", "kubernetes", "k8s",
  "aws", "gcp", "azure", "terraform", "ansible",
  "sql", "postgres", "mysql", "mongodb", "redis",
  "api", "rest", "graphql", "grpc",
  "test", "testing", "unittest", "pytest", "jest",
  "security", "auth", "authentication", "authorization",
  "ci", "cd", "pipeline", "deploy", "deployment",
  "code", "review", "refactor", "debug", "debugging",
  "git", "github", "gitlab", "bitbucket",
  "linux", "bash", "shell", "cli",
  "frontend", "backend", "fullstack", "devops", "sre",
  "performance", "optimization", "monitoring", "logging",
  "documentation", "docs", "readme", "comment",
  "architecture", "design", "pattern", "patterns",
  "database", "cache", "queue", "message",
  "microservice", "monolith", "serverless", "lambda",
  "machine learning", "ml", "ai", "data", "analytics",
];

/**
 * Extract a summary from agent markdown content.
 * Skips YAML frontmatter, finds first non-empty non-header lines,
 * joins them, truncates at 200 chars.
 */
function extractSummary(content) {
  const lines = content.trim().split("\n");

  // Skip YAML frontmatter if present
  let startIdx = 0;
  if (lines.length > 0 && lines[0].trim() === "---") {
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === "---") {
        startIdx = i + 1;
        break;
      }
    }
  }

  // Find first non-empty, non-header lines
  const summaryLines = [];
  for (let i = startIdx; i < lines.length; i++) {
    const stripped = lines[i].trim();
    if (!stripped) {
      if (summaryLines.length > 0) break;
      continue;
    }
    if (stripped.startsWith("#")) continue;
    summaryLines.push(stripped);
    if (summaryLines.join(" ").length > 150) break;
  }

  let summary = summaryLines.join(" ");
  if (summary.length > 200) {
    summary = summary.slice(0, 197) + "...";
  }

  return summary || "No description available";
}

/**
 * Extract keywords from agent content.
 * Matches against known tech terms and extracts words from headers.
 * Returns up to 20 keywords.
 */
function extractKeywords(content) {
  const contentLower = content.toLowerCase();
  const foundKeywords = [];

  for (const term of TECH_TERMS) {
    if (contentLower.includes(term)) {
      foundKeywords.push(term);
    }
  }

  // Also extract words from headers
  for (const line of content.split("\n")) {
    if (line.trim().startsWith("#")) {
      const words = line.toLowerCase().replace(/#/g, "").trim().split(/\s+/);
      for (const word of words) {
        const cleanWord = word.replace(/[^a-z0-9]/g, "");
        if (cleanWord.length > 3 && !foundKeywords.includes(cleanWord)) {
          foundKeywords.push(cleanWord);
        }
      }
    }
  }

  return foundKeywords.slice(0, 20);
}

/**
 * Compute a short MD5 content hash (first 8 hex chars).
 */
function contentHash(content) {
  return crypto.createHash("md5").update(content).digest("hex").slice(0, 8);
}

/**
 * Parse an agent .md file and return its metadata.
 * Returns null if the file cannot be read.
 */
function parseAgentFile(filepath) {
  try {
    const content = fs.readFileSync(filepath, "utf-8");
    const name = path.basename(filepath, path.extname(filepath));

    return {
      name,
      filename: path.basename(filepath),
      path: filepath,
      summary: extractSummary(content),
      keywords: extractKeywords(content),
      token_estimate: Math.floor(content.length / 4),
      content_hash: contentHash(content),
    };
  } catch (e) {
    process.stderr.write(`Warning: Could not parse ${filepath}: ${e.message}\n`);
    return null;
  }
}

module.exports = {
  extractSummary,
  extractKeywords,
  contentHash,
  parseAgentFile,
};
