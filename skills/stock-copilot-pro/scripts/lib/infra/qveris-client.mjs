const BASE_URL = "https://qveris.ai/api/v1";
const DEFAULT_FULL_CONTENT_ALLOWED_HOSTS = ["qveris.ai"];

function timeoutSignal(timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return { signal: controller.signal, cleanup: () => clearTimeout(timer) };
}

export function safeJsonParse(value) {
  if (!value || typeof value !== "string") return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function pickPayload(rawResult) {
  return rawResult?.result?.data ?? rawResult?.data ?? rawResult?.result ?? rawResult ?? {};
}

function pickFullContentFileUrl(rawResult, payload) {
  return (
    payload?.full_content_file_url ??
    rawResult?.result?.full_content_file_url ??
    rawResult?.data?.full_content_file_url ??
    null
  );
}

function isAllowedHost(hostname, allowedHosts = []) {
  const host = String(hostname || "").toLowerCase();
  if (!host) return false;
  for (const allowed of allowedHosts) {
    const base = String(allowed || "").toLowerCase().trim();
    if (!base) continue;
    if (host === base || host.endsWith(`.${base}`)) return true;
  }
  return false;
}

function validateFullContentUrl(rawUrl, allowedHosts = DEFAULT_FULL_CONTENT_ALLOWED_HOSTS) {
  if (!rawUrl || typeof rawUrl !== "string") {
    return { ok: false, reason: "missing full content url", url: null };
  }
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch {
    return { ok: false, reason: "invalid full content url", url: null };
  }
  const protocol = String(parsed.protocol || "").toLowerCase();
  if (protocol !== "https:") {
    return { ok: false, reason: `unsupported protocol: ${protocol || "unknown"}`, url: parsed.toString() };
  }
  if (!isAllowedHost(parsed.hostname, allowedHosts)) {
    return { ok: false, reason: `blocked host: ${parsed.hostname}`, url: parsed.toString() };
  }
  return { ok: true, reason: null, url: parsed.toString() };
}

export function resolveToolPayloadSync(rawResult) {
  const payload = pickPayload(rawResult);
  const truncated = payload?.truncated_content;
  const parsed = safeJsonParse(truncated);
  const fullContentFileUrl = pickFullContentFileUrl(rawResult, payload);
  const hasTruncatedContent = typeof truncated === "string";
  if (parsed != null) {
    return {
      content: parsed,
      meta: {
        contentMode: "truncated_content",
        hasTruncatedContent,
        fullContentFileUrl,
      },
    };
  }
  return {
    content: payload,
    meta: {
      contentMode: "payload",
      hasTruncatedContent,
      fullContentFileUrl,
    },
  };
}

export async function resolveToolPayload(rawResult, options = {}) {
  const initial = resolveToolPayloadSync(rawResult);
  if (initial.meta.contentMode !== "payload") return initial;
  if (!initial.meta.hasTruncatedContent) return initial;
  if (options.fetchFullContent === false) return initial;
  if (!initial.meta.fullContentFileUrl) return initial;

  const allowedHosts = Array.isArray(options.fullContentAllowedHosts) && options.fullContentAllowedHosts.length > 0
    ? options.fullContentAllowedHosts
    : DEFAULT_FULL_CONTENT_ALLOWED_HOSTS;
  const checked = validateFullContentUrl(initial.meta.fullContentFileUrl, allowedHosts);
  if (!checked.ok) {
    return {
      ...initial,
      meta: {
        ...initial.meta,
        fetchError: checked.reason,
      },
    };
  }

  const fetchImpl = options.fetchImpl || fetch;
  const timeoutMs = Number(options.timeoutMs || 10_000);
  const { signal, cleanup } = timeoutSignal(timeoutMs);
  try {
    const res = await fetchImpl(checked.url, { signal });
    if (!res.ok) {
      return {
        ...initial,
        meta: {
          ...initial.meta,
          fetchError: `full content fetch failed: ${res.status}`,
        },
      };
    }
    const fullContent = await res.json();
    return {
      content: fullContent,
      meta: {
        contentMode: "full_content_file_url",
        hasTruncatedContent: true,
        fullContentFileUrl: checked.url,
      },
    };
  } catch (error) {
    return {
      ...initial,
      meta: {
        ...initial.meta,
        fetchError: error?.message || String(error),
      },
    };
  } finally {
    cleanup();
  }
}

export function getApiKey() {
  const key = process.env.QVERIS_API_KEY;
  if (!key) {
    console.error("Error: QVERIS_API_KEY environment variable is required.");
    process.exit(1);
  }
  return key;
}

export async function searchTools(query, limit = 10, timeoutMs = 25_000) {
  const apiKey = getApiKey();
  const { signal, cleanup } = timeoutSignal(timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}/search`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, limit }),
      signal,
    });
    if (!res.ok) {
      throw new Error(`Search failed (${res.status}): ${await res.text()}`);
    }
    return await res.json();
  } finally {
    cleanup();
  }
}

export async function executeTool(toolId, searchId, parameters, maxResponseSize = 30_000, timeoutMs = 25_000) {
  const apiKey = getApiKey();
  const { signal, cleanup } = timeoutSignal(timeoutMs);
  try {
    const url = new URL(`${BASE_URL}/tools/execute`);
    url.searchParams.set("tool_id", toolId);
    const res = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        search_id: searchId,
        parameters,
        max_response_size: maxResponseSize,
      }),
      signal,
    });
    if (!res.ok) {
      throw new Error(`Execute failed (${res.status}): ${await res.text()}`);
    }
    return await res.json();
  } finally {
    cleanup();
  }
}
