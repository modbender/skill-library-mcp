import { strapi } from '@strapi/client';

export type StrapiClient = ReturnType<typeof strapi>;

export function createClient(): StrapiClient {
  const baseURL = process.env.STRAPI_BASE_URL;
  const auth = process.env.STRAPI_API_TOKEN;

  if (!baseURL) {
    throw new Error('STRAPI_BASE_URL environment variable is not set. Set it in openclaw.json under skills.entries.strapi.env');
  }

  if (!auth) {
    throw new Error('STRAPI_API_TOKEN environment variable is not set. Enter it as API Key during skill installation');
  }

  return strapi({ baseURL, auth });
}

/**
 * client.fetch() returns a raw Response object, not parsed JSON.
 * This helper checks the status code and calls .json() on the response.
 */
export async function fetchJson<T = unknown>(
  client: StrapiClient,
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await client.fetch(path, init);
  const resp = response as unknown as Response;
  if (!resp.ok) {
    let detail = '';
    try { detail = await resp.text(); } catch { /* ignore */ }
    throw new Error(`HTTP ${resp.status} ${resp.statusText}${detail ? ': ' + detail : ''}`);
  }
  return resp.json() as Promise<T>;
}
