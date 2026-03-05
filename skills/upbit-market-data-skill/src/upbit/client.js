const { loadConfig } = require("../config");
const { UpbitError } = require("./errors");
const { createJwt } = require("./auth");

function buildQuery(params = {}) {
  const esc = encodeURIComponent;
  const items = [];

  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    items.push(`${esc(k)}=${esc(String(v))}`);
  }

  return items.join("&");
}

async function request({ method = "GET", path, query, authRequired = false }) {
  const cfg = loadConfig();
  const baseUrl = cfg?.upbit?.baseUrl || "https://api.upbit.com";

  const qs = buildQuery(query);
  const url = `${baseUrl}${path}${qs ? `?${qs}` : ""}`;

  const headers = { Accept: "application/json" };

  if (authRequired) {
    const token = createJwt({ queryString: qs });
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, { method, headers });
  const text = await res.text();

  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    const upbitErr = data?.error;
    throw new UpbitError(`HTTP ${res.status}`, { status: res.status, upbit: upbitErr || data, url });
  }

  return data;
}

module.exports = { request };

