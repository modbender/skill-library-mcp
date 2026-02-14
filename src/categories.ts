import type { SkillEntry } from "./types.js";

const CATEGORY_KEYWORDS: [string, string[]][] = [
  ["Frontend", ["react", "angular", "vue", "svelte", "nextjs", "frontend", "css", "tailwind", "ui", "ux"]],
  ["Backend", ["backend", "nodejs", "express", "nestjs", "fastapi", "django", "rails", "api", "rest", "graphql"]],
  ["AI & LLM", ["ai", "llm", "agent", "prompt", "rag", "claude", "openai", "embedding", "ml"]],
  ["DevOps & Infra", ["docker", "kubernetes", "terraform", "aws", "gcp", "azure", "deployment", "infrastructure"]],
  ["Data & Databases", ["data", "database", "sql", "postgres", "mongodb", "redis", "analytics", "pipeline", "etl"]],
  ["Security", ["security", "penetration", "vulnerability", "audit", "owasp", "xss", "encryption"]],
  ["Testing", ["test", "tdd", "testing", "e2e", "vitest", "jest", "playwright"]],
  ["Mobile", ["mobile", "react-native", "flutter", "ios", "android", "expo"]],
  ["Automation", ["automation", "workflow", "n8n", "zapier", "scraping", "bot"]],
  ["Python", ["python", "django", "flask", "fastapi", "pandas"]],
  ["TypeScript & JS", ["typescript", "javascript", "deno", "bun"]],
  ["Architecture", ["architecture", "microservices", "system-design", "patterns", "monorepo"]],
];

export function buildCategories(entries: SkillEntry[]): Map<string, string[]> {
  const categories = new Map<string, string[]>();

  for (const entry of entries) {
    const text = `${entry.dirName} ${entry.frontmatter.description}`.toLowerCase();
    let matched = false;

    for (const [category, keywords] of CATEGORY_KEYWORDS) {
      if (keywords.some((kw) => text.includes(kw))) {
        const list = categories.get(category) ?? [];
        list.push(entry.dirName);
        categories.set(category, list);
        matched = true;
        break;
      }
    }

    if (!matched) {
      const list = categories.get("Other") ?? [];
      list.push(entry.dirName);
      categories.set("Other", list);
    }
  }

  return categories;
}
