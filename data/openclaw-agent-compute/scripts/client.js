import { request } from 'undici';

/**
 * Public skill HTTP client for the private compute gateway.
 *
 * Env:
 *  - MCP_COMPUTE_URL (e.g. https://compute.example.com)
 *  - MCP_COMPUTE_API_KEY
 */

const baseUrl = process.env.MCP_COMPUTE_URL;
const apiKey = process.env.MCP_COMPUTE_API_KEY;

function assertEnv() {
  if (!baseUrl) throw new Error('Missing MCP_COMPUTE_URL');
  if (!apiKey) throw new Error('Missing MCP_COMPUTE_API_KEY');
}

async function post(path, body) {
  assertEnv();
  const url = new URL(path, baseUrl);
  const res = await request(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify(body ?? {})
  });

  const text = await res.body.text();
  if (res.statusCode >= 400) {
    throw new Error(`${path} failed: ${res.statusCode} ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function del(path) {
  assertEnv();
  const url = new URL(path, baseUrl);
  const res = await request(url, {
    method: 'DELETE',
    headers: {
      'authorization': `Bearer ${apiKey}`
    }
  });
  const text = await res.body.text();
  if (res.statusCode >= 400) {
    throw new Error(`${path} failed: ${res.statusCode} ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function get(path) {
  assertEnv();
  const url = new URL(path, baseUrl);
  const res = await request(url, {
    method: 'GET',
    headers: {
      'authorization': `Bearer ${apiKey}`
    }
  });
  const text = await res.body.text();
  if (res.statusCode >= 400) {
    throw new Error(`${path} failed: ${res.statusCode} ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

export async function computeSessionCreate({ spec } = {}) {
  return post('/v1/sessions', { spec });
}

export async function computeExec({ session_id, cmd, cwd, env, timeout_s }) {
  return post('/v1/exec', { session_id, cmd, cwd, env, timeout_s });
}

export async function computeUsage({ session_id }) {
  return get(`/v1/usage/${encodeURIComponent(session_id)}`);
}

export async function computeSessionDestroy({ session_id }) {
  return del(`/v1/sessions/${encodeURIComponent(session_id)}`);
}
