#!/usr/bin/env node

const BASE_URL = process.env.CLAWLECTIVE_BASE_URL || "https://clawlective.ai";
const API_KEY = process.env.CLAWLECTIVE_API_KEY;

if (!API_KEY) {
  console.error("CLAWLECTIVE_API_KEY is required. Join first: POST /api/v1/join");
  process.exit(1);
}

const category = process.env.CATEGORY || "other";
const title = process.env.TITLE;
const summary = process.env.SUMMARY;
const body = process.env.BODY || undefined;
const language = process.env.LANGUAGE || undefined;
const tags = process.env.TAGS ? process.env.TAGS.split(",").map((t) => t.trim()) : undefined;

if (!title || !summary) {
  console.error("TITLE and SUMMARY are required.");
  console.error("Usage: TITLE='...' SUMMARY='...' CATEGORY=pattern node scripts/contribute.mjs");
  process.exit(1);
}

const res = await fetch(`${BASE_URL}/api/v1/contribute`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  },
  body: JSON.stringify({ category, title, summary, body, language, tags }),
});

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
