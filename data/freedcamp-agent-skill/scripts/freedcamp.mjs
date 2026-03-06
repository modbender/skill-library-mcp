#!/usr/bin/env node
/**
 * Freedcamp CLI for OpenClaw / Clawdbot skills
 *
 * - Authentication: HMAC-SHA1 secured credentials (API Key + API Secret)
 * - Zero external dependencies (Node 18+)
 * - JSON-only output (stdout)
 *
 * Intended usage: the agent calls this script with a single command per run.
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";

const API_BASE = "https://freedcamp.com/api/v1";

const TOKEN_ENV_VARS_KEY = ["FREEDCAMP_API_KEY"];
const TOKEN_ENV_VARS_SECRET = ["FREEDCAMP_API_SECRET"];

const DEFAULT_SESSION_PATH = process.env.FREEDCAMP_SESSION_PATH ||
  path.join(os.homedir(), ".openclaw", "skills", "freedcamp-session.json");

/** -------------------------------------------------------------------------- */
/** Constants                                                                  */
/** -------------------------------------------------------------------------- */

const STATUS_MAP = {
  not_started: 0,
  completed: 1,
  in_progress: 2,
  invalid: 3,
  review: 4,
};

const STATUS_NAMES = {
  0: "not_started",
  1: "completed",
  2: "in_progress",
  3: "invalid",
  4: "review",
};

const PRIORITY_NAMES = { 0: "none", 1: "low", 2: "medium", 3: "high" };

const APP_ID_TO_NAME = {
  2: "Tasks",
  3: "Discussions",
  4: "Milestones",
  5: "Time",
  6: "Files",
  7: "Invoices",
  13: "Issue Tracker",
  14: "Wikis",
  16: "CRM",
  17: "Passwords",
  19: "Calendar",
  20: "Invoices Plus",
  37: "Overview",
  47: "Planner",
  48: "Translations",
};

const APP_NAME_TO_ID = {};
for (const [id, name] of Object.entries(APP_ID_TO_NAME)) {
  APP_NAME_TO_ID[name] = Number(id);
}

/** -------------------------------------------------------------------------- */
/** Helpers                                                                    */
/** -------------------------------------------------------------------------- */

function die(msg, extra = undefined, code = 1) {
  const payload = { error: { message: String(msg) } };
  if (extra !== undefined) payload.error.extra = extra;
  process.stdout.write(JSON.stringify(payload, null, 2) + "\n");
  process.exit(code);
}

function emit(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + "\n");
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a) continue;

    if (a.startsWith("--") && a.includes("=")) {
      const [k, ...rest] = a.slice(2).split("=");
      out[k] = rest.join("=") || true;
      continue;
    }

    if (a.startsWith("--")) {
      const k = a.slice(2);
      const next = argv[i + 1];
      if (next !== undefined && !String(next).startsWith("--")) {
        out[k] = next;
        i++;
      } else {
        out[k] = true;
      }
      continue;
    }

    out._.push(a);
  }
  return out;
}

function asInt(v, def = undefined) {
  if (v === undefined || v === null || v === "") return def;
  const n = Number(v);
  if (!Number.isFinite(n)) return def;
  return Math.trunc(n);
}

function asBool(v, def = undefined) {
  if (v === undefined || v === null) return def;
  if (typeof v === "boolean") return v;
  const s = String(v).trim().toLowerCase();
  if (["true", "1", "yes"].includes(s)) return true;
  if (["false", "0", "no"].includes(s)) return false;
  return def;
}

function resolveStatusValue(input) {
  if (input === undefined || input === null) return undefined;
  const s = String(input).trim().toLowerCase();
  if (STATUS_MAP[s] !== undefined) return STATUS_MAP[s];
  const n = Number(s);
  if (Number.isFinite(n) && n >= 0 && n <= 4) return n;
  die(`Invalid status: "${input}". Use: not_started, completed, in_progress, invalid, review (or 0-4)`);
}

function resolveAppId(appName) {
  if (appName === undefined) return 2; // default to Tasks
  const id = APP_NAME_TO_ID[appName];
  if (id !== undefined) return id;
  // try case-insensitive
  for (const [name, appId] of Object.entries(APP_NAME_TO_ID)) {
    if (name.toLowerCase() === String(appName).toLowerCase()) return appId;
  }
  die(`Unknown app name: "${appName}". Valid: ${Object.keys(APP_NAME_TO_ID).join(", ")}`);
}

/** -------------------------------------------------------------------------- */
/** Auth & HTTP                                                                */
/** -------------------------------------------------------------------------- */

function getCredentials() {
  let apiKey, apiSecret;
  for (const v of TOKEN_ENV_VARS_KEY) {
    if (process.env[v]) { apiKey = process.env[v]; break; }
  }
  for (const v of TOKEN_ENV_VARS_SECRET) {
    if (process.env[v]) { apiSecret = process.env[v]; break; }
  }
  if (!apiKey || !apiSecret) {
    die("FREEDCAMP_API_KEY and FREEDCAMP_API_SECRET must be set as environment variables.");
  }
  return { apiKey, apiSecret };
}

function generateAuthParams(apiKey, apiSecret) {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const message = apiKey + timestamp;
  const hash = crypto.createHmac("sha1", apiSecret).update(message).digest("hex");
  return { api_key: apiKey, timestamp, hash };
}

/** Session management */

function loadSession() {
  try {
    if (fs.existsSync(DEFAULT_SESSION_PATH)) {
      const data = JSON.parse(fs.readFileSync(DEFAULT_SESSION_PATH, "utf-8"));
      return data;
    }
  } catch { /* ignore */ }
  return null;
}

function saveSession(sessionData) {
  const dir = path.dirname(DEFAULT_SESSION_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(DEFAULT_SESSION_PATH, JSON.stringify(sessionData, null, 2), "utf-8");
}

async function apiRequest(method, endpoint, { body, params, creds, session } = {}) {
  const url = new URL(API_BASE + endpoint);

  let headers = { "Content-Type": "application/json", Accept: "application/json" };

  if (session && session.sessionToken && session.userId) {
    headers["X-Freedcamp-API-Token"] = session.sessionToken;
    headers["X-Freedcamp-User-Id"] = session.userId;
  } else if (creds) {
    const authParams = generateAuthParams(creds.apiKey, creds.apiSecret);
    for (const [k, v] of Object.entries(authParams)) {
      url.searchParams.set(k, v);
    }
  }

  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (Array.isArray(v)) {
        for (const item of v) url.searchParams.append(k, String(item));
      } else if (v !== null && v !== undefined) {
        url.searchParams.set(k, String(v));
      }
    }
  }

  const fetchOpts = { method, headers };
  if (body && (method === "POST" || method === "PUT" || method === "PATCH")) {
    fetchOpts.body = JSON.stringify(body);
  }

  const res = await fetch(url.toString(), fetchOpts);

  if (res.status === 401 && session) {
    // Session expired, try re-auth
    return null; // signal to caller to refresh
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    die(`API ${method} ${endpoint} returned ${res.status}`, { body: text });
  }

  const data = await res.json();
  return data;
}

async function ensureSession(creds) {
  let session = loadSession();
  if (session && session.sessionToken && session.userId) {
    return session;
  }
  return await refreshSession(creds);
}

async function refreshSession(creds) {
  const res = await apiRequest("GET", "/sessions/current", { creds });
  const sessionData = res?.data || res;

  const sessionToken = sessionData?.api_token || sessionData?.token || null;
  const userId = sessionData?.user_id || null;

  const toSave = {
    sessionData,
    sessionToken,
    userId,
    lastUpdated: new Date().toISOString(),
  };
  saveSession(toSave);
  return toSave;
}

async function apiWithSession(method, endpoint, opts = {}) {
  const creds = getCredentials();
  let session = await ensureSession(creds);

  let result = await apiRequest(method, endpoint, { ...opts, session, creds });
  if (result === null) {
    // 401 - refresh and retry
    session = await refreshSession(creds);
    result = await apiRequest(method, endpoint, { ...opts, session, creds });
  }
  return result;
}

/** -------------------------------------------------------------------------- */
/** Commands                                                                   */
/** -------------------------------------------------------------------------- */

async function cmdMe() {
  const creds = getCredentials();
  const session = await ensureSession(creds);
  const sd = session.sessionData;
  emit({
    user_id: session.userId,
    projects_count: sd?.projects?.length || 0,
    users_count: sd?.users?.length || 0,
    groups_count: sd?.groups?.length || 0,
    notifications_count: sd?.notifications_count || 0,
  });
}

async function cmdGroupsProjects() {
  const creds = getCredentials();
  const session = await ensureSession(creds);
  const sd = session.sessionData;

  if (!sd || !sd.groups) die("No session data available. Try refreshing.");

  const groups = [];
  for (const group of sd.groups) {
    const groupObj = {
      name: group.name,
      id: group.group_id,
      applications: (group.applications || []).map(appId => APP_ID_TO_NAME[appId] || `unknown(${appId})`),
      projects: [],
    };

    for (const projectId of group.projects || []) {
      const project = (sd.projects || []).find(p => p.id === projectId);
      if (!project) continue; // archived/deleted
      groupObj.projects.push({
        id: project.id,
        project_name: project.project_name,
        applications: (project.applications || []).map(appId => APP_ID_TO_NAME[appId] || `unknown(${appId})`),
      });
    }

    groups.push(groupObj);
  }

  emit(groups);
}

async function cmdTasks(args) {
  const projectId = args.project;
  const limit = asInt(args.limit, 200);
  const offset = asInt(args.offset, 0);
  const all = asBool(args.all, false);

  const params = { limit, offset };
  if (projectId) params.project_id = projectId;

  // Status filter
  if (args.status) {
    const statuses = String(args.status).split(",").map(s => s.trim());
    for (const s of statuses) {
      const val = resolveStatusValue(s);
      params["status[]"] = params["status[]"] || [];
      if (Array.isArray(params["status[]"])) {
        params["status[]"].push(val);
      }
    }
  }

  // Assigned filter
  if (args.assigned_to) {
    const ids = String(args.assigned_to).split(",").map(s => s.trim());
    params["assigned_to_id[]"] = ids;
  }

  // Date filters
  if (args.due_from) params["due_date[from]"] = args.due_from;
  if (args.due_to) params["due_date[to]"] = args.due_to;
  if (args.created_from) params["created_date[from]"] = args.created_from;
  if (args.created_to) params["created_date[to]"] = args.created_to;

  // List status
  if (args.list_status) params.list_status = args.list_status;
  if (asBool(args.with_archived, false)) params.f_with_archived = 1;

  if (!all) {
    const res = await apiWithSession("GET", "/tasks", { params });
    const data = res?.data || res;
    emit({ tasks: data.tasks || [], meta: data.meta || {} });
    return;
  }

  // Auto-paginate
  const allTasks = [];
  let currentOffset = offset;
  let hasMore = true;
  while (hasMore) {
    params.offset = currentOffset;
    params.limit = limit;
    const res = await apiWithSession("GET", "/tasks", { params });
    const data = res?.data || res;
    const tasks = data.tasks || [];
    allTasks.push(...tasks);
    hasMore = data.meta?.has_more || false;
    currentOffset += limit;
  }

  emit({ tasks: allTasks, total: allTasks.length });
}

async function cmdTask(args) {
  const taskId = args._[1];
  if (!taskId) die("Usage: task <task_id>");

  const res = await apiWithSession("GET", `/tasks/${taskId}`);
  const data = res?.data || res;
  emit(data);
}

async function cmdCreateTask(args) {
  const projectId = args.project;
  const title = args.title;
  if (!projectId) die("--project is required");
  if (!title) die("--title is required");

  const body = { title, project_id: projectId };
  if (args.description) body.description = args.description;
  if (args.task_group) body.task_group_id = args.task_group;

  const res = await apiWithSession("POST", "/tasks", { body });
  emit(res?.data || res);
}

async function cmdCreateTaskByName(args) {
  const projectName = args.project_name;
  const appName = args.app_name || "Tasks";
  const title = args.title;
  if (!projectName) die("--project_name is required");
  if (!title) die("--title is required");

  const creds = getCredentials();
  const session = await ensureSession(creds);
  const sd = session.sessionData;

  const project = (sd.projects || []).find(p => p.project_name === projectName);
  if (!project) {
    die(`Project "${projectName}" not found. Use "groups-projects" to list available projects.`);
  }

  const appId = resolveAppId(appName);
  if (appId !== 2) {
    die(`Currently only Tasks (app_id=2) is supported for creation. Got app "${appName}" (id=${appId}).`);
  }

  const body = { title, project_id: project.id };
  if (args.description) body.description = args.description;
  if (args.task_group) body.task_group_id = args.task_group;

  const res = await apiWithSession("POST", "/tasks", { body });
  emit(res?.data || res);
}

async function cmdUpdateTask(args) {
  const taskId = args._[1];
  if (!taskId) die("Usage: update-task <task_id> [--title ...] [--status ...] [--description ...]");

  const body = {};
  if (args.title) body.title = args.title;
  if (args.description) body.description = args.description;
  if (args.task_group) body.task_group_id = args.task_group;
  if (args.status !== undefined) body.status = resolveStatusValue(args.status);

  if (Object.keys(body).length === 0) die("No fields to update. Use --title, --status, --description, or --task_group.");

  const res = await apiWithSession("POST", `/tasks/${taskId}`, { body });
  emit(res?.data || res);
}

async function cmdTaskLists(args) {
  const projectId = args.project;
  const appId = asInt(args.app_id, 2);
  if (!projectId) die("--project is required");

  const res = await apiWithSession("GET", `/lists/${appId}`, { params: { project_id: projectId } });
  emit(res?.data || res);
}

async function cmdComment(args) {
  const itemId = args._[1];
  if (!itemId) die("Usage: comment <item_id> --app_name <name> --text <text> | --html <html>");

  const appName = args.app_name || "Tasks";
  const appId = resolveAppId(appName);

  let description;
  if (args.html) {
    description = args.html;
  } else if (args.text) {
    description = `<p>${args.text}</p>`;
  } else {
    die("--text or --html is required");
  }

  const body = { item_id: itemId, app_id: appId, description };
  const res = await apiWithSession("POST", "/comments", { body });
  emit(res?.data || res);
}

async function cmdNotifications() {
  const sixtyDaysAgo = Math.floor(Date.now() / 1000) - (60 * 24 * 60 * 60);
  const res = await apiWithSession("GET", "/notifications", {
    params: { following: 1, from_ts: sixtyDaysAgo },
  });
  emit(res?.data || res);
}

async function cmdMarkRead(args) {
  const uid = args._[1];
  if (!uid) die("Usage: mark-read <notification_uid>");

  const body = {
    new_state: "read",
    items: [{ item_u_key: uid }],
  };
  const res = await apiWithSession("POST", "/notifications", { body });
  emit(res?.data || res);
}

async function cmdHelp() {
  emit({
    commands: {
      me: "Show session info (user ID, project/group/user counts)",
      "groups-projects": "List all groups, projects, and their apps",
      tasks: "List tasks (--project, --status, --assigned_to, --all, etc.)",
      task: "Get single task with comments and files: task <task_id>",
      "create-task": "Create a task (--project, --title, --description, --task_group)",
      "create-task-by-name": "Create task by project name (--project_name, --app_name, --title)",
      "update-task": "Update a task: update-task <task_id> --title/--status/--description",
      "task-lists": "List task lists/groups (--project, --app_id)",
      comment: "Add comment: comment <item_id> --app_name --text/--html",
      notifications: "Fetch recent notifications (last 60 days)",
      "mark-read": "Mark notification as read: mark-read <uid>",
      help: "Show this help",
    },
    statuses: STATUS_MAP,
    app_names: Object.keys(APP_NAME_TO_ID),
  });
}

/** -------------------------------------------------------------------------- */
/** Main                                                                       */
/** -------------------------------------------------------------------------- */

const COMMANDS = {
  me: cmdMe,
  "groups-projects": cmdGroupsProjects,
  tasks: cmdTasks,
  task: cmdTask,
  "create-task": cmdCreateTask,
  "create-task-by-name": cmdCreateTaskByName,
  "update-task": cmdUpdateTask,
  "task-lists": cmdTaskLists,
  comment: cmdComment,
  notifications: cmdNotifications,
  "mark-read": cmdMarkRead,
  help: cmdHelp,
};

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];

  if (!cmd || cmd === "help" || args.help) {
    await cmdHelp();
    return;
  }

  const handler = COMMANDS[cmd];
  if (!handler) {
    die(`Unknown command: "${cmd}". Run with "help" to see available commands.`);
  }

  await handler(args);
}

main().catch((err) => {
  die(err.message || String(err));
});
