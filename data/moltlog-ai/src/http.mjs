export async function fetchJson(url, { method = 'GET', headers = {}, body, timeoutMs = 30_000 } = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      method,
      headers: {
        'accept': 'application/json',
        ...headers,
      },
      body,
      signal: ctrl.signal,
    });

    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => '');

    if (!res.ok) {
      const err = new Error(`HTTP ${res.status} ${res.statusText}`);
      err.status = res.status;
      err.statusText = res.statusText;
      err.url = url;
      err.data = data;
      err.headers = Object.fromEntries(res.headers.entries());
      throw err;
    }

    return { res, data };
  } finally {
    clearTimeout(t);
  }
}

export function formatHttpError(err) {
  const status = err?.status;
  const msgParts = [];
  if (status) msgParts.push(`HTTP ${status}`);
  if (err?.data?.error) msgParts.push(String(err.data.error));
  if (err?.data?.message) msgParts.push(String(err.data.message));
  if (typeof err?.data === 'string' && err.data) msgParts.push(err.data.slice(0, 300));
  return msgParts.join(' — ') || String(err);
}
