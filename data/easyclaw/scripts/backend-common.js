#!/usr/bin/env node
require("dotenv").config();

const { URL } = require("node:url");

function ensureFetch() {
  if (typeof fetch !== "function") {
    throw new Error("Global fetch is not available. Use Node.js 18+.");
  }
}

function apiBaseUrl() {
  const raw =
    process.env.EASYCLAW_API_BASE_URL ||
    process.env.API_BASE_URL ||
    "http://127.0.0.1:8080";
  return String(raw).trim().replace(/\/$/, "");
}

function wsUrl() {
  const explicit =
    process.env.EASYCLAW_WS_URL ||
    process.env.BACKEND_WS_URL ||
    process.env.WS_URL;
  if (explicit && String(explicit).trim().length > 0) {
    return String(explicit).trim();
  }

  const base = apiBaseUrl();
  if (base.startsWith("https://")) {
    return `${base.replace("https://", "wss://")}/ws`;
  }
  if (base.startsWith("http://")) {
    return `${base.replace("http://", "ws://")}/ws`;
  }
  return `${base}/ws`;
}

function authToken(overrideToken) {
  if (overrideToken && String(overrideToken).trim().length > 0) {
    return String(overrideToken).trim();
  }
  const token =
    process.env.EASYCLAW_API_TOKEN ||
    process.env.API_AUTH_TOKEN ||
    process.env.API_TOKEN ||
    "";
  return String(token).trim();
}

function appendQueryParams(url, query) {
  if (!query) {
    return;
  }
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || String(value).trim() === "") {
      continue;
    }
    url.searchParams.set(key, String(value));
  }
}

async function apiRequest(path, options = {}) {
  ensureFetch();

  const {
    method = "GET",
    query,
    body,
    requireAuth = false,
    token,
    timeoutMs = 15000
  } = options;

  const endpoint = new URL(path, `${apiBaseUrl()}/`);
  appendQueryParams(endpoint, query);

  const headers = {
    Accept: "application/json"
  };

  const resolvedToken = authToken(token);
  if (resolvedToken) {
    headers.Authorization = `Bearer ${resolvedToken}`;
  } else if (requireAuth) {
    throw new Error(
      "Missing API auth token. Set EASYCLAW_API_TOKEN or pass --token."
    );
  }

  let payload;
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response;
  try {
    response = await fetch(endpoint.toString(), {
      method,
      headers,
      body: payload,
      signal: controller.signal
    });
  } finally {
    clearTimeout(timer);
  }

  const text = await response.text();
  let parsed;
  if (text.length > 0) {
    try {
      parsed = JSON.parse(text);
    } catch (_err) {
      parsed = text;
    }
  }

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    if (parsed && typeof parsed === "object" && parsed.error) {
      message = `${message}: ${parsed.error}`;
    } else if (typeof parsed === "string" && parsed.length > 0) {
      message = `${message}: ${parsed}`;
    }
    throw new Error(message);
  }

  return parsed;
}

module.exports = {
  apiBaseUrl,
  apiRequest,
  authToken,
  wsUrl
};
