const BASE = 'https://google.serper.dev';

function getKey(): string {
  const k = process.env.SERPER_API_KEY;
  if (!k) throw new Error('SERPER_API_KEY not set');
  return k;
}

export type SearchType = 'search' | 'news' | 'images' | 'videos' | 'places' | 'shopping' | 'scholar' | 'patents' | 'autocomplete' | 'account';

export interface SearchParams {
  q?: string;
  num?: number;
  gl?: string;
  hl?: string;
  tbs?: string;
  page?: number;
  autocorrect?: boolean;
  as_ylo?: number;
}

export async function query(type: SearchType, params: SearchParams = {}): Promise<any> {
  const url = `${BASE}/${type}`;
  const key = getKey();
  const body: any = {};
  if (params.q) body.q = params.q;
  if (params.num) body.num = params.num;
  if (params.gl) body.gl = params.gl;
  if (params.hl) body.hl = params.hl;
  if (params.tbs) body.tbs = params.tbs;
  if (params.page) body.page = params.page;
  if (params.autocorrect !== undefined) body.autocorrect = params.autocorrect;
  if (params.as_ylo) body.as_ylo = params.as_ylo;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-API-KEY': key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    if (res.status === 401 || res.status === 403) throw new Error('Invalid SERPER_API_KEY');
    if (res.status === 429) throw new Error('Rate limited — slow down (5 req/sec max)');
    throw new Error(`Serper API error ${res.status}: ${text}`);
  }

  return res.json();
}
