import { IntercomClient } from "intercom-client";

function mustEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}

// Singleton client (module-level); Clawhub may keep this module warm.
const intercom = new IntercomClient({
  tokenAuth: { token: mustEnv("INTERCOM_ACCESS_TOKEN") },
});

/**
 * Clawhub entrypoint: default(input)
 *
 * Supported actions (READ):
 * - "conversations.list"
 * - "conversations.find"
 * - "conversations.search"
 */
export default async function skill(input = {}) {
  const action = input?.action;

  switch (action) {
    case "conversations.list":
      return await conversationsList(input);

    case "conversations.find":
      return await conversationsFind(input);

    case "conversations.search":
      return await conversationsSearch(input);

    default:
      return {
        ok: false,
        error: `Unknown or missing action: ${String(action)}`,
        supported_actions: [
          "conversations.list",
          "conversations.find",
          "conversations.search",
        ],
      };
  }
}

// ---- READ: list conversations ----
async function conversationsList(input) {
  const per_page = clampInt(input.per_page, 1, 150);
  const starting_after = optString(input.starting_after);

  const page = await intercom.conversations.list({
    ...(per_page !== undefined ? { per_page } : {}),
    ...(starting_after ? { starting_after } : {}),
  });

  return normalizePage("conversations.list", page);
}

// ---- READ: find conversation by id ----
async function conversationsFind(input) {
  const conversation_id = optString(input.conversation_id);
  if (!conversation_id) throw new Error("conversation_id is required");

  const display_as = optString(input.display_as); // "plaintext" | "html"
  const include_translations =
    input.include_translations === undefined ? undefined : !!input.include_translations;

  const convo = await intercom.conversations.find({
    conversation_id,
    ...(display_as ? { display_as } : {}),
    ...(include_translations !== undefined ? { include_translations } : {}),
  });

  return { ok: true, action: "conversations.find", conversation: convo };
}

// ---- READ: search conversations ----
async function conversationsSearch(input) {
  if (!input.query) throw new Error("query is required (Intercom search query object)");

  const page = await intercom.conversations.search({
    query: input.query,
    ...(input.pagination ? { pagination: input.pagination } : {}),
  });

  return normalizePage("conversations.search", page);
}

// ---- helpers ----
function normalizePage(action, page) {
  const conversations =
    typeof page?.getItems === "function" ? page.getItems() : page?.items ?? [];

  const next_starting_after =
    page?.pages?.next?.starting_after ??
    page?.response?.pages?.next?.starting_after ??
    null;

  return { ok: true, action, conversations, next_starting_after };
}

function clampInt(v, min, max) {
  if (v === undefined || v === null || v === "") return undefined;
  const n = Number(v);
  if (!Number.isFinite(n)) throw new Error(`Invalid integer: ${v}`);
  const i = Math.trunc(n);
  return Math.min(max, Math.max(min, i));
}

function optString(v) {
  if (v === undefined || v === null) return undefined;
  const s = String(v).trim();
  return s.length ? s : undefined;
}
