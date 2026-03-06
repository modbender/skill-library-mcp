#!/usr/bin/env node

const args = process.argv.slice(2);

function getArg(name, def = undefined) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  return args[i + 1] ?? def;
}

function hasArg(name) {
  return args.includes(`--${name}`);
}

function usage() {
  console.error(`Usage:
  issues.mjs get --id <issueId>
  issues.mjs list [--project-id <idOrIdentifier>] [--status-id <id|open|closed|*>] [--assigned-to-id <id|me>] [--limit <n>] [--offset <n>] [--sort <field:asc|desc>] [--query-id <id>]
  issues.mjs update --id <issueId> [--subject <text>] [--description <text>] [--status-id <id>] [--priority-id <id>] [--assigned-to-id <id>] [--done-ratio <0-100>] [--notes <text>]`);
  process.exit(1);
}

const command = args[0];
if (!command || !["get", "list", "update"].includes(command)) usage();

const REDMINE_URL = process.env.REDMINE_URL?.replace(/\/$/, "");
const REDMINE_API_KEY = process.env.REDMINE_API_KEY;
const REDMINE_USERNAME = process.env.REDMINE_USERNAME;
const REDMINE_PASSWORD = process.env.REDMINE_PASSWORD;

if (!REDMINE_URL) {
  console.error("Missing REDMINE_URL");
  process.exit(2);
}

const headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
};

if (REDMINE_API_KEY) {
  headers["X-Redmine-API-Key"] = REDMINE_API_KEY;
}

const auth = (!REDMINE_API_KEY && REDMINE_USERNAME && REDMINE_PASSWORD)
  ? `Basic ${Buffer.from(`${REDMINE_USERNAME}:${REDMINE_PASSWORD}`).toString("base64")}`
  : null;
if (auth) headers["Authorization"] = auth;

if (!headers["X-Redmine-API-Key"] && !headers["Authorization"]) {
  console.error("Missing auth: set REDMINE_API_KEY or REDMINE_USERNAME+REDMINE_PASSWORD");
  process.exit(3);
}

async function requestJson(path, { method = "GET", params = {}, body = undefined } = {}) {
  const url = new URL(`${REDMINE_URL}${path}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && `${v}`.length > 0) url.searchParams.set(k, `${v}`);
  }

  const res = await fetch(url, {
    headers,
    method,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    console.error(JSON.stringify({
      ok: false,
      status: res.status,
      statusText: res.statusText,
      url: url.toString(),
      error: data,
    }, null, 2));
    process.exit(10);
  }

  return data;
}

(async () => {
  if (command === "get") {
    const id = getArg("id");
    if (!id) usage();
    const include = getArg("include", "attachments,journals,children,relations,watchers");
    const data = await requestJson(`/issues/${encodeURIComponent(id)}.json`, { params: { include } });
    console.log(JSON.stringify(data, null, 2));
    return;
  }

  if (command === "list") {
    const params = {
      project_id: getArg("project-id"),
      status_id: getArg("status-id", "open"),
      assigned_to_id: getArg("assigned-to-id"),
      query_id: getArg("query-id"),
      sort: getArg("sort", "updated_on:desc"),
      limit: getArg("limit", "25"),
      offset: getArg("offset", "0"),
    };

    if (hasArg("all-status")) params.status_id = "*";

    const data = await requestJson(`/issues.json`, { params });
    console.log(JSON.stringify(data, null, 2));
    return;
  }

  if (command === "update") {
    const id = getArg("id");
    if (!id) usage();

    const issue = {};

    const maybe = (key, val) => {
      if (val !== undefined && val !== null && `${val}`.length > 0) issue[key] = val;
    };

    maybe("subject", getArg("subject"));
    maybe("description", getArg("description"));
    maybe("status_id", getArg("status-id"));
    maybe("priority_id", getArg("priority-id"));
    maybe("assigned_to_id", getArg("assigned-to-id"));

    const doneRatio = getArg("done-ratio");
    if (doneRatio !== undefined) {
      const n = Number(doneRatio);
      if (!Number.isFinite(n) || n < 0 || n > 100) {
        console.error("--done-ratio must be a number between 0 and 100");
        process.exit(4);
      }
      issue.done_ratio = n;
    }

    maybe("notes", getArg("notes"));

    if (Object.keys(issue).length === 0) {
      console.error("No update fields provided");
      process.exit(5);
    }

    await requestJson(`/issues/${encodeURIComponent(id)}.json`, {
      method: "PUT",
      body: { issue },
    });

    const refreshed = await requestJson(`/issues/${encodeURIComponent(id)}.json`, {
      params: { include: "attachments,journals,children,relations,watchers" },
    });
    console.log(JSON.stringify(refreshed, null, 2));
    return;
  }
})();
